from __future__ import annotations

import json

from ckantoolkit import missing
from six import string_types

import ckan.plugins.toolkit as tk

from ckanext.scheming.validation import (
    scheming_multiple_choice_output,
    scheming_validator,
)


def get_validators():
    return {
        "relationship_related_entity": relationship_related_entity,
    }


@scheming_validator
def relationship_related_entity(field, schema):
    related_entity = field.get("related_entity")
    related_entity_type = field.get("related_entity_type")
    relation_type = field.get("relation_type")

    def validator(key, data, errors, context):
        if field.get("required") and data[key] is missing:
            errors[key].append(tk._("Select at least one"))

        entity_id = data.get(("id",))

        current_relations = get_current_relations(
            entity_id,
            related_entity,
            related_entity_type,
            relation_type,
        )

        selected_relations = get_selected_relations(data[key])

        data[key] = json.dumps([value for value in selected_relations])

        add_relations = selected_relations - current_relations
        del_relations = current_relations - selected_relations

        data[("add_relations",)] = data.get(("add_relations",), [])
        data[("del_relations",)] = data.get(("del_relations",), [])

        data[("add_relations",)].extend([(rel, relation_type) for rel in add_relations])
        data[("del_relations",)].extend([(rel, relation_type) for rel in del_relations])

    return validator


def get_current_relations(
    entity_id,
    related_entity,
    related_entity_type,
    relation_type,
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


def get_selected_relations(selected_relations):
    if isinstance(selected_relations, string_types) and "," in selected_relations:
        selected_relations = selected_relations.split(",")

    if (
        len(selected_relations) == 1
        and isinstance(selected_relations[0], string_types)
        and "," in selected_relations[0]
    ):
        selected_relations = selected_relations[0].split(",")

    if selected_relations is not missing:
        selected_relations = scheming_multiple_choice_output(selected_relations)
        selected_relations = [] if selected_relations == [""] else selected_relations
    else:
        selected_relations = []
    return set(selected_relations)
