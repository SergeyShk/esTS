# The ZeroGPU hardware of the Space wants its package imported before spaCy
try:
    import spaces
except ImportError:
    spaces = None

import threading
from collections import Counter
from functools import lru_cache
from importlib.metadata import version
from io import BytesIO
from math import isnan

import gradio as gr
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import spacy
from PIL import Image
from spacy.tokens import Doc

from ests import (
    BasicStats,
    CohesionStats,
    DiversityStats,
    LexicalStats,
    MorphStats,
    PhonStats,
    ReadabilityStats,
    StyleStats,
    SyntaxStats,
    VerseStats,
    WordsExtractor,
)
from ests.constants import (
    BASIC_STATS_DESC,
    COHESION_STATS_DESC,
    HIGHLIGHT_DEFAULT_LAYERS,
    HIGHLIGHT_LAYER_GROUPS,
    HIGHLIGHT_LAYERS_DESC,
    LEXICAL_STATS_DESC,
    MORPHOLOGY_MARKERS_DESC,
    MORPHOLOGY_STATS_DESC,
    PHON_STATS_DESC,
    READABILITY_STATS_DESC,
    STYLE_STATS_DESC,
    SYNTAX_STATS_DESC,
    VERSE_STATS_DESC,
)
from ests.corpus import collocations, keyness
from ests.datasets import FreqDict
from ests.exceptions import SourceError
from ests.style_stats import is_stopword
from ests.utils import get_nlp
from ests.visualizers import highlight, sentence_lengths_plot, zipf

matplotlib.use("Agg")

MAX_CHARS = 20_000
ZIPF_WORDS = 100
SENTENCES_MIN = 5
SENTENCES_WINDOW = 5
ZIPF_MIN_WORDS = 100
KEYWORDS_TOP_N = 15
COLLOCATION_WINDOW = 3
VERSE_MAX_LINES = 40
VERSE_PATTERN_WIDTH = 24
VERSE_NOTE = (
    "The stresses follow the rules of Spanish and are fitted to the meter; the pattern of a line "
    "is `-` for an unstressed syllable and `+` for a stressed one, the letter is its rhyme group, "
    "a hyphen an unrhymed line. Paste a poem line by line: a single line or a short phrase has "
    "no meter."
)
KEYWORDS_NOTE = (
    "Keywords are the words noticeably more frequent in the text than in the frequency "
    "dictionary of Google Books Ngram, as lemmas without the stopwords (G² - significance, "
    "Log Ratio - the binary logarithm of how many times more frequent). Collocations are pairs "
    "of content lemmas within three words of each other met at least twice, by logDice; a short "
    "text may have none."
)
POS_NAMES = MORPHOLOGY_STATS_DESC["pos"]["values"]
EXAMPLES = {
    "Tale": (
        "Había una vez un campesino que tenía una gallina muy especial. Cada mañana la gallina "
        "ponía un huevo de oro. El campesino vendía los huevos en el mercado del pueblo y poco "
        "a poco se hizo rico. Pero un día pensó: «Si esta gallina pone huevos de oro, dentro "
        "debe de tener un tesoro». Tomó un cuchillo, mató a la gallina y la abrió. Dentro no "
        "había nada. Así perdió el campesino su gallina y todos sus huevos de oro por querer "
        "tenerlo todo de una vez."
    ),
    "Sonnet": (
        "Cuando me paro a contemplar mi estado\n"
        "y a ver los pasos por do me han traído,\n"
        "hallo, según por do anduve perdido,\n"
        "que a mayor mal pudiera haber llegado;\n\n"
        "mas cuando del camino estó olvidado,\n"
        "a tanto mal no sé por dó he venido;\n"
        "sé que me acabo, y más he yo sentido\n"
        "ver acabar comigo mi cuidado.\n\n"
        "Yo acabaré, que me entregué sin arte\n"
        "a quien sabrá perderme y acabarme\n"
        "si quisiere, y aún sabrá querello;\n\n"
        "que pues mi voluntad puede matarme,\n"
        "la suya, que no es tanto de mi parte,\n"
        "pudiendo, ¿qué hará sino hacello?"
    ),
    "News": (
        "El ayuntamiento aprobó ayer el programa de reforma de los patios interiores para el "
        "próximo año. Según el documento, en primer lugar se repararán los accesos y los parques "
        "infantiles de los barrios construidos antes de 1980, y las solicitudes que los vecinos "
        "presenten a través de la sede electrónica se estudiarán en el plazo de un mes. El gasto "
        "se calcula en doscientos millones de euros, y las empresas se elegirán por concurso "
        "público en marzo.\n\n"
        "El programa durará tres años. El primer año se arreglarán cuarenta patios, el segundo "
        "sesenta y el tercero todos los demás. Los vecinos podrán seguir las obras en un mapa "
        "que aparecerá en la web municipal en primavera, con las direcciones, los plazos y las "
        "empresas. Según explicó el servicio de prensa, para elegir los patios se tuvieron en "
        "cuenta la antigüedad de los edificios, el estado del pavimento y el número de quejas. "
        "Los concejales apoyaron el programa por unanimidad, pero pidieron que se informe de su "
        "cumplimiento cada trimestre y no una vez al año, como proponía el ayuntamiento."
    ),
    "Science": (
        "Los tesauros son una clase especial de recursos lexicográficos que se caracterizan por "
        "los siguientes rasgos: la completitud de los significados del vocabulario de una lengua "
        "o de alguno de sus segmentos; la ordenación temática, o ideográfica, de los significados "
        "de las palabras. La diferencia entre los tesauros y las ontologías formales consiste en "
        "la salida hacia la esfera de los significados léxicos, en el establecimiento de "
        "relaciones no solo entre los significados y las palabras que los expresan, sino también "
        "entre los propios significados (el registro de diversas relaciones semánticas dentro "
        "del diccionario).\n\n"
        "La construcción de un tesauro supone delimitar los conceptos de un dominio, establecer "
        "entre ellos relaciones de sinonimia, hiponimia y asociación y asignar a cada concepto un "
        "conjunto de entradas textuales, es decir, las palabras y las expresiones con las que se "
        "expresa en los textos. La estructura resultante se emplea para ampliar las consultas en "
        "la búsqueda de información, clasificar documentos de forma automática y resolver la "
        "ambigüedad léxica, ya que permite relacionar formulaciones distintas con un mismo "
        "significado."
    ),
    "Officialese": (
        "El proyecto, elaborado durante el verano, fue aprobado por el consejo sin debate. "
        "El aumento de la eficiencia del uso de los recursos públicos se analizó, siguiendo "
        "las normas del reglamento. Los representantes de los ministerios regionales no "
        "consiguieron hacer una revisión conjunta de las cuestiones de financiación y de reparto "
        "de responsabilidades entre los organismos, puesto que cada uno de ellos defendía su "
        "propia interpretación de las disposiciones del acuerdo. En el marco de la reunión se "
        "procedió a la votación, y la decisión quedó aplazada hasta la próxima sesión.\n\n"
        "Como resultado de la reunión, se adoptó la decisión de llevar a cabo consultas "
        "adicionales con la participación de los representantes de los organismos interesados "
        "a efectos de la elaboración de una posición común sobre la cuestión del reparto de "
        "competencias. La responsabilidad de la organización de las consultas y de la "
        "preparación del acta correspondiente fue atribuida a la secretaría, que deberá "
        "garantizar la consideración de las observaciones recibidas en el transcurso del debate."
    ),
}

DEFAULT_LAYERS = list(HIGHLIGHT_DEFAULT_LAYERS)
DEFAULT_GROUP_LAYERS = [
    [layer for layer in group if layer in HIGHLIGHT_DEFAULT_LAYERS]
    for group in HIGHLIGHT_LAYER_GROUPS.values()
]
nlp = get_nlp()
freq_dict = FreqDict()
if not freq_dict.filepath:
    try:
        freq_dict.download()
    except (RuntimeError, OSError) as error:
        print(f"The frequency dictionary is not available: {error}")
plot_lock = threading.Lock()

if spaces is not None:

    @spaces.GPU
    def gpu_placeholder() -> None:
        """ZeroGPU starts a Space only with a GPU function; the demo computes on the CPU"""


@lru_cache(maxsize=32)
def parse(text: str) -> Doc:
    return nlp(text, disable=["ner"])


def format_value(value: float | int | str | None) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return "-" if isnan(value) else f"{value:.2f}"
    return str(value)


def stats_table(stats: dict[str, float], desc: dict[str, str]) -> pd.DataFrame:
    rows = [(desc[key], format_value(stats[key])) for key in desc if key in stats]
    return pd.DataFrame(rows, columns=["Metric", "Value"])


def format_reading_time(minutes: float) -> str:
    if minutes < 1:
        return "less than a minute"
    total = round(minutes)
    if total < 60:
        return f"{total} min"
    return f"{total // 60} h {total % 60} min"


def readability_summary(rs: ReadabilityStats) -> str:
    grade = rs.describe_grade()
    return (
        f"### {grade[:1].upper()}{grade[1:]}\n\n"
        f"Consensus grade - **{rs.consensus_grade:.1f}**, "
        f"Flesch reading ease by Szigriszt-Pazos - **{rs.flesch_reading_easy:.0f}** "
        f"({rs.describe_level()} on the INFLESZ scale), "
        f"reading time - **{format_reading_time(rs.reading_time)}**."
    )


def lexical_table(ls: LexicalStats) -> pd.DataFrame:
    if freq_dict.filepath:
        return stats_table(ls.get_stats(), LEXICAL_STATS_DESC)
    bands = {
        key: getattr(ls, key)
        for key in LEXICAL_STATS_DESC
        if key.startswith(("p_top", "p_beyond"))
    }
    bands["lexical_density"] = ls.lexical_density
    return stats_table(bands, LEXICAL_STATS_DESC)


def keywords_table(forms: tuple[str, ...]) -> pd.DataFrame:
    columns = [
        "Lemma",
        "In the text",
        "ipm in the text",
        "ipm in the dictionary",
        "G²",
        "Log Ratio",
    ]
    if not freq_dict.filepath or not forms:
        return pd.DataFrame(columns=columns)
    try:
        found = keyness(forms, freq_dict, min_freq=2)
    except SourceError:
        # No word of the text is made of the letters of the dictionary
        return pd.DataFrame(columns=columns)
    keywords = [keyword for keyword in found if not is_stopword(keyword.word)][:KEYWORDS_TOP_N]
    return pd.DataFrame(
        [
            (
                keyword.word,
                keyword.freq_target,
                round(keyword.ipm_target),
                round(keyword.ipm_reference, 1),
                round(keyword.g2, 1),
                round(keyword.log_ratio, 2),
            )
            for keyword in keywords
        ],
        columns=columns,
    )


def collocations_table(lemmas: tuple[str, ...]) -> pd.DataFrame:
    found = [
        collocation
        for collocation in collocations(lemmas, window=COLLOCATION_WINDOW, min_freq=2)
        if not is_stopword(collocation.left) and not is_stopword(collocation.right)
    ]
    return pd.DataFrame(
        [
            (
                f"{collocation.left} … {collocation.right}",
                collocation.freq_pair,
                round(collocation.score, 2),
            )
            for collocation in found[:KEYWORDS_TOP_N]
        ],
        columns=["Pair", "Together", "logDice"],
    )


def verse_tables(doc: Doc) -> tuple[pd.DataFrame, str]:
    vs = VerseStats(doc)
    if not vs.n_lines:
        return stats_table(vs.get_stats(), VERSE_STATS_DESC), "*The text has no Spanish words.*"
    accented = [line for stanza in vs.accentuate().split("\n\n") for line in stanza.split("\n")]
    letters = [letter for scheme in vs.rhyme_schemes for letter in scheme]
    rows = []
    for pattern, letter, line in zip(vs.patterns, letters, accented, strict=True):
        if len(pattern) > VERSE_PATTERN_WIDTH:
            pattern = pattern[: VERSE_PATTERN_WIDTH - 1] + "…"
        rows.append(f"{pattern:<{VERSE_PATTERN_WIDTH}} {letter} {line}")
    if len(rows) > VERSE_MAX_LINES:
        rows = [*rows[:VERSE_MAX_LINES], f"… {len(rows) - VERSE_MAX_LINES} more lines"]
    return stats_table(vs.get_stats(), VERSE_STATS_DESC), "```\n" + "\n".join(rows) + "\n```"


def morph_tables(ms: MorphStats) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    stats = ms.get_stats(filter_none=True)
    pos = sorted(stats["pos"].items(), key=lambda item: -item[1])
    pos_table = pd.DataFrame(
        [(POS_NAMES.get(tag, tag), count) for tag, count in pos],
        columns=["Part of speech", "Words"],
    )
    rows = []
    for category, counts in stats.items():
        if category == "pos":
            continue
        desc = MORPHOLOGY_STATS_DESC[category]
        for value, count in sorted(counts.items(), key=lambda item: -item[1]):
            rows.append((desc["name"], desc["values"].get(value, value), count))
    features = pd.DataFrame(rows, columns=["Feature", "Value", "Words"])
    return pos_table, features, stats_table(ms.get_markers(), MORPHOLOGY_MARKERS_DESC)


def figure_image(fig: plt.Figure) -> Image.Image:
    buffer = BytesIO()
    fig.tight_layout()
    fig.savefig(buffer, format="png", dpi=150)
    plt.close(fig)
    buffer.seek(0)
    return Image.open(buffer)


def zipf_image(lemmas: tuple[str, ...]) -> Image.Image:
    counter = Counter(lemma for lemma in lemmas if not is_stopword(lemma))
    with plot_lock:
        fig, ax = plt.subplots(figsize=(7, 4.5))
        zipf(
            counter,
            num_words=min(ZIPF_WORDS, len(counter)),
            num_labels=6,
            show_theory=True,
            alpha=1.1,
            show_fit=True,
            ax=ax,
        )
        return figure_image(fig)


def sentences_image(doc: Doc) -> Image.Image:
    with plot_lock:
        fig, ax = plt.subplots(figsize=(7, 3.5))
        sentence_lengths_plot(doc, window=SENTENCES_WINDOW, ax=ax)
        return figure_image(fig)


def render_highlight(text: str, layers: list[str]) -> str:
    return highlight(parse(text), layers=layers).to_html()


def compute(text: str, layers: list[str]) -> dict:
    text = text.strip()[:MAX_CHARS]
    if not text:
        raise ValueError("Paste a text to analyze")
    doc = parse(text)
    bs = BasicStats(doc)
    rs = ReadabilityStats(doc)
    ds = DiversityStats(doc)
    ms = MorphStats(doc)
    ss = StyleStats(doc)
    ps = PhonStats(doc)
    xs = SyntaxStats(doc)
    cs = CohesionStats(doc)
    ls = LexicalStats(doc, freq_dict=freq_dict)
    forms = WordsExtractor(filter_nums=True).extract(text)
    lemmas = WordsExtractor(use_lexemes=True, lowercase=True, filter_nums=True).extract(text)
    pos_table, morph_table, markers_table = morph_tables(ms)
    verse_table, verse_lines = verse_tables(doc)
    basic = {key: value for key, value in bs.get_stats().items() if key in BASIC_STATS_DESC}
    enough_words = bs.n_words >= ZIPF_MIN_WORDS
    enough_sents = bs.n_sents >= SENTENCES_MIN
    return {
        "text": text,
        "highlight": highlight(doc, layers=layers).to_html(),
        "summary": readability_summary(rs),
        "readability": stats_table(rs.get_stats(), READABILITY_STATS_DESC),
        "diversity": stats_table(ds.get_stats(), DiversityStats.stats_desc),
        "pos": pos_table,
        "morph": morph_table,
        "markers": markers_table,
        "syntax": stats_table(xs.get_stats(), SYNTAX_STATS_DESC),
        "cohesion": stats_table(cs.get_stats(), COHESION_STATS_DESC),
        "lexical": lexical_table(ls),
        "style": stats_table(ss.get_stats(), STYLE_STATS_DESC),
        "phon": stats_table(ps.get_stats(), PHON_STATS_DESC),
        "verse": verse_table,
        "verse_lines": verse_lines,
        "basic": stats_table(basic, BASIC_STATS_DESC),
        "keywords": keywords_table(forms),
        "collocations": collocations_table(lemmas),
        "zipf": zipf_image(lemmas) if enough_words else None,
        "enough_words": enough_words,
        "sentences": sentences_image(doc) if enough_sents else None,
        "enough_sents": enough_sents,
    }


def analyze(text: str, *groups: list[str]):
    try:
        result = compute(text, [layer for group in groups for layer in group])
    except ValueError as error:
        raise gr.Error(str(error)) from error
    return (
        result["text"],
        result["highlight"],
        result["summary"],
        result["readability"],
        result["diversity"],
        result["pos"],
        result["morph"],
        result["markers"],
        result["syntax"],
        result["cohesion"],
        result["lexical"],
        result["style"],
        result["phon"],
        result["verse"],
        result["verse_lines"],
        result["basic"],
        result["keywords"],
        result["collocations"],
        gr.Image(value=result["zipf"], visible=result["enough_words"]),
        gr.Markdown(visible=not result["enough_words"]),
        gr.Image(value=result["sentences"], visible=result["enough_sents"]),
    )


def rerender(text: str | None, *groups: list[str]) -> str:
    if not text:
        return ""
    return render_highlight(text, [layer for group in groups for layer in group])


HEADER = """
# esTS - statistics of Spanish texts

Paste a text in Spanish and get its readability with the school stage and the age of the reader,
lexical diversity, the morphological and syntactic profile, cohesion, word frequency, the SEO
metrics of style, phonostatistics, the meter and rhyme of verse, keywords and collocations, and the
highlighting of the fragments these numbers come from.
[GitHub](https://github.com/SergeyShk/esTS) · [Documentation](https://sergeyshk.github.io/esTS/) ·
[PyPI](https://pypi.org/project/pyests/)
"""
FOOTER = (
    f"esTS {version('pyests')} · anyTS {version('anyts')} · spaCy {spacy.__version__} · "
    f"es_core_news_sm {nlp.meta['version']}"
)
CSS = """
.ests-highlight { font-size: 1.05em; }
.stats { --font-mono: var(--font); }
#text-input, #text-input > label { display: flex; flex-direction: column; }
#text-input > label, #text-input .input-container { flex: 1 1 auto; }
#text-input .input-container { align-items: stretch; }
"""

INITIAL = compute(EXAMPLES["News"], DEFAULT_LAYERS)

with gr.Blocks(title="esTS") as demo:
    gr.Markdown(HEADER)
    text_state = gr.State(INITIAL["text"])
    highlight_output = gr.HTML(
        INITIAL["highlight"], label="Highlighting", container=True, padding=True, render=False
    )
    summary_output = gr.Markdown(INITIAL["summary"], render=False)
    tables = {
        name: gr.Dataframe(INITIAL[name], interactive=False, elem_classes="stats", render=False)
        for name in (
            "readability",
            "diversity",
            "morph",
            "markers",
            "syntax",
            "cohesion",
            "lexical",
            "style",
            "phon",
            "verse",
            "basic",
            "keywords",
            "collocations",
        )
    }
    verse_lines_output = gr.Markdown(INITIAL["verse_lines"], render=False)
    pos_output = gr.BarPlot(
        INITIAL["pos"],
        x="Part of speech",
        y="Words",
        sort="-y",
        x_label_angle=-30,
        height=300,
        container=False,
        render=False,
    )
    zipf_output = gr.Image(
        INITIAL["zipf"],
        label="Zipf's law",
        show_label=False,
        interactive=False,
        visible=INITIAL["enough_words"],
        render=False,
    )
    zipf_note = gr.Markdown(
        f"*The plot of Zipf's law is drawn for texts of {ZIPF_MIN_WORDS} words and more.*",
        visible=not INITIAL["enough_words"],
        render=False,
    )
    sentences_output = gr.Image(
        INITIAL["sentences"],
        label="Sentence lengths",
        show_label=False,
        interactive=False,
        visible=INITIAL["enough_sents"],
        render=False,
    )
    outputs = [
        text_state,
        highlight_output,
        summary_output,
        tables["readability"],
        tables["diversity"],
        pos_output,
        tables["morph"],
        tables["markers"],
        tables["syntax"],
        tables["cohesion"],
        tables["lexical"],
        tables["style"],
        tables["phon"],
        tables["verse"],
        verse_lines_output,
        tables["basic"],
        tables["keywords"],
        tables["collocations"],
        zipf_output,
        zipf_note,
        sentences_output,
    ]

    with gr.Row(equal_height=True):
        with gr.Column(scale=3):
            text_input = gr.Textbox(
                INITIAL["text"],
                lines=9,
                max_lines=9,
                max_length=MAX_CHARS,
                label="Text",
                elem_id="text-input",
                placeholder=f"Paste a text in Spanish, up to {MAX_CHARS:,} characters",
            )
        with gr.Column(scale=1):
            layer_inputs = [
                gr.CheckboxGroup(
                    choices=[(HIGHLIGHT_LAYERS_DESC[layer], layer) for layer in group],
                    value=[layer for layer in group if layer in HIGHLIGHT_DEFAULT_LAYERS],
                    label=f"Highlighting: {name.lower()}",
                )
                for name, group in HIGHLIGHT_LAYER_GROUPS.items()
            ]
            analyze_button = gr.Button("Analyze", variant="primary")
    gr.Examples(
        examples=[[text, *DEFAULT_GROUP_LAYERS] for text in EXAMPLES.values()],
        example_labels=list(EXAMPLES),
        inputs=[text_input, *layer_inputs],
        outputs=outputs,
        fn=analyze,
        run_on_click=True,
        cache_examples=False,
        label="Examples",
    )
    with gr.Row():
        with gr.Column():
            highlight_output.render()
            zipf_output.render()
            zipf_note.render()
            sentences_output.render()
        with gr.Column():
            summary_output.render()
            with gr.Tabs():
                with gr.Tab("Readability"):
                    tables["readability"].render()
                with gr.Tab("Diversity"):
                    tables["diversity"].render()
                with gr.Tab("Morphology"):
                    pos_output.render()
                    tables["morph"].render()
                    tables["markers"].render()
                with gr.Tab("Syntax"):
                    tables["syntax"].render()
                with gr.Tab("Cohesion"):
                    tables["cohesion"].render()
                with gr.Tab("Frequency"):
                    tables["lexical"].render()
                with gr.Tab("Style"):
                    tables["style"].render()
                with gr.Tab("Phonics"):
                    tables["phon"].render()
                with gr.Tab("Verse"):
                    gr.Markdown(VERSE_NOTE)
                    tables["verse"].render()
                    verse_lines_output.render()
                with gr.Tab("Basic"):
                    tables["basic"].render()
                with gr.Tab("Keywords"):
                    gr.Markdown(KEYWORDS_NOTE)
                    tables["keywords"].render()
                    tables["collocations"].render()
    gr.Markdown(FOOTER)

    analyze_button.click(analyze, inputs=[text_input, *layer_inputs], outputs=outputs)
    text_input.submit(analyze, inputs=[text_input, *layer_inputs], outputs=outputs)
    for layer_input in layer_inputs:
        layer_input.change(
            rerender, inputs=[text_state, *layer_inputs], outputs=[highlight_output]
        )

if __name__ == "__main__":
    demo.launch(css=CSS)
