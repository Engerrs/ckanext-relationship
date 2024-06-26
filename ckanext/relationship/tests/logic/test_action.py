import pytest

import ckan.plugins.toolkit as tk
from ckan.tests import factories

from ckanext.relationship.model.relationship import Relationship


@pytest.mark.usefixtures("clean_db")
class TestRelationCreate:
    def test_create_new_relation(self):
        subject_dataset = factories.Dataset()
        object_dataset = factories.Dataset()

        subject_id = subject_dataset["id"]
        object_id = object_dataset["id"]
        relation_type = "related_to"

        result = tk.get_action("relationship_relation_create")(
            {"ignore_auth": True},
            {
                "subject_id": subject_id,
                "object_id": object_id,
                "relation_type": relation_type,
            },
        )

        assert result[0]["subject_id"] == subject_id
        assert result[0]["object_id"] == object_id
        assert result[0]["relation_type"] == relation_type

        assert result[1]["subject_id"] == object_id
        assert result[1]["object_id"] == subject_id
        assert result[1]["relation_type"] == relation_type

    def test_does_not_create_duplicate_relation(self):
        subject_dataset = factories.Dataset()
        object_dataset = factories.Dataset()

        subject_id = subject_dataset["id"]
        object_id = object_dataset["id"]
        relation_type = "related_to"

        tk.get_action("relationship_relation_create")(
            {"ignore_auth": True},
            {
                "subject_id": subject_id,
                "object_id": object_id,
                "relation_type": relation_type,
            },
        )

        result = tk.get_action("relationship_relation_create")(
            {"ignore_auth": True},
            {
                "subject_id": subject_id,
                "object_id": object_id,
                "relation_type": relation_type,
            },
        )

        assert result is None

    def test_relation_is_added_to_db(self):
        subject_dataset = factories.Dataset()
        object_dataset = factories.Dataset()

        subject_id = subject_dataset["id"]
        object_id = object_dataset["id"]
        relation_type = "related_to"

        tk.get_action("relationship_relation_create")(
            {"ignore_auth": True},
            {
                "subject_id": subject_id,
                "object_id": object_id,
                "relation_type": relation_type,
            },
        )

        relation_straight = Relationship.by_object_id(
            subject_id,
            object_id,
            relation_type,
        )
        relation_reverse = Relationship.by_object_id(
            object_id,
            subject_id,
            relation_type,
        )

        assert relation_straight.subject_id == subject_id
        assert relation_straight.object_id == object_id
        assert relation_straight.relation_type == relation_type

        assert relation_reverse.subject_id == object_id
        assert relation_reverse.object_id == subject_id
        assert relation_reverse.relation_type == relation_type

    @pytest.mark.parametrize(
        "relation_type",
        [
            "related_to",
            "parent_of",
            "child_of",
        ],
    )
    def test_different_relation_types(self, relation_type):
        subject_dataset = factories.Dataset()
        object_dataset = factories.Dataset()

        subject_id = subject_dataset["id"]
        object_id = object_dataset["id"]

        result = tk.get_action("relationship_relation_create")(
            {"ignore_auth": True},
            {
                "subject_id": subject_id,
                "object_id": object_id,
                "relation_type": relation_type,
            },
        )

        assert result[0]["relation_type"] == relation_type
        assert (
            result[1]["relation_type"]
            == Relationship.reverse_relation_type[relation_type]
        )


@pytest.mark.usefixtures("clean_db")
class TestRelationDelete:
    def test_relation_delete(self):
        subject_dataset = factories.Dataset()
        object_dataset = factories.Dataset()

        subject_id = subject_dataset["id"]
        object_id = object_dataset["id"]
        relation_type = "related_to"

        tk.get_action("relationship_relation_create")(
            {"ignore_auth": True},
            {
                "subject_id": subject_id,
                "object_id": object_id,
                "relation_type": relation_type,
            },
        )

        result = tk.get_action("relationship_relation_delete")(
            {"ignore_auth": True},
            {
                "subject_id": subject_id,
                "object_id": object_id,
                "relation_type": relation_type,
            },
        )

        assert result[0]["subject_id"] == subject_id
        assert result[0]["object_id"] == object_id
        assert result[0]["relation_type"] == relation_type

        assert result[1]["subject_id"] == object_id
        assert result[1]["object_id"] == subject_id
        assert result[1]["relation_type"] == relation_type

    def test_relation_deleted_from_db(self):
        subject_dataset = factories.Dataset()
        object_dataset = factories.Dataset()

        subject_id = subject_dataset["id"]
        object_id = object_dataset["id"]
        relation_type = "related_to"

        tk.get_action("relationship_relation_create")(
            {"ignore_auth": True},
            {
                "subject_id": subject_id,
                "object_id": object_id,
                "relation_type": relation_type,
            },
        )

        tk.get_action("relationship_relation_delete")(
            {"ignore_auth": True},
            {
                "subject_id": subject_id,
                "object_id": object_id,
                "relation_type": relation_type,
            },
        )

        relation_straight = Relationship.by_object_id(
            subject_id,
            object_id,
            relation_type,
        )
        relation_reverse = Relationship.by_object_id(
            object_id,
            subject_id,
            relation_type,
        )

        assert not relation_straight
        assert not relation_reverse

    def test_relation_delete_after_dataset_delete(self):
        subject_dataset = factories.Dataset()
        object_dataset = factories.Dataset()

        subject_id = subject_dataset["id"]
        object_id = object_dataset["id"]
        relation_type = "related_to"

        tk.get_action("relationship_relation_create")(
            {"ignore_auth": True},
            {
                "subject_id": subject_id,
                "object_id": object_id,
                "relation_type": relation_type,
            },
        )

        tk.get_action("package_delete")({"ignore_auth": True}, {"id": subject_id})

        relation_straight = Relationship.by_object_id(
            subject_id,
            object_id,
            relation_type,
        )
        relation_reverse = Relationship.by_object_id(
            object_id,
            subject_id,
            relation_type,
        )

        assert not relation_straight
        assert not relation_reverse


@pytest.mark.usefixtures("clean_db")
class TestRelationList:
    @pytest.mark.parametrize(
        "subject_factory, object_factory, object_entity, object_type",
        [
            (factories.Dataset, factories.Dataset, "package", "dataset"),
            (factories.Dataset, factories.Organization, "organization", "organization"),
            (factories.Dataset, factories.Group, "group", "group"),
            (factories.Organization, factories.Dataset, "package", "dataset"),
            (
                factories.Organization,
                factories.Organization,
                "organization",
                "organization",
            ),
            (factories.Organization, factories.Group, "group", "group"),
            (factories.Group, factories.Dataset, "package", "dataset"),
            (factories.Group, factories.Organization, "organization", "organization"),
            (factories.Group, factories.Group, "group", "group"),
        ],
    )
    def test_relation_list(
        self,
        subject_factory,
        object_factory,
        object_entity,
        object_type,
    ):
        subject = subject_factory()
        object = object_factory()

        subject_id = subject["id"]
        object_id = object["id"]
        relation_type = "related_to"

        tk.get_action("relationship_relation_create")(
            {"ignore_auth": True},
            {
                "subject_id": subject_id,
                "object_id": object_id,
                "relation_type": relation_type,
            },
        )

        result = tk.get_action("relationship_relations_list")(
            {"ignore_auth": True},
            {
                "subject_id": subject_id,
                "object_entity": object_entity,
                "object_type": object_type,
                "relation_type": relation_type,
            },
        )

        assert result[0]["subject_id"] == subject_id
        assert result[0]["object_id"] == object_id
        assert result[0]["relation_type"] == relation_type

    def test_relation_list_empty(self):
        subject_dataset = factories.Dataset()

        subject_id = subject_dataset["id"]
        relation_type = "related_to"

        result = tk.get_action("relationship_relations_list")(
            {"ignore_auth": True},
            {
                "subject_id": subject_id,
                "object_entity": "package",
                "object_type": "dataset",
                "relation_type": relation_type,
            },
        )

        assert result == []

    def test_relation_list_after_dataset_delete(self):
        subject_dataset = factories.Dataset()
        object_dataset = factories.Dataset()

        subject_id = subject_dataset["id"]
        object_id = object_dataset["id"]
        relation_type = "related_to"

        tk.get_action("relationship_relation_create")(
            {"ignore_auth": True},
            {
                "subject_id": subject_id,
                "object_id": object_id,
                "relation_type": relation_type,
            },
        )

        tk.get_action("package_delete")({"ignore_auth": True}, {"id": subject_id})

        result = tk.get_action("relationship_relations_list")(
            {"ignore_auth": True},
            {
                "subject_id": subject_id,
                "object_entity": "package",
                "object_type": "dataset",
                "relation_type": relation_type,
            },
        )

        assert result == []


@pytest.mark.usefixtures("clean_db")
class TestRelationsIdsList:
    def test_relations_ids_list(self):
        subject_dataset = factories.Dataset()
        object1_dataset = factories.Dataset()
        object2_dataset = factories.Dataset()

        subject_id = subject_dataset["id"]
        object1_id = object1_dataset["id"]
        object2_id = object2_dataset["id"]
        relation_type = "related_to"

        tk.get_action("relationship_relation_create")(
            {"ignore_auth": True},
            {
                "subject_id": subject_id,
                "object_id": object1_id,
                "relation_type": relation_type,
            },
        )

        tk.get_action("relationship_relation_create")(
            {"ignore_auth": True},
            {
                "subject_id": subject_id,
                "object_id": object2_id,
                "relation_type": relation_type,
            },
        )

        result = tk.get_action("relationship_relations_ids_list")(
            {"ignore_auth": True},
            {
                "subject_id": subject_id,
                "object_entity": "package",
                "object_type": "dataset",
                "relation_type": relation_type,
            },
        )

        assert object1_id in result
        assert object2_id in result
