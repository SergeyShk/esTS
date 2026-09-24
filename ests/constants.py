import string
from pathlib import Path

# Punctuation marks and symbols, including the Spanish inverted marks,
# dashes, ellipsis, guillemets, curly quotes and the middle dot
PUNCTUATIONS = string.punctuation + "¿¡—–…«»“”‘’·"

# Characters that may open a sentence besides an upper-case letter or a digit:
# inverted question and exclamation marks, opening quotes and brackets,
# dashes of a dialogue line
SENTENCE_OPENERS = "¿¡«“\"'([—–―-"

# Dashes that open a line of dialogue - the raya, the en dash, the horizontal bar
# of some digitized texts and the hyphen of plain text; one followed by a
# lower-case word opens the remark of the narrator inside the same sentence
# (-¿Vienes? -preguntó ella)
DASHES = "—–―-"

# Rules added to the tokenizer for the dashes of a dialogue glued to the words,
# as plain-text corpora type them (--No, -dijo, Juan- y, sí--dijo, reírse—me decía,
# dijo:—¡Mis, cuatro.-¿Cinco?, sí-¿y qué?): a run of hyphens before a letter or
# an opening mark, a run of hyphens after a letter at the end of a token, two or
# more hyphens or a long dash between letters, a hyphen between a letter and an
# opening mark, any dash after a closing mark, the closing marks before a dash
# and an opening mark after one are split off, and the horizontal bar ― as the
# raya and the en dash at the ends of a token, with the closing marks after it
# (él―.). The underscores of the italics of
# Project Gutenberg (--_Siguro_, lux_--dijo) count as opening and closing marks.
# A single hyphen between two letters (franco-alemán) or before a digit (-5) is
# left alone
_LETTER = r"[^\W\d_]"
_OPENING = r"[¿¡«“\"'(\[_]"
_CLOSING = r"[.,;:!?…»”\"')\]_]"
_DASH = r"(?:-+|[—–―])"
TOKENIZER_PREFIXES = (rf"-+(?={_LETTER}|{_OPENING})", "―")
TOKENIZER_SUFFIXES = (rf"(?<={_LETTER})-+", "―", rf"(?<=―){_CLOSING}")
TOKENIZER_INFIXES = (
    rf"(?<={_LETTER})(?:-{{2,}}|[—–―])(?={_LETTER}|{_OPENING})",
    rf"(?<={_LETTER})-(?={_OPENING})",
    rf"(?<={_CLOSING}){_DASH}(?={_LETTER}|{_OPENING})",
    rf"(?<={_LETTER}){_CLOSING}+(?={_DASH})",
    rf"(?<=[-—–―]){_OPENING}",
)

# Abbreviations after which a sentence does not end even before an upper-case
# word or a number: forms of address, references, times and eras; compared in
# lower case with the last one or two space-separated tokens before the period.
# Single capital initials (J. L. Borges) are recognized separately.
# Abbreviations that usually do end a sentence (etc.) or coincide with
# a word (mar., no.) are not listed. The ones of time (a. m., p. m.) are listed
# although they often close a sentence. The list decides nothing before a
# lower-case word, which never opens a sentence; it decides before an upper-case
# word or a digit, and there the readings collide: a digit usually continues the
# sentence (a las 5 p. m. 30 personas esperaban), an upper-case word usually
# opens a new one (Llegó a las 5 p. m. Luego se fue). Keeping the abbreviation
# joins both, and joining two sentences costs less than cutting one in half
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

# Interpretation of each preset: the scale of describe_level and the thresholds
# that convert the reading ease into years of schooling for the consensus grade.
# The INFLESZ bands are read through their text types and the school stages of
# Spain; the bands of Fernández Huerta are those of Flesch, so his own
# interpretation table gives the grades
PRESET_SCALES: dict[str, str] = {"general": "inflesz", "classic": "fernandez_huerta"}
READING_EASE_GRADES: dict[str, tuple[tuple[float, float], ...]] = {
    "general": ((80, 3), (65, 5), (55, 8), (40, 11)),
    "classic": ((90, 5), (80, 6), (70, 7), (60, 8.5), (50, 10), (40, 11), (30, 12)),
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
# Block of factor starts and window of offsets in the MA-MTLD and MTLD-W computation
MTLD_BLOCK_SIZE = 4096
MTLD_WINDOW_LEN = 32
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


# Model of spaCy that the statistics on Universal Dependencies fall back to
SPACY_MODEL = "es_core_news_sm"

# Directory where the datasets are downloaded by default: next to the package
DEFAULT_DATA_DIR = Path(__file__).parent.parent.resolve() / "ests_data"

# Morphological features counted by the statistics, by the name of the statistic.
# The Spanish models annotate 23 features; the ones left out are either marginal
# (AdvType, Foreign, NumForm, Number[psor], PrepCase, Typo) or live on punctuation
# (PunctSide, PunctType), which is not a word. They all stay inside the tags string
MORPHOLOGY_FEATURES = {
    "case": "Case",
    "definite": "Definite",
    "degree": "Degree",
    "gender": "Gender",
    "mood": "Mood",
    "num_type": "NumType",
    "number": "Number",
    "person": "Person",
    "polarity": "Polarity",
    "polite": "Polite",
    "poss": "Poss",
    "pron_type": "PronType",
    "reflex": "Reflex",
    "tense": "Tense",
    "verb_form": "VerbForm",
}

MORPHOLOGY_STATS_DESC: dict[str, dict[str, object]] = {
    "pos": {
        "name": "Part of speech",
        "values": {
            "NOUN": "Noun",
            "PROPN": "Proper noun",
            "ADJ": "Adjective",
            "ADV": "Adverb",
            "VERB": "Verb",
            "AUX": "Auxiliary verb",
            "PRON": "Pronoun",
            "DET": "Determiner",
            "NUM": "Numeral",
            "ADP": "Adposition",
            "CCONJ": "Coordinating conjunction",
            "SCONJ": "Subordinating conjunction",
            "PART": "Particle",
            "INTJ": "Interjection",
            "SYM": "Symbol",
            "X": "Other",
        },
    },
    "case": {
        "name": "Case",
        "values": {"Nom": "Nominative", "Acc": "Accusative", "Dat": "Dative", "Com": "Comitative"},
    },
    "definite": {"name": "Definiteness", "values": {"Def": "Definite", "Ind": "Indefinite"}},
    "degree": {
        "name": "Degree",
        "values": {"Cmp": "Comparative", "Sup": "Superlative", "Abs": "Absolute superlative"},
    },
    "gender": {"name": "Gender", "values": {"Masc": "Masculine", "Fem": "Feminine"}},
    "mood": {
        "name": "Mood",
        "values": {
            "Ind": "Indicative",
            "Sub": "Subjunctive",
            "Imp": "Imperative",
            "Cnd": "Conditional",
        },
    },
    "num_type": {
        "name": "Numeral type",
        "values": {"Card": "Cardinal", "Ord": "Ordinal", "Frac": "Fraction"},
    },
    "number": {"name": "Number", "values": {"Sing": "Singular", "Plur": "Plural"}},
    "person": {"name": "Person", "values": {"1": "First", "2": "Second", "3": "Third"}},
    "polarity": {"name": "Polarity", "values": {"Neg": "Negative"}},
    "polite": {"name": "Politeness", "values": {"Form": "Formal"}},
    "poss": {"name": "Possessive", "values": {"Yes": "Possessive"}},
    "pron_type": {
        "name": "Pronoun type",
        "values": {
            "Art": "Article",
            "Prs": "Personal",
            "Dem": "Demonstrative",
            "Ind": "Indefinite",
            "Int": "Interrogative",
            "Rel": "Relative",
            "Neg": "Negative",
            "Tot": "Total",
            "Exc": "Exclamative",
        },
    },
    "reflex": {"name": "Reflexive", "values": {"Yes": "Reflexive"}},
    "tense": {
        "name": "Tense",
        "values": {"Pres": "Present", "Past": "Past", "Imp": "Imperfect", "Fut": "Future"},
    },
    "verb_form": {
        "name": "Verb form",
        "values": {"Fin": "Finite", "Inf": "Infinitive", "Part": "Participle", "Ger": "Gerund"},
    },
}

# Spanish markers computed on top of the features, each a share of its own base
MORPHOLOGY_MARKERS_DESC = {
    "p_indicative": "Indicative among the finite forms",
    "p_subjunctive": "Subjunctive among the finite forms",
    "p_conditional": "Conditional among the finite forms",
    "p_imperative": "Imperative among the finite forms",
    "p_infinitive": "Infinitive among the verb forms",
    "p_gerund": "Gerund among the verb forms",
    "p_participle": "Participle among the verb forms",
    "p_ser": "ser among the copulas ser and estar",
    "p_mente_adverbs": "Adverbs in -mente among the adverbs",
}

# The two copulas of Spanish, by lemma
COPULAS = ("ser", "estar")


# Dependencies that head a clause: the subtypes of Universal Dependencies are not
# used by the Spanish models, which give acl for a relative clause as well
CLAUSE_DEPS = frozenset({"ccomp", "advcl", "acl", "csubj", "parataxis"})
SUBORDINATE_CLAUSE_DEPS = frozenset({"ccomp", "advcl", "acl", "csubj"})
SUBJECT_DEPS = frozenset({"nsubj", "csubj"})
VALENCY_IGNORED_DEPS = frozenset({"cc", "conj", "parataxis", "punct"})
NOUN_MODIFIER_DEPS = frozenset({"amod", "det", "nmod", "nummod", "acl"})
# Prepositions of a chain of complements (el aumento de la eficiencia del uso) and
# of the agent of a passive (construida por los obreros); the contractions del and al
# keep their own lemma in the models, so they are listed as they are written
DE_PREPOSITIONS = frozenset({"de", "del"})
AGENT_PREPOSITION = "por"
# Auxiliary of the periphrastic passive (fue construida), the se of the passive
# (se construyó la casa) and the se of an impersonal sentence (se vive bien)
PASSIVE_AUX = "ser"
SE_PASSIVE_DEP = "expl:pass"
SE_IMPERSONAL_DEP = "expl:impers"
# Words of negation: only no carries Polarity=Neg in the models, the others are
# recognized by their form; ni is left to the conjunctions of ni... ni
NEGATION_WORDS = frozenset(
    {
        "no",
        "nunca",
        "jamás",
        "nada",
        "nadie",
        "ningún",
        "ninguno",
        "ninguna",
        "ningunos",
        "ningunas",
        "tampoco",
    }
)
# Suffixes and lemmas of the nouns derived from a verb, the nominal part of a split
# predicate (hacer una revisión, tomar una decisión). The heuristic catches nouns of
# other origins with the same endings (ciencia, distancia), as any suffix rule does
VERBAL_NOUN_SUFFIXES = ("ción", "sión", "miento", "anza", "encia", "ancia", "aje", "dura", "azgo")
VERBAL_NOUN_LEMMAS = frozenset(
    {
        "abandono",
        "análisis",
        "apoyo",
        "ataque",
        "aviso",
        "cambio",
        "comienzo",
        "control",
        "desarrollo",
        "empleo",
        "consulta",
        "entrega",
        "envío",
        "estudio",
        "intento",
        "lectura",
        "mejora",
        "olvido",
        "pago",
        "prueba",
        "rechazo",
        "reforma",
        "respuesta",
        "traslado",
        "uso",
    }
)
# Verbs that carry only the grammar of a split predicate, the meaning being in the noun
LIGHT_VERBS = frozenset(
    {
        "dar",
        "efectuar",
        "ejercer",
        "hacer",
        "llevar",
        "poner",
        "prestar",
        "proceder",
        "proporcionar",
        "realizar",
        "tener",
        "tomar",
    }
)
# Nouns of the fixed split predicates that no suffix gives away, by the verbs they
# are fixed with: parte, lugar, caso and cuenta are ordinary nouns with any other
# verb (dar traslado a las partes, poner en primer lugar la seguridad)
SPLIT_PREDICATE_NOUNS = {
    "cabo": ("llevar",),
    "cargo": ("hacer", "tener"),
    "caso": ("hacer",),
    "comienzo": ("dar",),
    "cuenta": ("dar", "tener"),
    "efecto": ("hacer", "tener"),
    "fin": ("dar", "poner"),
    "gala": ("hacer",),
    "hincapié": ("hacer",),
    "lugar": ("tener", "dar"),
    "manifiesto": ("poner",),
    "marcha": ("poner",),
    "parte": ("tomar", "formar"),
}
# Light verbs whose nominal part comes with a preposition: se procedió a la votación
PREPOSITIONAL_LIGHT_VERBS = frozenset({"proceder"})
# Verbs of the periphrases with a gerund: sigue trabajando, lleva años estudiando.
# The models attach the gerund of these as xcomp or advcl instead of an auxiliary
GERUND_PERIPHRASIS_VERBS = frozenset(
    {"seguir", "continuar", "ir", "venir", "andar", "llevar", "quedar", "acabar"}
)

SYNTAX_STATS_DESC = {
    "mean_dependency_distance": "Mean dependency distance",
    "std_dependency_distance": "Standard deviation of the dependency distance",
    "max_dependency_distance": "Mean of the longest dependencies of the sentences",
    "p_adjacent_dependencies": "Share of adjacent dependencies",
    "tree_depth": "Depth of the dependency tree",
    "leaves_per_sent": "Leaves per sentence",
    "subtrees_per_sent": "Subtrees per sentence",
    "nodes_per_leaf": "Mean of the nodes per leaf of the sentences",
    "verb_valency": "Valency of the finite verbs",
    "coordination_chains_per_sent": "Coordination chains per sentence",
    "mean_coordination_chain_len": "Mean length of a coordination chain",
    "clauses_per_sent": "Clauses per sentence",
    "mean_clause_len": "Mean length of a clause (words)",
    "subordinate_clauses_per_sent": "Subordinate clauses per sentence",
    "p_complex_sents": "Share of sentences with a subordinate clause",
    "modifiers_per_noun": "Modifiers per noun phrase",
    "de_chains_per_sent": "Chains of de per sentence",
    "max_de_chain_len": "Maximum length of a chain of de",
    "participle_clauses_per_sent": "Participial clauses per sentence",
    "mean_participle_clause_len": "Mean length of a participial clause (words)",
    "gerund_clauses_per_sent": "Gerund clauses per sentence",
    "mean_gerund_clause_len": "Mean length of a gerund clause (words)",
    "p_passive": "Share of passive forms among the verbs",
    "p_agentless_passive": "Share of agentless forms among the passive ones",
    "se_passives_per_sent": "Passives with se per sentence",
    "impersonal_se_per_sent": "Impersonal sentences with se per sentence",
    "infinitives_per_sent": "Infinitives per sentence",
    "negations_per_sent": "Words of negation per sentence",
    "split_predicates_per_sent": "Split predicates per sentence",
    "noun_verb_ratio": "Ratio of nouns to verbs",
}


# Parts of speech of a content word, as Universal Dependencies names them
CONTENT_UD_POS = frozenset({"NOUN", "PROPN", "ADJ", "VERB", "ADV"})
# Classes of the discourse markers, by Martín Zorraquino and Portolés
CONNECTOR_CLASSES = {
    "causal": "causal",
    "adversative": "adversative",
    "concessive": "concessive",
    "temporal": "temporal",
    "additive": "additive",
    "conditional": "conditional",
    "reformulative": "reformulative",
}
# Kinds of the discourse markers: conjunctions, conjunctive locutions and adverbs
# against the lexicalized phrases (sin embargo, por lo tanto, es decir)
CONNECTOR_TYPES = {"primary": "primary", "secondary": "secondary"}
# Parts of speech a one-word marker may carry. PROPN is among them because the models
# read a marker that opens a sentence as a proper noun (Primeramente, Concluyendo)
CONNECTOR_POS = frozenset({"CCONJ", "SCONJ", "PART", "ADV", "ADP", "INTJ", "PROPN", "X"})
# Parts of speech allowed for single markers on top of CONNECTOR_POS
CONNECTOR_POS_EXTRA = {
    "pues": frozenset({"NOUN"}),
    "resumiendo": frozenset({"VERB"}),
    "recapitulando": frozenset({"VERB"}),
    "concluyendo": frozenset({"VERB"}),
    "verbigracia": frozenset({"NOUN"}),
}
# Words that turn a marker into a part of a prepositional phrase: antes de la
# reunión, por encima de 80, al final de la línea are no discourse markers
CONNECTOR_BLOCKED_AFTER = {
    "antes": frozenset({"de", "del"}),
    "después": frozenset({"de", "del"}),
    "encima": frozenset({"de", "del"}),
    "al final": frozenset({"de", "del"}),
    "al principio": frozenset({"de", "del"}),
    "al comienzo": frozenset({"de", "del"}),
    "luego": frozenset({"de", "del"}),
}
CONNECTOR_BLOCKED_BEFORE = {"encima": frozenset({"por"})}
# Parts of speech of the following word that turn a marker into a phrase of its own:
# sobre todo el texto is sobre + todo el texto, sobre todo cuando is the marker
CONNECTOR_BLOCKED_AFTER_POS = {"sobre todo": frozenset({"DET"})}

COHESION_STATS_DESC = {
    "noun_overlap_adjacent": "Noun overlap in adjacent sentences",
    "noun_overlap_all": "Noun overlap in all pairs of sentences",
    "argument_overlap_adjacent": "Argument overlap in adjacent sentences",
    "argument_overlap_all": "Argument overlap in all pairs of sentences",
    "content_overlap_adjacent": "Content word overlap in adjacent sentences",
    "content_overlap_all": "Content word overlap in all pairs of sentences",
    "content_overlap_prop_adjacent": "Share of shared content words in adjacent sentences",
    "content_overlap_prop_all": "Share of shared content words in all pairs of sentences",
    "p_pronouns": "Share of pronouns",
    "pronoun_noun_ratio": "Ratio of pronouns to nouns",
    "p_demonstratives": "Share of demonstratives",
    "p_given": "Share of content words seen before",
    "tense_repetition": "Repetition of the tense in adjacent sentences",
    "mood_repetition": "Repetition of the mood in adjacent sentences",
    "temporal_cohesion": "Temporal cohesion",
    "connectors": "Connectors per 1000 words",
    "connectors_causal": "Causal connectors per 1000 words",
    "connectors_adversative": "Adversative connectors per 1000 words",
    "connectors_concessive": "Concessive connectors per 1000 words",
    "connectors_temporal": "Temporal connectors per 1000 words",
    "connectors_additive": "Additive connectors per 1000 words",
    "connectors_conditional": "Conditional connectors per 1000 words",
    "connectors_reformulative": "Reformulative connectors per 1000 words",
    "connectors_primary": "Primary connectors per 1000 words",
    "connectors_secondary": "Secondary connectors per 1000 words",
}


# Measures of keyness, of association of collocations, of dispersion of words and of stylometry
KEYNESS_MEASURES = {
    "log_likelihood": "Log-likelihood G²",
    "chi2": "Chi-square with Yates's correction",
    "diff": "Difference of normalized frequencies %DIFF",
    "log_ratio": "Binary logarithm of the ratio of normalized frequencies",
    "bic": "Bayesian information criterion",
    "ell": "Effect size for the log-likelihood",
    "odds_ratio": "Odds ratio",
}
# Critical values of G² with one degree of freedom, by the level of significance
G2_CRITICAL_VALUES = {0.05: 3.84, 0.01: 6.63, 0.001: 10.83, 0.0001: 15.13}
COLLOCATION_MEASURES = {
    "mi": "Mutual information MI",
    "mi3": "Cubic mutual information MI³",
    "t_score": "t-score",
    "dice": "Dice coefficient",
    "logdice": "logDice",
    "log_likelihood": "Log-likelihood G²",
    "npmi": "Normalized pointwise mutual information",
    "min_sensitivity": "Minimum sensitivity",
}
DISPERSION_STATS_DESC = {
    "dp": "Deviation of proportions DP of Gries",
    "dp_norm": "Normalized DP",
    "juilland_d": "Juilland's D",
    "carroll_d2": "Carroll's D2",
    "rosengren_s": "Rosengren's S",
    "kl_divergence": "Kullback-Leibler divergence",
}
# Marks that stay with the first word of a window of a text: quotes, brackets,
# dashes of a dialogue and the inverted marks
OPENING_MARKS = frozenset('«"„“‘([{—–―-¿¡')
# Opening marks that close as well - the straight quote and the dashes of an aside:
# glued to the end of a word they close it and stay in its window
SYMMETRIC_MARKS = frozenset('"—–―-')
DELTA_VARIANTS = {
    "burrows": "Burrows's Delta - Manhattan distance of the z-scores divided by the number of units",
    "quadratic": "Argamon's quadratic Delta - Euclidean distance of the z-scores divided by the number of units",
    "eder": "Eder's Delta - Manhattan distance of the z-scores weighted by rank",
    "cosine": "Cosine Delta - cosine distance of the z-scores",
}
# Parts of speech of the function words: adpositions, conjunctions, particles,
# pronouns, determiners and interjections
FUNCTION_UD_POS = ("ADP", "CCONJ", "SCONJ", "PART", "PRON", "DET", "INTJ")
