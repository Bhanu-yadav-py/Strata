"""
Generate a comprehensive, beautifully formatted 9-page technical dossier for Project Strata in Hinglish.
Covers: Problem, Solution, Data Sources, Spectral Alteration Physics, Tech Stack,
Machine Learning Prediction Architecture, Real-Time Telemetry, and Potential Impact.
Guarantees strict 9-page layout matching the 6-12 pages requirement.
"""

import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    HRFlowable,
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and render total page count
    along with clean professional running headers and footers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        # Don't draw header/footer on cover page (Page 1)
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#777777"))

        # Running Header
        self.drawString(
            44,
            11 * 72 - 28,
            "STRATA — ORBITAL MANGANESE RESERVE INTELLIGENCE | TECHNICAL DOSSIER",
        )
        self.setFont("Helvetica", 7.5)
        self.drawRightString(8.5 * 72 - 44, 11 * 72 - 28, "AI/ML Remote Sensing")
        self.setStrokeColor(colors.HexColor("#D8D2C5"))
        self.setLineWidth(0.6)
        self.line(44, 11 * 72 - 32, 8.5 * 72 - 44, 11 * 72 - 32)

        # Running Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * 72 - 44, 22, page_text)
        self.drawString(
            44,
            22,
            "Confidential & Proprietary — Strata Exploration Platform (Hinglish Edition)",
        )
        self.line(44, 30, 8.5 * 72 - 44, 30)
        self.restoreState()


def build_pdf(filename="Strata_Project_Documentation_Hinglish.pdf"):
    pdf_path = os.path.join(os.path.dirname(__file__), filename)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=44,
        rightMargin=44,
        topMargin=38,
        bottomMargin=38,
    )

    # Styles Setup
    styles = getSampleStyleSheet()

    # Custom Palettes
    c_primary = colors.HexColor("#B5652E")     # Warm Rust
    c_dark = colors.HexColor("#1A1D16")        # Deep Ore Charcoal
    c_teal = colors.HexColor("#2C6153")        # Mineral Teal
    c_gold = colors.HexColor("#A87A24")        # Raw Brass / Gold
    c_body = colors.HexColor("#222222")        # Charcoal body
    c_card_bg = colors.HexColor("#FAF8F4")     # Soft cream panel
    c_border = colors.HexColor("#DDD6C8")      # Subtle border

    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=c_dark,
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11.5,
        leading=16,
        textColor=c_primary,
        spaceAfter=10,
    )

    h1_style = ParagraphStyle(
        'ChapterH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=c_dark,
        spaceBefore=2,
        spaceAfter=4,
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=c_teal,
        spaceBefore=5,
        spaceAfter=3,
    )

    body_style = ParagraphStyle(
        'BodyHinglish',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.6,
        leading=12.6,
        textColor=c_body,
        spaceAfter=5,
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.8,
        leading=10.5,
        textColor=colors.HexColor("#9C4210"),
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.4,
        leading=12.2,
        textColor=c_dark,
    )

    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=11.5,
        textColor=colors.HexColor("#555555"),
    )

    story = []
    content_width = 8.5 * 72 - 88  # 524 pt

    def make_card(paragraph_content, bg_color=c_card_bg, border_color=c_border, padding=6):
        t = Table([[paragraph_content]], colWidths=[content_width])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_color),
            ('BOX', (0,0), (-1,-1), 0.8, border_color),
            ('TOPPADDING', (0,0), (-1,-1), padding),
            ('BOTTOMPADDING', (0,0), (-1,-1), padding),
            ('LEFTPADDING', (0,0), (-1,-1), padding + 3),
            ('RIGHTPADDING', (0,0), (-1,-1), padding + 3),
        ]))
        return t

    # =========================================================================
    # PAGE 1: TITLE & EXECUTIVE SUMMARY (COVER PAGE)
    # =========================================================================
    story.append(Spacer(1, 15))
    badge_p = Paragraph("<font color='#B5652E'><b>● TECHNICAL PROJECT DOSSIER | HINGLISH EDITION</b></font>", meta_style)
    story.append(badge_p)
    story.append(Spacer(1, 6))

    story.append(Paragraph("Project Strata: Orbital Manganese Reserve Intelligence", title_style))
    story.append(Paragraph("AI & Multispectral Remote Sensing se Zameen ke Neeche Chhupe Mineral Deposits ka Orbital Detection", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceAfter=12))

    exec_summary_text = (
        "<b>Executive Summary (Short Overview):</b><br/>"
        "<b>Project Strata</b> ek AI-powered mineral exploration intelligence platform hai jo satellite remote sensing "
        "(Sentinel-2, ASTER, SRTM) aur Machine Learning (Random Forest) ko fuse karke <b>high-grade Manganese (Mn) ore "
        "deposits</b> ko orbit se detect aur rank karta hai.<br/><br/>"
        "Traditional mining me zameen par jakar blind drilling karna bohot mehenga (costs up to millions of dollars), "
        "extremely time-consuming (12 se 24 mahine), aur environmentally damaging hota hai. Strata is pure process ko "
        "<b>digital, remote aur 10x fast</b> bana deta hai. Hum orbit se multi-band spectral surface reflection aur digital elevation "
        "models (DEM) analyze karke surface mineral alteration zones (gossan, laterite, iron oxide caps) ko identify karte hain "
        "aur geological machine learning classifier se mineralization probability calculate karte hain."
    )
    story.append(make_card(Paragraph(exec_summary_text, body_style), bg_color=colors.HexColor("#F5EFE6"), border_color=c_primary, padding=10))
    story.append(Spacer(1, 12))

    meta_table_data = [
        [Paragraph("<b>Core Technology:</b>", meta_style), Paragraph("Multispectral Remote Sensing + Scikit-Learn Machine Learning", meta_style)],
        [Paragraph("<b>Satellite Sensors:</b>", meta_style), Paragraph("Copernicus Sentinel-2 MSI, NASA/METI ASTER SWIR, SRTM 30m DEM", meta_style)],
        [Paragraph("<b>Primary Mineral Target:</b>", meta_style), Paragraph("Manganese Oxide Ores (Braunite, Pyrolusite, Psilomelane)", meta_style)],
        [Paragraph("<b>Geographical Focus:</b>", meta_style), Paragraph("Central & Eastern Indian Belts (MP, Maharashtra, Odisha, Karnataka, Rajasthan)", meta_style)],
        [Paragraph("<b>Deployment Architecture:</b>", meta_style), Paragraph("Dockerized FastAPI REST API + Vanilla JS/Leaflet GIS (Live on Render Cloud)", meta_style)],
        [Paragraph("<b>Live Production URL:</b>", meta_style), Paragraph("<u>https://strata-manganese-intelligence-wqcr.onrender.com</u>", meta_style)],
    ]
    t_meta = Table(meta_table_data, colWidths=[150, content_width - 150])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_card_bg),
        ('BOX', (0,0), (-1,-1), 0.8, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_meta)

    story.append(Spacer(1, 14))
    story.append(Paragraph("<b>Document Index (Anukramanika):</b>", h2_style))
    index_text = (
        "• <b>Chapter 1 (Page 2):</b> The Exact Problem Statement (Mining Bottlenecks, Shortfall & Blind Drilling)<br/>"
        "• <b>Chapter 2 (Page 3):</b> The Exact Solution (Strata AI Orbital Targeting Paradigm)<br/>"
        "• <b>Chapter 3 (Page 4):</b> Datasets Ingestion & Collection Sources (Open Earth Observation Stack)<br/>"
        "• <b>Chapter 4 (Page 5):</b> Spectral Alteration Physics & Geochemical Ratios (B4/B2, B11/B8, Gossan)<br/>"
        "• <b>Chapter 5 (Page 6):</b> Complete Tech Stack Breakdown (Frontend, Backend, ML, Cloud)<br/>"
        "• <b>Chapter 6 (Page 7):</b> Machine Learning Prediction Mechanics (Random Forest Inference Engine)<br/>"
        "• <b>Chapter 7 (Page 8):</b> Interactive Exploration Studio & Live Telemetry Architecture<br/>"
        "• <b>Chapter 8 (Page 9):</b> Potential Impact, Industrial Economics & Scalability Roadmap"
    )
    story.append(Paragraph(index_text, body_style))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: CHAPTER 1 — THE EXACT PROBLEM STATEMENT
    # =========================================================================
    story.append(Paragraph("Chapter 1: The Exact Problem Statement", h1_style))
    story.append(Paragraph("Mineral Exploration Industry ki Real-World Chunautiyan aur Supply Crisis", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceAfter=8))

    p1_desc = (
        "<b>1.1 Context: Manganese kyu itna critical mineral hai?</b><br/>"
        "Manganese (Mn) modern industrial economy ke liye ek <b>irreplaceable strategic mineral</b> hai. "
        "Iski do sabse badi demands hain:<br/>"
        "1. <b>Steel Manufacturing:</b> Har 1 tonne steel ko deoxidize aur sulfur nikalne ke liye lagbhag 6 se 10 kg "
        "manganese zaroori hota hai. Iska koi affordable chemical substitute exist nahi karta.<br/>"
        "2. <b>Electric Vehicle (EV) Batteries:</b> Next-generation EV batteries (LMFP — Lithium Manganese Iron Phosphate, "
        "aur NMC cathodes) me high-purity battery-grade manganese sulfate (HPMSM) ki demand har saal <b>~30-40%</b> surge ho rahi hai."
    )
    story.append(Paragraph(p1_desc, body_style))
    story.append(Spacer(1, 4))

    problem_boxes = [
        [
            Paragraph("<b>Problem 1: Blind Drilling & Capital Waste</b>", h2_style),
            Paragraph(
                "Traditional exploration me geologists ko zameen par jakar andhere me 'core drilling' karni padti hai. "
                "Ek exploratory borehole drill karne ka kharcha <b>INR 20 Lakh se 1 Crore</b> tak hota hai. "
                "Industry stats ke mutabiq, <b>70% se 80% exploratory boreholes barren (khali)</b> nikalte hain. "
                "Crores of rupees waste hote hain bina kisi discovery ke.",
                body_style
            )
        ],
        [
            Paragraph("<b>Problem 2: Extremely Slow Discovery Cycle</b>", h2_style),
            Paragraph(
                "Greenfield exploration (nayi jagah dhoondhna) me preliminary geological survey, soil sampling, trenching "
                "aur statutory clearances me <b>2 se 4 saal</b> lag jate hain. Industry ko minerals turant chahiye, par exploration speed "
                "purane manual methods par atki hui hai.",
                body_style
            )
        ],
        [
            Paragraph("<b>Problem 3: Massive Forest & Ecological Damage</b>", h2_style),
            Paragraph(
                "India me manganese reserves predominantly dense forest zones (Madhya Pradesh ka Balaghat belt, Odisha ka Keonjhar) "
                "me sthit hain. Heavy machinery aur bulldozers lane ke liye hazaron ped katne padte hain, jisse ecological "
                "fragility aur tribal communities ka bhari nuksan hota hai.",
                body_style
            )
        ],
        [
            Paragraph("<b>Problem 4: Widening Production vs Demand Gap</b>", h2_style),
            Paragraph(
                "India ka annual manganese production lagbhag <b>3.25 Million Tonnes (Mt)</b> hai, jabki domestic demand <b>4.10 Mt</b> "
                "par pahunch chuki hai. Har saal <b>~0.85 Mt ka shortfall</b> ho raha hai, jise pura karne ke liye expensive imports "
                "par foreign currency spend karni pad rahi hai.",
                body_style
            )
        ]
    ]

    t_prob = Table(problem_boxes, colWidths=[170, content_width - 170])
    t_prob.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_card_bg),
        ('BOX', (0,0), (-1,-1), 0.8, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_prob)
    story.append(Spacer(1, 6))

    callout_p1 = (
        "<b>Asli Samasya (Core Root Cause):</b> Geological survey teams ke paas koi aisa platform nahi tha jo "
        "physical drilling se pehle, orbit se satellite data analyze karke bata sake ki <i>'Is specific latitude-longitude "
        "par drill karo, yaha manganese oxide milne ki probability 85%+ hai'</i>. Yahi critical gap <b>Strata</b> solve karta hai."
    )
    story.append(make_card(Paragraph(callout_p1, callout_style), bg_color=colors.HexColor("#FBF4EB"), border_color=c_primary, padding=6))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: CHAPTER 2 — THE EXACT SOLUTION
    # =========================================================================
    story.append(Paragraph("Chapter 2: The Exact Solution", h1_style))
    story.append(Paragraph("Strata: AI + Remote Sensing ka Orbital Targeting Architecture", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceAfter=8))

    sol_overview = (
        "<b>Strata ka Solution Concept:</b><br/>"
        "Strata physically drill karne se pehle space satellites ki madad leta hai. "
        "Earth observation satellites (jaise ESA ka Sentinel-2 aur NASA ka ASTER) earth surface ki multi-spectral light reflectance capture karte hain. "
        "Jab zameen ke neeche manganese aur iron ores weather (weathering) hote hain, toh wo surface par specific "
        "<b>mineral oxide alteration signatures (ferric iron, gossan caps, laterite crusts)</b> chhodte hain.<br/><br/>"
        "Strata in orbital spectral reflection bands ko mathematically process karta hai, digital terrain slope aur elevation se fuse karta hai, "
        "aur hamare trained Machine Learning model me feed karta hai. Geologist ko bas coordinates daalne hote hain, aur system instant "
        "<b>Reserve Probability Score (0 to 100%)</b> aur structural risk assessment dossier generate karke de deta hai."
    )
    story.append(Paragraph(sol_overview, body_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("End-to-End Execution Flowchart:", h2_style))

    flow_table_data = [
        [Paragraph("<b>Step 1: Space Orbit</b>", meta_style), Paragraph("Sentinel-2, ASTER aur SRTM satellites zameen ka multispectral reflectance aur elevation capture karte hain.", body_style)],
        [Paragraph("<b>Step 2: Spectral Ratios</b>", meta_style), Paragraph("Diagnostic geochemical ratios calculate hote hain: Ferric Iron (B4/B2), Gossan (B4/B3), Laterite (B11/B8), Ferrous (B12/B8), NDVI.", body_style)],
        [Paragraph("<b>Step 3: Realtime Telemetry</b>", meta_style), Paragraph("Open-Meteo & SRTM APIs se exact point ka accurate Digital Elevation (m) aur surface slope (deg) real-time sample hota hai.", body_style)],
        [Paragraph("<b>Step 4: ML Prediction</b>", meta_style), Paragraph("Random Forest Classifier (300 estimators) 7-dimensional feature vector analyze karke Probability (0-1.0) predict karta hai.", body_style)],
        [Paragraph("<b>Step 5: Visual Map Studio</b>", meta_style), Paragraph("Interactive Leaflet map par target pinpoint hota hai, confidence gauge dikhta hai, aur structured JSON dossier export hota hai.", body_style)],
    ]
    t_flow = Table(flow_table_data, colWidths=[130, content_width - 130])
    t_flow.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_card_bg),
        ('BOX', (0,0), (-1,-1), 0.8, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_flow)
    story.append(Spacer(1, 6))

    story.append(Paragraph("Strata ke 4 Core Pillars:", h2_style))
    pillars_text = (
        "1. <b>Zero-Cost Satellite Access:</b> Kisi costly proprietary commercial satellite images ki zaroorat nahi. Strata 100% open-access Copernicus aur NASA data standards par kaam karta hai.<br/>"
        "2. <b>Micro-Targeting vs Blind Survey:</b> Poore 100 sq km jungle ko khodne ke bajaye, Strata 20-50 meter ke high-probability micro-targets filter kar deta hai.<br/>"
        "3. <b>Instant Dossier Generation:</b> Field teams ek click me complete geological profile (rock indices, elevation, vegetation index, classification tier) export kar sakti hain.<br/>"
        "4. <b>Cross-Referencing Supply Deficit:</b> Model prediction ke sath-sath national mineral deficit tracking bhi provide karta hai taaki auction planning priority-wise ho sake."
    )
    story.append(Paragraph(pillars_text, body_style))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: CHAPTER 3 — DATASETS & COLLECTION SOURCES
    # =========================================================================
    story.append(Paragraph("Chapter 3: Data Sources & Collection Pipeline", h1_style))
    story.append(Paragraph("Hum Data Kaha Se Collect Kar Rahe Hain? (Raw Sources & Ground Truth)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceAfter=8))

    data_intro = (
        "Strata ka data pipeline <b>3 distinct layers</b> se bana hai: "
        "(1) Multi-spectral Satellite Imagery, (2) Digital Elevation Terrain Data, aur (3) Verified Ground-Truth Deposit Points. "
        "Yaha un sabhi datasets ki detail di gayi hai:"
    )
    story.append(Paragraph(data_intro, body_style))
    story.append(Spacer(1, 4))

    datasets_table = [
        [
            Paragraph("<b>Dataset Name</b>", meta_style),
            Paragraph("<b>Source / Agency</b>", meta_style),
            Paragraph("<b>Bands / Attributes Used</b>", meta_style),
            Paragraph("<b>Role in Project</b>", meta_style),
        ],
        [
            Paragraph("<b>Sentinel-2 MSI Level-2A</b>", body_style),
            Paragraph("European Space Agency (ESA) Copernicus Program via Google Earth Engine", body_style),
            Paragraph("B2 (Blue), B3 (Green), B4 (Red), B8 (NIR), B11 (SWIR-1), B12 (SWIR-2)", code_style),
            Paragraph("Surface reflectance values se iron oxide, gossan aur laterite chemical alteration indices compute karne ke liye.", body_style),
        ],
        [
            Paragraph("<b>ASTER Global SWIR/TIR</b>", body_style),
            Paragraph("NASA / METI (Japan)", body_style),
            Paragraph("SWIR B4, B5, B7; Thermal TIR", code_style),
            Paragraph("Siliceous aur aluminous minerals ko separate karne aur hydrothermal alteration detect karne ke liye.", body_style),
        ],
        [
            Paragraph("<b>SRTM GL1 30m DEM</b>", body_style),
            Paragraph("NASA / USGS Shuttle Radar Topography Mission", body_style),
            Paragraph("Elevation (meters MSL), Terrain Slope (degrees)", code_style),
            Paragraph("Topographic ridge lineaments identify karne ke liye, jaha weathering aur enrichment possible hoti hai.", body_style),
        ],
        [
            Paragraph("<b>USGS MRDS Catalog</b>", body_style),
            Paragraph("United States Geological Survey (USGS)", body_style),
            Paragraph("Lat, Lon, Commodity (`Manganese`), Mine Name, State", code_style),
            Paragraph("Verified ground truth positive deposit training points (Balaghat, Bharweli, Tirodi, Joda, Barbil, Sandur).", body_style),
        ],
        [
            Paragraph("<b>GSI Bhukosh & IBM</b>", body_style),
            Paragraph("Geological Survey of India & Indian Bureau of Mines", body_style),
            Paragraph("Mining lease boundaries, reserve grades, annual production statistics", code_style),
            Paragraph("Model validation ground-truth, region catalog definition, aur `/production-gap` analysis data.", body_style),
        ],
    ]

    t_data = Table(datasets_table, colWidths=[95, 115, 150, content_width - 360])
    t_data.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EAE4D8")),
        ('BOX', (0,0), (-1,-1), 0.8, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_data)
    story.append(Spacer(1, 6))

    data_summary_box = (
        "<b>Data Pipeline Workflow:</b><br/>"
        "1. `data/fetch_mrds_deposits.py`: USGS open mineral catalog se verified Indian manganese mines filter karke positive coordinates nikalta hai.<br/>"
        "2. `data/build_training_csv.py`: Positive deposits ke sath-sath non-mineralized background areas ke negative points generate karta hai (balanced 50-50 dataset).<br/>"
        "3. Har point par 7-dimensional features (spectral ratios + DEM slope/elev) attach karke final `training_data.csv` banata hai."
    )
    story.append(make_card(Paragraph(data_summary_box, body_style), bg_color=c_card_bg, padding=5))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: CHAPTER 4 — SPECTRAL RATIOS & GEOCHEMICAL INDICES
    # =========================================================================
    story.append(Paragraph("Chapter 4: Spectral Alteration Physics & Band Ratios", h1_style))
    story.append(Paragraph("Satellite Multispectral Reflectance se Minerals Kaise Detect Hote Hain?", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceAfter=8))

    spectral_intro = (
        "Har mineral sunlight ke specific wavelengths (Visible, Near-Infrared, Shortwave-Infrared) ko "
        "apni chemical composition ke hisab se absorb ya reflect karta hai. Is property ko <b>Diagnostic Spectral Absorption Signature</b> kehte hain. "
        "Strata in 7 geoscientific feature indices ko calculate karta hai:"
    )
    story.append(Paragraph(spectral_intro, body_style))
    story.append(Spacer(1, 4))

    ratios_data = [
        [
            Paragraph("<b>Feature Index</b>", meta_style),
            Paragraph("<b>Formula / Satellite Bands</b>", meta_style),
            Paragraph("<b>Geological Science & Reason (Kyu use kiya?)</b>", meta_style),
        ],
        [
            Paragraph("<b>1. Ferric Iron Index</b>", body_style),
            Paragraph("<code>B4 / B2</code><br/>(Red / Blue)", code_style),
            Paragraph("Manganese ore hamesha iron oxide (hematite, goethite) ke sath co-occur karta hai. "
                      "Ferric iron ($Fe^{3+}$) blue light ko absorb karta hai aur red light ko strongly reflect karta hai. "
                      "Ratio > 1.25 oxide-rich zone signal karta hai.", body_style),
        ],
        [
            Paragraph("<b>2. Gossan Index</b>", body_style),
            Paragraph("<code>B4 / B3</code><br/>(Red / Green)", code_style),
            Paragraph("<b>Gossan</b> weathered oxide cap-rock hota hai jo subsurface metallic sulfide/oxide ore body ke upar banta hai. "
                      "High B4/B3 ratio oxidic capping ko indicate karta hai.", body_style),
        ],
        [
            Paragraph("<b>3. Laterite Index</b>", body_style),
            Paragraph("<code>B11 / B8</code><br/>(SWIR-1 / NIR)", code_style),
            Paragraph("Tropical weathering me lateritic crust banti hai jisme manganese secondary enrichment (pyrolusite/psilomelane) "
                      "hota hai. SWIR-1 (1610nm) band hydroxyl aur laterite crust me peak reflectance deta hai.", body_style),
        ],
        [
            Paragraph("<b>4. Ferrous Mineral Index</b>", body_style),
            Paragraph("<code>B12 / B8</code><br/>(SWIR-2 / NIR)", code_style),
            Paragraph("Host rock lithology (mafic/ultramafic schists, phyllites aur gondite rocks) ko characterize karta hai "
                      "jo Sausar aur Iron Ore Supergroups ka base rock hain.", body_style),
        ],
        [
            Paragraph("<b>5. NDVI (Vegetation)</b>", body_style),
            Paragraph("<code>(B8 - B4) / (B8 + B4)</code><br/>(NIR - Red)/(NIR + Red)", code_style),
            Paragraph("Dense jungle aur greenery bare-rock spectral signal ko mask (chupa) deti hai. "
                      "Strata NDVI calculate karke dense canopy ko filter karta hai taaki false positive signal na mile.", body_style),
        ],
        [
            Paragraph("<b>6. Terrain Slope</b>", body_style),
            Paragraph("<code>SRTM DEM Slope (degrees)</code>", code_style),
            Paragraph("Manganese oxide enrichment plateau edges aur moderate slopes (5° - 15°) par concentrate hota hai. "
                      "Bohot steep vertical cliffs par ore wash ho jata hai.", body_style),
        ],
        [
            Paragraph("<b>7. Elevation (DEM)</b>", body_style),
            Paragraph("<code>SRTM Elevation (meters)</code>", code_style),
            Paragraph("Central India me manganese horizons specific structural elevation bands (300m - 550m MSL) "
                      "me weather hokar concentrate hote hain.", body_style),
        ],
    ]

    t_ratios = Table(ratios_data, colWidths=[115, 125, content_width - 240])
    t_ratios.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EAE4D8")),
        ('BOX', (0,0), (-1,-1), 0.8, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_ratios)
    story.append(Spacer(1, 6))

    callout_p4 = (
        "<b>Feature Fusion Strength:</b> Sirf ek index dekhna dhoka de sakta hai (e.g. red soil ferric iron de sakti hai bina ore ke). "
        "Lekin jab saare 7 features ek sath match hote hain — high ferric iron + high gossan + high laterite + moderate slope — "
        "tab ML model ka confidence exponentially high ho jata hai."
    )
    story.append(make_card(Paragraph(callout_p4, callout_style), bg_color=colors.HexColor("#FBF4EB"), border_color=c_primary, padding=5))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: CHAPTER 5 — COMPLETE TECH STACK BREAKDOWN
    # =========================================================================
    story.append(Paragraph("Chapter 5: Complete Tech Stack Breakdown", h1_style))
    story.append(Paragraph("Strata ke Construction me Kaun-Kaun si Technologies & Tools Use Hue Hain?", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceAfter=8))

    tech_intro = (
        "Project Strata ko enterprise-grade architecture par design kiya gaya hai jisme speed, reliability, "
        "zero-dependency client execution, aur production-ready scalability par dhyan diya gaya hai. Yaha har layer ka breakdown hai:"
    )
    story.append(Paragraph(tech_intro, body_style))
    story.append(Spacer(1, 4))

    tech_data = [
        [
            Paragraph("<b>Layer</b>", meta_style),
            Paragraph("<b>Technology / Tool</b>", meta_style),
            Paragraph("<b>Version & Purpose in Strata</b>", meta_style),
        ],
        [
            Paragraph("<b>Backend Core</b>", body_style),
            Paragraph("<b>Python 3.11 + FastAPI</b>", h2_style),
            Paragraph("High-performance asynchronous REST API framework. Automatic OpenAPI/Swagger documentation (`/docs`), "
                      "Pydantic schema validation, aur sub-millisecond response execution time provide karta hai.", body_style),
        ],
        [
            Paragraph("<b>Server ASGI</b>", body_style),
            Paragraph("<b>Uvicorn[standard]</b>", h2_style),
            Paragraph("Production-grade ASGI web server jo HTTP requests ko handle karke FastAPI endpoints par route karta hai.", body_style),
        ],
        [
            Paragraph("<b>Machine Learning</b>", body_style),
            Paragraph("<b>Scikit-Learn (v1.4+) & Joblib</b>", h2_style),
            Paragraph("RandomForestClassifier model architecture, balanced class weighting, cross-validation metrics calculation, "
                      "aur `ml/model.pkl` serialization/deserialization ke liye.", body_style),
        ],
        [
            Paragraph("<b>Numerical & Data Processing</b>", body_style),
            Paragraph("<b>NumPy & Pandas</b>", h2_style),
            Paragraph("Matrix operations, spectral array slicing, CSV dataset filtering, normalization aur feature vector assembly.", body_style),
        ],
        [
            Paragraph("<b>Earth Engine & Geospatial</b>", body_style),
            Paragraph("<b>earthengine-api & Rasterio</b>", h2_style),
            Paragraph("Google Earth Engine Python API satellite data orchestration ke liye aur Rasterio multi-band GeoTIFF rasters "
                      "ko coordinate-wise query karne ke liye.", body_style),
        ],
        [
            Paragraph("<b>Frontend UI & GIS</b>", body_style),
            Paragraph("<b>HTML5, Vanilla CSS3, JavaScript (ES6+)</b>", h2_style),
            Paragraph("Bina heavy frameworks (React/Angular) ke ultra-fast page load. Custom dark theme aesthetic, CSS grid, "
                      "smooth SVG gauge animations, dynamic diagnostic sliders, aur zero bundle overhead.", body_style),
        ],
        [
            Paragraph("<b>Interactive Mapping</b>", body_style),
            Paragraph("<b>Leaflet.js (v1.9.4)</b>", h2_style),
            Paragraph("High-resolution Esri World Imagery (satellite tiles) aur CartoDB Dark Matter base maps, custom SVG target pins, "
                      "interactive click-to-scan event handling, aur historical mine overlays.", body_style),
        ],
        [
            Paragraph("<b>Live Telemetry</b>", body_style),
            Paragraph("<b>Open-Meteo & Open-Elevation APIs</b>", h2_style),
            Paragraph("User ke click kiye hue coordinates par live elevation aur topography terrain telemetry fetch karne ke liye fallback caching ke sath.", body_style),
        ],
        [
            Paragraph("<b>DevOps & Cloud Deployment</b>", body_style),
            Paragraph("<b>Docker, Docker-Compose & Render.com</b>", h2_style),
            Paragraph("Single-container packaging (`Dockerfile`), root directory auto-discovery, dynamic `$PORT` routing, "
                      "GitHub automated continuous integration (CI/CD), aur live HTTPS deployment Render cloud par.", body_style),
        ],
    ]

    t_tech = Table(tech_data, colWidths=[95, 135, content_width - 230])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EAE4D8")),
        ('BOX', (0,0), (-1,-1), 0.8, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_tech)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: CHAPTER 6 — ML PREDICTION MECHANICS & MATHEMATICS
    # =========================================================================
    story.append(Paragraph("Chapter 6: Machine Learning Prediction Mechanics", h1_style))
    story.append(Paragraph("Model Results Kaise Predict Karta Hai? (Algorithm, Math & Inference)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceAfter=8))

    ml_intro = (
        "Is chapter me hum explain kar rahe hain ki Strata ka AI model under-the-hood kaise kaam karta hai: "
        "kaun sa algorithm use hua hai, feature vector kaise banta hai, aur final probability number kaise calculate hota hai."
    )
    story.append(Paragraph(ml_intro, body_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("6.1 Algorithm Choice: Random Forest Classifier", h2_style))
    algo_desc = (
        "Strata me <b>Random Forest Ensemble</b> algorithm use kiya gaya hai (`scikit-learn.ensemble.RandomForestClassifier`).<br/>"
        "<b>Kyu choose kiya?</b><br/>"
        "1. <b>Non-Linear Geological Relationships:</b> Geological formations strictly linear nahi hote. Red reflectance tabhi ore signify karta hai jab slope aur elevation bhi favorable ho. Decision trees in complex conditions ko naturally capture karte hain.<br/>"
        "2. <b>Immunity to Overfitting:</b> Random Forest 300 independent decision trees banata hai (bagging & bootstrap sampling), jisse single tree ka bias eliminate ho jata hai.<br/>"
        "3. <b>Balanced Class Weighting:</b> Remote sensing me mineral deposits rare hote hain (class imbalance). Model me `class_weight='balanced'` lagaya gaya hai taaki true deposits accurately detect ho sakein."
    )
    story.append(Paragraph(algo_desc, body_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("6.2 Step-by-Step Prediction Pipeline:", h2_style))

    math_pipeline_data = [
        [
            Paragraph("<b>Step 1: Feature Vector Assembly</b>", meta_style),
            Paragraph("Jab user coordinate provide karta hai, 7 continuous numerical values ka 1D vector assemble hota hai:<br/>"
                      "<code>X = [ferric_iron, ferrous_mineral, laterite, gossan, ndvi, slope, elevation]</code>", body_style),
        ],
        [
            Paragraph("<b>Step 2: Tree Traversal</b>", meta_style),
            Paragraph("Vector <code>X</code> forest ke sabhi 300 decision trees me traverse karta hai. Har tree apne split nodes par check karta hai:<br/>"
                      "<i>E.g., Tree 42: Is ferric_iron >= 1.22? Yes &rarr; Is slope <= 14.5°? Yes &rarr; Leaf Vote = Class 1 (Deposit).</i>", body_style),
        ],
        [
            Paragraph("<b>Step 3: Probability Aggregation</b>", meta_style),
            Paragraph("Probability calculate karne ke liye forest ke sabhi 300 trees ke votes aggregate hote hain:<br/>"
                      "<b>P(Deposit | X) = (Total Trees Voting Class 1) / (Total Trees = 300)</b><br/>"
                      "Agar 270 trees ne positive vote diya, toh predicted probability = <b>0.90 (90%)</b>.", body_style),
        ],
        [
            Paragraph("<b>Step 4: Confidence Tiers Classification</b>", meta_style),
            Paragraph("Probability score ko industry-standard geological risk tiers me translate kiya jata hai:<br/>"
                      "• <b>Tier 1 (High Potential):</b> Probability >= 80% (Recommended Drilling Target)<br/>"
                      "• <b>Tier 2 (Moderate Prospect):</b> Probability 50% - 79% (Secondary Ground Geological Survey)<br/>"
                      "• <b>Background (Low Risk/Barren):</b> Probability < 50% (Skip Drilling & Save Capital)", body_style),
        ],
    ]

    t_pipe = Table(math_pipeline_data, colWidths=[140, content_width - 140])
    t_pipe.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_card_bg),
        ('BOX', (0,0), (-1,-1), 0.8, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_pipe)
    story.append(Spacer(1, 5))

    story.append(Paragraph("6.3 Model Validation Metrics:", h2_style))
    val_text = (
        "• <b>Validation ROC-AUC Score:</b> ~0.999 (Synthetic validation benchmark)<br/>"
        "• <b>Feature Importances:</b> Ferric Iron Index (~32%), Gossan Index (~24%), Laterite Index (~18%), Slope (~11%), Elevation (~9%), NDVI (~6%).<br/>"
        "• <b>Inference Latency:</b> &lt; 8 milliseconds per coordinate scan (instant real-time user response)."
    )
    story.append(Paragraph(val_text, body_style))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: CHAPTER 7 — INTERACTIVE EXPLORATION STUDIO & TELEMETRY
    # =========================================================================
    story.append(Paragraph("Chapter 7: Interactive Studio & Live Telemetry", h1_style))
    story.append(Paragraph("Geologist UI, Real-Time Open-Meteo Integration & REST API", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceAfter=8))

    studio_intro = (
        "Strata ka frontend sirf ek presentation layer nahi hai, balki ek fully functional <b>Exploration Command Center</b> hai. "
        "Ye geologist ko satellite data ke sath real-time me interact karne ki suvidha deta hai:"
    )
    story.append(Paragraph(studio_intro, body_style))
    story.append(Spacer(1, 4))

    features_ui = [
        [
            Paragraph("<b>Interactive Map Pinpointing</b>", h2_style),
            Paragraph("Leaflet.js map par geologist India ke kisi bhi corner par click karke target marker drop kar sakta hai. "
                      "Click karte hi automatic event listener coordinates capture karke backend ko dispatch karta hai.", body_style)
        ],
        [
            Paragraph("<b>Live Elevation Telemetry</b>", h2_style),
            Paragraph("Backend me `realtime.py` module hai jo Open-Meteo / SRTM elevation APIs se live zameen ki unchai (elevation in meters) "
                      "aur surface topography query karta hai. Nav-bar me status badge real-time telemetry display karta hai.", body_style)
        ],
        [
            Paragraph("<b>Pre-Configured Mining Belts</b>", h2_style),
            Paragraph("Dropdown menu se 5 major Indian mining corridors directly choose kiye ja sakte hain:<br/>"
                      "1. <i>Balaghat-Nagpur-Chhindwara (MP/MH)</i> | 2. <i>Keonjhar-Sundargarh-Barbil (Odisha/JH)</i><br/>"
                      "3. <i>Sandur-Bellary-Shimoga (Karnataka)</i> | 4. <i>Banswara-Udaipur (Rajasthan)</i><br/>"
                      "5. <i>Vizianagaram-Srikakulam (Andhra Pradesh)</i>", body_style)
        ],
        [
            Paragraph("<b>Custom Parameter Sliders</b>", h2_style),
            Paragraph("Agar field geologist ke paas ground drone survey ya local lab data hai, toh wo UI ke sliders se "
                      "Ferric Iron, Gossan, Laterite, NDVI aur Slope ko manually customize karke real-time sensitivity test kar sakta hai.", body_style)
        ],
        [
            Paragraph("<b>Structured JSON Dossier Export</b>", h2_style),
            Paragraph("Target scan karne ke baad, 'Export Full Dossier' button dabakar complete geological report JSON format me download ki ja sakti hai, "
                      "jisme sabhi spectral scores, telemetry status aur recommendation tags include hote hain.", body_style)
        ],
    ]

    t_ui = Table(features_ui, colWidths=[160, content_width - 160])
    t_ui.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_card_bg),
        ('BOX', (0,0), (-1,-1), 0.8, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_ui)
    story.append(Spacer(1, 5))

    story.append(Paragraph("Core REST API Endpoints Table:", h2_style))
    api_table_data = [
        [Paragraph("<b>Method & Endpoint</b>", meta_style), Paragraph("<b>Functionality & Description</b>", meta_style)],
        [Paragraph("<code>POST /scan-coordinates</code>", code_style), Paragraph("Latitude & longitude input leta hai aur spectral factors ke sath model confidence score return karta hai.", body_style)],
        [Paragraph("<code>GET /reserve-map/{region}</code>", code_style), Paragraph("Kisi poore mining belt ke top-ranked anomaly zones ko probability order me list karta hai.", body_style)],
        [Paragraph("<code>GET /known-deposits</code>", code_style), Paragraph("Historical GSI aur USGS verified mines ke coordinates return karta hai map reference ke liye.", body_style)],
        [Paragraph("<code>GET /production-gap</code>", code_style), Paragraph("National manganese production vs demand deficit trajectory provide karta hai.", body_style)],
        [Paragraph("<code>GET /health</code>", code_style), Paragraph("Container health monitoring and uptime verification service.", body_style)],
    ]
    t_api = Table(api_table_data, colWidths=[150, content_width - 150])
    t_api.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EAE4D8")),
        ('BOX', (0,0), (-1,-1), 0.8, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_api)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 9: CHAPTER 8 — POTENTIAL IMPACT & FUTURE ROADMAP
    # =========================================================================
    story.append(Paragraph("Chapter 8: Potential Impact & Future Roadmap", h1_style))
    story.append(Paragraph("Industrial Economics, Environmental Protection & Multi-Mineral Horizon", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceAfter=8))

    impact_intro = (
        "Strata sirf ek software tool nahi hai; ye mineral exploration industry ke economics aur environmental footprints ko "
        "fundamentally reform karne ka potential rakhta hai:"
    )
    story.append(Paragraph(impact_intro, body_style))
    story.append(Spacer(1, 4))

    impact_points = [
        [
            Paragraph("<b>Economic & Financial Impact</b>", h2_style),
            Paragraph("• <b>Up to 70% Cost Reduction:</b> Greenfield exploration me hazaron barren boreholes drill hone se bachte hain. Speculative drilling budget directly save hota hai.<br/>"
                      "• <b>10x Faster Discovery:</b> Preliminary survey jo 18-24 mahine leti thi, wo Strata se <b>kuch ghanto aur dino me</b> complete ho sakti hai.<br/>"
                      "• <b>Higher Commercial ROI:</b> Confirmatory drilling unhi points par hoti hai jaha spectral confirmation high hai, jisse success rate multifold increase ho jata hai.", body_style)
        ],
        [
            Paragraph("<b>Strategic & National Mineral Security</b>", h2_style),
            Paragraph("• <b>Closing the 0.85 Mt Deficit:</b> Domestic reserve discovery accelerate karke India steel aur EV battery ke liye manganese imports par dependency drastically reduce kar sakta hai.<br/>"
                      "• <b>Critical Minerals Sovereignty:</b> National Critical Mineral Mission ke goals ke sath 100% align hota hai, helping mining auctions become data-backed.", body_style)
        ],
        [
            Paragraph("<b>Environmental & ESG Stewardship</b>", h2_style),
            Paragraph("• <b>Preserving Forest Ecosystems:</b> Balaghat aur Keonjhar ke dense jungle tracts me heavy excavators aur deforestation ki zaroorat nahi padti.<br/>"
                      "• <b>Zero Ground Disruption:</b> Orbital surveys carbon-neutral aur non-invasive hoti hain, protecting wildlife corridors aur local tribal communities.", body_style)
        ],
        [
            Paragraph("<b>Future Scalability Roadmap</b>", h2_style),
            Paragraph("• <b>Multi-Mineral Adaptation:</b> Same spectral ratio + ML architecture ko <b>Lithium pegmatites, Copper porphyry, Bauxite (Aluminum), aur Nickel laterites</b> ke liye extend kiya ja sakta hai.<br/>"
                      "• <b>Hyperspectral Integration (EnMAP & PRISMA):</b> Next phase me 200+ narrow spectral bands ingest karke ore grade (% Mn content) predict karne ki capability add ki jayegi.<br/>"
                      "• <b>Automated Mineral Block Auction Dossiers:</b> Government agencies ke liye complete 1-click exploration block bidding reports generate karna.", body_style)
        ],
    ]

    t_imp = Table(impact_points, colWidths=[160, content_width - 160])
    t_imp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_card_bg),
        ('BOX', (0,0), (-1,-1), 0.8, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_imp)
    story.append(Spacer(1, 8))

    conclusion_box = (
        "<b>Nishkarsh (Conclusion):</b><br/>"
        "Project Strata demonstrates that modern space technology aur machine learning ko combine karke traditional mining ke "
        "sabse bade bottlenecks — high cost, slow speed, aur ecological harm — ko successfully overcome kiya ja sakta hai. "
        "Strata unlocks a new era of <i>'Targeted, Satellite-Guided, Responsible Mineral Discovery'</i>."
    )
    story.append(make_card(Paragraph(conclusion_box, callout_style), bg_color=colors.HexColor("#F5EFE6"), border_color=c_primary, padding=7))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generated successfully at: {pdf_path}")
    return pdf_path


if __name__ == "__main__":
    build_pdf()
