from collections.abc import Iterable, Mapping
from math import floor, isnan, sqrt
from statistics import median

from spacy.tokens import Doc

from .basic_stats import BasicStats
from .constants import (
    GRADE_AGE_LEVELS,
    LIX_LONG_WORD_LETTER_FACTOR,
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
    SMOG_COMPLEX_SYL_FACTOR,
)
from .exceptions import ParameterError, SourceError
from .extractors import SentsExtractor, WordsExtractor


def check_preset(preset: str) -> None:
    """
    Checking the name of a coefficient preset

    Arguments:
        preset (str): Name of the preset

    Raises:
        ParameterError: If the preset is unknown
    """
    if preset not in READABILITY_PRESETS:
        raise ParameterError(
            f"Unknown coefficient preset: {preset}. "
            f"Available presets: {tuple(READABILITY_PRESETS)}"
        )


class ReadabilityStats:
    """
    Class for computing the main readability metrics of a text

    Description:
        The formulas of the Spanish tradition: the Flesch reading ease with
        the coefficients of Szigriszt-Pazos (1993, preset general) or of
        Fernández Huerta (1959, preset classic), the comprehensibility
        formula of Gutiérrez de Polini (1972), the grade formula of
        Crawford (1989), Legibilidad µ of Muñoz Baquedano and Muñoz Urra
        (2006), the SOL grade of Contreras et al. (1999) - SMOG converted
        to Spanish - and the language-independent LIX and RIX.
        The interpretation layer: the INFLESZ and other scales of the reading
        ease, the µ scale, a consensus grade by the median of the grade
        formulas, the school stage and reader age of Spain and the reading
        time by the norms of Spanish-speaking readers. The scale of the
        reading ease follows the preset: INFLESZ for general, the bands of
        Fernández Huerta for classic, both in describe_level and in the
        conversion of the reading ease into the consensus grade

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
            a ready BasicStats object, so that the basic statistics are not
            computed again
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

    Methods:
        describe_level: Band of a reading ease scale or of the µ scale for a metric
        describe_grade: School stage and reader age for the consensus grade or a grade formula
        reading_time_by_speed: Reading time at a given speed
        reading_time_by_norm: Reading time aloud and silently by a norm of READING_SPEED_NORMS
        get_stats: Getting the computed readability metrics of the text
        print_stats: Printing the computed readability metrics with descriptions

    Raises:
        SourceError: If the source has no words or no sentences
        ParameterError: If the coefficient preset is unknown
    """

    def __init__(
        self,
        source: str | Doc | BasicStats,
        sents_extractor: SentsExtractor | None = None,
        words_extractor: WordsExtractor | None = None,
        preset: str = "general",
    ):
        check_preset(preset)
        self.preset = preset
        self.coefficients = dict(READABILITY_PRESETS[preset])
        if isinstance(source, BasicStats):
            self.bs = source
        else:
            self.bs = BasicStats(source, sents_extractor, words_extractor)
        if not self.bs.n_sents:
            raise SourceError("The data source has no sentences")

    @property
    def flesch_reading_easy(self) -> float:
        return calc_flesch_reading_easy(
            self.bs.n_syllables,
            self.bs.n_words,
            self.bs.n_sents,
            *self.coefficients["flesch_reading_easy"],
        )

    @property
    def gutierrez_polini_index(self) -> float:
        # letters of the extracted words, not of the whole text, so that the mean word
        # length stays on the same token set as the word count with any extractor
        n_letters = sum(letters * count for letters, count in self.bs.c_letters.items())
        return calc_gutierrez_polini_index(n_letters, self.bs.n_words, self.bs.n_sents)

    @property
    def crawford_grade(self) -> float:
        return calc_crawford_grade(self.bs.n_syllables, self.bs.n_words, self.bs.n_sents)

    @property
    def mu_index(self) -> float:
        return calc_mu_index(self.bs.c_letters)

    @property
    def sol_grade(self) -> float:
        return calc_sol_grade(
            self.bs.count_words_by_syllables(SMOG_COMPLEX_SYL_FACTOR), self.bs.n_sents
        )

    @property
    def lix(self) -> float:
        return calc_lix(
            self.bs.count_words_by_letters(LIX_LONG_WORD_LETTER_FACTOR),
            self.bs.n_words,
            self.bs.n_sents,
        )

    @property
    def rix(self) -> float:
        return calc_rix(
            self.bs.count_words_by_letters(LIX_LONG_WORD_LETTER_FACTOR), self.bs.n_sents
        )

    @property
    def consensus_grade(self) -> float:
        grades = [getattr(self, stat) for stat in READABILITY_GRADE_STATS]
        return calc_consensus_grade(grades, self.flesch_reading_easy, self.preset)

    @property
    def reading_time(self) -> float:
        return calc_reading_time(self.bs.n_words)

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

    def describe_grade(self, stat: str = "consensus_grade") -> str:
        """
        Getting the school stage and reader age by the value of a grade formula

        Arguments:
            stat (str): Name of the grade formula, the consensus grade by default

        Returns:
            str: School stage and reader age

        Raises:
            ParameterError: If the metric is not a grade formula
        """
        grade_stats = ("consensus_grade", *READABILITY_GRADE_STATS)
        if stat not in grade_stats:
            raise ParameterError(
                f"The metric {stat} is not a grade formula. Grade formulas: {grade_stats}"
            )
        return grade_to_age(getattr(self, stat))

    def reading_time_by_speed(self, wpm: int) -> float:
        """
        Computing the reading time of the text at a given speed

        Arguments:
            wpm (int): Reading speed, words per minute

        Returns:
            float: Reading time in minutes
        """
        return calc_reading_time(self.bs.n_words, wpm)

    def reading_time_by_norm(self, norm: str) -> tuple[float, float]:
        """
        Computing the reading time of the text aloud and silently by a norm

        Arguments:
            norm (str): Name of the norm from READING_SPEED_NORMS: grade_1 to
                grade_11 (years of schooling) or adult

        Returns:
            tuple[float, float]: Reading time in minutes aloud and silently

        Raises:
            ParameterError: If the norm is unknown
        """
        if norm not in READING_SPEED_NORMS:
            raise ParameterError(
                f"Unknown reading speed norm: {norm}. "
                f"Available norms: {tuple(READING_SPEED_NORMS)}"
            )
        aloud, silent = READING_SPEED_NORMS[norm]
        return calc_reading_time(self.bs.n_words, aloud), calc_reading_time(
            self.bs.n_words, silent
        )

    def get_stats(self) -> dict[str, float]:
        """
        Getting the computed readability metrics of the text

        Returns:
            dict[str, float]: Dictionary of the computed readability metrics
        """
        return {stat: getattr(self, stat) for stat in READABILITY_STATS_DESC}

    def print_stats(self):
        """Printing the computed readability metrics with descriptions"""
        print(f"{'Metric':^45}|{'Value':^10}")
        print("-" * 55)
        stats = self.get_stats()
        for stat, value in READABILITY_STATS_DESC.items():
            print(f"{value:45}|{stats[stat]:^10.2f}")


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
        from 0 to 100. The default coefficients are those of the fórmula de
        perspicuidad of Szigriszt-Pazos (1993), 206.835 - 62.3 * ASW - ASL,
        which Barrio-Cantalejo et al. (2008) validated and provided with the
        INFLESZ scale (flesch_reading_easy_to_level):
            80-100 - muy fácil (comics, children's books)
            65-80 - bastante fácil (primary school textbooks)
            55-65 - normal (general press)
            40-55 - algo difícil (secondary school textbooks)
            0-40 - muy difícil (scientific and technical texts)
        The coefficients of Fernández Huerta (1959), 206.84 - 60 * ASW -
        1.02 * ASL, are available through the classic preset. Fernández
        Huerta printed the last term as 1.02 times the number of sentences
        per 100 words; Law (2011) showed that this inverts the fraction of
        the Flesch formula the adaptation was based on, so the mean sentence
        length is used here, as in koRpus and textstat

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
        float: Value of the index
    """
    return c - (a * n_words / n_sents) - (b * n_syllables / n_words)


def calc_gutierrez_polini_index(n_letters: int, n_words: int, n_sents: int) -> float:
    """
    Computing the comprehensibility formula of Gutiérrez de Polini

    Description:
        The first formula written for Spanish rather than adapted from
        English (Gutiérrez de Polini, 1972), 95.2 - 9.7 * AWL - 0.35 * ASL
        with the mean word length in letters. The higher the value, the
        easier the text; it was fitted on school texts for the sixth grade
        and gives no scale of its own: the values of ordinary prose lie
        between 30 and 50, and a text above 70 is read by a young child

    References:
        Gutiérrez de Polini, L. E. Investigación sobre lectura en Venezuela.
            Ministerio de Educación, Caracas, 1972

    Arguments:
        n_letters (int): Number of letters
        n_words (int): Number of words
        n_sents (int): Number of sentences

    Returns:
        float: Value of the formula
    """
    return 95.2 - (9.7 * n_letters / n_words) - (0.35 * n_words / n_sents)


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
        float: Value of the formula
    """
    return (-0.205 * 100 * n_sents / n_words) + (0.049 * 100 * n_syllables / n_words) - 3.407


def calc_mu_index(c_letters: Mapping[int, int]) -> float:
    """
    Computing Legibilidad µ

    Description:
        The index of Muñoz Baquedano and Muñoz Urra (2006) measures the
        variability of word length: the mean of the number of letters per
        word divided by its variance, times 100. The variance is the sample
        one, divided by n - 1, which is the "cuasivarianza" of the authors:
        the population variance multiplied by the factor n / (n - 1) that
        their printed formula carries. Read that way the worked example of
        their manual comes out exactly (18 words, mean 6.9444, variance
        13.5844, µ = 51.12); applying the factor once more, on top of the
        sample variance, gives 54.13 instead and does not reproduce the
        example. The higher the value, the easier the text;
        the scale (mu_to_level):
            91-100 - muy fácil
            81-90 - fácil
            71-80 - un poco fácil
            61-70 - adecuado
            51-60 - un poco difícil
            31-50 - difícil
            0-30 - muy difícil
        Words without letters (numbers) are left out; with fewer than two
        words or without variability the index is undefined (nan)

    References:
        Muñoz Baquedano, M. Legibilidad y variabilidad de los textos.
            Boletín de Investigación Educacional, 21(2), 2006
        https://www.legibilidadmu.cl/

    Arguments:
        c_letters (dict[int, int]): Distribution of words by number of letters

    Returns:
        float: Value of the index
    """
    counts = {letters: count for letters, count in c_letters.items() if letters > 0}
    n = sum(counts.values())
    if n < 2:
        return float("nan")
    mean = sum(letters * count for letters, count in counts.items()) / n
    variance = sum(count * (letters - mean) ** 2 for letters, count in counts.items()) / (n - 1)
    if not variance:
        return float("nan")
    return mean / variance * 100


def calc_smog_index(n_complex: int, n_sents: int, a: float = 1.043, b: float = 3.1291) -> float:
    """
    Computing the SMOG index

    Description:
        The formula of McLaughlin (1969), a * sqrt(30 * polysyllables /
        sentences) + b, with the polysyllables being the words of three or
        more syllables. Fitted on English; for Spanish it is the input of
        the SOL formula (calc_sol_grade)

    References:
        McLaughlin, G. H. SMOG grading: a new readability formula.
            Journal of Reading, 12(8), 1969

    Arguments:
        n_complex (int): Number of words of three or more syllables
        n_sents (int): Number of sentences
        a (float): Coefficient a
        b (float): Coefficient b

    Returns:
        float: Value of the index
    """
    return a * sqrt(30 * n_complex / n_sents) + b


def calc_sol_grade(n_complex: int, n_sents: int, a: float = 0.74, b: float = -2.51) -> float:
    """
    Computing the SOL grade

    Description:
        Contreras et al. (1999) applied the SMOG index to Spanish texts and
        their English translations and fitted the conversion E = -2.51 +
        0.74 * S, where S is the SMOG index of the Spanish text and E the
        grade of the English scale, the years of schooling; the SOL
        formulas are named after the Spanish word for sun. The higher
        the value, the harder the text

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
        float: Value of the grade
    """
    return b + a * calc_smog_index(n_complex, n_sents)


def calc_lix(n_long_words: int, n_words: int, n_sents: int) -> float:
    """
    Computing the LIX readability index

    Description:
        The index of Björnsson (1968) does not depend on the language:
        the mean sentence length plus the percentage of long words.
        The higher the value, the harder the text; the scale:
            0-30 - very easy texts, children's books
            30-40 - easy texts, fiction, newspaper articles
            40-50 - texts of medium difficulty, magazine articles
            50-60 - hard texts, popular science, official texts
            60-100 - very hard texts, laws and bureaucratic language
        A long word has more than six letters, so ReadabilityStats passes
        the number of words of seven or more letters

    References:
        https://en.wikipedia.org/wiki/Lix_(readability_test)

    Arguments:
        n_long_words (int): Number of long words
        n_words (int): Number of words
        n_sents (int): Number of sentences

    Returns:
        float: Value of the index
    """
    return (n_words / n_sents) + (100 * n_long_words / n_words)


def calc_rix(n_long_words: int, n_sents: int) -> float:
    """
    Computing the RIX readability index

    Description:
        The simplified companion of LIX (Anderson, 1983), long words per
        sentence, independent of the language. The higher the value, the
        harder the text; the scale by grade:
            < 0.2 - grade 1
            0.2-0.5 - grade 2
            0.5-0.8 - grade 3
            0.8-1.3 - grade 4
            1.3-1.8 - grade 5
            1.8-2.4 - grade 6
            2.4-3.0 - grade 7
            3.0-3.7 - grade 8
            3.7-4.5 - grade 9
            4.5-5.3 - grade 10
            5.3-6.2 - grade 11
            6.2-7.2 - grade 12
            > 7.2 - college
        As for LIX, a long word has more than six letters

    References:
        https://en.wikipedia.org/wiki/Lix_(readability_test)

    Arguments:
        n_long_words (int): Number of long words
        n_sents (int): Number of sentences

    Returns:
        float: Value of the index
    """
    return n_long_words / n_sents


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
        Used to include the reading ease in the consensus grade by analogy
        with text_standard of textstat. The thresholds belong to the scale
        of the preset, since the same value means different things on the
        two scales.
        With the general preset, through the text types of the INFLESZ bands
        and the school stages of Spain:
            80-100 - 3 (comics and children's books, primary school grades 1-3)
            65-80 - 5 (primary school textbooks, grades 4-6)
            55-65 - 8 (general press, ESO)
            40-55 - 11 (secondary school textbooks, bachillerato)
            below 40 - 13 (scientific texts, university)
        With the classic preset, through the interpretation table of Flesch,
        whose bands Fernández Huerta kept: 90-100 - 5, 80-90 - 6, 70-80 - 7,
        60-70 - 8.5, 50-60 - 10, 40-50 - 11, 30-40 - 12, below 30 - 13
        Values above 100 belong to the first grade of the scale

    Arguments:
        flesch_reading_easy (float): Value of the reading ease
        preset (str): Coefficient preset whose scale is read

    Returns:
        float: Years of schooling

    Raises:
        ParameterError: If the preset is unknown
    """
    check_preset(preset)
    for threshold, grade in READING_EASE_GRADES[preset]:
        if flesch_reading_easy >= threshold:
            return grade
    return 13


def calc_consensus_grade(
    grades: Iterable[float], flesch_reading_easy: float | None = None, preset: str = "general"
) -> float:
    """
    Computing the consensus grade

    Description:
        The median of the rounded values of the grade formulas by analogy
        with text_standard of textstat, which uses the mode; the median
        is more robust to an outlying formula. The values are rounded half
        up. The reading ease is converted with flesch_reading_easy_to_grade
        by the scale of the preset and added without rounding

    Arguments:
        grades (list[float]): Values of the grade formulas
        flesch_reading_easy (float): Value of the reading ease
        preset (str): Coefficient preset of the reading ease

    Returns:
        float: Consensus grade

    Raises:
        ParameterError: If the list of values is empty or the preset is unknown
    """
    values = [float(floor(grade + 0.5)) for grade in grades]
    if flesch_reading_easy is not None:
        values.append(flesch_reading_easy_to_grade(flesch_reading_easy, preset))
    if not values:
        raise ParameterError("The list of grade formulas is empty")
    return float(median(values))


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
    """
    rounded = floor(grade + 0.5)
    for _, high, education, age in GRADE_AGE_LEVELS:
        if rounded <= high:
            return f"{education} ({age})"
    education, age = POSTGRADUATE_LEVEL
    return f"{education} ({age})"


def calc_reading_time(n_words: int, wpm: int = READING_SPEED_WPM) -> float:
    """
    Computing the reading time of a text

    Description:
        The default speed is the silent reading speed of adults in Spanish,
        278 words per minute (Brysbaert, 2019, mean of six studies; reading
        aloud - 191). The norms of school years from the meta-analysis of
        Ripoll, Tapia and Aguado (2020) are available in READING_SPEED_NORMS

    References:
        Brysbaert, M. How many words do we read per minute? A review and
            meta-analysis of reading rate. Journal of Memory and Language, 109, 2019
        Ripoll, J. C., Tapia, M. M., Aguado, G. Velocidad lectora en alumnado
            hispanohablante: un metaanálisis. Revista de Psicodidáctica, 25(2), 2020

    Arguments:
        n_words (int): Number of words
        wpm (int): Reading speed, words per minute

    Returns:
        float: Reading time in minutes

    Raises:
        ParameterError: If the reading speed is not positive
    """
    if wpm <= 0:
        raise ParameterError("The reading speed must be greater than 0")
    return n_words / wpm
