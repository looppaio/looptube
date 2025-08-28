from pydantic import Field
from .base import EntitySchema


class CommentSchema(EntitySchema):
    """Comment component for Looptube"""

    com_id: str | None = Field(
        title="Comment ID",
        description="The id of the comment",
        examples=["dQw4w9WgXcQ"],
        default=None,
    )
    com_author: str | None = Field(
        title="Comment Author",
        description="The author of the comment",
        examples=["Rick Astley"],
        default=None,
    )
    com_text: str = Field(
        ...,
        title="Comment Text",
        description="The text of the comment",
        examples=["Rick Astley - Never Gonna Give You Up"],
    )
    com_published: float | None = Field(
        title="Comment Published",
        description="The published date of the comment",
        examples=[1714339200],
        default=None,
    )
    com_likes: int | None = Field(
        title="Comment Likes",
        description="The likes of the comment",
        examples=[1000],
        default=None,
    )
    com_in_reply_to: str | None = Field(
        title="Comment In Reply To",
        description="The id of the comment this comment is in reply to",
        examples=["dQw4w9WgXcQ"],
        default=None,
    )
