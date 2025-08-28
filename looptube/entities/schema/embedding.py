from pydantic import Field, AnyHttpUrl, computed_field

from dateutil.parser import parse
from joblib import Parallel, delayed
import feedparser

from .base import EntitySchema
from looptube.core import LTSchema


class EmbeddingMetadataSchema(EntitySchema):
    pass
