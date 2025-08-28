from functools import cached_property
from dataclasses import dataclass

from unittest import mock
import pytest

from pydantic import AnyHttpUrl
from looptube.entities import Channel, Video, Playlist


@pytest.fixture(
    scope="session",
    params=[
        (
            Video,
            AnyHttpUrl("https://www.youtube.com/watch?v=dGf9JZSJGog"),
        ),
        (
            Channel,
            AnyHttpUrl("https://www.youtube.com/@NewStatesman"),
        ),
        (
            Playlist,
            AnyHttpUrl(
                "https://www.youtube.com/playlist?list=PLSfumUEfFlcIN_cm531aURNLfjvx8jTCo"
            ),
        ),
    ],
)
def entity_fixture(request):
    return request.param
