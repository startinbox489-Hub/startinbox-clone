"""
PDF Service
"""

from typing import Dict, Any

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors


class PDFService:
    """
    PDF Service
    """

    def __init__(self) -> None:
        """
        Constructor
        """

        return

    def export_to_pdf(self, data: Dict[str, Any], filename: str = "startup_report.pdf"):
        """
        Formats and Exports file to pdf
        """
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph("🚀 Startup Idea Validation Report", styles["Title"]))
        story.append(Spacer(1, 12))

        # Idea Score
        story.append(
            Paragraph(
                f"Idea Score: {data['A. Validation Output']['idea_score']}",
                styles["Heading2"],
            )
        )
        story.append(Spacer(1, 12))

        # Lean Canvas
        story.append(Paragraph("Lean Canvas", styles["Heading2"]))
        for key, value in data["A. Validation Output"]["lean_canvas"].items():
            story.append(
                Paragraph(f"<b>{key.capitalize()}:</b> {value}", styles["Normal"])
            )
            story.append(Spacer(1, 6))

        # Customer Persona
        story.append(Paragraph("Ideal Customer Persona", styles["Heading2"]))
        for key, value in data["A. Validation Output"][
            "ideal_customer_persona"
        ].items():
            story.append(
                Paragraph(f"<b>{key.capitalize()}:</b> {value}", styles["Normal"])
            )
            story.append(Spacer(1, 6))

        # Launch Content
        story.append(Paragraph("Launch Content", styles["Heading2"]))
        hero = data["B. Launch Content Generator"]["website_hero"]
        story.append(
            Paragraph(
                f"<b>Website Hero:</b> {hero['headline']} - {hero['subheadline']}",
                styles["Normal"],
            )
        )
        for f in hero["features"]:
            story.append(Paragraph(f"- {f}", styles["Normal"]))

        doc.build(story)
        print(f"PDF saved as {filename}")

    def export_polished_pdf(self, data: dict, filename="startup_report.pdf"):
        """
        Formats and Exports polished PDF.
        """
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=40,
            bottomMargin=30,
        )
        styles = getSampleStyleSheet()
        story = []

        # Custom Styles
        title_style = ParagraphStyle(
            "title",
            parent=styles["Title"],
            fontSize=20,
            textColor=colors.HexColor("#2E86AB"),
        )
        h1 = ParagraphStyle(
            "h1", parent=styles["Heading1"], textColor=colors.HexColor("#2E4053")
        )
        h2 = ParagraphStyle(
            "h2", parent=styles["Heading2"], textColor=colors.HexColor("#117A65")
        )
        normal = styles["Normal"]

        # Cover Page
        story.append(Paragraph("🚀 Startup Idea Validation Report", title_style))
        story.append(Spacer(1, 20))
        story.append(
            Paragraph(
                f"Idea Score: <b>{data['A. Validation Output']['idea_score']}</b>", h1
            )
        )
        story.append(Spacer(1, 30))

        # === LEAN CANVAS (Table) ===
        story.append(Paragraph("Lean Canvas", h1))
        lean = data["A. Validation Output"]["lean_canvas"]
        canvas_table = [[k.capitalize(), v] for k, v in lean.items()]
        table = Table(canvas_table, colWidths=[150, 350])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E86AB")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 20))

        # === CUSTOMER PERSONA ===
        story.append(Paragraph("Ideal Customer Persona", h1))
        persona = data["A. Validation Output"]["ideal_customer_persona"]
        persona_table = [[k.capitalize(), v] for k, v in persona.items()]
        p_table = Table(persona_table, colWidths=[150, 350])
        p_table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FDFEFE")),
                ]
            )
        )
        story.append(p_table)
        story.append(Spacer(1, 20))

        # === STARTUP NAMES & MODELS ===
        story.append(Paragraph("Suggested Startup Names", h1))
        for name in data["A. Validation Output"]["suggested_startup_names"]:
            story.append(Paragraph(f"• {name}", normal))
        story.append(Spacer(1, 10))

        story.append(Paragraph("Monetization Models", h1))
        for model in data["A. Validation Output"]["monetization_models"]:
            story.append(Paragraph(f"• {model}", normal))
        story.append(PageBreak())

        # === WEBSITE HERO ===
        story.append(Paragraph("Website Hero Section", h1))
        hero = data["B. Launch Content Generator"]["website_hero"]
        story.append(Paragraph(f"<b>{hero['headline']}</b>", h2))
        story.append(Paragraph(hero["subheadline"], normal))
        story.append(Spacer(1, 10))
        story.append(Paragraph("Features:", h2))
        for f in hero["features"]:
            story.append(Paragraph(f"• {f}", normal))
        story.append(Spacer(1, 20))

        # === BLOG POSTS ===
        story.append(Paragraph("Blog Post Ideas", h1))
        for post in data["B. Launch Content Generator"]["blog_posts"]:
            story.append(Paragraph(f"<b>{post['title']}</b>", h2))
            for bullet in post["outline"]:
                story.append(Paragraph(f"– {bullet}", normal))
            story.append(Spacer(1, 10))

        # === TWITTER POSTS ===
        story.append(PageBreak())
        story.append(Paragraph("Social Media Launch Posts", h1))
        for tw in data["B. Launch Content Generator"]["twitter_posts"]:
            story.append(Paragraph(f"• {tw}", normal))
        story.append(Spacer(1, 20))

        # === ELEVATOR PITCH SLIDE ===
        story.append(Paragraph("Elevator Pitch Slide", h1))
        pitch = data["B. Launch Content Generator"]["elevator_pitch_slide"]
        story.append(Paragraph(f"<b>{pitch['headline']}</b>", h2))
        for bp in pitch["bullet_points"]:
            story.append(Paragraph(f"• {bp}", normal))

        # Build the PDF
        doc.build(story)
        print(f"✅ Polished PDF saved as {filename}")


pdf_service = PDFService()
