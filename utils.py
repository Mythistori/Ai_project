from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import io
from datetime import datetime


def generate_pdf_report(result: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Normal"],
        fontSize=22,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        fontName="Helvetica",
        textColor=colors.HexColor("#64748b"),
        spaceAfter=16,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#64748b"),
        spaceBefore=16,
        spaceAfter=8,
        borderPad=0,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=11,
        fontName="Helvetica",
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6,
        leading=16,
    )
    verdict_colors = {
        "hire": colors.HexColor("#166534"),
        "maybe": colors.HexColor("#854d0e"),
        "reject": colors.HexColor("#991b1b"),
    }
    verdict_bg = {
        "hire": colors.HexColor("#dcfce7"),
        "maybe": colors.HexColor("#fef9c3"),
        "reject": colors.HexColor("#fee2e2"),
    }

    story = []

    # Header
    story.append(Paragraph("AI Recruitment Report", title_style))
    story.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}",
        subtitle_style,
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
    story.append(Spacer(1, 12))

    # Candidate name + verdict
    verdict = result.get("verdict", "maybe")
    verdict_label = {"hire": "RECOMMEND HIRE", "maybe": "CONSIDER", "reject": "NOT A FIT"}.get(verdict, verdict.upper())

    header_data = [
        [
            Paragraph(f"<b>{result.get('candidate_name', 'Candidate')}</b>", ParagraphStyle(
                "CandName", parent=styles["Normal"], fontSize=16, fontName="Helvetica-Bold",
                textColor=colors.HexColor("#0f172a"),
            )),
            Paragraph(verdict_label, ParagraphStyle(
                "Verdict", parent=styles["Normal"], fontSize=11, fontName="Helvetica-Bold",
                textColor=verdict_colors.get(verdict, colors.black),
                alignment=TA_CENTER,
            )),
        ]
    ]
    header_table = Table(header_data, colWidths=["70%", "30%"])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (1, 0), (1, 0), verdict_bg.get(verdict, colors.white)),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
        ("PADDING", (1, 0), (1, 0), 10),
        ("PADDING", (0, 0), (0, 0), 4),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 16))

    # Score + metrics table
    story.append(Paragraph("OVERVIEW", section_style))
    metrics_data = [
        ["Match Score", "Experience", "Skills Matched"],
        [
            f"{result.get('score', 0)}%",
            result.get("experience_years", "—"),
            f"{len(result.get('matching_skills', []))} / {len(result.get('matching_skills', [])) + len(result.get('missing_skills', []))}",
        ],
    ]
    metrics_table = Table(metrics_data, colWidths=["33%", "33%", "34%"])
    metrics_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
        ("BACKGROUND", (0, 1), (-1, 1), colors.white),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#64748b")),
        ("TEXTCOLOR", (0, 1), (-1, 1), colors.HexColor("#0f172a")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica"),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTSIZE", (0, 1), (-1, 1), 18),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 8))
    # Score Breakdown
    breakdown = result.get("score_breakdown", {})
    if breakdown:
        story.append(Paragraph("SCORE BREAKDOWN", section_style))
        breakdown_data = [
            ["Skills Match", "Experience", "Education", "Job Fit"],
            [
                f"{breakdown.get('skills_match', 0)}%",
                f"{breakdown.get('experience_match', 0)}%",
                f"{breakdown.get('education_match', 0)}%",
                f"{breakdown.get('job_fit', 0)}%",
            ],
        ]
        breakdown_table = Table(breakdown_data, colWidths=["25%", "25%", "25%", "25%"])
        breakdown_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#64748b")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(breakdown_table)
        story.append(Spacer(1, 8))


    # HR Summary
    story.append(Paragraph("HR SUMMARY", section_style))
    story.append(Paragraph(result.get("hr_summary", "—"), body_style))
    story.append(Spacer(1, 4))

    # Skills
    story.append(Paragraph("SKILLS ANALYSIS", section_style))
    matching = ", ".join(result.get("matching_skills", [])) or "None"
    missing = ", ".join(result.get("missing_skills", [])) or "None"

    skills_data = [
        ["✓ Matching Skills", "✗ Missing Skills"],
        [matching, missing],
    ]
    skills_table = Table(skills_data, colWidths=["50%", "50%"])
    skills_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#f0fdf4")),
        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#fef2f2")),
        ("TEXTCOLOR", (0, 0), (0, 0), colors.HexColor("#166534")),
        ("TEXTCOLOR", (1, 0), (1, 0), colors.HexColor("#991b1b")),
        ("TEXTCOLOR", (0, 1), (-1, 1), colors.HexColor("#1e293b")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(skills_table)
    story.append(Spacer(1, 8))

    # Profile
    story.append(Paragraph("CANDIDATE PROFILE", section_style))
    profile_data = [
        ["Education", result.get("education", "—")],
        ["Experience", result.get("experience_years", "—")],
        ["Strengths", result.get("strengths", "—")],
        ["Weaknesses", result.get("weaknesses", "—")],
    ]
    profile_table = Table(profile_data, colWidths=["25%", "75%"])
    profile_table.setStyle(TableStyle([
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#64748b")),
        ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#1e293b")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(profile_table)
    story.append(Spacer(1, 8))

    # Interview questions
    story.append(Paragraph("INTERVIEW QUESTIONS", section_style))
    q_colors = {
        "technical": colors.HexColor("#dbeafe"),
        "behavioral": colors.HexColor("#ede9fe"),
        "situational": colors.HexColor("#fef9c3"),
    }
    q_text_colors = {
        "technical": colors.HexColor("#1e40af"),
        "behavioral": colors.HexColor("#6b21a8"),
        "situational": colors.HexColor("#854d0e"),
    }
    for i, q in enumerate(result.get("questions", []), 1):
        qtype = q.get("type", "technical")
        q_data = [[
            Paragraph(qtype.upper(), ParagraphStyle(
                "QType", parent=styles["Normal"], fontSize=8, fontName="Helvetica-Bold",
                textColor=q_text_colors.get(qtype, colors.black),
            )),
            Paragraph(f"{i}. {q.get('text', '')}", body_style),
        ]]
        q_table = Table(q_data, colWidths=["15%", "85%"])
        q_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), q_colors.get(qtype, colors.white)),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (0, 0), "CENTER"),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(q_table)
        story.append(Spacer(1, 4))

    # Footer
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0")))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Generated by AI Recruitment Assistant · Powered by Groq (LLaMA 3.3 70B)",
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8,
                       textColor=colors.HexColor("#94a3b8"), alignment=TA_CENTER),
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()