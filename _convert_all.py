# -*- coding: utf-8 -*-
"""Convert all distinct study works (.docx) into Jupyter-Book folders under works/.
Skips templates, reading lists and duplicate draft versions.
"""
import os, subprocess, sys

BASE = r"D:\PROTON-DRIVE LOCAL\Other computers\DESKTOP-F64DS1Q\OneDrive - Afondo Consulting GmbH\BOOKS\Personal Writing - UNI - Eigene Texte"

# (relpath, slug, title)
WORKS = [
    ("091012-Essay01_Vishnu_JonasH.docx", "vishnu-essay", "Vishnu"),
    ("Arbeit_Kittler_Nietzsche.docx", "kittler-nietzsche", "Kittler & Nietzsche"),
    ("Diplomarbeiten\\Jonas_Hässig_BA-Arbeit_Biotech.docx", "ba-biotech", "BA-Arbeit: Biotech"),
    ("Eine konkrete Utopie für eine bessere Welt.docx", "konkrete-utopie", "Eine konkrete Utopie für eine bessere Welt"),
    ("Essay_Goethe_Jonas_H.docx", "goethe-essay", "Goethe"),
    ("Essay_Nietzsche_Krieg_und_Frieden.docx", "nietzsche-krieg-frieden", "Nietzsche: Krieg und Frieden"),
    ("Essay_Nietzsche1.docx", "nietzsche-essay1", "Nietzsche (Essay)"),
    ("Essay_Schopenhauer_J-Hässig.docx", "schopenhauer-essay", "Schopenhauer"),
    ("Essay_Soziologie-der-Universität.docx", "soziologie-universitaet", "Soziologie der Universität"),
    ("Handout_Carlo-Ginzburg.docx", "handout-ginzburg", "Handout: Carlo Ginzburg"),
    ("Handout_Lewitscharoff.docx", "handout-lewitscharoff", "Handout: Lewitscharoff"),
    ("Handout-Luhmann1996.docx", "handout-luhmann", "Handout: Luhmann 1996"),
    ("J.H._Arbeit_Goffman_Streit.docx", "goffman-streit", "Arbeit: Goffman, Streit"),
    ("JH_Protokoll_Freud.docx", "protokoll-freud", "Protokoll: Freud"),
    ("JH_Seminararbeit_Nietzsche.docx", "seminararbeit-nietzsche", "Seminararbeit: Nietzsche"),
    ("Jonas_Haessig-Essay01-JohnRawls.docx", "rawls-essay", "Essay: John Rawls"),
    ("Jonas_Hässig_Essay_Bioethik_Crispr.docx", "bioethik-crispr", "Bioethik & CRISPR"),
    ("Jonas_Hässig_Essay_Wissenschaft_Wunderbar.docx", "wissenschaft-wunderbar", "Wissenschaft, wunderbar"),
    ("Jonas_Hässig_Protokoll_Koevolutionstheorie.docx", "protokoll-koevolution", "Protokoll: Koevolutionstheorie"),
    ("Jonas_Hässig_Protokoll_Phil_Techne_2.docx", "protokoll-phil-techne", "Protokoll: Philosophie & Techne"),
    ("Jonas_Hässig_religious_turn_essay_1.docx", "religious-turn-essay", "Essay: Religious Turn"),
    ("Legende (Nietz-Trans-Umanismüs)\\Lektüreessay_Nietzsche_JH.docx", "lektuereessay-nietzsche", "Lektüreessay: Nietzsche"),
    ("Legende (Nietz-Trans-Umanismüs)\\Lektüreessay_Transhumanismus_versFinal1.docx", "lektuereessay-transhumanismus", "Lektüreessay: Transhumanismus"),
    ("Protokoll_Digital_Humanities.docx", "protokoll-digital-humanities", "Protokoll: Digital Humanities"),
    ("Protokoll_Kolloquium_WissForsch2017_JH.docx", "protokoll-wissforsch-2017", "Protokoll: Kolloquium Wissenschaftsforschung"),
    ("Protokoll_Machiavelli.docx", "protokoll-machiavelli", "Protokoll: Machiavelli"),
    ("Protokoll_Neue_Formen_der_Verwandtschaft.docx", "protokoll-verwandtschaft", "Protokoll: Neue Formen der Verwandtschaft"),
    ("Protokoll_Nietzsche.docx", "protokoll-nietzsche", "Protokoll: Nietzsche"),
    ("PS_Arbeit_HS12_SozialeInnovation.docx", "soziale-innovation", "Arbeit: Soziale Innovation"),
    ("Turing_Gödel_JH.docx", "turing-goedel", "Turing & Gödel"),
    ("ZGW_Kolloqu_Klassenwissen_JH.docx", "klassenwissen", "Kolloquium: Klassenwissen"),
]

def main():
    ok, missing, fail = [], [], []
    for rel, slug, title in WORKS:
        path = os.path.join(BASE, rel)
        if not os.path.exists(path):
            missing.append(slug)
            continue
        out = os.path.join("works", slug)
        if os.path.isdir(out):
            print("skip (exists):", slug)
            continue
        r = subprocess.run([sys.executable, "_docx_to_book.py", path, slug, title],
                           capture_output=True, text=True)
        if r.returncode == 0:
            ok.append(slug)
            print("ok:", slug)
        else:
            fail.append((slug, r.stderr[-200:]))
            print("FAIL:", slug, r.stderr[-120:].replace("\n", " "))
    print("\nconverted:", len(ok), "| missing:", missing, "| fail:", fail)


if __name__ == "__main__":
    main()
