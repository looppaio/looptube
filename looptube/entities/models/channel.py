from pyquery import PyQuery
from functools import cached_property, lru_cache
from pydantic import AnyHttpUrl
from joblib import Parallel, delayed
import feedparser

from urllib.parse import unquote
from looptube.entities.schema import ChannelSchema
from .base import LTEntity


class Channel(LTEntity[ChannelSchema]):
    """Channel component for Looptube"""

    __schema__ = ChannelSchema
    __clicks__ = [r".*Accept.*", "...more"]
    __wait_fors__ = ["ytd-about-channel-renderer"]

    @cached_property
    def _chn_tabs(self) -> list[dict] | None:
        if self._yt_initial_data:
            if contents := self._yt_initial_data.get("contents", {}):
                render_key = list(
                    filter(lambda x: "ResultsRenderer" in x, contents.keys())
                )
                if render_key:
                    if render_data := contents.get(render_key[0], {}):
                        if tabs := render_data.get("tabs", []):
                            return tabs or None
        return None

    @cached_property
    def _chn_dts(self) -> dict:
        if self._yt_initial_data:
            if metadata := self._yt_initial_data.get("metadata"):
                return metadata.get("channelMetadataRenderer")
        return None

    @cached_property
    def _chn_cmf(self) -> dict | None:
        if self._yt_initial_data:
            if microformat := self._yt_initial_data.get("microformat"):
                return microformat.get("microformatDataRenderer")

    @cached_property
    def _about(self) -> PyQuery:
        return self.pq("ytd-about-channel-renderer div[id*='about-container']")

    @cached_property
    def _info(self) -> PyQuery:
        if self._about:
            return self._about("div[id*='additional-info-container'] table")

    @cached_property
    def _chn_pyl_tab(self) -> dict | None:
        if self._chn_tabs:
            pyl_tab = list(
                filter(lambda x: x.get("title") == "Playlists", self._chn_tabs)
            )
            if pyl_tab:
                return pyl_tab.pop()
        return None

    @cached_property
    def _chn_sht_tab(self) -> dict | None:
        if self._chn_tabs:
            sht_tab = list(filter(lambda x: x.get("title") == "Shorts", self._chn_tabs))
            if sht_tab:
                return sht_tab.pop()
        return None

    @cached_property
    def _chn_pod_tab(self) -> dict | None:
        if self._chn_tabs:
            pod_tab = list(
                filter(lambda x: x.get("title") == "Podcasts", self._chn_tabs)
            )
            if pod_tab:
                return pod_tab.pop()
        return None

    @cached_property
    def _chn_pst_tab(self) -> dict | None:
        if self._chn_tabs:
            pst_tab = list(filter(lambda x: x.get("title") == "Posts", self._chn_tabs))
            if pst_tab:
                return pst_tab.pop()
        return None

    @lru_cache(maxsize=1)
    def chn_canonical(self) -> AnyHttpUrl:
        """Get the canonical url of the channel"""
        if canonical := self.pq("link[rel='canonical']").attr("href"):
            return AnyHttpUrl(canonical)
        if self._chn_cmf:
            if canonical := self._chn_cmf.get("urlCanonical"):
                return AnyHttpUrl(canonical)
        raise ValueError(f"Failed to get canonical url from {self.url}")

    @lru_cache(maxsize=1)
    def chn_title(self) -> str | None:
        if self._chn_cmf:
            if title := self._chn_cmf.get("title"):
                return title
        if title := self.pq("meta[property*='og:title']").attr("content"):
            return title
        return None

    @lru_cache(maxsize=1)
    def chn_description(self) -> str | None:
        if self._chn_dts:
            if description := self._chn_dts.get("description"):
                return description
        if description := self.pq("meta[name*='description']").attr("content"):
            return description

    @lru_cache(maxsize=1)
    def chn_about(self) -> str | None:
        if self._about:
            return self._about("*[id*='description-container']").text().strip()

    @lru_cache(maxsize=1)
    def chn_author(self) -> str | None:
        if handheld := self.pq("link[rel*='alternate'][media*='handheld'][href*='/@']"):
            if author := handheld.attr("href"):
                return author.strip("/").split("/")[-1]
        return None

    @lru_cache(maxsize=1)
    def chn_country(self) -> str | None:
        if self._info:
            if c_icon := self._info("yt-icon[icon*='privacy_public']"):
                if country := c_icon.parent().siblings().eq(0).text().strip():
                    return country

    @lru_cache(maxsize=1)
    def chn_joined(self) -> float | None:
        if self._info:
            if j_icon := self._info("yt-icon[icon*='info_outline']"):
                if (
                    joined := j_icon.closest("*:contains('Joined ')")
                    .eq(0)
                    .text()
                    .strip()
                ):
                    return self.parse_datetime(joined.split("Joined ")[-1], fuzzy=True)

    @lru_cache(maxsize=1)
    def chn_subscribers(self) -> str | None:
        if self._info:
            if sub_icon := self._info("yt-icon[icon*='person_radar']"):
                if (
                    subs := sub_icon.closest("*:contains(' subscribers')")
                    .eq(0)
                    .text()
                    .strip()
                ):
                    return subs.split()[0].strip()

    @lru_cache(maxsize=1)
    def chn_videos_count(self) -> int | None:
        if self._info:
            if vc_icon := self._info("yt-icon[icon*='my_videos']"):
                if (
                    vid_count := vc_icon.closest("*:contains(' videos')")
                    .eq(0)
                    .text()
                    .strip()
                ):
                    return int("".join(filter(str.isdigit, vid_count)))

    @lru_cache(maxsize=1)
    def chn_views(self) -> int | None:
        if self._info:
            if vw_icon := self._info("yt-icon[icon*='trending_up']"):
                if (
                    view_count := vw_icon.closest("*:contains(' views')")
                    .eq(0)
                    .text()
                    .strip()
                ):
                    return int("".join(filter(str.isdigit, view_count)))

    @lru_cache(maxsize=1)
    def chn_categories(self) -> list[str] | None:
        return [
            i.attr("content") for i in self.pq("meta[property*='og:video:tag']").items()
        ] or None

    @lru_cache(maxsize=1)
    def chn_hashtags(self) -> list[str] | None:
        if self._chn_cmf:
            if hashtags := self._chn_cmf.get("hashtags"):
                return hashtags

    @lru_cache(maxsize=1)
    def chn_feed_link(self) -> AnyHttpUrl | None:
        if self._chn_dts:
            if feed := self._chn_dts.get("rssUrl"):
                return AnyHttpUrl(feed)

        if canonical := self.chn_canonical():
            chn_id = str(canonical).split("/")[-1].split("?")[0].strip("/").strip()
            return AnyHttpUrl(
                f"https://www.youtube.com/feeds/videos.xml?channel_id={chn_id}"
            )

    @lru_cache(maxsize=1)
    def chn_available_countries(self) -> list[str] | None:
        if self._chn_dts:
            if countries := self._chn_dts.get("availableCountryCodes"):
                return countries

    @lru_cache(maxsize=1)
    def chn_external_links(self) -> list[AnyHttpUrl] | None:
        if self._about:
            links = [
                i.attr("href")
                for i in self._about("yt-channel-external-link-view-model a").items()
            ]
            links = list(map(lambda h: unquote(h.split("q=")[-1]), filter(bool, links)))
            return [AnyHttpUrl(i) for i in links if i] or None

    @lru_cache(maxsize=1)
    def chn_videos(self) -> list[str] | None:
        if self.chn_feed:
            return [AnyHttpUrl(i.get("link")) for i in self.chn_feed.get("entries", [])]
        return None

    @cached_property
    def chn_feed(self) -> dict | None:
        if self.chn_feed_link:
            feed = feedparser.parse(str(self.chn_feed_link()))
            return feed

    @lru_cache(maxsize=1)
    def chn_has_podcasts(self) -> bool:
        return bool(self._chn_pod_tab)

    @lru_cache(maxsize=1)
    def chn_has_shorts(self) -> bool:
        return bool(self._chn_sht_tab)

    @lru_cache(maxsize=1)
    def chn_has_playlists(self) -> bool:
        return bool(self._chn_pyl_tab)

    @lru_cache(maxsize=1)
    def chn_has_posts(self) -> bool:
        return bool(self._chn_pst_tab)

    def download(self) -> list[str | bytes]:
        urls = list(filter(bool, [i.get("vid_url") for i in self.chn_latest_videos()]))
        return Parallel(n_jobs=-1)(delayed(self.ltr.download)(i) for i in urls)
