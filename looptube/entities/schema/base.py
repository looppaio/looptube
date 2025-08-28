"""This module contains the schemas for the Looptube project."""

from __future__ import annotations

from pydantic import Field, AnyHttpUrl, computed_field

from looptube.core import LTSchema, LTEntityType


class EntitySchema(LTSchema):
    """Base component for Looptube"""

    ent_url: AnyHttpUrl = Field(
        title="Entity URL",
        description="The url of the entity",
        examples=[AnyHttpUrl("https://www.youtube.com/watch?v=dQw4w9WgXcQ")],
    )
    ent_tag: LTEntityType = Field(
        title="Entity Tag",
        description="The tag of the entity",
        examples=[LTEntityType.VIDEO],
        default=LTEntityType.VIDEO,
    )

    @computed_field(
        title="Entity ID",
        description="A Unique ID for the entity based on the URL",
        examples=["dQw4w9WgXcQ"],
    )
    @property
    def ent_lt_id(self) -> str:
        """Get the ID for the entity based on the URL"""
        _hash = self.make_id(data=self.ent_url)
        return f"{str(self.ent_tag).lower()}-{str(_hash)}"
