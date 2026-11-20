# Campus Explorer pas à pas : comment l'application est construite, et pourquoi

Pour Patrick et Asma. Le code complet est sur GitHub : `https://github.com/Asma-bey/campus-Explorer`
(copie locale : `D:\All\Licence_Cergy\Semestre_5\07_Mineure_Mobile_Computing\CampusExplorer\campus-Explorer`).

Ce guide suit l'ordre de construction, qui est aussi l'ordre des 5 commits. Pour chaque étape :
**ce qui est fait**, **où**, **pourquoi ce choix**, et **comment le vérifier**. Les extraits de code
importants sont recopiés ici, pour lire le guide sans ouvrir Android Studio (dans le train, par
exemple). À la fin : les questions qu'un enseignant peut poser à l'oral, avec les réponses.

Plan : **0.** ouvrir et lancer le projet. **1.** le projet Gradle. **2.** le système visuel de la
maquette. **3.** les données. **4.** les trois écrans et la navigation. **5.** la carte Leaflet dans
une WebView. **6.** la position et les permissions. **7.** le service de suivi. **8.** ce qui a été
testé. **9.** les questions de l'oral. **10.** ce qu'il reste à faire, et qui fait quoi.

---

## 0. Ouvrir et lancer le projet

1. **Asma** : le dépôt est le sien. Dans Android Studio, **File > New > Project from Version
   Control**, URL `https://github.com/Asma-bey/campus-Explorer.git`.
   **Patrick** : le projet est déjà cloné dans le dossier ci-dessus ; **File > Open** et choisis le
   dossier `campus-Explorer`.
2. Laisse Gradle se synchroniser (barre de progression en bas). La première fois, il télécharge
   Gradle 9.2.1 et le plugin Android 9.0.1.
3. **Run** (triangle vert). Sur l'émulateur, mets une position à Cergy : **⋯ > Location**, cherche
   « Cergy », **Set location**. Sans ça, l'émulateur te place en Californie (siège de Google).

Pour simuler une marche pendant un suivi : change la position plusieurs fois dans **⋯ > Location**,
quelques rues plus loin à chaque fois.

---

## 1. Le projet Gradle (commit 1)

**Fichiers** : `settings.gradle.kts`, `build.gradle.kts`, `app/build.gradle.kts`,
`gradle/libs.versions.toml`.

| Réglage | Valeur | Pourquoi |
|---|---|---|
| `minSdk` | 26 (Android 8.0) | c'est la version qui impose les **canaux de notification** et les **services au premier plan** : en partant de 26, le code n'a pas besoin de cas spéciaux pour les versions plus anciennes |
| `targetSdk` / `compileSdk` | 36 | la version installée chez Asma (son TP3 utilise 36) |
| plugin Android (AGP) | 9.0.1 | la version d'Asma : un Android Studio récent ouvre un projet plus ancien, l'inverse est refusé |
| `applicationId` | `fr.cyu.campusexplorer` | un identifiant à nous, ni `com.example` ni celui d'un TP |

Trois bibliothèques seulement :

```kotlin
dependencies {
    implementation(libs.appcompat)   // AppCompatActivity, compatibilite
    implementation(libs.material)    // theme MaterialComponents
    implementation(libs.webkit)      // WebViewAssetLoader (etape 5)
}
```

**Pourquoi si peu ?** La déclaration du projet dit « XML layouts and standard Android Views ». Pas
de Jetpack Compose, pas de Google Maps, pas de bibliothèque de carte Android : la carte est une page
web (étape 5).

Le dossier `design/` garde le prototype Figma Make (code React et fichier `.make`), pour montrer d'où
vient chaque écran. La vidéo de 40 Mo reste en local, elle alourdirait le dépôt.

---

## 2. Le système visuel de la maquette (commit 2)

**Le principe** : avant d'écrire un seul écran, on traduit la maquette en ressources Android. Chaque
écran réutilise ensuite ces ressources : la fidélité vient de là.

### 2.1 Les couleurs : `res/values/colors.xml`

Copiées des variables CSS du prototype (`design/figma-make-prototype/src/index.css`) :

```xml
<color name="yellow">#FFE500</color>
<color name="black">#090909</color>
<color name="cyan">#50C6E5</color>
<color name="green">#69B72E</color>
```

Plus une trentaine de nuances (fonds pastel des pastilles, gris des bordures, vert du bandeau
« suivi en cours ») relevées une par une dans le CSS.

### 2.2 La police : Inter, dans `res/font`

La maquette utilise Inter. Les fichiers `.ttf` (Regular, Medium, SemiBold, Bold, ExtraBold) sont
**dans l'appli**, pas téléchargés : ça marche hors connexion. Licence libre OFL, copiée dans
`assets/INTER_LICENSE.txt`.

Chaque graisse a son fichier, et on choisit le fichier dans la vue :

```xml
android:fontFamily="@font/inter_bold"
```

**Le piège rencontré** : au premier lancement, tout le texte était en Regular. La cause : le thème
contenait aussi `<item name="fontFamily">` (l'attribut d'AppCompat, sans `android:`). Un attribut du
thème sert de valeur par défaut à toutes les vues, et AppCompat fait passer `fontFamily` **avant**
le `android:fontFamily` de chaque vue. On a gardé seulement `android:fontFamily` dans le thème.

### 2.3 Les tailles de texte

Le prototype est dessiné petit (des textes de 7 à 9 px). Sur un vrai téléphone, c'est illisible :
Android recommande au moins 11sp. Les tailles sont donc environ **1,3 fois** celles de la maquette,
en gardant les proportions (le grand titre reste 4 fois plus grand que le texte courant).

`sp` pour le texte, `dp` pour le reste : les deux s'adaptent à la densité de l'écran, et `sp` suit
en plus la taille de texte choisie par l'utilisateur dans les réglages.

### 2.4 Les icônes : `res/drawable/ic_*.xml`

Les 16 icônes du prototype sont des chemins SVG (`<path d="...">`). Un **vector drawable** Android
accepte presque la même syntaxe, dans `android:pathData`. Elles ont été converties telles quelles,
avec le même trait (1,8) et les bouts arrondis :

```xml
<path
    android:pathData="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"
    android:strokeColor="#FF000000"
    android:strokeWidth="1.8"
    android:strokeLineCap="round"
    android:strokeLineJoin="round" />
```

Seule différence : les `<circle>` SVG n'existent pas en vector drawable ; on les écrit comme deux
demi-arcs (`a r,r 0 1,0 2r,0`).

La couleur se règle avec `app:tint` sur l'`ImageView` : une seule icône sert en noir, en blanc ou en
gris.

### 2.5 Les formes : `res/drawable/bg_*.xml`

Chaque arrondi de la maquette devient une `<shape>`. Exemple, le bouton noir de l'accueil, avec son
« ombre » cyan décalée de 5 px (`box-shadow: 5px 5px 0`) : deux rectangles superposés dans un
`layer-list`.

```xml
<layer-list>
    <item android:left="5dp" android:top="5dp">      <!-- l'ombre cyan, decalee -->
        <shape><solid android:color="@color/shadow_cyan" /><corners android:radius="5dp" /></shape>
    </item>
    <item android:right="5dp" android:bottom="5dp">  <!-- le bouton noir -->
        <shape><solid android:color="@color/black" /><corners android:radius="5dp" /></shape>
    </item>
</layer-list>
```

**Économie** : plutôt qu'une forme par couleur, des formes blanches (`bg_round5`, `bg_oval`...)
recolorées avec `android:backgroundTint`. Les filtres de la carte, eux, utilisent un `selector` :
noir quand `state_checked`, blanc bordé sinon.

**Comment vérifier** : ouvre `activity_main.xml` en mode **Split** ; l'aperçu doit ressembler à la
maquette avant même de lancer l'appli.

---

## 3. Les données (commit 3)

### 3.1 Les lieux : `data/Place.java` et `data/Places.java`

La déclaration dit : « predefined places stored in the application ». Pas de base distante, pas de
compte : une liste Java.

```java
new Place(1, "Bibliothèque universitaire", Place.Category.LIBRARY, "Bibliothèque",
        "Un espace dédié au travail, à la lecture et à l'étude.",
        "La bibliothèque universitaire des Cerclades, place des Cerclades, ...",
        49.0372263, 2.0808313),
```

**D'où viennent les coordonnées ?** La maquette n'en a pas (sa carte est un dessin). Elles ont été
cherchées dans OpenStreetMap (services Nominatim et Overpass) le 6 novembre 2026 : bibliothèque des
Cerclades, restaurant universitaire du 5 avenue du Parc, site des Chênes, Maison des étudiants du
boulevard du Port. Les 4 premiers lieux sont ceux de la maquette ; 3 autres complètent la carte
(sites Saint-Martin et Bernard Hirsch, résidence Crous). Pour en ajouter un : sur openstreetmap.org,
clic droit sur le lieu, **Afficher l'adresse**, et les coordonnées s'affichent à gauche.

La catégorie est un `enum` qui porte aussi l'icône et les couleurs : un seul endroit à changer.

### 3.2 Les lieux enregistrés : `data/SavedPlaces.java` (SharedPreferences)

Quelques entiers ne justifient pas une base de données. Comme le nom et l'email au TP2, ils vont
dans les `SharedPreferences`, sous forme d'une chaîne `"3,1,4"`.

**Pourquoi une chaîne et pas `putStringSet` ?** Un `Set` ne garde pas l'ordre : la liste
« Mes lieux » changerait d'ordre au hasard. La chaîne garde l'ordre d'ajout.

### 3.3 L'historique des parcours : `data/SessionDb.java` (SQLite)

Même construction que `EventDbHelper` au TP2 : un `SQLiteOpenHelper`, une table.

```sql
CREATE TABLE SESSIONS (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                       START_TIME INTEGER NOT NULL,   -- millisecondes depuis 1970
                       DURATION_S INTEGER NOT NULL,
                       DISTANCE_M REAL NOT NULL)
```

**Pourquoi SQLite ici et SharedPreferences pour les lieux ?** L'historique grandit sans limite et se
lit trié (`ORDER BY START_TIME DESC LIMIT 5`) : c'est le travail d'une base. On ne garde que le
résumé (début, durée, distance), pas les positions : moins de données personnelles, comme le promet
la section « Privacy » de la déclaration.

---

## 4. Les trois écrans et la navigation (commit 3)

### 4.1 Une classe commune : `BaseActivity.java`

Les trois Activities héritent de `BaseActivity`, qui fait trois choses.

**1. Le journal du cycle de vie.** Chaque callback écrit dans Logcat :

```java
@Override
protected void onResume() {
    super.onResume();
    Log.d(LIFECYCLE, getClass().getSimpleName() + ".onResume");
}
```

Dans Logcat, filtre `tag:Lifecycle` : tu vois `MapActivity.onPause`, puis `MapActivity.onStop`, etc.
C'est la preuve demandée par la déclaration (« onCreate, onResume, onPause and onStop are
implemented and tested »).

**2. La barre du bas.** Elle est dans `view_bottom_nav.xml`, incluse par les trois écrans avec
`<include>`. `setupBottomNav(Tab.MAP)` marque l'onglet actif avec `setSelected(true)` ; grâce à
`android:duplicateParentState`, l'icône, le texte et le trait jaune passent tous à l'état
« sélectionné », et leurs `selector` changent de couleur tout seuls.

**3. Les marges du système.** Avec `targetSdk` 35 et plus, Android 15 dessine l'appli **sous** la
barre d'état et la barre de navigation. On décale le contenu :

```java
ViewCompat.setOnApplyWindowInsetsListener(root, (v, insets) -> {
    Insets bars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
    v.setPadding(bars.left, bars.top, bars.right, 0);   // en haut : la racine
    bottomNav.setPadding(0, 0, 0, bars.bottom);         // en bas : la barre de l'appli
    return insets;
});
```

La couleur de fond de la racine remplit la zone de la barre d'état : jaune sur l'accueil, blanc
ailleurs. C'est ce qui donne la barre d'état jaune de la maquette.

### 4.2 La navigation : Intents explicites et pile d'activités

```java
protected void openTab(Class<? extends BaseActivity> target) {
    Intent intent = new Intent(this, target);
    intent.addFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);
    startActivity(intent);
    noTransition();
}
```

**Pourquoi `FLAG_ACTIVITY_REORDER_TO_FRONT` ?** Sans lui, chaque clic sur un onglet crée une
nouvelle Activity. Après Accueil, Carte, Accueil, Carte, la pile contiendrait 4 écrans, et le bouton
retour les repasserait tous. Avec le drapeau, si l'écran existe déjà, il est **ramené devant** au
lieu d'être recréé : chaque écran existe une seule fois. C'est le même problème que le bonus « pile
d'activités » du TP3.

**Pourquoi `noTransition()` ?** Dans la maquette, les onglets changent sans glissement.
`overridePendingTransition(0, 0)` supprime l'animation.

### 4.3 L'identifiant du lieu en extra

La déclaration : « the identifier of a selected place is passed as an Intent extra ». Depuis
l'accueil (« À découvrir ») ou l'écran Enregistrés (« Voir sur la carte ») :

```java
Intent intent = new Intent(this, MapActivity.class);
intent.addFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);
intent.putExtra(MapActivity.EXTRA_PLACE_ID, place.id);
startActivity(intent);
```

Côté carte, deux cas :

- la carte n'existe pas encore : l'extra se lit dans `onCreate` (`getIntent()`) ;
- la carte existe déjà (elle est ramenée devant) : `onCreate` n'est **pas** rappelé. Le nouvel
  Intent arrive dans `onNewIntent`.

```java
@Override
protected void onNewIntent(@NonNull Intent intent) {
    super.onNewIntent(intent);
    setIntent(intent);
    handleIntent(intent);   // lit EXTRA_PLACE_ID et ouvre la fiche
}
```

Après lecture, l'extra est retiré (`intent.removeExtra`) : sinon, chaque retour sur la carte
rouvrirait la fiche que l'utilisateur a fermée.

### 4.4 Les écrans

| Écran | Layout | Ce qui est construit en Java |
|---|---|---|
| Accueil | `activity_main.xml` | les 4 cartes de catégories (`item_category.xml`) et les 3 lieux « À découvrir » (`item_discovery.xml`), gonflés en boucle depuis la liste des lieux |
| Carte | `activity_map.xml` | tout le comportement (étapes 5 à 7) |
| Enregistrés | `activity_saved.xml` | la liste des lieux (`item_saved_place.xml`) et des parcours (`item_session.xml`), **relue dans `onResume`** |

**Pourquoi gonfler les cartes en Java plutôt que les écrire 4 fois en XML ?** Le texte, l'icône et
la couleur viennent des données : une seule source, pas de copie à tenir à jour.

**Pourquoi relire dans `onResume` et pas dans `onCreate` ?** Enregistrés est ramené devant (pas
recréé) quand on y revient. Un lieu enregistré entre-temps sur la carte n'apparaîtrait pas si la
liste n'était lue qu'une fois.

### 4.5 Français ou anglais selon la langue du téléphone

**Le principe** : on n'écrit aucun texte dans le code ni dans les layouts, seulement des noms de
ressources (`@string/home_title`, `R.string.place1_name`). Le texte lui-même est dans deux dossiers :

| Dossier | Langue | Utilisé quand |
|---|---|---|
| `res/values/` | anglais | le téléphone est dans **n'importe quelle** langue autre que le français |
| `res/values-fr/` | français | le téléphone est en français (France, Belgique, Canada...) |

Android choisit le dossier tout seul au démarrage de chaque écran. **Pourquoi l'anglais par
défaut ?** Le dossier sans suffixe sert aussi de secours : un téléphone en espagnol ou en arabe
tombe sur `values/`, et l'anglais lui est plus utile que le français.

Chaque fichier existe dans les deux dossiers, avec **les mêmes noms** :

```xml
<!-- res/values/strings.xml -->
<string name="home_title">Explore your\ncampus</string>
<!-- res/values-fr/strings.xml -->
<string name="home_title">Explorez votre\ncampus</string>
```

Le lint d'Android Studio vérifie qu'aucune clé ne manque dans une langue (erreur
`MissingTranslation`). Les textes identiques partout (`CY`, `+`, `%1$.2f km`) sont marqués
`translatable="false"` et restent seulement dans `values/`.

**Les lieux** : au début, leurs noms étaient des `String` en dur dans `Places.java`, donc toujours en
français. Ils sont passés dans `places.xml` (un par langue), et `Place` garde des identifiants :

```java
@StringRes public final int name;     // R.string.place1_name, pas "Bibliothèque universitaire"
...
((TextView) findViewById(R.id.sheet_name)).setText(place.name);   // setText(int) traduit
String nom = getString(place.name);                               // pour la recherche et la carte
```

**Les formats** suivent aussi la langue, sans code de sélection :

| | Français | Anglais |
|---|---|---|
| date d'un parcours (`DateFormat.getDateTimeInstance`) | 6 novembre 2026 17:53 | November 6, 2026 5:53 PM |
| distance (`getString(R.string.tracking_km, km)`) | 0,66 km | 0.66 km |

Seule exception : les coordonnées envoyées au JavaScript gardent `Locale.US`, car `49,03` (avec une
virgule) casserait l'appel `CampusMap.showUser(49,03, 2,07)`.

**Sur Android 13+**, `res/xml/locales_config.xml` (déclaré dans le manifeste) ajoute l'appli dans
**Paramètres > Applis > CY Campus Explorer > Langue** : on choisit la langue de l'appli seule, sans
toucher à celle du téléphone. Pratique pour montrer les deux langues à l'oral en quelques secondes.

**Comment vérifier** : sur l'émulateur, **Settings > System > Languages**, ajoute Français et
mets-le en premier ; relance l'appli. Ou, plus rapide, le réglage de langue par appli ci-dessus.

### 4.6 Les dialogues

Les dialogues de la maquette (« Votre position », « Arrêter le suivi ? ») utilisent un seul layout,
`dialog_confirm.xml`, affiché par `Dialogs.confirm(...)` dans un `AlertDialog` à fond transparent
(sinon le fond blanc carré d'Android cacherait nos coins arrondis).

---

## 5. La carte : Leaflet dans une WebView (commit 4)

### 5.1 Le principe

La déclaration impose « OpenStreetMap tiles displayed using Leaflet.js in a WebView ». Leaflet est
une bibliothèque **JavaScript** de cartes. On écrit donc une petite page web,
`app/src/main/assets/map/index.html`, et une `WebView` (un mini-navigateur) l'affiche dans
`activity_map.xml`. Tout le reste de l'écran (recherche, filtres, boutons, fiche) est en vues
Android **posées par-dessus** la WebView, dans un `FrameLayout` : dans un `FrameLayout`, la vue
écrite en dernier est au-dessus.

Leaflet est **dans l'appli** (`assets/map/leaflet/`), pas chargé depuis Internet : la page s'ouvre
même hors connexion, et rien ne dépend d'un serveur extérieur à part les tuiles.

### 5.2 Le WebViewAssetLoader : le piège du 403

```java
WebViewAssetLoader assetLoader = new WebViewAssetLoader.Builder()
        .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
        .build();
...
webView.loadUrl("https://appassets.androidplatform.net/assets/map/index.html");
```

**Pourquoi pas `file:///android_asset/map/index.html`, plus simple ?** Une page en `file://` n'a pas
d'origine web, donc pas d'en-tête « Referer » dans ses requêtes. Les serveurs de tuiles
d'OpenStreetMap refusent ces requêtes : la carte n'affiche que des cases « Access blocked » (erreur
403), exactement ce qui est arrivé à Asma au TP3 avec osmdroid. Le `WebViewAssetLoader` sert les
mêmes fichiers sous une vraie adresse `https://` : les requêtes de tuiles ont un Referer et passent.

La politique d'OpenStreetMap demande aussi d'identifier l'application :

```java
settings.setUserAgentString(settings.getUserAgentString()
        + " CampusExplorer/1.0 (projet etudiant CY Cergy)");
```

### 5.3 Java et JavaScript se parlent dans les deux sens

**Java vers JavaScript** : `evaluateJavascript` exécute une fonction de `map.js`.

```java
private void js(String code) {
    if (mapReady) webView.evaluateJavascript(code, null);
}
...
js("CampusMap.select(" + place.id + ", true)");   // met le marqueur en avant et centre la carte
```

**JavaScript vers Java** : `addJavascriptInterface` injecte un objet Java dans la page, sous le nom
`Android`. Ses méthodes annotées `@JavascriptInterface` sont appelables depuis JavaScript :

```java
private class MapBridge {
    @JavascriptInterface
    public void onPlaceClicked(int id) {
        runOnUiThread(() -> {
            Place place = Places.byId(id);
            if (place != null) showSheet(place, false);
        });
    }
}
```

```javascript
marker.on("click", function () {
    Android.onPlaceClicked(place.id);
});
```

**Pourquoi `runOnUiThread` ?** Les méthodes `@JavascriptInterface` tournent sur un thread de la
WebView, pas sur le thread principal. Seul le thread principal a le droit de toucher aux vues (même
règle que le Geocoder au TP3).

**Pourquoi `mapReady` ?** Tant que la page n'est pas chargée, `CampusMap` n'existe pas : l'appel
échouerait. La page prévient Java avec `Android.onMapReady()` ; Java envoie alors les lieux et
l'état courant (lieu sélectionné, position, tracé).

### 5.4 La recherche, protégée

Le texte tapé part dans un appel JavaScript. Si l'utilisateur tape une apostrophe, une concaténation
naïve casserait l'appel, et un texte bien choisi pourrait exécuter du code dans la page (injection).

```java
String query = JSONObject.quote(search.getText().toString());
js("CampusMap.filter('" + currentCategory + "', " + query + ")");
```

`JSONObject.quote` entoure le texte de guillemets et échappe `'`, `"` et `\` : c'est toujours une
chaîne, jamais du code.

### 5.5 La fidélité à la maquette

- **Marqueurs** : la goutte de la maquette est un carré aux coins arrondis sauf un, tourné de -45°
  (`border-radius: 50% 50% 50% 8px; transform: rotate(-45deg)`). Elle est reprise telle quelle en
  CSS dans un `L.divIcon`. Le point d'ancrage est la pointe : au centre, plus une demi-diagonale
  (`taille × √2 / 2`).
- **Tuiles** : les tuiles OpenStreetMap sont très colorées, la carte de la maquette est sourde. Un
  filtre CSS les rapproche (`grayscale(0.6) saturate(0.85)`), sans changer de fournisseur.
- **Boutons + et -** : des vues Android rondes qui appellent `CampusMap.zoomIn()`. Le contrôle de
  zoom de Leaflet est désactivé (`zoomControl: false`).
- **Attribution** « © OpenStreetMap » en bas à droite : obligatoire pour utiliser les tuiles.

### 5.6 Hors connexion

La déclaration : « Without [internet], the application shows a message and keeps working with the
list of places. » Deux signaux :

- `ConnectivityManager` dans `onResume` : pas de réseau, le bandeau s'affiche ;
- l'événement `tileerror` de Leaflet prévient Java (`Android.onTilesError()`) si les tuiles échouent
  en cours de route.

Les marqueurs, la recherche et les fiches viennent de l'appli : ils marchent sans réseau.

---

## 6. La position et les permissions (commit 4)

### 6.1 Demander au bon moment, en expliquant

La déclaration : « Location permission is requested when the user opens a feature that needs it,
with a short explanation of why. » Donc **pas** au lancement de l'appli.

```java
private void withLocationPermission(Runnable action) {
    if (hasLocationPermission()) {
        action.run();
        return;
    }
    // d'abord le dialogue de la maquette : POURQUOI on a besoin de la position
    Dialogs.confirm(this, ..., R.string.dialog_location_title, R.string.dialog_location_text, ...,
            () -> {
                afterPermission = action;
                locationPermission.launch(new String[]{
                        Manifest.permission.ACCESS_FINE_LOCATION,
                        Manifest.permission.ACCESS_COARSE_LOCATION});
            });
}
```

La réponse d'Android arrive dans le callback de `registerForActivityResult` (même API qu'au TP3).
Trois cas :

| Réponse | Ce que fait l'appli |
|---|---|
| accordée | exécute l'action demandée (afficher la position ou démarrer le suivi) |
| refusée | message court ; la carte garde tous ses lieux |
| refusée « définitivement » (`shouldShowRequestPermissionRationale` renvoie `false`) | message qui indique les paramètres, car Android n'affichera plus sa fenêtre |

On demande les **deux** permissions : sur Android 12+, l'utilisateur peut n'accorder que la position
approximative. Le code l'accepte (`FINE` **ou** `COARSE`).

### 6.2 Le point bleu suit le cycle de vie

```java
@Override
protected void onResume() {
    super.onResume();
    ...
    if (wantsLocation() && hasLocationPermission()) startLocationUpdates();
}

@Override
protected void onPause() {
    stopLocationUpdates();   // l'ecran n'est plus visible : on coupe le GPS
    ...
    super.onPause();
}
```

**Pourquoi couper dans `onPause` ?** Un écran invisible n'a pas besoin du point bleu, et le GPS vide
la batterie. La déclaration : « The map screen manages UI-related location updates according to its
lifecycle. »

`getLastKnownLocation` affiche le point tout de suite, sans attendre le premier relevé GPS. Le choix
« afficher ma position » est retenu dans les préférences : en revenant sur la carte, le point
réapparaît sans redemander.

Si la localisation du téléphone est coupée dans les réglages (`isProviderEnabled` faux), un message
le dit ; rien ne plante.

---

## 7. Le service de suivi (commit 4)

C'est la partie « Background service » de la déclaration, la plus importante à savoir expliquer.

### 7.1 Pourquoi un service, et pourquoi « au premier plan »

Une Activity s'arrête quand l'utilisateur la quitte (`onStop`) ; Android peut la détruire. Un
parcours doit continuer **écran éteint ou dans une autre appli**. Il faut donc un `Service`, dont la
vie ne dépend pas de l'écran.

Depuis Android 8, un service en arrière-plan est arrêté par le système au bout de quelques minutes.
Un **service au premier plan** (foreground service) est autorisé à continuer, à une condition :
afficher une notification permanente. C'est aussi une garantie pour l'utilisateur : il voit toujours
que sa position est suivie.

### 7.2 Démarrer

```java
// depuis MapActivity, au clic sur "Demarrer le suivi", permission accordee
ContextCompat.startForegroundService(context, intent);
```

Dans le service, `onStartCommand` doit appeler `startForeground` **dans les 5 secondes**, sinon
Android plante l'appli :

```java
ServiceCompat.startForeground(this, NOTIFICATION_ID, buildNotification(),
        ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION);
requestUpdates();
return START_NOT_STICKY;
```

Le **type `location`** est obligatoire depuis Android 14 pour un service qui utilise la position. Il
se déclare à trois endroits :

```xml
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_LOCATION" />
...
<service
    android:name=".tracking.TrackingService"
    android:exported="false"
    android:foregroundServiceType="location" />
```

**Pourquoi `START_NOT_STICKY` ?** Si Android tue le processus, il ne relance pas le service tout
seul. La déclaration : le service « never runs when no session is active » et ne démarre que sur une
action de l'utilisateur.

**Pourquoi pas de permission « en arrière-plan » (`ACCESS_BACKGROUND_LOCATION`) ?** Elle n'est pas
nécessaire : un service au premier plan démarré pendant que l'appli est visible garde le droit
d'utiliser la position ensuite. C'est l'approche recommandée par Android, et elle évite une
deuxième demande de permission très intrusive.

### 7.3 Pendant le suivi

```java
private void onNewLocation(Location location) {
    if (location.hasAccuracy() && location.getAccuracy() > MAX_ACCURACY_M) return;  // 35 m
    double added = lastLocation == null ? 0 : lastLocation.distanceTo(location);
    lastLocation = location;
    TrackingState.addPoint(location.getLatitude(), location.getLongitude(), added);
    ...
}
```

- `distanceTo` calcule la distance réelle entre deux points GPS, en mètres.
- Les positions imprécises (plus de 35 m d'erreur) sont ignorées : sinon un point qui « saute » de
  100 m ajouterait de faux mètres à la distance.
- GPS **et** réseau : le GPS est le capteur principal (déclaration : « GPS is used as the sensor »),
  le réseau complète à l'intérieur des bâtiments où le GPS capte mal.

### 7.4 Comment l'écran suit le service

Deux mécanismes, chacun avec son rôle :

1. **`TrackingState`**, un objet statique : le service et les écrans tournent dans le même
   processus, donc ils voient le même objet. En revenant sur la carte (`onResume`), l'écran y lit
   tout de suite le chrono, la distance et le tracé complet, sans attendre la prochaine position.
2. **Une diffusion (broadcast)** à chaque nouvelle position : la carte, si elle est visible, ajoute
   le point au tracé jaune et met la distance à jour.

```java
sendBroadcast(new Intent(BROADCAST_UPDATE)
        .setPackage(getPackageName())   // diffusion reservee a notre appli
        .putExtra(EXTRA_LAT, location.getLatitude()) ...);
```

Le récepteur est enregistré dans `onResume` et retiré dans `onPause` (avec
`RECEIVER_NOT_EXPORTED` : aucune autre appli ne peut lui écrire). Même construction qu'au TP2 avec
le `DownloadService`.

Le chrono du panneau est un `Chronometer`, une vue Android qui compte toute seule à partir d'un
instant de départ : `setBase(TrackingState.startElapsed())` puis `start()`. On utilise
`SystemClock.elapsedRealtime()` et pas l'heure murale : si l'utilisateur change l'heure du téléphone
pendant le suivi, le chrono reste juste.

### 7.5 La notification

```java
new NotificationCompat.Builder(this, CHANNEL_ID)
        .setSmallIcon(R.drawable.ic_pin)
        .setContentTitle(getString(R.string.notif_title))   // "Suivi de localisation actif"
        .setContentText(getString(R.string.notif_text))
        .setSubText(distance)                              // "0,66 km"
        .setUsesChronometer(true)                          // chrono qui tourne tout seul
        .setOngoing(true)                                  // impossible a balayer
        .addAction(R.drawable.ic_close, getString(R.string.notif_stop), stopPending)
        ...
```

- **Le canal** (`NotificationChannel`) est obligatoire depuis Android 8. Importance basse : la
  notification reste visible mais ne sonne pas.
- **ARRÊTER** est un `PendingIntent` vers le service avec l'action `ACTION_STOP`.
- **Toucher la notification** ramène à la carte, avec `FLAG_ACTIVITY_REORDER_TO_FRONT` : pas de
  deuxième carte dans la pile.
- **Android 13+** : afficher une notification demande la permission `POST_NOTIFICATIONS`. Elle est
  demandée au premier « Démarrer le suivi ». Si l'utilisateur refuse, le suivi démarre quand même ;
  la notification est seulement masquée du volet (le service reste visible dans le gestionnaire
  d'activités d'Android).

### 7.6 Arrêter et libérer les ressources

```java
private void finishSession() {
    locationManager.removeUpdates(listener);                    // 1. couper le GPS
    db.insert(TrackingState.startWallClock(), seconds, meters); // 2. enregistrer le resume
    TrackingState.stop();
    sendBroadcast(...EXTRA_RUNNING, false);                     // 3. prevenir l'ecran
    ServiceCompat.stopForeground(this, ServiceCompat.STOP_FOREGROUND_REMOVE); // 4. retirer la notification
    stopSelf();                                                 // 5. detruire le service
}
```

La déclaration : « When the session ends, the service stops location updates and releases its
resources. » Chaque ligne y répond.

---

## 8. Ce qui a été testé (émulateur, Android API 37)

| Scénario | Résultat observé |
|---|---|
| Accueil, carte, enregistrés | identiques à la maquette (captures dans `docs/screenshots`) |
| Clic sur un marqueur | fiche, « Voir les détails », enregistrement (bouton jaune et message) |
| « Voir sur la carte » depuis Enregistrés | la carte vole jusqu'au lieu, fiche ouverte (`onNewIntent`) |
| « Afficher ma position » | dialogue, fenêtre d'Android, point bleu au site des Chênes, statut « Position disponible » |
| Permission refusée | message, aucun plantage, la carte garde ses lieux |
| Suivi, marche simulée de 8 points | chrono, distance, tracé jaune, notification avec ARRÊTER |
| Touche Accueil pendant le suivi | Logcat : `MapActivity.onPause`, `GPS d'interface arrete`, `MapActivity.onStop` ; le service reste au premier plan (type `location`) et la distance continue (0,47 puis 0,66 km) |
| ARRÊTER dans la notification | `Session enregistree : 123 s, 659 m`, puis `onDestroy` du service |
| Enregistrés | le parcours apparaît (2 min 03 s, 0,66 km) |
| Wi-Fi et données coupés | bandeau « Pas de connexion », marqueurs et fiches disponibles |

**À refaire sur un vrai téléphone, écran éteint**, avant la démonstration : c'est le test « tracking
while the screen is off » de la déclaration, qu'un émulateur ne reproduit qu'à moitié. Sur un
Samsung, l'optimisation de batterie peut être agressive : si le suivi s'arrête écran éteint, va dans
**Paramètres > Applis > CY Campus Explorer > Batterie > Non restreinte**.

---

## 9. Les questions de l'oral

**Pourquoi trois Activities et pas des fragments ?**
La déclaration prévoit trois Activities, et le cours porte sur les Activities, les Intents et leur
cycle de vie. Le drapeau `REORDER_TO_FRONT` règle le seul défaut de cette approche (la pile qui
grossit).

**Que se passe-t-il quand on quitte la carte pendant un suivi ?**
`MapActivity.onPause` coupe le GPS de l'écran et retire le récepteur ; `onStop` suit. Le service,
lui, a son propre cycle de vie et continue. En revenant, `onResume` relit `TrackingState` et
redessine le tracé complet.

**Pourquoi deux sources de position (la carte et le service) ?**
Elles n'ont pas la même durée de vie. Le point bleu ne sert que si l'écran est visible ; le parcours
doit continuer sans écran. Si le service gérait aussi le point bleu, le GPS tournerait en permanence
dès qu'on ouvre la carte.

**Pourquoi un service au premier plan et pas un WorkManager ?**
WorkManager sert aux tâches différables (une synchronisation « quand c'est possible »). Un parcours
demande des positions continues, maintenant, pendant que l'utilisateur marche : c'est le cas d'usage
du service au premier plan de type `location`.

**Comment la page JavaScript appelle-t-elle le Java ? Est-ce sûr ?**
Par `addJavascriptInterface` : seules les méthodes annotées `@JavascriptInterface` sont exposées. La
page est locale (servie depuis nos assets), la navigation vers d'autres pages est bloquée
(`shouldOverrideUrlLoading` renvoie `true`), et le texte de l'utilisateur passe par
`JSONObject.quote`. L'accès aux fichiers est désactivé (`setAllowFileAccess(false)`).

**Pourquoi Leaflet et pas Google Maps ?**
Choix de la déclaration : OpenStreetMap est libre, sans clé d'API ni compte. Leaflet est la
bibliothèque de référence pour l'afficher.

**Que se passe-t-il si l'utilisateur refuse la permission ?**
L'appli continue : carte, lieux, recherche, fiches et enregistrements marchent. Seuls le point bleu
et le suivi demandent la position.

**Où vont les données de position ?**
Nulle part ailleurs que sur le téléphone : un résumé (début, durée, distance) dans SQLite. Pas de
compte, pas de serveur. Les seules requêtes réseau sont les tuiles de la carte.

**Comment avez-vous respecté la maquette ?**
Couleurs copiées du CSS du prototype, même police, icônes converties depuis ses chemins SVG, mêmes
écrans et mêmes états (fiche, panneau de suivi, dialogues, état vide). Écarts assumés : textes 1,3
fois plus grands pour la lisibilité, carte réelle au lieu du dessin, vraie notification Android au
lieu du volet simulé.

---

## 10. Ce qu'il reste à faire, et qui fait quoi

1. **Tester sur un vrai téléphone, écran éteint** (section 8), et noter le résultat pour le README.
2. **Vérifier les lieux sur place** : les coordonnées viennent d'OpenStreetMap ; si l'entrée réelle
   d'un bâtiment est ailleurs, corrigez `Places.java`.
3. **Se répartir l'oral** : par exemple Asma présente les écrans, la navigation et la carte
   (sections 4 et 5), Patrick la position, le service et les tests (sections 6 à 8). Chacun doit
   pouvoir répondre à toutes les questions de la section 9.
4. **Captures et démonstration** : les captures sont dans `docs/screenshots`. Pour la démo, prévoir
   un trajet court sur le campus avec le suivi.
5. **Si vous modifiez le code** : un commit par changement, avec un message qui dit ce qui change.
   Le dépôt est celui d'Asma ; Patrick y pousse avec son compte GitHub, qui a déjà les droits
   d'écriture (le premier envoi a fonctionné).
