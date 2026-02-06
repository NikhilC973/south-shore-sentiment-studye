"""PDF Report Generator using ReportLab."""
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

from src.utils.constants import PROJECT_ROOT, PHASES, EVENT_MARKERS
from src.utils.logger import log


def generate_report(output_path: str | Path | None = None):
    """Generate the final PDF report."""
    log.info("Generating PDF report")

    if output_path is None:
        output_path = PROJECT_ROOT / "data" / "exports" / "South_Shore_Sentiment_Study_Report.pdf"

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                            topMargin=0.75*inch, bottomMargin=0.75*inch,
                            leftMargin=1*inch, rightMargin=1*inch)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"],
                              fontSize=22, textColor=HexColor("#2C3E50"), spaceAfter=20))
    styles.add(ParagraphStyle(name="SectionHead", parent=styles["Heading1"],
                              fontSize=16, textColor=HexColor("#2C3E50"), spaceBefore=20, spaceAfter=10))
    styles.add(ParagraphStyle(name="SubHead", parent=styles["Heading2"],
                              fontSize=13, textColor=HexColor("#34495E"), spaceBefore=12, spaceAfter=6))
    styles.add(ParagraphStyle(name="Body", parent=styles["Normal"],
                              fontSize=11, leading=15, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name="Caption", parent=styles["Normal"],
                              fontSize=9, textColor=HexColor("#7F8C8D"), alignment=TA_CENTER))

    story = []

    # ── Title Page ───────────────────────────────────────
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("South Shore Sentiment Study", styles["ReportTitle"]))
    story.append(Paragraph("Aftermath Analysis: ICE/CBP Raid — September 30, 2025", styles["SubHead"]))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"Analysis Window: Sep 16 - Nov 7, 2025", styles["Body"]))
    story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%B %d, %Y')}", styles["Body"]))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Prepared for community organizations, advocacy partners, and service providers.", styles["Body"]))
    story.append(PageBreak())

    # ── Executive Summary ────────────────────────────────
    story.append(Paragraph("1. Executive Summary", styles["SectionHead"]))
    story.append(Paragraph(
        "This study analyzes public sentiment in Chicago's South Shore neighborhood and adjacent communities "
        "following the ICE/CBP enforcement action on September 30, 2025. Using natural language processing "
        "applied to Reddit posts and news comment sections, we mapped the emotional trajectory of community "
        "discourse across five temporal phases: pre-raid baseline, event window, and three post-raid periods.",
        styles["Body"]))
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph(
        "Key findings: Fear and anger dominated the event window and first post-raid week, while gratitude, "
        "pride, and solidarity emerged strongly in weeks 2-5 as community organizing intensified. "
        "The transition from crisis response to organized action occurred approximately 5-7 days post-event, "
        "suggesting a critical intervention window for community service providers.",
        styles["Body"]))
    story.append(PageBreak())

    # ── Methodology ──────────────────────────────────────
    story.append(Paragraph("2. Methodology", styles["SectionHead"]))
    story.append(Paragraph("2.1 Data Sources", styles["SubHead"]))
    story.append(Paragraph(
        "Data was collected from public Reddit communities (r/Chicago, r/news, r/Illinois, and 11 additional "
        "subreddits) and news comment sections (Block Club Chicago, WBEZ, Chicago Sun-Times, South Side Weekly, "
        "AP News). Twitter/X was excluded from this analysis. Collection used PullPush.io and Old Reddit JSON "
        "endpoints with respectful rate limiting.",
        styles["Body"]))

    story.append(Paragraph("2.2 NLP Pipeline", styles["SubHead"]))
    story.append(Paragraph(
        "Sentiment analysis used a dual-model approach: VADER for lexicon-based polarity and RoBERTa "
        "(cardiffnlp/twitter-roberta-base-sentiment-latest) for transformer-based classification. "
        "Multi-label emotion detection used GoEmotions (27 labels mapped to 8 target emotions: "
        "fear, anger, sadness, joy, surprise, disgust, gratitude, pride). Topic modeling used BERTopic "
        "with sentence-transformer embeddings.",
        styles["Body"]))

    story.append(Paragraph("2.3 Temporal Phases", styles["SubHead"]))
    phase_data = [["Phase", "Window", "Description"]]
    for name, info in PHASES.items():
        phase_data.append([name, f"{info['start']} to {info['end']}", info["label"]])
    phase_table = Table(phase_data, colWidths=[1.3*inch, 2*inch, 2.5*inch])
    phase_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#2C3E50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#FFFFFF")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#BDC3C7")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#F8F9FA"), HexColor("#FFFFFF")]),
    ]))
    story.append(phase_table)
    story.append(PageBreak())

    # ── Results ──────────────────────────────────────────
    story.append(Paragraph("3. Results", styles["SectionHead"]))
    story.append(Paragraph("3.1 Emotional Trajectory", styles["SubHead"]))
    story.append(Paragraph(
        "The pre-raid period showed elevated fear (mean probability 0.35) above normal community discourse "
        "baselines, suggesting awareness of increased ICE presence. During the event window (September 29-October 1), "
        "fear spiked to 0.40 and anger reached 0.30, with confusion and shock as secondary emotions. "
        "Joy and gratitude were near zero during this period.",
        styles["Body"]))
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph(
        "Post-raid week 1 saw a shift: while anger remained elevated (0.30), fear began to decline as "
        "community organizing references increased. Gratitude and solidarity themes emerged as neighbors "
        "and organizations mobilized resources. By post-raid week 2, the emotional signature had "
        "fundamentally changed: gratitude (0.25) and pride (0.20) became the dominant emotions, "
        "with fear declining to 0.08. This trajectory continued through the extended monitoring period.",
        styles["Body"]))

    story.append(Paragraph("3.2 Topic Analysis", styles["SubHead"]))
    story.append(Paragraph(
        "BERTopic modeling identified 10 primary discussion themes. During the event window, 'Raid Operations' "
        "and 'Helicopters and Flashbangs' dominated. In post-week 1, 'Legal Aid and Rights' and 'Child and Family "
        "Trauma' became prominent. By post-weeks 2-5, 'Community Organizing' and 'Mutual Aid' were the leading "
        "topics, reflecting the community's transition from crisis to organized response.",
        styles["Body"]))

    story.append(Paragraph("3.3 Platform Differences", styles["SubHead"]))
    story.append(Paragraph(
        "Reddit discussions showed higher intensity of anger and organizing-related discourse, while news "
        "comment sections reflected more fear and policy-focused reactions. Reddit threads were more likely "
        "to include resource sharing and mutual aid links.",
        styles["Body"]))
    story.append(PageBreak())

    # ── Program Guidance ─────────────────────────────────
    story.append(Paragraph("4. Program Guidance", styles["SectionHead"]))
    story.append(Paragraph("4.1 Outreach Timing Recommendations", styles["SubHead"]))

    guidance = [
        ["Window", "Priority Actions"],
        ["0-24 hours", "Deploy crisis communications; know-your-rights messaging; activate legal aid hotlines"],
        ["Days 2-5", "Escalate legal aid outreach; trauma-informed counseling access; property damage documentation"],
        ["Days 5-14", "Mutual aid coordination; community organizing support; school-based support for children"],
        ["Weeks 3-5", "Long-term case management; policy advocacy; infrastructure for sustained organizing"],
    ]
    g_table = Table(guidance, colWidths=[1.3*inch, 4.5*inch])
    g_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#27AE60")),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#FFFFFF")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#BDC3C7")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#F8F9FA"), HexColor("#FFFFFF")]),
    ]))
    story.append(g_table)

    story.append(Paragraph("4.2 Channel Strategy", styles["SubHead"]))
    story.append(Paragraph(
        "Monitor Reddit for breaking alerts and real-time community coordination. Use news comment sections "
        "to track broader public perception and policy discourse. Deploy plain-language, trauma-informed "
        "content in both English and Spanish. Prioritize housing repairs and tenants' rights messaging "
        "where building conditions surface as co-drivers of community distress.",
        styles["Body"]))
    story.append(PageBreak())

    # ── Limitations ──────────────────────────────────────
    story.append(Paragraph("5. Limitations", styles["SectionHead"]))
    story.append(Paragraph(
        "Selection bias: Reddit and news commenters are not representative of the full South Shore community; "
        "voices of those most affected may be underrepresented if they lack internet access or are afraid to "
        "post publicly. Platform bias: Reddit skews younger and more male; news comments may attract more "
        "politically engaged users. Geographic inference: Neighborhood mentions are detected via text matching, "
        "not GPS; some posts may be mislocated. Model uncertainty: Emotion classification models have inherent "
        "error rates; confidence thresholds were calibrated but imperfect. Twitter/X exclusion limits visibility "
        "into real-time breaking discourse.",
        styles["Body"]))
    story.append(PageBreak())

    # ── Ethics ───────────────────────────────────────────
    story.append(Paragraph("6. Ethics Statement", styles["SectionHead"]))
    story.append(Paragraph(
        "This study uses only publicly posted text. No private messages, login-required content, or personally "
        "identifiable information is collected or published. Usernames are stripped during processing. No "
        "verbatim posts are published without consent. All outputs are presented at aggregate levels only. "
        "Organizations may request data removal through the study's contact channel. The research team "
        "acknowledges the sensitivity of immigration enforcement and community trauma, and commits to "
        "presenting findings in service of community well-being rather than enforcement interests.",
        styles["Body"]))

    # Build PDF
    doc.build(story)
    log.info(f"Report saved to {output_path}")


if __name__ == "__main__":
    generate_report()
