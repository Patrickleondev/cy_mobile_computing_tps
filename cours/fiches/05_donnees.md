# 05. Stocker des données

> Source : cours 3 (*Files, Preferences, and Content Provider*). Corrigé :
> `10_corriges.md`, partie 05.
> Questions d'examen liées : **annale 1, ex. 1.1** (« de quelles manières stocke-t-on des
> données en local, et quels gestionnaires sont impliqués ? »), **annale 2, Q1i** (SQLite
> locale ou distante ?) et **Q3c** (insérer des coordonnées dans une table SQLite).

---

## 1. Pourquoi sauver, et où

Le système peut tuer ton appli **à tout moment** (chapitre 02). Une appli doit donc sauver
ses données **chaque fois qu'elle passe en arrière-plan**, même si tu penses qu'elle reste
toujours au premier plan : un appel, une autre appli ou simplement l'usage normal d'un
téléphone suffisent à l'interrompre.

**Le tableau qui répond à l'annale 1, ex. 1.1 :**

| Moyen | Pour quoi | Les classes (« gestionnaires ») impliquées | Où sur le téléphone |
|---|---|---|---|
| **SharedPreferences** | petites valeurs **clé/valeur** : réglages, pseudo, dernier score | `SharedPreferences`, `SharedPreferences.Editor`, `PreferenceManager` | `/data/data/<package>/shared_prefs/<nom>.xml` |
| **Bundle** (état d'instance) | l'état **temporaire** d'un écran (texte en cours, position) | `Bundle`, via `onSaveInstanceState` / `onRestoreInstanceState` | en mémoire, géré par le système |
| **Fichiers internes** | données privées à l'appli (texte, image, JSON) | `Context` : `openFileOutput()`, `openFileInput()`, `FileOutputStream`, `FileInputStream` | `/data/data/<package>/files/` |
| **Fichiers externes** | gros fichiers, partageables (photos, téléchargements) | `Environment` (`getExternalStorageDirectory()`, `getExternalStorageState()`) | carte SD ou stockage partagé (`/sdcard/...`) |
| **Base SQLite** | données **structurées** (tables, requêtes SQL) | `SQLiteOpenHelper`, `SQLiteDatabase`, `ContentValues`, `Cursor` | `/data/data/<package>/databases/<nom>` |
| **Content Provider** | **partager** des données avec d'autres applis (contacts, médias) | `ContentProvider` (côté fournisseur), `ContentResolver` (côté client), `Uri` | dépend du fournisseur |
| (base **distante**) | données sur un serveur | réseau (HTTP, REST) | ailleurs : **pas** du stockage local |

**Une base SQLite sur le téléphone est LOCALE** *(annale 2, Q1i)* : c'est un simple
fichier dans le dossier privé de l'appli, sans serveur.

---

## 2. SharedPreferences : les réglages

**Principe :** un petit dictionnaire clé/valeur, stocké dans un fichier XML privé. Types
acceptés : `boolean`, `int`, `long`, `float`, `String` (et un ensemble de `String`).

> **À savoir écrire par cœur :**

```java
// ÉCRIRE
SharedPreferences prefs = getSharedPreferences("MesPrefs", Context.MODE_PRIVATE);
SharedPreferences.Editor editor = prefs.edit();      // on passe par un éditeur
editor.putString("pseudo", "Patrick");
editor.putInt("score", 42);
editor.putBoolean("sonActif", true);
editor.commit();      // enregistre (synchrone). apply() fait pareil en arrière-plan

// LIRE (le 2e argument est la valeur par défaut si la clé n'existe pas)
SharedPreferences prefs = getSharedPreferences("MesPrefs", Context.MODE_PRIVATE);
String pseudo = prefs.getString("pseudo", "");
int score     = prefs.getInt("score", 0);
boolean son   = prefs.getBoolean("sonActif", false);
```

**Les deux pièges :**
1. Oublier **`commit()`** (ou `apply()`) : rien n'est enregistré.
2. Écrire **sur `prefs`** au lieu de passer par **`edit()`** : `prefs.putString` n'existe
   pas. On lit sur `prefs`, on écrit sur l'**éditeur**.

**Les préférences par défaut** de l'appli, partagées par tous ses composants (activités,
services, receivers) :

```java
SharedPreferences prefs = PreferenceManager.getDefaultSharedPreferences(this);
```

**Être prévenu quand une préférence change :**
`prefs.registerOnSharedPreferenceChangeListener(listener)`, avec la méthode
`onSharedPreferenceChanged(SharedPreferences prefs, String key)`.

---

## 3. Les fichiers

**Interne** (privé, toujours disponible, supprimé avec l'appli) :

```java
// ÉCRIRE
try {
    FileOutputStream fos = openFileOutput("notes.txt", Context.MODE_PRIVATE);
    fos.write("Bonjour".getBytes());
    fos.close();
} catch (IOException e) {
    Log.e("Fichier", "Erreur d'écriture", e);
}

// LIRE
try {
    FileInputStream fis = openFileInput("notes.txt");
    BufferedReader br = new BufferedReader(new InputStreamReader(fis));
    String ligne = br.readLine();
    br.close();
} catch (IOException e) {
    Log.e("Fichier", "Erreur de lecture", e);
}
```

Le reste, c'est **du Java standard** (flux, lecteurs).

**Externe** (carte SD, stockage partagé) : il faut **vérifier qu'il est disponible**
avant (la carte peut être retirée, ou le téléphone branché en USB) et, dans le style du
cours, déclarer la permission :

```xml
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
```

```java
if (Environment.getExternalStorageState().equals(Environment.MEDIA_MOUNTED)) {
    File sd = Environment.getExternalStorageDirectory();
    File f = new File(sd, "export.txt");
    // ... écrire avec un FileOutputStream
}
```

🕰️ Depuis Android 10, le « stockage limité » (*scoped storage*) a changé les règles : une
appli peut écrire dans **son propre** dossier externe sans permission
(`getExternalFilesDir()`), et passe par le système (MediaStore, sélecteur) pour le reste.
**À l'examen, réponds comme le cours :** `WRITE_EXTERNAL_STORAGE`.

**Annale 2, Q2b :** « télécharger un fichier et l'enregistrer sur le stockage externe » →
**deux** permissions : `INTERNET` (pour télécharger) **et** `WRITE_EXTERNAL_STORAGE` (pour
écrire).

---

## 4. SQLite : la base de données locale

**Pourquoi :** dès que les données ont une **structure** (une liste de notes, de positions,
de contacts) et qu'on veut les **interroger** (trier, filtrer), les préférences ne
suffisent plus.

**Ce qu'il faut savoir :**
- SQLite est une base **embarquée** : pas de serveur, un simple fichier.
- **Trois types principaux** : `TEXT` (comme `String`), `INTEGER` (comme `long`), `REAL`
  (comme `double`). SQLite **ne vérifie pas** les types de façon stricte.
- Chaque base est **privée** à l'appli qui l'a créée.

### 4.1 Les trois classes à connaître

| Classe | Rôle |
|---|---|
| **`SQLiteOpenHelper`** | tu en **hérites** pour **créer** la base (`onCreate`) et la **mettre à jour** (`onUpgrade`) |
| **`SQLiteDatabase`** | la base ouverte : `insert`, `update`, `delete`, `query`, `rawQuery`, `execSQL` |
| **`Cursor`** | le **résultat** d'une requête : un curseur qu'on fait avancer ligne par ligne |
| (`ContentValues`) | un petit dictionnaire colonne → valeur, pour `insert` et `update` |

### 4.2 Créer la base

> **À savoir écrire par cœur :**

```java
public class BaseHelper extends SQLiteOpenHelper {

    private static final String NOM_BASE = "suivi.db";
    private static final int VERSION = 1;

    public BaseHelper(Context context) {
        super(context, NOM_BASE, null, VERSION);
        //              nom      factory version
    }

    @Override
    public void onCreate(SQLiteDatabase db) {           // appelée UNE fois, à la création
        db.execSQL("CREATE TABLE notes ("
                + "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                + "titre TEXT, "
                + "date INTEGER)");
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int ancienne, int nouvelle) {
        // appelée quand VERSION augmente : le plus simple, tout recréer
        db.execSQL("DROP TABLE IF EXISTS notes");
        onCreate(db);
    }
}
```

**Quand `onCreate` est-elle appelée ?** Pas au démarrage de l'appli : **la première fois
qu'on demande la base** (`getWritableDatabase()`) **et qu'elle n'existe pas encore**.

### 4.3 Insérer, modifier, supprimer

```java
BaseHelper helper = new BaseHelper(this);
SQLiteDatabase db = helper.getWritableDatabase();   // lecture + écriture

// INSERT : avec ContentValues (méthode recommandée)
ContentValues cv = new ContentValues();
cv.put("titre", "Réviser Android");
cv.put("date", System.currentTimeMillis());
long id = db.insert("notes", null, cv);             // renvoie l'id, ou -1 si erreur

// INSERT : en SQL direct (marche aussi)
db.execSQL("INSERT INTO notes (titre, date) VALUES ('Lire le cours 3', 0)");

// UPDATE : table, nouvelles valeurs, condition, arguments de la condition
ContentValues maj = new ContentValues();
maj.put("titre", "Réviser Android (fait)");
db.update("notes", maj, "id = ?", new String[]{ String.valueOf(id) });

// DELETE
db.delete("notes", "id = ?", new String[]{ String.valueOf(id) });

db.close();
```

**Pourquoi les `?`** : on ne colle jamais une valeur saisie par l'utilisateur dans la
chaîne SQL (risque d'**injection SQL**). Le `?` est remplacé proprement par la valeur du
tableau.

### 4.4 Lire avec un Cursor

```java
SQLiteDatabase db = helper.getReadableDatabase();

Cursor c = db.rawQuery("SELECT id, titre FROM notes WHERE date > ? ORDER BY titre",
                       new String[]{ "0" });
// ou : db.query("notes", new String[]{"id","titre"}, "date > ?", new String[]{"0"},
//               null, null, "titre");   // table, colonnes, where, args, groupBy, having, orderBy

while (c.moveToNext()) {                             // passe à la ligne suivante
    long id      = c.getLong(c.getColumnIndex("id"));
    String titre = c.getString(c.getColumnIndex("titre"));
    Log.d("BD", id + " : " + titre);
}
c.close();                                           // TOUJOURS fermer le curseur
db.close();
```

Méthodes du Cursor : `moveToNext()`, `moveToFirst()`, `getCount()`,
`getColumnIndex(nom)`, `getString(i)`, `getInt(i)`, `getLong(i)`, `getDouble(i)`.

🕰️ Aujourd'hui on utilise **Room** (une couche au-dessus de SQLite, avec des annotations
`@Entity`, `@Dao`). L'examen suit le cours : **SQLiteOpenHelper**.

> **Rappel du chapitre 06 :** une requête en base peut être lente. Dans une vraie appli, on
> la fait **hors du thread principal**.

---

## 5. Le Content Provider : partager des données

**Pourquoi :** la base SQLite d'une appli est privée. Si une appli veut **offrir** ses
données aux autres (comme Contacts offre les contacts), elle passe par un **Content
Provider**. Toute appli qui a la **permission** peut alors lire (et écrire) ces données,
avec une interface commune.

**Les données sont vues comme une table**, et chaque ligne a un identifiant `_ID`.

**L'adresse d'un fournisseur, l'URI :**

```
content://  contacts  /  people  /  45
 schéma     autorité     chemin     identifiant (optionnel)
            (qui ?)      (quoi ?)   (lequel ?)
```

| URI | Renvoie |
|---|---|
| `content://contacts/people` | tous les contacts |
| `content://contacts/people/45` | le contact d'id 45 |
| `content://call_log/calls` | le journal d'appels |
| `content://media/external/images` | les images du stockage externe |

**Côté client, on passe par le `ContentResolver`**, avec les mêmes 4 opérations qu'une base :

```java
// Lire les contacts (permission READ_CONTACTS dans le manifeste)
Cursor c = getContentResolver().query(
        ContactsContract.Contacts.CONTENT_URI,               // quoi
        new String[]{ ContactsContract.Contacts.DISPLAY_NAME }, // quelles colonnes
        null, null,                                          // filtre, arguments
        ContactsContract.Contacts.DISPLAY_NAME + " ASC");    // tri
while (c.moveToNext()) {
    String nom = c.getString(0);
}
c.close();

// Les autres opérations
getContentResolver().insert(uri, valeurs);
getContentResolver().update(uri, valeurs, selection, args);
getContentResolver().delete(uri, selection, args);
```

**Créer son propre fournisseur, en 3 étapes :**
1. Avoir un stockage (souvent une base `SQLiteOpenHelper`).
2. **Hériter de `ContentProvider`** et redéfinir **6 méthodes** : `onCreate()`, `query()`,
   `insert()`, `update()`, `delete()`, `getType()`. Un `UriMatcher` aide à savoir si l'URI
   demande toute la table ou une seule ligne.
3. Le **déclarer** dans le manifeste :
   `<provider android:name=".MonProvider" android:authorities="fr.cyu.monappli.provider" />`

---

## 6. À toi (sur papier, fichier fermé)

**Exercice 5.1 (annale 1, ex. 1.1, 2 points) :** De quelles manières peut-on stocker des
données en local sur Android ? Pour chacune, quelles classes Android sont impliquées ?

**Exercice 5.2 :** Écris le code qui compte combien de fois l'appli a été ouverte : à
chaque `onCreate`, lire le compteur dans les SharedPreferences, l'augmenter de 1,
l'enregistrer, et l'afficher dans un Toast.

**Exercice 5.3 :** Quel moyen de stockage choisir, et pourquoi ?
1. Le thème clair ou sombre choisi par l'utilisateur.
2. L'historique de 3 000 trajets avec date, distance et durée.
3. Le texte qu'un utilisateur est en train de taper, quand il tourne le téléphone.
4. Une photo de 4 Mo que l'utilisateur veut retrouver dans sa galerie.
5. La liste des contacts du téléphone, pour en choisir un.

**Exercice 5.4 :** Écris une classe `LivresHelper` qui crée une base `biblio.db` avec une
table `livres(id INTEGER PRIMARY KEY AUTOINCREMENT, titre TEXT, auteur TEXT, annee
INTEGER)`.

**Exercice 5.5 :** Avec ce helper, écris le code qui :
1. insère le livre « L'Enfant noir », Camara Laye, 1953 ;
2. affiche dans Logcat tous les livres parus après 1950, triés par année ;
3. supprime les livres d'un auteur donné (variable `String auteur`), sans risque
   d'injection SQL.

**Exercice 5.6 (annale 2, Q3c) :** Une base SQLite existe déjà, avec la table
`locations(lat VARCHAR(25), lng VARCHAR(25))`. Tu as un helper `MaBase` déjà écrit, et
deux variables `double latitude, longitude`. Écris le code qui ajoute ces coordonnées dans
la table.

**Exercice 5.7 :** Décompose l'URI `content://com.android.contacts/contacts/12` : schéma,
autorité, chemin, identifiant. Quelle permission faut-il pour la lire ?

**Exercice 5.8 :** Vrai ou faux ?
1. Une base SQLite d'une appli est accessible à toutes les applis du téléphone.
2. `onCreate` d'un `SQLiteOpenHelper` est appelée à chaque lancement de l'appli.
3. Sans `commit()` ni `apply()`, les modifications des SharedPreferences sont perdues.
4. Pour partager les données de sa base avec une autre appli, on utilise un Content
   Provider.
