from collections.abc import Iterable
from math import isnan, nan

import anyts.readability_stats
from anyts.readability_stats import (
    calc_lix as calc_lix,
    calc_mu_index as calc_mu_index,
    calc_rix as calc_rix,
    calc_smog_index as calc_smog_index,
)
from anyts.utils import safe_divide
from spacy.tokens import Doc

from .basic_stats import BasicStats
from .constants import (
    GRADE_AGE_LEVELS,
    MU_SCALE,
    POSTGRADUATE_LEVEL,
    PRESET_SCALES,
    READABILITY_GRADE_STATS,
    READABILITY_PRESETS,
    READABILITY_STATS_DESC,
    READING_EASE_GRADES,
    READING_EASE_SCALES,
    READING_SPEED_NORMS,
    READING_SPEED_WPM,
)
from .exceptions import ParameterError
from .extractors import SentsExtractor, WordsExtractor


def check_preset(preset: str) -> None:
    """
    Checking the name of a coefficient preset

    Arguments:
        preset (str): Name of the preset

    Raises:
        ParameterError: If the preset is not a string or is unknown
    """
    if not isinstance(preset, str):
        raise ParameterError(f"The preset must be a string, not {type(preset).__name__}")
    if preset not in READABILITY_PRESETS:
        raise ParameterError(
            f"Unknown coefficient preset: {preset}. "
            f"Available presets: {tuple(READABILITY_PRESETS)}"
        )


class ReadabilityStats(anyts.readability_stats.ReadabilityStats):
    """
    Class for computing the main readability metrics of a text

    Description:
        The Spanish readability formulas, their interpretation scales, the school
        stage and reader age of Spain and the reading time. The preset selects the
        coefficients of the Flesch reading ease and its scale, used by describe_level
        and by the consensus grade: general - Szigriszt-Pazos (1993) with the INFLESZ
        scale, classic - Fernández Huerta (1959) with his own bands

    Example:
        >>> from ests import ReadabilityStats
        >>> text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"
        >>> rs = ReadabilityStats(text)
        >>> rs.get_stats()
        {'flesch_reading_easy': 53.545000000000016,
         'gutierrez_polini_index': 33.5,
         'crawford_grade': 5.812999999999999,
         'mu_index': 50.943396226415096,
         'sol_grade': 9.258359866374562,
         'lix': 60.0,
         'rix': 5.0,
         'consensus_grade': 9.0,
         'reading_time': 0.03597122302158273}
        >>> rs.describe_level()
        'algo difícil'
        >>> rs.describe_grade()
        'ESO (12-16 years)'

    Arguments:
        source (str|Doc|BasicStats): Data source - a string, a Doc object or
            a ready BasicStats object to reuse
        sents_extractor (SentsExtractor): Sentence extraction tool
        words_extractor (WordsExtractor): Word extraction tool
        preset (str): Coefficient preset (general, classic)

    Attributes:
        bs (BasicStats): Basic statistics of the text
        preset (str): Name of the coefficient preset
        coefficients (dict[str, tuple[float, float, float]]): Coefficients of the
            preset, a copy of READABILITY_PRESETS that can be changed for one object
        flesch_reading_easy (float): Flesch reading ease with the coefficients of the preset
        gutierrez_polini_index (float): Comprehensibility formula of Gutiérrez de Polini
        crawford_grade (float): Crawford formula, years of schooling
        mu_index (float): Legibilidad µ
        sol_grade (float): SOL grade, SMOG converted to Spanish
        lix (float): LIX readability index
        rix (float): RIX readability index
        consensus_grade (float): Consensus grade over the grade formulas and the reading ease
        reading_time (float): Reading time in minutes at 278 words per minute
        flesch_kincaid_grade, coleman_liau_index, automated_readability_index,
            smog_index, gunning_fog_index (float): The formulas of the core with
            their English coefficients, outside get_stats

    Methods:
        reading_ease_to_grade: Years of schooling for a value of the reading ease by the preset
        describe_level: Band of a reading ease scale or of the µ scale for a metric
        describe_grade: School stage and reader age for the consensus grade or a grade formula
        reading_time_by_speed: Reading time at a given speed
        reading_time_by_norm: Reading time aloud and silently by a norm of READING_SPEED_NORMS
        get_stats: Getting the computed readability metrics of the text
        print_stats: Printing the computed readability metrics with descriptions

    Raises:
        SourceTypeError: If the source is neither a string, a Doc nor a BasicStats object,
            the basic statistics are not those of esTS, or an extractor is of another type
        SourceError: If the source has no words or no sentences
        ParameterError: If the coefficient preset is not a string or is unknown
    """

    basic_stats_class = BasicStats
    presets = READABILITY_PRESETS
    grade_stats = READABILITY_GRADE_STATS
    stats_desc = READABILITY_STATS_DESC
    grade_age_levels = GRADE_AGE_LEVELS
    postgraduate_level = POSTGRADUATE_LEVEL
    reading_speed = READING_SPEED_WPM
    reading_speed_norms = READING_SPEED_NORMS

    def __init__(
        self,
        source: str | Doc | BasicStats,
        sents_extractor: SentsExtractor | None = None,
        words_extractor: WordsExtractor | None = None,
        preset: str = "general",
    ):
        super().__init__(source, sents_extractor, words_extractor, preset)

    @property
    def gutierrez_polini_index(self) -> float:
        # letters of the extracted words, so the mean word length matches the word count
        n_letters = sum(letters * count for letters, count in self.bs.c_letters.items())
        return calc_gutierrez_polini_index(n_letters, self.bs.n_words, self.bs.n_sents)

    @property
    def crawford_grade(self) -> float:
        return calc_crawford_grade(self.bs.n_syllables, self.bs.n_words, self.bs.n_sents)

    @property
    def sol_grade(self) -> float:
        return calc_sol_grade(
            self.bs.count_words_by_syllables(self.smog_complex_syl_factor), self.bs.n_sents
        )

    def reading_ease_to_grade(self, flesch_reading_easy: float) -> float:
        """
        Converting the Flesch reading ease into years of schooling by the scale of the preset

        Arguments:
            flesch_reading_easy (float): Value of the reading ease

        Returns:
            float: Years of schooling

        Raises:
            ParameterError: If the reading ease is not a finite number
        """
        return flesch_reading_easy_to_grade(flesch_reading_easy, self.preset)

    def describe_level(self, stat: str = "flesch_reading_easy", scale: str | None = None) -> str:
        """
        Getting the band of a readability scale for a metric

        Arguments:
            stat (str): Name of the metric: flesch_reading_easy or mu_index
            scale (str): Scale for the reading ease: inflesz, szigriszt or
                fernandez_huerta; without it the scale of the preset is used
                (general - inflesz, classic - fernandez_huerta); the µ index
                has a single scale of its own and accepts no other

        Returns:
            str: Band of the scale

        Raises:
            ParameterError: If the metric has no scale, the scale is unknown
                or a scale is given for the µ index
        """
        if stat == "flesch_reading_easy":
            return flesch_reading_easy_to_level(
                self.flesch_reading_easy, scale or PRESET_SCALES[self.preset]
            )
        if stat == "mu_index":
            if scale is not None:
                raise ParameterError("Legibilidad µ has a single scale, scale must not be set")
            return mu_to_level(self.mu_index)
        raise ParameterError(
            f"The metric {stat} has no interpretation scale. "
            "Metrics with a scale: ('flesch_reading_easy', 'mu_index')"
        )


def calc_flesch_reading_easy(
    n_syllables: int,
    n_words: int,
    n_sents: int,
    a: float = 1.0,
    b: float = 62.3,
    c: float = 206.835,
) -> float:
    """
    Computing the Flesch reading ease with Spanish coefficients

    Description:
        The higher the value, the easier the text is to read; the scale runs
        from 0 to 100. The default coefficients are those of Szigriszt-Pazos
        (1993), 206.835 - 62.3 * ASW - ASL, with the INFLESZ scale of
        Barrio-Cantalejo et al. (2008) (flesch_reading_easy_to_level):
            80-100 - muy fácil (comics, children's books)
            65-80 - bastante fácil (primary school textbooks)
            55-65 - normal (general press)
            40-55 - algo difícil (secondary school textbooks)
            0-40 - muy difícil (scientific and technical texts)
        The coefficients of Fernández Huerta (1959), 206.84 - 60 * ASW -
        1.02 * ASL, are the classic preset; the last term takes the mean
        sentence length, as corrected by Law (2011), not the number of
        sentences per 100 words that Fernández Huerta printed

    References:
        Szigriszt Pazos, F. Sistemas predictivos de legibilidad del mensaje escrito:
            fórmula de perspicuidad. Universidad Complutense de Madrid, 1993
        Barrio-Cantalejo, I. M. et al. Validación de la Escala INFLESZ para evaluar
            la legibilidad de los textos dirigidos a pacientes. Anales del Sistema
            Sanitario de Navarra, 31(2), 2008
        Fernández Huerta, J. Medidas sencillas de lecturabilidad. Consigna, 214, 1959
        Law, G. Error in the Fernández Huerta readability formula. LINGUIST List 22.2332, 2011

    Arguments:
        n_syllables (int): Number of syllables
        n_words (int): Number of words
        n_sents (int): Number of sentences
        a (float): Coefficient a, at the mean sentence length in words
        b (float): Coefficient b, at the mean word length in syllables
        c (float): Coefficient c, the constant

    Returns:
        float: Value of the index, nan without words or sentences
    """
    return anyts.readability_stats.calc_flesch_reading_easy(n_syllables, n_words, n_sents, a, b, c)


def calc_gutierrez_polini_index(n_letters: int, n_words: int, n_sents: int) -> float:
    """
    Computing the comprehensibility formula of Gutiérrez de Polini

    Description:
        95.2 - 9.7 * AWL - 0.35 * ASL with the mean word length in letters
        The higher the value, the easier the text; there is no scale of its
        own: ordinary prose lies between 30 and 50, a text above 70 is read
        by a young child

    References:
        Gutiérrez de Polini, L. E. Investigación sobre lectura en Venezuela.
            Ministerio de Educación, Caracas, 1972

    Arguments:
        n_letters (int): Number of letters
        n_words (int): Number of words
        n_sents (int): Number of sentences

    Returns:
        float: Value of the formula, nan without words or sentences
    """
    return (
        95.2
        - safe_divide(9.7 * n_letters, n_words, nan)
        - safe_divide(0.35 * n_words, n_sents, nan)
    )


def calc_crawford_grade(n_syllables: int, n_words: int, n_sents: int) -> float:
    """
    Computing the Crawford formula

    Description:
        Years of schooling needed to read the text (Crawford, 1989), fitted
        on Spanish primary school readers of grades 1-6, so higher values
        saturate: -0.205 * sentences per 100 words + 0.049 * syllables per
        100 words - 3.407. The higher the value, the harder the text

    References:
        Crawford, A. N. Fórmula y gráfico para determinar la comprensibilidad de
            textos del nivel primario en castellano. Lectura y Vida, 10(4), 1989

    Arguments:
        n_syllables (int): Number of syllables
        n_words (int): Number of words
        n_sents (int): Number of sentences

    Returns:
        float: Value of the formula, nan without words
    """
    return (
        safe_divide(-0.205 * 100 * n_sents, n_words, nan)
        + safe_divide(0.049 * 100 * n_syllables, n_words, nan)
        - 3.407
    )


def calc_sol_grade(n_complex: int, n_sents: int, a: float = 0.74, b: float = -2.51) -> float:
    """
    Computing the SOL grade

    Description:
        E = -2.51 + 0.74 * S (Contreras et al., 1999), where S is the SMOG
        index of the Spanish text and E the years of schooling on the English
        scale. The higher the value, the harder the text

    References:
        Contreras, A., García-Alonso, R., Echenique, M., Daye-Contreras, F. The SOL
            formulas for converting SMOG readability scores between health education
            materials written in Spanish, English, and French. Journal of Health
            Communication, 4(1), 1999

    Arguments:
        n_complex (int): Number of words of three or more syllables
        n_sents (int): Number of sentences
        a (float): Coefficient a, at the SMOG index
        b (float): Coefficient b, the constant

    Returns:
        float: Value of the grade, nan without sentences
    """
    return b + a * calc_smog_index(n_complex, n_sents)


def flesch_reading_easy_to_level(flesch_reading_easy: float, scale: str = "inflesz") -> str:
    """
    Getting the band of a scale for the Flesch reading ease

    Description:
        The scales of READING_EASE_SCALES: inflesz (Barrio-Cantalejo et al.,
        2008, five bands for the Szigriszt-Pazos coefficients), szigriszt
        (Szigriszt-Pazos, 1993, seven bands) and fernandez_huerta
        (Fernández Huerta, 1959, seven bands for his coefficients)

    Arguments:
        flesch_reading_easy (float): Value of the reading ease
        scale (str): Name of the scale

    Returns:
        str: Band of the scale

    Raises:
        ParameterError: If the scale is unknown
    """
    if scale not in READING_EASE_SCALES:
        raise ParameterError(
            f"Unknown scale: {scale}. Available scales: {tuple(READING_EASE_SCALES)}"
        )
    return _level(flesch_reading_easy, READING_EASE_SCALES[scale])


def mu_to_level(mu_index: float) -> str:
    """
    Getting the band of the µ scale for Legibilidad µ

    Description:
        The seven bands of Muñoz Baquedano and Muñoz Urra (2006) from
        MU_SCALE; an undefined index (nan) has no band and gives an empty string

    Arguments:
        mu_index (float): Value of Legibilidad µ

    Returns:
        str: Band of the scale
    """
    return _level(mu_index, MU_SCALE)


def _level(value: float, scale: tuple[tuple[float, str], ...]) -> str:
    """Band of a scale given as lower bounds in descending order; the lowest band is open below"""
    for threshold, level in scale:
        if value >= threshold:
            return level
    return "" if isnan(value) else scale[-1][1]


def flesch_reading_easy_to_grade(flesch_reading_easy: float, preset: str = "general") -> float:
    """
    Converting the Flesch reading ease into years of schooling

    Description:
        Used for the consensus grade; the thresholds follow the scale of the
        preset. With the general preset, through the text types of the INFLESZ
        bands and the school stages of Spain:
            80-100 - 3 (comics and children's books, primary school grades 1-3)
            65-80 - 5 (primary school textbooks, grades 4-6)
            55-65 - 8 (general press, ESO)
            40-55 - 11 (secondary school textbooks, bachillerato)
            below 40 - 13 (scientific texts, university)
        With the classic preset, through the bands of Flesch kept by Fernández
        Huerta: 90-100 - 5, 80-90 - 6, 70-80 - 7,
        60-70 - 8.5, 50-60 - 10, 40-50 - 11, 30-40 - 12, below 30 - 13
        Values above 100 belong to the first grade of the scale

    Arguments:
        flesch_reading_easy (float): Value of the reading ease
        preset (str): Coefficient preset whose scale is read

    Returns:
        float: Years of schooling

    Raises:
        ParameterError: If the preset is unknown or the reading ease is not a finite number
    """
    check_preset(preset)
    return anyts.readability_stats.flesch_reading_easy_to_grade(
        flesch_reading_easy, READING_EASE_GRADES[preset], 13
    )


def calc_consensus_grade(
    grades: Iterable[float], flesch_reading_easy: float | None = None, preset: str = "general"
) -> float:
    """
    Computing the consensus grade

    Description:
        The median of the values of the grade formulas rounded half up; the
        reading ease is converted with flesch_reading_easy_to_grade by the
        scale of the preset and added without rounding

    Arguments:
        grades (list[float]): Values of the grade formulas
        flesch_reading_easy (float): Value of the reading ease
        preset (str): Coefficient preset of the reading ease

    Returns:
        float: Consensus grade

    Raises:
        ParameterError: If there are no values, a grade or the reading ease is not a
            finite number or the preset is unknown
    """
    check_preset(preset)
    return anyts.readability_stats.calc_consensus_grade(
        grades,
        flesch_reading_easy,
        lambda value: flesch_reading_easy_to_grade(value, preset),
    )


def grade_to_age(grade: float) -> str:
    """
    Getting the school stage and reader age by the value of a grade formula

    Description:
        The stages of the Spanish school system by years of schooling,
        counted from the first year of primary school at the age of six:
            1-3 - primary school, grades 1-3, 6-9 years
            4-6 - primary school, grades 4-6, 9-12 years
            7-10 - ESO, 12-16 years
            11-12 - bachillerato, 16-18 years
            13-16 - university, 18-22 years
            above 16 - postgraduate, over 22 years
        The value is rounded half up, values below 1 belong to grades 1-3.
        Applies to the formulas whose result is a grade: Crawford, SOL
        and the consensus grade

    Arguments:
        grade (float): Value of a grade formula

    Returns:
        str: School stage and reader age

    Raises:
        ParameterError: If the grade is not a finite number
    """
    return anyts.readability_stats.grade_to_age(grade, GRADE_AGE_LEVELS, POSTGRADUATE_LEVEL)


def calc_reading_time(n_words: int, wpm: float = READING_SPEED_WPM) -> float:
    """
    Computing the reading time of a text

    Description:
        The default speed is the silent reading speed of adults in Spanish,
        278 words per minute (Brysbaert, 2019); the norms of school years
        (Ripoll, Tapia and Aguado, 2020) are in READING_SPEED_NORMS

    References:
        Brysbaert, M. How many words do we read per minute? A review and
            meta-analysis of reading rate. Journal of Memory and Language, 109, 2019
        Ripoll, J. C., Tapia, M. M., Aguado, G. Velocidad lectora en alumnado
            hispanohablante: un metaanálisis. Revista de Psicodidáctica, 25(2), 2020

    Arguments:
        n_words (int): Number of words
        wpm (float): Reading speed, words per minute

    Returns:
        float: Reading time in minutes

    Raises:
        ParameterError: If the reading speed is not a positive number
    """
    return anyts.readability_stats.calc_reading_time(n_words, wpm)
