import re
import json
from typing import ClassVar, Callable
from functools import cached_property
from pydantic import AnyHttpUrl
from pyquery import PyQuery
import inspect
from functools import lru_cache


from looptube.core import LTModel
from looptube.network import LTRequest


class LTEntity[S](LTModel):
    """Base component for Looptube"""

    __schema__: ClassVar[Callable[..., S]]
    __clicks__: ClassVar[list[str]] = []
    __wait_fors__: ClassVar[list[str]] = []
    __scroll__: ClassVar[bool] = True
    __headless__: ClassVar[bool] = True
    __max_scroll__: ClassVar[int] = 2

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if not getattr(cls, "__schema__", None):
            raise ValueError(
                f"Subclass {cls.__name__} must define a __schema__ attribute"
            )

    def __init__(self, url: str, pq: PyQuery | None = None):
        self.url = url
        self._pq = pq

    @cached_property
    def _yt_initial_data(self) -> dict:
        if script := self.pq("script:contains('var ytInitialData =')"):
            script_text = script.text()
            if match := re.search(r"var ytInitialData = (.*)}", script_text):
                match_text = match.group(0).split("var ytInitialData = ")[-1].strip()
                return json.loads(match_text)
        return None

    @lru_cache(maxsize=1)
    def ent_url(self) -> AnyHttpUrl:
        return self.url

    @cached_property
    def ltr(self) -> LTRequest:
        return LTRequest(
            clicks=self.__clicks__,
            scroll=self.__scroll__,
            headless=self.__headless__,
            wait_fors=self.__wait_fors__,
            max_scroll=self.__max_scroll__,
        )

    @cached_property
    def pq(self) -> PyQuery:
        if self._pq:
            return self._pq
        if response := self.ltr.run(self.url):
            return PyQuery(response).make_links_absolute(self.url)
        raise ValueError(f"Failed to get response from {self.url}")

    @lru_cache(maxsize=1)
    def build(self) -> S:
        item = dict()

        schema_fields = list(self.__schema__.model_fields.keys())
        for name, func in inspect.getmembers(self, predicate=inspect.ismethod):
            if name in schema_fields:
                item[name] = func()
        return self.__schema__(**item)

    @lru_cache(maxsize=1)
    def to_json(self) -> dict:
        return self.build().model_dump(mode="json")

    def get_cookie_jar(self) -> list:
        return self.ltr.COOKIE_JAR

    def get_local_storage(self) -> dict:
        return self.ltr.LOCAL_STORAGE

    def get_session_storage(self) -> dict:
        return self.ltr.SESSION_STORAGE
