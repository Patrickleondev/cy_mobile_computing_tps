# TP2 pas à pas complet : préférences, téléchargement, base SQLite, liste

Chaque fichier est donné **en entier** (Ctrl + A, coller). Pour un fichier qui existait au TP1,
« Ce qui a été ajouté » montre les lignes nouvelles, puis pourquoi et pourquoi à cet endroit.

Ce que fait l'appli en plus : elle se souvient du nom (on ne remplit le formulaire qu'une fois),
télécharge un fichier d'événements dans un service, le range dans une base SQLite et l'affiche
dans une liste.

## 0. Préparer le projet

1. Ferme Android Studio. Copie `AndroidStudioProjects\TP1Intents` en `AndroidStudioProjects\TP2Events`.
2. Dans la copie, supprime `build`, `app\build`, `.gradle` et `.idea` (ils seront recréés).
3. Ouvre `TP2Events` (**File > Open**) et attends la fin du Sync Gradle.
4. Change **seulement** ces lignes :
   - `settings.gradle.kts` : `rootProject.name = "TP2Events"` ;
   - `app/build.gradle.kts` : `applicationId = "com.cyu.tp2events"` ;
   - `res/values/strings.xml` : `<string name="app_name">TP2Events</string>`.

**Ne touche jamais** à `namespace = "com.cyu.tp1intents"` dans `app/build.gradle.kts`. C'est le
paquet Java où Android génère la classe `R`. S'il change, tout le projet affiche
« package R does not exist ». Si Studio propose « Rename package », refuse.

`applicationId` est l'identité de l'appli sur le téléphone : en le changeant, le TP2
s'installe **à côté** du TP précédent au lieu de l'écraser.

## 1. Manifeste et textes

### 1.1 AndroidManifest.xml

**Remplace tout** le contenu de `app/src/main/AndroidManifest.xml` par :

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- TP2 2.1 : telecharger le fichier -->
    <uses-permission android:name="android.permission.INTERNET" />

    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.TP1Intents">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:label="@string/app_name"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />

                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <activity
            android:name=".SecondActivity"
            android:exported="false"
            android:windowSoftInputMode="adjustResize" />

        <activity
            android:name=".ThirdActivity"
            android:exported="false" />

        <service
            android:name=".DownloadService"
            android:exported="false" />
    </application>

</manifest>
```

**Ce qui a été ajouté ou changé** par rapport au TP précédent :

```xml

    <!-- TP2 2.1 : telecharger le fichier -->
    <uses-permission android:name="android.permission.INTERNET" />
```

```xml

        <service
            android:name=".DownloadService"
            android:exported="false" />
```

**Pourquoi :**

- `INTERNET` : sans elle, toute connexion réseau échoue (`SecurityException`). Permission
  « normale » : accordée à l'installation, rien à demander à l'utilisateur.
- `<service android:name=".DownloadService">` : un service, comme une Activity, doit être déclaré.

**Pourquoi à cet endroit :**

`<uses-permission>` va **avant** `<application>` ; le `<service>` va **dans** `<application>`, à
côté des Activities.

### 1.2 strings.xml

**Remplace tout** le contenu de `app/src/main/res/values/strings.xml` par :

```xml
<resources>
    <string name="app_name">TP2Events</string>
    <string name="welcome">Welcome!\nPlease enter your details below to continue...</string>
    <string name="hint_name">Name</string>
    <string name="hint_email">Email</string>
    <string name="action_ok">OK</string>
    <string name="hello">Hello</string>
    <string name="action_next">NEXT</string>
    <string name="action_previous">PREVIOUS</string>
    <string name="third_title">Evenements</string>
    <string name="photo_description">Photo illustrant le second ecran</string>
    <string name="empty_name">Entrez au moins un nom</string>
    <string name="status_loading">Telechargement des evenements...</string>
    <string name="status_error">Echec du telechargement (voir Logcat)</string>
    <string name="status_count">%1$d evenements</string>
    <string name="event_details">Latitude : %1$s\nLongitude : %2$s\nType : %3$s</string>
</resources>
```

**Ce qui a été ajouté ou changé** par rapport au TP précédent :

```xml
    <string name="app_name">TP2Events</string>
```

```xml
    <string name="third_title">Evenements</string>
```

```xml
    <string name="status_loading">Telechargement des evenements...</string>
    <string name="status_error">Echec du telechargement (voir Logcat)</string>
    <string name="status_count">%1$d evenements</string>
    <string name="event_details">Latitude : %1$s\nLongitude : %2$s\nType : %3$s</string>
```

**Pourquoi :**

- Les textes du statut de la liste (`status_loading`, `status_error`, `status_count` avec `%1$d`
  pour le nombre) et du détail d'un événement (`event_details`, trois `%s`).

**Pourquoi à cet endroit :**

Avec les autres textes, dans `res/values/strings.xml`.

## 2. Se souvenir de l'utilisateur

### 2.1 MainActivity.java

**Remplace tout** le contenu de `app/src/main/java/com/cyu/tp1intents/MainActivity.java` par :

```java
package com.cyu.tp1intents;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

public class MainActivity extends AppCompatActivity {

    // cles de l intent, prefixees par le package
    public final static String NAME = "com.cyu.tp1intents.name";
    public final static String EMAIL = "com.cyu.tp1intents.email";

    // fichier de preferences ou on garde le nom et l email (TP2, partie 1)
    public final static String PREFS = "com.cyu.tp1intents.user";

    private SharedPreferences prefs;
    private EditText champNom;
    private EditText champEmail;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // deja inscrit : on saute le formulaire
        prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        String nomSauve = prefs.getString(NAME, "");
        if (!nomSauve.isEmpty()) {
            ouvrirSecond(nomSauve, prefs.getString(EMAIL, ""));
            finish();
            return;
        }

        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets barres = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(barres.left, barres.top, barres.right, barres.bottom);
            return insets;
        });

        champNom = findViewById(R.id.name);
        champEmail = findViewById(R.id.email);
    }

    // liee au bouton par android:onClick="submit"
    public void submit(View view) {
        String nom = champNom.getText().toString().trim();
        String email = champEmail.getText().toString().trim();

        if (nom.isEmpty()) {
            Toast.makeText(this, R.string.empty_name, Toast.LENGTH_SHORT).show();
            return;
        }

        prefs.edit()
                .putString(NAME, nom)
                .putString(EMAIL, email)
                .apply();

        ouvrirSecond(nom, email);
    }

    private void ouvrirSecond(String nom, String email) {
        Intent intent = new Intent(this, SecondActivity.class);
        intent.putExtra(NAME, nom);
        intent.putExtra(EMAIL, email);
        startActivity(intent);
    }
}
```

**Ce qui a été ajouté ou changé** par rapport au TP précédent :

```java
import android.content.SharedPreferences;
```

```java
    // fichier de preferences ou on garde le nom et l email (TP2, partie 1)
    public final static String PREFS = "com.cyu.tp1intents.user";

    private SharedPreferences prefs;
```

```java

        // deja inscrit : on saute le formulaire
        prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        String nomSauve = prefs.getString(NAME, "");
        if (!nomSauve.isEmpty()) {
            ouvrirSecond(nomSauve, prefs.getString(EMAIL, ""));
            finish();
            return;
        }

```

```java
        prefs.edit()
                .putString(NAME, nom)
                .putString(EMAIL, email)
                .apply();

        ouvrirSecond(nom, email);
    }

    private void ouvrirSecond(String nom, String email) {
```

**Pourquoi :**

- `PREFS` : le nom du fichier de préférences. `SharedPreferences` = un petit dictionnaire
  clé/valeur gardé sur le téléphone, même après fermeture de l'appli.
- Au début de `onCreate`, **avant** `setContentView` : si un nom est déjà sauvé, on ouvre
  directement le 2e écran et `finish()` ferme celui-ci (sinon BACK y reviendrait), puis `return`.
- Dans `submit` : `prefs.edit().putString(...).apply()` sauve le nom et l'email. `apply()` écrit
  en arrière-plan, sans bloquer l'écran.
- `ouvrirSecond` : le code de l'Intent, appelé à deux endroits, est mis dans une méthode.

**Pourquoi à cet endroit :**

Le test se fait au tout début de `onCreate` : inutile d'afficher le formulaire s'il ne sert pas.

## 3. Les données

### 3.1 Event.java

**Nouveau fichier.** Clic droit sur le paquet > **New > Java Class** > `Event`. Colle **tout** ce contenu :

```java
package com.cyu.tp1intents;

// une ligne de la table TABLE_EVENTS
public class Event {

    public final int id;
    public final String name;
    public final String lat;
    public final String lng;
    public final String type;

    public Event(int id, String name, String lat, String lng, String type) {
        this.id = id;
        this.name = name;
        this.lat = lat;
        this.lng = lng;
        this.type = type;
    }

    @Override
    public String toString() {
        return "ID: " + id + ", NAME: " + name + ", LAT: " + lat + ", LNG: " + lng + ", TYPE: " + type;
    }
}
```

**Pourquoi :**

- Une ligne de la table : `id`, `name`, `lat`, `lng`, `type`. Champs `public final` : un simple
  objet de données, lu par les autres classes, jamais modifié.
- `toString()` : le texte écrit dans Logcat (le sujet demande d'afficher chaque ligne lue).

**Pourquoi à cet endroit :**

Classe à part, utilisée par `DownloadService`, `EventDbHelper` et `ThirdActivity`.

### 3.2 EventDbHelper.java

**Nouveau fichier.** Clic droit sur le paquet > **New > Java Class** > `EventDbHelper`. Colle **tout** ce contenu :

```java
package com.cyu.tp1intents;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.DatabaseUtils;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

import java.util.ArrayList;
import java.util.List;

public class EventDbHelper extends SQLiteOpenHelper {

    private static final String DB_NAME = "events.db";
    private static final int DB_VERSION = 1;

    // noms imposes par le sujet (2.2)
    public static final String TABLE_EVENTS = "TABLE_EVENTS";
    public static final String ID = "ID";
    public static final String NAME = "NAME";
    public static final String LAT = "LAT";
    public static final String LNG = "LNG";
    public static final String TYPE = "TYPE";

    public EventDbHelper(Context context) {
        super(context, DB_NAME, null, DB_VERSION);
    }

    // appele une seule fois, quand le fichier events.db n existe pas encore
    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE " + TABLE_EVENTS + " ("
                + ID + " INTEGER PRIMARY KEY, "
                + NAME + " TEXT, "
                + LAT + " TEXT, "
                + LNG + " TEXT, "
                + TYPE + " TEXT)");
    }

    // appele quand DB_VERSION augmente
    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_EVENTS);
        onCreate(db);
    }

    // vide la table puis insere les evenements du fichier, tout ou rien
    public void remplacer(List<Event> events) {
        SQLiteDatabase db = getWritableDatabase();
        db.beginTransaction();
        try {
            db.delete(TABLE_EVENTS, null, null);
            for (Event e : events) {
                ContentValues ligne = new ContentValues();
                ligne.put(NAME, e.name);
                ligne.put(LAT, e.lat);
                ligne.put(LNG, e.lng);
                ligne.put(TYPE, e.type);
                db.insert(TABLE_EVENTS, null, ligne);
            }
            db.setTransactionSuccessful();
        } finally {
            db.endTransaction();
        }
    }

    public boolean estVide() {
        return DatabaseUtils.queryNumEntries(getReadableDatabase(), TABLE_EVENTS) == 0;
    }

    // SELECT * FROM TABLE_EVENTS ORDER BY ID
    public List<Event> lireTout() {
        List<Event> events = new ArrayList<>();
        try (Cursor c = getReadableDatabase().query(TABLE_EVENTS, null, null, null, null, null, ID)) {
            while (c.moveToNext()) {
                events.add(new Event(
                        c.getInt(c.getColumnIndexOrThrow(ID)),
                        c.getString(c.getColumnIndexOrThrow(NAME)),
                        c.getString(c.getColumnIndexOrThrow(LAT)),
                        c.getString(c.getColumnIndexOrThrow(LNG)),
                        c.getString(c.getColumnIndexOrThrow(TYPE))));
            }
        }
        return events;
    }
}
```

**Pourquoi :**

- `extends SQLiteOpenHelper` : Android crée et ouvre `events.db` pour nous.
- Les constantes `TABLE_EVENTS`, `ID`, `NAME`... : les noms imposés par le sujet, écrits une
  seule fois pour éviter les fautes de frappe dans le SQL.
- `onCreate` : appelée **une seule fois**, quand le fichier n'existe pas : `CREATE TABLE`.
- `onUpgrade` : appelée quand `DB_VERSION` augmente.
- `remplacer` : vide la table puis insère tout, dans une **transaction** : si une insertion échoue,
  rien n'est changé (`setTransactionSuccessful` n'est pas atteint).
- `estVide` : compte les lignes ; `lireTout` : `SELECT *` trié par `ID`, avec un `Cursor` fermé
  automatiquement par le `try (...)`.

**Pourquoi à cet endroit :**

Toute la base est dans cette classe : les écrans ne voient jamais de SQL, seulement des `Event`.

### 3.3 DownloadService.java

**Nouveau fichier.** Clic droit sur le paquet > **New > Java Class** > `DownloadService`. Colle **tout** ce contenu :

```java
package com.cyu.tp1intents;

import android.app.IntentService;
import android.content.Intent;
import android.os.Environment;
import android.util.Log;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

// onHandleIntent tourne dans un thread a part : le reseau y est permis
public class DownloadService extends IntentService {

    private static final String TAG = "DownloadService";

    // adresse donnee dans le sujet (2.1)
    public static final String URL_EVENTS =
            "https://drive.google.com/uc?export=download&id=1oa5a6P8nJ6aQgsbjurdiRorzAF92V2wP";
    public static final String FICHIER = "events.txt";

    // message envoye a ThirdActivity quand c est fini
    public static final String ACTION_FINI = "com.cyu.tp1intents.EVENTS_READY";
    public static final String SUCCES = "com.cyu.tp1intents.succes";

    public DownloadService() {
        super("DownloadService");
    }

    @Override
    protected void onHandleIntent(Intent intent) {
        boolean succes = false;
        try {
            File fichier = telecharger();
            List<Event> events = lire(fichier);
            new EventDbHelper(this).remplacer(events);
            Log.d(TAG, events.size() + " evenements enregistres dans la base");
            succes = true;
        } catch (IOException e) {
            Log.e(TAG, "echec du telechargement", e);
        }

        Intent fini = new Intent(ACTION_FINI);
        fini.setPackage(getPackageName());   // seule notre application le recoit
        fini.putExtra(SUCCES, succes);
        sendBroadcast(fini);
    }

    // 2.1 : copie le fichier du web dans le dossier Download de l application
    private File telecharger() throws IOException {
        File dossier = getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS);
        if (dossier == null) {
            throw new IOException("stockage externe indisponible");
        }
        File fichier = new File(dossier, FICHIER);

        Log.d(TAG, "Connexion a " + URL_EVENTS);
        HttpURLConnection connexion = (HttpURLConnection) new URL(URL_EVENTS).openConnection();
        connexion.setConnectTimeout(10000);
        connexion.setReadTimeout(10000);
        try {
            int code = connexion.getResponseCode();
            if (code != HttpURLConnection.HTTP_OK) {
                throw new IOException("reponse HTTP " + code);
            }
            try (InputStream in = new BufferedInputStream(connexion.getInputStream());
                 OutputStream out = new FileOutputStream(fichier)) {
                byte[] tampon = new byte[4096];
                int n;
                // read renvoie le nombre d octets lus : on n ecrit que ceux-la
                while ((n = in.read(tampon)) != -1) {
                    out.write(tampon, 0, n);
                }
            }
        } finally {
            connexion.disconnect();
        }

        Log.d(TAG, "Fichier enregistre : " + fichier.getAbsolutePath());
        return fichier;
    }

    // 2.2 : une ligne = NOM;;LAT;;LNG;;TYPE
    private List<Event> lire(File fichier) throws IOException {
        List<Event> events = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(fichier))) {
            String ligne;
            while ((ligne = br.readLine()) != null) {
                ligne = ligne.trim();
                if (ligne.isEmpty()) {
                    continue;
                }
                String[] morceaux = ligne.split(";;");
                if (morceaux.length == 4) {
                    events.add(new Event(0, morceaux[0], morceaux[1], morceaux[2], morceaux[3]));
                } else {
                    Log.w(TAG, "Ligne ignoree : " + ligne);
                }
            }
        }
        return events;
    }
}
```

**Pourquoi :**

- `extends IntentService` : `onHandleIntent` tourne dans un **thread à part**. Le réseau est
  interdit sur le thread de l'écran (`NetworkOnMainThreadException`).
- `telecharger` : `HttpURLConnection`, puis copie par blocs de 4 Ko dans
  `getExternalFilesDir(DIRECTORY_DOWNLOADS)/events.txt`. `read` rend le nombre d'octets lus : on
  n'écrit que ceux-là.
- `lire` : chaque ligne `NOM;;LAT;;LNG;;TYPE` est coupée par `split(";;")` en 4 morceaux. Une
  ligne mal formée est ignorée (et notée dans Logcat).
- À la fin : un `Intent(ACTION_FINI)` envoyé par `sendBroadcast`, avec `SUCCES` vrai ou faux.
  `setPackage` : seul ton appli le reçoit.

**Pourquoi à cet endroit :**

Un service plutôt qu'un thread dans l'Activity : le téléchargement continue même si l'écran est
tourné ou fermé.

## 4. La liste

### 4.1 activity_third.xml

**Remplace tout** le contenu de `app/src/main/res/layout/activity_third.xml` par :

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:gravity="center_horizontal"
    android:padding="16dp"
    tools:context=".ThirdActivity">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="@string/third_title"
        android:textSize="20sp"
        android:textStyle="bold" />

    <TextView
        android:id="@+id/status"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="8dp"
        tools:text="15 evenements" />

    <!-- prend toute la hauteur qui reste entre le statut et le bouton -->
    <ListView
        android:id="@+id/events"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"
        android:layout_marginTop="8dp" />

    <Button
        android:id="@+id/previous"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="16dp"
        android:onClick="previous"
        android:text="@string/action_previous" />

</LinearLayout>
```

**Ce qui a été ajouté ou changé** par rapport au TP précédent :

```xml
    android:gravity="center_horizontal"
```

```xml
    <TextView
        android:id="@+id/status"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="8dp"
        tools:text="15 evenements" />

    <!-- prend toute la hauteur qui reste entre le statut et le bouton -->
    <ListView
        android:id="@+id/events"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"
        android:layout_marginTop="8dp" />

```

```xml
        android:layout_marginTop="16dp"
```

**Pourquoi :**

- `TextView status` : « Téléchargement... », puis « 15 evenements ».
- `ListView events` avec `layout_height="0dp"` et `layout_weight="1"` : elle prend toute la
  hauteur restante entre le statut et le bouton.

**Pourquoi à cet endroit :**

Le 3e écran du TP1 devient l'écran de la liste.

### 4.2 ThirdActivity.java

**Remplace tout** le contenu de `app/src/main/java/com/cyu/tp1intents/ThirdActivity.java` par :

```java
package com.cyu.tp1intents;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import java.util.ArrayList;
import java.util.List;

public class ThirdActivity extends AppCompatActivity {

    private static final String TAG = "ThirdActivity";

    private EventDbHelper db;
    private ListView liste;
    private TextView statut;
    private List<Event> events = new ArrayList<>();

    // recoit le message du service quand le fichier est en base
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

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_third);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets barres = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(barres.left, barres.top, barres.right, barres.bottom);
            return insets;
        });

        db = new EventDbHelper(this);
        liste = findViewById(R.id.events);
        statut = findViewById(R.id.status);

        // 3.1.2 : un clic montre coordonnees et type
        liste.setOnItemClickListener((parent, vue, position, id) -> {
            Event e = events.get(position);
            new AlertDialog.Builder(this)
                    .setTitle(e.name)
                    .setMessage(getString(R.string.event_details, e.lat, e.lng, e.type))
                    .setPositiveButton(android.R.string.ok, null)
                    .show();
        });

        // base vide : on lance le telechargement une fois
        if (db.estVide()) {
            statut.setText(R.string.status_loading);
            startService(new Intent(this, DownloadService.class));
        }
    }

    // on n ecoute que quand l ecran est visible
    @Override
    protected void onResume() {
        super.onResume();
        ContextCompat.registerReceiver(this, receveur,
                new IntentFilter(DownloadService.ACTION_FINI), ContextCompat.RECEIVER_NOT_EXPORTED);
        afficher();
    }

    @Override
    protected void onPause() {
        super.onPause();
        unregisterReceiver(receveur);
    }

    @Override
    protected void onDestroy() {
        db.close();
        super.onDestroy();
    }

    // 3.1 : interroge la base, ecrit chaque ligne dans Logcat, puis remplit la liste
    private void afficher() {
        events = db.lireTout();
        if (events.isEmpty()) {
            return;   // pas encore telecharge
        }

        List<String> noms = new ArrayList<>();
        for (Event e : events) {
            Log.d(TAG, e.toString());
            noms.add(e.name);
        }
        liste.setAdapter(new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, noms));
        statut.setText(getString(R.string.status_count, events.size()));
    }

    // finish() suffit pour revenir : un nouvel intent empilerait une 2e SecondActivity
    public void previous(View view) {
        finish();
    }
}
```

**Ce qui a été ajouté ou changé** par rapport au TP précédent :

```java
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
```

```java
import android.util.Log;
```

```java
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;
```

```java
import androidx.appcompat.app.AlertDialog;
```

```java
import androidx.core.content.ContextCompat;
```

```java
import java.util.ArrayList;
import java.util.List;

```

```java

    private static final String TAG = "ThirdActivity";

    private EventDbHelper db;
    private ListView liste;
    private TextView statut;
    private List<Event> events = new ArrayList<>();

    // recoit le message du service quand le fichier est en base
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

```java

        db = new EventDbHelper(this);
        liste = findViewById(R.id.events);
        statut = findViewById(R.id.status);

        // 3.1.2 : un clic montre coordonnees et type
        liste.setOnItemClickListener((parent, vue, position, id) -> {
            Event e = events.get(position);
            new AlertDialog.Builder(this)
                    .setTitle(e.name)
                    .setMessage(getString(R.string.event_details, e.lat, e.lng, e.type))
                    .setPositiveButton(android.R.string.ok, null)
                    .show();
        });

        // base vide : on lance le telechargement une fois
        if (db.estVide()) {
            statut.setText(R.string.status_loading);
            startService(new Intent(this, DownloadService.class));
        }
    }

    // on n ecoute que quand l ecran est visible
    @Override
    protected void onResume() {
        super.onResume();
        ContextCompat.registerReceiver(this, receveur,
                new IntentFilter(DownloadService.ACTION_FINI), ContextCompat.RECEIVER_NOT_EXPORTED);
        afficher();
    }

    @Override
    protected void onPause() {
        super.onPause();
        unregisterReceiver(receveur);
    }

    @Override
    protected void onDestroy() {
        db.close();
        super.onDestroy();
    }

    // 3.1 : interroge la base, ecrit chaque ligne dans Logcat, puis remplit la liste
    private void afficher() {
        events = db.lireTout();
        if (events.isEmpty()) {
            return;   // pas encore telecharge
        }

        List<String> noms = new ArrayList<>();
        for (Event e : events) {
            Log.d(TAG, e.toString());
            noms.add(e.name);
        }
        liste.setAdapter(new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, noms));
        statut.setText(getString(R.string.status_count, events.size()));
```

**Pourquoi :**

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

**Pourquoi à cet endroit :**

`afficher()` est appelée dans `onResume` : quand on revient sur l'écran, la liste est relue.

### 4.3 app/build.gradle.kts

**Remplace tout** le contenu de `app/build.gradle.kts` par :

```kotlin
plugins {
    alias(libs.plugins.android.application)
}

android {
    namespace = "com.cyu.tp1intents"
    compileSdk {
        version = release(37)
    }

    defaultConfig {
        applicationId = "com.cyu.tp2events"
        minSdk = 24
        targetSdk = 37
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            optimization {
                enable = false
            }
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
}

dependencies {
    implementation(libs.androidx.activity.ktx)
    implementation(libs.androidx.appcompat)
    implementation(libs.material)
    implementation(libs.androidx.constraintlayout)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
}
```

**Ce qui a été ajouté ou changé** par rapport au TP précédent :

```kotlin
        applicationId = "com.cyu.tp2events"
```

**Pourquoi :**

- Seul `applicationId` change (`com.cyu.tp2events`). `namespace` ne change pas.

**Pourquoi à cet endroit :**

Dans le bloc `defaultConfig`.

## 5. Tester

Lance l'appli, remplis le formulaire, NEXT : « Téléchargement... » puis la liste des 15
événements. Dans Logcat (filtre `ThirdActivity`) : une ligne par événement. Relance l'appli : le
formulaire est sauté (préférences) et la liste s'affiche sans téléchargement (base remplie).
