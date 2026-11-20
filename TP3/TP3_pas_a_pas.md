# TP3 pas à pas : géocodage, carte OpenStreetMap, position GPS, nouvel événement

Construit depuis `tp3.pdf` et **ton** projet TP2 (`C:\Users\User\AndroidStudioProjects\TP2Events`).
Rien n'est codé à ta place : chaque étape dit **quoi écrire, où, et pourquoi**. Les lignes
importantes sont laissées en trou `/* À TOI ... */`. Les réponses aux trous sont à la toute fin
(partie 9), à ouvrir **seulement après avoir essayé**.

Plan : **0.** préparer le projet. **1.** géocodage (partie 1 du sujet). **2.** la carte OSM (2.1).
**3.** la position GPS (2.2). **4.** le formulaire et l'enregistrement (2.3). **5.** les bonus.
**6.** tester sur l'émulateur. **7.** rendre. **8.** questions de compréhension. **9.** les trous corrigés.
**10.** finaliser : ton état au 6 novembre et ce qui reste.

Après chaque étape, il y a un **point de contrôle** : lance l'application et vérifie avant de
passer à la suite. Une erreur trouvée tout de suite se corrige en 2 minutes ; cinq erreurs
empilées prennent une soirée.

---

## 0. Préparer le projet

### 0.1 Copier le TP2

Comme pour le TP2, on travaille sur une **copie**, pour que ton rendu TP2 reste intact.

1. Ferme Android Studio.
2. Dans l'explorateur : copie `AndroidStudioProjects\TP2Events` en `AndroidStudioProjects\TP3Maps`.
3. Dans la copie, supprime les dossiers `build`, `app\build` et `.idea` (ils seront recréés).
4. Ouvre `TP3Maps` dans Android Studio (**File > Open**) et laisse le Sync Gradle finir.
5. Change trois lignes :

| Fichier                    | Ligne                                        | Pourquoi                                                                                |
| -------------------------- | -------------------------------------------- | --------------------------------------------------------------------------------------- |
| `settings.gradle.kts`    | `rootProject.name = "TP3Maps"`             | le nom du projet dans Studio                                                            |
| `app/build.gradle.kts`   | `applicationId = "com.cyu.tp3maps"`        | l'émulateur voit une **3ᵉ application** : installer le TP3 n'écrase pas le TP2 |
| `res/values/strings.xml` | `<string name="app_name">TP3Maps</string>` | le nom sous l'icône                                                                    |

Le paquet Java reste `com.cyu.tp1intents` (le `namespace`), comme au TP2. `applicationId`
identifie l'application sur le téléphone ; `namespace` sert seulement à générer la classe `R`.

**Point de contrôle 0** : lance l'application. Tu dois retrouver exactement ton TP2 (formulaire,
2ᵉ écran, liste des 15 événements), avec « TP3Maps » sous l'icône.

### 0.2 Ce que tu vas créer

| Fichier                                                | Nouveau ?         | Partie du sujet                                                           |
| ------------------------------------------------------ | ----------------- | ------------------------------------------------------------------------- |
| `EventActivity.java` + `activity_event.xml`        | **nouveau** | **1** l'écran d'un événement, avec son adresse                   |
| `AddEventActivity.java` + `activity_add_event.xml` | **nouveau** | **2.1** la carte, **2.2** le GPS, **2.3** le formulaire |
| `ThirdActivity.java`                                 | modifié          | le clic ouvre `EventActivity` ; un bouton ouvre `AddEventActivity`    |
| `EventDbHelper.java`                                 | modifié          | **2.3** méthode `ajouter(Event)`                                 |
| `AndroidManifest.xml`                                | modifié          | permissions de localisation, déclaration des 2 activités                |
| `libs.versions.toml`, `app/build.gradle.kts`       | modifié          | la bibliothèque osmdroid                                                 |
| `strings.xml`                                        | modifié          | les nouveaux textes                                                       |

> **Réfléchis** : pourquoi une seule activité pour la carte, le GPS **et** le formulaire, au lieu
> de trois ? (réponse en partie 8)

---

## 1. Partie 1 du sujet : transformer les coordonnées en adresse

> Use the Geocoder to reverse geocode the coordinates of each event and display an address for
> each event in the corresponding field of the event activity layout.

Le sujet parle de « l'event activity ». Au TP2, un clic sur un événement ouvrait seulement une
**boîte de dialogue** (`AlertDialog`). Il faut donc d'abord un vrai **écran d'événement**, avec un
champ « adresse ».

### Rappel : géocodage et géocodage inverse

| Sens                                               | Méthode                                | Exemple                          |
| -------------------------------------------------- | --------------------------------------- | -------------------------------- |
| adresse → coordonnées (géocodage)               | `getFromLocationName("Cergy", 1)`     | → 49.03, 2.06                   |
| coordonnées → adresse (**inverse**, ce TP) | `getFromLocation(49.0353, 2.0700, 1)` | → « Bd du Port, 95000 Cergy » |

Le dernier paramètre (`1`) est le **nombre maximum de résultats**. Le résultat est une
`List<Address>` ; `address.getAddressLine(0)` donne l'adresse complète sur une ligne.

**Deux pièges** :

1. `Geocoder` interroge un **serveur** (celui de Google, fourni par le téléphone). C'est donc un
   accès réseau : **interdit sur le thread principal** (l'écran gèlerait, et Android lève une
   exception). Depuis Android 13 (API 33), il existe une version avec **callback** qui ne bloque
   pas. Ton `minSdk` est 24 : il faut donc **les deux versions**, choisies selon la version
   d'Android.
2. Sur l'émulateur, le géocodeur n'existe que si l'image système est une image **Google APIs** ou
   **Google Play**. `Geocoder.isPresent()` le dit. Sur une image « AOSP » nue, il répond `false`.

### 1.1 Les textes (`strings.xml`)

**Ce qu'est ce fichier.** `strings.xml` contient **tous** les textes de l'application, chacun avec
un nom. Dans le code, on n'écrit pas `"Adresse introuvable"` mais `R.string.address_not_found`.
On **ajoute** des lignes ; on n'efface **rien** de ce qui vient du TP1 et du TP2 : ces textes
servent encore aux autres écrans.

**Dans Android Studio, clic par clic :**

1. À gauche, le panneau **Project** (s'il est fermé : **Alt+1**). En haut de ce panneau, vérifie
   que la vue choisie est **Android** (menu déroulant).
2. Déplie **app > res > values**, double-clique sur **strings.xml**. Le fichier s'ouvre au milieu.
3. Va sur la **dernière ligne**, `</resources>`. Clique **au début** de cette ligne (avant le `<`),
   appuie sur **Entrée** : une ligne vide apparaît au-dessus.
4. Monte sur cette ligne vide et colle les 6 lignes ci-dessous.

```xml
<string name="event_title">Evenement</string>
<string name="label_type">Type : %1$s</string>
<string name="label_coords">Coordonnees : %1$s, %2$s</string>
<string name="address_loading">Recherche de l\'adresse...</string>
<string name="address_not_found">Adresse introuvable</string>
<string name="address_unavailable">Geocodeur indisponible sur cet appareil</string>
```

**Le fichier complet après ton ajout** (les 16 premières lignes sont celles du TP2, intactes ;
seul `app_name` a changé à l'étape 0) :

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
    <string name="third_title">Evenements</string>
    <string name="photo_description">Photo illustrant le second ecran</string>
    <string name="empty_name">Entrez au moins un nom</string>
    <string name="status_loading">Telechargement des evenements...</string>
    <string name="status_error">Echec du telechargement (voir Logcat)</string>
    <string name="status_count">%1$d evenements</string>
    <string name="event_details">Latitude : %1$s\nLongitude : %2$s\nType : %3$s</string>
    <string name="event_title">Evenement</string>
    <string name="label_type">Type : %1$s</string>
    <string name="label_coords">Coordonnees : %1$s, %2$s</string>
    <string name="address_loading">Recherche de l\'adresse...</string>
    <string name="address_not_found">Adresse introuvable</string>
    <string name="address_unavailable">Geocodeur indisponible sur cet appareil</string>
</resources>
```

Les nouvelles lignes vont **avant** `</resources>`, jamais après : `</resources>` ferme la liste.
Les espaces au début des lignes ne comptent pas, ils servent à la lisibilité (**Ctrl+Alt+L** les
remet en ordre).

Deux détails de ces lignes :

- **`%1$s`** est une **place réservée** : `getString(R.string.label_type, "concert")` donne
  « Type : concert ». `%1$s` = 1ᵉʳ argument, de type texte (`s` pour *string*) ; `%2$s` = 2ᵉ.
- **`\'`** : dans `strings.xml`, une apostrophe **doit** être précédée d'une barre oblique
  inverse. `l'adresse` sans elle fait échouer la compilation (erreur « Invalid unicode escape
  sequence » ou « Apostrophe not preceded by \ »). C'est pour ça que tes textes du TP2 évitaient
  les apostrophes.

**Point de contrôle 1.1** : menu **Build > Make Project** (**Ctrl+F9**). Pas d'erreur en rouge
dans l'onglet **Build** en bas : c'est bon.

### 1.2 Le layout `res/layout/activity_event.xml`

**Ce qu'est un layout.** Un fichier XML qui décrit **ce qu'on voit à l'écran** : chaque balise
est une vue (un texte, un bouton...). Le tableau ci-dessous n'est **pas** quelque chose à créer
dans Android Studio : c'est seulement la liste des 5 vues à mettre dans le fichier. Une ligne du
tableau = une balise XML.

| Vue                      | id                | Ce qu'elle affichera                                       |
| ------------------------ | ----------------- | ---------------------------------------------------------- |
| `TextView` grand, gras | `event_name`    | le nom                                                     |
| `TextView`             | `event_type`    | « Type : concert »                                       |
| `TextView`             | `event_coords`  | « Coordonnees : 49.0387, 2.0782 »                        |
| `TextView`             | `event_address` | **l'adresse** : c'est le champ demandé par le sujet |
| `Button`               | `back`          | le bouton PREVIOUS                                         |

Le `LinearLayout` est la **boîte** qui contient les 5 vues et les empile de haut en bas
(`orientation="vertical"`), dans l'ordre où elles sont écrites.

**Étape A : créer le fichier, clic par clic**

1. Panneau **Project** (vue **Android**) : déplie **app > res**.
2. **Clic droit sur le dossier `layout`** > **New** > **Layout Resource File**.
3. Une fenêtre s'ouvre :
   - **File name** : `activity_event` (sans `.xml`, Studio l'ajoute) ;
   - **Root element** : efface ce qui est écrit (souvent
     `androidx.constraintlayout.widget.ConstraintLayout`) et tape **`LinearLayout`** ;
   - laisse le reste tel quel, clique **OK**.
4. Le fichier s'ouvre, souvent en mode **Design** (un écran de téléphone vide, avec une palette
   à gauche). En **haut à droite** de l'éditeur, il y a trois boutons : **Code**, **Split**,
   **Design**. Clique sur **Split** : le XML à gauche, l'aperçu à droite. Chaque modification du
   XML apparaît dans l'aperçu.

**Étape B : remplacer le contenu par celui-ci**

Dans la partie XML, sélectionne tout (**Ctrl+A**) et colle :

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
        tools:text="Concert de rentree" />

    <TextView
        android:id="@+id/event_type"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="8dp"
        tools:text="Type : concert" />

    <TextView
        android:id="@+id/event_coords"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="4dp"
        tools:text="Coordonnees : 49.0387, 2.0782" />

    <!-- partie 1 du sujet : l'adresse trouvee par le Geocoder -->
    <TextView
        android:id="@+id/event_address"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="16dp"
        android:textSize="16sp"
        tools:text="Boulevard du Port, 95000 Cergy" />

    <Button
        android:id="@+id/back"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="24dp"
        android:onClick="previous"
        android:text="@string/action_previous" />

</LinearLayout>
```

**Lis-le attribut par attribut, c'est la partie à comprendre :**

| Attribut                                  | Ce qu'il fait                                                                                                                                                        |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `android:id="@+id/event_name"`          | donne un nom à la vue. Le `+` veut dire « crée ce nom ». En Java, `findViewById(R.id.event_name)` la retrouve                                                |
| `layout_width` / `layout_height`      | obligatoires sur **chaque** vue. `wrap_content` = juste la taille du contenu ; `match_parent` = toute la largeur (ou hauteur) de la boîte qui la contient |
| `orientation="vertical"`                | le `LinearLayout` empile ses vues de haut en bas (`horizontal` : de gauche à droite)                                                                            |
| `padding="16dp"`                        | marge **intérieure** de la boîte : rien ne colle au bord de l'écran                                                                                         |
| `layout_marginTop="8dp"`                | marge **au-dessus** d'une vue : l'espace avec la précédente                                                                                                  |
| `textSize="22sp"`, `textStyle="bold"` | taille et graisse du texte. `sp` pour le texte, `dp` pour le reste (les deux s'adaptent à l'écran)                                                             |
| `tools:text="..."`                      | texte visible **seulement dans l'aperçu** de Studio, jamais sur le téléphone. Le vrai texte est mis par le Java (`setText`)                               |
| `tools:context=".EventActivity"`        | dit à Studio quelle activité utilise ce layout (pour l'aperçu)                                                                                                    |
| `android:onClick="previous"`            | au clic, Android appelle la méthode `public void previous(View view)` de l'activité                                                                              |
| `<!-- ... -->`                          | un commentaire XML                                                                                                                                                   |

Compare avec ton `activity_third.xml` : c'est la même construction (un `LinearLayout`
vertical, des vues dedans, un bouton `previous` en bas).

**Si tu préfères la souris (mode Design)** : la palette à gauche contient **TextView** (dans
*Common* ou *Text*) et **Button** (dans *Buttons*). Glisse-les dans l'arbre **Component Tree**
(en bas à gauche), sous le `LinearLayout`. Puis, la vue sélectionnée, le panneau
**Attributes** (à droite) permet de remplir **id**, **layout_width**, etc. Ça marche, mais c'est
plus long et on voit moins ce qu'on fait : le mode **Code** ou **Split** est plus sûr pour ce TP.

**Point de contrôle 1.2** : dans l'aperçu (Split), tu vois le nom en gros, deux lignes en
dessous, l'adresse, puis le bouton PREVIOUS. Aucun soulignement rouge dans le XML. Un
`@string/action_previous` en rouge voudrait dire que ce nom n'existe pas dans `strings.xml`
(il y est depuis le TP1 : vérifie l'orthographe).

À ce stade, `tools:context=".EventActivity"` peut être souligné : la classe n'existe pas encore.
Ce sera réglé à l'étape suivante.

### 1.3 L'activité `EventActivity.java`

Crée la classe (clic droit sur le paquet > New > Activity > Empty Views Activity, **ou** une
classe Java vide ; dans ce cas, déclare-la toi-même dans le manifeste, voir 1.5).

Elle reçoit l'événement par l'**Intent** (des *extras*), l'affiche, puis lance la recherche
d'adresse.

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

    private static final String TAG = "EventActivity";

    // les cles des extras : publiques pour que ThirdActivity les utilise aussi
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

        ((TextView) findViewById(R.id.event_name)).setText(nom);
        ((TextView) findViewById(R.id.event_type)).setText(getString(R.string.label_type, type));
        ((TextView) findViewById(R.id.event_coords)).setText(getString(R.string.label_coords, lat, lng));
        adresse = findViewById(R.id.event_address);

        // les coordonnees sont stockees en TEXT dans la base : on les convertit
        /* À TOI (trou 1) : convertir lat et lng en double, puis appeler chercherAdresse */
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
                    /* À TOI (trou 2) : l'appel bloquant du geocodage inverse, 1 resultat */
                } catch (IOException e) {
                    Log.e(TAG, "geocodage impossible", e);
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
        /* À TOI (trou 3) : ecrire la premiere ligne de la premiere adresse dans le TextView */
    }

    public void previous(View view) {
        finish();
    }
}
```

Trois choses à comprendre avant d'écrire les trous :

- **`runOnUiThread(...)`** : seul le thread principal a le droit de modifier une vue. Le résultat
  du géocodage arrive sur un autre thread ; `runOnUiThread` renvoie le travail au thread principal.
- **`List<Address> fin = resultats;`** : une lambda Java ne peut utiliser qu'une variable
  *effectivement finale* (jamais réaffectée). `resultats` est réaffectée dans le `try`, d'où la
  copie.
- **L'avertissement « deprecated »** sur `getFromLocation(lat, lng, 1)` : normal, la version
  bloquante est dépréciée depuis l'API 33. On ne l'appelle que sur les vieux Android, c'est
  exactement ce qu'il faut faire. Tu peux ajouter `@SuppressWarnings("deprecation")` au-dessus de
  `chercherAdresse`.

### 1.4 Ouvrir `EventActivity` depuis la liste (`ThirdActivity`)

Dans `onCreate`, ton `setOnItemClickListener` ouvre un `AlertDialog`. Remplace son contenu :
au lieu du dialogue, crée un `Intent` vers `EventActivity`, mets les quatre extras, et lance-le.

```java
liste.setOnItemClickListener((parent, vue, position, id) -> {
    Event e = events.get(position);
    Intent intent = new Intent(this, EventActivity.class);
    /* À TOI (trou 4) : les 4 putExtra avec les cles EXTRA_... d'EventActivity */
    startActivity(intent);
});
```

L'import `androidx.appcompat.app.AlertDialog` devient inutile : supprime-le.

### 1.5 Le manifeste

Si Studio ne l'a pas fait (classe créée à la main), ajoute dans `<application>` :

```xml
<activity
    android:name=".EventActivity"
    android:exported="false" />
```

`exported="false"` : aucune autre application ne peut ouvrir cet écran. Seule la nôtre l'ouvre.

**Point de contrôle 1** : clique sur « Concert de rentree ». Le nouvel écran s'affiche, puis,
après une seconde, une adresse à Cergy remplace « Recherche de l'adresse... ». Si tu lis
« Geocodeur indisponible », ton émulateur n'est pas une image Google : voir partie 6.

---

## 2. Partie 2.1 : une carte OpenStreetMap avec une épingle

> Create a simple OpenStreetMaps Maps Activity displaying a pin with a location.

On utilise **osmdroid**, la bibliothèque Android d'OpenStreetMap (`github.com/osmdroid/osmdroid`).
Pas de clé d'API, contrairement à Google Maps. Le sujet dit « on google maps » par erreur :
c'est bien une carte OSM qu'il demande.

### 2.1 Ajouter la bibliothèque

Dans `gradle/libs.versions.toml`, ajoute une ligne dans chacune des deux sections :

```toml
[versions]
osmdroid = "6.1.20"

[libraries]
osmdroid-android = { group = "org.osmdroid", name = "osmdroid-android", version.ref = "osmdroid" }
```

Dans `app/build.gradle.kts`, dans `dependencies { ... }` :

```kotlin
implementation(libs.osmdroid.android)
```

Le tiret de `osmdroid-android` devient un **point** dans `libs.osmdroid.android` : c'est la règle
du catalogue de versions de Gradle. Puis **Sync Now** (bandeau en haut de l'éditeur).

### 2.2 Les permissions réseau (manifeste)

`INTERNET` est déjà là (TP2). Ajoute :

```xml
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

osmdroid télécharge les **tuiles** (les petites images carrées de la carte) depuis les serveurs
d'OpenStreetMap ; il vérifie l'état du réseau avant.

### 2.3 Le layout `activity_add_event.xml`

Pour l'instant, juste la carte qui remplit l'écran (le formulaire viendra en partie 4) :

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

</LinearLayout>
```

La balise porte le **nom complet de la classe** (`org.osmdroid.views.MapView`) : c'est comme ça
qu'on place une vue qui ne vient pas d'Android.

### 2.4 L'activité `AddEventActivity.java`

```java
package com.cyu.tp1intents;

import android.os.Bundle;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import org.osmdroid.config.Configuration;
import org.osmdroid.tileprovider.tilesource.TileSourceFactory;
import org.osmdroid.util.GeoPoint;
import org.osmdroid.views.MapView;
import org.osmdroid.views.overlay.Marker;

public class AddEventActivity extends AppCompatActivity {

    private static final String TAG = "AddEventActivity";

    // centre de depart : le campus des Chenes, a Cergy
    private static final GeoPoint CERGY = new GeoPoint(49.0353, 2.0700);

    private MapView carte;
    private Marker epingle;

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

        /* À TOI (trou 5) : creer l'epingle (new Marker(carte)), la placer sur CERGY,
           lui donner un titre, puis l'ajouter aux overlays de la carte */
    }

    // la carte doit suivre le cycle de vie de l'activite
    @Override
    protected void onResume() {
        super.onResume();
        carte.onResume();
    }

    @Override
    protected void onPause() {
        carte.onPause();
        super.onPause();
    }
}
```

Pourquoi chaque ligne étrange :

- **`setUserAgentValue(getPackageName())`** : les serveurs d'OpenStreetMap **bloquent** les
  applications qui ne s'identifient pas. Sans cette ligne, la carte reste grise.
- **Overlay** (calque) : tout ce qu'on dessine *par-dessus* la carte (épingle, position, tracé)
  est un overlay, ajouté à la liste `carte.getOverlays()`.
- **`carte.onResume()` / `onPause()`** : la carte arrête ses téléchargements et ses capteurs quand
  l'écran n'est plus visible. Même logique que ton `BroadcastReceiver` du TP2, enregistré dans
  `onResume` et retiré dans `onPause`.

### 2.5 L'ouvrir depuis la liste

1. Manifeste : déclare `.AddEventActivity` comme `EventActivity` (`exported="false"`).
2. `activity_third.xml` : ajoute un bouton **au-dessus** de « PREVIOUS » :
   `android:onClick="addEvent"`, texte `@string/action_add` (ajoute
   `<string name="action_add">AJOUTER UN EVENEMENT</string>`).
3. `ThirdActivity.java` : écris la méthode publique `addEvent(View view)` qui démarre
   `AddEventActivity` avec un `Intent`. Tu l'as déjà fait trois fois depuis le TP1.

**Point de contrôle 2** : « AJOUTER UN EVENEMENT » ouvre une carte de Cergy avec une épingle.
La carte est grise ? Vérifie la connexion internet de l'émulateur et la ligne `setUserAgentValue`.

---

## 3. Partie 2.2 : la position actuelle de l'appareil

> Make your application location-aware, get the current device location and display it on the
> map. Pay attention to the permissions.

On utilise le schéma du cours (`LocationManager` + `LocationListener`), en 5 étapes.

### Étape 1 : déclarer les permissions (manifeste)

```xml
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
```

| Permission                 | Précision                    | Source          |
| -------------------------- | ----------------------------- | --------------- |
| `ACCESS_FINE_LOCATION`   | quelques mètres              | GPS             |
| `ACCESS_COARSE_LOCATION` | quelques centaines de mètres | antennes, Wi-Fi |

Depuis Android 12, quand on demande `FINE`, il **faut** aussi demander `COARSE` : l'utilisateur
peut choisir « position approximative » dans la fenêtre système.

### Étape 2 : demander la permission **pendant l'exécution**

Le manifeste ne suffit plus depuis Android 6 (API 23) : la localisation est une permission
**dangereuse**, l'utilisateur doit dire oui dans une fenêtre. On utilise l'API moderne
`registerForActivityResult` (elle est dans `activity-ktx`, déjà dans tes dépendances).

Dans `AddEventActivity`, en attribut de classe :

```java
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
```

(`<string name="location_denied">Sans la permission de localisation, impossible de placer l\'evenement</string>`)

Et une petite méthode pour savoir si on l'a déjà :

```java
private boolean aLaPermission() {
    /* À TOI (trou 6) : vrai si ACCESS_FINE_LOCATION OU ACCESS_COARSE_LOCATION est accordee
       (ContextCompat.checkSelfPermission(...) == PackageManager.PERMISSION_GRANTED) */
}
```

À la fin d'`onCreate` :

```java
if (!aLaPermission()) {
    demandePermission.launch(new String[]{
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION});
}
```

> **Réfléchis** : pourquoi `registerForActivityResult` est-il appelé en **attribut** (à la
> création de l'objet) et pas au moment du clic ? (partie 8)

### Étape 3 : écrire le listener (4 méthodes)

```java
private final LocationListener ecouteur = new LocationListener() {
    @Override
    public void onLocationChanged(@NonNull Location position) {
        placer(position);
    }

    // les 3 suivantes : obligatoires sur Android < 11 (sinon plantage au premier changement d'etat)
    @Override public void onProviderEnabled(@NonNull String fournisseur) { }
    @Override public void onProviderDisabled(@NonNull String fournisseur) { }
    @Override public void onStatusChanged(String fournisseur, int statut, Bundle extras) { }
};
```

Pourquoi pas une lambda `position -> placer(position)` ? Depuis Android 11, seules
`onLocationChanged` est abstraite et une lambda compile. Mais ton `minSdk` est 24 : sur un vieux
téléphone, les 3 autres méthodes n'ont pas de version par défaut, et le premier appel à l'une
d'elles plante (`AbstractMethodError`). La classe anonyme avec les 4 méthodes marche partout.

### Étape 4 : demander les mises à jour

```java
private LocationManager gestionnaire;
private Location positionActuelle;   // null tant qu'on n'a pas de position

@SuppressLint("MissingPermission")   // on n'appelle demarrerGps qu'apres aLaPermission()
private void demarrerGps() {
    gestionnaire = (LocationManager) getSystemService(LOCATION_SERVICE);

    // la derniere position connue s'affiche tout de suite, sans attendre le GPS
    Location derniere = gestionnaire.getLastKnownLocation(LocationManager.GPS_PROVIDER);
    if (derniere != null) {
        placer(derniere);
    }

    /* À TOI (trou 7) : requestLocationUpdates sur GPS_PROVIDER,
       au plus toutes les 2 secondes, au moins 5 metres de deplacement, avec ecouteur */
}
```

Les deux nombres de `requestLocationUpdates(fournisseur, tempsMin, distanceMin, listener)` sont
des **minimums** : pas plus d'une mise à jour toutes les 2 000 ms, et seulement si on a bougé
d'au moins 5 m. Ça économise la batterie.

### Étape 5 : arrêter, et reprendre

Le GPS est ce qui vide le plus vite une batterie : on l'arrête dès que l'écran n'est plus visible.

```java
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
```

(remplace les `onResume` / `onPause` de la partie 2)

### La méthode `placer` : montrer la position sur la carte

L'épingle de la partie 2 était fixe sur Cergy. Maintenant, **c'est elle qui suit l'appareil** :

```java
private void placer(Location position) {
    positionActuelle = position;
    GeoPoint point = new GeoPoint(position.getLatitude(), position.getLongitude());
    epingle.setPosition(point);
    epingle.setTitle(getString(R.string.you_are_here));
    carte.getController().animateTo(point);
    carte.invalidate();   // redessine la carte avec l'epingle a sa nouvelle place
}
```

(`<string name="you_are_here">Vous etes ici</string>`)

`onLocationChanged` est appelée **sur le thread principal** : on peut toucher à la carte
directement, sans `runOnUiThread`.

**Point de contrôle 3** : ouvre l'écran d'ajout. La fenêtre de permission apparaît ; accepte.
Puis, dans l'émulateur, **⋯ (Extended controls) > Location**, cherche une adresse (par exemple
« Cergy-Préfecture »), clique sur **Set location**. L'épingle saute à cet endroit et la carte la
suit. Envoie une 2ᵉ position : elle se déplace encore.

Teste aussi le **refus** : désinstalle l'application, relance, refuse la permission. Tu dois voir
le Toast, et rien ne doit planter.

---

## 4. Partie 2.3 : nom et type, puis enregistrement

> After getting the current location, let the user define the rest of the event details (NAME
> and TYPE) and save the event in the existing database. The new event should now appear in the
> list.

### 4.1 Le formulaire sous la carte

Dans `activity_add_event.xml`, **après** la `MapView`, ajoute :

| Vue          | id                | Détail                                                                      |
| ------------ | ----------------- | ---------------------------------------------------------------------------- |
| `TextView` | `position_text` | « En attente de la position GPS... » puis les coordonnées                 |
| `EditText` | `new_name`      | `android:hint="@string/hint_event_name"`, `inputType="textCapSentences"` |
| `Spinner`  | `new_type`      | `android:entries="@array/event_types"`                                     |
| `Button`   | `save`          | `android:onClick="save"`, `android:enabled="false"`                      |

La carte garde `layout_height="0dp"` + `layout_weight="1"` : elle prend toute la place qui reste
au-dessus du formulaire. Mets `android:padding="16dp"` sur un `LinearLayout` qui entoure le
formulaire, pas sur la carte.

Les types possibles viennent de ton fichier `events.txt`. Dans `strings.xml` :

```xml
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

Un `Spinner` plutôt qu'un champ libre : l'utilisateur ne peut pas inventer « Concerts » ou
« sprot », et tous les types restent cohérents avec ceux de la base.

> **Réfléchis** : pourquoi le bouton ENREGISTRER est-il **désactivé** au départ ? (partie 8)

En attributs de `AddEventActivity`, ajoute les 4 vues, et récupère-les dans `onCreate` (après
`setContentView`) :

```java
private TextView textePosition;
private EditText champNom;
private Spinner spinnerType;
private Button boutonEnregistrer;
```

```java
textePosition = findViewById(R.id.position_text);
champNom = findViewById(R.id.new_name);
spinnerType = findViewById(R.id.new_type);
boutonEnregistrer = findViewById(R.id.save);
```

Dans `placer(...)`, ajoute deux lignes : afficher les coordonnées dans `position_text`, et
**activer** le bouton (`setEnabled(true)`).

### 4.2 La méthode `ajouter` dans `EventDbHelper`

`remplacer(...)` vidait la table avant d'insérer : ici, on veut **ajouter une ligne** sans rien
effacer.

```java
// 2.3 : insere un evenement cree sur le telephone, renvoie son ID (-1 si echec)
public long ajouter(Event e) {
    ContentValues ligne = new ContentValues();
    /* À TOI (trou 8) : les 4 put, comme dans remplacer */
    return getWritableDatabase().insert(TABLE_EVENTS, null, ligne);
}
```

On ne met **pas** l'ID : la colonne est `INTEGER PRIMARY KEY`, SQLite lui donne tout seul la
valeur suivante. C'est le format `(ID, NAME, LAT, LNG, TYPE)` demandé par le sujet.

### 4.3 La méthode `save` dans `AddEventActivity`

```java
public void save(View view) {
    String nom = champNom.getText().toString().trim();
    if (nom.isEmpty()) {
        champNom.setError(getString(R.string.empty_event_name));
        return;
    }
    if (positionActuelle == null) {
        return;   // ne devrait pas arriver : le bouton est desactive sans position
    }
    String type = (String) spinnerType.getSelectedItem();

    // Locale.US : un POINT decimal, comme dans le fichier telecharge
    String lat = String.format(Locale.US, "%.4f", positionActuelle.getLatitude());
    String lng = String.format(Locale.US, "%.4f", positionActuelle.getLongitude());

    /* À TOI (trou 9) : creer l'Event (id 0), l'ajouter avec un EventDbHelper,
       fermer le helper, puis revenir a la liste */
}
```

**Le piège du `Locale.US`** : ton téléphone est en français. `String.format("%.4f", 49.0353)`
donnerait **« 49,0353 »**, avec une virgule. Plus tard, `Double.parseDouble("49,0353")` dans
`EventActivity` lèverait une `NumberFormatException`, et l'écran de l'événement planterait.
`Locale.US` force le point.

**Revenir à la liste** : avec `finish()`, **pas** avec `startActivity(new Intent(this, ThirdActivity.class))`.
Au retour, `ThirdActivity.onResume()` est rappelée, et ton `onResume` appelle déjà `afficher()`,
qui relit la base : le nouvel événement apparaît **sans une ligne de code en plus**.

**Point de contrôle 4** : place la position, écris « Soiree jeux », type « forum », ENREGISTRER.
Tu reviens à la liste, qui affiche **16 événements** ; « Soiree jeux » est en bas. Clique dessus :
l'écran de l'événement montre ses coordonnées et **son adresse** (la partie 1 marche aussi sur
les nouveaux événements). Ferme et relance l'application : il est toujours là, il est en base.

---

## 5. Les bonus

### 5.1 « Take care of the application's activity stack »

La **pile d'activités** : chaque `startActivity` pose un écran sur la pile, chaque `finish()` (ou
retour) l'enlève. Le piège classique :

| Code au moment d'enregistrer                             | Pile après                                    | Problème                                                                     |
| -------------------------------------------------------- | ---------------------------------------------- | ----------------------------------------------------------------------------- |
| `startActivity(new Intent(this, ThirdActivity.class))` | Main, Second, **Third, AddEvent, Third** | deux listes empilées ; « retour » ramène au formulaire déjà enregistré |
| `finish()`                                             | Main, Second, **Third**                  | propre                                                                        |

Ce que tu fais déjà bien depuis le TP2 : `previous()` appelle `finish()`. Pour le rendu, dessine
la pile à chaque étape (Main → Second → Third → AddEvent → retour Third → Event → retour Third)
et explique ton choix : c'est exactement ce que le bonus attend.

Vérification : après un enregistrement, appuie sur **retour** autant de fois que possible. Tu
dois passer par Third, Second, puis quitter. **Jamais** revoir le formulaire.

### 5.2 « Think of and add more event fields »

Exemple : `DATE` (date de l'événement) et `ADDRESS` (l'adresse trouvée par le géocodeur, gardée
pour ne pas la redemander à chaque fois).

Ce qu'il faut changer :

1. `Event` : deux attributs de plus.
2. `EventDbHelper` : `DB_VERSION = 2`, les colonnes dans `onCreate`, et **`onUpgrade`**.
3. Le formulaire : un champ date (un `DatePickerDialog` est le plus propre).

**Attention à `onUpgrade`** : le tien fait `DROP TABLE` puis `onCreate`. Passer en version 2
**effacerait tous les événements**, y compris ceux créés à la main (les 15 du fichier seraient
retéléchargés, pas les tiens). Mieux :

```java
@Override
public void onUpgrade(SQLiteDatabase db, int ancienne, int nouvelle) {
    if (ancienne < 2) {
        db.execSQL("ALTER TABLE " + TABLE_EVENTS + " ADD COLUMN DATE TEXT");
        db.execSQL("ALTER TABLE " + TABLE_EVENTS + " ADD COLUMN ADDRESS TEXT");
    }
}
```

`ALTER TABLE ... ADD COLUMN` garde les lignes existantes ; leurs nouvelles colonnes valent `NULL`.
C'est le même SQL qu'en cours de bases de données (TD10).

### 5.3 Bonus personnel (non demandé)

Une petite carte dans `EventActivity`, centrée sur l'événement : tu réutilises tout ce que tu as
écrit en partie 2. Très visuel pour les captures du rendu.

---

## 6. Tester sur l'émulateur

| Problème                                                              | Cause                                                | Solution                                                                                         |
| ---------------------------------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| « Geocodeur indisponible »                                           | image système sans services Google                  | Device Manager > crée un appareil avec une image **Google APIs** ou **Google Play** |
| Adresse introuvable                                                    | pas d'internet dans l'émulateur                     | ouvre Chrome dans l'émulateur pour vérifier ; redémarre l'émulateur (**Cold Boot**)    |
| Carte grise                                                            | pas d'internet, ou pas de `setUserAgentValue`      | voir 2.4                                                                                         |
| La position ne vient jamais                                            | l'émulateur n'a pas de GPS réel                    | **⋯ > Location > Set location** (à refaire après chaque redémarrage)                   |
| Position en Californie                                                 | position par défaut de l'émulateur (Mountain View) | envoie une position à Cergy                                                                     |
| Plantage à l'ouverture de l'écran d'un événement créé à la main | virgule dans LAT/LNG                                 | `Locale.US` (4.3) ; supprime l'événement fautif en désinstallant l'appli                    |
| `SecurityException` sur `requestLocationUpdates`                   | permission pas encore accordée                      | n'appelle `demarrerGps()` qu'après `aLaPermission()`                                        |

**Logcat** : filtre sur `package:mine`, et ajoute des `Log.d(TAG, ...)` dans `placer` et `save`
pour voir passer chaque position et chaque insertion.

---

## 7. Rendre

Sur le modèle de ton `TP2_rendu_GANDONOU` :

- `README.md` (+ PDF) : ce qui marche, partie par partie du sujet, les choix (une seule activité
  pour carte + formulaire, `finish()` et la pile, `Locale.US`, les deux versions du géocodeur), et
  ce qui ne marche pas s'il y a quelque chose.
- Captures : liste avec le bouton d'ajout ; écran d'un événement **avec son adresse** ; carte
  avec l'épingle ; fenêtre de permission ; formulaire rempli ; liste avec le **16ᵉ** événement ;
  son écran avec son adresse.
- L'APK : **Build > Build App Bundle(s) / APK(s) > Build APK(s)**, dans
  `app\build\outputs\apk\debug\`.

---

## 8. Questions de compréhension (réponds avant de lire)

1. Pourquoi une seule activité pour la carte, le GPS et le formulaire ?
2. Pourquoi ne peut-on pas appeler `geocodeur.getFromLocation(lat, lng, 1)` directement dans
   `onCreate` ?
3. Pourquoi `registerForActivityResult` est-il appelé en attribut, et pas au moment du clic ?
4. Pourquoi le bouton ENREGISTRER est-il désactivé au départ ?
5. Que se passe-t-il si on oublie `gestionnaire.removeUpdates(ecouteur)` dans `onPause` ?
6. Pourquoi le nouvel événement apparaît-il dans la liste sans qu'on rappelle `afficher()` ?

**Réponses**

1. La position GPS est déjà dans l'activité : la passer à un 2ᵉ écran demanderait des extras, et
   chaque écran de plus complique la pile (bonus 5.1). Un seul écran : l'utilisateur voit où il
   est **pendant** qu'il remplit le formulaire.
2. C'est un accès réseau **bloquant** : sur le thread principal, l'écran gèle, et Android peut
   afficher « L'application ne répond pas ». D'où le thread à part (ou le callback en API 33+).
3. Android peut détruire et recréer l'activité (rotation, mémoire) pendant que la fenêtre de
   permission est ouverte. L'enregistrement doit exister **dès la création** de l'activité, pour
   que la réponse retrouve son destinataire. Android l'impose : l'appeler après `onStart` lève une
   exception.
4. Sans position, il n'y a pas de LAT/LNG à enregistrer. Le bouton désactivé empêche un
   événement sans coordonnées, sans même avoir à écrire de message d'erreur.
5. Le GPS continue à tourner écran éteint ou application en arrière-plan : la batterie se vide,
   et `placer` est appelée sur une activité qui n'est plus visible.
6. `finish()` ramène à `ThirdActivity`, dont `onResume()` est rappelée ; or ton `onResume` appelle
   `afficher()`, qui relit la base.

---

## 9. Les trous corrigés (après avoir essayé)

**Trou 1** (`EventActivity.onCreate`)

```java
chercherAdresse(Double.parseDouble(lat), Double.parseDouble(lng));
```

**Trou 2** (appel bloquant)

```java
resultats = geocodeur.getFromLocation(lat, lng, 1);
```

**Trou 3** (`montrer`)

```java
adresse.setText(resultats.get(0).getAddressLine(0));
```

**Trou 4** (`ThirdActivity`, clic)

```java
intent.putExtra(EventActivity.EXTRA_NAME, e.name);
intent.putExtra(EventActivity.EXTRA_LAT, e.lat);
intent.putExtra(EventActivity.EXTRA_LNG, e.lng);
intent.putExtra(EventActivity.EXTRA_TYPE, e.type);
```

**Trou 5** (l'épingle)

```java
epingle = new Marker(carte);
epingle.setPosition(CERGY);
epingle.setAnchor(Marker.ANCHOR_CENTER, Marker.ANCHOR_BOTTOM);   // la pointe sur le point exact
epingle.setTitle("CY Cergy Paris Universite");
carte.getOverlays().add(epingle);
```

**Trou 6** (`aLaPermission`)

```java
return ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION)
            == PackageManager.PERMISSION_GRANTED
        || ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_COARSE_LOCATION)
            == PackageManager.PERMISSION_GRANTED;
```

**Trou 7** (`demarrerGps`)

```java
gestionnaire.requestLocationUpdates(LocationManager.GPS_PROVIDER, 2000, 5, ecouteur);
```

**Trou 8** (`ajouter`)

```java
ligne.put(NAME, e.name);
ligne.put(LAT, e.lat);
ligne.put(LNG, e.lng);
ligne.put(TYPE, e.type);
```

**Trou 9** (`save`)

```java
EventDbHelper db = new EventDbHelper(this);
long id = db.ajouter(new Event(0, nom, lat, lng, type));
db.close();
Log.d(TAG, "evenement ajoute, ID " + id);
finish();
```

Les imports à ajouter dans `AddEventActivity` (Studio les propose avec **Alt+Entrée**) :
`android.Manifest`, `android.annotation.SuppressLint`, `android.content.pm.PackageManager`,
`android.location.Location`, `android.location.LocationListener`,
`android.location.LocationManager`, `android.util.Log`, `android.view.View`,
`android.widget.Button`, `android.widget.EditText`, `android.widget.Spinner`, `android.widget.TextView`,
`android.widget.Toast`, `androidx.activity.result.ActivityResultLauncher`,
`androidx.activity.result.contract.ActivityResultContracts`, `androidx.annotation.NonNull`,
`androidx.core.content.ContextCompat`, `java.util.Locale`.
Attention à `Manifest` : prends **`android.Manifest`**, pas une classe `Manifest` de ton paquet.

---

## 10. Finaliser (état de ton projet le 6 novembre à 12 h 53)

### 10.1 Où tu en es

J'ai relu ton projet `C:\Users\User\AndroidStudioProjects\TP3Maps` et je l'ai compilé
(`assembleDebug`) : **aucune erreur**, l'APK `app-debug.apk` est produit. Partie par partie :

| Partie du sujet | Où | État |
|---|---|---|
| 1. Coordonnées vers adresse | `EventActivity.java`, `activity_event.xml` | fait : Geocoder, les deux versions (Android 13+ et avant) |
| Ouvrir l'écran d'un événement | `ThirdActivity.java` (clic sur la liste) | fait : les 4 extras sont envoyés |
| 2.1 Carte OSM + épingle | `AddEventActivity.java`, `activity_add_event.xml` | fait : `Configuration.load` avant `setContentView`, `onResume`/`onPause` de la carte |
| 2.2 Position GPS | `AddEventActivity.java` | fait : permission à l'exécution, listener à 4 méthodes, `removeUpdates` dans `onPause` |
| 2.3 Nom, type, enregistrement | `activity_add_event.xml`, `EventDbHelper.ajouter`, `save` | fait : `Locale.US`, bouton grisé tant qu'il n'y a pas de position |
| Bonus pile d'activités | `save` et `previous` appellent `finish()` | fait dans le code, **reste à l'expliquer** dans le README |
| Bonus champs en plus | | pas fait (facultatif) |
| Rendu | `README.md` | **encore celui du TP2**, à réécrire |

Il reste donc : une retouche dans le manifeste (10.2), le test complet sur le téléphone avec
les captures (10.3), le README (10.4) et le dossier de rendu (10.5).

### 10.2 La retouche du manifeste

Dans `app > manifests > AndroidManifest.xml`, tu as `INTERNET` et les deux permissions de
localisation, mais **pas `ACCESS_NETWORK_STATE`**. Ajoute cette ligne juste sous celle
d'`INTERNET` :

```xml
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

Pourquoi : osmdroid télécharge les **tuiles** (les petites images carrées de la carte) depuis les
serveurs d'OpenStreetMap et vérifie d'abord que le réseau est disponible. Sans cette permission,
la carte marche souvent quand même, mais la documentation d'osmdroid la demande : avec, tu es
tranquille. C'est une permission « normale » : aucune fenêtre ne s'affiche, la déclarer suffit.

Pendant que tu y es : dans `activity_event.xml`, ton `tools:text="Coordonnees : 49.0387, 2.O782"`
contient la **lettre O** au lieu du chiffre 0 dans `2.O782`. Ça ne change rien sur le téléphone
(`tools:text` n'apparaît que dans l'aperçu de Studio), mais corrige-le : un correcteur qui ouvre
le layout le verra.

Ce qui **n'est pas** une erreur, pour que tu saches l'expliquer : après que tu as accepté la
permission, `demarrerGps()` est appelée deux fois (par la réponse à la permission, puis par
`onResume`). Ce n'est pas grave : `requestLocationUpdates` avec le **même** listener remplace
l'abonnement précédent au lieu d'en créer un second.

**Point de contrôle 10.2** : **Build > Make Project** (Ctrl+F9), aucune erreur.

### 10.3 Le test complet, avec les captures

Branche ton Samsung (comme au TP2), choisis-le dans la liste des appareils en haut de Studio,
puis **Run** (triangle vert, ou Maj+F10). Active la **localisation** du téléphone et
**Internet**. Comme l'`applicationId` est `com.cyu.tp3maps`, c'est une application **neuve**,
installée à côté du TP2 : sa base est vide, elle retélécharge les 15 événements.

Fais le parcours dans cet ordre et prends une capture (bouton marche + volume bas) aux étapes
qui en demandent une. Renomme-les comme indiqué : ce sont les noms que le README utilisera.

| # | Action | Ce que tu dois voir | Capture |
|---|---|---|---|
| 1 | Remplis le formulaire, OK, puis NEXT | la liste se remplit : « 15 evenements » | `01_list_add_button.jpg` (bouton AJOUTER visible) |
| 2 | Touche un événement de la liste | nom, type, coordonnées, puis « Recherche de l'adresse... » remplacé par **une adresse** | `02_event_address.jpg` |
| 3 | PREVIOUS | retour à la liste (pas au formulaire) | |
| 4 | AJOUTER | la fenêtre de permission de localisation | `03_permission.jpg` |
| 5 | Accepte (« Lorsque vous utilisez l'appli ») | la carte, l'épingle qui va **sur ta position**, « Position : 49.03.., 2.0.. » | `04_map_pin.jpg` |
| 6 | Touche l'épingle | la bulle « Vous etes ici » | |
| 7 | Écris un nom, choisis un type | bouton ENREGISTRER actif | `05_form_filled.jpg` |
| 8 | ENREGISTRER | retour à la liste : « 16 evenements », le tien en dernier | `06_list_16.jpg` |
| 9 | Touche ton événement | **ton adresse** (celle où tu étais) | `07_new_event_address.jpg` |
| 10 | Appuie sur **retour** autant de fois que possible | liste, puis second écran, puis on quitte. **Jamais** la carte | |
| 11 | AJOUTER, nom vide, ENREGISTRER | message d'erreur rouge sur le champ, rien n'est ajouté | |

Si une étape ne donne pas le résultat attendu, regarde le tableau de la partie 6 (problèmes
fréquents) et **Logcat** filtré sur `package:mine`. Si ça ne suffit pas, envoie-moi une capture
de l'écran et de Logcat.

Le résultat de l'étape 10 est la preuve du **bonus de la pile d'activités** : note-le pour le
README.

### 10.4 Le README du TP3

Ton `README.md` actuel est celui du TP2. Garde la même forme (en anglais, comme au TP2), et
remplace le contenu. Voici le plan, avec **ce que chaque partie doit dire** ; écris les phrases
toi-même, avec ce que tu as vu pendant le test.

```markdown
# TP3: Geocoding, Maps and Location

Patrick-léon GANDONOU, L3 Informatique, CY Cergy Paris Université
Mobile Computing, TP3

## Overview
(3 lignes : le projet TP3Maps part du TP2 ; même paquet com.cyu.tp1intents ;
applicationId com.cyu.tp3maps pour l'installer à côté du TP2 ; minSdk 24, targetSdk 37 ;
testé sur quel téléphone, quelle version d'Android.)

## 1. From coordinates to an address
(EventActivity : ce qu'elle reçoit (4 extras), ce qu'elle affiche.
Le Geocoder et ses DEUX branches : Android 13+ avec le callback, avant avec un Thread.
Pourquoi pas directement sur le thread principal. Le cas Geocoder.isPresent() == false.
Un extrait : le if/else de chercherAdresse.)

## 2. Adding an event
### 2.1 OpenStreetMap
(osmdroid 6.1.20 ; Configuration.load et setUserAgentValue AVANT setContentView, et pourquoi ;
la carte suit onResume / onPause.)
### 2.2 Current location
(les permissions dans le manifeste + la demande à l'exécution ;
LocationManager, GPS sinon réseau ; getLastKnownLocation pour afficher tout de suite ;
removeUpdates dans onPause pour la batterie.)
### 2.3 Name, type and saving
(EditText + Spinner rempli par le string-array ; ENREGISTRER grisé sans position ;
la méthode ajouter ; Locale.US et pourquoi : virgule en français, Double.parseDouble plante.)

## 3. Activity stack (bonus)
(la pile à chaque étape : Main > Second > Third > AddEvent, puis finish() : Main > Second > Third.
Ce qui se passerait avec startActivity(ThirdActivity) à la place. Le résultat du test retour.)

## Files
(tableau fichier / rôle, comme au TP2, avec EventActivity, AddEventActivity,
activity_event.xml, activity_add_event.xml en plus.)

## Notes
(les limites : bouton grisé si la permission est refusée, le Geocoder a besoin d'Internet, etc.)

## Screenshots
(les 7 captures en deux tableaux, comme au TP2.)
```

Pour les phrases sur le Geocoder, le GPS et `Locale.US`, tu as la matière dans les parties 1.3,
3 et 4.3 de ce guide et dans tes réponses aux questions de la partie 8 : reformule avec tes mots.

### 10.5 Le dossier de rendu

Même forme que `TP2_rendu_GANDONOU` :

```
TP3_rendu_GANDONOU\
    README.md
    README.pdf
    TP3Maps.apk
    screenshots\
        01_list_add_button.jpg ... 07_new_event_address.jpg
```

1. **L'APK** : après la retouche 10.2, dans Studio, **Build > Build App Bundle(s) / APK(s) >
   Build APK(s)**. Une bulle en bas à droite propose **locate** : elle ouvre
   `app\build\outputs\apk\debug\`. Copie `app-debug.apk` dans le dossier de rendu et renomme-le
   `TP3Maps.apk`.
2. **Les captures** : du téléphone vers `screenshots\` (câble USB ou Google Photos), renommées.
3. **Le README** : écris-le dans le dossier de rendu. Quand il est fini, envoie-le-moi : je
   génère `README.pdf` comme pour le TP2.
4. **Le zip** : clic droit sur `TP3_rendu_GANDONOU` > **Compresser vers > Fichier ZIP**.

Avant d'envoyer, ouvre le zip et vérifie : 4 éléments, et les images s'affichent dans le README.
