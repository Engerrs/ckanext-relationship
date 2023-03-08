from __future__ import annotations

from ckan.plugins import toolkit as tk


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
