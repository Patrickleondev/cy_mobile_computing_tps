# -*- coding: utf-8 -*-
"""Diagrammes de la déclaration Campus Explorer (même rendu que la SAE : SVG -> PNG par Edge).
Largeur 860 px imprimée sur 16 cm : 1 px = 0,53 pt ; police de 18 px = 9,5 pt."""
import math
import os
import sys

sys.path.insert(0, r"D:\All\Licence_Cergy\Semestre_5\05_SAE_BD_Reseau\rapport")
from generer_figures_v4 import rendre, esc, POLICE, MONO  # noqa: E402

SORTIE = r"D:\All\Licence_Cergy\Semestre_5\07_Mineure_Mobile_Computing\figures_declaration"
L = 860


def svg(s, h):
    return '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d">' % (L, h) + "\n".join(s) + "</svg>"


def boite(s, x, y, l, h, lignes, fond, bord="#333", rx=8):
    s.append('<rect x="%d" y="%d" width="%d" height="%d" rx="%d" fill="%s" stroke="%s" stroke-width="1.5"/>'
             % (x, y, l, h, rx, fond, bord))
    y0 = y + h / 2 - 11 * (len(lignes) - 1) + 6
    for i, (t, style) in enumerate(lignes):
        attrs = {"titre": ' font-weight="bold" font-size="19"', "": ' font-size="17"',
                 "code": ' font-size="16" fill="#1f4e79"'}[style]
        police = MONO if style == "code" else POLICE
        s.append('<text x="%d" y="%d" font-family="%s"%s text-anchor="middle">%s</text>'
                 % (x + l / 2, y0 + 22 * i, police, attrs, esc(t)))


def fleche(s, pts, texte="", couleur="#1f4e79", pos=None, tirets=False, ancre="middle"):
    d = ' stroke-dasharray="7,5"' if tirets else ""
    s.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"%s/>'
             % (" ".join("%d,%d" % p for p in pts), couleur, d))
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    a = math.atan2(y2 - y1, x2 - x1)
    tri = [(x2, y2), (x2 - 13 * math.cos(a) + 6 * math.sin(a), y2 - 13 * math.sin(a) - 6 * math.cos(a)),
           (x2 - 13 * math.cos(a) - 6 * math.sin(a), y2 - 13 * math.sin(a) + 6 * math.cos(a))]
    s.append('<polygon points="%s" fill="%s"/>' % (" ".join("%.0f,%.0f" % p for p in tri), couleur))
    if texte:
        x, y = pos
        for i, l in enumerate(texte.split("\n")):
            s.append('<text x="%d" y="%d" font-family="%s" font-size="16" fill="%s" text-anchor="%s" '
                     'stroke="#fff" stroke-width="5" paint-order="stroke">%s</text>'
                     % (x, y + 19 * i, POLICE, couleur, ancre, esc(l)))


def police(t):
    """Chasse fixe seulement pour un appel de méthode Android (« startForeground(...) »)."""
    return MONO if "(" in t and t.split("(")[0].isidentifier() else POLICE


def titre(s, t):
    s.append('<text x="10" y="28" font-family="%s" font-size="21" font-weight="bold">%s</text>' % (POLICE, esc(t)))


# ------------------------------------------------------------------ 1. navigation
def navigation():
    s = []
    titre(s, "Navigation between the three Activities")
    boite(s, 20, 150, 220, 100, [("HomeActivity", "titre"), ("entry point", ""), ("(launcher)", "")], "#dae8fc")
    boite(s, 620, 60, 220, 100, [("MapActivity", "titre"), ("campus map, location,", ""), ("tracking controls", "")], "#d5e8d4")
    boite(s, 620, 250, 220, 100, [("SavedActivity", "titre"), ("saved places and", ""), ("session history", "")], "#ffe6cc")
    fleche(s, [(240, 180), (430, 180), (430, 110), (620, 110)], "explicit Intent", pos=(430, 96))
    fleche(s, [(240, 220), (430, 220), (430, 300), (620, 300)], "explicit Intent", pos=(430, 330))
    fleche(s, [(680, 250), (680, 160)], "Intent + extra\n\"placeId\"", couleur="#7f6000", pos=(668, 196), ancre="end")
    fleche(s, [(790, 160), (790, 250)], "", couleur="#888", tirets=True)
    s.append('<text x="800" y="210" font-family="%s" font-size="15" fill="#666">Back</text>' % POLICE)
    s.append('<text x="10" y="395" font-family="%s" font-size="16" fill="#444">'
             'The Back button returns to the previous Activity (dashed arrow). '
             'Only a place identifier travels between screens.</text>' % POLICE)
    rendre(svg(s, 410), L, 410, os.path.join(SORTIE, "fig1_navigation.png"))


# ------------------------------------------------------------------ 2. architecture
def architecture():
    s = []
    titre(s, "Application architecture: components and data flows")

    def zone(x, y, l, h, t):
        s.append('<rect x="%d" y="%d" width="%d" height="%d" rx="14" fill="#f7f7f7" stroke="#999" stroke-dasharray="6,4"/>'
                 % (x, y, l, h))
        s.append('<text x="%d" y="%d" font-family="%s" font-size="16" font-weight="bold" fill="#555">%s</text>'
                 % (x + 12, y + 22, POLICE, esc(t)))

    zone(10, 45, 840, 140, "Screens (Activities, XML layouts)")
    zone(350, 225, 500, 140, "Android framework services")
    zone(10, 435, 400, 105, "Stored on the phone")
    zone(450, 435, 400, 105, "Internet")
    boite(s, 30, 80, 150, 85, [("Home", "titre"), ("Activity", "")], "#dae8fc")
    boite(s, 195, 80, 150, 85, [("Saved", "titre"), ("Activity", "")], "#ffe6cc")
    boite(s, 360, 80, 470, 85, [("MapActivity", "titre"), ("WebView + Leaflet.js", "")], "#d5e8d4")
    boite(s, 360, 260, 180, 90, [("TrackingService", "titre"), ("foreground service", ""), ("+ notification", "")], "#e1d5e7")
    boite(s, 555, 260, 140, 90, [("Location", "titre"), ("APIs", "")], "#ffffff")
    boite(s, 710, 260, 130, 90, [("Sensors", "titre"), ("SensorManager", "")], "#ffffff")
    boite(s, 30, 465, 360, 60, [("SharedPreferences / SQLite", "titre"), ("places, bookmarks, sessions", "")], "#fff2cc")
    boite(s, 470, 465, 360, 60, [("OpenStreetMap tile server", "titre"), ("map tiles", "")], "#ffffff")
    fleche(s, [(450, 165), (450, 260)], "start / stop", pos=(460, 222), ancre="start")
    fleche(s, [(625, 165), (625, 260)])
    fleche(s, [(775, 165), (775, 260)], "accelerometer", pos=(765, 222), ancre="end")
    fleche(s, [(625, 350), (625, 395), (470, 395), (470, 350)], "location updates", couleur="#7f6000", pos=(548, 388))
    fleche(s, [(390, 350), (390, 420), (300, 420), (300, 465)], "save points", couleur="#7f6000", pos=(398, 412), ancre="start")
    fleche(s, [(270, 165), (270, 465)], "read", couleur="#7f6000", pos=(260, 320), ancre="end")
    fleche(s, [(830, 140), (852, 140), (852, 425), (700, 425), (700, 465)], "tiles (HTTPS)", pos=(842, 455), ancre="end")
    rendre(svg(s, 555), L, 555, os.path.join(SORTIE, "fig2_architecture.png"))


# ------------------------------------------------------------------ 3. tracking session
def tracking():
    s = []
    titre(s, "A tracking session, from Start to Stop")
    acteurs = [("User", 60, 100), ("MapActivity", 210, 150), ("TrackingService", 420, 170),
               ("Location APIs", 620, 150), ("Storage", 785, 110)]
    for nom, x, larg in acteurs:
        boite(s, x - larg // 2, 45, larg, 40, [(nom, "titre")], "#dae8fc" if nom == "User" else "#ffffff")
        s.append('<line x1="%d" y1="85" x2="%d" y2="640" stroke="#aaa" stroke-dasharray="5,4"/>' % (x, x))
    X = {n: x for n, x, _ in acteurs}
    y = 120
    etapes = [
        ("User", "MapActivity", "taps Start"),
        ("MapActivity", "MapActivity", "location permission granted? (asks if not)"),
        ("MapActivity", "TrackingService", "startForegroundService(intent)"),
        ("TrackingService", "TrackingService", "startForeground(notification)"),
        ("TrackingService", "Location APIs", "requestLocationUpdates()"),
        ("Location APIs", "TrackingService", "new position (repeats)"),
        ("TrackingService", "Storage", "save point"),
        ("User", "TrackingService", "taps Stop (app or notification)"),
        ("TrackingService", "Location APIs", "removeLocationUpdates()"),
        ("TrackingService", "Storage", "save session summary"),
        ("TrackingService", "TrackingService", "stopSelf(): resources released"),
    ]
    for a, b, t in etapes:
        xa, xb = X[a], X[b]
        couleur = "#7f6000" if a == "Location APIs" else "#1f4e79"
        if a == b:
            s.append('<polyline points="%d,%d %d,%d %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2"/>'
                     % (xa, y - 6, xa + 30, y - 6, xa + 30, y + 12, xa + 4, y + 12, couleur))
            s.append('<polygon points="%d,%d %d,%d %d,%d" fill="%s"/>' % (xa, y + 12, xa + 11, y + 7, xa + 11, y + 17, couleur))
            s.append('<text x="%d" y="%d" font-family="%s" font-size="16" fill="%s" stroke="#fff" stroke-width="4" '
                     'paint-order="stroke">%s</text>' % (xa + 38, y + 9, police(t), couleur, esc(t)))
        else:
            fleche(s, [(xa, y), (xb, y)], "", couleur=couleur)
            gauche = min(xa, xb)
            s.append('<text x="%d" y="%d" font-family="%s" font-size="16" fill="%s" stroke="#fff" stroke-width="4" '
                     'paint-order="stroke">%s</text>' % (gauche + 10, y - 8, police(t), couleur, esc(t)))
        y += 47
    rendre(svg(s, 650), L, 650, os.path.join(SORTIE, "fig3_tracking.png"))


if __name__ == "__main__":
    os.makedirs(SORTIE, exist_ok=True)
    for f in (sys.argv[1:] or ["navigation", "architecture", "tracking"]):
        globals()[f]()
    print("ok")
