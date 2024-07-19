from __future__ import annotations

import ckan.plugins.toolkit as tk

CONFIG_VIEWS_WITHOUT_RELATIONSHIPS = (
    "ckanext.relationship.views_without_relationships_in_package_show"
)
DEFAULT_VIEWS_WITHOUT_RELATIONSHIPS = ["search", "read"]


def views_without_relationships_in_package_show() -> list[str]:
    return tk.aslist(
        tk.config.get(
            CONFIG_VIEWS_WITHOUT_RELATIONSHIPS,
            DEFAULT_VIEWS_WITHOUT_RELATIONSHIPS,
        ),
    )
