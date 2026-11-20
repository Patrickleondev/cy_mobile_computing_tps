"""Guides pas à pas complets des TP1 à TP4 : pour chaque fichier nouveau ou modifié, le fichier
entier (copié du projet), les lignes ajoutées par rapport au TP précédent, puis le pourquoi.
Usage (depuis la racine du dépôt) : python outils/generer_guides.py
"""
import difflib
import pathlib

RACINE = pathlib.Path(__file__).resolve().parent.parent
J = "app/src/main/java/com/cyu/tp1intents/"
RES = "app/src/main/res/"


def lire(chemin):
    return chemin.read_text(encoding="utf-8").replace("\r\n", "\n").rstrip("\n")


def langage(rel):
    return {"java": "java", "xml": "xml", "kts": "kotlin", "toml": "toml"}.get(rel.rsplit(".", 1)[-1], "")


def ajouts(avant, apres):
    """Les blocs de lignes ajoutées ou modifiées (diff sans contexte)."""
    blocs, bloc = [], []
    for l in difflib.unified_diff(avant.splitlines(), apres.splitlines(), lineterm="", n=0):
        if l.startswith("@@"):
            if bloc:
                blocs.append(bloc)
            bloc = []
        elif l.startswith("+") and not l.startswith("+++"):
            bloc.append(l[1:])
    if bloc:
        blocs.append(bloc)
    return [b for b in blocs if any(x.strip() for x in b)]


def section(tp, rel, titre, creer, pourquoi, ou):
    projet, precedent = tp["projet"], tp.get("precedent")
    contenu = lire(projet / rel)
    out = [f"### {titre}", ""]
    ancien = precedent / rel if precedent else None
    nouveau = not (ancien and ancien.exists())
    if nouveau:
        out.append(f"**Nouveau fichier.** {creer} Colle **tout** ce contenu :" if creer
                   else "**Remplace tout** le contenu du fichier par :")
    else:
        out.append(f"**Remplace tout** le contenu de `{rel}` par :")
    out += ["", f"```{langage(rel)}", contenu, "```", ""]
    if not nouveau:
        blocs = ajouts(lire(ancien), contenu)
        if blocs:
            out += ["**Ce qui a été ajouté ou changé** par rapport au TP précédent :", ""]
            for b in blocs:
                out += [f"```{langage(rel)}", "\n".join(b), "```", ""]
    out += ["**Pourquoi :**", "", pourquoi.strip(), "", "**Pourquoi à cet endroit :**", "", ou.strip(), ""]
    return "\n".join(out)


def guide(tp):
    parties = [tp["entete"].strip(), ""]
    for s in tp["sections"]:
        if isinstance(s, str):
            parties.append(s.strip() + "\n")
        else:
            parties.append(section(tp, *s))
    parties.append(tp.get("fin", "").strip())
    return "\n".join(parties) + "\n"


def preparer(n, ancien, nouveau, app_id):
    return f"""
## 0. Préparer le projet

1. Ferme Android Studio. Copie `AndroidStudioProjects\\{ancien}` en `AndroidStudioProjects\\{nouveau}`.
2. Dans la copie, supprime `build`, `app\\build`, `.gradle` et `.idea` (ils seront recréés).
3. Ouvre `{nouveau}` (**File > Open**) et attends la fin du Sync Gradle.
4. Change **seulement** ces lignes :
   - `settings.gradle.kts` : `rootProject.name = "{nouveau}"` ;
   - `app/build.gradle.kts` : `applicationId = "{app_id}"` ;
   - `res/values/strings.xml` : `<string name="app_name">{nouveau}</string>`.

**Ne touche jamais** à `namespace = "com.cyu.tp1intents"` dans `app/build.gradle.kts`. C'est le
paquet Java où Android génère la classe `R`. S'il change, tout le projet affiche
« package R does not exist ». Si Studio propose « Rename package », refuse.

`applicationId` est l'identité de l'appli sur le téléphone : en le changeant, le TP{n}
s'installe **à côté** du TP précédent au lieu de l'écraser.
"""


P = lambda nom: RACINE / nom

TPS = []

# ======================================================================= TP1
TPS.append(dict(
    nom="TP1", projet=P("TP1/projet_TP1Intents"), sortie=P("TP1/TP1_pas_a_pas_complet.md"),
    entete="""
# TP1 pas à pas complet : trois écrans reliés par des Intents

Chaque fichier est donné **en entier** : ouvre-le dans Android Studio, **Ctrl + A**, colle.
Après chaque fichier : pourquoi ce code, et pourquoi à cet endroit.

Ce que fait l'appli : un formulaire (nom, email), un 2e écran qui dit « Hello <nom> » avec une
photo et écrit l'email dans Logcat, un 3e écran avec un bouton PREVIOUS.

## 0. Créer le projet

**File > New > New Project > Empty Views Activity**. Name `TP1Intents`, package
`com.cyu.tp1intents`, langage **Java**, Minimum SDK **API 24**. Studio crée `MainActivity`,
`activity_main.xml`, le manifeste et les fichiers Gradle.

Ajoute une image `photo.jpg` dans `app/src/main/res/drawable/` (glisser-déposer dans Studio).
Le nom doit être en minuscules, sans espace ni tiret : il devient `R.drawable.photo`.
""",
    sections=[
        "## 1. Les ressources",
        ("app/src/main/res/values/strings.xml", "1.1 strings.xml", None, """
- Tous les textes affichés sont ici, pas dans le Java ni dans les layouts : on peut traduire
  l'appli sans toucher au code, et Studio ne met plus d'avertissement « Hardcoded string ».
- `\\n` dans `welcome` : un retour à la ligne.
- `empty_name` : le message du Toast si le nom est vide.
""", """
`res/values/` est le dossier des valeurs simples (textes, couleurs, dimensions). Android y cherche
`R.string.xxx` ; ailleurs, la ressource n'existerait pas.
"""),
        ("app/src/main/res/layout/activity_main.xml", "1.2 activity_main.xml (1er écran)", None, """
- `LinearLayout` vertical : les éléments s'empilent de haut en bas. `gravity="center_horizontal"`
  les centre.
- `android:id="@+id/main"` sur la racine : `MainActivity` s'en sert pour les marges des barres
  système (EdgeToEdge).
- Deux `EditText` avec un `id` (`name`, `email`) : le Java les retrouve par `findViewById`.
  `inputType` choisit le clavier (email : avec @). `hint` : le texte gris quand le champ est vide.
- Le `Button` a `android:onClick="submit"` : au clic, Android appelle la méthode
  `public void submit(View view)` de l'Activity.
""", """
Dans `res/layout/` : c'est là qu'Android cherche `R.layout.activity_main`, que `setContentView`
charge dans `onCreate`.
"""),
        ("app/src/main/res/layout/activity_second.xml", "1.3 activity_second.xml (2e écran)",
         "Clic droit sur `res/layout` > **New > Layout Resource File** > `activity_second`.", """
- Un `TextView` fixe « Hello », puis un `TextView` avec `id="name"` que le Java remplit.
- `tools:text="Patrick"` : visible seulement dans l'aperçu de Studio, jamais sur le téléphone.
- `ImageView` avec `src="@drawable/photo"` : la photo ajoutée au point 0.
  `contentDescription` : le texte lu par TalkBack (accessibilité).
- Bouton `onClick="next"` vers le 3e écran.
""", """
Un écran = une Activity + son layout. Celui-ci est chargé par `SecondActivity`.
"""),
        ("app/src/main/res/layout/activity_third.xml", "1.4 activity_third.xml (3e écran)",
         "Clic droit sur `res/layout` > **New > Layout Resource File** > `activity_third`.", """
- Un titre et un bouton PREVIOUS (`onClick="previous"`). Le fond orange clair montre qu'on a
  bien changé d'écran.
""", """
Chargé par `ThirdActivity`.
"""),
        "## 2. Les Activities",
        (J + "MainActivity.java", "2.1 MainActivity.java", None, """
- `public final static String NAME = "com.cyu.tp1intents.name"` : la **clé** de l'extra.
  `public static` : `SecondActivity` la lit avec `MainActivity.NAME`, sans créer d'objet.
  `final` : constante. Préfixée par le paquet pour ne jamais entrer en conflit avec une autre clé.
- `private EditText champNom` : attribut, parce que `onCreate` le trouve et `submit` le lit.
- `onCreate` : `setContentView` affiche le layout, **puis** `findViewById` (avant, les vues
  n'existent pas encore).
- `submit(View view)` : signature imposée par `android:onClick` (`public void`, un `View`).
  `trim()` enlève les espaces. Si le nom est vide : un `Toast` et `return`.
- `new Intent(this, SecondActivity.class)` : un Intent **explicite** (on nomme l'écran visé).
  `putExtra` y range le nom et l'email ; `startActivity` ouvre l'écran.
""", """
`MainActivity` est l'écran de lancement (déclaré `LAUNCHER` dans le manifeste) : c'est lui qui
porte le formulaire et qui envoie les données.
"""),
        (J + "SecondActivity.java", "2.2 SecondActivity.java",
         "Clic droit sur le paquet `com.cyu.tp1intents` > **New > Java Class** > `SecondActivity`.", """
- `private static final String TAG` : l'étiquette des messages Logcat (filtrer sur « SecondActivity »).
- `getIntent()` rend l'Intent qui a ouvert l'écran ; `getStringExtra(MainActivity.NAME)` lit
  l'extra avec **la même clé** que `putExtra`.
- `Log.d(TAG, ...)` : le sujet demande l'email dans le log, pas à l'écran.
- `next(View)` : ouvre `ThirdActivity`.
""", """
La lecture des extras se fait dans `onCreate`, après `setContentView`, parce qu'il faut afficher
le nom dès l'ouverture de l'écran.
"""),
        (J + "ThirdActivity.java", "2.3 ThirdActivity.java",
         "Clic droit sur le paquet > **New > Java Class** > `ThirdActivity`.", """
- `previous(View)` appelle `finish()` : l'écran se ferme et Android réaffiche celui d'en dessous
  dans la pile. Un `new Intent` vers `SecondActivity` empilerait un **deuxième** exemplaire.
""", """
Le bouton PREVIOUS est dans `activity_third.xml`, donc sa méthode est dans l'Activity qui charge
ce layout.
"""),
        "## 3. Le manifeste",
        ("app/src/main/AndroidManifest.xml", "3.1 AndroidManifest.xml", None, """
- **Chaque** Activity doit être déclarée, sinon `ActivityNotFoundException` au clic.
- `MainActivity` a l'`intent-filter` `MAIN` + `LAUNCHER` : c'est l'icône du lanceur.
  `exported="true"` : obligatoire pour une Activity avec `intent-filter`.
- `SecondActivity` et `ThirdActivity` : `exported="false"`, seule ton appli les ouvre.
- `windowSoftInputMode="adjustResize"` : l'écran se réduit quand le clavier s'ouvre, les champs
  restent visibles.
""", """
Les `<activity>` vont **dans** `<application>`. Le manifeste est à la racine de `app/src/main/`.
"""),
    ],
    fin="""
## 4. Tester

Run : tape un nom et un email, OK. « Hello <nom> » et la photo s'affichent ; dans **Logcat**,
filtre `SecondActivity` : « The user's email is: ... ». NEXT, puis PREVIOUS : retour au 2e écran.
Nom vide : le Toast « Entrez au moins un nom ».
""",
))

# ======================================================================= TP2
TPS.append(dict(
    nom="TP2", projet=P("TP2/projet_TP2Events"), precedent=P("TP1/projet_TP1Intents"),
    sortie=P("TP2/TP2_pas_a_pas_complet.md"),
    entete="""
# TP2 pas à pas complet : préférences, téléchargement, base SQLite, liste

Chaque fichier est donné **en entier** (Ctrl + A, coller). Pour un fichier qui existait au TP1,
« Ce qui a été ajouté » montre les lignes nouvelles, puis pourquoi et pourquoi à cet endroit.

Ce que fait l'appli en plus : elle se souvient du nom (on ne remplit le formulaire qu'une fois),
télécharge un fichier d'événements dans un service, le range dans une base SQLite et l'affiche
dans une liste.
""" + preparer(2, "TP1Intents", "TP2Events", "com.cyu.tp2events"),
    sections=[
        "## 1. Manifeste et textes",
        ("app/src/main/AndroidManifest.xml", "1.1 AndroidManifest.xml", None, """
- `INTERNET` : sans elle, toute connexion réseau échoue (`SecurityException`). Permission
  « normale » : accordée à l'installation, rien à demander à l'utilisateur.
- `<service android:name=".DownloadService">` : un service, comme une Activity, doit être déclaré.
""", """
`<uses-permission>` va **avant** `<application>` ; le `<service>` va **dans** `<application>`, à
côté des Activities.
"""),
        ("app/src/main/res/values/strings.xml", "1.2 strings.xml", None, """
- Les textes du statut de la liste (`status_loading`, `status_error`, `status_count` avec `%1$d`
  pour le nombre) et du détail d'un événement (`event_details`, trois `%s`).
""", """
Avec les autres textes, dans `res/values/strings.xml`.
"""),
        "## 2. Se souvenir de l'utilisateur",
        (J + "MainActivity.java", "2.1 MainActivity.java", None, """
- `PREFS` : le nom du fichier de préférences. `SharedPreferences` = un petit dictionnaire
  clé/valeur gardé sur le téléphone, même après fermeture de l'appli.
- Au début de `onCreate`, **avant** `setContentView` : si un nom est déjà sauvé, on ouvre
  directement le 2e écran et `finish()` ferme celui-ci (sinon BACK y reviendrait), puis `return`.
- Dans `submit` : `prefs.edit().putString(...).apply()` sauve le nom et l'email. `apply()` écrit
  en arrière-plan, sans bloquer l'écran.
- `ouvrirSecond` : le code de l'Intent, appelé à deux endroits, est mis dans une méthode.
""", """
Le test se fait au tout début de `onCreate` : inutile d'afficher le formulaire s'il ne sert pas.
"""),
        "## 3. Les données",
        (J + "Event.java", "3.1 Event.java", "Clic droit sur le paquet > **New > Java Class** > `Event`.", """
- Une ligne de la table : `id`, `name`, `lat`, `lng`, `type`. Champs `public final` : un simple
  objet de données, lu par les autres classes, jamais modifié.
- `toString()` : le texte écrit dans Logcat (le sujet demande d'afficher chaque ligne lue).
""", """
Classe à part, utilisée par `DownloadService`, `EventDbHelper` et `ThirdActivity`.
"""),
        (J + "EventDbHelper.java", "3.2 EventDbHelper.java", "Clic droit sur le paquet > **New > Java Class** > `EventDbHelper`.", """
- `extends SQLiteOpenHelper` : Android crée et ouvre `events.db` pour nous.
- Les constantes `TABLE_EVENTS`, `ID`, `NAME`... : les noms imposés par le sujet, écrits une
  seule fois pour éviter les fautes de frappe dans le SQL.
- `onCreate` : appelée **une seule fois**, quand le fichier n'existe pas : `CREATE TABLE`.
- `onUpgrade` : appelée quand `DB_VERSION` augmente.
- `remplacer` : vide la table puis insère tout, dans une **transaction** : si une insertion échoue,
  rien n'est changé (`setTransactionSuccessful` n'est pas atteint).
- `estVide` : compte les lignes ; `lireTout` : `SELECT *` trié par `ID`, avec un `Cursor` fermé
  automatiquement par le `try (...)`.
""", """
Toute la base est dans cette classe : les écrans ne voient jamais de SQL, seulement des `Event`.
"""),
        (J + "DownloadService.java", "3.3 DownloadService.java", "Clic droit sur le paquet > **New > Java Class** > `DownloadService`.", """
- `extends IntentService` : `onHandleIntent` tourne dans un **thread à part**. Le réseau est
  interdit sur le thread de l'écran (`NetworkOnMainThreadException`).
- `telecharger` : `HttpURLConnection`, puis copie par blocs de 4 Ko dans
  `getExternalFilesDir(DIRECTORY_DOWNLOADS)/events.txt`. `read` rend le nombre d'octets lus : on
  n'écrit que ceux-là.
- `lire` : chaque ligne `NOM;;LAT;;LNG;;TYPE` est coupée par `split(";;")` en 4 morceaux. Une
  ligne mal formée est ignorée (et notée dans Logcat).
- À la fin : un `Intent(ACTION_FINI)` envoyé par `sendBroadcast`, avec `SUCCES` vrai ou faux.
  `setPackage` : seul ton appli le reçoit.
""", """
Un service plutôt qu'un thread dans l'Activity : le téléchargement continue même si l'écran est
tourné ou fermé.
"""),
        "## 4. La liste",
        ("app/src/main/res/layout/activity_third.xml", "4.1 activity_third.xml", None, """
- `TextView status` : « Téléchargement... », puis « 15 evenements ».
- `ListView events` avec `layout_height="0dp"` et `layout_weight="1"` : elle prend toute la
  hauteur restante entre le statut et le bouton.
""", """
Le 3e écran du TP1 devient l'écran de la liste.
"""),
        (J + "ThirdActivity.java", "4.2 ThirdActivity.java", None, """
- `receveur` : un `BroadcastReceiver` qui reçoit `ACTION_FINI` du service, puis affiche la liste
  (ou le message d'erreur).
- `onCreate` : si la base est vide, on lance le service une fois (`startService`).
- `onResume` / `onPause` : on s'inscrit au message quand l'écran est visible, on se désinscrit
  quand il ne l'est plus. `RECEIVER_NOT_EXPORTED` : depuis Android 14, il faut dire que ce
  récepteur n'accepte pas les messages des autres applis.
- `afficher` : lit la base, écrit chaque `Event` dans Logcat, met les noms dans un
  `ArrayAdapter` (une ligne de texte par élément).
- Au clic sur un élément : une `AlertDialog` avec les coordonnées et le type.
- `onDestroy` : ferme la base.
""", """
`afficher()` est appelée dans `onResume` : quand on revient sur l'écran, la liste est relue.
"""),
        ("app/build.gradle.kts", "4.3 app/build.gradle.kts", None, """
- Seul `applicationId` change (`com.cyu.tp2events`). `namespace` ne change pas.
""", """
Dans le bloc `defaultConfig`.
"""),
    ],
    fin="""
## 5. Tester

Lance l'appli, remplis le formulaire, NEXT : « Téléchargement... » puis la liste des 15
événements. Dans Logcat (filtre `ThirdActivity`) : une ligne par événement. Relance l'appli : le
formulaire est sauté (préférences) et la liste s'affiche sans téléchargement (base remplie).
""",
))

# ======================================================================= TP3
TPS.append(dict(
    nom="TP3", projet=P("TP3/projet_TP3Maps"), precedent=P("TP2/projet_TP2Events"),
    sortie=P("TP3/TP3_pas_a_pas_complet.md"),
    entete="""
# TP3 pas à pas complet : écran d'un événement, adresse, carte et GPS

Chaque fichier est donné **en entier** (Ctrl + A, coller). « Ce qui a été ajouté » montre les
lignes nouvelles par rapport au TP2.

Ce que fait l'appli en plus : un clic sur un événement ouvre son écran avec son adresse
(géocodage) ; un bouton AJOUTER ouvre une carte OpenStreetMap centrée sur la position GPS, pour
créer un événement à l'endroit où l'on est.
""" + preparer(3, "TP2Events", "TP3Maps", "com.cyu.tp3maps"),
    sections=[
        "## 1. Gradle : la bibliothèque de carte",
        ("gradle/libs.versions.toml", "1.1 gradle/libs.versions.toml", None, """
- `osmdroid = "6.1.20"` (section `[versions]`) et `osmdroid-android` (section `[libraries]`) :
  la bibliothèque de cartes OpenStreetMap, sans clé d'API (Google Maps en demande une).
""", """
Ce fichier est le catalogue des versions du projet : on y déclare la bibliothèque, puis on
l'utilise dans `app/build.gradle.kts`.
"""),
        ("app/build.gradle.kts", "1.2 app/build.gradle.kts", None, """
- `implementation(libs.osmdroid.android)` : ajoute osmdroid à l'appli. Puis **Sync Now**.
- `applicationId = "com.cyu.tp3maps"`. `namespace` ne change pas.
""", """
Dans le bloc `dependencies`, avec les autres bibliothèques.
"""),
        "## 2. Manifeste et textes",
        ("app/src/main/AndroidManifest.xml", "2.1 AndroidManifest.xml", None, """
- `ACCESS_FINE_LOCATION` (GPS précis) et `ACCESS_COARSE_LOCATION` (position approximative) :
  permissions **dangereuses**, à déclarer ici **et** à demander à l'exécution (voir
  `AddEventActivity`).
- `ACCESS_NETWORK_STATE` : osmdroid vérifie la connexion avant de télécharger les tuiles.
- Les deux nouvelles Activities, `EventActivity` et `AddEventActivity`.
""", """
Permissions avant `<application>`, Activities dedans.
"""),
        ("app/src/main/res/values/strings.xml", "2.2 strings.xml", None, """
- Les textes de l'écran d'un événement (type, coordonnées, adresse) et du formulaire d'ajout
  (position, nom, ENREGISTRER, refus de la localisation).
- `event_types` : un `string-array`, la liste du `Spinner` (concert, forum...).
- Les apostrophes s'écrivent `\\'`, sinon la compilation échoue.
""", """
Avec les autres textes.
"""),
        "## 3. L'écran d'un événement",
        ("app/src/main/res/layout/activity_event.xml", "3.1 activity_event.xml",
         "Clic droit sur `res/layout` > **New > Layout Resource File** > `activity_event`.", """
- Nom (gros, gras), type, coordonnées, puis l'adresse trouvée par le géocodeur.
- L'adresse a `layout_weight="1"` : elle prend la place restante, le bouton PREVIOUS reste en bas.
""", """
Chargé par `EventActivity`.
"""),
        (J + "EventActivity.java", "3.2 EventActivity.java",
         "Clic droit sur le paquet > **New > Java Class** > `EventActivity`.", """
- `EXTRA_NAME`, `EXTRA_LAT`... : `public static final`, les clés partagées avec `ThirdActivity`.
- `onCreate` lit les extras et remplit les `TextView`. `nom != null ? nom : ""` : évite d'afficher
  « null ».
- `Double.parseDouble` dans un `try` : les coordonnées arrivent en texte.
- `chercherAdresse` : `Geocoder` transforme (lat, lng) en adresse. Il fait une requête réseau :
  - Android 13+ (`TIRAMISU`) : la version avec **callback**, le résultat arrive plus tard ;
  - avant : la version bloquante, donc dans un `new Thread`.
  Dans les deux cas, `runOnUiThread` revient sur le thread de l'écran : seul lui peut modifier
  une vue.
- `montrer` : assemble les lignes de l'adresse.
""", """
L'adresse est cherchée dans `onCreate`, une fois, dès l'ouverture de l'écran.
"""),
        "## 4. Le formulaire avec la carte",
        ("app/src/main/res/layout/activity_add_event.xml", "4.1 activity_add_event.xml",
         "Clic droit sur `res/layout` > **New > Layout Resource File** > `activity_add_event`.", """
- `org.osmdroid.views.MapView` : la carte, avec le nom complet de sa classe (elle ne vient pas
  d'Android). `layout_weight="1"` : elle prend tout le haut.
- En bas : la position, le nom (`EditText`), le type (`Spinner` rempli par `@array/event_types`)
  et ENREGISTRER, désactivé (`enabled="false"`) tant que la position n'est pas connue.
""", """
Chargé par `AddEventActivity`.
"""),
        (J + "AddEventActivity.java", "4.2 AddEventActivity.java",
         "Clic droit sur le paquet > **New > Java Class** > `AddEventActivity`.", """
- `demandePermission` : `registerForActivityResult(RequestMultiplePermissions)`, en **attribut**.
  Il doit être créé avant le démarrage de l'écran ; dans un clic, l'appli plante.
- `ecouteur` : un `LocationListener`, appelé à chaque nouvelle position (`onLocationChanged`).
- `onCreate` : `Configuration.getInstance().load(...)` **avant** `setContentView` (osmdroid lit
  sa configuration en créant la carte) et `setUserAgentValue` (les serveurs OSM refusent les
  requêtes sans identifiant). Puis la carte, le zoom, l'épingle sur Cergy, et la demande de
  permission si besoin.
- `demarrerGps` : la dernière position connue tout de suite, puis `requestLocationUpdates`
  toutes les 2 s ou 5 m. `@SuppressLint("MissingPermission")` : on a vérifié `aLaPermission()`.
- `placer` : déplace l'épingle et la carte, affiche la position, active ENREGISTRER.
- `save` : vérifie le nom, formate lat/lng avec `Locale.US` (un point, pas une virgule), insère
  dans la base avec `ajouter`, puis `finish()`.
- `onResume` / `onPause` : on démarre et on arrête le GPS avec l'écran, pour ne pas vider la
  batterie ; `carte.onResume/onPause` sont demandés par osmdroid.
""", """
Tout le formulaire est dans cette Activity : la carte, le GPS et l'enregistrement servent au même
écran.
"""),
        "## 5. La liste et la base",
        (J + "EventDbHelper.java", "5.1 EventDbHelper.java", None, """
- `ajouter(Event e)` : insère **un** événement créé sur le téléphone, sans vider la table (à la
  différence de `remplacer`). Rend l'`ID` créé, ou -1 si l'insertion échoue.
""", """
Dans la classe de la base, à côté de `remplacer`.
"""),
        ("app/src/main/res/layout/activity_third.xml", "5.2 activity_third.xml", None, """
- Les boutons PREVIOUS et AJOUTER côte à côte, dans un `LinearLayout` horizontal.
""", """
En bas de la liste.
"""),
        (J + "ThirdActivity.java", "5.3 ThirdActivity.java", None, """
- Au clic sur un événement : au lieu de l'`AlertDialog` du TP2, un `Intent` vers `EventActivity`
  avec les 4 extras.
- `addEvent(View)` : ouvre le formulaire. Au retour, `onResume` relit la base : le nouvel
  événement apparaît en bas.
""", """
Le clic sur la liste est réglé dans `onCreate`, avec la liste.
"""),
    ],
    fin="""
## 6. Tester

Clic sur EVENT1 : son écran, puis l'adresse. AJOUTER : accepte la permission de localisation.
Sur l'émulateur, donne une position avec **⋯ > Location** (ou `adb emu geo fix 2.07 49.035`) :
l'épingle bouge, ENREGISTRER s'active. Nom, type, ENREGISTRER : l'événement est en bas de la liste.
""",
))

# ======================================================================= TP4
TPS.append(dict(
    nom="TP4", projet=P("TP4/projet_TP4Calls"), precedent=P("TP3/projet_TP3Maps"),
    sortie=P("TP4/TP4_pas_a_pas_complet.md"),
    entete="""
# TP4 pas à pas complet : appeler les secours, envoyer et recevoir un SMS

Chaque fichier est donné **en entier** (Ctrl + A, coller). « Ce qui a été ajouté » montre les
lignes nouvelles par rapport au TP3.

Ce que fait l'appli en plus : depuis l'écran d'un événement, appeler le numéro de secours qui
correspond à son type (15, 17, 18 ou 112) et afficher l'état de l'appel ; envoyer un SMS avec le
nom et la position de l'événement ; afficher les SMS reçus.

**Sécurité** : 15, 17, 18 et 112 sont de vrais numéros. Teste **uniquement sur l'émulateur**.
""" + preparer(4, "TP3Maps", "TP4Calls", "com.cyu.tp4calls"),
    sections=[
        "## 1. Manifeste et textes",
        ("app/src/main/AndroidManifest.xml", "1.1 AndroidManifest.xml", None, """
- `CALL_PHONE` : appeler sans passer par le clavier. `READ_PHONE_STATE` : être prévenu des états
  de l'appel. `SEND_SMS`, `RECEIVE_SMS` : envoyer et recevoir. Toutes **dangereuses** : à demander
  aussi à l'exécution.
- `POST_NOTIFICATIONS` : depuis Android 13, sans elle les Toast d'une appli en arrière-plan
  (pendant l'appel) ne s'affichent pas.
- `uses-feature telephony required="false"` : l'appli s'installe aussi sur une tablette.
- `<receiver .SmsReceiver>` : `exported="true"` car le message vient du système ;
  `permission="BROADCAST_SMS"` : seul le système (qui a cette permission) peut l'appeler, une autre
  appli ne peut pas envoyer de faux SMS ; l'`intent-filter` `SMS_RECEIVED`.
""", """
Permissions et `uses-feature` avant `<application>` ; le `<receiver>` dedans, à côté du `<service>`.
"""),
        ("app/src/main/res/values/strings.xml", "1.2 strings.xml", None, """
- Les textes des boutons, des Toast d'état d'appel et de SMS. `%1$s` / `%1$d` : valeurs insérées
  par `getString(id, valeur)`.
""", """
Avec les autres textes, avant le `string-array`.
"""),
        ("app/src/main/res/layout/activity_event.xml", "1.3 activity_event.xml", None, """
- Bouton `call` : son texte (APPELER LE 15...) est mis par le Java, d'où `tools:text`.
- `EditText sms_number` : `inputType="phone"` (clavier numérique), `5554` = l'émulateur lui-même.
- Bouton ENVOYER UN SMS (`onClick="sendSms"`).
""", """
Sous les coordonnées et avant l'adresse : les actions de l'événement restent visibles en haut.
"""),
        "## 2. L'écran de l'événement",
        (J + "EventActivity.java", "2.1 EventActivity.java", None, """
- `nom`, `lat`, `lng` deviennent des **attributs** (plus des variables de `onCreate`) : `sendSms`
  en a besoin plus tard.
- `apresPermission` + `messageRefus` + `demandePermissions` : **une seule** demande de permissions
  réutilisée pour l'appel et le SMS. `messageRefus` est déclaré **avant** le launcher qui l'utilise
  (sinon « illegal forward reference »).
- `avecPermissions(permissions, action)` : si tout est accordé, l'action tout de suite ; sinon on
  la garde et on demande.
- `numeroPourType` : ramène `TYPE1`..`TYPE5` (téléchargés) et `concert`... (formulaire) à un
  numéro 1 à 5, puis `switch` : 15, 17, 18, et `default` 112 (types 4, 5 et inconnus).
- `call` : `Intent.ACTION_CALL` + `tel:15` (appel direct, demande `CALL_PHONE`). On écoute l'état
  **avant** d'appeler pour ne rien rater.
- `ecouterAppels` : Android 12+ `TelephonyCallback` (classe interne `EcouteurAppel12`), avant
  `PhoneStateListener`, déprécié. `getMainExecutor()` : rappels sur le thread de l'écran (Toast).
- `montrerEtat` : `dernierEtat` filtre l'état IDLE donné dès l'inscription.
- `envoyerSms` : `SmsManager.sendTextMessage(numero, null, texte, quandEnvoye, null)`. Le
  `PendingIntent` est renvoyé par Android quand l'envoi est fini ; `resultatSms` le lit avec
  `getResultCode()`.
- `onDestroy` : désinscriptions. `onDestroy` et pas `onPause` : pendant l'appel, l'écran du
  téléphone passe devant (onPause), et on raterait les états à afficher.
""", """
Tout est dans `EventActivity` parce que le sujet dit « depuis l'événement qu'il regarde » : le
type, le nom et la position sont déjà dans ses extras.
"""),
        (J + "SmsReceiver.java", "2.2 SmsReceiver.java",
         "Clic droit sur le paquet > **New > Java Class** > `SmsReceiver`.", """
- `extends BroadcastReceiver` : `onReceive` est appelée à chaque SMS reçu.
- `Telephony.Sms.Intents.getMessagesFromIntent` : les morceaux du SMS (un long message arrive en
  plusieurs SMS de 160 caractères), recollés dans l'ordre.
- `getDisplayOriginatingAddress` : l'expéditeur ; `getMessageBody` : le texte.
""", """
Déclaré dans le **manifeste** (et pas inscrit en Java) : Android réveille l'appli pour lui, même
quand aucun écran n'est ouvert.
"""),
        ("app/build.gradle.kts", "2.3 app/build.gradle.kts", None, """
- `applicationId = "com.cyu.tp4calls"`. `namespace` ne change pas.
""", """
Dans `defaultConfig`.
"""),
    ],
    fin="""
## 3. Tester (émulateur seulement)

EVENT3 (TYPE1) : APPELER LE 15, accepte la permission : Toast « en communication », puis
« termine ». Appel entrant : `adb emu gsm call 0612345678`, `adb emu gsm accept ...`,
`adb emu gsm cancel ...` : sonne, en communication, termine. ENVOYER UN SMS vers 5554 : « SMS
envoye ». Réception : `adb emu sms send 0612345678 "Bonjour"`.
""",
))

if __name__ == "__main__":
    for tp in TPS:
        tp["sortie"].write_text(guide(tp), encoding="utf-8")
        print(tp["nom"], "->", tp["sortie"].relative_to(RACINE), len(tp["sortie"].read_text(encoding="utf-8").splitlines()), "lignes")
