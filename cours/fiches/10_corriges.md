# 10. Corrigés

> **Ne lis une partie qu'après avoir écrit tes réponses sur papier.** Une réponse lue sans
> l'avoir cherchée donne l'impression de savoir : c'est cette impression qui coûte des
> points le jour de l'examen.
>
> À l'examen, une réponse de code est jugée sur **les bons choix** (bon service, bon
> listener, bonne permission, bon callback) bien plus que sur un point-virgule.

---

## Partie 01 : les bases

**1.1**
1. **Vrai.** Le noyau Linux gère les processus, la mémoire, les pilotes, la sécurité et
   l'énergie.
2. **Faux.** Il n'y a pas de `main` : le système crée l'activité et appelle `onCreate`
   (inversion de contrôle).
3. **Vrai.** `Activity` → `ContextThemeWrapper` → `ContextWrapper` → `Context`. C'est pour
   ça qu'on peut écrire `getSystemService(...)` ou passer `this` comme `Context`.
4. **Faux.** Chaque appli a son UID Linux et ses fichiers privés (bac à sable). Pour
   partager, on passe par un Content Provider.
5. **Faux.** Un composant non déclaré n'existe pas pour le système :
   `ActivityNotFoundException`.
6. **Faux.** ART a remplacé Dalvik depuis Android 5 (2014).

**1.2** AVD = *Android Virtual Device* (l'émulateur). ADB = *Android Debug Bridge* (outil en
ligne de commande pour parler au téléphone). AOSP = *Android Open Source Project* (la partie
libre d'Android). ART = *Android Runtime* (exécute le bytecode DEX). APK = *Android
Package* (le fichier installable).

**1.3** (exemples, d'autres sont valables)
- **Activity** : l'écran du menu, l'écran du panier.
- **Service** : suivre la position du livreur en arrière-plan, même écran éteint.
- **BroadcastReceiver** : être prévenu que la connexion revient pour envoyer une commande
  en attente ; ou réagir au démarrage du téléphone.
- **ContentProvider** : lire les contacts pour envoyer un code de parrainage ; ou offrir
  l'historique des commandes à une autre appli.

L'Intent **n'est pas** un composant : c'est le message qui les relie.

**1.4** Couche 5 : `MainActivity`. Couche 4 : `LocationManager`. Couche 3 : ART et SQLite.
Couche 1 : les pilotes Wi-Fi (la couche 2, la HAL, est l'interface standard entre le
système et ces pilotes).

**1.5**
```java
SensorManager sm = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
TelephonyManager tm = (TelephonyManager) getSystemService(Context.TELEPHONY_SERVICE);
```

**1.6** `findViewById` est appelé **avant** `setContentView` : l'arbre des vues n'existe pas
encore, `ok` vaut `null`, et `ok.setText(...)` lève une `NullPointerException`. Correction :
mettre `setContentView(R.layout.activity_main);` juste après `super.onCreate(b);`.

**1.7** `android:id="@+id/nom"` **crée** l'identifiant `nom` et le donne à cette vue.
`android:layout_below="@id/nom"` **fait référence** à une vue qui a déjà cet identifiant,
pour se placer par rapport à elle.

---

## Partie 02 : les activités

**2.1** Voir le diagramme du chapitre 02, section 2. Vérifie que tu as : les 7 callbacks
dans l'ordre, la flèche `onPause → onResume` (retour au premier plan), la flèche
`onStop → onRestart → onStart`, la flèche du processus tué (depuis l'état arrêté), et les
trois durées de vie : entière (`onCreate` à `onDestroy`), visible (`onStart` à `onStop`),
premier plan (`onResume` à `onPause`).

**2.2**
1. `A.onCreate → A.onStart → A.onResume`
2. `A.onPause → B.onCreate → B.onStart → B.onResume → A.onStop` (puis
   `A.onSaveInstanceState`)
3. `B.onPause → A.onRestart → A.onStart → A.onResume → B.onStop → B.onDestroy`
4. `A.onPause → A.onStop` (puis `A.onSaveInstanceState`)
5. `A.onRestart → A.onStart → A.onResume`

**Les points qui comptent à l'examen :** `A.onPause` **avant** la création de B ;
`A.onStop` **après** `B.onResume` ; au retour, `onRestart` et **pas** `onCreate` pour A ;
`B.onDestroy` car Back retire B de la pile.

**2.3** Démarrer dans **`onResume`**, arrêter dans **`onPause`** (la paire miroir). Pas
dans `onCreate`/`onDestroy` : `onCreate` n'a pas de miroir quand l'écran passe en
arrière-plan, donc GPS et capteur tourneraient pendant que l'appli est cachée ; et
`onDestroy` peut ne jamais être appelée si le processus est tué. Les deux vident la
batterie. Si la course doit être suivie **écran éteint**, il faut un **Service**
(chapitre 06).

**2.4** La rotation **détruit et recrée** l'activité : tout ce qui était dans les champs de
la classe est perdu. Correction : sauver dans le `Bundle`.

```java
private static final String KEY_MSG = "message";

@Override
protected void onSaveInstanceState(Bundle outState) {
    super.onSaveInstanceState(outState);
    outState.putString(KEY_MSG, saisie.getText().toString());
}

@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_main);
    saisie = (EditText) findViewById(R.id.saisie);
    if (savedInstanceState != null) {
        saisie.setText(savedInstanceState.getString(KEY_MSG));
    }
}
```

*Nuance (bonus) :* un `EditText` **qui a un `android:id`** sauve et restaure son texte tout
seul. Le texte se perd quand le champ n'a pas d'id, ou quand le message est gardé dans une
variable de la classe.

**2.5** `onDestroy` **n'est pas garantie** : si le système tue le processus pour récupérer
de la mémoire, elle n'est pas appelée et les notes sont perdues. Il faut sauver dans
**`onStop`** (l'endroit fiable), ou mieux, **dès que la donnée change**.

**2.6**
```java
// MainActivity
public static final String EXTRA_AGE = "fr.cyu.app.age";
public static final String EXTRA_VILLE = "fr.cyu.app.ville";

Intent i = new Intent(this, ProfilActivity.class);
i.putExtra(EXTRA_AGE, 21);
i.putExtra(EXTRA_VILLE, "Cergy");
startActivity(i);
```

```java
// ProfilActivity
@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_profil);
    Intent recu = getIntent();
    int age = recu.getIntExtra(MainActivity.EXTRA_AGE, 0);       // 0 = valeur par défaut
    String ville = recu.getStringExtra(MainActivity.EXTRA_VILLE);
    TextView info = (TextView) findViewById(R.id.info);
    info.setText(age + " ans, " + ville);
}
```

```xml
<activity android:name=".ProfilActivity" />
```

Piège : `getIntExtra` **exige** une valeur par défaut (2e argument), `getStringExtra` non.

**2.7**
1. **Vrai** dans le parcours normal. Exception : si on appelle `finish()` dans `onCreate`,
   le système passe directement à `onDestroy`.
2. **Faux.** Un processus tué pour libérer de la mémoire ne reçoit pas `onDestroy`.
3. **Faux.** L'activité est recréée : c'est un **nouvel objet**, ses champs repartent à
   zéro.
4. **Faux.** `A.onPause`, puis création de B, et `A.onStop` seulement **après**
   `B.onResume`.

---

## Partie 03 : Intents, manifeste, permissions

**3.1**
```java
// 1. Explicite
startActivity(new Intent(this, ParametresActivity.class));

// 2. Implicite
startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("https://www.cyu.fr")));

// 3. Implicite
startActivity(new Intent(Intent.ACTION_DIAL, Uri.parse("tel:0134251010")));

// 4. Implicite
startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("geo:49.0389,2.0749")));

// 5. Implicite
Intent sms = new Intent(Intent.ACTION_SENDTO, Uri.parse("smsto:0612345678"));
sms.putExtra("sms_body", "J'arrive");
startActivity(sms);
```
(Pour 2 à 5, l'idéal est d'entourer `startActivity` d'un `try / catch
(ActivityNotFoundException e)`.)

**3.2** **Aucune** permission pour les cinq. `ACTION_DIAL` remplit seulement le clavier ;
`ACTION_SENDTO` ouvre l'appli SMS, et c'est l'utilisateur qui appuie sur Envoyer. Les
permissions seraient nécessaires pour `ACTION_CALL` (`CALL_PHONE`) ou pour envoyer le SMS
soi-même avec `SmsManager` (`SEND_SMS`).

**3.3**
```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="fr.cyu.suivi">

    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.VIBRATE" />
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />

    <application
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name">

        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <activity android:name=".HistoriqueActivity" />

        <service android:name=".SuiviService" />

        <receiver android:name=".DemarrageReceiver" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
            </intent-filter>
        </receiver>
    </application>
</manifest>
```
**Ce qu'on vérifie :** les permissions **hors** de `<application>` ; `RECEIVE_BOOT_COMPLETED`
(souvent oubliée) ; MAIN + LAUNCHER sur la seule activité de démarrage ; le filtre
`BOOT_COMPLETED` sur le **receiver** (pas sur le service).

**3.4**
```xml
<uses-permission android:name="android.permission.CALL_PHONE" />
```
```java
private static final int CODE_APPEL = 1;

private void appeler112() {
    if (ContextCompat.checkSelfPermission(this, Manifest.permission.CALL_PHONE)
            != PackageManager.PERMISSION_GRANTED) {
        ActivityCompat.requestPermissions(this,
                new String[]{ Manifest.permission.CALL_PHONE }, CODE_APPEL);
    } else {
        startActivity(new Intent(Intent.ACTION_CALL, Uri.parse("tel:112")));
    }
}

@Override
public void onRequestPermissionsResult(int requestCode, String[] permissions,
                                       int[] grantResults) {
    super.onRequestPermissionsResult(requestCode, permissions, grantResults);
    if (requestCode == CODE_APPEL && grantResults.length > 0
            && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
        appeler112();
    }
}
```

**3.5** `INTERNET` est une permission **normale** : accordée automatiquement à
l'installation. `ACCESS_FINE_LOCATION` est **dangereuse** (elle touche à la vie privée) :
depuis Android 6 (API 23), l'utilisateur doit l'accepter **à l'exécution**, dans une
fenêtre, et peut la retirer à tout moment. La ligne du manifeste est nécessaire mais ne
suffit plus.

**3.6** Cause la plus probable : **aucune appli installée ne déclare de filtre pour le
schéma `geo:`** (pas d'appli de cartes), et l'appel n'était pas protégé. Exception :
**`ActivityNotFoundException`**. Protection : `try { startActivity(i); } catch
(ActivityNotFoundException e) { /* message à l'utilisateur */ }`.
Les autres pistes sont fausses : `CATEGORY_DEFAULT` est ajoutée automatiquement aux Intents
implicites ; `geo:` ne demande aucune permission ; `exported` concerne l'activité **qui
reçoit**, pas celle qui envoie.

**3.7**
```xml
<activity android:name=".LecteurActivity" android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data android:scheme="https" android:host="notes.cyu.fr" />
    </intent-filter>
</activity>
```
**`DEFAULT`** est indispensable : le système l'ajoute à **tout** Intent implicite, et un
filtre doit contenir toutes les catégories de l'Intent ; sans elle, l'activité n'est jamais
choisie. `BROWSABLE` permet qu'un lien cliqué dans un navigateur ou un message l'ouvre.
`exported="true"` car c'est une **autre** appli qui la lance.

---

## Partie 04 : l'interface

**4.1 (annale 1, ex. 2)**

| Vue | Horizontal | Vertical | Largeur |
|---|---|---|---|
| EditText `name` | toute la largeur intérieure | en haut | match_parent |
| Spinner `dates` | du bord **gauche** jusqu'au bord gauche de `times` (contraint des deux côtés : il s'étire) | sous `name` | 0dp → s'étire |
| Spinner `times` | collé à **droite** | sous `name` | **96dp** |
| Button | collé à **droite** | sous `times` | **96dp** |

```
┌────────────────────────────────────────────┐
│16dp                                    16dp│  padding gauche et droite seulement :
│  ┌──────────────────────────────────────┐  │  l'EditText touche le HAUT
│  │ Reminder name              (grisé)   │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────┐┌──────────┐  │
│  │                        ▾ ││        ▾ │  │  dates (s'étire)  |  times (96dp)
│  └──────────────────────────┘└──────────┘  │
│                              ┌──────────┐  │
│                              │   Done   │  │  bouton (96dp), sous times, à droite
│                              └──────────┘  │
│                                            │
│                  (vide)                    │
└────────────────────────────────────────────┘
```
**Bonus :** `@+id/times` porte un `+` dans `dates` parce que `times` est déclaré **plus
bas** dans le fichier : au moment où `dates` est lu, l'identifiant n'existe pas encore, le
`+` le crée à l'avance. Dans la déclaration de `times`, on écrit alors `@id/times` (sans
`+`), car il existe déjà.

**4.2 (annale 2, Q4)**

| Vue | Horizontal | Vertical | Taille |
|---|---|---|---|
| `tv_titre` | toute la largeur (Start + End), **texte centré** | en haut | s'étire en largeur |
| `rl_middle` | toute la largeur | sous le titre | hauteur = son plus grand enfant (160dp) |
| `imageView_ann` | du bord gauche jusqu'au prix | en haut du bloc | hauteur **160dp** |
| `tv_prix` | à droite | en haut du bloc | son texte |
| `tv_date` | à droite | sous le prix | son texte |
| `tv_vendeur` | toute la largeur, texte à gauche (par défaut) | sous le bloc | |

```
┌──────────────────────────────────────────┐
│       Vends trépied photographique       │  titre : toute la largeur, centré
│┌─────────────────────────────────┐ 300 € │  prix : en haut à droite
││                            04-07-2019   │  date : sous le prix, à droite,
││                                 │       │         elle DÉBORDE sur l'image
││         [ image ]  160dp        │       │  image : de la gauche jusqu'au prix
││                                 │       │
│└─────────────────────────────────┘       │
│Pro16 - Pontoise                          │  vendeur : sous le bloc, à gauche
│                                          │
│                 (vide)                   │
└──────────────────────────────────────────┘
```
**Remarque qui fait la différence :** l'image s'arrête au bord gauche de `tv_prix`. Or la
date « 04-07-2019 » est **plus large** que « 300 € » et elle est alignée à droite : elle
déborde donc vers la gauche et **chevauche le coin bas-droit de l'image**. Le signaler montre
que tu as compris que, dans un RelativeLayout, les vues ne se poussent pas.
**À signaler aussi :** le sujet contient des erreurs (balises `TextView` non fermées,
`layout_width`/`layout_height` manquants, qui sont obligatoires) : le fichier ne
compilerait pas tel quel.

**4.3**
```xml
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:padding="16dp">

    <ImageView android:id="@+id/photo"
        android:layout_width="80dp" android:layout_height="80dp"
        android:layout_alignParentTop="true"
        android:layout_alignParentLeft="true" />

    <TextView android:id="@+id/nom"
        android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:layout_toRightOf="@id/photo"
        android:layout_alignTop="@id/photo"
        android:layout_marginLeft="8dp"
        android:text="Awa Mensah" />

    <TextView android:id="@+id/statut"
        android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:layout_below="@id/nom"
        android:layout_alignLeft="@id/nom"
        android:text="Licence 3" />

    <Button android:id="@+id/deconnexion"
        android:layout_width="match_parent" android:layout_height="wrap_content"
        android:layout_alignParentBottom="true"
        android:text="Se déconnecter" />
</RelativeLayout>
```
Variantes acceptées : `alignParentStart`/`toEndOf`/`alignStart` à la place de
Left/Right ; `alignParentTop` sur `nom` au lieu de `alignTop`.

**4.4** LinearLayout (en ligne ou en colonne, poids), RelativeLayout (par rapport au parent
ou aux frères), ConstraintLayout (contraintes sur chaque bord, arbre plat), FrameLayout
(enfants empilés), TableLayout (lignes et colonnes avec `TableRow`), GridLayout (grille),
AbsoluteLayout (coordonnées fixes, déprécié).

**4.5**
```java
Button envoyer = (Button) findViewById(R.id.envoyer);

// 1. Classe anonyme
envoyer.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) { envoyer(); }
});

// 2. Lambda
envoyer.setOnClickListener(v -> envoyer());

// 3. L'activité implémente View.OnClickListener
//    class MainActivity extends Activity implements View.OnClickListener
envoyer.setOnClickListener(this);
@Override
public void onClick(View v) {
    if (v.getId() == R.id.envoyer) { envoyer(); }
}
```
4e façon : `android:onClick="surEnvoyer"` dans le XML, avec
`public void surEnvoyer(View v) { envoyer(); }` dans l'activité.

**4.6 (annale 2, Q2a)** Le code **branche un adaptateur sur la ListView** pour qu'elle
affiche **chaque élément de `myList` sur une ligne de texte**.
- `MyActivity.this` : le `Context` (on écrit `MyActivity.this` parce que ce code est
  souvent dans une classe anonyme, où `this` ne serait pas l'activité) ;
- `android.R.layout.simple_list_item_1` : le layout d'**une ligne**, fourni **par Android**
  (`android.R`), qui contient un seul `TextView` ;
- `myList` : les données ; l'adaptateur appelle `toString()` sur chaque élément.

```java
listview.setOnItemClickListener(new AdapterView.OnItemClickListener() {
    @Override
    public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
        Toast.makeText(MyActivity.this, myList.get(position).toString(),
                       Toast.LENGTH_SHORT).show();
    }
});
```
(`myList[position]` si `myList` est un tableau.)

**4.7**
- `dp` : taille indépendante de la densité de l'écran, pour les dimensions et marges.
  `sp` : pareil, mais suit aussi la taille de police choisie par l'utilisateur ; pour le
  texte (accessibilité).
- `padding` : espace **intérieur** (entre le bord de la vue et son contenu). `margin` :
  espace **extérieur** (entre la vue et ses voisines).
- `gravity` : position du **contenu** dans la vue. `layout_gravity` : position de **la
  vue** dans son parent.
- `invisible` : cachée mais **garde sa place**. `gone` : cachée et **libère sa place**.

**4.8**
1. Il manque **`.show()`** : le Toast est créé mais jamais affiché.
2. La durée doit être **`Toast.LENGTH_SHORT`** ou **`Toast.LENGTH_LONG`**, pas `2000`.
3. **`findViewById` avant `setContentView`** : renvoie `null`.

Corrigé :
```java
setContentView(R.layout.activity_main);
TextView t = (TextView) findViewById(R.id.titre);
Toast.makeText(this, "Sauvegardé", Toast.LENGTH_SHORT).show();
```

---

## Partie 05 : les données

**5.1 (annale 1, ex. 1.1)** Voir le tableau du chapitre 05, section 1. La réponse attendue
en 5 points :
1. **SharedPreferences** (clé/valeur, réglages) : `SharedPreferences`,
   `SharedPreferences.Editor`, `PreferenceManager`.
2. **Bundle** (état temporaire d'un écran) : `onSaveInstanceState` /
   `onRestoreInstanceState`.
3. **Fichiers internes** : `openFileOutput` / `openFileInput` du `Context`,
   `FileOutputStream` / `FileInputStream`.
4. **Fichiers externes** (carte SD) : `Environment`, permission `WRITE_EXTERNAL_STORAGE`.
5. **Base SQLite** : `SQLiteOpenHelper`, `SQLiteDatabase`, `Cursor`, `ContentValues`.

Et pour partager : **Content Provider** (`ContentProvider`, `ContentResolver`).

**5.2**
```java
@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_main);

    SharedPreferences prefs = getSharedPreferences("stats", Context.MODE_PRIVATE);
    int n = prefs.getInt("lancements", 0) + 1;
    SharedPreferences.Editor editor = prefs.edit();
    editor.putInt("lancements", n);
    editor.commit();
    Toast.makeText(this, "Ouverture n° " + n, Toast.LENGTH_SHORT).show();
}
```
*Bonus :* `onCreate` est aussi appelée à **chaque rotation**. Pour ne compter que les vraies
ouvertures, n'incrémenter que si `savedInstanceState == null`.

**5.3**
1. **SharedPreferences** : un simple réglage clé/valeur.
2. **SQLite** : beaucoup de données structurées, à trier et filtrer.
3. **Bundle** (`onSaveInstanceState`) : état temporaire de l'écran.
4. **Stockage externe** partagé (aujourd'hui via MediaStore) : gros fichier, visible par la
   galerie.
5. **Content Provider** des contacts, via le `ContentResolver`, avec `READ_CONTACTS`.

**5.4**
```java
public class LivresHelper extends SQLiteOpenHelper {

    public LivresHelper(Context context) {
        super(context, "biblio.db", null, 1);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE livres ("
                + "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                + "titre TEXT, "
                + "auteur TEXT, "
                + "annee INTEGER)");
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS livres");
        onCreate(db);
    }
}
```

**5.5**
```java
LivresHelper helper = new LivresHelper(this);
SQLiteDatabase db = helper.getWritableDatabase();

// 1. Insérer
ContentValues cv = new ContentValues();
cv.put("titre", "L'Enfant noir");
cv.put("auteur", "Camara Laye");
cv.put("annee", 1953);
db.insert("livres", null, cv);

// 2. Lire les livres après 1950, triés par année
Cursor c = db.rawQuery(
        "SELECT titre, auteur, annee FROM livres WHERE annee > ? ORDER BY annee",
        new String[]{ "1950" });
while (c.moveToNext()) {
    Log.d("Biblio", c.getString(0) + " (" + c.getString(1) + ", " + c.getInt(2) + ")");
}
c.close();

// 3. Supprimer les livres d'un auteur, sans injection SQL
db.delete("livres", "auteur = ?", new String[]{ auteur });

db.close();
```
Note : avec `ContentValues`, l'apostrophe de « L'Enfant » ne pose aucun problème. Dans une
chaîne SQL écrite à la main, elle casserait la requête : une raison de plus de préférer
`ContentValues` et les `?`.

**5.6 (annale 2, Q3c)**
```java
MaBase helper = new MaBase(this);
SQLiteDatabase db = helper.getWritableDatabase();

ContentValues cv = new ContentValues();
cv.put("lat", String.valueOf(latitude));      // colonnes VARCHAR → on stocke du texte
cv.put("lng", String.valueOf(longitude));
db.insert("locations", null, cv);

db.close();
```
Variante acceptée :
`db.execSQL("INSERT INTO locations (lat, lng) VALUES (?, ?)", new Object[]{ latitude, longitude });`
**Les points notés :** `getWritableDatabase()` (pas `Readable`), le nom de la table et des
colonnes, la conversion en texte.

**5.7** Schéma `content://`, autorité `com.android.contacts`, chemin `contacts`, identifiant
`12` (le contact d'id 12). Permission : `READ_CONTACTS`.

**5.8**
1. **Faux** : privée à l'appli qui l'a créée.
2. **Faux** : seulement la première fois qu'on demande la base et qu'elle n'existe pas.
3. **Vrai.**
4. **Vrai.**

---

## Partie 06 : services, broadcasts, téléphonie

**6.1 (annale 2, Q1 g, h, j)**
1. **Faux.** Il s'exécute dans le thread principal ; c'est à lui de lancer un thread pour
   le travail lourd.
2. **Faux.** Elle est appelée à **chaque** `startService`.
3. **Faux.** `onCreate` de l'activité principale n'est appelée que **quand l'utilisateur
   ouvre l'appli**, pas au démarrage du téléphone.
4. **Vrai.** On déclare dans le manifeste un **BroadcastReceiver** avec un intent-filter
   `BOOT_COMPLETED` (+ permission `RECEIVE_BOOT_COMPLETED`), et son `onReceive` appelle
   `startService`. *(Précise bien que le filtre est sur le receiver, qui démarre le
   service.)*
5. **Faux.** `onReceive` doit finir en **moins de 10 secondes** ; un travail long doit être
   confié à un service (ou à WorkManager).
6. **`android.intent.action.BOOT_COMPLETED`** (`Intent.ACTION_BOOT_COMPLETED`).

**6.2**
```java
public class CompteurService extends Service {
    private volatile boolean actif = true;

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        new Thread(new Runnable() {
            @Override
            public void run() {
                for (int i = 0; i < 60 && actif; i++) {
                    Log.d("Compteur", "tic " + i);
                    try {
                        Thread.sleep(1000);
                    } catch (InterruptedException e) {
                        return;
                    }
                }
                stopSelf();                       // s'arrête tout seul à la fin
            }
        }).start();
        return START_NOT_STICKY;
    }

    @Override
    public IBinder onBind(Intent intent) { return null; }

    @Override
    public void onDestroy() {
        super.onDestroy();
        actif = false;                            // arrête la boucle si on stoppe avant
    }
}
```
```java
// Dans l'activité
startService(new Intent(this, CompteurService.class));
```
```xml
<service android:name=".CompteurService" />
```
**Ce qui est noté :** le `Thread` (sinon `Thread.sleep` gèlerait l'interface pendant une
minute) ; `stopSelf()` ; la déclaration dans le manifeste. `START_STICKY` serait aussi
accepté.

**6.3**
```java
// 1. Dans le service
Intent annonce = new Intent("fr.cyu.action.COMPTEUR");
annonce.putExtra("valeur", n);
sendBroadcast(annonce);
```
```java
// 2. Dans l'activité
private BroadcastReceiver receveur = new BroadcastReceiver() {
    @Override
    public void onReceive(Context context, Intent intent) {
        int v = intent.getIntExtra("valeur", 0);
        texte.setText("Compteur : " + v);
    }
};

// 3. Enregistrer et désinscrire (paire miroir)
@Override
protected void onResume() {
    super.onResume();
    registerReceiver(receveur, new IntentFilter("fr.cyu.action.COMPTEUR"));
}

@Override
protected void onPause() {
    super.onPause();
    unregisterReceiver(receveur);
}
```
🕰️ Depuis Android 14, pour un receiver dynamique qui écoute une annonce **qui n'est pas
du système**, il faut préciser s'il est exporté :
`ContextCompat.registerReceiver(this, receveur, filtre, ContextCompat.RECEIVER_NOT_EXPORTED)`.

**6.4** Le manifeste et le receiver du chapitre 06, section 4, avec `SauvegardeService` :
la permission `RECEIVE_BOOT_COMPLETED`, le `<service>`, le `<receiver>` avec le filtre
`BOOT_COMPLETED`, et `context.startService(new Intent(context, SauvegardeService.class))`
dans `onReceive`.

**6.5 (annale 1, ex. 3)**
```java
private class MyPhoneListener extends PhoneStateListener {
    private boolean onCall = false;
    private long debutAppel = 0;

    @Override
    public void onCallStateChanged(int state, String incomingNumber) {
        switch (state) {
            case TelephonyManager.CALL_STATE_RINGING:
                // Appel entrant : le numéro n'est disponible qu'ici
                Toast.makeText(getApplicationContext(),
                        "Appel entrant de " + incomingNumber, Toast.LENGTH_LONG).show();
                break;

            case TelephonyManager.CALL_STATE_OFFHOOK:
                // Décroché : une communication commence
                onCall = true;
                debutAppel = System.currentTimeMillis();
                Toast.makeText(getApplicationContext(),
                        "Communication en cours", Toast.LENGTH_SHORT).show();
                break;

            case TelephonyManager.CALL_STATE_IDLE:
                // Au repos : si on était en appel, l'appel vient de se terminer
                if (onCall) {
                    long duree = (System.currentTimeMillis() - debutAppel) / 1000;
                    Toast.makeText(getApplicationContext(),
                            "Fin d'appel, durée : " + duree + " s", Toast.LENGTH_LONG).show();
                    onCall = false;
                }
                break;

            default:
                break;
        }
    }
}
```
```java
// Enregistrer le listener (dans onCreate par exemple)
TelephonyManager tm = (TelephonyManager) getSystemService(Context.TELEPHONY_SERVICE);
tm.listen(new MyPhoneListener(), PhoneStateListener.LISTEN_CALL_STATE);
```
```xml
<uses-permission android:name="android.permission.READ_PHONE_STATE" />
<uses-permission android:name="android.permission.READ_CALL_LOG" />  <!-- numéro, Android 10+ -->
```
**Ce qui est noté :** les **`break`** (sans eux, RINGING exécuterait aussi le code
d'OFFHOOK et d'IDLE) ; `onCall = true` + l'heure de début en OFFHOOK ; le **test
`if (onCall)`** en IDLE (IDLE arrive aussi sans appel, et dès l'enregistrement du
listener) ; la remise à `false` ; la durée = fin moins début.

**6.6** `doInBackground` : thread d'**arrière-plan**, **interdit** de toucher à
l'interface. `onProgressUpdate` : thread **principal**. `onPostExecute` : thread
**principal**, reçoit le résultat.

**6.7** Le téléchargement s'exécute **sur le thread principal** (le listener y tourne) :
l'interface est bloquée 8 secondes, ce qui déclenche un **ANR** (plus de 5 s). En réalité,
Android refuse même tout accès réseau sur le thread principal et lève
`NetworkOnMainThreadException`. Correction :
```java
bouton.setOnClickListener(v -> new Thread(() -> {
    String page = telechargerPage("https://cyu.fr");     // arrière-plan
    runOnUiThread(() -> texte.setText(page));            // retour sur le thread UI
}).start());
```

---

## Partie 07 : les capteurs

**7.1** `TYPE_ACCELEROMETER` inclut la **gravité** ; `TYPE_LINEAR_ACCELERATION` l'**exclut**
(seulement l'accélération due au mouvement). Posé à plat, l'accéléromètre donne environ
**(0 ; 0 ; 9,81)** m/s² : la gravité sur l'axe z.

**7.2**
1. **Proximité** (`TYPE_PROXIMITY`).
2. **Champ magnétique + accéléromètre** (ou `TYPE_ROTATION_VECTOR`, ou l'ancien
   `TYPE_ORIENTATION`).
3. **Accéléromètre** (pic soudain de la norme, ou chute libre proche de 0).
4. **Lumière** (`TYPE_LIGHT`).

**7.3**
```java
public class LumiereActivity extends Activity implements SensorEventListener {

    private SensorManager sm;
    private Sensor lumiere;
    private TextView valeur;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_lumiere);
        valeur = (TextView) findViewById(R.id.valeur);
        sm = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
        lumiere = sm.getDefaultSensor(Sensor.TYPE_LIGHT);
        if (lumiere == null) {
            valeur.setText("Pas de capteur de lumière");
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (lumiere != null) {
            sm.registerListener(this, lumiere, SensorManager.SENSOR_DELAY_NORMAL);
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        sm.unregisterListener(this);
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        valeur.setText(event.values[0] + " lx");
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) { }
}
```

**7.4** `onCreate` n'est appelée qu'une fois et n'a pas de miroir quand l'écran passe en
arrière-plan : le capteur continuerait d'envoyer des mesures alors que personne ne regarde.
`onResume`/`onPause` forment la paire « premier plan ». Sans `unregisterListener`, le
capteur reste actif **même écran éteint** (le système ne le coupe pas) : la batterie se vide.

**7.5**
```java
@Override
public void onSensorChanged(SensorEvent event) {
    float x = event.values[0], y = event.values[1], z = event.values[2];
    double norme = Math.sqrt(x * x + y * y + z * z);
    if (norme > 25) {
        Vibrator v = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);
        v.vibrate(500);
    }
}
```
Permission : `<uses-permission android:name="android.permission.VIBRATE" />`.

---

## Partie 08 : la localisation

**8.1**
- **GPS** : + très précis (quelques mètres), + marche partout en extérieur sans réseau ;
  − consomme beaucoup, − lent au premier calcul et mauvais en intérieur.
- **Réseau** : + rapide, + peu gourmand, + marche en intérieur ; − moins précis (dizaines à
  centaines de mètres), − dépend de la couverture réseau / Wi-Fi.

**8.2**
- 48° 51' 24" = 48 + 51/60 + 24/3600 = 48 + 0,85 + 0,00667 = **48,8567**
- 2° 21' 7" = 2 + 21/60 + 7/3600 = 2 + 0,35 + 0,00194 = **2,3519** (c'est Paris)
- 40° 26' 46" S = −(40 + 0,43333 + 0,01278) = **−40,4461**
- 79° 58' 56" O = −(79 + 0,96667 + 0,01556) = **−79,9822**

**8.3 (annale 2, Q3)**

a. Accéder au service :
```java
LocationManager lm = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
```

b. Surveiller avec le GPS, 1 minute et 1 km :
```java
LocationListener ecouteur = new LocationListener() {
    @Override
    public void onLocationChanged(Location location) {
        enregistrer(location.getLatitude(), location.getLongitude());   // voir c.
    }
    @Override public void onProviderDisabled(String provider) { }
    @Override public void onProviderEnabled(String provider) { }
    @Override public void onStatusChanged(String provider, int status, Bundle extras) { }
};

lm.requestLocationUpdates(LocationManager.GPS_PROVIDER,
                          60000,     // 1 minute = 60 000 ms
                          1000,      // 1 km = 1 000 m
                          ecouteur);
```

c. Enregistrer en base (même code que 5.6) :
```java
private void enregistrer(double latitude, double longitude) {
    SQLiteDatabase db = new MaBase(this).getWritableDatabase();
    ContentValues cv = new ContentValues();
    cv.put("lat", String.valueOf(latitude));
    cv.put("lng", String.valueOf(longitude));
    db.insert("locations", null, cv);
    db.close();
}
```

d. Les autorisations : le manifeste **et** la demande à l'exécution.
```xml
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
```
```java
if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION)
        != PackageManager.PERMISSION_GRANTED) {
    ActivityCompat.requestPermissions(this,
            new String[]{ Manifest.permission.ACCESS_FINE_LOCATION }, 1);
} else {
    lm.requestLocationUpdates(LocationManager.GPS_PROVIDER, 60000, 1000, ecouteur);
}
// + onRequestPermissionsResult qui lance requestLocationUpdates si accordée
```
**Bonus qui montre la maîtrise :** pour surveiller la position **en continu, même appli
fermée**, le suivi doit vivre dans un **Service** (comme l'exemple 1 du cours 6), et
aujourd'hui il faut en plus `ACCESS_BACKGROUND_LOCATION` ou un service de premier plan.

**8.4 (annale 1, ex. 4)**

1.a.
```java
public Address locationToAddress(Location location) {
    Geocoder geocoder = new Geocoder(this, Locale.getDefault());
    try {
        List<Address> adresses = geocoder.getFromLocation(
                location.getLatitude(), location.getLongitude(), 1);   // 1 résultat suffit
        if (adresses != null && !adresses.isEmpty()) {
            return adresses.get(0);                                    // la première
        }
    } catch (IOException e) {
        Log.e("Geo", "Géocodage impossible", e);
    }
    return null;                                                       // aucune adresse
}
```
1.b. Le **géocodage inverse** (*reverse geocoding*) : coordonnées → adresse.

1.c. Au choix parmi : `getAddressLine(0)` (adresse complète), `getThoroughfare()` (rue),
`getSubThoroughfare()` (numéro), `getLocality()` (ville), `getPostalCode()` (code postal),
`getAdminArea()` (région), `getCountryName()` (pays), `getCountryCode()`,
`getFeatureName()`, `getLatitude()`, `getLongitude()`.

1.d. **Non.** Le niveau de détail dépend du **lieu** et des **données du serveur** : en
ville on obtient souvent le numéro et la rue, ailleurs seulement la ville, la région ou le
pays, et parfois aucun résultat (en mer, zone mal cartographiée). Cela dépend aussi de la
**précision** de la position fournie, et le service exige une connexion.

2.a.
```java
private class GPSListener implements LocationListener {
    @Override
    public void onLocationChanged(Location location) {
        String msg = "Nouvelle position : " + location.getLatitude()
                   + ", " + location.getLongitude();
        Toast.makeText(getApplicationContext(), msg, Toast.LENGTH_SHORT).show();
    }
    @Override public void onProviderDisabled(String provider) { }
    @Override public void onProviderEnabled(String provider) { }
    @Override public void onStatusChanged(String provider, int status, Bundle extras) { }
}
```
2.b. Elle est appelée **par le système**, via le service de localisation
(`LocationManager`), **chaque fois qu'une nouvelle position est disponible** et que les
seuils `minTime` / `minDistance` donnés à `requestLocationUpdates` sont respectés. Elle
n'est appelée qu'**après** l'enregistrement du listener avec `requestLocationUpdates`. Ni
l'utilisateur ni l'Activity Manager ne l'appellent ; c'est un **callback**.

**8.5**
1. `Context.SENSOR_SERVICE` au lieu de **`Context.LOCATION_SERVICE`** : le système renvoie
   un `SensorManager`, et le cast en `LocationManager` plante
   (`ClassCastException`).
2. Les **unités** : `5` et `10` veulent dire **5 millisecondes** et **10 mètres**, donc des
   mises à jour en rafale qui vident la batterie. Pour 5 minutes et 10 km, il faut
   **`300000`** (5 × 60 × 1000) et **`10000`**.

**8.6**
```java
public class PositionActivity extends Activity {

    private LocationManager lm;
    private TextView lat, lng;

    private final LocationListener ecouteur = new LocationListener() {
        @Override
        public void onLocationChanged(Location location) {
            lat.setText(String.valueOf(location.getLatitude()));
            lng.setText(String.valueOf(location.getLongitude()));
        }
        @Override public void onProviderDisabled(String provider) { }
        @Override public void onProviderEnabled(String provider) { }
        @Override public void onStatusChanged(String provider, int status, Bundle extras) { }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_position);
        lat = (TextView) findViewById(R.id.lat);
        lng = (TextView) findViewById(R.id.lng);
        lm = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_COARSE_LOCATION)
                == PackageManager.PERMISSION_GRANTED) {
            lm.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, 10000, 20, ecouteur);
        } else {
            ActivityCompat.requestPermissions(this,
                    new String[]{ Manifest.permission.ACCESS_COARSE_LOCATION }, 1);
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        lm.removeUpdates(ecouteur);
    }
}
```
Permission : `ACCESS_COARSE_LOCATION` suffit pour le fournisseur réseau
(`ACCESS_FINE_LOCATION` marche aussi, car elle l'inclut).

**8.7** `GeoPoint` stocke les coordonnées en **micro-degrés entiers** (`int`), pas en
`double`. Multiplier par 10⁶ (`1E6`) garde 6 décimales, soit une précision d'environ 10 cm,
tout en évitant les nombres à virgule.

---

## Partie 09 : l'examen blanc

### Exercice 1

a. `onPause → onStop` quand l'écran d'appel passe devant, puis `onRestart → onStart →
onResume` au retour. (Comme le bouton Accueil.)

b. Un **Service** est un **composant** Android (cycle de vie, déclaré dans le manifeste,
priorité élevée, peut vivre sans écran). Un **Thread** est un **fil d'exécution**. Un
service tourne **dans le thread principal** : à lui seul, il **n'évite pas** de bloquer
l'interface ; il faut lancer un thread à l'intérieur.

c. **Explicite** : on nomme la classe, pour naviguer dans son appli :
`new Intent(this, DetailActivity.class)`. **Implicite** : on décrit l'action, le système
trouve une appli : `new Intent(Intent.ACTION_VIEW, Uri.parse("https://cyu.fr"))`.

d. Normales : `INTERNET`, `VIBRATE`, `WAKE_LOCK`, `RECEIVE_BOOT_COMPLETED`. Dangereuses :
`ACCESS_FINE_LOCATION`, `SEND_SMS`, `READ_CONTACTS`, `CALL_PHONE`, `CAMERA`,
`READ_PHONE_STATE`. Depuis Android 6, les dangereuses doivent **en plus** être demandées
**à l'exécution** (l'utilisateur accepte ou refuse, et peut retirer son accord) ; les
normales sont accordées à l'installation.

e. Un composant qui **expose les données d'une appli aux autres applis** sous forme de
table, avec une interface commune (query, insert, update, delete), accessible via le
`ContentResolver` et protégée par des permissions. URI :
`content://<autorité>/<chemin>/<identifiant optionnel>`.

f. 1. **Faux** (une boîte de dialogue ou le mode multi-fenêtre : `onPause` puis directement
`onResume`, sans `onStop`). 2. **Faux** (`ACTION_DIAL` ne fait que remplir le clavier).
3. **Vrai.** 4. **Vrai** (aucune position encore connue).

### Exercice 2

| Vue | Horizontal | Vertical | Taille |
|---|---|---|---|
| `pochette` | centrée | en haut | 160 × 160dp |
| `titre` | centré | sous la pochette | son texte |
| `artiste` | **bord gauche aligné sur celui du titre** (pas centré !) | sous le titre | son texte |
| `barre` | toute la largeur | sous l'artiste | match_parent |
| `debut` | à gauche | sous la barre | « 0:00 » |
| `fin` | à droite | sous la barre | « 3:45 » |
| `lecture` | centré | **en bas** | 120dp |
| `precedent` | du bord gauche jusqu'à `lecture` (s'étire) | en bas | 0dp → s'étire |
| `suivant` | **commence** au bord droit de `lecture`, largeur de son texte | en bas | wrap_content |

```
┌────────────────────────────────────────────┐
│               ┌────────────┐               │
│               │            │               │
│               │  pochette  │ 160 × 160dp   │
│               │            │               │
│               └────────────┘               │
│              Titre du morceau              │
│              Artiste                       │  aligné à GAUCHE du titre
│  ────────────────●──────────────────────   │  barre : toute la largeur
│  0:00                                3:45  │
│                                            │
│                  (vide)                    │
│                                            │
│ ┌──────────────┐┌──────────┐┌─────────┐    │
│ │  Précédent   ││ Lecture  ││ Suivant │    │  Suivant ne va PAS jusqu'au bord
│ └──────────────┘└──────────┘└─────────┘    │
└────────────────────────────────────────────┘
```
**Les deux pièges :** `artiste` est aligné sur le **bord gauche** du titre, pas centré ; et
`suivant` n'a pas `alignParentRight` : il démarre après `lecture` et ne fait que la largeur
de son texte, contrairement à `precedent` qui s'étire (contraint des deux côtés).

### Exercice 3

```java
(1) SensorEventListener
(2) (TextView) findViewById(R.id.etat)
(3) (SensorManager) getSystemService(Context.SENSOR_SERVICE)
(4) sm.getDefaultSensor(Sensor.TYPE_PROXIMITY)
(5) if (proximite != null) {
        sm.registerListener(this, proximite, SensorManager.SENSOR_DELAY_NORMAL);
    }
(6) sm.unregisterListener(this);
(7) if (event.values[0] < proximite.getMaximumRange()) {
        etat.setText("Proche");
    } else {
        etat.setText("Loin");
    }
```

### Exercice 4

a. `ACCESS_FINE_LOCATION` : position précise par GPS (dangereuse : demande à l'exécution).
`INTERNET` : le géocodage inverse se fait sur un serveur. (`ACCESS_COARSE_LOCATION` en plus
si on veut le fournisseur réseau.)

b. **SharedPreferences** : deux petites valeurs, qui doivent survivre à la fermeture de
l'appli et au redémarrage. Une base SQLite serait disproportionnée, et un `Bundle` ne
survit pas à la fermeture.
```java
LocationManager lm = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
Location ici = lm.getLastKnownLocation(LocationManager.GPS_PROVIDER);
if (ici == null) {
    Toast.makeText(this, "Position inconnue, réessaie dehors", Toast.LENGTH_SHORT).show();
    return;
}
SharedPreferences.Editor editor =
        getSharedPreferences("voiture", Context.MODE_PRIVATE).edit();
editor.putString("lat", String.valueOf(ici.getLatitude()));
editor.putString("lng", String.valueOf(ici.getLongitude()));
editor.commit();
```
On stocke en `String` car les SharedPreferences n'ont pas de `putDouble`, et `putFloat`
perdrait de la précision.

c. Processus : **géocodage inverse**.
```java
SharedPreferences prefs = getSharedPreferences("voiture", Context.MODE_PRIVATE);
String latTxt = prefs.getString("lat", null);
if (latTxt == null) {
    Toast.makeText(this, "Aucune voiture enregistrée", Toast.LENGTH_SHORT).show();
    return;
}
double lat = Double.parseDouble(latTxt);
double lng = Double.parseDouble(prefs.getString("lng", "0"));

Geocoder geocoder = new Geocoder(this, Locale.getDefault());
try {
    List<Address> adresses = geocoder.getFromLocation(lat, lng, 1);
    if (adresses != null && !adresses.isEmpty()) {
        Toast.makeText(this, adresses.get(0).getAddressLine(0), Toast.LENGTH_LONG).show();
    } else {
        Toast.makeText(this, "Adresse introuvable", Toast.LENGTH_SHORT).show();
    }
} catch (IOException e) {
    Toast.makeText(this, "Pas de connexion", Toast.LENGTH_SHORT).show();
}
```

d.
```java
private final LocationListener suivi = new LocationListener() {
    @Override
    public void onLocationChanged(Location ici) {
        Location voiture = new Location("voiture");
        voiture.setLatitude(latVoiture);
        voiture.setLongitude(lngVoiture);
        float metres = ici.distanceTo(voiture);
        distance.setText(Math.round(metres) + " m");
    }
    @Override public void onProviderDisabled(String provider) { }
    @Override public void onProviderEnabled(String provider) { }
    @Override public void onStatusChanged(String provider, int status, Bundle extras) { }
};

@Override
protected void onResume() {
    super.onResume();
    lm.requestLocationUpdates(LocationManager.GPS_PROVIDER, 5000, 10, suivi);
}

@Override
protected void onPause() {
    super.onPause();
    lm.removeUpdates(suivi);
}
```
On l'enregistre dans **`onResume`** et on le retire dans **`onPause`** : la distance n'a
d'intérêt que tant que l'écran est au premier plan, et le GPS est le capteur le plus
gourmand du téléphone.
