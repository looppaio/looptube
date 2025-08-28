from functools import cached_property
from pydantic import computed_field
from textblob import TextBlob

from spacy import load, Language
from spacy.tokens import Doc


class TextNLPMixin:
    @cached_property
    def nlp(self) -> Language:
        return load("en_core_web_trf")

    @cached_property
    def doc(self) -> Doc:
        return self.nlp(self.content)

    @cached_property
    def blob(self) -> TextBlob:
        return TextBlob(self.content)

    @computed_field(
        title="Sentiment Polarity",
        description="The sentiment polarity of the text",
        examples=[0.1, -0.1],
    )
    @property
    def polarity(self) -> float:
        return self.blob.sentiment.polarity

    @computed_field(
        title="Sentiment Subjectivity",
        description="The sentiment subjectivity of the text",
        examples=[0.1, 0.9],
    )
    @property
    def subjectivity(self) -> float:
        return self.blob.sentiment.subjectivity

    @computed_field(
        title="Sentences",
        description="The sentences in the text",
        examples=[["Hello, world!"]],
    )
    @property
    def sentences(self) -> list[str]:
        sents = [sent.text for sent in self.doc.sents]
        return list(filter(lambda x: x.strip(), sents))

    @computed_field(
        title="Word Count",
        description="The number of words in the text",
        examples=[100],
    )
    @property
    def word_count(self) -> int:
        words = list(
            filter(
                lambda w: w.is_alpha
                and not (w.is_stop or w.is_punct or w.is_space or w.is_digit),
                self.doc,
            )
        )
        return len(words)

    @computed_field(
        title="Character Count",
        description="The number of characters in the text",
        examples=[100],
    )
    @property
    def char_count(self) -> int:
        return len(self.content)

    @computed_field(
        title="Average Word Length",
        description="The average length of the words in the text",
        examples=[5],
    )
    @property
    def avg_word_length(self) -> float:
        if self.word_count == 0:
            return 0
        return self.char_count / self.word_count

    @computed_field(
        title="Average Sentence Length",
        description="The average length of the sentences in the text",
        examples=[10],
    )
    @property
    def avg_sentence_length(self) -> float:
        if len(self.sentences) == 0:
            return 0
        return self.word_count / len(self.sentences)
