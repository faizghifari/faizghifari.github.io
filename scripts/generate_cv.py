#!/usr/bin/env python3
"""
CV PDF Generator for Faiz Ghifari Haznitrama
Generates ATS-friendly PDF CVs (short 1-page and long complete) from site data.
Uses reportlab (pure Python) for PDF generation.
"""

import json
import os
import sys
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor, black
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
PAPERS_JSON = BASE_DIR / "src" / "data" / "papers.json"
OUTPUT_DIR = BASE_DIR / "public"

# ---------------------------------------------------------------------------
# Profile data (kept in sync with src/pages/about/index.astro)
# ---------------------------------------------------------------------------
PROFILE = {
    "name": "Faiz Ghifari Haznitrama",
    "title": "Ph.D. Student at UILab, KAIST",
    "email": "haznitrama@kaist.ac.kr / faiz.haznitrama@gmail.com",
    "location": "Daejeon, South Korea",
    "website": "https://faizghifari.github.io",
}

EDUCATION = [
    {
        "period": "2024 - Present",
        "degree": "Ph.D. in Computer Science",
        "institution": "Korea Advanced Institute of Science and Technology (KAIST)",
        "detail": "UILab -- Research in multilingual NLP, reasoning under uncertainty, and human-centered AI.",
    },
    {
        "period": "2021 - 2023",
        "degree": "M.Sc. in Computer Science",
        "institution": "Korea Advanced Institute of Science and Technology (KAIST)",
        "detail": "Master of Computer Science at KAIST, School of Computing.",
    },
    {
        "period": "2015 - 2019",
        "degree": "B.Sc. in Informatics",
        "institution": "Institut Teknologi Bandung (ITB)",
        "detail": "Studied computer science with a focus on artificial intelligence and natural language processing.",
    },
]

EXPERIENCE = [
    {
        "role": "Lead Researcher",
        "org": "PT. Feedloop Global Teknologi / Feedloop.ai",
        "location": "Indonesia",
        "period": "Dec 2023 - Mar 2026",
        "description": "Lead the research and development team of Feedloop. Improve the current RAG-based pipeline with an increase in performance of up to 20%. Research in making our own LLM, VLM, TTS, AutoML pipeline, and LLM-based apps.",
    },
    {
        "role": "Student Researcher",
        "org": "UILab, KAIST",
        "location": "Daejeon, South Korea",
        "period": "Feb 2024 - Present",
        "description": "Conducting research on multilingual NLP, reasoning under uncertainty, and human-centered AI. Focusing on how language models can better understand and communicate across diverse linguistic contexts.",
    },
    {
        "role": "NLP Engineer",
        "org": "PT. Prosa Solusi Cerdas / Prosa.ai",
        "location": "Indonesia",
        "period": "Sep 2019 - Aug 2021",
        "description": "Develop and maintain NLP-based applications/APIs. Conduct experiments in NLP (sentiment analysis, plagiarism detection, info extraction). Create and optimize resource-efficient pipeline for ML model in production.",
    },
    {
        "role": "Software Engineer Intern",
        "org": "E-Life Solutions Sdn. Bhd.",
        "location": "Malaysia",
        "period": "May 2018 - Aug 2018",
        "description": "Design system architecture for Smart Hospital Asset Management System (SHAMS). Develop server using Node.js, provide communication with hospital embedded devices. Build Qur'an verse search related to Indonesian text by measuring similarity.",
    },
]

SKILLS = [
    "Python", "PyTorch", "Transformers (Hugging Face)", "LLMs",
    "NLP", "Machine Translation", "Multilingual Models",
    "Research Writing", "LaTeX", "Git", "Linux",
    "Data Analysis", "Experimental Design",
]

LANGUAGES = [
    ("Indonesian", "Native"),
    ("English", "Fluent"),
    ("Korean", "Intermediate"),
]

# Full publication list from the research page (canonical source of truth)
PUBLICATIONS = [
    {
        "title": "OLA: Output Language Alignment in Code-Switched LLM Interactions",
        "authors": "Juhyun Oh, Haneul Yoo, Faiz Ghifari Haznitrama, Alice Oh",
        "venue": "ACL 2026 Main Conference",
        "year": 2026,
    },
    {
        "title": "BabyBabelLM: A Multilingual Benchmark of Developmentally Plausible Training Data",
        "authors": "Jaap Jumelet, Abdellah Fourtassi, Akari Haga, Bastian Bunzeck, Bhargav Shandilya, Diana Galvan-Sosa, Faiz Ghifari Haznitrama, et al.",
        "venue": "EACL 2026 Main Conference",
        "year": 2026,
    },
    {
        "title": "Survey of Cultural Awareness in Language Models: Text and Beyond",
        "authors": "Siddhesh Pawar, Junyeong Park, Jiho Jin, Arnav Arora, Junho Myung, Srishti Yadav, Faiz Ghifari Haznitrama, Inhwa Song, Alice Oh, Isabelle Augenstein",
        "venue": "Computational Linguistics Journal",
        "year": 2025,
    },
    {
        "title": "Methodologies and Their Comparison in Complex Compound Aspect-Based Sentiment Analysis: A Survey",
        "authors": "Faiz Ghifari Haznitrama, Ho-Jin Choi, Chin-Wan Chung",
        "venue": "AI Open",
        "year": 2025,
    },
    {
        "title": "Can LLM Generate Culturally Relevant Commonsense QA Data? Case Study in Indonesian and Sundanese",
        "authors": "Rifki Afina Putri, Faiz Ghifari Haznitrama, Dea Adhista, Alice Oh",
        "venue": "EMNLP 2024 Main Conference",
        "year": 2024,
    },
    {
        "title": "Comparative Analysis of Recent Studies on Aspect-Based Sentiment Analysis",
        "authors": "Faiz Ghifari Haznitrama, Ho-Jin Choi, Chin-Wan Chung",
        "venue": "Annual Conference of KIPS",
        "year": 2023,
    },
]

PREPRINTS = [
    {
        "title": "A Neuropsychologically Grounded Evaluation of LLM Cognitive Abilities",
        "authors": "Faiz Ghifari Haznitrama, Faeyza Rishad Ardi, Alice Oh",
        "venue": "arXiv Preprint",
        "year": 2026,
    },
    {
        "title": "Addressing Hallucination in Abstractive Dialogue Summarization via Span Identification and Correction",
        "authors": "Faiz Ghifari Haznitrama, Ho-Jin Choi, Chin-Wan Chung",
        "venue": "Master's Thesis / OpenReview",
        "year": 2023,
    },
]

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
ACCENT = HexColor("#2563eb")  # indigo-600
DARK = HexColor("#111827")    # gray-900
MID = HexColor("#4b5563")     # gray-600
LIGHT = HexColor("#6b7280")   # gray-500

STYLE_NAME = ParagraphStyle(
    "Name",
    fontName="Helvetica-Bold",
    fontSize=22,
    leading=26,
    textColor=DARK,
    alignment=TA_CENTER,
    spaceAfter=2,
)

STYLE_CONTACT = ParagraphStyle(
    "Contact",
    fontName="Helvetica",
    fontSize=9,
    leading=13,
    textColor=MID,
    alignment=TA_CENTER,
    spaceAfter=4,
)

STYLE_SECTION = ParagraphStyle(
    "Section",
    fontName="Helvetica-Bold",
    fontSize=12,
    leading=15,
    textColor=DARK,
    spaceBefore=8,
    spaceAfter=3,
)

STYLE_SUBSECTION = ParagraphStyle(
    "Subsection",
    fontName="Helvetica-Bold",
    fontSize=10,
    leading=13,
    textColor=DARK,
    spaceBefore=4,
    spaceAfter=1,
)

STYLE_BODY = ParagraphStyle(
    "Body",
    fontName="Helvetica",
    fontSize=9,
    leading=12,
    textColor=DARK,
    spaceAfter=2,
)

STYLE_BODY_INDENT = ParagraphStyle(
    "BodyIndent",
    fontName="Helvetica",
    fontSize=9,
    leading=12,
    textColor=DARK,
    leftIndent=18,
    spaceAfter=2,
)

STYLE_PUB_TITLE = ParagraphStyle(
    "PubTitle",
    fontName="Helvetica-Bold",
    fontSize=9,
    leading=12,
    textColor=DARK,
    leftIndent=18,
    spaceAfter=0,
)

STYLE_PUB_AUTHORS = ParagraphStyle(
    "PubAuthors",
    fontName="Helvetica",
    fontSize=9,
    leading=12,
    textColor=MID,
    leftIndent=18,
    spaceAfter=0,
)

STYLE_PUB_VENUE = ParagraphStyle(
    "PubVenue",
    fontName="Helvetica-Oblique",
    fontSize=9,
    leading=12,
    textColor=MID,
    leftIndent=18,
    spaceAfter=4,
)

STYLE_COMPACT = ParagraphStyle(
    "Compact",
    fontName="Helvetica",
    fontSize=8.5,
    leading=11,
    textColor=DARK,
    spaceAfter=1,
)

STYLE_COMPACT_INDENT = ParagraphStyle(
    "CompactIndent",
    fontName="Helvetica",
    fontSize=8.5,
    leading=11,
    textColor=DARK,
    leftIndent=18,
    spaceAfter=1,
)

HR = HRFlowable(width="100%", thickness=0.5, color=HexColor("#d1d5db"), spaceBefore=2, spaceAfter=4)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def section_header(text: str) -> list:
    return [Paragraph(text, STYLE_SECTION), HR]

def contact_line() -> Paragraph:
    parts = [
        PROFILE["email"],
        " | ",
        PROFILE["location"],
        " | ",
        PROFILE["website"],
    ]
    return Paragraph("".join(parts), STYLE_CONTACT)


def build_short_cv(story: list):
    """Build the 1-page short CV."""

    # Header
    story.append(Paragraph(PROFILE["name"], STYLE_NAME))
    story.append(Paragraph(PROFILE["title"], STYLE_CONTACT))
    story.append(contact_line())
    story.append(Spacer(1, 6))

    # Education
    story.extend(section_header("Education"))
    for edu in EDUCATION:
        line = f"<b>{edu['degree']}</b> -- {edu['institution']}  <i>({edu['period']})</i>"
        story.append(Paragraph(line, STYLE_BODY_INDENT))

    # Experience
    story.extend(section_header("Experience"))
    for exp in EXPERIENCE:
        line = f"<b>{exp['role']}</b> -- {exp['org']}  <i>({exp['period']})</i>"
        story.append(Paragraph(line, STYLE_BODY_INDENT))

    # Selected Publications (top 4 by recency)
    story.extend(section_header("Selected Publications"))
    top_pubs = sorted(PUBLICATIONS, key=lambda p: p["year"], reverse=True)[:4]
    for pub in top_pubs:
        story.append(Paragraph(f"<b>{pub['title']}</b>", STYLE_PUB_TITLE))
        story.append(Paragraph(pub["authors"], STYLE_PUB_AUTHORS))
        story.append(Paragraph(pub["venue"], STYLE_PUB_VENUE))

    # Skills
    story.extend(section_header("Skills"))
    story.append(Paragraph(", ".join(SKILLS[:10]), STYLE_BODY_INDENT))

    # Languages
    story.extend(section_header("Languages"))
    lang_str = " | ".join(f"{name} ({level})" for name, level in LANGUAGES)
    story.append(Paragraph(lang_str, STYLE_BODY_INDENT))


def build_long_cv(story: list):
    """Build the complete long CV."""

    # Header
    story.append(Paragraph(PROFILE["name"], STYLE_NAME))
    story.append(Paragraph(PROFILE["title"], STYLE_CONTACT))
    story.append(contact_line())
    story.append(Spacer(1, 6))

    # Education
    story.extend(section_header("Education"))
    for edu in EDUCATION:
        story.append(Paragraph(f"<b>{edu['degree']}</b>", STYLE_BODY_INDENT))
        story.append(Paragraph(f"{edu['institution']}  <i>({edu['period']})</i>", STYLE_BODY_INDENT))
        story.append(Paragraph(edu["detail"], STYLE_BODY_INDENT))
        story.append(Spacer(1, 2))

    # Experience
    story.extend(section_header("Experience"))
    for exp in EXPERIENCE:
        story.append(Paragraph(f"<b>{exp['role']}</b>", STYLE_BODY_INDENT))
        story.append(Paragraph(f"{exp['org']}  --  {exp['location']}  <i>({exp['period']})</i>", STYLE_BODY_INDENT))
        story.append(Paragraph(exp["description"], STYLE_BODY_INDENT))
        story.append(Spacer(1, 2))

    # Publications
    story.extend(section_header("Publications"))
    for pub in PUBLICATIONS:
        story.append(Paragraph(f"<b>{pub['title']}</b>", STYLE_PUB_TITLE))
        story.append(Paragraph(pub["authors"], STYLE_PUB_AUTHORS))
        story.append(Paragraph(pub["venue"], STYLE_PUB_VENUE))

    # Preprints
    if PREPRINTS:
        story.extend(section_header("Preprints"))
        for pub in PREPRINTS:
            story.append(Paragraph(f"<b>{pub['title']}</b>", STYLE_PUB_TITLE))
            story.append(Paragraph(pub["authors"], STYLE_PUB_AUTHORS))
            story.append(Paragraph(pub["venue"], STYLE_PUB_VENUE))

    # Research Interests
    story.extend(section_header("Research Interests"))
    interests = [
        "Multilingual NLP",
        "Reasoning Under Uncertainty",
        "Human-Centered AI",
        "Machine Translation",
    ]
    for interest in interests:
        story.append(Paragraph(f"• {interest}", STYLE_BODY_INDENT))

    # Skills
    story.extend(section_header("Skills & Technologies"))
    story.append(Paragraph(", ".join(SKILLS), STYLE_BODY_INDENT))

    # Languages
    story.extend(section_header("Languages"))
    for name, level in LANGUAGES:
        story.append(Paragraph(f"{name} -- {level}", STYLE_BODY_INDENT))


def generate_pdf(filename: str, builder_fn):
    """Generate a single PDF file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filepath = OUTPUT_DIR / filename
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=1 * inch,
        rightMargin=1 * inch,
    )
    story = []
    builder_fn(story)
    doc.build(story)
    print(f"  Generated: {filepath}")


def main():
    print("CV PDF Generator")
    print("=" * 40)

    # Optionally read papers.json to verify it exists (but we use hardcoded
    # canonical data from the research page for consistency)
    if PAPERS_JSON.exists():
        with open(PAPERS_JSON) as f:
            data = json.load(f)
        print(f"  papers.json found ({data.get('paper_count', 0)} publications, "
              f"{len(data.get('preprints', []))} preprints)")
    else:
        print("  papers.json not found -- using embedded data from research page")

    print()
    print("Generating short CV (1-page)...")
    generate_pdf("cv-short.pdf", build_short_cv)

    print("Generating long CV (complete)...")
    generate_pdf("cv-long.pdf", build_long_cv)

    print()
    print("Done! PDFs saved to public/")


if __name__ == "__main__":
    main()
