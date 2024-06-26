from flask import Blueprint

import ckan.plugins.toolkit as tk


def get_blueprints():
    return [
        relationships,
    ]


relationships = Blueprint("relationships", __name__)


@relationships.route("/api/2/util/relationships/autocomplete")
def relationships_autocomplete():
    request_args = tk.request.args
    return tk.get_action("relationship_autocomplete")(
        {},
        {
            "incomplete": request_args.get("incomplete"),
            "current_entity_id": request_args.get("current_entity_id"),
            "entity_type": request_args.get("entity_type", "dataset"),
            "updatable_only": tk.asbool(request_args.get("updatable_only")),
            "owned_only": tk.asbool(request_args.get("owned_only")),
            "check_sysadmin": tk.asbool(request_args.get("check_sysadmin")),
            "format_autocomplete_helper": request_args.get(
                "format_autocomplete_helper",
            ),
        },
    )
