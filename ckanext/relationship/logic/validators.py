from __future__ import annotations

import json
from typing import Any, cast

import ckan.plugins.toolkit as tk
from ckan.types import Context, FlattenDataDict, FlattenErrorDict, FlattenKey

from ckanext.scheming.validation import (
    scheming_multiple_choice_output,  # pyright: ignore[reportUnknownVariableType]
    scheming_validator,  # pyright: ignore[reportUnknownVariableType]
)


def get_validators():
    return {
        "relationship_related_entity": relationship_related_entity,
    }


@scheming_validator
def relationship_related_entity(field: dict[str, Any], schema: dict[str, Any]):
    related_entity = field.get("related_entity")
    related_entity_type = field.get("related_entity_type")
    relation_type = field.get("relation_type")

    def validator(
        key: FlattenKey,
        data: FlattenDataDict,
        errors: FlattenErrorDict,
        context: Context,
    ):
        if field.get("required") and data[key] is tk.missing:
            errors[key].append(tk._("Select at least one"))

        entity_id = data.get(("id",))

        current_relations = get_current_relations(
            entity_id,
            related_entity,
            related_entity_type,
            relation_type,
        )

        selected_relations = get_selected_relations(data[key])
        data[key] = json.dumps(list(selected_relations))

        add_relations = selected_relations - current_relations
        del_relations = current_relations - selected_relations

        data[("add_relations",)] = data.get(("add_relations",), [])
        data[("del_relations",)] = data.get(("del_relations",), [])

        data[("add_relations",)].extend([(rel, relation_type) for rel in add_relations])
        data[("del_relations",)].extend([(rel, relation_type) for rel in del_relations])

    return validator


def get_current_relations(
    entity_id: str | None,
    related_entity: str | None,
    related_entity_type: str | None,
    relation_type: str | None,
):
    if entity_id:
        current_relations = tk.get_action("relationship_relations_list")(
            {},
            {
                "subject_id": entity_id,
                "object_entity": related_entity,
                "object_type": related_entity_type,
                "relation_type": relation_type,
            },
        )
        current_relations = [rel["object_id"] for rel in current_relations]
    else:
        current_relations = []
    return set(current_relations)


def get_selected_relations(selected_relations: list[Any] | str | None) -> set[str]:
    if selected_relations is None:
        selected_relations = []

    if isinstance(selected_relations, str) and "," in selected_relations:
        selected_relations = selected_relations.split(",")

    if (
        len(selected_relations) == 1
        and isinstance(selected_relations[0], str)
        and "," in selected_relations[0]
    ):
        selected_relations = selected_relations[0].split(",")

    if selected_relations is not tk.missing:
        selected_relations = cast(
            "list[str]", scheming_multiple_choice_output(selected_relations)
        )
        selected_relations = [] if selected_relations == [""] else selected_relations
    else:
        selected_relations = []
    return set(selected_relations)
