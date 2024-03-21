import pytest


@pytest.fixture
def clean_db(reset_db, migrate_db_for, with_plugins):
    reset_db()
    migrate_db_for("relationship")
