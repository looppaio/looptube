from .base import LTEnum

class LTEntityType(LTEnum):
    """Looptube Tags"""

    VIDEO = "vid"
    PLAYLIST = "pyl"
    POST = "pst"
    COMMENT = "com"
    USER = "usr"
    CHANNEL = "chn"
    EMBEDDING = "emb"
    TRANSCRIPT = "trs"

class LTVideoType(LTEnum):
    """Looptube Video Types"""

    VIDEO = "video"
    SHORT = "short"
    PODCAST = "podcast"


class LTCodec(LTEnum):
    """Looptube Codecs"""

    MP4 = "mp4"
    M4A = "m4a"
    MP3 = "mp3"


class LTProvider(LTEnum):
    """Looptube Providers"""

    OPENAI = "openai"
    GROQ = "groq"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    HUGGINGFACE = "huggingface"
