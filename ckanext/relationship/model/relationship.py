from __future__ import annotations

from sqlalchemy import Column, Text, or_

from ckan import logic, model
from ckan.model.types import make_uuid

from .base import Base


class Relationship(Base):
    __tablename__ = "relationship_relationship"
    id: str = Column(Text, primary_key=True, default=make_uuid)
    subject_id: str = Column(Text, nullable=False)
    object_id: str = Column(Text, nullable=False)
    relation_type: str = Column(Text, nullable=False)

    reverse_relation_type = {
        "related_to": "related_to",
        "child_of": "parent_of",
        "parent_of": "child_of",
    }

    def __repr__(self):
        return (
            "Relationship("
            f"id={self.id!r}, "
            f"subject_id={self.subject_id!r}, "
            f"object_id={self.object_id!r}, "
            f"relation_type={self.relation_type!r})"
        )

    def as_dict(self):
        return {
            "id": self.id,
            "subject_id": self.subject_id,
            "object_id": self.object_id,
            "relation_type": self.relation_type,
        }

    @classmethod
    def by_object_id(cls, subject_id: str, object_id: str, relation_type: str):
        subject_name = _entity_name_by_id(subject_id)
        subject_identifiers = [subject_id]
        if subject_name is not None:
            subject_identifiers.append(subject_name)

        object_name = _entity_name_by_id(object_id)
        object_identifiers = [object_id]
        if object_name is not None:
            object_identifiers.append(object_name)

        return (
            model.Session.query(cls)
            .filter(
                cls.subject_id.in_(subject_identifiers),
                cls.object_id.in_(object_identifiers),
                cls.relation_type == relation_type,
            )
            .one_or_none()
        )

    @classmethod
    def by_subject_id(
        cls,
        subject_id: str,
        object_entity: str | None = None,
        object_type: str | None = None,
        relation_type: str | None = None,
    ):
        subject_name = _entity_name_by_id(subject_id)
        subject_identifiers = [subject_id]
        if subject_name is not None:
            subject_identifiers.append(subject_name)

        q = model.Session.query(cls).filter(
            cls.subject_id.in_(subject_identifiers),
        )

        if object_entity:
            object_class = logic.model_name_to_class(model, object_entity)
            q = q.join(
                object_class,
                or_(
                    cls.object_id == object_class.id,
                    cls.object_id == object_class.name,
                ),
            )

            if object_type:
                q = q.filter(object_class.type == object_type)

        if relation_type:
            q = q.filter(cls.relation_type == relation_type)

        return q.all()


def _entity_name_by_id(entity_id: str) -> str | None:
    """Returns the name of an entity (package or group) given its ID."""
    if not entity_id:
        return None

    pkg = (
        model.Session.query(model.Package)
        .filter(model.Package.id == entity_id)
        .one_or_none()
    )
    if pkg:
        return pkg.name

    group = (
        model.Session.query(model.Group)
        .filter(model.Group.id == entity_id)
        .one_or_none()
    )
    if group:
        return group.name
