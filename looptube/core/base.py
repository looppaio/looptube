"""This module contains the base classes for the Looptube project."""

from __future__ import annotations

import os
import logging
from uuid import uuid4, UUID
from hashlib import blake2b
from datetime import datetime, UTC
from dateutil.parser import parse
from queue import PriorityQueue
from enum import Enum
from pathlib import Path
from typing import ClassVar, Optional, Self, Any, TypeVar, Literal
from pydantic import computed_field, BaseModel, EmailStr, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from polyfactory.factories.pydantic_factory import ModelFactory

LOGGER = logging.getLogger(__name__)

T = TypeVar("T")
S = TypeVar("S", bound="LTSchema")


class LTEnum(Enum):
    """Base class for all enums."""

    @classmethod
    def choices(cls) -> list[str]:
        """
        Return a list of all choices in the enumeration.
        """
        return [choice.value for choice in cls]


class _Base:
    @classmethod
    def now(cls, **kwargs) -> datetime:
        """Return the current time in UTC."""
        return datetime.now(UTC)

    @classmethod
    def get_uuid(cls, **kwargs) -> str:
        """Return a unique identifier."""
        return str(uuid4())

    @classmethod
    def make_id(cls, data: Any = None, **kwargs) -> UUID:
        """Return a unique identifier for the model."""
        if data:
            return UUID(blake2b(str(data).encode(), digest_size=16).hexdigest())
        return cls.get_uuid()

    @classmethod
    def parse_datetime(cls, date_str: str, **kwargs) -> float | None:
        """Parse a datetime string and return a float."""
        try:
            return parse(date_str, fuzzy=True).astimezone(UTC).timestamp()
        except Exception as e:
            return None


class LTConfig(_Base):
    """Base configuration for Looptube"""

    ...


class LTSettings(BaseSettings, _Base):
    """Base settings for the application."""

    # TODO: Add secrets source SecretsSettingsSource
    # https://docs.pydantic.dev/latest/concepts/pydantic_settings/#parsing-environment-variable-values

    model_config = SettingsConfigDict(
        use_enum_values=True,
        case_sensitive=True,
        extra="ignore",
    )

    # Base Config
    lt_home: Optional[str] = "~/.looptube"
    cache_capacity: Optional[int] = 10000
    log_level: Optional[Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]] = (
        "DEBUG"
    )
    goog_acc_email: Optional[str] | None = None
    goog_acc_password: Optional[str] | None = None
    gcp_project_id: Optional[str] | None = None
    gcp_api_key: Optional[str] | None = None
    gcp_service_account: Optional[str] | None = None

    # AI Config
    openai_api_key: Optional[str] | None = None
    gemini_api_key: Optional[str] | None = None
    anthropic_api_key: Optional[str] | None = None
    groq_api_key: Optional[str] | None = None
    hf_api_key: Optional[str] | None = None

    # Network Config
    concurrent_requests: Optional[int] | None = 10
    concurrent_jobs: Optional[int] | None = 10
    request_timeout: Optional[int] | None = 30000
    selector_timeout: Optional[int] | None = 1000

    @computed_field
    @property
    def lt(self) -> Path:
        return Path(self.lt_home).expanduser()

    @computed_field
    @property
    def cache(self) -> Path:
        return self.lt / ".cache"

    @computed_field
    @property
    def storage(self) -> Path:
        return self.cache / ".storage"

    @computed_field
    @property
    def logs(self) -> Path:
        return self.cache / ".logs"

    @computed_field
    @property
    def ml(self) -> Path:
        return self.cache / ".ml"

    def has_goog_credentials(self) -> bool:
        return bool(self.goog_acc_email and self.goog_acc_password)

    def has_gcp_credentials(self) -> bool:
        return bool(
            self.gcp_project_id and self.gcp_api_key and self.gcp_service_account
        )


class LTFactory[S](_Base):
    def __init__(self, model: S, **kwargs: Any):
        super().__init__(**kwargs)
        self.model: S = model

    def create(
        self, use_examples: bool = True, is_base_factory: bool = True, **kwargs: Any
    ) -> type[ModelFactory[S]]:
        class _Factory(ModelFactory[self.model]):
            __model__ = self.model
            __use_examples__ = use_examples
            __is_base_factory__ = is_base_factory

        return _Factory


class LTSchema(BaseModel, _Base):
    """Base schema for Looptube"""

    model_config = dict(
        use_enum_values=True,
        json_encoders={
            EmailStr: str,
            AnyHttpUrl: str,
            UUID: str,
            Enum: lambda x: x.value,
        },
    )

    @classmethod
    def mock_me(cls, **kwargs: Any) -> Self:
        """Create a mock instance of the schema class."""

        factory = LTFactory[cls](cls).create()
        return factory.build(**kwargs)


class LTModel(_Base):
    """Base model for Looptube"""

    REGISTRY: ClassVar[dict[str, type[LTModel]]] = dict()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        for k, _ in LTSettings.model_fields.items():
            if hasattr(cls, k):
                os.environ[k] = getattr(cls, k)

        if not getattr(cls, "__env__", None):
            cls.__env__: LTSettings = LTSettings()

        for cache_store in ("lt", "cache", "storage", "logs", "ml"):
            _cs: Path = getattr(cls.__env__, cache_store)
            if not _cs.exists():
                _cs.mkdir(parents=True, exist_ok=True)

        cls.__files_store__ = cls.__env__.storage / ".files"
        cls.__images_store__ = cls.__files_store__ / ".images"
        cls.__audio_store__ = cls.__files_store__ / ".audios"
        cls.__video_store__ = cls.__files_store__ / ".videos"
        cls.__docs_store__ = cls.__files_store__ / ".docs"

        for store in (
            cls.__files_store__,
            cls.__images_store__,
            cls.__audio_store__,
            cls.__video_store__,
            cls.__docs_store__,
        ):
            if not store.exists():
                store.mkdir(parents=True, exist_ok=True)

        cls.__log_stream__ = cls.__env__.logs / f"{datetime.now(UTC).isoformat()}.log"

        if not getattr(cls, "__log_level__", None):
            cls.__log_level__ = cls.__env__.log_level

        if not (
            getattr(cls, "__logger__", None)
            and isinstance(cls.__logger__, logging.Logger)
        ):
            cls.__logger__: logging.Logger = LOGGER
            cls.__logger__.setLevel(cls.__log_level__)

            _handler = logging.StreamHandler(
                stream=cls.__log_stream__.open("w", encoding="utf-8"),
            )
            _handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            cls.__logger__.addHandler(_handler)

        cls.REGISTRY[cls.__name__] = cls


class LTQueue[T](LTModel):
    """Local Cache for Looptube"""

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.tree: PriorityQueue[T] = PriorityQueue()

    def add(self, priority: Any, item: T) -> None:
        """Add a file to the queue"""
        self.tree.put((priority, item))

    def delete(self, **kwargs: Any) -> tuple[Any, T]:
        """Delete a file from the queue"""
        return self.tree.get()

    def clear(self, **kwargs: Any) -> None:
        """Clear the queue"""
        self.tree.queue.clear()


"""
from dataclasses import dataclass, asdict


class Symbol: ...
S = TypeVar("S", bound=Symbol)

class LTBuilder[F1:S, F2:S]:

    @staticmethod
    def new() -> "LTBuilder[S, S]":
        return LTBuilder[S, S]()

@dataclass
class Python:
  f1: str
  f2: str


@dataclass(kw_only=True)
class PythonBuilder[F1:Symbol,F2:Symbol]:
  f1: str = ""
  f2: str = ""

  @staticmethod
  def new() -> "PythonBuilder[Disallow, Disallow]":
    return PythonBuilder()

  def set_f1(self, val: str):
    return PythonBuilder[Allow, F2](**dict(asdict(self), f1=val))

  def set_f2(self, val: str):
    return PythonBuilder[F1, Allow](**dict(asdict(self), f2=val))

  @classmethod
  def build(cls, inner: "PythonBuilder[Allow, Allow]") -> Python:
    # Do the thing that makes the Python
    return Python(f1=inner.f1, f2=inner.f2)


PythonBuilder.build(PythonBuilder.new().set_f1("a").set_f2("b"))
PythonBuilder.build(PythonBuilder.new().set_f1("a"))
PythonBuilder.build(PythonBuilder.new().set_f2("b"))
PythonBuilder.build(PythonBuilder.new())"""
