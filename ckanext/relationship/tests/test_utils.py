import pytest

from ckan.tests import factories

from ckanext.relationship.utils import entity_name_by_id


@pytest.mark.usefixtures("clean_db")
class TestEntityNameById:
    def test_entity_name_by_id_when_package_exists(self):
        dataset = factories.Dataset()
        assert entity_name_by_id(dataset["id"]) == dataset["name"]

    def test_entity_name_by_id_when_organization_exists(self):
        organization = factories.Organization()
        assert entity_name_by_id(organization["id"]) == organization["name"]

    def test_entity_name_by_id_when_group_exists(self):
        group = factories.Group()
        assert entity_name_by_id(group["id"]) == group["name"]

    def test_entity_name_by_id_when_no_entity_exists(self):
        assert entity_name_by_id("nonexistent") is None
