import string

# Punctuation marks and symbols, including the Spanish inverted marks,
# dashes, ellipsis, guillemets, curly quotes and the middle dot
PUNCTUATIONS = string.punctuation + "¿¡—–…«»“”‘’·"

# Characters that may open a sentence besides an upper-case letter or a digit:
# inverted question and exclamation marks, opening quotes and brackets,
# dashes of a dialogue line
SENTENCE_OPENERS = "¿¡«“\"'([—–-"

# Abbreviations after which a sentence does not end even before an upper-case
# word or a number: forms of address, references, times and eras; compared in
# lower case with the last one or two space-separated tokens before the period.
# Single capital initials (J. L. Borges) are recognized separately.
# Abbreviations that usually do end a sentence (etc.) or coincide with
# a word (mar., no.) are not listed
ABBREVIATIONS = frozenset(
    {
        # Forms of address and titles
        "sr.",
        "sra.",
        "srta.",
        "sres.",
        "sras.",
        "d.",
        "dña.",
        "dr.",
        "dra.",
        "dres.",
        "prof.",
        "profa.",
        "lic.",
        "lcdo.",
        "lcda.",
        "ing.",
        "arq.",
        "gral.",
        "cnel.",
        "cap.",
        "pdte.",
        "pdta.",
        "pbro.",
        "mons.",
        "fr.",
        "sto.",
        "sta.",
        "st.",
        "excmo.",
        "excma.",
        "ilmo.",
        "ilma.",
        "rvdo.",
        "rvda.",
        "ud.",
        "uds.",
        "vd.",
        "vds.",
        "ss.",
        "ee.",
        "ee. uu.",
        "ss. mm.",
        "s. m.",
        "s. a.",
        "s. l.",
        "cía.",
        "ltda.",
        "admón.",
        # References and text apparatus
        "p.",
        "pp.",
        "pág.",
        "págs.",
        "núm.",
        "núms.",
        "nro.",
        "n.",
        "vol.",
        "vols.",
        "t.",
        "caps.",
        "art.",
        "arts.",
        "fig.",
        "figs.",
        "ed.",
        "eds.",
        "col.",
        "ej.",
        "p. ej.",
        "v. gr.",
        "cf.",
        "cfr.",
        "vid.",
        "op.",
        "cit.",
        "op. cit.",
        "loc.",
        "loc. cit.",
        "ibíd.",
        "ibid.",
        "íd.",
        "id.",
        "trad.",
        "coord.",
        "comp.",
        "dir.",
        "s.",
        "sig.",
        "sigs.",
        "aprox.",
        "máx.",
        "mín.",
        "tel.",
        "tfno.",
        "av.",
        "avda.",
        "c.",
        "dpto.",
        "depto.",
        "izq.",
        "izqda.",
        "dcha.",
        "dcho.",
        # Times and eras
        "a.",
        "a. m.",
        "p. m.",
        "a. c.",
        "d. c.",
        "a. j. c.",
        "d. j. c.",
    }
)

# Vowels: every accented vowel is strong, an unaccented i, u, ü and a vocalic y
# are weak; a weak vowel next to another vowel forms a diphthong, two strong
# vowels a hiatus. Vowels with a grave, a circumflex, a tilde or a diaeresis
# other than ü come from Catalan, French, Portuguese and German names
# (Lluïsa, Citroën, São, Björk); they count as accented, so they are strong
# and take the stress. A diaeresis marks a hiatus in Catalan and French
# (Llu-ï-sa, Ci-tro-ën); the Portuguese nasal ã and õ join a following
# o or e into a diphthong (São, Ca-mões)
VOWELS = "aeiouáéíóúüàèìòùâêîôûãõäëïöå"
WEAK_VOWELS = "iuü"
ACCENTED_VOWELS = "áéíóúàèìòùâêîôûãõäëïöå"
HIATUS_VOWELS = "ïë"
NASAL_VOWELS = "ãõ"

# Two-letter consonant units that are never split (digraphs and the silent u)
DIGRAPHS = ("ch", "ll", "rr", "qu", "gu")

# Consonant pairs that open a syllable together: an obstruent with l or r
ONSET_CLUSTERS = frozenset(
    {"bl", "br", "cl", "cr", "dr", "fl", "fr", "gl", "gr", "kl", "kr", "pl", "pr", "tr"}
)

# Words in -mente that look like adverbs but are not, so they carry a single
# stress: adjectives and nouns, and subjunctives of verbs in -mentar whose stem
# ends like an adjective
NON_ADVERBS_MENTE = frozenset(
    {
        "clemente",
        "demente",
        "inclemente",
        "vehemente",
        "atormente",
        "cemente",
        "complemente",
        "fermente",
        "fundamente",
        "implemente",
        "incremente",
        "juramente",
        "lamente",
        "medicamente",
        "ornamente",
        "parlamente",
        "reglamente",
        "sacramente",
        "suplemente",
    }
)

# Whitespace counted as spaces by the basic statistics
SPACES = [" ", "\t"]

# Thresholds of the basic statistics: a complex word has three or more syllables,
# as in the Spanish readability formulas, a long word seven or more letters,
# as in LIX and RIX
COMPLEX_SYL_FACTOR = 3
LONG_WORD_LETTER_FACTOR = 7

# Types of punctuation marks; the inverted marks ¿ and ¡ count as question
# and exclamation marks, so a Spanish question carries two of them
PUNCTUATION_TYPES = {
    "comma": "Commas",
    "period": "Periods",
    "question": "Question marks",
    "exclamation": "Exclamation marks",
    "ellipsis": "Ellipses",
    "colon": "Colons",
    "semicolon": "Semicolons",
    "dash": "Dashes",
    "hyphen": "Hyphens",
    "angle_quotes": "Guillemets",
    "straight_quotes": "Straight and curly quotes",
    "parentheses": "Parentheses",
    "other": "Other marks",
}

BASIC_STATS_DESC = {
    "n_sents": "Sentences",
    "n_words": "Words",
    "n_unique_words": "Unique words",
    "n_long_words": "Long words",
    "n_complex_words": "Complex words",
    "n_simple_words": "Simple words",
    "n_monosyllable_words": "Monosyllabic words",
    "n_polysyllable_words": "Polysyllabic words",
    "n_chars": "Characters",
    "n_letters": "Letters",
    "n_spaces": "Spaces",
    "n_syllables": "Syllables",
    "n_punctuations": "Punctuation marks",
}

# Readability: thresholds of the formulas that differ from the basic statistics
LIX_LONG_WORD_LETTER_FACTOR = 7
SMOG_COMPLEX_SYL_FACTOR = 3

READABILITY_STATS_DESC = {
    "flesch_reading_easy": "Flesch reading ease (Szigriszt-Pazos)",
    "gutierrez_polini_index": "Gutiérrez de Polini comprehensibility",
    "crawford_grade": "Crawford grade",
    "mu_index": "Legibilidad µ",
    "sol_grade": "SOL grade (SMOG for Spanish)",
    "lix": "LIX readability index",
    "rix": "RIX readability index",
    "consensus_grade": "Consensus grade",
    "reading_time": "Reading time (min)",
}
READABILITY_GRADE_STATS = ("crawford_grade", "sol_grade")

# Coefficients (a, b, c) of the Flesch reading ease c - a * ASL - b * ASW for Spanish:
# general - Szigriszt-Pazos (1993), classic - Fernández Huerta (1959)
READABILITY_PRESETS: dict[str, dict[str, tuple[float, float, float]]] = {
    "general": {"flesch_reading_easy": (1.0, 62.3, 206.835)},
    "classic": {"flesch_reading_easy": (1.02, 60.0, 206.84)},
}

# Interpretation scales of the Flesch reading ease: lower bound of each band
READING_EASE_SCALES: dict[str, tuple[tuple[float, str], ...]] = {
    # Barrio-Cantalejo et al. (2008), for the Szigriszt-Pazos formula
    "inflesz": (
        (80, "muy fácil"),
        (65, "bastante fácil"),
        (55, "normal"),
        (40, "algo difícil"),
        (0, "muy difícil"),
    ),
    # Szigriszt-Pazos (1993): 0-15, 16-35, 36-50, 51-65, 66-75, 76-85, 86-100
    "szigriszt": (
        (86, "muy fácil"),
        (76, "fácil"),
        (66, "bastante fácil"),
        (51, "normal"),
        (36, "bastante difícil"),
        (16, "árido"),
        (0, "muy difícil"),
    ),
    # Fernández Huerta (1959)
    "fernandez_huerta": (
        (90, "muy fácil"),
        (80, "fácil"),
        (70, "bastante fácil"),
        (60, "normal"),
        (50, "bastante difícil"),
        (30, "difícil"),
        (0, "muy difícil"),
    ),
}
# Muñoz Baquedano and Muñoz Urra (2006): lower bound of each band of Legibilidad µ
MU_SCALE: tuple[tuple[float, str], ...] = (
    (91, "muy fácil"),
    (81, "fácil"),
    (71, "un poco fácil"),
    (61, "adecuado"),
    (51, "un poco difícil"),
    (31, "difícil"),
    (0, "muy difícil"),
)

# School stages of Spain by years of schooling from the first year of primary school
GRADE_AGE_LEVELS: tuple[tuple[int, int, str, str], ...] = (
    (1, 3, "primary school, grades 1-3", "6-9 years"),
    (4, 6, "primary school, grades 4-6", "9-12 years"),
    (7, 10, "ESO", "12-16 years"),
    (11, 12, "bachillerato", "16-18 years"),
    (13, 16, "university", "18-22 years"),
)
POSTGRADUATE_LEVEL = ("postgraduate", "over 22 years")

# Silent reading speed of adults in Spanish, words per minute: Brysbaert (2019),
# mean of six studies; reading aloud - 191
READING_SPEED_WPM = 278
# Reading speed norms (aloud, silent) in words per minute: means by school year
# from the meta-analysis of Ripoll, Tapia and Aguado (2020), grades 1-6 primary
# school, 7-10 ESO, 11 bachillerato; adults - Brysbaert (2019)
READING_SPEED_NORMS: dict[str, tuple[int, int]] = {
    "grade_1": (49, 30),
    "grade_2": (73, 79),
    "grade_3": (85, 95),
    "grade_4": (104, 125),
    "grade_5": (114, 137),
    "grade_6": (124, 155),
    "grade_7": (134, 180),
    "grade_8": (136, 176),
    "grade_9": (143, 180),
    "grade_10": (164, 200),
    "grade_11": (161, 186),
    "adult": (191, 278),
}

# Lexical diversity: the conventions of koRpus and lexical-diversity
MATTR_WINDOW_LEN = 50
MTLD_TTR_THRESHOLD = 0.72
MTLD_MIN_LEN = 10
HDD_SAMPLE_SIZE = 42
DIVERSITY_LOG_BASE = 10
BRUNET_W_EXPONENT = 0.172
DIVERSITY_STATS_DESC = {
    "ttr": "Type-Token Ratio (TTR)",
    "rttr": "Root Type-Token Ratio (RTTR)",
    "cttr": "Corrected Type-Token Ratio (CTTR)",
    "httr": "Herdan Type-Token Ratio (HTTR)",
    "sttr": "Summer Type-Token Ratio (STTR)",
    "mttr": "Maas Type-Token Ratio (MTTR)",
    "dttr": "Dugast Type-Token Ratio (DTTR)",
    "mattr": "Moving Average Type-Token Ratio (MATTR)",
    "msttr": "Mean Segmental Type-Token Ratio (MSTTR)",
    "mtld": "Measure of Textual Lexical Diversity (MTLD)",
    "mamtld": "Moving Average Measure of Textual Lexical Diversity (MA-MTLD)",
    "mtldw": "Moving Average Measure of Textual Lexical Diversity with Wrap (MTLD-W)",
    "hdd": "Hypergeometric Distribution D (HD-D)",
    "simpson_index": "Simpson's index (D)",
    "inverse_simpson_index": "Inverse Simpson's index (1/D)",
    "gini_simpson_index": "Gini-Simpson index (1-D)",
    "hapax_index": "Hapax index (Honoré's R)",
    "yule_k": "Yule's characteristic K",
    "yule_i": "Yule's inverse characteristic I",
    "herdan_vm": "Herdan's Vm",
    "sichel_s": "Sichel's S",
    "michea_m": "Michéa's M",
    "brunet_w": "Brunet's W",
    "dugast_k": "Dugast's k",
    "baayen_p": "Baayen's P",
    "hapax_ratio": "Hapax ratio",
    "alpha2": "Exponent α₂",
    "entropy": "Shannon entropy (bits)",
    "evenness": "Evenness",
    "perplexity": "Perplexity",
    "zipf_alpha": "Zipf's law slope (α)",
    "heaps_beta": "Heaps' law exponent (β)",
}
