# -*- coding: utf-8 -*-
"""Project declaration, Campus Explorer: same layout as the SAE report
(cover page with logo and info table, header/footer, TOC, numbered headings)."""
import os
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

LOGO = r"D:\All\Licence_Cergy\Semestre_5\05_SAE_BD_Reseau\rapport\logo_cy.png"
OUT = r"D:\All\Licence_Cergy\Semestre_5\07_Mineure_Mobile_Computing\Campus_Explorer_Project_Declaration.docx"
GRIS = RGBColor(0x60, 0x60, 0x60)
BLEU = RGBColor(0x1F, 0x3A, 0x5F)
A_COMPLETER = "[to complete]"


def champ(p, instruction, provisoire="1"):
    for kind, val in (("begin", None), ("instr", instruction), ("separate", None),
                      ("text", provisoire), ("end", None)):
        r = OxmlElement("w:r")
        if kind == "instr":
            t = OxmlElement("w:instrText"); t.set(qn("xml:space"), "preserve"); t.text = val
        elif kind == "text":
            t = OxmlElement("w:t"); t.text = val
        else:
            t = OxmlElement("w:fldChar"); t.set(qn("w:fldCharType"), kind)
        r.append(t)
        p._p.append(r)


def filet(p, cote="bottom", couleur="BFBFBF"):
    pPr = p._p.get_or_add_pPr()
    b = OxmlElement("w:pBdr")
    e = OxmlElement("w:" + cote)
    for k, v in (("val", "single"), ("sz", "6"), ("space", "6"), ("color", couleur)):
        e.set(qn("w:" + k), v)
    b.append(e)
    pPr.insert_element_before(b, "w:shd", "w:tabs", "w:suppressAutoHyphens", "w:spacing",
                              "w:ind", "w:jc", "w:rPr", "w:sectPr", "w:pPrChange")


def tab_droite(p, section):
    largeur = section.page_width - section.left_margin - section.right_margin
    ts = p.paragraph_format.tab_stops
    ts.add_tab_stop(Cm(8.25), WD_TAB_ALIGNMENT.CLEAR)   # tabulations du style Header/Footer
    ts.add_tab_stop(Cm(16.5), WD_TAB_ALIGNMENT.CLEAR)
    ts.add_tab_stop(largeur, WD_TAB_ALIGNMENT.RIGHT)


def ombre(cellule, couleur="E8EEF5"):
    tcPr = cellule._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), couleur)
    tcPr.append(shd)


def tableau(doc, entetes, lignes, largeurs):
    t = doc.add_table(rows=1, cols=len(entetes))
    t.style = "Table Grid"
    t.autofit = False
    for i, h in enumerate(entetes):
        c = t.rows[0].cells[i]
        c.width = Cm(largeurs[i])
        r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(10.5)
        ombre(c)
    for ligne in lignes:
        cells = t.add_row().cells
        for i, v in enumerate(ligne):
            cells[i].width = Cm(largeurs[i])
            paras = v if isinstance(v, list) else [v]
            for k, texte in enumerate(paras):
                p = cells[i].paragraphs[0] if k == 0 else cells[i].add_paragraph()
                if isinstance(v, list):
                    texte = "\u2022 " + texte
                p.paragraph_format.space_after = Pt(1)
                r = p.add_run(texte); r.font.size = Pt(10.5)
                if i == 0 and not isinstance(v, list):
                    r.bold = True
    # une ligne ne se coupe jamais, et le tableau reste sur une seule page
    for k, row in enumerate(t.rows):
        trPr = row._tr.get_or_add_trPr()
        cs = OxmlElement("w:cantSplit"); trPr.append(cs)
        if k == 0:
            th = OxmlElement("w:tblHeader"); trPr.append(th)
        if k < len(t.rows) - 1:
            for c in row.cells:
                for pp in c.paragraphs:
                    pp.paragraph_format.keep_with_next = True
    doc.add_paragraph()
    return t


FIG = os.path.join(os.path.dirname(OUT), "figures_declaration")


def figure(doc, png, legende, largeur=16.0):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(os.path.join(FIG, png), width=Cm(largeur))
    c = doc.add_paragraph(style="Caption"); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.add_run("Figure ")
    champ(c, r" SEQ Figure \* ARABIC ", "1")
    c.add_run(": " + legende)


def puces(doc, items):
    for it in items:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(it)


def para(doc, texte):
    return doc.add_paragraph(texte)


def main():
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Calibri"; st.font.size = Pt(11)
    st.paragraph_format.space_after = Pt(6)
    for niveau, taille in ((1, 16), (2, 13)):
        h = doc.styles["Heading %d" % niveau]
        h.font.name = "Calibri"; h.font.size = Pt(taille); h.font.color.rgb = BLEU
    sec = doc.sections[0]
    sec.page_width = Cm(21.0); sec.page_height = Cm(29.7)
    sec.top_margin = Cm(2.2); sec.bottom_margin = Cm(2.0)
    sec.left_margin = Cm(2.5); sec.right_margin = Cm(2.5)
    sec.different_first_page_header_footer = True

    # header / footer (not on the cover page)
    p = sec.header.paragraphs[0]; tab_droite(p, sec)
    p.add_run().add_picture(LOGO, width=Cm(2.6)); p.add_run("\t")
    r = p.add_run("Campus Explorer \u00b7 Project declaration"); r.font.size = Pt(9); r.font.color.rgb = GRIS
    filet(p, "bottom")
    p = sec.footer.paragraphs[0]; tab_droite(p, sec)
    p.add_run("Licence 3 Informatique \u00b7 Mobile Computing\t")
    champ(p, " PAGE "); p.add_run(" / "); champ(p, " NUMPAGES ")
    for r in p.runs:
        r.font.size = Pt(9); r.font.color.rgb = GRIS
    filet(p, "top")

    # ------------------------------------------------------------ cover page
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(LOGO, width=Cm(6))
    doc.add_paragraph(); doc.add_paragraph()
    for texte, taille, gras in (("Mobile Computing \u00b7 Class project", 14, True),
                                ("Campus Explorer", 30, True),
                                ("A location-based Android application", 14, False),
                                ("Project declaration", 13, False)):
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(texte); r.bold = gras; r.font.size = Pt(taille)
        if taille == 30:
            r.font.color.rgb = BLEU
    for _ in range(3):
        doc.add_paragraph()
    infos = [
        ("Team", "GANDONOU Koffi Patrick-L\u00e9on\nASMA " + A_COMPLETER),
        ("Programme", "Licence 3 Informatique, CY Cergy Paris Universit\u00e9"),
        ("Course", "Mobile Computing (minor)"),
        ("Instructor", A_COMPLETER),
        ("Academic year", "2026-2027"),
        ("Date", "22 October 2026"),
    ]
    t = doc.add_table(rows=0, cols=2); t.style = "Table Grid"; t.autofit = False
    t.alignment = 1
    for k, v in infos:
        c = t.add_row().cells
        c[0].width = Cm(4.5); c[1].width = Cm(10.5)
        r = c[0].paragraphs[0].add_run(k); r.bold = True
        ombre(c[0])
        lignes = v.split("\n")
        for i, l in enumerate(lignes):
            pp = c[1].paragraphs[0] if i == 0 else c[1].add_paragraph()
            rr = pp.add_run(l)
            if A_COMPLETER in l:
                rr.font.color.rgb = RGBColor(0xB0, 0x30, 0x30)
    doc.add_page_break()

    # ------------------------------------------------------------ contents
    p = doc.add_paragraph()
    r = p.add_run("Contents"); r.bold = True; r.font.size = Pt(16); r.font.color.rgb = BLEU
    champ(doc.add_paragraph(), r' TOC \o "1-2" \h \z \u ', "Right-click and choose Update Field")
    doc.add_page_break()

    # ------------------------------------------------------------ body
    doc.add_heading("1. Project overview", level=1)
    para(doc, "Campus Explorer is an Android application that helps students find their way around a "
              "university campus: lecture buildings, libraries, cafeterias and study areas.")
    para(doc, "The application shows a campus map with a few points of interest, displays the user's "
              "position, and can record a walk as a tracking session. A phone sensor adds one simple "
              "interactive feature.")
    para(doc, "We build it in Java with XML layouts in Android Studio. The map uses OpenStreetMap data, "
              "displayed with Leaflet.js inside an Android WebView. The project covers the main topics of "
              "the course: Activities, Intents, the Activity lifecycle, a background service, a sensor, "
              "location services and user interface design.")

    doc.add_heading("2. Problem and motivation", level=1)
    para(doc, "New students often do not know where buildings and services are on campus. Campus Explorer "
              "gives them a simple map with a short list of useful places.")
    para(doc, "We do not build a full navigation system. The application shows campus points of interest "
              "and lets users follow their position while they walk. We keep the scope small so that the "
              "application works reliably by the deadline.")

    doc.add_heading("3. Main objectives", level=1)
    puces(doc, [
        "Display a campus map with predefined points of interest.",
        "Show basic information about a selected place.",
        "Display the user's current location once permission is granted.",
        "Start and stop a location-tracking session.",
        "Use a device sensor for one interactive feature.",
        "Manage the Activity lifecycle correctly and navigate between screens.",
        "Keep a tracking session running in a background service when the app is no longer visible, "
        "only if the user started it.",
        "Follow our Figma mockup for a simple and consistent interface.",
    ])

    doc.add_heading("4. Screens and Activities", level=1)
    para(doc, "The application has three Activities, which meets the project requirement.").paragraph_format.keep_with_next = True
    tableau(doc, ["Activity", "Role", "Main elements"], [
        ("1. Home", "Entry point of the application",
         ["application name and short description", "button to open the map",
          "button to open saved places and history"]),
        ("2. Campus map", "OpenStreetMap map displayed with Leaflet.js",
         ["map centred on the campus", "markers for the predefined places, with name and description",
          "button to show the current location", "start and stop buttons for tracking"]),
        ("3. Saved places and history", "List of saved places and recent tracking sessions",
         ["select a place to return to the map", "data stored locally on the phone"]),
    ], [3.2, 4.3, 8.5])
    para(doc, "The first version uses predefined places stored in the application. It has no user "
              "accounts, no cloud synchronisation and no remote database.")
    para(doc, "Figure 1 shows how the user moves between the three screens.")
    figure(doc, "fig1_navigation.png", "Navigation between the three Activities", 15.0)

    doc.add_heading("5. Android components and course concepts", level=1)
    para(doc, "Figure 2 shows the components of the application and the data that flows between them. "
              "The table below links each one to a topic of the course.")
    figure(doc, "fig2_architecture.png", "Application architecture: components and data flows")
    tableau(doc, ["Course concept", "How Campus Explorer uses it"], [
        ("Activities and Intents", "Three Activities, one per screen. Explicit Intents for navigation; "
                                   "the identifier of a selected place is passed as an Intent extra."),
        ("Activity lifecycle", "onCreate(), onResume(), onPause() and onStop() are implemented and tested. "
                               "The map screen stops its sensor listener and UI location updates in "
                               "onPause() and refreshes its state in onResume()."),
        ("Background service", "A foreground service records location updates during a tracking session, "
                               "even when the user switches app or turns off the screen."),
        ("Sensor", "Accelerometer through SensorManager: shaking the phone bookmarks the current position."),
        ("Location and maps", "Android location APIs with runtime permission; OpenStreetMap tiles shown "
                              "with Leaflet.js in a WebView."),
        ("Local data", "Predefined places in the app; saved places and session summaries in "
                       "SharedPreferences or SQLite."),
    ], [4.0, 12.0])

    doc.add_heading("5.1 Background service", level=2)
    para(doc, "The user starts and stops tracking explicitly. While a session is active, the service shows "
              "a persistent notification with the session status and a Stop action. When the session ends, "
              "the service stops location updates and releases its resources.")
    figure(doc, "fig3_tracking.png", "A tracking session, from Start to Stop", 15.5)
    para(doc, "The service follows Android's rules for foreground services and location permissions, and "
              "never runs when no session is active. Its lifecycle is independent of the map Activity: "
              "leaving the map screen does not stop a session the user started.")

    doc.add_heading("5.2 Sensor", level=2)
    para(doc, "During an active session, shaking the phone marks the current position as a bookmark. The "
              "listener is registered only while the map screen or a session is active, and unregistered "
              "as soon as it is no longer needed.")
    para(doc, "Fallback: if shake detection does not work reliably, the screen will show basic movement "
              "information from the accelerometer instead. A manual bookmark button stays available in "
              "both cases.")

    doc.add_heading("5.3 Location and maps", level=2)
    para(doc, "Location permission is requested only when the user needs it. If permission is denied or "
              "location is unavailable, the map still shows the predefined campus places.")

    doc.add_heading("6. Technical choices", level=1)
    tableau(doc, ["Component", "Choice"], [
        ("Language", "Java"),
        ("Development environment", "Android Studio"),
        ("Interface", "XML layouts and standard Android Views"),
        ("Navigation", "Activities and explicit Intents"),
        ("Map", "OpenStreetMap tiles displayed with Leaflet.js in a WebView"),
        ("Location", "Android location APIs and runtime permissions"),
        ("Background work", "Foreground service, started by the user, for active tracking"),
        ("Sensor", "Accelerometer through SensorManager"),
        ("Local storage", "Predefined data; SharedPreferences or SQLite for saved places and sessions"),
    ], [5.0, 11.0])
    para(doc, "Map tiles need an internet connection. Without one, the application shows a message and "
              "keeps working with the list of places.")

    doc.add_heading("7. Privacy and permissions", level=1)
    puces(doc, [
        "Location permission is requested when the user opens a feature that needs it, with a short "
        "explanation of why.",
        "Background tracking starts only after a user action and is always shown by a notification. "
        "The user can stop it at any time.",
        "Location data stays on the phone. No account, no personal data, nothing sent to a server.",
        "A denied permission or a missing sensor never makes the application crash.",
    ])

    doc.add_heading("8. Development plan", level=1)
    tableau(doc, ["Phase", "Tasks"], [
        ("1. Design and setup", ["finalise the Figma mockup", "create the Android Studio project",
                                 "build the three Activities and their XML layouts",
                                 "navigation with Intents"]),
        ("2. Map and location", ["display the campus map", "add the predefined points of interest",
                                 "request location permission and show the user's position"]),
        ("3. Sensor and tracking", ["accelerometer feature", "tracking service and its notification",
                                    "start and stop controls"]),
        ("4. Testing and documentation", ["Activity transitions and lifecycle callbacks",
                                          "denied permission, no location, no sensor",
                                          "tracking while the screen is off",
                                          "README, code reuse notes, demonstration"]),
    ], [4.5, 11.5])

    doc.add_heading("9. Expected results", level=1)
    para(doc, "The final application will show a working campus map, navigation between three Activities, "
              "location access, one sensor and a background tracking service, with correct lifecycle "
              "management, permission handling and resource cleanup.")
    para(doc, "We will give priority to these core features working reliably rather than adding many "
              "optional ones.")

    doc.add_heading("10. Code reuse and references", level=1)
    para(doc, "We may use external libraries, mainly for the map. Any reused or adapted code will be listed "
              "in the final report with a link to its source. Reused code will stay below the project limit "
              "of about 50% of the total code, and both of us will be able to explain every part.")
    para(doc, "The final repository will contain the source code with comments and a README describing the "
              "Activities, Intents, background service, sensor, permissions and external libraries.")

    doc.save(OUT)
    print("OK", OUT)


if __name__ == "__main__":
    main()
