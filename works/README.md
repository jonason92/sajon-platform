# works

Jede **akademische Arbeit** liegt als **eigenes Jupyter-Book** in einem eigenen
Unterordner:

```
works/
  <studienarbeit-slug>/
    _config.yml      # Titel, Autor, Repository
    _toc.yml         # Inhaltsverzeichnis
    <kapitel>.md     # MyST-Inhalt
```

Beispiel: `works/ethik-von-ki/`, `works/drei-gliederung/`, `works/reanimation-der-imagination/`.

Jede Arbeit wird unabhängig gebaut und taucht auf der Startseite des Lebendigen
Archivs als eigener Eintrag auf.
