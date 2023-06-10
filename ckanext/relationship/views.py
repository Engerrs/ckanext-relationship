from flask import Blueprint, jsonify

import ckan.plugins.toolkit as tk


def get_blueprints():
    return [
        relationships,
    ]


relationships = Blueprint("relationships", __name__)


@relationships.route("/api/util/relationships/autocomplete")
def relationships_autocomplete():
    incomplete = tk.request.args.get("incomplete", "")
    entity_type = tk.request.args.get("entity_type", "dataset")
    updatable_only = tk.asbool(tk.request.args.get("updatable_only", "False"))
    packages = tk.get_action("package_search")(
        {},
        {
            "q": incomplete,
            "fq": f"type:{entity_type}",
            "fl": "id, title",
            "rows": 100,
            "include_private": True,
            "sort": "score desc",
        },
    )["results"]

    # packages = filter(
    #     lambda pkg: incomplete.lower() in pkg["title"].lower(), packages
    # )

    if updatable_only:
        packages = filter(
            lambda pkg: tk.h.check_access("package_update", {"id": pkg["id"]}), packages
        )

    result = {
        "ResultSet": {
            "Result": [
                {
                    "name": pkg["id"],
                    "title": pkg["title"],
                }
                for pkg in packages
            ]
        }
    }
    return jsonify(result)
