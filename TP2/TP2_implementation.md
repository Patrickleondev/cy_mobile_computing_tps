# TP2 implémenté depuis le sujet : ce qui a été écrit, et pourquoi

Construit depuis `da20-tp2 (1).pdf` seulement, **sans le code du prof** (`da20-tp2/`). Le sujet dit
« modify and extend the application you developed during TP1 » : on part donc de **ton** TP1.

Plan : **1.** ouvrir le projet. **2.** les fichiers touchés. **3 à 5.** chaque partie du sujet, avec le
code et le pourquoi. **6.** les écarts avec le sujet, à écrire dans ton rendu. **7.** tester. **8.** rendre.
**9.** questions pour vérifier que tu as compris.

---

## 1. Ouvrir le projet

Le projet est dans `C:\Users\User\AndroidStudioProjects\TP2Events`. C'est une **copie** de
`TP1Intents` : ton TP1 reste intact, tel que tu l'as rendu.

Dans Android Studio : **File > Open**, choisis le dossier `TP2Events`, puis attends la fin du
Sync Gradle. J'ai déjà compilé le projet en ligne de commande le 01/11 : `assembleDebug`
réussit. Le seul avertissement vient de `IntentService`, que le sujet impose (voir partie 6).

Deux choses changées par rapport au TP1, en plus du code :

| Fichier | Changement | Pourquoi |
|---|---|---|
| `settings.gradle.kts` | `rootProject.name = "TP2Events"` | le nom du projet dans Studio |
| `app/build.gradle.kts` | `applicationId = "com.cyu.tp2events"` | l'émulateur voit **deux applications différentes** : installer le TP2 n'écrase pas le TP1 |
| `strings.xml` | `app_name` = `TP2Events` | le nom sous l'icône |

Le **paquet Java** reste `com.cyu.tp1intents` (le `namespace`). C'est permis : `applicationId`
identifie l'application sur le téléphone, `namespace` sert seulement à générer la classe `R`. Renommer
le paquet aurait obligé à déplacer tous les fichiers, sans rien apporter au TP.

---

## 2. Les fichiers touchés

| Fichier | Nouveau ? | Partie du sujet |
|---|---|---|
| `MainActivity.java` | modifié | **1** User Data |
| `DownloadService.java` | **nouveau** | **2.1** téléchargement, **2.2** lecture du fichier |
| `EventDbHelper.java` | **nouveau** | **2.2** base SQLite |
| `Event.java` | **nouveau** | une ligne de la table |
| `ThirdActivity.java` | modifié | **2.1** BroadcastReceiver, **3.1** requête, Log, ListView, clic |
| `activity_third.xml` | modifié | **3.1** la `ListView` |
| `AndroidManifest.xml` | modifié | **2.1** permission `INTERNET`, déclaration du service |
| `strings.xml` | modifié | textes du 3ᵉ écran |

`SecondActivity.java` n'a **pas** changé : elle lit toujours le nom dans l'Intent, comme au TP1.

---

## 3. Partie 1 du sujet : User Data

> Save the information that the user gives you in MainActivity so that the next time that the user
> will launch the application she will be presented with the SecondActivity directly.

Il faut un stockage qui **survit à la fermeture** de l'application. Pour deux petites chaînes, c'est
**SharedPreferences** : un fichier XML clé → valeur, privé à l'application.

**Enregistrer**, dans `submit()`, une fois le nom vérifié :

```java
prefs.edit()
        .putString(NAME, nom)
        .putString(EMAIL, email)
        .apply();
```

`apply()` écrit en arrière-plan et rend la main tout de suite. `commit()` ferait la même chose, mais
attendrait la fin de l'écriture sur le thread de l'écran.

**Relire**, au tout début de `onCreate()` :

```java
prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
String nomSauve = prefs.getString(NAME, "");
if (!nomSauve.isEmpty()) {
    ouvrirSecond(nomSauve, prefs.getString(EMAIL, ""));
    finish();
    return;
}
```

| Ligne | Pourquoi |
|---|---|
| `getString(NAME, "")` | le 2ᵉ argument est la valeur si la clé n'existe pas : au premier lancement, `""` |
| test **avant** `setContentView` | inutile de construire le formulaire s'il ne sera jamais vu |
| `finish()` | retire MainActivity de la pile : Retour depuis l'écran 2 **quitte** l'application au lieu de ramener au formulaire |
| `return` | sans lui, la suite de `onCreate` s'exécuterait quand même |
| `ouvrirSecond(...)` | l'écran 2 du TP1 lit le nom **dans l'Intent** : on remet donc le nom sauvé dans l'Intent, et SecondActivity n'a pas à changer |

« if all the needed information was provided » : dans ton TP1, seul le nom est obligatoire (Toast
`empty_name`). On saute donc le formulaire dès qu'un nom est enregistré.

`getSharedPreferences(PREFS, MODE_PRIVATE)` plutôt que `PreferenceManager.getDefaultSharedPreferences` :
`PreferenceManager` est **déprécié** depuis Android 10.

---

## 4. Partie 2 du sujet : fichier et SQLite

### 4.1 Le service qui télécharge (`DownloadService.java`)

> Create a Service responsible to download a file from the web. […] Create an Activity that will
> communicate with an IntentService using a BroadcastReceiver.

**Pourquoi un service, et pas le téléchargement directement dans l'activité ?** Android **interdit
le réseau sur le thread principal**, celui qui dessine l'écran : l'appel lève
`NetworkOnMainThreadException`. Et un téléchargement lent y figerait l'écran (ANR, « l'application ne
répond pas »). Un `IntentService` exécute `onHandleIntent()` **dans un thread à part**, traite les
demandes une par une, et s'arrête tout seul quand il a fini.

Ce que fait `onHandleIntent()`, dans l'ordre :

```java
File fichier = telecharger();                     // 2.1
List<Event> events = lire(fichier);               // 2.2 découper les lignes
new EventDbHelper(this).remplacer(events);        // 2.2 insérer dans SQLite
...
Intent fini = new Intent(ACTION_FINI);
fini.setPackage(getPackageName());                // seule notre application le reçoit
fini.putExtra(SUCCES, succes);
sendBroadcast(fini);                              // prévenir ThirdActivity
```

La lecture du fichier et l'insertion en base sont faites **dans le service**, donc aussi hors du thread
principal. Pour 15 lignes, ça ne change rien. Pour 10 000, l'écran resterait fluide.

**Le téléchargement**, dans `telecharger()` :

```java
HttpURLConnection connexion = (HttpURLConnection) new URL(URL_EVENTS).openConnection();
connexion.setConnectTimeout(10000);
connexion.setReadTimeout(10000);
int code = connexion.getResponseCode();
if (code != HttpURLConnection.HTTP_OK) { throw new IOException("reponse HTTP " + code); }
...
byte[] tampon = new byte[4096];
int n;
while ((n = in.read(tampon)) != -1) {
    out.write(tampon, 0, n);
}
```

| Point | Pourquoi |
|---|---|
| `URL_EVENTS` = l'adresse **du sujet** | testée le 01/11 : elle renvoie 15 lignes, `EVENT1` à `EVENT15` |
| Google répond d'abord `303 See Other` | `HttpURLConnection` suit tout seul ce renvoi vers `drive.usercontent.google.com`, car il reste en `https` |
| les deux *timeouts* | sans eux, sans réseau, le service peut attendre très longtemps avant d'échouer |
| test `HTTP_OK` (200) | sinon une page d'erreur de Google serait enregistrée comme si c'était le fichier |
| `write(tampon, 0, n)` | `read` renvoie **le nombre d'octets lus**, souvent moins de 4096 au dernier tour. `write(tampon)` recopierait aussi les restes du tour précédent à la fin du fichier |
| `try ( … )` | ferme les flux même en cas d'erreur |

**Où est enregistré le fichier :**

```java
File dossier = getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS);
File fichier = new File(dossier, FICHIER);    // events.txt
```

C'est le dossier `Download` de l'application, **sur le stockage externe** :
`/storage/emulated/0/Android/data/com.cyu.tp2events/files/Download/events.txt`. Ce n'est pas
exactement le `/storage/sdcard/Download` du sujet : la raison est dans la partie 6.

### 4.2 Lire le fichier (`lire()` dans `DownloadService`)

> Each line in this file contains the name, latitude, longitude and event type number of a single
> event, separated by ";;".

```java
String[] morceaux = ligne.split(";;");
if (morceaux.length == 4) {
    events.add(new Event(0, morceaux[0], morceaux[1], morceaux[2], morceaux[3]));
} else {
    Log.w(TAG, "Ligne ignoree : " + ligne);
}
```

`EVENT1;;48.863429;;2.388223;;TYPE3` donne `["EVENT1", "48.863429", "2.388223", "TYPE3"]`. Une ligne vide
est sautée. Une ligne qui n'a pas 4 morceaux est signalée dans Logcat, au lieu de faire planter
l'application avec un `ArrayIndexOutOfBoundsException`.

L'`id` vaut 0 ici : c'est SQLite qui le choisira (voir 4.3).

### 4.3 La base (`EventDbHelper.java`)

> Your database should contain a table with name: TABLE_EVENTS. You need five columns in that table:
> ID (INTEGER), NAME (TEXT), LAT (TEXT), LNG (TEXT), TYPE (TEXT).

Les noms sont **exactement** ceux du sujet :

```java
db.execSQL("CREATE TABLE " + TABLE_EVENTS + " ("
        + ID + " INTEGER PRIMARY KEY, "
        + NAME + " TEXT, "
        + LAT + " TEXT, "
        + LNG + " TEXT, "
        + TYPE + " TEXT)");
```

| Méthode | Quand elle tourne | Ce qu'elle fait |
|---|---|---|
| `onCreate(db)` | **une seule fois**, quand `events.db` n'existe pas encore | crée la table |
| `onUpgrade(db, …)` | quand `DB_VERSION` augmente | supprime la table, puis la recrée |
| `remplacer(events)` | après chaque téléchargement | vide la table, puis insère les lignes du fichier |
| `estVide()` | à l'ouverture de l'écran 3 | dit s'il faut télécharger |
| `lireTout()` | à l'affichage | `SELECT * FROM TABLE_EVENTS ORDER BY ID` |

**`ID INTEGER PRIMARY KEY`** : en SQLite, une telle colonne reçoit automatiquement 1, 2, 3… si on ne
lui donne pas de valeur. C'est pourquoi `remplacer()` ne met jamais `ID` dans le `ContentValues`.

**La transaction** dans `remplacer()` :

```java
db.beginTransaction();
try {
    db.delete(TABLE_EVENTS, null, null);
    for (Event e : events) { … db.insert(TABLE_EVENTS, null, ligne); }
    db.setTransactionSuccessful();
} finally {
    db.endTransaction();
}
```

Tout ou rien : si une insertion échoue, la table garde son ancien contenu. Et 15 insertions dans une
seule transaction vont beaucoup plus vite que 15 écritures séparées sur le disque. Le `delete` au
début évite d'avoir les événements en double si on télécharge deux fois.

**`LAT` et `LNG` en `TEXT`** : c'est le sujet qui le demande. `Event` les garde donc en `String`. Pour
les mettre sur une carte (TP suivant), il faudra `Double.parseDouble(e.lat)`.

---

## 5. Partie 3 du sujet : l'interface (`ThirdActivity.java`)

### 5.1 Lancer le téléchargement, puis recevoir le message

```java
// onCreate
if (db.estVide()) {
    statut.setText(R.string.status_loading);
    startService(new Intent(this, DownloadService.class));
}
```

On ne télécharge **que si la base est vide**. Une fois les 15 lignes en base, les ouvertures
suivantes de l'écran 3 n'utilisent plus le réseau.

Le **BroadcastReceiver** :

```java
private final BroadcastReceiver receveur = new BroadcastReceiver() {
    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent.getBooleanExtra(DownloadService.SUCCES, false)) {
            afficher();
        } else {
            statut.setText(R.string.status_error);
        }
    }
};
```

| Où | Code | Pourquoi |
|---|---|---|
| `onResume` | `ContextCompat.registerReceiver(this, receveur, new IntentFilter(ACTION_FINI), ContextCompat.RECEIVER_NOT_EXPORTED)` | on n'écoute que quand l'écran est visible |
| `onPause` | `unregisterReceiver(receveur)` | sinon le système garde une référence vers une activité peut-être détruite (fuite mémoire) |
| `onResume` | `afficher()` | si le message est arrivé pendant que l'écran était caché, il est perdu. Mais les données sont en base : on les relit en revenant |

**`RECEIVER_NOT_EXPORTED`** : depuis Android 14, une application doit dire si son receiver accepte
les messages **des autres applications**. Ici, non. Côté envoi, `setPackage(getPackageName())` fait
la même chose : le message ne sort pas de l'application.

### 5.2 Requête, Log, ListView, clic

> 1. Print the information from your database in the console using Log.
> 2. Show the name of the events on the screen as a list in the ThirdActivity. […] The user should
>    be able to click on an event and see the rest of the details (coordinates and type).

```java
private void afficher() {
    events = db.lireTout();                       // la requête SQL
    if (events.isEmpty()) { return; }
    List<String> noms = new ArrayList<>();
    for (Event e : events) {
        Log.d(TAG, e.toString());                 // 3.1.1 : dans Logcat
        noms.add(e.name);
    }
    liste.setAdapter(new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, noms));   // 3.1.2
    statut.setText(getString(R.string.status_count, events.size()));
}
```

**L'adapter** fait le lien entre les données (la liste de noms) et la `ListView`. Pour chaque nom, il
fabrique une ligne avec le modèle d'Android `simple_list_item_1` (un seul `TextView`).

**Le clic** :

```java
liste.setOnItemClickListener((parent, vue, position, id) -> {
    Event e = events.get(position);
    new AlertDialog.Builder(this)
            .setTitle(e.name)
            .setMessage(getString(R.string.event_details, e.lat, e.lng, e.type))
            .setPositiveButton(android.R.string.ok, null)
            .show();
});
```

`position` est le rang de la ligne cliquée. C'est aussi le rang dans `events`, puisque l'adapter a été
construit dans le même ordre. Les détails s'affichent dans une **boîte de dialogue** : le sujet
demande de « voir le reste des détails », pas un nouvel écran. Une 4ᵉ activité marcherait aussi :
il faudrait alors passer `lat`, `lng` et `type` en extras de l'Intent, comme le nom au TP1.

**Le layout** `activity_third.xml` : la `ListView` a `layout_height="0dp"` et `layout_weight="1"`.
Dans un `LinearLayout` vertical, ça veut dire « prends toute la hauteur qui reste ». Le bouton
PREVIOUS reste donc visible en bas, même avec 15 lignes.

### 5.3 Le manifeste

```xml
<uses-permission android:name="android.permission.INTERNET" />
...
<service android:name=".DownloadService" android:exported="false" />
```

| Ligne | Si elle manque |
|---|---|
| `INTERNET` | `SecurityException` au moment de `openConnection` / `getResponseCode` : rien n'est téléchargé |
| `<service>` | `startService` ne trouve pas le service : rien ne se passe, avec un avertissement dans Logcat |

---

## 6. Les écarts avec le sujet (à écrire dans ton rendu)

Le sujet date de 2017-2020. Ton projet cible **Android 17 (API 37)**. Trois choses du sujet ne
marchent plus telles quelles, ou sont dépréciées. Mieux vaut le dire dans ton rendu que de laisser le
prof le découvrir.

| Le sujet dit | Ce qui a été fait | Pourquoi |
|---|---|---|
| sauver dans `/storage/sdcard/Download` | `getExternalFilesDir(DIRECTORY_DOWNLOADS)`, sur le stockage externe | depuis Android 10, le **stockage cloisonné** (*scoped storage*) interdit d'écrire avec `File` dans le dossier `Download` commun. Et depuis Android 13, la permission `WRITE_EXTERNAL_STORAGE` n'est plus jamais accordée |
| « Remember to specify the system permissions! » | `INTERNET` seulement | le dossier de l'application sur le stockage externe ne demande **aucune** permission depuis Android 4.4. Demander `WRITE_EXTERNAL_STORAGE` serait inutile |
| `IntentService` | gardé, car le sujet l'impose | déprécié depuis Android 11 : c'est l'avertissement à la compilation. Aujourd'hui on utiliserait **WorkManager** |

Le `LocalBroadcastManager` (utilisé dans les vieux tutoriels) n'a pas été pris : il est déprécié. On
utilise un broadcast normal, limité à l'application par `setPackage` et `RECEIVER_NOT_EXPORTED`.

**Phrase à mettre dans ton rendu** (adapte-la) :

> The app targets API 37. Since Android 10 (scoped storage), apps can no longer write to the shared
> Download folder with the File API, and WRITE_EXTERNAL_STORAGE is never granted on Android 13+. The
> file is therefore saved in the app's own Download folder on external storage
> (getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS)), which needs no permission. INTERNET is the
> only permission required. IntentService is used as requested, although it is deprecated since API 30.

---

## 7. Tester, dans cet ordre

Il te faut un émulateur (**Tools > Device Manager**) avec **Internet**, ou ton téléphone en
débogage USB.

| # | Ce que tu fais | Ce que tu dois voir |
|---|---|---|
| 1 | Lance l'application (▶) | le formulaire du TP1 |
| 2 | Valide avec le nom vide | le Toast « Entrez au moins un nom » |
| 3 | Remplis nom et email, OK | l'écran 2 avec ton nom ; Logcat, filtre `tag:SecondActivity` : ton email |
| 4 | NEXT | « Telechargement des evenements... », puis « 15 evenements » et la liste EVENT1 à EVENT15 |
| 5 | Logcat, filtre `tag:DownloadService` | `Connexion a https://drive…`, `Fichier enregistre : /storage/emulated/0/Android/data/com.cyu.tp2events/files/Download/events.txt`, `15 evenements enregistres dans la base` |
| 6 | Logcat, filtre `tag:ThirdActivity` | 15 lignes `ID: 1, NAME: EVENT1, LAT: 48.863429, LNG: 2.388223, TYPE: TYPE3` … (3.1.1 du sujet) |
| 7 | Clique sur EVENT1 | une boîte « EVENT1 » avec `Latitude : 48.863429`, `Longitude : 2.388223`, `Type : TYPE3` |
| 8 | Ferme l'application (applications récentes, balaie-la), puis rouvre-la | elle s'ouvre **directement sur l'écran 2** (partie 1 du sujet) |
| 9 | NEXT | la liste s'affiche **tout de suite**, sans « Telechargement » : elle vient de la base |
| 10 | **App Inspection > Database Inspector** (en bas de Studio, application lancée) | `events.db` > `TABLE_EVENTS`, avec les colonnes `ID NAME LAT LNG TYPE` et 15 lignes |
| 11 | **Device Explorer** > `sdcard/Android/data/com.cyu.tp2events/files/Download/` | `events.txt` |
| 12 | Mode avion, désinstalle, relance, va jusqu'à l'écran 3 | « Echec du telechargement (voir Logcat) » ; l'application ne plante pas |

**Corrigé après ton premier test (02/11) : la liste était presque illisible.** Ton téléphone est en
**mode sombre** : le thème écrit donc le texte en **blanc**. Mais `activity_third.xml` (venu du TP1)
imposait un fond clair `android:background="#FFF3E0"`, d'où du blanc sur crème. J'ai retiré cette
ligne : l'écran prend maintenant le fond du thème, sombre en mode sombre, clair en mode clair. Leçon :
ne fixe jamais une couleur de fond sans fixer aussi la couleur du texte, ou laisse le thème choisir
les deux.

**Pour tout recommencer à zéro** : désinstalle l'application (appui long sur l'icône > Désinstaller).
Ça efface les préférences, la base **et** `events.txt`, parce que les trois sont dans les dossiers de
l'application.

**Captures utiles pour le rendu** : étapes 3, 4, 6, 7, 10. Si tu veux que je les vérifie, envoie-les.

**Si ça ne marche pas** : copie les lignes rouges de Logcat, ou l'onglet *Build*, et envoie-les. Ne
change rien au hasard avant.

---

## 8. Rendre

Le sujet ne dit pas sous quelle forme rendre. **Regarde la consigne sur Moodle** (zip du projet ?
APK ? captures ? compte rendu ?). Si c'est le projet en zip :

**File > Export > Export to Zip File…** dans Android Studio. Ça exclut les dossiers `build/` et
`.gradle/` (des centaines de Mo, inutiles : le prof les régénère en compilant).

Si un compte rendu est demandé, il contient : les captures de la partie 7, la phrase de la partie 6,
et pour chaque partie du sujet, le nom du fichier et de la méthode qui la réalisent (le tableau de la
partie 2 suffit).

---

## 9. Vérifie que tu as compris (réponds avant de lire le corrigé)

1. Pourquoi l'application ne repasse-t-elle pas par le formulaire au deuxième lancement ? Et
   pourquoi `finish()` juste après ?
2. Pourquoi le téléchargement est-il dans un `IntentService` ? Qu'est-ce qui se passe si tu
   l'appelles directement dans `onCreate` ?
3. Que vaut `n` au dernier tour de la boucle de copie, pour un fichier de 531 octets ? Qu'est-ce
   que `write(tampon)` écrirait à la place de `write(tampon, 0, n)` ?
4. Tu ajoutes une colonne `DATE` dans `onCreate` de `EventDbHelper`, tu relances : plantage
   « no such column: DATE ». Pourquoi ? Deux façons de corriger ?
5. Pourquoi le receiver est-il inscrit dans `onResume` et pas dans `onCreate` ? Et pourquoi
   `afficher()` est-il aussi appelé dans `onResume` ?
6. Pourquoi n'a-t-on pas besoin de `WRITE_EXTERNAL_STORAGE` ?
7. Que fait `layout_weight="1"` avec `layout_height="0dp"` ?

### Corrigé

1. Le nom est dans SharedPreferences : `onCreate` de MainActivity le trouve et ouvre directement
   SecondActivity. `finish()` retire le formulaire de la pile : sinon, Retour depuis l'écran 2
   ramènerait au formulaire.
2. Le réseau est interdit sur le thread principal (`NetworkOnMainThreadException`) et figerait
   l'écran. `onHandleIntent` tourne dans un thread à part. Dans `onCreate` : l'exception, et rien
   n'est téléchargé.
3. 531 < 4096 : si tout arrive d'un coup, un seul tour utile avec `n = 531` (le réseau peut aussi
   livrer en plusieurs morceaux, `n` est alors plus petit à chaque tour). `write(tampon)` écrirait
   les 4096 octets du tampon : 531 octets utiles suivis de 3565 octets nuls. Avec plusieurs tours, ce
   seraient les restes du tour précédent.
4. `onCreate` ne tourne que si la base n'existe pas : l'ancienne table, sans `DATE`, est toujours là.
   Désinstaller l'application (la base est supprimée avec), ou passer `DB_VERSION` à 2 pour que
   `onUpgrade` recrée la table.
5. Pour ne recevoir que quand l'écran est visible, et désinscrire dans `onPause` pour éviter une fuite.
   Un message envoyé pendant que l'écran est caché est perdu ; mais les données sont déjà en base, donc
   `afficher()` dans `onResume` les montre quand même.
6. `getExternalFilesDir` est le dossier **de l'application** sur le stockage externe : aucune
   permission depuis Android 4.4. Le dossier `Download` commun, lui, n'est plus accessible par `File`
   depuis Android 10.
7. Dans un `LinearLayout` vertical, la vue prend toute la hauteur laissée par les autres vues. Le
   bouton reste en bas et la liste défile entre les deux.
