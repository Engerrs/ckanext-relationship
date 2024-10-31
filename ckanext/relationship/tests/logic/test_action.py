import pytest

import ckan.plugins.toolkit as tk
from ckan.tests import factories
from ckan.tests.helpers import call_action

from ckanext.relationship.model.relationship import Relationship


@pytest.mark.usefixtures("clean_db")
class TestRelationCreate:
    def test_create_new_relation(self):
        subject_dataset = factories.Dataset()
        object_dataset = factories.Dataset()

        subject_id = subject_dataset["id"]
        object_id = object_dataset["id"]
        relation_type = "related_to"

        result = call_action(
            "relationship_relation_create",
            {"ignore_auth": True},
            subject_id=subject_id,
            object_id=object_id,
            relation_type=relation_type,
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

        call_action(
            "relationship_relation_create",
            {"ignore_auth": True},
            subject_id=subject_id,
            object_id=object_id,
            relation_type=relation_type,
        )

        result = call_action(
            "relationship_relation_create",
            {"ignore_auth": True},
            subject_id=subject_id,
            object_id=object_id,
            relation_type=relation_type,
        )

        assert result == []

    def test_relation_is_added_to_db(self):
        subject_dataset = factories.Dataset()
        object_dataset = factories.Dataset()

        subject_id = subject_dataset["id"]
        object_id = object_dataset["id"]
        relation_type = "related_to"

        call_action(
            "relationship_relation_create",
            {"ignore_auth": True},
            subject_id=subject_id,
            object_id=object_id,
            relation_type=relation_type,
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

    def test_creation_by_name(self):
        """We can create a relation by name instead of ID.

        Should be revised in the future to avoid this kind of behavior.
        """
        subject_dataset = factories.Dataset()
        object_dataset = factories.Dataset()

        subject_id = subject_dataset["name"]
        object_id = object_dataset["name"]
        relation_type = "related_to"

        result = call_action(
            "relationship_relation_create",
            {"ignore_auth": True},
            subject_id=subject_id,
            object_id=object_id,
            relation_type=relation_type,
        )

        assert result[0]["subject_id"] == subject_id
        assert result[0]["object_id"] == object_id
        assert result[0]["relation_type"] == relation_type

        assert result[1]["subject_id"] == object_id
        assert result[1]["object_id"] == subject_id
        assert result[1]["relation_type"] == relation_type

    def test_get_by_id_relation_created_by_name(self):
        """We can get a relation by ID if it was created by name."""
        subject_dataset = factories.Dataset()
        object_dataset = factories.Dataset()

        subject_id = subject_dataset["id"]

        subject_name = subject_dataset["name"]
        object_name = object_dataset["name"]
        relation_type = "related_to"

        call_action(
            "relationship_relation_create",
            {"ignore_auth": True},
            subject_id=subject_name,
            object_id=object_name,
            relation_type=relation_type,
        )

        result = call_action(
            "relationship_relations_list",
            {"ignore_auth": True},
            subject_id=subject_id,
        )

        assert result[0]["subject_id"] == subject_name
        assert result[0]["object_id"] == object_name
        assert result[0]["relation_type"] == relation_type

    def test_get_by_name_relation_created_by_id(self):
        """We cannot get a relation by name if it was created by ID."""
        subject_dataset = factories.Dataset()
        object_dataset = factories.Dataset()

        subject_id = subject_dataset["id"]
        object_id = object_dataset["id"]

        subject_name = subject_dataset["name"]
        relation_type = "related_to"

        call_action(
            "relationship_relation_create",
            {"ignore_auth": True},
            subject_id=subject_id,
            object_id=object_id,
            relation_type=relation_type,
        )

        result = call_action(
            "relationship_relations_list",
            {"ignore_auth": True},
            subject_id=subject_name,
        )

        assert result == []

    @pytest.mark.parametrize(
        "relation_type",
        [
            "related_to",
            "parent_of",
            "child_of",
        ],
    )
    def test_different_relation_types(self, relation_type: str):
        subject_dataset = factories.Dataset()
        object_dataset = factories.Dataset()

        subject_id = subject_dataset["id"]
        object_id = object_dataset["id"]

        result = call_action(
            "relationship_relation_create",
            {"ignore_auth": True},
            subject_id=subject_id,
            object_id=object_id,
            relation_type=relation_type,
        )

        assert result[0]["relation_type"] == relation_type
        assert (
            result[1]["relation_type"]
            == Relationship.reverse_relation_type[relation_type]
        )

    def test_no_subject_id(self):
        object_dataset = factories.Dataset()

        object_id = object_dataset["id"]

        with pytest.raises(tk.ValidationError):
            call_action(
                "relationship_relation_create",
                {"ignore_auth": True},
                object_id=object_id,
            )

    def test_no_object_id(self):
        subject_dataset = factories.Dataset()

        subject_id = subject_dataset["id"]

        with pytest.raises(tk.ValidationError):
            call_action(
                "relationship_relation_create",
                {"ignore_auth": True},
                subject_id=subject_id,
            )

    def test_no_relation_type(self):
        subject_dataset = factories.Dataset()
        object_dataset = factories.Dataset()

        subject_id = subject_dataset["id"]
        object_id = object_dataset["id"]

        with pytest.raises(tk.ValidationError):
            call_action(
                "relationship_relation_create",
                {"ignore_auth": True},
                subject_id=subject_id,
                object_id=object_id,
            )

    def test_created_at(self):
        subject_dataset = factories.Dataset()
        object_dataset = factories.Dataset()

        subject_id = subject_dataset["id"]
        object_id = object_dataset["id"]
        relation_type = "related_to"

        result = call_action(
            "relationship_relation_create",
            {"ignore_auth": True},
            subject_id=subject_id,
            object_id=object_id,
            relation_type=relation_type,
        )

        assert "created_at" in result[0]
        assert "created_at" in result[1]

    def test_extras(self):
        subject_dataset = factories.Dataset()
        object_dataset = factories.Dataset()

        subject_id = subject_dataset["id"]
        object_id = object_dataset["id"]
        relation_type = "related_to"
        extras = {"key": "value"}

        result = call_action(
            "relationship_relation_create",
            {"ignore_auth": True},
            subject_id=subject_id,
            object_id=object_id,
            relation_type=relation_type,
            extras=extras,
        )

        assert result[0]["extras"] == extras
        assert result[1]["extras"] == extras


@pytest.mark.usefixtures("clean_db")
class TestRelationDelete:
    def test_relation_delete(self):
        subject_dataset = factories.Dataset()
        object_dataset = factories.Dataset()

        subject_id = subject_dataset["id"]
        object_id = object_dataset["id"]
        relation_type = "related_to"

        call_action(
            "relationship_relation_create",
            {"ignore_auth": True},
            subject_id=subject_id,
            object_id=object_id,
            relation_type=relation_type,
        )

        result = call_action(
            "relationship_relation_delete",
            {"ignore_auth": True},
            subject_id=subject_id,
            object_id=object_id,
            relation_type=relation_type,
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

        call_action(
            "relationship_relation_create",
            {"ignore_auth": True},
            subject_id=subject_id,
            object_id=object_id,
            relation_type=relation_type,
        )

        call_action(
            "relationship_relation_delete",
            {"ignore_auth": True},
            subject_id=subject_id,
            object_id=object_id,
            relation_type=relation_type,
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

        call_action(
            "relationship_relation_create",
            {"ignore_auth": True},
            subject_id=subject_id,
            object_id=object_id,
            relation_type=relation_type,
        )

        call_action("package_delete", {"ignore_auth": True}, id=subject_id)

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
        ("subject_factory", "object_factory", "object_entity", "object_type"),
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
        object_entity: str,
        object_type: str,
    ):
        subject = subject_factory()
        object = object_factory()

        subject_id = subject["id"]
        object_id = object["id"]
        relation_type = "related_to"

        call_action(
            "relationship_relation_create",
            {"ignore_auth": True},
            subject_id=subject_id,
            object_id=object_id,
            relation_type=relation_type,
        )

        result = call_action(
            "relationship_relations_list",
            {"ignore_auth": True},
            subject_id=subject_id,
            object_entity=object_entity,
            object_type=object_type,
            relation_type=relation_type,
        )

        assert result[0]["subject_id"] == subject_id
        assert result[0]["object_id"] == object_id
        assert result[0]["relation_type"] == relation_type

    def test_relation_list_empty(self):
        subject_dataset = factories.Dataset()

        subject_id = subject_dataset["id"]
        relation_type = "related_to"

        result = call_action(
            "relationship_relations_list",
            {"ignore_auth": True},
            subject_id=subject_id,
            object_entity="package",
            object_type="dataset",
            relation_type=relation_type,
        )

        assert result == []

    def test_relation_list_after_dataset_delete(self):
        subject_dataset = factories.Dataset()
        object_dataset = factories.Dataset()

        subject_id = subject_dataset["id"]
        object_id = object_dataset["id"]
        relation_type = "related_to"

        call_action(
            "relationship_relation_create",
            {"ignore_auth": True},
            subject_id=subject_id,
            object_id=object_id,
            relation_type=relation_type,
        )

        call_action("package_delete", {"ignore_auth": True}, id=subject_id)

        result = call_action(
            "relationship_relations_list",
            {"ignore_auth": True},
            subject_id=subject_id,
            object_entity="package",
            object_type="dataset",
            relation_type=relation_type,
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

        call_action(
            "relationship_relation_create",
            {"ignore_auth": True},
            subject_id=subject_id,
            object_id=object1_id,
            relation_type=relation_type,
        )

        call_action(
            "relationship_relation_create",
            {"ignore_auth": True},
            subject_id=subject_id,
            object_id=object2_id,
            relation_type=relation_type,
        )

        result = call_action(
            "relationship_relations_ids_list",
            {"ignore_auth": True},
            subject_id=subject_id,
            object_entity="package",
            object_type="dataset",
            relation_type=relation_type,
        )

        assert object1_id in result
        assert object2_id in result


@pytest.mark.usefixtures("clean_db")
def test_keep_relation_after_dataset_patch():
    subject_dataset = factories.Dataset(type="package_with_relationship")
    object_dataset = factories.Dataset(type="package_with_relationship")

    subject_id = subject_dataset["id"]
    object_id = object_dataset["id"]
    relation_type = "related_to"

    call_action(
        "relationship_relation_create",
        {"ignore_auth": True},
        subject_id=subject_id,
        object_id=object_id,
        relation_type=relation_type,
    )

    call_action(
        "package_patch", {"ignore_auth": True}, id=subject_id, title="New title"
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

    assert relation_straight is not None
    assert relation_reverse is not None
