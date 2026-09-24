from collections import defaultdict
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Any

import pandas as pd
from graphviz import Digraph, nohtml

from ..exceptions import ParameterError, SourceError, SourceTypeError
from ..utils import check_sequence


class Direction(Enum):
    """Direction of a subtree of words from the keyword"""

    Forward = 1
    Backward = 2


@dataclass
class FreqNode:
    """Node of a word tree: the frequency of its N-gram and the following words"""

    freq: int
    children: dict[str, "FreqNode"]


class TreeDrawer:
    """
    Class for drawing a word tree

    Arguments:
        keyword (str): Keyword whose context is shown
        fwd_tree (FreqNode): Subtree after the keyword
        bwd_tree (FreqNode): Subtree before the keyword
        max_font_size (int): Largest size of the font
        min_font_size (int): Smallest size of the font
        font_interp (Callable): Function interpolating the size of the font

    Attributes:
        max_freq (int): Greatest frequency
        graph (Digraph): Directed graph

    Methods:
        interpolate_fontsize: Computing the size of the font of a node of the tree
        draw_subtree: Drawing a subtree of words
        draw: Drawing the word tree as a directed graph
    """

    def __init__(
        self,
        keyword: str,
        fwd_tree: FreqNode,
        bwd_tree: FreqNode,
        max_font_size: int = 30,
        min_font_size: int = 12,
        font_interp: Callable[[float], float] | None = None,
    ) -> None:
        self.keyword = keyword
        self.fwd_tree = fwd_tree
        self.bwd_tree = bwd_tree
        self.max_font_size = max_font_size
        self.min_font_size = min_font_size
        self.font_interp = font_interp
        self.max_freq = max(
            [t.freq for t in fwd_tree.children.values()]
            + [t.freq for t in bwd_tree.children.values()]
        )
        self.graph = Digraph(nohtml(keyword), format="png")
        self.graph.attr("graph", rankdir="LR")
        self.graph.attr("node", shape="plaintext", margin="0")

    def interpolate_fontsize(self, freq: int) -> int:
        """
        Computing the size of the font of a node of the tree

        Arguments:
            freq (int): Frequency of the N-gram

        Returns:
            int: Size of the font
        """
        lower = self.min_font_size
        upper = self.max_font_size
        t = freq / self.max_freq

        def quad(t: float) -> float:
            return float(t ** (1.0 / 3))

        font_interp = quad if self.font_interp is None else self.font_interp
        return int(font_interp(t) * (upper - lower) + lower)

    def draw_subtree(
        self, tree: FreqNode, direction: Direction, root: str, suffix: str, depth: int
    ) -> None:
        """
        Drawing a subtree of words

        Arguments:
            tree (FreqNode): Subtree of words
            direction (Direction): Direction of the subtree
            root (str): Root word
            suffix (str): Suffix of the subtree
            depth (int): Depth of the subtree
        """
        if depth > 0:
            fontsize = self.interpolate_fontsize(tree.freq)
            self.graph.node(nohtml(root + suffix), label=nohtml(root), fontsize=str(fontsize))
        for word, subtree in tree.children.items():
            new_suffix = f"{suffix}-{word}"
            self.draw_subtree(subtree, direction, word, new_suffix, depth + 1)
            src = root if depth == 0 else root + suffix
            dst = word + new_suffix
            if direction == Direction.Forward:
                self.graph.edge(nohtml(src), nohtml(dst))
            else:
                self.graph.edge(nohtml(dst), nohtml(src))

    def draw(self) -> Digraph:
        """
        Drawing the word tree as a directed graph

        Returns:
            Digraph: Word tree
        """
        self.graph.node(
            nohtml(self.keyword), label=nohtml(self.keyword), fontsize=str(self.max_font_size)
        )
        self.draw_subtree(self.bwd_tree, Direction.Backward, self.keyword, "-bwd", 0)
        self.draw_subtree(self.fwd_tree, Direction.Forward, self.keyword, "-fwd", 0)
        return self.graph


class WordTree:
    """
    Class for building a word tree

    Arguments:
        texts (list[list[str]]): List of lists of words
        keyword (str): Keyword whose context is shown
        max_n (int): Largest size of the context
        max_per_n (int): Largest number of examples for every size of the context

    Attributes:
        ngrams (list[str]): List of N-grams
        frequencies (list[int]): List of the frequencies of the N-grams

    Methods:
        search: Finding the N-grams that start or end with the keyword and their frequencies
        build_tree: Building a subtree of words
        build_trees: Building the subtrees of words before and after the keyword
        draw: Drawing the word tree as a directed graph

    Raises:
        SourceTypeError: If the texts are not a list of lists of words
        SourceError: If there are no texts
        ParameterError: If the size of the context is below 2 or the number of
            examples below one
    """

    def __init__(
        self,
        texts: list[list[str]],
        keyword: str,
        max_n: int = 5,
        max_per_n: int = 8,
    ):
        check_sequence(texts, "lists of words")
        if not all(isinstance(text, (list, tuple)) for text in texts):
            raise SourceTypeError("The texts must be a list of lists of words")
        if not texts:
            raise SourceError("The data source has no words")
        if max_n < 2:
            raise ParameterError("The size of the context must be at least 2")
        if max_per_n < 1:
            raise ParameterError(
                "The number of examples for every size of the context must be greater than 0"
            )
        self.texts = texts
        self.keyword = keyword
        self.max_n = max_n
        self.max_per_n = max_per_n
        self.ngrams: list[tuple[str, ...]] = []
        self.frequencies: list[int] = []

    def search(self) -> None:
        """Finding the N-grams that start or end with the keyword and their frequencies"""
        frequencies_dict: defaultdict[tuple[str, ...], int] = defaultdict(int)
        for sent in self.texts:
            for n in range(2, self.max_n + 1):
                for i in range(0, len(sent) - n + 1):
                    ngram = sent[i : i + n]
                    if ngram[0] == self.keyword or ngram[-1] == self.keyword:
                        frequencies_dict[tuple(ngram)] += 1
        for found_ngram, freq in frequencies_dict.items():
            self.ngrams.append(found_ngram)
            self.frequencies.append(freq)

    @staticmethod
    def build_tree(ngrams: Sequence[Sequence[str]], frequencies: Sequence[int]) -> FreqNode:
        """
        Building a subtree of words

        Arguments:
            ngrams (Sequence[Sequence[str]]): List of N-grams
            frequencies (Sequence[int]): List of the frequencies of the N-grams

        Returns:
            FreqNode: Subtree of words
        """
        tree = FreqNode(freq=0, children={})
        for ngram, freq in zip(ngrams, frequencies, strict=False):
            subtree = tree
            for gram in ngram:
                if gram not in subtree.children:
                    subtree.children[gram] = FreqNode(children={}, freq=freq)
                subtree = subtree.children[gram]
            subtree.freq = freq
        return tree

    def build_trees(self) -> tuple[FreqNode, FreqNode]:
        """
        Building the subtrees of words before and after the keyword

        Returns:
            tuple[FreqNode, FreqNode]: Subtrees of words after and before the keyword
        """
        forward_ngrams: list[Sequence[str]] = []
        forward_frequencies: list[int] = []
        backward_ngrams: list[Sequence[str]] = []
        backward_frequencies: list[int] = []
        for ngram, freq in zip(self.ngrams, self.frequencies, strict=False):
            forward = ngram[0] == self.keyword
            backward = ngram[-1] == self.keyword
            if forward:
                forward_ngrams.append(ngram[1:])
                forward_frequencies.append(freq)
            if backward:
                backward_ngrams.append(list(reversed(ngram[:-1])))
                backward_frequencies.append(freq)
        forward_tree = self.build_tree(forward_ngrams, forward_frequencies)
        backward_tree = self.build_tree(backward_ngrams, backward_frequencies)
        return forward_tree, backward_tree

    def draw(self, **kwargs: Any) -> Digraph:
        """
        Drawing the word tree as a directed graph

        Arguments:
            kwargs: Drawing parameters of TreeDrawer - max_font_size, min_font_size, font_interp

        Returns:
            Digraph: Word tree
        """
        df = pd.DataFrame(
            [
                {
                    "ngram": ngram,
                    "n": len(ngram),
                    "forward": ngram[0] == self.keyword,
                    "freq": freq,
                }
                for ngram, freq in zip(self.ngrams, self.frequencies, strict=False)
            ]
        )
        filtered_df = (
            df.sort_values("freq", ascending=False)
            .groupby(["forward", "n"])
            .head(self.max_per_n)
            .reset_index()
        )
        self.ngrams = filtered_df.ngram.tolist()
        self.frequencies = filtered_df.freq.tolist()
        forward_tree, backward_tree = self.build_trees()
        td = TreeDrawer(self.keyword, forward_tree, backward_tree, **kwargs)
        return td.draw()


def wordtree(
    texts: list[list[str]], keyword: str, max_n: int = 5, max_per_n: int = 8, **kwargs: Any
) -> Digraph:
    """
    Building a word tree that shows the contexts of a keyword in texts

    Description:
        The N-grams of up to max_n words that start or end with the keyword
        are counted in every text (a sentence, for instance), the most frequent
        max_per_n of every size on each side are kept and joined into two
        trees - the words after the keyword and before it - with the size of
        the font by frequency (Wattenberg and Viégas 2008). Rendering needs the
        executables of Graphviz

    References:
        https://www.cg.tuwien.ac.at/courses/InfoVis/HallOfFame/2011/Gruppe05/Homepage/Paper/wordtree-paper-wattenberg.pdf

    Arguments:
        texts (list[list[str]]): List of lists of words
        keyword (str): Keyword whose context is shown
        max_n (int): Largest size of the context
        max_per_n (int): Largest number of examples for every size of the context
        kwargs: Drawing parameters of TreeDrawer - max_font_size, min_font_size, font_interp

    Returns:
        Digraph: Word tree

    Raises:
        SourceTypeError: If the texts are not a list of lists of words
        SourceError: If there are no texts or the keyword occurs in none of them
        ParameterError: If the size of the context is below 2 or the number of
            examples below one

    Example:
        >>> from ests.visualizers import wordtree
        >>> tree = wordtree([["el", "gato", "duerme"], ["el", "gato", "come"]], "gato", max_n=2)
        >>> tree.name, len(tree.body)
        ('gato', 9)
    """
    wt = WordTree(
        texts,
        keyword,
        max_n=max_n,
        max_per_n=max_per_n,
    )
    wt.search()
    if not wt.ngrams:
        raise SourceError("The keyword is not found")
    return wt.draw(**kwargs)
