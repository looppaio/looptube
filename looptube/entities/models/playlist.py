from functools import cached_property, lru_cache
from pydantic import AnyHttpUrl
from joblib import Parallel, delayed

from looptube.entities.schema import PlaylistSchema
from .base import LTEntity


class Playlist(LTEntity[PlaylistSchema]):
    """Playlist component for Looptube"""

    __schema__ = PlaylistSchema
    __clicks__ = [r".*Accept.*", "...more"]
    __wait_fors__ = ["ytd-playlist-video-list-renderer"]
    __max_scroll__ = -1

    @cached_property
    def _pmf(self) -> dict | None:
        if self._yt_initial_data:
            return self._yt_initial_data.get("microformat", {}).get(
                "microformatDataRenderer"
            )

    @cached_property
    def _psb(self) -> dict | None:
        if self._yt_initial_data:
            if sidebar := self._yt_initial_data.get("sidebar"):
                if view := sidebar.get("playlistSidebarRenderer"):
                    if items := view.get("items"):
                        if isinstance(items, list):
                            item = items[0]
                            return item.get("playlistSidebarPrimaryInfoRenderer")
                    return view.get("playlistSidebarSecondaryInfoRenderer")
        return None

    @lru_cache(maxsize=1)
    def pyl_canonical(self) -> AnyHttpUrl:
        """Get the canonical URL of the playlist"""
        if self._pmf:
            if canonical := self._pmf.get("urlCanonical"):
                return AnyHttpUrl(canonical)

        if canonical := self.pq("link[rel*='canonical']").attr("href"):
            return AnyHttpUrl(canonical)
        raise ValueError(f"No canonical URL found for {self.url}")

    @lru_cache(maxsize=1)
    def pyl_title(self) -> str | None:
        """Get the title of the playlist"""
        if self._pmf:
            if title := self._pmf.get("title"):
                return title
        if title := self.pq("title").text():
            return title
        return None

    @lru_cache(maxsize=1)
    def pyl_description(self) -> str | None:
        """Get the description of the playlist"""
        if self._psb:
            if description := self._psb.get("description", {}).get("simpleText"):
                if bool(description):
                    return description
        if self._pmf:
            if description := self._pmf.get("description"):
                if bool(description):
                    return description

        return None

    @lru_cache(maxsize=1)
    def pyl_videos(self) -> list[AnyHttpUrl] | None:
        """Get the videos of the playlist"""
        videos = [
            i.attr("href")
            for i in self.pq(
                "ytd-playlist-video-list-renderer ytd-playlist-video-renderer :header a"
            ).items()
        ]
        videos = list(filter(bool, videos))
        videos = list(map(lambda x: AnyHttpUrl(x.split("&")[0]), videos))
        return videos or None
