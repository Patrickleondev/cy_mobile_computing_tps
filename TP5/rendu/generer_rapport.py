# Génère le rapport du TP5 (Word, A4) à partir des captures de TP5_captures.
# Ensuite : python theme_word.py, harmoniser_word.ps1 (styles de Normal.dotm), puis export PDF par Word.
import pathlib

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ICI = pathlib.Path(__file__).parent
CAPTURES = ICI.parent / "TP5_captures"
SORTIE = ICI / "Rapport_TP5_GANDONOU.docx"
BLEU = RGBColor(0x1F, 0x4E, 0x79)
GRIS = RGBColor(0x59, 0x59, 0x59)

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.2)
sec.top_margin, sec.bottom_margin = Cm(2.2), Cm(2)
sec.different_first_page_header_footer = True


def ombrer(cellule, couleur):
    tc = cellule._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), couleur)
    tc.append(shd)


def sans_bordures(table):
    tblPr = table._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for cote in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{cote}")
        e.set(qn("w:val"), "nil")
        b.append(e)
    tblPr.append(b)


def champ(paragraphe, code):
    """Champ Word (PAGE, NUMPAGES) : le numéro est calculé par Word."""
    r = paragraphe.add_run()
    for typ, txt in (("begin", None), (None, code), ("end", None)):
        if typ:
            e = OxmlElement("w:fldChar")
            e.set(qn("w:fldCharType"), typ)
        else:
            e = OxmlElement("w:instrText")
            e.set(qn("xml:space"), "preserve")
            e.text = txt
        r._r.append(e)
    return r


def texte(p, t, gras=False, taille=None, couleur=None, italique=False):
    r = p.add_run(t)
    r.bold, r.italic = gras, italique
    if taille:
        r.font.size = Pt(taille)
    if couleur:
        r.font.color.rgb = couleur
    return r


# ---------- en-tête et pied des pages 2 et suivantes ----------
h = sec.header.paragraphs[0]
h.paragraph_format.tab_stops.add_tab_stop(Cm(16.6), WD_TAB_ALIGNMENT.RIGHT)
texte(h, "Mobile Computing · TP5 Multimedia", taille=9, couleur=GRIS)
texte(h, "\tPatrick-Léon GANDONOU · L3 Informatique", taille=9, couleur=GRIS)
for f in (sec.footer, sec.first_page_footer):
    p = f.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    texte(p, "Page ", taille=9, couleur=GRIS)
    champ(p, "PAGE").font.size = Pt(9)
    texte(p, " / ", taille=9, couleur=GRIS)
    champ(p, "NUMPAGES").font.size = Pt(9)

# ---------- bandeau de la première page ----------
bandeau = doc.add_table(rows=1, cols=2)
sans_bordures(bandeau)
bandeau.alignment = WD_TABLE_ALIGNMENT.CENTER
g, d = bandeau.rows[0].cells
for c in (g, d):
    ombrer(c, "1F4E79")
g.width, d.width = Cm(10.3), Cm(6.3)
p = g.paragraphs[0]
texte(p, "CY Cergy Paris Université", gras=True, taille=12, couleur=RGBColor(0xFF, 0xFF, 0xFF))
p = g.add_paragraph()
texte(p, "Licence 3 Informatique · Mineure Mobile Computing", taille=10, couleur=RGBColor(0xDD, 0xE8, 0xF3))
p = d.paragraphs[0]
p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
texte(p, "TP5 · Multimedia", gras=True, taille=12, couleur=RGBColor(0xFF, 0xFF, 0xFF))
p = d.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
texte(p, "Année 2026-2027", taille=10, couleur=RGBColor(0xDD, 0xE8, 0xF3))

doc.add_paragraph()
t = doc.add_paragraph(style="Title")
t.add_run("TP5: Capturing Photos and Videos")
st = doc.add_paragraph(style="Subtitle")
st.add_run("Adding pictures and videos to the events of the application")

infos = doc.add_table(rows=0, cols=2)
infos.style = "Light List Accent 1"
for k, v in (
    ("Student", "Patrick-Léon GANDONOU"),
    ("Project", "TP5Photos (Android Studio, Java), built on my TP4 application"),
    ("Application id / package", "com.cyu.tp5photos / com.cyu.tp1intents"),
    ("SDK", "minSdk 24, targetSdk 37"),
    ("Tested on", "Android Studio emulator, Medium Phone, API 37, 20 November 2026"),
):
    r = infos.add_row().cells
    r[0].text, r[1].text = k, v
    r[0].paragraphs[0].runs[0].bold = True
    r[0].width, r[1].width = Cm(4.6), Cm(12)

doc.add_paragraph()


# ---------- contenu ----------
def titre(t, niveau=1):
    doc.add_heading(t, level=niveau)


def para(t):
    return doc.add_paragraph(t)


def puces(lignes):
    for l in lignes:
        doc.add_paragraph(l, style="List Bullet")


def code(lignes):
    tab = doc.add_table(rows=1, cols=1)
    sans_bordures(tab)
    c = tab.rows[0].cells[0]
    ombrer(c, "F2F2F2")
    p = c.paragraphs[0]
    r = p.add_run("\n".join(lignes))
    r.font.name = "Consolas"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
    r.font.size = Pt(8.5)
    doc.add_paragraph()


n_fig = [0]


def figure(nom, legende, largeur=16):
    doc.add_picture(str(CAPTURES / nom), width=Cm(largeur))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    n_fig[0] += 1
    p = doc.add_paragraph(style="Caption")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run(f"Figure {n_fig[0]}: {legende}")


titre("1. Overview")
para("This TP extends my TP4 application (list of events, event screen with its address, "
     "calls and SMS). When the user adds an event, there is now one more step: taking a picture "
     "(and, for the bonus, a video). The picture is shown in the event screen, and a new screen "
     "shows every picture taken by the application.")
puces([
    "AddEventActivity: a preview and the buttons TAKE A PHOTO and FILM (bonus).",
    "EventActivity: the photo (ImageView) and the video (VideoView) among the other details.",
    "GalleryActivity: a grid with all the pictures taken by the application.",
    "Medias: a small class shared by the three screens (create the file, give its address, read a reduced image).",
])

titre("2. Capturing photos")
titre("2.1 Where the pictures are stored", 2)
para("The application does not drive the camera itself: it asks the Camera application to take "
     "the picture, with ActivityResultContracts.TakePicture. Before that, it creates an empty file "
     "in its own folder on the external storage, getExternalFilesDir(Environment.DIRECTORY_PICTURES). "
     "I chose this folder because it needs no runtime permission since Android 4.4, and the gallery "
     "only has to list one folder.")
para("The Camera application is another app and cannot write in my folder. Since Android 7 (my "
     "minSdk is 24), giving it a file:// URI throws FileUriExposedException. So the file is shared "
     "through a FileProvider, which gives a content:// URI and a temporary write permission on this "
     "file only.")
code([
    '<provider',
    '    android:name="androidx.core.content.FileProvider"',
    '    android:authorities="${applicationId}.fileprovider"',
    '    android:exported="false"',
    '    android:grantUriPermissions="true">',
    '    <meta-data android:name="android.support.FILE_PROVIDER_PATHS"',
    '        android:resource="@xml/file_paths" />',
    '</provider>',
])

titre("2.2 Permissions", 2)
puces([
    "uses-feature android.hardware.camera, required=\"true\", as given in the subject.",
    "WRITE_EXTERNAL_STORAGE with maxSdkVersion=\"18\": it is only needed before Android 4.4 for "
    "the app folder, so it is limited to those versions.",
    "No CAMERA permission: the Camera application uses the camera, not mine. If CAMERA is declared "
    "but not granted, Android refuses to start the camera intent (SecurityException).",
])

titre("2.3 The extra step in the form", 2)
para("The launcher is declared as a field, because registerForActivityResult must be called "
     "before the activity starts. It receives the content:// URI and returns true when the picture "
     "was taken. If the user cancels, the empty file is deleted.")
code([
    "private final ActivityResultLauncher<Uri> prendrePhoto =",
    "        registerForActivityResult(new ActivityResultContracts.TakePicture(), reussi -> {",
    "            if (reussi) {",
    "                cheminPhoto = cheminPhotoEnCours;",
    "                montrerApercu();",
    "            } else {",
    "                new File(cheminPhotoEnCours).delete();",
    "            }",
    "        });",
])
para("The path of the picture is saved in a new PHOTO column of the database (version 2, and "
     "version 3 with VIDEO for the bonus). onUpgrade adds the columns with ALTER TABLE instead of "
     "dropping the table, so the events already created are kept.")
figure("1_prendre_photo.png", "the form, the Camera application, the confirmation, then the preview in the form")

titre("2.4 Keeping the picture when the screen is recreated", 2)
para("While the Camera application is open, Android may destroy the form, for example when the "
     "phone is rotated. The new activity has all its fields set to null, so the picture is on the "
     "disk but the form does not know where. I save both paths in onSaveInstanceState and read them "
     "back in onCreate. I checked it on the emulator: without this code, the preview stays grey "
     "after a rotation; with it, the preview is shown.")
figure("4_rotation_sans_et_avec.png", "rotation during the capture, without onSaveInstanceState (top) and with it (bottom)", 14)

titre("3. Displaying the picture in the event")
para("ThirdActivity passes the path of the picture in the Intent (EXTRA_PHOTO). EventActivity reads "
     "it and shows a reduced copy in an ImageView. The ImageView is gone by default, so the 15 "
     "downloaded events, which have no picture, keep the same screen as before.")
para("A photo of 12 megapixels takes 48 MB once decoded. Medias.chargerReduite reads the file "
     "twice: first only its size (inJustDecodeBounds), then the pixels with inSampleSize, which keeps "
     "one pixel out of 2, 4 or 8. It also rotates the picture with the angle written in its EXIF data.")

titre("4. The gallery")
para("GalleryActivity lists the files of the pictures folder, the most recent first, and shows "
     "them in a GridView with 3 columns. I list the folder rather than the database because the "
     "subject asks for all the pictures taken by the application, including one taken in a form "
     "that was not saved. The adapter extends ArrayAdapter<File> and overrides getView to build an "
     "ImageView, reusing the views that leave the screen.")
figure("2_galerie.png", "the PHOTOS button, the empty gallery, the gallery with 6 pictures")

titre("5. Bonus: capturing videos")
para("The video works like the photo: ActivityResultContracts.CaptureVideo writes into a .mp4 file "
     "of getExternalFilesDir(Environment.DIRECTORY_MOVIES), shared by the same FileProvider (a second "
     "external-files-path entry). EventActivity plays it in a VideoView with a MediaController. "
     "seekTo(1) shows the first frame, otherwise the VideoView stays black.")
figure("3_ecran_evenement.png", "the event with its photo and its video, then the video controls", 12)
figure("5_video_et_annulation.png", "recording a video, confirming it, and a cancelled photo")

titre("6. Tests")
tab = doc.add_table(rows=1, cols=2)
tab.style = "Light List Accent 1"
tab.rows[0].cells[0].text, tab.rows[0].cells[1].text = "Test", "Result"
for a, b in (
    ("Take a photo from the form", "preview shown, .jpg file in files/Pictures"),
    ("Save the event, open it", "photo shown under the coordinates"),
    ("Open a downloaded event", "no photo, no empty space"),
    ("Cancel a photo", "Toast « Photo annulee », empty file deleted"),
    ("Rotate the phone during the capture", "preview kept (onSaveInstanceState)"),
    ("Gallery before and after", "« Aucune photo », then the grid of pictures"),
    ("Bonus: film 2 seconds", "Toast « Video enregistree », video played in the event"),
):
    r = tab.add_row().cells
    r[0].text, r[1].text = a, b

doc.save(SORTIE)
print("ok", SORTIE)
