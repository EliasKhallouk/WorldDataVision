#!/usr/bin/env python3
"""Génère le rapport IRC en PDF."""

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

OUTPUT_PDF = Path(__file__).parent.parent / "IRC_Report.pdf"


def build_story():
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    h_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        leading=14,
        spaceAfter=6,
    )

    story = []

    story.append(Paragraph("Rapport — Index de Résilience Civilisationnelle (IRC)", title_style))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("1) Objet du projet", h_style))
    story.append(Paragraph(
        "L’Index de Résilience Civilisationnelle (IRC) vise à répondre à la question : « Quels pays sont réellement préparés à traverser les 20 prochaines années ? ». "
        "L’objectif est de produire un score robuste et transparent, basé sur des indicateurs publics, permettant une comparaison internationale, une vision prospective, "
        "et un usage médiatique et institutionnel.",
        body_style,
    ))

    story.append(Paragraph("2) Hypothèse centrale", h_style))
    story.append(Paragraph(
        "La capacité d’un pays à traverser les chocs futurs dépend de cinq piliers systémiques : "
        "(1) Résilience démographique, (2) Souveraineté alimentaire, (3) Indépendance énergétique, "
        "(4) Stabilité politico-économique, (5) Capacité d’innovation et de transformation. "
        "Ces piliers conditionnent la stabilité sociale, la continuité économique et l’adaptation aux crises.",
        body_style,
    ))

    story.append(Paragraph("3) Indicateurs choisis et justification", h_style))

    story.append(Paragraph("A. Résilience démographique", ParagraphStyle("H3", parent=styles["Heading3"])) )
    story.append(Paragraph(
        "Pourquoi : un pays en vieillissement rapide ou à forte dépendance est structurellement fragile. "
        "Indicateurs : ratio de dépendance total, âge médian, parts des 0–14 et 65+, fécondité, croissance, solde migratoire. "
        "Apport : capacité de renouvellement et pression sur services publics.",
        body_style,
    ))

    story.append(Paragraph("B. Souveraineté alimentaire", ParagraphStyle("H3", parent=styles["Heading3"])) )
    story.append(Paragraph(
        "Pourquoi : la dépendance aux importations alimentaires augmente la vulnérabilité aux chocs géopolitiques. "
        "Indicateurs : terres agricoles et arables par habitant, rendement des cultures, importations alimentaires, stress hydrique. "
        "Apport : autonomie et robustesse des chaînes alimentaires.",
        body_style,
    ))

    story.append(Paragraph("C. Indépendance énergétique", ParagraphStyle("H3", parent=styles["Heading3"])) )
    story.append(Paragraph(
        "Pourquoi : les chocs énergétiques sont systémiques (inflation, crise sociale, instabilité). "
        "Indicateurs : importations nettes d’énergie, mix énergétique (renouvelable, fossile, nucléaire), électricité produite. "
        "Apport : capacité à soutenir l’économie sans dépendance critique.",
        body_style,
    ))

    story.append(Paragraph("D. Stabilité politico-économique", ParagraphStyle("H3", parent=styles["Heading3"])) )
    story.append(Paragraph(
        "Pourquoi : les États faibles ou endettés gèrent mal les crises longues. "
        "Indicateurs : dette publique, service de la dette, inflation, croissance, chômage, qualité de gouvernance (corruption, stabilité politique, état de droit). "
        "Apport : solidité institutionnelle et marge de manœuvre budgétaire.",
        body_style,
    ))

    story.append(Paragraph("E. Capacité d’innovation", ParagraphStyle("H3", parent=styles["Heading3"])) )
    story.append(Paragraph(
        "Pourquoi : la résilience future dépend de la capacité à se transformer. "
        "Indicateurs : R&D (% PIB), chercheurs par million, brevets, articles scientifiques, éducation supérieure, infrastructure numérique. "
        "Apport : vitesse d’adaptation et compétitivité long terme.",
        body_style,
    ))

    story.append(Paragraph("4) Méthodologie scientifique (approche proposée)", h_style))
    story.append(Paragraph(
        "Étape 1 — Normalisation : transformation des indicateurs en scores comparables (z-score ou min–max) et inversion des indicateurs de risque. "
        "Étape 2 — Construction des piliers : moyenne pondérée des indicateurs, pondérations initiales basées sur expertise puis testées. "
        "Étape 3 — Score global IRC : agrégation des cinq piliers, publication du score et des profils de résilience. "
        "Étape 4 — Validation : tests de sensibilité, comparaison avec indices existants (HDI, Fragile State Index), analyse de cohérence historique.",
        body_style,
    ))

    story.append(Paragraph("5) Transparence et reproductibilité", h_style))
    story.append(Paragraph(
        "Chaque score est traçable (source publique, méthode de normalisation, calculs reproductibles). "
        "L’objectif est d’éviter l’accusation de “score politique” et d’ancrer l’IRC dans une démarche rigoureuse.",
        body_style,
    ))

    story.append(Paragraph("6) Limites connues", h_style))
    story.append(Paragraph(
        "Certaines dimensions restent difficiles à quantifier (cohésion sociale, culture politique). "
        "Les données publiques ont des retards (1 à 2 ans). "
        "Les pondérations peuvent être contestées ; d’où l’intérêt de scénarios alternatifs.",
        body_style,
    ))

    story.append(Paragraph("7) Valeur ajoutée", h_style))
    story.append(Paragraph(
        "L’IRC ne se contente pas de décrire : il produit une synthèse structurante et prospective capable d’alimenter la décision publique, "
        "générer des analyses médiatiques fortes et devenir un standard référentiel.",
        body_style,
    ))

    return story


def main():
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Index de Résilience Civilisationnelle (IRC)",
        author="WorldDataVision",
    )
    story = build_story()
    doc.build(story)
    print(f"✅ PDF généré : {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
