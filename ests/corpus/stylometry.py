from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from typing import TYPE_CHECKING, cast

from anyts.corpus.stylometry import (
    ZetaScore as ZetaScore,
    delta as delta,
    delta_profiles as delta_profiles,
    frequency_table as frequency_table,
    kilgarriff_chi2 as kilgarriff_chi2,
    mendenhall_curve as mendenhall_curve,
    mendenhall_distance as mendenhall_distance,
    rolling_delta as rolling_delta,
    z_scores as z_scores,
    zeta as zeta,
    zeta_segments as zeta_segments,
)
from anyts.document import get_tree
from anyts.utils import check_words, has_words, is_doc, is_document, is_punctuation

from ..constants import FUNCTION_UD_POS
from ..exceptions import SourceError
from ..utils import get_document, get_morph_analyzer

if TYPE_CHECKING:
    from spacy.tokens import Doc


def function_words_profile(source: Sequence[str] | Doc) -> dict[str, float]:
    """
    Computing the profile of the function words - the shares of the function parts of speech

    Description:
        The shares of the parts of speech of FUNCTION_UD_POS among the words
        of the text. A Doc keeps its own tags; the words of a list or of an
        untagged Doc get the parts of speech of esMorph in context, so they go
        in the order of the text; punctuation helps the analysis and is not
        counted. The negation no is an adverb in Spanish UD, so PART is rare

    Arguments:
        source (list[str]|Doc): Words of the text or Doc object

    Returns:
        dict[str, float]: Shares by the parts of speech of FUNCTION_UD_POS

    Raises:
        SourceTypeError: If the words are not a list of strings
        SourceError: If there are no words

    Example:
        >>> from ests.corpus import function_words_profile
        >>> profile = function_words_profile("el gato duerme en la casa".split())
        >>> profile["DET"], profile["ADP"]
        (0.3333333333333333, 0.16666666666666666)
    """
    if is_doc(source) or is_document(source):
        tree = get_tree(get_document(source))
        words = [word for word in tree.words if has_words(word.form)]
        if any(word.upos for word in words):
            tags = [word.upos or "" for word in words]
        else:
            tags = _tag_words([word.form for word in tree.words])
    else:
        check_words(source)
        tags = _tag_words([word for word in cast("Sequence[str]", source) if word.strip()])
    if not tags:
        raise SourceError("The data source has no words")
    counts = Counter(tags)
    return {pos: counts[pos] / len(tags) for pos in FUNCTION_UD_POS}


def _tag_words(words: Sequence[str]) -> list[str]:
    """Parts of speech of the words that are not punctuation, by esMorph in context; X for a
    word without analyses"""
    analyses = get_morph_analyzer().analyze_sentence(words)
    return [
        found[0].pos if found else "X"
        for word, found in zip(words, analyses, strict=True)
        if not is_punctuation(word)
    ]
