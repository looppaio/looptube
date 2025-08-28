from looptube.core import TextNLPMixin
from .base import EntitySchema


class TranscriptSchema(EntitySchema, TextNLPMixin):
    """Transcript component for Looptube"""

    pass
