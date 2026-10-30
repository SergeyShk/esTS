import anyts.unadapted_readability_stats
from anyts.unadapted_readability_stats import (
    calc_dickes_steiwer as calc_dickes_steiwer,
    calc_eflaw as calc_eflaw,
    calc_elf as calc_elf,
    calc_forcast as calc_forcast,
    calc_fucks as calc_fucks,
    calc_gulpease as calc_gulpease,
    calc_linsear_write as calc_linsear_write,
    calc_powers_sumner_kearl as calc_powers_sumner_kearl,
    calc_strain_index as calc_strain_index,
    calc_wheeler_smith as calc_wheeler_smith,
    calc_wiener_sachtextformel as calc_wiener_sachtextformel,
)

from .basic_stats import BasicStats


class UnadaptedReadabilityStats(anyts.unadapted_readability_stats.UnadaptedReadabilityStats):
    """
    Class for computing the readability formulas of other languages with their own coefficients

    Description:
        Formulas made for English, German and Italian, with their published
        coefficients and no calibration for Spanish, over the basic statistics of
        esTS - the letters and the syllables of Spanish words: their values compare
        Spanish texts with each other and with other tools, but give no Spanish
        grade and do not enter the consensus grade; the formulas with Spanish
        coefficients are those of ReadabilityStats

    Example:
        >>> from ests import UnadaptedReadabilityStats
        >>> text = "Pies no tengo, ando; boca no tengo, hablo: cuándo dormir, cuándo levantarse, cuándo empezar labores"
        >>> urs = UnadaptedReadabilityStats(text)
        >>> round(urs.forcast, 2), round(urs.gulpease, 2)
        (17.0, 56.33)

    Arguments:
        source (str|Doc|BasicStats): Data source - a string, a Doc object or a ready
            BasicStats object
        sents_extractor (SentsExtractor): Sentence extraction tool; not used for ready
            basic statistics
        words_extractor (WordsExtractor): Word extraction tool; not used for ready basic
            statistics

    Attributes:
        bs (BasicStats): Basic statistics of the text
        forcast (float): FORCAST grade
        linsear_write (float): Linsear Write grade
        powers_sumner_kearl (float): Powers-Sumner-Kearl grade
        eflaw (float): McAlpine EFLAW score
        wiener_sachtextformel_1 (float): Wiener Sachtextformel 1
        wiener_sachtextformel_2 (float): Wiener Sachtextformel 2
        wiener_sachtextformel_3 (float): Wiener Sachtextformel 3
        wiener_sachtextformel_4 (float): Wiener Sachtextformel 4
        dickes_steiwer (float): Dickes-Steiwer index
        gulpease (float): Gulpease index
        fucks (float): Fucks index
        strain_index (float): Strain index
        elf (float): Easy listening formula (ELF)
        wheeler_smith (float): Wheeler-Smith index

    Methods:
        describe: Reading of a formula by its scale, None for every formula
        get_stats: Getting the computed formulas
        to_dataframe: Getting the formulas as a table of one row
        print_stats: Printing the computed formulas with descriptions

    Raises:
        SourceTypeError: If the source is neither a string, a Doc object nor BasicStats,
            or an extractor is of another type
        SourceError: If the source has no words or no sentences, or is a string with a
            character without a UTF-8 form
    """

    basic_stats_class = BasicStats
