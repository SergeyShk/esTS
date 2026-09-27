from collections.abc import Sequence

import anyts
from anyts.constants import (
    DIVERSITY_LOG_BASE,
    HDD_SAMPLE_SIZE,
    MATTR_WINDOW_LEN,
    MTLD_MIN_LEN,
    MTLD_TTR_THRESHOLD,
)
from anyts.diversity_stats import (
    Calculator as Calculator,
    HeapsFit as HeapsFit,
    WindowStats as WindowStats,
    ZipfMandelbrot as ZipfMandelbrot,
    calc_alpha2 as calc_alpha2,
    calc_baayen_p as calc_baayen_p,
    calc_brunet_w as calc_brunet_w,
    calc_cttr as calc_cttr,
    calc_dttr as calc_dttr,
    calc_dugast_k as calc_dugast_k,
    calc_entropy as calc_entropy,
    calc_evenness as calc_evenness,
    calc_frequency_spectrum as calc_frequency_spectrum,
    calc_gini_simpson_index as calc_gini_simpson_index,
    calc_hapax_index as calc_hapax_index,
    calc_hapax_ratio as calc_hapax_ratio,
    calc_hdd as calc_hdd,
    calc_heaps_beta as calc_heaps_beta,
    calc_herdan_vm as calc_herdan_vm,
    calc_honore_r as calc_honore_r,
    calc_httr as calc_httr,
    calc_inverse_simpson_index as calc_inverse_simpson_index,
    calc_mamtld as calc_mamtld,
    calc_mattr as calc_mattr,
    calc_michea_m as calc_michea_m,
    calc_msttr as calc_msttr,
    calc_mtld as calc_mtld,
    calc_mtldw as calc_mtldw,
    calc_mttr as calc_mttr,
    calc_perplexity as calc_perplexity,
    calc_rttr as calc_rttr,
    calc_sichel_s as calc_sichel_s,
    calc_simpson_index as calc_simpson_index,
    calc_sttr as calc_sttr,
    calc_ttr as calc_ttr,
    calc_windowed as calc_windowed,
    calc_yule_i as calc_yule_i,
    calc_yule_k as calc_yule_k,
    calc_zipf_alpha as calc_zipf_alpha,
    check_params as check_params,
    fit_heaps as fit_heaps,
    fit_zipf_mandelbrot as fit_zipf_mandelbrot,
    vocabulary_growth as vocabulary_growth,
)
from spacy.tokens import Doc

from .exceptions import SourceTypeError
from .extractors import WordsExtractor
from .utils import iter_doc_words


class DiversityStats(anyts.DiversityStats):
    """
    Class for computing the main lexical diversity metrics of a text

    Description:
        Lexical diversity reflects the richness of the vocabulary of a text of a given
        length. Defaults: base 10 for the logarithmic measures of Summer, Maas and
        Dugast, a 50-word MATTR window and MSTTR segment, the MTLD threshold 0.72
        (a factor closes at a TTR not above it) with a minimum factor of 10 words,
        an HD-D sample of 42 words; all of them are parameters of the class

    References:
        https://en.wikipedia.org/wiki/Lexical_diversity
        https://en.wikipedia.org/wiki/Diversity_index
        https://core.ac.uk/download/pdf/82620241.pdf

    Example:
        >>> from ests import DiversityStats
        >>> text = "Pies no tengo, ando; boca no tengo, hablo: cuándo dormir, cuándo levantarse, cuándo empezar labores"
        >>> ds = DiversityStats(text)
        >>> ds.ttr
        0.7333333333333333
        >>> ds.yule_k
        444.44444444444446
        >>> ds.windowed("ttr", window_len=5)
        WindowStats(mean=0.9333333333333332, std=0.11547005383792512, lower=0.6464898180167025, upper=1.220176848649964, n_windows=3)

    Arguments:
        source (str|Doc): Data source (a string or a Doc object); words are
            always lower-cased
        words_extractor (WordsExtractor): Word extraction tool; for a Doc it is
            applied to the text of the Doc, without it the words come from the tokens
        window_len (int): Window size for MATTR and segment size for MSTTR
        mtld_threshold (float): TTR threshold for MTLD, MA-MTLD and MTLD-W
        mtld_min_len (int): Minimum factor length for MTLD, MA-MTLD and MTLD-W
        hdd_sample_size (int): Sample size for HD-D
        log_base (float): Logarithm base for the Summer, Maas and Dugast metrics

    Attributes:
        words (tuple[str]): Tuple of extracted words in lower case
        window_len (int): Window size for MATTR and segment size for MSTTR
        mtld_threshold (float): TTR threshold for MTLD, MA-MTLD and MTLD-W
        mtld_min_len (int): Minimum factor length for MTLD, MA-MTLD and MTLD-W
        hdd_sample_size (int): Sample size for HD-D
        log_base (float): Logarithm base for the Summer, Maas and Dugast metrics;
            the five parameters can be changed on the object
        frequency_spectrum (dict[int, int]): Frequency spectrum - the number of lexemes with a given frequency
        ttr (float): Type-Token Ratio (TTR)
        rttr (float): Root Type-Token Ratio (RTTR)
        cttr (float): Corrected Type-Token Ratio (CTTR)
        httr (float): Herdan Type-Token Ratio (HTTR)
        sttr (float): Summer Type-Token Ratio (STTR)
        mttr (float): Maas Type-Token Ratio (MTTR)
        dttr (float): Dugast Type-Token Ratio (DTTR)
        mattr (float): Moving Average Type-Token Ratio (MATTR)
        msttr (float): Mean Segmental Type-Token Ratio (MSTTR)
        mtld (float): Measure of Textual Lexical Diversity (MTLD)
        mamtld (float): Moving Average Measure of Textual Lexical Diversity (MA-MTLD)
        mtldw (float): MTLD with a moving window and text wrap (MTLD-W)
        hdd (float): Hypergeometric Distribution D (HD-D)
        simpson_index (float): Simpson's index (D)
        inverse_simpson_index (float): Inverse Simpson's index (1/D)
        gini_simpson_index (float): Gini-Simpson index (1-D)
        hapax_index (float): Hapax index, a.k.a. Honoré's R
        honore_r (float): Alias for the hapax index
        yule_k (float): Yule's characteristic (Yule's K)
        yule_i (float): Inverse Yule's characteristic (Yule's I)
        herdan_vm (float): Herdan's Vm
        sichel_s (float): Sichel's S
        michea_m (float): Michéa's M
        brunet_w (float): Brunet's W
        dugast_k (float): Dugast's k
        baayen_p (float): Baayen's P
        hapax_ratio (float): Share of hapaxes among lexemes
        alpha2 (float): The α₂ exponent
        entropy (float): Shannon entropy in bits
        evenness (float): Evenness - the ratio of entropy to its maximum
        perplexity (float): Perplexity
        zipf_alpha (float): Zipf's law slope
        heaps_beta (float): Heaps' law exponent

    Methods:
        windowed: Windowed computation of a metric with the mean and a confidence interval
        get_stats: Getting the computed lexical diversity metrics of the text
        print_stats: Printing the computed lexical diversity metrics with descriptions

    Raises:
        SourceTypeError: If the source is neither a string nor a Doc object
        SourceError: If the source has no words
        ParameterError: If the parameters of the metrics are set incorrectly
    """

    def __init__(
        self,
        source: str | Doc,
        words_extractor: WordsExtractor | None = None,
        window_len: int = MATTR_WINDOW_LEN,
        mtld_threshold: float = MTLD_TTR_THRESHOLD,
        mtld_min_len: int = MTLD_MIN_LEN,
        hdd_sample_size: int = HDD_SAMPLE_SIZE,
        log_base: float = DIVERSITY_LOG_BASE,
    ):
        check_params(window_len, mtld_threshold, mtld_min_len, hdd_sample_size, log_base)
        if isinstance(source, Doc) and words_extractor is None:
            words: Sequence[str] = [word for _, _, word in iter_doc_words(source)]
        elif isinstance(source, Doc | str):
            text = source.text if isinstance(source, Doc) else source
            words = (words_extractor or WordsExtractor()).extract(text)
        else:
            raise SourceTypeError("The data source is set incorrectly")
        super().__init__(
            [word.lower() for word in words],
            window_len,
            mtld_threshold,
            mtld_min_len,
            hdd_sample_size,
            log_base,
        )
