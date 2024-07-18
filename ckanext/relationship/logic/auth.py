from __future__ import annotations

from ckan.plugins import toolkit as tk


def get_auth_functions():
    auth_functions = [
        relationship_relation_create,
        relationship_relation_delete,
        relationship_relations_list,
        relationship_relations_ids_list,
        relationship_get_entity_list,
        relationship_relationship_autocomplete,
    ]
    return {f.__name__: f for f in auth_functions}


def relationship_relation_create(context, data_dict):
    return {"success": True}


def relationship_relation_delete(context, data_dict):
    return {"success": True}


@tk.auth_allow_anonymous_access
def relationship_relations_list(context, data_dict):
    return {"success": True}


@tk.auth_allow_anonymous_access
def relationship_relations_ids_list(context, data_dict):
    return {"success": True}


@tk.auth_allow_anonymous_access
def relationship_get_entity_list(context, data_dict):
    return {"success": True}


@tk.auth_allow_anonymous_access
def relationship_relationship_autocomplete(context, data_dict):
    return {"success": True}
