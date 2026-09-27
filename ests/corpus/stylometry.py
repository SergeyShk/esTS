from collections import Counter
from collections.abc import Sequence

from anyts.corpus.stylometry import (
    ZERO_SEGMENTS as ZERO_SEGMENTS,
    ZetaScore as ZetaScore,
    delta as delta,
    delta_profiles as delta_profiles,
    frequency_table as frequency_table,
    kilgarriff_chi2 as kilgarriff_chi2,
    mendenhall_curve as mendenhall_curve,
    mendenhall_distance as mendenhall_distance,
    z_scores as z_scores,
    zeta as zeta,
)
from spacy.language import Language
from spacy.tokens import Doc

from ..constants import FUNCTION_UD_POS
from ..exceptions import SourceError
from ..utils import check_sequence, get_nlp, is_punctuation, iter_doc_tokens

# Components the parts of speech of a list of words do not need
UNUSED_COMPONENTS = ["parser", "lemmatizer", "ner"]
# A list of words is tagged in chunks to bound the memory; the margin of context is
# wider than what the encoder sees, so the tags are those of the whole list
CHUNK_SIZE = 1000
CHUNK_MARGIN = 16


def function_words_profile(
    source: Sequence[str] | Doc, nlp: Language | None = None
) -> dict[str, float]:
    """
    Computing the profile of the function words - the shares of the function parts of speech

    Description:
        The shares of the parts of speech of FUNCTION_UD_POS among the words
        of the text. A Doc keeps its own tags; the words of a list or of an
        untagged Doc are tagged by the model in context, so they go in the
        order of the text; punctuation helps the tagging and is not counted.
        The negation no is an adverb in Spanish UD, so PART is rare

    Arguments:
        source (list[str]|Doc): Words of the text or Doc object
        nlp (Language): Pipeline for a list of words; None - the default model

    Returns:
        dict[str, float]: Shares by the parts of speech of FUNCTION_UD_POS

    Raises:
        SourceTypeError: If a string is passed instead of a list of words
        SourceError: If there are no words or the pipeline does not tag the
            parts of speech
        DatasetNotFoundError: If the default model is not installed

    Example:
        >>> from ests.corpus import function_words_profile
        >>> profile = function_words_profile("el gato duerme en la casa".split())
        >>> profile["DET"], profile["ADP"]
        (0.3333333333333333, 0.16666666666666666)
    """
    if isinstance(source, Doc) and source.has_annotation("POS"):
        tags = [token.pos_ for token in iter_doc_tokens(source)]
    else:
        if isinstance(source, Doc):
            words = [token.text for token in source if not token.is_space]
        else:
            check_sequence(source)
            words = [word for word in source if word.strip()]
        tags = _tag_words(words, nlp)
    if not tags:
        raise SourceError("The data source has no words")
    counts = Counter(tags)
    return {pos: counts[pos] / len(tags) for pos in FUNCTION_UD_POS}


def _tag_words(words: Sequence[str], nlp: Language | None) -> list[str]:
    """Parts of speech of the words that are not punctuation, tagged by the model in context"""
    if all(is_punctuation(word) for word in words):
        return []
    pipeline = nlp or get_nlp()
    starts = range(0, len(words), CHUNK_SIZE)
    chunks = (
        Doc(
            pipeline.vocab,
            words=[
                str(word)
                for word in words[max(start - CHUNK_MARGIN, 0) : start + CHUNK_SIZE + CHUNK_MARGIN]
            ],
        )
        for start in starts
    )
    tags: list[str] = []
    # One chunk at a time: a larger batch holds the activations of all its chunks at once
    for start, doc in zip(
        starts, pipeline.pipe(chunks, disable=UNUSED_COMPONENTS, batch_size=1), strict=True
    ):
        if not doc.has_annotation("POS"):
            raise SourceError("The pipeline does not tag the parts of speech")
        offset = min(start, CHUNK_MARGIN)
        tags.extend(
            token.pos_
            for token in doc[offset : offset + CHUNK_SIZE]
            if not is_punctuation(token.text)
        )
    return tags
