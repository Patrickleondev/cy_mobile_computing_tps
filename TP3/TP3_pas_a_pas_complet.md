# TP3 pas à pas complet : écran d'un événement, adresse, carte et GPS

Chaque fichier est donné **en entier** (Ctrl + A, coller). « Ce qui a été ajouté » montre les
lignes nouvelles par rapport au TP2.

Ce que fait l'appli en plus : un clic sur un événement ouvre son écran avec son adresse
(géocodage) ; un bouton AJOUTER ouvre une carte OpenStreetMap centrée sur la position GPS, pour
créer un événement à l'endroit où l'on est.

## 0. Préparer le projet

1. Ferme Android Studio. Copie `AndroidStudioProjects\TP2Events` en `AndroidStudioProjects\TP3Maps`.
2. Dans la copie, supprime `build`, `app\build`, `.gradle` et `.idea` (ils seront recréés).
3. Ouvre `TP3Maps` (**File > Open**) et attends la fin du Sync Gradle.
4. Change **seulement** ces lignes :
   - `settings.gradle.kts` : `rootProject.name = "TP3Maps"` ;
   - `app/build.gradle.kts` : `applicationId = "com.cyu.tp3maps"` ;
   - `res/values/strings.xml` : `<string name="app_name">TP3Maps</string>`.

**Ne touche jamais** à `namespace = "com.cyu.tp1intents"` dans `app/build.gradle.kts`. C'est le
paquet Java où Android génère la classe `R`. S'il change, tout le projet affiche
« package R does not exist ». Si Studio propose « Rename package », refuse.

`applicationId` est l'identité de l'appli sur le téléphone : en le changeant, le TP3
s'installe **à côté** du TP précédent au lieu de l'écraser.

## 1. Gradle : la bibliothèque de carte

### 1.1 gradle/libs.versions.toml

**Remplace tout** le contenu de `gradle/libs.versions.toml` par :

```toml
[versions]
agp = "9.4.1"
junit = "4.13.2"
junitVersion = "1.3.0"
espressoCore = "3.7.0"
appcompat = "1.7.0"
material = "1.12.0"
constraintlayout = "2.2.0"
activityKtx = "1.13.0"
osmdroid = "6.1.20"



[libraries]
junit = { group = "junit", name = "junit", version.ref = "junit" }
androidx-junit = { group = "androidx.test.ext", name = "junit", version.ref = "junitVersion" }
androidx-espresso-core = { group = "androidx.test.espresso", name = "espresso-core", version.ref = "espressoCore" }
androidx-appcompat = { group = "androidx.appcompat", name = "appcompat", version.ref = "appcompat" }
material = { group = "com.google.android.material", name = "material", version.ref = "material" }
androidx-constraintlayout = { group = "androidx.constraintlayout", name = "constraintlayout", version.ref = "constraintlayout" }
androidx-activity-ktx = { group = "androidx.activity", name = "activity-ktx", version.ref = "activityKtx" }
osmdroid-android = { group = "org.osmdroid", name = "osmdroid-android", version.ref = "osmdroid" }

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
```

**Ce qui a été ajouté ou changé** par rapport au TP précédent :

```toml
osmdroid = "6.1.20"


```

```toml
osmdroid-android = { group = "org.osmdroid", name = "osmdroid-android", version.ref = "osmdroid" }
```

**Pourquoi :**

- `osmdroid = "6.1.20"` (section `[versions]`) et `osmdroid-android` (section `[libraries]`) :
  la bibliothèque de cartes OpenStreetMap, sans clé d'API (Google Maps en demande une).

**Pourquoi à cet endroit :**

Ce fichier est le catalogue des versions du projet : on y déclare la bibliothèque, puis on
l'utilise dans `app/build.gradle.kts`.

### 1.2 app/build.gradle.kts

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
        applicationId = "com.cyu.tp3maps"
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
    implementation(libs.osmdroid.android)
}
```

**Ce qui a été ajouté ou changé** par rapport au TP précédent :

```kotlin
        applicationId = "com.cyu.tp3maps"
```

```kotlin
    implementation(libs.osmdroid.android)
```

**Pourquoi :**

- `implementation(libs.osmdroid.android)` : ajoute osmdroid à l'appli. Puis **Sync Now**.
- `applicationId = "com.cyu.tp3maps"`. `namespace` ne change pas.

**Pourquoi à cet endroit :**

Dans le bloc `dependencies`, avec les autres bibliothèques.

## 2. Manifeste et textes

### 2.1 AndroidManifest.xml

**Remplace tout** le contenu de `app/src/main/AndroidManifest.xml` par :

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- TP2 2.1 : telecharger le fichier -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />

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

        <activity
            android:name=".EventActivity"
            android:exported="false" />

        <activity
            android:name=".AddEventActivity"
            android:exported="false" />

        <service
            android:name=".DownloadService"
            android:exported="false" />
    </application>

</manifest>
```

**Ce qui a été ajouté ou changé** par rapport au TP précédent :

```xml
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
```

```xml
        <activity
            android:name=".EventActivity"
            android:exported="false" />

        <activity
            android:name=".AddEventActivity"
            android:exported="false" />

```

**Pourquoi :**

- `ACCESS_FINE_LOCATION` (GPS précis) et `ACCESS_COARSE_LOCATION` (position approximative) :
  permissions **dangereuses**, à déclarer ici **et** à demander à l'exécution (voir
  `AddEventActivity`).
- `ACCESS_NETWORK_STATE` : osmdroid vérifie la connexion avant de télécharger les tuiles.
- Les deux nouvelles Activities, `EventActivity` et `AddEventActivity`.

**Pourquoi à cet endroit :**

Permissions avant `<application>`, Activities dedans.

### 2.2 strings.xml

**Remplace tout** le contenu de `app/src/main/res/values/strings.xml` par :

```xml
<resources>
    <string name="app_name">TP3Maps</string>
    <string name="welcome">Welcome!\nPlease enter your details below to continue...</string>
    <string name="hint_name">Name</string>
    <string name="hint_email">Email</string>
    <string name="action_ok">OK</string>
    <string name="hello">Hello</string>
    <string name="action_next">NEXT</string>
    <string name="action_previous">PREVIOUS</string>
    <string name="action_add">AJOUTER</string>
    <string name="third_title">Evenements</string>
    <string name="photo_description">Photo illustrant le second ecran</string>
    <string name="empty_name">Entrez au moins un nom</string>
    <string name="status_loading">Telechargement des evenements...</string>
    <string name="status_error">Echec du telechargement (voir Logcat)</string>
    <string name="status_count">%1$d evenements</string>
    <string name="event_details">Latitude : %1$s\nLongitude : %2$s\nType : %3$s</string>
    <string name="event_title">Evenement</string>
    <string name="label_type">Type: %1$s</string>
    <string name="label_coords">Coordonnees : %1$s, %2$s</string>
    <string name="address_loading">Recherche de l\'adresse...</string>
    <string name="address_not_found">Adresse introuvable</string>
    <string name="address_unavailable">Geocodeur indisponible sur cet appareil</string>
    <string name="location_denied">Sans la permission de localisation, impossible de placer l\'evenement</string>
    <string name="you_are_here">Vous etes ici</string>
    <string name="hint_event_name">Nom de l\'evenement</string>
    <string name="waiting_position">En attente de la position GPS...</string>
    <string name="action_save">ENREGISTRER</string>
    <string name="empty_event_name">Donne un nom a l\'evenement</string>
    <string-array name="event_types">
        <item>concert</item>
        <item>forum</item>
        <item>conference</item>
        <item>sport</item>
        <item>exposition</item>
    </string-array>
</resources>
```

**Ce qui a été ajouté ou changé** par rapport au TP précédent :

```xml
    <string name="app_name">TP3Maps</string>
```

```xml
    <string name="action_add">AJOUTER</string>
```

```xml
    <string name="event_title">Evenement</string>
    <string name="label_type">Type: %1$s</string>
    <string name="label_coords">Coordonnees : %1$s, %2$s</string>
    <string name="address_loading">Recherche de l\'adresse...</string>
    <string name="address_not_found">Adresse introuvable</string>
    <string name="address_unavailable">Geocodeur indisponible sur cet appareil</string>
    <string name="location_denied">Sans la permission de localisation, impossible de placer l\'evenement</string>
    <string name="you_are_here">Vous etes ici</string>
    <string name="hint_event_name">Nom de l\'evenement</string>
    <string name="waiting_position">En attente de la position GPS...</string>
    <string name="action_save">ENREGISTRER</string>
    <string name="empty_event_name">Donne un nom a l\'evenement</string>
    <string-array name="event_types">
        <item>concert</item>
        <item>forum</item>
        <item>conference</item>
        <item>sport</item>
        <item>exposition</item>
    </string-array>
```

**Pourquoi :**

- Les textes de l'écran d'un événement (type, coordonnées, adresse) et du formulaire d'ajout
  (position, nom, ENREGISTRER, refus de la localisation).
- `event_types` : un `string-array`, la liste du `Spinner` (concert, forum...).
- Les apostrophes s'écrivent `\'`, sinon la compilation échoue.

**Pourquoi à cet endroit :**

Avec les autres textes.

## 3. L'écran d'un événement

### 3.1 activity_event.xml

**Nouveau fichier.** Clic droit sur `res/layout` > **New > Layout Resource File** > `activity_event`. Colle **tout** ce contenu :

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp"
    tools:context=".EventActivity">


    <TextView
        android:id="@+id/event_name"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:textSize="22sp"
        android:textStyle="bold"
        tools:text="Concert de rentree"
        />
    <TextView
        android:id="@+id/event_type"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="8dp"
        tools:text="Type: Concert"
        />

    <TextView
        android:id="@+id/event_coords"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="4dp"
        tools:text="Coordonnees : 49.0387, 2.0782" />
<!--  La partie du 1 du sujet : L'adresse trouvee par le Geocoder -->
    <TextView
        android:id="@+id/event_address"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"
        android:layout_marginTop="16dp"
        android:textSize="16sp"
        tools:text="Boulevard du Port, 95000 Cergy" />

    <Button
        android:id="@+id/back"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="24dp"
        android:onClick="previous"
        android:text="@string/action_previous"/>
</LinearLayout>
```

**Pourquoi :**

- Nom (gros, gras), type, coordonnées, puis l'adresse trouvée par le géocodeur.
- L'adresse a `layout_weight="1"` : elle prend la place restante, le bouton PREVIOUS reste en bas.

**Pourquoi à cet endroit :**

Chargé par `EventActivity`.

### 3.2 EventActivity.java

**Nouveau fichier.** Clic droit sur le paquet > **New > Java Class** > `EventActivity`. Colle **tout** ce contenu :

```java
package com.cyu.tp1intents;

import android.location.Address;
import android.location.Geocoder;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import java.io.IOException;
import java.util.List;
import java.util.Locale;

public class EventActivity extends AppCompatActivity {
    public static final String TAG = "EventActivity";

    // Les cles des extras : publiques pour que ThirdActivity les utilise aussi
    public static final String EXTRA_NAME = "com.cyu.tp1intents.name";
    public static final String EXTRA_LAT = "com.cyu.tp1intents.lat";
    public static final String EXTRA_LNG = "com.cyu.tp1intents.lng";
    public static final String EXTRA_TYPE = "com.cyu.tp1intents.type";

    private TextView adresse;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_event);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets barres = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(barres.left, barres.top, barres.right, barres.bottom);
            return insets;
        });

        String nom = getIntent().getStringExtra(EXTRA_NAME);
        String lat = getIntent().getStringExtra(EXTRA_LAT);
        String lng = getIntent().getStringExtra(EXTRA_LNG);
        String type = getIntent().getStringExtra(EXTRA_TYPE);

        ((TextView) findViewById(R.id.event_name)).setText(nom != null ? nom : "");
        ((TextView) findViewById(R.id.event_type)).setText(getString(R.string.label_type, type != null ? type : ""));
        ((TextView) findViewById(R.id.event_coords)).setText(getString(R.string.label_coords, lat != null ? lat : "", lng != null ? lng : ""));
        adresse = findViewById(R.id.event_address);

        if (lat != null && lng != null) {
            try {
                double doubleLat = Double.parseDouble(lat);
                double doubleLng = Double.parseDouble(lng);
                chercherAdresse(doubleLat, doubleLng);
            } catch (NumberFormatException e) {
                Log.e(TAG, "Erreur de conversion des coordonnees", e);
            }
        }
    }

    private void chercherAdresse(double lat, double lng) {
        if (!Geocoder.isPresent()) {
            adresse.setText(R.string.address_unavailable);
            return;
        }
        adresse.setText(R.string.address_loading);
        Geocoder geocodeur = new Geocoder(this, Locale.FRANCE);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            // Android 13+ : le resultat arrive plus tard, sur un autre thread
            geocodeur.getFromLocation(lat, lng, 1, resultats -> runOnUiThread(() -> montrer(resultats)));
        } else {
            // avant Android 13 : appel bloquant, donc dans un thread a part
            new Thread(() -> {
                List<Address> resultats = null;
                try {
                    resultats = geocodeur.getFromLocation(lat, lng, 1);
                } catch (IOException e) {
                    Log.e(TAG, "Geocodage impossible", e);
                }
                List<Address> fin = resultats;
                runOnUiThread(() -> montrer(fin));
            }).start();
        }
    }

    // toujours appelee sur le thread principal : elle peut toucher a l'ecran
    private void montrer(List<Address> resultats) {
        if (resultats == null || resultats.isEmpty()) {
            adresse.setText(R.string.address_not_found);
            return;
        }
        Address adresseTrouvee = resultats.get(0);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i <= adresseTrouvee.getMaxAddressLineIndex(); i++) {
            if (i > 0) sb.append("\n");
            sb.append(adresseTrouvee.getAddressLine(i));
        }
        adresse.setText(sb.toString());
    }

    public void previous(View view) {
        finish();
    }
}
```

**Pourquoi :**

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

**Pourquoi à cet endroit :**

L'adresse est cherchée dans `onCreate`, une fois, dès l'ouverture de l'écran.

## 4. Le formulaire avec la carte

### 4.1 activity_add_event.xml

**Nouveau fichier.** Clic droit sur `res/layout` > **New > Layout Resource File** > `activity_add_event`. Colle **tout** ce contenu :

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <org.osmdroid.views.MapView
        android:id="@+id/map"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1" />

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="16dp">

        <TextView
            android:id="@+id/position_text"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="@string/waiting_position" />

        <EditText
            android:id="@+id/new_name"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="8dp"
            android:hint="@string/hint_event_name"
            android:inputType="textCapSentences" />

        <Spinner
            android:id="@+id/new_type"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="8dp"
            android:entries="@array/event_types" />

        <Button
            android:id="@+id/save"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="16dp"
            android:enabled="false"
            android:onClick="save"
            android:text="@string/action_save" />

    </LinearLayout>

</LinearLayout>
```

**Pourquoi :**

- `org.osmdroid.views.MapView` : la carte, avec le nom complet de sa classe (elle ne vient pas
  d'Android). `layout_weight="1"` : elle prend tout le haut.
- En bas : la position, le nom (`EditText`), le type (`Spinner` rempli par `@array/event_types`)
  et ENREGISTRER, désactivé (`enabled="false"`) tant que la position n'est pas connue.

**Pourquoi à cet endroit :**

Chargé par `AddEventActivity`.

### 4.2 AddEventActivity.java

**Nouveau fichier.** Clic droit sur le paquet > **New > Java Class** > `AddEventActivity`. Colle **tout** ce contenu :

```java
package com.cyu.tp1intents;

import android.Manifest;
import android.annotation.SuppressLint;
import android.content.pm.PackageManager;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import org.osmdroid.config.Configuration;
import org.osmdroid.tileprovider.tilesource.TileSourceFactory;
import org.osmdroid.util.GeoPoint;
import org.osmdroid.views.MapView;
import org.osmdroid.views.overlay.Marker;

import java.util.Locale;

public class AddEventActivity extends AppCompatActivity {

    private static final String TAG = "AddEventActivity";

    // centre de depart : le campus des Chenes, a Cergy
    private static final GeoPoint CERGY = new GeoPoint(49.0353, 2.0700);

    private MapView carte;
    private Marker epingle;

    private TextView textePosition;
    private EditText champNom;
    private Spinner spinnerType;
    private Button boutonEnregistrer;

    private LocationManager gestionnaire;
    private Location positionActuelle;

    private final ActivityResultLauncher<String[]> demandePermission =
            registerForActivityResult(new ActivityResultContracts.RequestMultiplePermissions(), reponses -> {
                boolean accepte = Boolean.TRUE.equals(reponses.get(Manifest.permission.ACCESS_FINE_LOCATION))
                        || Boolean.TRUE.equals(reponses.get(Manifest.permission.ACCESS_COARSE_LOCATION));
                if (accepte) {
                    demarrerGps();
                } else {
                    Toast.makeText(this, R.string.location_denied, Toast.LENGTH_LONG).show();
                }
            });

    private boolean aLaPermission() {
        return ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
                || ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED;
    }

    private final LocationListener ecouteur = new LocationListener() {
        @Override
        public void onLocationChanged(@NonNull Location position) {
            placer(position);
        }

        @Override public void onProviderEnabled(@NonNull String fournisseur) { }
        @Override public void onProviderDisabled(@NonNull String fournisseur) { }
        @Override public void onStatusChanged(String fournisseur, int statut, Bundle extras) { }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // AVANT setContentView : osmdroid lit sa configuration en creant la MapView
        Configuration.getInstance().load(this, getSharedPreferences("osmdroid", MODE_PRIVATE));
        Configuration.getInstance().setUserAgentValue(getPackageName());

        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_add_event);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets barres = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(barres.left, barres.top, barres.right, barres.bottom);
            return insets;
        });

        carte = findViewById(R.id.map);
        carte.setTileSource(TileSourceFactory.MAPNIK);   // le style standard d'OpenStreetMap
        carte.setMultiTouchControls(true);               // zoom a deux doigts
        carte.getController().setZoom(16.0);
        carte.getController().setCenter(CERGY);

        epingle = new Marker(carte);
        epingle.setPosition(CERGY);
        epingle.setTitle(getString(R.string.you_are_here));
        carte.getOverlays().add(epingle);

        textePosition = findViewById(R.id.position_text);
        champNom = findViewById(R.id.new_name);
        spinnerType = findViewById(R.id.new_type);
        boutonEnregistrer = findViewById(R.id.save);

        if (!aLaPermission()) {
            demandePermission.launch(new String[]{
                    Manifest.permission.ACCESS_FINE_LOCATION,
                    Manifest.permission.ACCESS_COARSE_LOCATION});
        }
    }

    @SuppressLint("MissingPermission")
    private void demarrerGps() {
        if (!aLaPermission()) return;

        gestionnaire = (LocationManager) getSystemService(LOCATION_SERVICE);
        if (gestionnaire == null) return;

        Location derniere = null;
        if (gestionnaire.isProviderEnabled(LocationManager.GPS_PROVIDER)) {
            derniere = gestionnaire.getLastKnownLocation(LocationManager.GPS_PROVIDER);
        }
        if (derniere == null && gestionnaire.isProviderEnabled(LocationManager.NETWORK_PROVIDER)) {
            derniere = gestionnaire.getLastKnownLocation(LocationManager.NETWORK_PROVIDER);
        }
        if (derniere != null) {
            placer(derniere);
        }

        if (gestionnaire.isProviderEnabled(LocationManager.GPS_PROVIDER)) {
            gestionnaire.requestLocationUpdates(LocationManager.GPS_PROVIDER, 2000, 5, ecouteur);
        } else if (gestionnaire.isProviderEnabled(LocationManager.NETWORK_PROVIDER)) {
            gestionnaire.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, 2000, 5, ecouteur);
        }
    }

    private void placer(Location position) {
        positionActuelle = position;
        GeoPoint point = new GeoPoint(position.getLatitude(), position.getLongitude());
        epingle.setPosition(point);
        epingle.setTitle(getString(R.string.you_are_here));
        carte.getController().animateTo(point);
        carte.invalidate();

        if (textePosition != null) {
            textePosition.setText(String.format(Locale.US, "Position : %.4f, %.4f", position.getLatitude(), position.getLongitude()));
        }
        if (boutonEnregistrer != null) {
            boutonEnregistrer.setEnabled(true);
        }
    }

    public void save(View view) {
        String nom = champNom.getText().toString().trim();
        if (nom.isEmpty()) {
            champNom.setError(getString(R.string.empty_event_name));
            return;
        }
        if (positionActuelle == null) {
            return;
        }
        String type = (String) spinnerType.getSelectedItem();

        String lat = String.format(Locale.US, "%.4f", positionActuelle.getLatitude());
        String lng = String.format(Locale.US, "%.4f", positionActuelle.getLongitude());

        Event e = new Event(0, nom, lat, lng, type);
        EventDbHelper db = new EventDbHelper(this);
        db.ajouter(e);
        db.close();

        finish();
    }

    @Override
    protected void onResume() {
        super.onResume();
        carte.onResume();
        if (aLaPermission()) {
            demarrerGps();
        }
    }

    @Override
    protected void onPause() {
        if (gestionnaire != null) {
            gestionnaire.removeUpdates(ecouteur);
        }
        carte.onPause();
        super.onPause();
    }
}
```

**Pourquoi :**

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

**Pourquoi à cet endroit :**

Tout le formulaire est dans cette Activity : la carte, le GPS et l'enregistrement servent au même
écran.

## 5. La liste et la base

### 5.1 EventDbHelper.java

**Remplace tout** le contenu de `app/src/main/java/com/cyu/tp1intents/EventDbHelper.java` par :

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

    // 2.3 : insere un evenement cree sur le telephone, renvoie son ID (-1 si echec)
    public long ajouter(Event e) {
        ContentValues ligne = new ContentValues();
        ligne.put(NAME, e.name);
        ligne.put(LAT, e.lat);
        ligne.put(LNG, e.lng);
        ligne.put(TYPE, e.type);
        return getWritableDatabase().insert(TABLE_EVENTS, null, ligne);
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

**Ce qui a été ajouté ou changé** par rapport au TP précédent :

```java
    // 2.3 : insere un evenement cree sur le telephone, renvoie son ID (-1 si echec)
    public long ajouter(Event e) {
        ContentValues ligne = new ContentValues();
        ligne.put(NAME, e.name);
        ligne.put(LAT, e.lat);
        ligne.put(LNG, e.lng);
        ligne.put(TYPE, e.type);
        return getWritableDatabase().insert(TABLE_EVENTS, null, ligne);
    }

```

**Pourquoi :**

- `ajouter(Event e)` : insère **un** événement créé sur le téléphone, sans vider la table (à la
  différence de `remplacer`). Rend l'`ID` créé, ou -1 si l'insertion échoue.

**Pourquoi à cet endroit :**

Dans la classe de la base, à côté de `remplacer`.

### 5.2 activity_third.xml

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

    <LinearLayout
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="16dp"
        android:orientation="horizontal">

        <Button
            android:id="@+id/previous"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:onClick="previous"
            android:text="@string/action_previous" />

        <Button
            android:id="@+id/add_event"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginStart="16dp"
            android:onClick="addEvent"
            android:text="@string/action_add" />
    </LinearLayout>

</LinearLayout>
```

**Ce qui a été ajouté ou changé** par rapport au TP précédent :

```xml
    <LinearLayout
```

```xml
        android:orientation="horizontal">

        <Button
            android:id="@+id/previous"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:onClick="previous"
            android:text="@string/action_previous" />

        <Button
            android:id="@+id/add_event"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginStart="16dp"
            android:onClick="addEvent"
            android:text="@string/action_add" />
    </LinearLayout>
```

**Pourquoi :**

- Les boutons PREVIOUS et AJOUTER côte à côte, dans un `LinearLayout` horizontal.

**Pourquoi à cet endroit :**

En bas de la liste.

### 5.3 ThirdActivity.java

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

        // Au clic sur un element de la liste : ouvre EventActivity avec les infos
        liste.setOnItemClickListener((parent, vue, position, id) -> {
            Event e = events.get(position);
            Intent intent = new Intent(this, EventActivity.class);
            intent.putExtra(EventActivity.EXTRA_NAME, e.name);
            intent.putExtra(EventActivity.EXTRA_LAT, e.lat);
            intent.putExtra(EventActivity.EXTRA_LNG, e.lng);
            intent.putExtra(EventActivity.EXTRA_TYPE, e.type);
            startActivity(intent);
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

    public void addEvent(View view) {
        startActivity(new Intent(this, AddEventActivity.class));
    }

    // finish() suffit pour revenir : un nouvel intent empilerait une 2e SecondActivity
    public void previous(View view) {
        finish();
    }
}
```

**Ce qui a été ajouté ou changé** par rapport au TP précédent :

```java
        // Au clic sur un element de la liste : ouvre EventActivity avec les infos
```

```java
            Intent intent = new Intent(this, EventActivity.class);
            intent.putExtra(EventActivity.EXTRA_NAME, e.name);
            intent.putExtra(EventActivity.EXTRA_LAT, e.lat);
            intent.putExtra(EventActivity.EXTRA_LNG, e.lng);
            intent.putExtra(EventActivity.EXTRA_TYPE, e.type);
            startActivity(intent);
```

```java
    public void addEvent(View view) {
        startActivity(new Intent(this, AddEventActivity.class));
    }

```

**Pourquoi :**

- Au clic sur un événement : au lieu de l'`AlertDialog` du TP2, un `Intent` vers `EventActivity`
  avec les 4 extras.
- `addEvent(View)` : ouvre le formulaire. Au retour, `onResume` relit la base : le nouvel
  événement apparaît en bas.

**Pourquoi à cet endroit :**

Le clic sur la liste est réglé dans `onCreate`, avec la liste.

## 6. Tester

Clic sur EVENT1 : son écran, puis l'adresse. AJOUTER : accepte la permission de localisation.
Sur l'émulateur, donne une position avec **⋯ > Location** (ou `adb emu geo fix 2.07 49.035`) :
l'épingle bouge, ENREGISTRER s'active. Nom, type, ENREGISTRER : l'événement est en bas de la liste.
