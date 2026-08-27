# -*- coding: utf-8 -*-
"""Reorganise the_book_2.73.md into thematic chapters with a table of contents.

Keeps every unique passage verbatim (no rewriting). Removes Facebook/web UI
artefacts and exact duplicate passages. Groups passages under curated themes.
Writes a NEW file; the source is left untouched.
"""
import re, unicodedata, os, urllib.parse

SRC = "the_book_2.73.md"
OUT = "the_book_2.73_strukturiert.md"

def norm(s: str) -> str:
    """Normalise a string for duplicate detection."""
    s = s.lower()
    s = re.sub(r"https?://\S+", "", s)          # strip urls
    s = re.sub(r"[^\w\s]", " ", s)              # strip punctuation
    s = re.sub(r"\s+", " ", s).strip()
    return s

# Canonical chapter headings.
KUNST = "Kunst, Kultur & Poesie"
SPIRIT = "Spiritualität, Anthroposophie & Übersinnliches"
BEWUSST = "Bewusstsein, Psyche & der Mensch"
TECH = "Technologie, KI & die digitale Welt"
GESELL = "Gesellschaft, Politik & Macht"
NATUR = "Natur, Tiere & die Erde"
BIBLIO = "Die lebendige Bibliothek · Das Wissens- & Archivprojekt"
ASTRO = "Astrologie & die Sterne"
VERMISCHT = "Vermischtes & Weiteres"
FRAGMENT = "Fragmente & Aphorismen"
FALLBACK = "Vermischtes & Weiteres"
FB_COLLECTION = "Facebook-Posts & Chronik"

# Long verbatim quotes that were split into single lines by blank-line separators
# in the source.  Each entry: (0-based start line, 0-based end line, heading).
# Content lines inside the range are joined back into one block; the block is
# placed in its canonical chapter.
QUOTE_BLOCKS = [
    (1122, 1168, KUNST),    # Chaplin, "The Great Dictator" closing speech (src 1123-1169)
    (1090, 1112, TECH),     # Essay 2016: Virtual / Augmented Reality (src 1091-1113)
    (1056, 1074, SPIRIT),   # Kilindi Iyi, "We are alone in the Dark" (src 1057-1075)
]

# Manual reassignment: distinctive substring -> canonical chapter.  Checked before
# keyword classification, so it overrides the heuristic for clearly-misfit passages.
OVERRIDES = [
    # --- out of Astrologie ---
    ("yes AGI's are all over youtube", TECH),
    ("in evil I see happenings that are themselves", SPIRIT),
    ("cybaspace is on fyya", TECH),
    ("Isn't it clear that Self--Knowledge is ultimately neutral", BEWUSST),
    ("religion, how it was concieved during the age of pisces", SPIRIT),
    ("heaven do have a ghetto", SPIRIT),
    # --- out of Technologie ---
    ("it is a materialistic and wrong perception that there would be something like a singular godly being", SPIRIT),
    ("I felt guilty too when I skipped ahead a couple of pages", SPIRIT),
    ("Hard Facts in Religion are called Dogma", SPIRIT),
    ("real hand crafted art is in any case unique", KUNST),
    ("if you imagine the mind like a supercomputer", BEWUSST),
    ("gladiator II is a pretty significant movie", KUNST),
    ("we're literally experiencing reciprocal creation", SPIRIT),
    ("Many thanks for all these birthday wishes", VERMISCHT),
    ("It's as if the soul is using the mind", BEWUSST),
    ("By producing an accurate 'enough', self healing", BEWUSST),
    ("A 'false' version of the piece of the pie", BEWUSST),
    ("if you want to see somethin' very disturbing", GESELL),
    ("The metaverse (meta in greek means death)", GESELL),
    ("the fb insta .com bubble 8th sphere", GESELL),
    ("just to make some things clear - i like computers", TECH),
    # --- out of Gesellschaft ---
    ("if some people would know the facts they wouldn't even question", SPIRIT),
    ("there exist understandings of a true union of individuals", SPIRIT),
    ("control-non control is not a dualism in the usual sense", BEWUSST),
    ("it can already be seen how many of these routes are being travelled", SPIRIT),
    ("it's actually healthy for the body when the heart-mind-spirit connection", SPIRIT),
    ("Once this is produced, a sheer image from a glance at the larger reality", BEWUSST),
    ("Instead of allowing the shadows to grow imbalanced", BEWUSST),
    ("morals, ethics, discernment are the spheres of righteous actions", BEWUSST),
    ("our relationship to animals is one of having incorporated all species", NATUR),
    ("The aeroplane and the radio have brought us closer together", KUNST),
    ("The misery that is now upon us is but the passing of greed", KUNST),
    ("You the people have the power", KUNST),
    # --- out of Natur ---
    ("this web would then serve as neutral informational", BIBLIO),
    ("perspectivism in philosophy alone", BEWUSST),
    ("I have never seen a physical being ever that is sober", SPIRIT),
    ("people are asking what 'egotistical' means", BEWUSST),
    ("all of the most brilliant minds Ive known have been talking about a metamorphosis", SPIRIT),
    ("there is a great grand freeing balance to be found in coming to see the current bodily instruments", SPIRIT),
    ("tolkien did transcribe a real place in the spirit world", SPIRIT),
    ("Ima repeat it once again: inside the true and genuine spiritual movements", SPIRIT),
    ("Just as not achieving full self potential", BEWUSST),
    ("This is part of the basis of the understanding of the true nature of the self", BEWUSST),
    ("the subparticle in esotericism is the lower astral", SPIRIT),
    ("some of the talked about 'dead' are able to reach trough", SPIRIT),
    # --- out of Kunst ---
    ("there are true understandings of the christian mysterys", SPIRIT),
    ("my inner vibe is literally like an unsuspecting autistic child", BEWUSST),
    ("I guess some peoples reasoning is just more", BEWUSST),
    ("clairvoyant insight means entering divine imagination", SPIRIT),
    ("where he's at at the university everything seems to be calm", VERMISCHT),
    ("Sometimes DJ'ing and communicating with peeps between death", SPIRIT),
    ("i.e. when I mention cg jung, there is direct access", BEWUSST),
    ("Im mostly coming from an anti-authoriterian", VERMISCHT),
    ("If one writes an improper reality and code", BEWUSST),
    ("That's not the destruction of reality", BEWUSST),
    # --- out of Bewusstsein ---
    ("in spiritual sciene the question of karma", SPIRIT),
    ("the knowledge of karma has also been lost", SPIRIT),
    ("I've been a student in philosophy and histroy of science", SPIRIT),
    ("concerning my remarks yesterday: so many people are starting to have insights into the spiritual world", SPIRIT),
    ("a psychedelic break trough experience", SPIRIT),
    ("The soul of man has been given wings", KUNST),
    # --- short fragments ---
    ("still. there's something to think about here", FRAGMENT),
    ("populism supporters: ", FRAGMENT),
    ("Im fully aware that some philosophers would call this relativism", FRAGMENT),
]

# Curated reading list, appended to the "Fragmente & Aphorismen" chapter.  Grounded
# in the references and themes that already appear in the source text.
LITERATURE_TIPS = [
    ("Rudolf Steiner", "Die Philosophie der Freiheit",
     "Das Kernwerk zum freien, selbstbestimmten Denken — Grundlage vieler Aphorismen über Freiheit, Denken und höhere Logik."),
    ("Rudolf Steiner", "Wie erlangt man Erkenntnisse der höheren Welten?",
     "Der methodische Initiationsweg zur übersinnlichen Wahrnehmung, der hier immer wieder anklingt."),
    ("Rudolf Steiner", "Die Geheimwissenschaft im Umriss",
     "Im Text ausdrücklich erwähnt; die verständliche Einführung in die übersinnliche Forschung."),
    ("Rudolf Steiner", "Die Kernpunkte der sozialen Frage",
     "Zur Dreigliederung des sozialen Organismus — ein zentrales Thema der Texte."),
    ("Johann Wolfgang von Goethe", "Faust (Erster Teil)",
     "Vom Autor ausdrücklich empfohlen: über Mephisto, Erkenntnis und die Kräfte Luzifer/Ahriman."),
    ("Mabel Collins", "Light on the Path",
     "Im Text genannt, von Steiner kommentiert — ein klassischer Initiationstext."),
    ("Carl Gustav Jung", "Erinnerungen, Träume, Gedanken",
     "Einstieg in Ego, Selbst und Psyche; der Autor verweist explizit auf Jung."),
    ("Carl Gustav Jung", "Aion",
     "Über das Selbst und die Wandlung des Christusbildes — passt zu den Auferstehungs- und Ich-Aphorismen."),
    ("Gary Goldschneider", "The Secret Language of Birthdays",
     "Personologie/Astrologie, im Text empfohlen."),
    ("Helena P. Blavatsky", "Die geheime Lehre (The Secret Doctrine)",
     "Die theosophische Grundlage für Geheimwissen, Monismus und die Lehre von den Äonen."),
    ("Nisargadatta Maharaj", "I Am That",
     "Zur Non-Dualität und dem „I AM“, das in mehreren Aphorismen aufscheint."),
]

# For the interactive-book file: passages pulled out of the themed chapters into
# dedicated "Autor:in" and "Notizen" sections (each appears once).
AUTOR_KEYS = [
    "my name is jonas", "nice to meet you", "kind regards,",
    "my inner vibe is literally like an unsuspecting autistic child",
    "oh and ps - Ive been actively feeling myself protected by my guardian angel",
    "my mode operandi has been pretty hermitty for some years",
    "for any inquerys please contact me thru", "jonason@protonmail.ch",
    "after all, I appreaciate most of the work that all these readers have been doing",
    "there yu have my daily blog. happy weekfrends",
    "Im mostly coming from an anti-authoriterian",
    "I do hope to meet up with people that I got to know over cyberspace in person",
    "so sending you so much love and hope to see you soon",
    "I've been a student in philosophy and histroy of science",
    "Im a guy and Im a virgo", "other than that, Im rather rebellious when it comes to labeling",
    "its a strange world",
]
NOTIZEN_KEYS = [
    "these here below are just my monologue ramblings",
    "non-nativ english speakers dont take english as literal",
    "this message will be missunderstood in so many ways",
    "I'm nowhere claiming any poetical justice",
    "just my two cents", "maybe this post inspires someone",
    "I will be uploading talks and written digital documents",
    "don't worry if I'm on and off off here like a maniac",
    "stay grounded stay funky stay blessed",
    "and remember, opinions are like assholes",
    "this is a fun read of a fun 9th september kid yo",
    "after Ive written a classical text about it",
    "curating nd editing these fb collects nd shares is going thru note born of many moments",
    "I would like to share a Substack-Post of a cyberfriend called Aug Tells",
    "Im just here because some threads to the americas",
]

# Curated glossary for the "Lexikon" layer (term -> one-line gloss).
LEXIKON = [
    ("Anthroposophie", "Von Rudolf Steiner begründete Geisteswissenschaft, die übersinnliche Erkenntnis methodisch erforschbar machen will."),
    ("Ahriman", "In der Anthroposophie die der Verhärtung, Mechanisierung und Kälte zugeneigte Gegenmacht; mit KI und Materialismus verknüpft."),
    ("Luzifer", "Die der Verführung, Illusion und Überschwinglichkeit zugeneigte Gegenmacht; Gegenpol zu Ahriman."),
    ("Mysterium von Golgatha", "Steiners Bezeichnung für das Christus-Ereignis als Überwindung von Tod und Stofflichkeit."),
    ("Karma", "Die übersinnliche Verkettung von Handlung und Schicksal über Inkarnationen hinweg — nicht als mechanische Vergeltung zu verstehen."),
    ("Monismus / Non-Dualität", "Die Sicht, dass Geist und Welt nicht getrennt sind; im Text oft als „oneness“ oder „das I AM“."),
    ("Personologie", "Astrologisches Persönlichkeitssystem von Gary Goldschneider, hier mehrfach empfohlen."),
    ("Theosophie", "Esoterische Bewegung des 19. Jh. (Blavatsky), die östliche und westliche Weisheit zu vereinen suchte."),
    ("Übersinnliche Wahrnehmung", "„Clairvoyance“ — das Erkennen jenseits der Sinneserfahrung, im Text auch „divine imagination“."),
    ("Christus-Impuls / Ich-Impuls", "Der im Text zentrale Gedanke der Entwicklung vom ego zum höheren Selbst (I AM)."),
    ("Dreigliederung des sozialen Organismus", "Steiners Modell einer Gesellschaft aus Geistesleben, Rechtsleben und Wirtschaftsleben."),
    ("Die Große Diktator-Rede", "Chaplins Schlussrede aus „The Great Dictator“ — im Text als Aufruf zu Menschlichkeit zitiert."),
]

# Notable sources/references named in the text, for the "Referenzen & Quellen" layer.
REFERENCE_SOURCES = [
    ("Rudolf-Steiner-Archiv (GA)", "Digitales Archiv von Steiners Schriften und Vorträgen; im Text als frei verfügbar genannt."),
    ("academia.edu", "Wissenschaftliche Plattform, auf die im Text mehrfach verwiesen wird."),
    ("Baba Kilindi (BTR-Serie)", "Lehren über Quantencomputer, KI und übersinnliches Wissen — mehrfach bezogen."),
    ("Fehmi Krasniqi", "Forschung zu Pyramiden- und Bautechnik; im Text als Anregung genannt."),
    ("Gary Goldschneider", "Autor der Personology-Bücher; astrologische Persönlichkeitstypologie."),
    ("Mabel Collins, „Light on the Path“", "Initiationstext, von Steiner kommentiert."),
]

def clean_urls(t: str) -> str:
    """Unwrap / remove Facebook redirect and tracking URLs from a passage."""
    def _dec(m):
        u = urllib.parse.unquote(m.group(1))
        u = re.sub(r"[?&](fbclid|__tn__|__cft__|_rdr|c\[0\]|h|fref)[^&]*", "", u)
        u = re.sub(r"&+$", "", u).rstrip("?&")
        return u if u.startswith("http") else ""
    # [label](https://l.facebook.com/l.php?u=...) -> the real target
    t = re.sub(r"\[[^\]]*\]\(\s*https?://l\.facebook\.com/l\.php\?u=([^&\s\)]+)[^)\s]*\s*\)", _dec, t)
    # bare facebook redirect -> the real target
    t = re.sub(r"https?://l\.facebook\.com/l\.php\?u=([^&\s)]+)", _dec, t)
    # [label](https://www.facebook.com/...) -> keep the label, drop the link
    t = re.sub(r"\[([^\]]*)\]\(\s*https?://(?:www\.)?facebook\.com/[^)\s]*\s*\)", r"\1", t)
    # remaining bare facebook / redirect urls -> drop
    t = re.sub(r"https?://(?:www\.)?facebook\.com/[^\s)\]]*", "", t)
    t = re.sub(r"https?://l\.facebook\.com/[^\s)\]]*", "", t)
    t = re.sub(r"[ \t]{2,}", " ", t).strip()
    return t

def read_paras(path: str):
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    excluded = set()
    quote_blocks = []           # (heading, text)
    for start, end, heading in QUOTE_BLOCKS:
        block = []
        for i in range(start, end + 1):
            excluded.add(i)
            if i < len(lines):
                t = lines[i].strip()
                if t:
                    block.append(t)
        text = " ".join(block)
        text = re.sub(r"[ \t]{2,}", " ", text).strip()
        if text:
            quote_blocks.append((heading, text))

    remaining = [lines[i] for i in range(len(lines)) if i not in excluded]
    text = "\n".join(remaining)
    raw = re.split(r"\n\s*\n", text)
    paras = []
    for p in raw:
        p = p.strip()
        # collapse internal single newlines to spaces (keep as one block)
        p = re.sub(r"[ \t]*\n[ \t]*", " ", p)
        p = re.sub(r"[ \t]{2,}", " ", p).strip()
        # skip empty / stray separator / UI noise
        if not p:
            continue
        if p in {"·", ".", "…", "Weniger anzeigen", "LINK TAKEN DOWN.",
                 "academia.edu", "www.academia.edu"}:
            continue
        if re.fullmatch(r"[-–—\s]{1,6}", p):
            continue
        # skip pure hyperlink references and bare fb/useless hashtag urls
        if re.fullmatch(r"\[.+?\]\(https?://[^\s]+\)", p) or re.fullmatch(r"https?://\S+", p):
            continue
        p = clean_urls(p)
        if not p.strip():
            continue
        paras.append(p)

    # Facebook posts: keep as their own collection (not mixed into themes)
    fb_posts = []
    fb_file = os.path.join(os.path.dirname(os.path.abspath(path)), "facebook_posts.md")
    if os.path.exists(fb_file):
        with open(fb_file, encoding="utf-8") as fh:
            fb = fh.read()
        for p in re.split(r"\n\s*\n", fb):
            p = p.strip()
            p = re.sub(r"[ \t]*\n[ \t]*", " ", p)
            p = re.sub(r"[ \t]{2,}", " ", p).strip()
            if not p:
                continue
            p = clean_urls(p)
            if p.strip():
                fb_posts.append(p)

    return paras, quote_blocks, fb_posts

# ----------------------------------------------------------------------------
# Theme keyword map.  Order matters: more specific / distinctive themes first so
# broad terms in later themes don't steal from them.  Matching is word-boundary
# aware for short tokens.  Each theme: (heading, [keywords]).
# ----------------------------------------------------------------------------
THEMES = [
    ("Astrologie & die Sterne", [
        "astrolog", "virgo", "pisces", "aquarius", "scorpio", "constellation",
        "goldschneider", "personology", "ascendant", "zodiac", "horoscope",
        "astro", "jupiter", "saturn", "mercury", "sun sign",
    ]),
    ("Die lebendige Bibliothek · Das Wissens- & Archivprojekt", [
        "library", "bibliothek", "archivist", "archives", "librarian",
        "information science", "knowledge repository", "selftransforming",
        "knowledge management", "academic reference", "provenance",
        "open access", "original document", "participatory", "gutenberg",
        "metadata", "data steward", "catalog", "koha", "evergreen", "zotero",
        "europeana", "archive", "archiving",
    ]),
    ("Technologie, KI & die digitale Welt", [
        "artificial intelligence", "llm", "large language", "generative", "chatgpt",
        "algorithm", "computer", "computing", "cyber", "robot", "android",
        "turing", "singularity", "automation", "datacenter", "metaverse",
        "social media", "facebook", "instagram", "threads", "youtub", "tiktok",
        "avatar", "slop", "cyberspace", "hyperspace", "blockchain", "encrypt",
        "software", "device", "technolog", "digital", "internet", "ai",
    ]),
    ("Gesellschaft, Politik & Macht", [
        "politics", "politic", "government", "capitalism", "capitalist", "monopol",
        "corporate", "propaganda", "manipul", "group mind", "collective",
        "racism", "racist", "neocolonial", "colonial", "afrofuturism",
        "war of all against all", "post-atlantean", "econom", "economic",
        "population control", "thought police", "anarchist", "fascist", "nazi",
        "inauguration", "dictator", "democracy", "democratic", "tyranny",
        "revolution", "geopolit", "oligarch", "establishment", "system",
    ]),
    ("Natur, Tiere & die Erde", [
        "animal", "nature", "earth", "tree", "plant", "concrete", "archaeolog",
        "archeol", "pyramid", "khemet", "egypt", "chaga", "climate", "species",
        "beast", "garden", "river", "swim", "organic", "mushroom", "fungi",
        "air", "forest", "soil", "water", "minerals", "healing", "health",
    ]),
    ("Kunst, Kultur & Poesie", [
        "artist", "art", "aura", "music", "song", "poetry", "poet", "romantic",
        "tolkien", "faust", "goethe", "book", "movie", "film", "gladiator",
        "chaplin", "speech", "novel", "painter", "architect", "theatre",
        "theater", "comic", "sculpt", "literary", "writing", "author", "creative",
        "imagination", "narrat", "dj",
    ]),
    ("Bewusstsein, Psyche & der Mensch", [
        "jung", "psyche", "psycholog", "ego", "consciousness", "unconscious",
        "anima", "animus", "non-self", "self-knowledge", "personality", "mind",
        "meditat", "awareness", "perception", "ego death", "soul", "spirit soul",
        "consciousness soul", "default mode", "neutralit", "perspectiv",
        "relativism", "philosoph", "epistemolog", "dualist", "trinity",
        "dichotom", "introvert", "extrovert",
    ]),
    ("Spiritualität, Anthroposophie & Übersinnliches", [
        "steiner", "anthroposoph", "spiritual science", "spiritual-scientific",
        "spiritual world", "spiritual realm", "karma", "clairvoy", "golgatha",
        "michael", "ahriman", "lucifer", "etheric", "elemental", "supersensible",
        "spirit world", "life between death", "reincarnat", "goetheanum",
        "occult", "esoteric", "gnosis", "divine imagination", "light on the path",
        "mystery", "myster", "sacred", "christ", "christed", "angel", "angelic",
        "guardian angel", "buddha", "maya", "babylon", "monism", "non-dual",
        "oneness", "anthropos", "kilindi", "astral", "subparticle", "initiat",
        "ether", "higher world", "spiritual being", "spiritual truth",
        "spiritual growth", "spiritual movement", "spiritual",
    ]),
]

FALLBACK = "Vermischtes & Weiteres"
FRAGMENT = "Fragmente & Aphorismen"

def classify(p: str) -> str:
    low = p.lower()
    # manual overrides win (case-insensitive)
    for key, heading in OVERRIDES:
        if key.lower() in low:
            return heading
    for heading, kws in THEMES:
        for kw in kws:
            k = kw.strip()
            if not k:
                continue
            if len(k) <= 5:
                # word-boundary match for short tokens
                if re.search(r"(?<![a-z])" + re.escape(k) + r"(?![a-z])", low):
                    return heading
            else:
                if k in low:
                    return heading
    return FALLBACK

def slugify(s: str) -> str:
    s = s.lower()
    s = s.replace("&", "")
    s = s.replace("·", "")
    s = s.replace(",", "")
    s = s.replace(".", "")
    s = s.replace(":", "")
    s = s.replace("—", "-")
    s = s.replace("–", "-")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s

def build_buch(groups, order):
    """Assemble the interactive-book markdown, mirroring the concept page's
    sections and immersion modes.  Author/notizen passages are moved out of the
    themed chapters into their own sections so each text appears once."""
    g = {k: list(v) for k, v in groups.items()}
    autor, notizen = [], []
    for k in g:
        kept = []
        for p in g[k]:
            low = p.lower()
            if any(a in low for a in AUTOR_KEYS):
                autor.append(p)
            elif any(n in low for n in NOTIZEN_KEYS):
                notizen.append(p)
            else:
                kept.append(p)
        g[k] = kept

    lines = []
    lines.append("# Das Lebendige Archiv — Gedanken zur Verfassung eines ausführbaren, interaktiven Online-Buches")
    lines.append("")
    lines.append("> Eine interaktiv-buch-taugliche Gliederung, angelehnt an die Abschnitte und Eintauch-Modi der "
                 "Konzeptseite `jonason-lebendiges-archiv.html`. Die Textpassagen sind unverändert übernommen; "
                 "Autor:in-, Notizen-, Lexikon- und Quellen-Abschnitte ergänzen das Gerüst. Aus `the_book_2.73_strukturiert.md` ableitbar.")
    lines.append("")
    # main TOC
    lines.append("## Inhalt")
    lines.append("")
    lines.append("1. [Autor:in](#autorin)")
    lines.append("2. [Der Text](#der-text)")
    for i, h in enumerate(order, 1):
        lines.append(f"   - [{h}](#{slugify(f'{i}. {h}')})")
    lines.append("3. [Lexikon](#lexikon)")
    lines.append("4. [Referenzen & Quellen](#referenzen-quellen)")
    lines.append("5. [Notizen](#notizen)")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Autor:in
    lines.append("# Autor:in")
    lines.append("")
    if autor:
        for p in autor:
            lines.append(p)
            lines.append("")
    else:
        lines.append("_Hier erscheinen die Selbstbeschreibungen der Autorin/des Autors._")
        lines.append("")
    lines.append("---")
    lines.append("")

    # Der Text
    lines.append("# Der Text")
    lines.append("")
    for i, h in enumerate(order, 1):
        items = g.get(h, [])
        lines.append(f"## {i}. {h}")
        lines.append("")
        if not items:
            lines.append("_In diesem Kapitel sind aktuell keine Textstücke einsortiert._")
            lines.append("")
            continue
        for p in items:
            lines.append(p)
            lines.append("")
        lines.append("")
    lines.append("---")
    lines.append("")

    # Lexikon
    lines.append("# Lexikon")
    lines.append("")
    lines.append("> Kurzglossar zu den zentralen Begriffen des Textes. (Ideal für den Lexikon-Modus.)")
    lines.append("")
    for term, gloss in LEXIKON:
        lines.append(f"- **{term}**: {gloss}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Referenzen & Quellen
    lines.append("# Referenzen & Quellen")
    lines.append("")
    lines.append("> Genannte Quellen und Anknüpfungspunkte sowie weiterführende Literatur.")
    lines.append("")
    lines.append("**Im Text genannte Quellen**")
    lines.append("")
    for name, note in REFERENCE_SOURCES:
        lines.append(f"- **{name}**: {note}")
    lines.append("")
    lines.append("**Weiterführende Literatur**")
    lines.append("")
    for author, title, note in LITERATURE_TIPS:
        lines.append(f"- **{author}** – „{title}“: {note}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Notizen
    lines.append("# Notizen")
    lines.append("")
    lines.append("> Randnotizen und Meta-Bemerkungen zum Schreiben, zum Medium und zum eigenen Zugang.")
    lines.append("")
    if notizen:
        for p in notizen:
            lines.append(p)
            lines.append("")
    else:
        lines.append("_Hier erscheinen die Notiz- und Meta-Passagen._")
    lines.append("")

    with open("the_book_2.73_buch.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("wrote the_book_2.73_buch.md bytes:", os.path.getsize("the_book_2.73_buch.md"))

def main():
    paras, quote_blocks, fb_posts = read_paras(SRC)
    print("total paragraph blocks after clean:", len(paras))

    # deduplicate (exact normalized match), keep first occurrence, original order
    seen = set()
    unique = []
    for p in paras:
        n = norm(p)
        if n in seen:
            continue
        seen.add(n)
        unique.append(p)
    print("unique blocks after de-dup:", len(unique))

    # group by theme, preserve original relative order inside each theme;
    # very short aphoristic one-liners go to their own chapter
    groups = {}
    # reconstructed long quotes go straight to their canonical chapter (first)
    for heading, text in quote_blocks:
        groups.setdefault(heading, []).append(text)
    for p in unique:
        words = p.split()
        if len(words) <= 12:
            groups.setdefault(FRAGMENT, []).append(p)
        else:
            g = classify(p)
            groups.setdefault(g, []).append(p)

    # Facebook posts as their own collection
    if fb_posts:
        seen_fb, fb_clean = set(), []
        for p in fb_posts:
            n = norm(p)
            if n in seen_fb:
                continue
            seen_fb.add(n)
            fb_clean.append(p)
        groups[FB_COLLECTION] = fb_clean

    # build output
    lines = []
    lines.append("# Das Lebendige Archiv — Gedanken zur Verfassung eines ausführbaren, interaktiven Online-Buches")
    lines.append("")
    lines.append("> Strukturierte Ausgabe von `the_book_2.73.md` — jedes einzigartige Textstück ist unverändert "
                 "übernommen, die ursprüngliche Reihenfolge innerhalb eines Kapitels bleibt erhalten. Entfernt wurden "
                 "offensichtliche Duplikate und UI-Artefakte; drei wörtliche Langzitate (Chaplins „Great Dictator“-Rede, "
                 "der Essay über Virtual/Augmented Reality von 2016, Kilindi Iyis „We are alone in the Dark“) wurden "
                 "aus ihren Einzelzeilen wieder zu zusammenhängenden Blöcken zusammengesetzt. Die Zuordnung zu Kapiteln "
                 "wurde kuratiert und nachgeschärft, ist aber als Gliederung zur Weiterbearbeitung gedacht. "
                 "Die Originaldatei wurde nicht verändert.")
    lines.append("")
    # table of contents (in THEMES order, then fallback)
    order = [t[0] for t in THEMES] + [FALLBACK, FB_COLLECTION, FRAGMENT]
    lines.append("## Inhalt")
    lines.append("")
    for i, h in enumerate(order, 1):
        cnt = len(groups.get(h, []))
        head = f"{i}. {h}"
        anchor = slugify(head)
        lines.append(f"{i}. [{h}](#{anchor}) — *{cnt} Textstücke*")
    lines.append("")
    lines.append("---")
    lines.append("")

    for i, h in enumerate(order, 1):
        items = groups.get(h, [])
        lines.append(f"# {i}. {h}")
        lines.append("")
        if not items:
            lines.append("_In diesem Kapitel sind aktuell keine Textstücke einsortiert._")
            lines.append("")
            lines.append("---")
            lines.append("")
            continue
        for p in items:
            # preserve paragraph breaks inside long passages
            lines.append(p)
            lines.append("")
        # enrich the aphorisms chapter with a curated reading list
        if h == FRAGMENT and LITERATURE_TIPS:
            lines.append("### 📚 Leseempfehlungen zu diesen Themen")
            lines.append("")
            for author, title, note in LITERATURE_TIPS:
                lines.append(f"- **{author}** – „{title}“: {note}")
            lines.append("")
        lines.append("")
        lines.append("---")
        lines.append("")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("wrote", OUT, "bytes:", os.path.getsize(OUT))
    print("chapter sizes:", {h: len(groups.get(h, [])) for h in order})
    build_buch(groups, order)

if __name__ == "__main__":
    main()
