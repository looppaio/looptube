import re
from pathlib import Path
import yaml
import json
from functools import cached_property, lru_cache
from typing import Self
from pydantic import model_validator, AnyHttpUrl

from looptube.entities.schema import VideoSchema
from .base import LTEntity


class Video(LTEntity[VideoSchema]):
    """Video component for Looptube"""

    __schema__ = VideoSchema
    __clicks__ = [r".*Accept.*", "...more"]
    __wait_fors__ = ["ytd-comments-header-renderer", "yt-formatted-string"]

    @cached_property
    def _inpr(self) -> dict | None:
        if yt_details := self.pq(
            "body script:contains('var ytInitialPlayerResponse =')"
        ):
            for detail in yt_details.items():
                script_text = (
                    detail.text()
                    .strip("var ytInitialPlayerResponse =")
                    .strip(";")
                    .split(";var")[0]
                    .strip()
                )

                try:
                    return yaml.safe_load(script_text)
                except json.JSONDecodeError as e:
                    print(e)
                    continue
        return None

    @cached_property
    def _vds(self) -> dict:
        return self._inpr.get("videoDetails", {})

    @cached_property
    def _vmf(self) -> dict:
        return self._inpr.get("microformat", {}).get("playerMicroformatRenderer", {})

    @cached_property
    def _url(self) -> AnyHttpUrl:
        if canonical := self.pq("link[rel*='canonical']").attr("href"):
            return AnyHttpUrl(canonical)
        return AnyHttpUrl(self.url)

    @lru_cache(maxsize=1)
    def vid_id(self) -> str:
        if vid_id := self._vds.get("videoId"):
            return vid_id
        return (
            str(self._url)
            .rstrip("/")
            .split("/")[-1]
            .strip()
            .split("?v=")[-1]
            .split("&")[0]
            .strip()
        )

    @lru_cache(maxsize=1)
    def vid_channel_id(self) -> str | None:
        if channel_id := self._vds.get("channelId"):
            return channel_id
        return None

    @lru_cache(maxsize=1)
    def vid_title(self) -> str | None:
        return self._vds.get("title", None)

    @lru_cache(maxsize=1)
    def vid_description(self) -> str | None:
        return self._vmf.get("description", {}).get("simpleText", None)

    @lru_cache(maxsize=1)
    def vid_categories(self) -> str | None:
        if category := self._vmf.get("category", self._vmf.get("categories", None)):
            if isinstance(category, list):
                return [
                    k
                    for j in [re.split(r"\|\&| and |\+", c) for c in category]
                    for k in j
                ]
            return [i.strip().lower() for i in re.split(r"\|\&| and |\+", category)]
        return None

    @lru_cache(maxsize=1)
    def vid_author(self) -> str | None:
        return self._vds.get("author", None)

    @lru_cache(maxsize=1)
    def vid_uploaded(self) -> float | None:
        if pub_date := self._vmf.get("uploadDate", None):
            return self.parse_datetime(pub_date)

    @lru_cache(maxsize=1)
    def vid_published(self) -> float | None:
        if pub_date := self._vmf.get("publishDate", None):
            return self.parse_datetime(pub_date)

    @lru_cache(maxsize=1)
    def vid_duration(self) -> int | None:
        if vid_secs := self._vds.get("lengthSeconds", None):
            return int(vid_secs)
        return None

    @lru_cache(maxsize=1)
    def vid_thumbnails(self) -> list[str] | None:
        if thumbnails := self._vds.get("thumbnail", {}).get("thumbnails", None):
            thumbs = [t.get("url", None) for t in thumbnails]
            thumbs = list(set(filter(bool, thumbs)))
            if len(thumbs) > 0:
                return thumbs
        return None

    @lru_cache(maxsize=1)
    def vid_views(self) -> int | None:
        if views := self._vds.get("viewCount", None):
            return int(views)
        return None

    @lru_cache(maxsize=1)
    def vid_likes(self) -> int | None:
        if like_count := self._vmf.get("likeCount", None):
            return int(like_count)

    @lru_cache(maxsize=1)
    def vid_keywords(self) -> list[str] | None:
        if keywords := self._vds.get("keywords", None):
            return keywords
        if keywords := self.pq("meta[name*='keywords']").attr("content"):
            k = [i.lower().strip() for i in re.split(r",|\&|", keywords)]
            return list(set(filter(bool, k)))
        return None

    @lru_cache(maxsize=1)
    def vid_comments_count(self) -> int | None:
        if (
            comments_count := self.pq(
                "ytd-comments-header-renderer div#title h2#count yt-formatted-string span"
            )
            .eq(0)
            .text()
        ):
            return int(comments_count.strip())
        return None

    @lru_cache(maxsize=1)
    def vid_available_countries(self) -> list[str] | None:
        if available_countries := self._vmf.get("availableCountries", None):
            return available_countries
        return None

    @model_validator(mode="after")
    def validate_url(self) -> Self:
        if not self._inpr:
            raise ValueError(f"Failed to get script from {self.url}")
        return self

    def download(self) -> Path:
        """Download the video"""
        return self.ltr.download(self.url)

    def transcribe(self) -> str:
        """Transcribe the video"""
        return "Transcribed"

    def translate(self) -> str:
        """Translate the video"""
        return "Translated"

    def embed(self) -> list[list[float]]:
        """Embed the video"""
        return [[0, 1], [2, 3]]

    def summarize(self) -> str:
        """Summarize the video"""
        return "Summarized"
