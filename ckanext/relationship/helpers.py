from __future__ import annotations

import json
from typing import Any

import ckan.plugins.toolkit as tk
from ckan import authz


def get_helpers():
    helper_functions = [
        relationship_get_entity_list,
        relationship_get_current_relations_list,
        relationship_get_selected_json,
        relationship_get_choices_for_related_entity_field,
        relationship_format_autocomplete,
    ]
    return {f.__name__: f for f in helper_functions}


def relationship_get_entity_list(entity, entity_type, include_private=True):
    """Return ids list of specified entity (entity, entity_type)."""
    context = {}
    if entity == "package":
        entity_list = tk.get_action("package_search")(
            context,
            {
                "fq": f"type:{entity_type}",
                "rows": 1000,
                "include_private": include_private,
            },
        )
        entity_list = entity_list["results"]
    else:
        entity_list = tk.get_action("relationship_get_entity_list")(
            context,
            {"entity": entity, "entity_type": entity_type},
        )
        entity_list = [
            {"id": id, "name": name, "title": title} for id, name, title in entity_list
        ]
    return entity_list


def relationship_get_current_relations_list(data, field) -> list[str]:
    """Pull existing relations for form_snippet and display_snippet."""
    subject_id = field.get("id")
    subject_name = field.get("name")
    if not subject_id and not subject_name:
        return []
    related_entity = data["related_entity"]
    related_entity_type = data["related_entity_type"]
    relation_type = data["relation_type"]

    current_relation_by_id = []
    current_relation_by_name = []

    if subject_id:
        current_relation_by_id = tk.get_action("relationship_relations_ids_list")(
            {},
            {
                "subject_id": subject_id,
                "object_entity": related_entity,
                "object_type": related_entity_type,
                "relation_type": relation_type,
            },
        )
    if subject_name:
        current_relation_by_name = tk.get_action("relationship_relations_ids_list")(
            {},
            {
                "subject_id": subject_name,
                "object_entity": related_entity,
                "object_type": related_entity_type,
                "relation_type": relation_type,
            },
        )
    return current_relation_by_id + current_relation_by_name


def relationship_get_selected_json(selected_ids: list | None = None) -> str:
    if not selected_ids:
        return json.dumps([])

    selected_pkgs = []
    for pkg_id in selected_ids:
        try:
            pkg_dict = tk.get_action("package_show")({}, {"id": pkg_id})
            selected_pkgs.append({"name": pkg_dict["id"], "title": pkg_dict["title"]})
        except (tk.ObjectNotFound, tk.NotAuthorized):
            continue
    return json.dumps(selected_pkgs)


def relationship_get_choices_for_related_entity_field(
    field: dict[str, Any],
    current_entity_id: str | None,
) -> list[str | None]:
    entities = relationship_get_entity_list(
        field["related_entity"],
        field["related_entity_type"],
    )

    choices = []

    for entity in entities:
        if entity["id"] == current_entity_id:
            continue

        if field.get("updatable_only", False) and not tk.h.check_access(
            field["related_entity"] + "_update",
            {"id": entity["id"]},
        ):
            continue

        if (
            field.get("owned_only", False)
            and not authz.is_sysadmin(tk.current_user.id)
            and field["related_entity"] == "package"
            and tk.current_user.id != entity["creator_user_id"]
        ):
            continue

        choices.append((entity["id"], entity.get("title") or entity.get("name")))

    choices.sort(key=lambda x: x[1])
    return choices


def relationship_format_autocomplete(packages: dict[str, Any]) -> dict[str, Any]:
    return {
        "ResultSet": {
            "Result": [
                {
                    "name": pkg["id"],
                    "title": pkg["title"],
                }
                for pkg in packages
            ],
        },
    }
