from pydantic import Field, AnyHttpUrl, computed_field
from looptube.core import (
    LTVideoType,
)

from .base import EntitySchema
from .comment import CommentSchema


class VideoSchema(EntitySchema):
    """Video component for Looptube"""

    vid_id: str = Field(
        title="Video ID",
        description="The id of the video",
        examples=["dQw4w9WgXcQ"],
    )

    vid_channel_id: str | None = Field(
        title="Channel ID",
        description="The id of the channel",
        examples=["UC-9-kyTWdEJ-9slrvT-veyaw"],
        default=None,
    )

    @computed_field(
        title="Video URL",
        description="The URL of the video",
        examples=[AnyHttpUrl("https://www.youtube.com/watch?v=dQw4w9WgXcQ")],
    )
    @property
    def vid_url(self) -> AnyHttpUrl:
        return self.ent_url

    @computed_field(
        title="Video Embed URL",
        description="The Embed URL of the video",
        examples=[AnyHttpUrl("https://www.youtube.com/embed/dQw4w9WgXcQ")],
    )
    @property
    def vid_embed_url(self) -> AnyHttpUrl:
        return AnyHttpUrl(f"https://www.youtube.com/embed/{self.vid_id}")

    vid_type: LTVideoType = Field(
        title="Video Type",
        description="The type of the video",
        examples=[LTVideoType.VIDEO],
        default=LTVideoType.VIDEO,
    )

    vid_title: str | None = Field(
        title="Video Title",
        description="The title of the video",
        examples=["Rick Astley - Never Gonna Give You Up"],
        default=None,
    )
    vid_description: str | None = Field(
        title="Video Description",
        description="The description of the video",
        examples=["Rick Astley - Never Gonna Give You Up"],
        default=None,
    )
    vid_author: str | None = Field(
        title="Video Author",
        description="The author of the video",
        examples=["Rick Astley"],
        default=None,
    )
    vid_uploaded: float | None = Field(
        title="Video Uploaded",
        description="The uploaded date of the video",
        examples=[1714339200],
        default=None,
    )
    vid_published: float | None = Field(
        title="Video Published",
        description="The published date of the video",
        examples=[1714339200],
        default=None,
    )
    vid_duration: int = Field(
        title="Video Duration",
        description="The duration of the video",
        examples=[120],
    )
    vid_thumbnails: list[str] | None = Field(
        title="Video Thumbnails",
        description="The thumbnails of the video",
        examples=[["https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg"]],
        default=None,
    )
    vid_views: int | None = Field(
        title="Video Views",
        description="The views of the video",
        examples=[1000],
        default=None,
    )
    vid_likes: int | None = Field(
        title="Video Likes",
        description="The likes of the video",
        examples=[1000],
        default=None,
    )
    vid_categories: list[str] | None = Field(
        title="Video Categories",
        description="The categories of the video",
        examples=[["Music", "Entertainment"]],
        default=None,
    )
    vid_keywords: list[str] | None = Field(
        title="Video Keywords",
        description="The keywords of the video",
        examples=[["Rick Astley", "Never Gonna Give You Up"]],
        default=None,
    )

    @computed_field(
        title="Video Hashtags",
        description="The hashtags of the video",
        examples=[["Rick Astley", "Never Gonna Give You Up"]],
    )
    @property
    def vid_hashtags(self) -> list[str] | None:
        if not self.vid_description:
            return None
        return list(
            map(
                lambda x: x.strip().rstrip("."),
                filter(
                    lambda x: x.strip().startswith("#"), self.vid_description.split()
                ),
            )
        )

    vid_available_countries: list[str] | None = Field(
        title="Video Available Countries",
        description="The countries where the video is available",
        examples=[["United States", "United Kingdom"]],
        default=None,
    )
    vid_external_urls: list[AnyHttpUrl] | None = Field(
        title="Video External URLs",
        description="The external urls of the video",
        examples=[
            [
                AnyHttpUrl("https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
                AnyHttpUrl("https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
            ],
        ],
        default=None,
    )
    vid_comments_count: int | None = Field(
        title="Video Comments Count",
        description="The number of comments on the video",
        examples=[1000],
        default=None,
    )
    vid_comments: list[CommentSchema] | None = Field(
        title="Video Comments",
        description="The comments on the video",
        examples=[[CommentSchema.mock_me() for _ in range(2)]],
        default=None,
    )


class ShortSchema(VideoSchema):
    """Short component for Looptube"""

    # TODO: Change Pydantic field names

    vid_type: LTVideoType = Field(
        title="Video Type",
        description="The type of the video",
        examples=[LTVideoType.SHORT],
        default=LTVideoType.SHORT,
    )
