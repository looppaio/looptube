from pydantic import Field, AnyHttpUrl, computed_field

from looptube.core import LTEntityType

from .base import EntitySchema


class PlaylistSchema(EntitySchema):
    """Playlist component for Looptube"""

    ent_tag: LTEntityType = Field(
        title="Entity Type",
        description="The type of the entity",
        examples=[LTEntityType.PLAYLIST],
        default=LTEntityType.PLAYLIST,
    )

    @computed_field(
        title="Playlist ID",
        description="The id of the playlist",
        examples=["PL-9-kyTWdEJ-9slrvT-veyaw"],
    )
    @property
    def pyl_id(self) -> str:
        return str(self.pyl_canonical).split("/playlist/")[-1].split("?")[0].strip()

    @computed_field(
        title="Playlist URL",
        description="The url of the playlist",
        examples=["PL-9-kyTWdEJ-9slrvT-veyaw"],
    )
    @property
    def pyl_url(self) -> AnyHttpUrl:
        return self.ent_url

    pyl_canonical: AnyHttpUrl = Field(
        title="Playlist Canonical URL",
        description="The canonical url of the playlist",
        examples=[
            AnyHttpUrl(
                "https://www.youtube.com/playlist?list=PL-9-kyTWdEJ-9slrvT-veyaw"
            )
        ],
    )
    pyl_title: str | None = Field(
        title="Playlist Title",
        description="The title of the playlist",
        examples=["Rick Astley"],
        default=None,
    )
    pyl_description: str | None = Field(
        title="Playlist Description",
        description="The description of the playlist",
        examples=["Rick Astley"],
        default=None,
    )
    pyl_videos: list[AnyHttpUrl] | None = Field(
        title="Playlist Videos",
        description="The videos of the playlist",
        examples=[
            [
                AnyHttpUrl("https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
                AnyHttpUrl("https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
            ]
        ],
        default=None,
    )

    @computed_field(
        title="Playlist Videos Count",
        description="The videos count of the playlist",
        examples=[10],
    )
    @property
    def pyl_videos_count(self) -> int | None:
        if self.pyl_videos:
            return len(self.pyl_videos)
        return None
