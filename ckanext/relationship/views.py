from flask import Blueprint, jsonify

import ckan.plugins.toolkit as tk
from ckan import authz


def get_blueprints():
    return [
        relationships,
    ]


relationships = Blueprint("relationships", __name__)


@relationships.route("/api/util/relationships/autocomplete")
def relationships_autocomplete():
    incomplete = tk.request.args.get("incomplete", "")
    current_entity_id = tk.request.args.get("current_entity_id")
    entity_type = tk.request.args.get("entity_type", "dataset")
    updatable_only = tk.asbool(tk.request.args.get("updatable_only", "False"))
    owned_only = tk.asbool(tk.request.args.get("owned_only", "False"))

    fq = f"type:{entity_type} -id:{current_entity_id}"
    if owned_only and not authz.is_sysadmin(tk.current_user.id):
        fq += f" creator_user_id:{tk.current_user.id}"

    packages = tk.get_action("package_search")(
        {},
        {
            "q": incomplete,
            "fq": fq,
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
