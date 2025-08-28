import re
from pydantic import Field, AnyHttpUrl, computed_field

from looptube.core import LTEntityType

from .base import EntitySchema


class ChannelSchema(EntitySchema):
    """Channel component for Looptube"""

    ent_tag: LTEntityType = Field(
        title="Entity Type",
        description="The type of the entity",
        examples=[LTEntityType.CHANNEL],
        default=LTEntityType.CHANNEL,
    )

    @computed_field(
        title="Channel ID",
        description="The feed of the channel",
        examples=["UC-9-kyTWdEJ-9slrvT-veyaw"],
    )
    @property
    def chn_id(self) -> str:
        match = re.search(r"/channel/([^?]+)", str(self.chn_canonical))
        return match.group(1).strip()

    @computed_field(
        title="Channel URL",
        description="The url of the channel",
        examples=["UC-9-kyTWdEJ-9slrvT-veyaw"],
    )
    @property
    def chn_url(self) -> AnyHttpUrl:
        return self.ent_url

    chn_canonical: AnyHttpUrl = Field(
        title="Channel Canonical URL",
        description="The canonical url of the channel",
        examples=[
            AnyHttpUrl("https://www.youtube.com/channel/UC-9-kyTWdEJ-9slrvT-veyaw")
        ],
    )
    chn_title: str | None = Field(
        title="Channel Title",
        description="The title of the channel",
        examples=["Rick Astley"],
        default=None,
    )
    chn_description: str | None = Field(
        title="Channel Description",
        description="The description of the channel",
        examples=["Rick Astley"],
        default=None,
    )
    chn_about: str | None = Field(
        title="Channel About",
        description="The about of the channel",
        examples=["Rick Astley"],
        default=None,
    )
    chn_author: str | None = Field(
        title="Channel Author",
        description="The author of the channel",
        examples=["@rickastley"],
        default=None,
    )
    chn_country: str | None = Field(
        title="Channel Country",
        description="The country of the channel",
        examples=["United States"],
        default=None,
    )
    chn_joined: float | None = Field(
        title="Channel Joined",
        description="The joined date of the channel",
        examples=[1714339200],
        default=None,
    )
    chn_subscribers: str | None = Field(
        title="Channel Subscribers",
        description="The subscribers of the channel",
        examples=["1k subscribers"],
        default=None,
    )
    chn_videos_count: int | None = Field(
        title="Channel Videos",
        description="The videos of the channel",
        examples=[1000],
        default=None,
    )
    chn_views: int | None = Field(
        title="Channel Views",
        description="The views of the channel",
        examples=[1000],
        default=None,
    )
    chn_external_links: list[AnyHttpUrl] | None = Field(
        title="Channel External Links",
        description="The external links of the channel",
        examples=[
            [AnyHttpUrl("https://www.youtube.com/channel/UC-9-kyTWdEJ-9slrvT-veyaw")]
        ],
        default=None,
    )
    chn_categories: list[str] | None = Field(
        title="Channel Categories",
        description="The categories of the channel",
        examples=[["Music", "Entertainment"]],
        default=None,
    )
    chn_hashtags: list[str] | None = Field(
        title="Channel Hashtags",
        description="The hashtags of the channel",
        examples=[["#Music", "#Entertainment"]],
        default=None,
    )
    chn_available_countries: list[str] | None = Field(
        title="Channel Available Countries",
        description="The available countries of the channel",
        examples=[["United States", "Canada"]],
        default=None,
    )
    chn_feed_link: AnyHttpUrl | None = Field(
        title="Channel Feed",
        description="The feed of the channel",
        examples=[
            AnyHttpUrl(
                "https://www.youtube.com/feeds/videos.xml?channel_id=UCeRxxz9ByOqdd8A-0iF_Idg"
            )
        ],
        default=None,
    )

    chn_videos: list[AnyHttpUrl] | None = Field(
        title="Channel Latest Videos",
        description="The latest videos of the channel",
        examples=[
            [AnyHttpUrl("https://www.youtube.com/watch?v=dQw4w9WgXcQ")]
        ],
        default=None,
    )

    chn_has_podcasts: bool = Field(
        title="Channel Has Podcasts",
        description="Whether the channel has podcasts",
        examples=[True],
        default=False,
    )

    chn_has_shorts: bool = Field(
        title="Channel Has Shorts",
        description="Whether the channel has shorts",
        examples=[True],
        default=False,
    )

    chn_has_playlists: bool = Field(
        title="Channel Has Playlists",
        description="Whether the channel has playlists",
        examples=[True],
        default=False,
    )

    chn_has_posts: bool = Field(
        title="Channel Has Posts",
        description="Whether the channel has posts",
        examples=[True],
        default=False,
    )
