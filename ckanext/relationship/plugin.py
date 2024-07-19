import ckan.plugins.toolkit as tk
from ckan import plugins
from ckan.lib.search import rebuild
from ckan.logic import NotFound

import ckanext.scheming.helpers as sch

from ckanext.relationship import helpers, utils, views
from ckanext.relationship.logic import action, auth, validators


class RelationshipPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IPackageController, inherit=True)

    # IConfigurer
    def update_config(self, config_):
        tk.add_template_directory(config_, "templates")
        tk.add_public_directory(config_, "public")
        tk.add_resource("assets", "relationship")

    # IActions
    def get_actions(self):
        return action.get_actions()

    # IAuthFunctions
    def get_auth_functions(self):
        return auth.get_auth_functions()

    # IValidators
    def get_validators(self):
        return validators.get_validators()

    # ITemplateHelpers
    def get_helpers(self):
        return helpers.get_helpers()

    # IBlueprint
    def get_blueprint(self):
        return views.get_blueprints()

    # IPackageController
    def after_dataset_create(self, context, pkg_dict):
        context = context.copy()
        context.pop("__auth_audit", None)
        return _update_relations(context, pkg_dict)

    def after_dataset_update(self, context, pkg_dict):
        context = context.copy()
        context.pop("__auth_audit", None)
        return _update_relations(context, pkg_dict)

    def after_dataset_delete(self, context, pkg_dict):
        context = context.copy()
        context.pop("__auth_audit", None)

        subject_id = pkg_dict["id"]

        relations_ids_list = tk.get_action("relationship_relations_ids_list")(
            context,
            {"subject_id": subject_id},
        )

        for object_id in relations_ids_list:
            tk.get_action("relationship_relation_delete")(
                context,
                {"subject_id": subject_id, "object_id": object_id},
            )

            try:
                rebuild(object_id)
            except NotFound:
                pass
        rebuild(subject_id)

    def before_dataset_index(self, pkg_dict):
        pkg_id = pkg_dict["id"]
        pkg_type = pkg_dict["type"]
        schema = sch.scheming_get_schema("dataset", pkg_type)
        if not schema:
            return pkg_dict
        relations_info = utils.get_relations_info(pkg_type)
        for (
            related_entity,
            related_entity_type,
            relation_type,
        ) in relations_info:
            relations_ids = tk.get_action("relationship_relations_ids_list")(
                {},
                {
                    "subject_id": pkg_id,
                    "object_entity": related_entity,
                    "object_type": related_entity_type,
                    "relation_type": relation_type,
                },
            )

            if not relations_ids:
                continue
            field = utils.get_relation_field(
                pkg_type,
                related_entity,
                related_entity_type,
                relation_type,
            )
            pkg_dict[f'vocab_{field["field_name"]}'] = relations_ids

            pkg_dict.pop(field["field_name"], None)

        return pkg_dict

    # CKAN < 2.10 hooks
    def after_create(self, context, data_dict):
        return self.after_dataset_create(context, data_dict)

    def after_update(self, context, data_dict):
        return self.after_dataset_update(context, data_dict)

    def after_delete(self, context, data_dict):
        return self.after_dataset_delete(context, data_dict)

    def before_index(self, pkg_dict):
        return self.before_dataset_index(pkg_dict)


if tk.check_ckan_version("2.10"):
    tk.blanket.config_declarations(RelationshipPlugin)


def _update_relations(context, pkg_dict):
    subject_id = pkg_dict["id"]
    add_relations = pkg_dict.get("add_relations", [])
    del_relations = pkg_dict.get("del_relations", [])
    if not add_relations and not del_relations:
        return pkg_dict
    for object_id, relation_type in del_relations + add_relations:
        if (object_id, relation_type) in add_relations:
            tk.get_action("relationship_relation_create")(
                context,
                {
                    "subject_id": subject_id,
                    "object_id": object_id,
                    "relation_type": relation_type,
                },
            )
        else:
            tk.get_action("relationship_relation_delete")(
                context,
                {
                    "subject_id": subject_id,
                    "object_id": object_id,
                    "relation_type": relation_type,
                },
            )

        try:
            rebuild(object_id)
        except NotFound:
            pass
    rebuild(subject_id)
    return pkg_dict
