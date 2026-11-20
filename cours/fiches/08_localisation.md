# 08. La localisation et les cartes

> Source : cours 6 (*Location and Maps*). Corrigé : `10_corriges.md`, partie 08.
> **Le chapitre qui rapporte le plus :** annale 1, ex. 4 (**6 points** : géocodage inverse,
> `onLocationChanged`) et annale 2, Q3 (**8 points** : accès au service, suivi GPS,
> enregistrement en base, permissions).

---

## 1. Comment un téléphone sait où il est

| Technique | Principe | Précision | Avantages / limites |
|---|---|---|---|
| **GPS** | le récepteur capte des **satellites** et calcule sa position par **trilatération** (distance à plusieurs satellites) | **la meilleure** (quelques mètres) | lent au démarrage, **consomme beaucoup**, mal en intérieur |
| **Réseau** (antennes et Wi-Fi) | distance aux **antennes relais** estimée par le temps aller-retour du signal (triangulation), et réseaux Wi-Fi connus | moyenne (dizaines à centaines de mètres) | rapide, peu gourmand, marche en intérieur |

**Latitude et longitude** (en degrés décimaux) :
- **latitude** : de **+90** (pôle Nord) à **-90** (pôle Sud). 0 = équateur.
- **longitude** : de **+180** (Est) à **-180** (Ouest). 0 = méridien de Greenwich.

Cergy : environ **49,04° N** et **2,07° E**, soit `49.04, 2.07`.

**Les trois formats d'écriture** (60 secondes = 1 minute, 60 minutes = 1 degré) :

| Format | Exemple |
|---|---|
| degrés, minutes, secondes | 32° 18' 23.1" N |
| degrés, minutes décimales | 32° 18.385' N |
| degrés décimaux | 32.30642° N, soit **+32.30642** |

Conversion : 32° 18' 23.1" = 32 + 18/60 + 23.1/3600 = 32,30642°. Sud et Ouest deviennent
**négatifs**.

---

## 2. Les classes de la localisation

| Classe | Rôle |
|---|---|
| **`LocationManager`** | le **service système** de localisation : position actuelle, suivi des déplacements, alertes de proximité, liste des fournisseurs |
| **`LocationProvider`** | un **fournisseur** = une technologie de localisation. Constantes : `LocationManager.GPS_PROVIDER`, `LocationManager.NETWORK_PROVIDER` |
| **`Criteria`** | pour choisir un fournisseur selon des critères (précision, énergie, coût) |
| **`Location`** | **une position** à un instant : latitude, longitude, heure UTC, et si disponibles altitude, vitesse, cap |
| **`LocationListener`** | l'interface à implémenter pour **recevoir les nouvelles positions** |
| **`Geocoder`** | traduit **adresse ↔ coordonnées** |
| **`Address`** | une adresse renvoyée par le `Geocoder` |

**Les méthodes de `Location` :** `getLatitude()`, `getLongitude()`, `getAltitude()`,
`getSpeed()` (m/s), `getBearing()` (cap en degrés), `getAccuracy()` (rayon d'incertitude
en m), `getTime()`, `getProvider()`, et `distanceTo(autreLocation)` (en mètres).

---

## 3. Le schéma complet, étape par étape

C'est **le même schéma que les capteurs** (chapitre 07) : un manager, un listener, on
s'abonne, on se désabonne.

### Étape 1 : déclarer les permissions (manifeste)

```xml
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />   <!-- GPS -->
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" /> <!-- réseau -->
<uses-permission android:name="android.permission.INTERNET" />  <!-- géocodage, cartes -->
```

Ce sont des permissions **dangereuses** (sauf `INTERNET`) : depuis Android 6, il faut aussi
les **demander à l'exécution** (chapitre 03, section 5).

### Étape 2 : obtenir le service

```java
LocationManager lm = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
```

### Étape 3 : écrire le listener (4 méthodes)

```java
LocationListener ecouteur = new LocationListener() {
    @Override
    public void onLocationChanged(Location location) {          // nouvelle position
        double lat = location.getLatitude();
        double lng = location.getLongitude();
    }
    @Override
    public void onProviderDisabled(String provider) { }         // GPS coupé par l'utilisateur
    @Override
    public void onProviderEnabled(String provider) { }          // GPS rallumé
    @Override
    public void onStatusChanged(String provider, int status, Bundle extras) { }  // 🕰️
};
```

### Étape 4 : demander les mises à jour

```java
lm.requestLocationUpdates(LocationManager.GPS_PROVIDER,   // quel fournisseur
                          60000,                          // minTime : en MILLISECONDES
                          1000,                           // minDistance : en MÈTRES
                          ecouteur);                      // qui prévenir
```

> **LE piège des unités, qui tombe à l'annale 2 (Q3b) :** `minTime` est en
> **millisecondes** et `minDistance` en **mètres**. « Une minute et un kilomètre » s'écrit
> donc **`60000` et `1000`**, pas `1` et `1`.

**Ce que veulent dire ces deux nombres :** le système ne te préviendra **pas plus souvent
que toutes les `minTime` ms**, et **pas pour un déplacement de moins de `minDistance` m**.
Plus ils sont grands, moins le GPS travaille, plus la batterie dure.

### Étape 5 : arrêter

```java
lm.removeUpdates(ecouteur);
```

Dans une activité : s'abonner dans **`onResume`**, se désabonner dans **`onPause`**, comme
les capteurs. Pour suivre la position **même écran fermé**, on le fait dans un
**Service** (c'est l'exemple 1 du cours 6, voir section 6).

### Et la dernière position connue (sans attendre)

```java
Location derniere = lm.getLastKnownLocation(LocationManager.GPS_PROVIDER);
if (derniere != null) { ... }   // peut être null : aucune position encore connue
```

**Pourquoi le GPS n'est pas instantané :** la puce GPS n'est pas un appareil qui répond
tout de suite à « donne-moi ma position ». Le premier calcul peut prendre plusieurs
secondes, voire minutes. D'où le fonctionnement par **listener** (on est prévenu quand ça
arrive) plutôt que par appel direct.

---

## 4. Qui appelle `onLocationChanged`, et quand ? (annale 1, ex. 4.2b)

- **Qui :** **le système**, via le service de localisation (le `LocationManager`). Ni
  l'utilisateur, ni l'*Activity Manager*, ni ton propre code : tu ne l'appelles **jamais**
  toi-même.
- **Quand :** chaque fois qu'une **nouvelle position** est disponible, **après** qu'un
  listener a été enregistré avec `requestLocationUpdates`, et **dans le respect des seuils**
  `minTime` et `minDistance`.
- C'est le principe du **callback** : tu fournis la méthode, le système l'appelle.

---

## 5. Choisir un fournisseur avec des critères

```java
Criteria c = new Criteria();
c.setAccuracy(Criteria.ACCURACY_COARSE);     // une précision grossière suffit
c.setPowerRequirement(Criteria.POWER_LOW);   // économiser la batterie
c.setAltitudeRequired(false);
c.setSpeedRequired(false);
c.setCostAllowed(true);
String meilleur = lm.getBestProvider(c, true);   // true = seulement les fournisseurs activés

List<String> tous = lm.getProviders(true);       // tous les fournisseurs activés
```

---

## 6. L'architecture du cours : le GPS dans un service

Le cours 6 (exemple 1) montre l'architecture complète, qui réutilise les chapitres 06 et
03 :

```
MainActivity                                   MyGpsService
  │ startService(intent) ──────────────────────► onStartCommand()
  │                                               └─ lance un Thread :
  │                                                    Looper.prepare();
  │                                                    lm.requestLocationUpdates(GPS, 10000, 50, listener);
  │                                                    Looper.loop();
  │                                              listener.onLocationChanged(loc) :
  │                                                 Intent i = new Intent("cs495.action.GPS_LOCATION");
  │ ◄──────────── sendBroadcast(i) ──────────────   i.putExtra("latitude", ...);
  │ receiver.onReceive() : affiche lat / lng
```

**Pourquoi un `Looper` :** `requestLocationUpdates` a besoin d'une **boucle de messages**
pour livrer les positions au listener. Le thread principal en a une ; un thread créé à la
main n'en a pas, d'où `Looper.prepare()` puis `Looper.loop()`.

---

## 7. Le géocodage : adresse ↔ coordonnées

**Deux sens :**

| Nom | Entrée → Sortie | Méthode |
|---|---|---|
| **Géocodage direct** (*forward geocoding*) | adresse → latitude, longitude | `getFromLocationName(String adresse, int maxResultats)` |
| **Géocodage inverse** (*reverse geocoding*) | latitude, longitude → adresse | `getFromLocation(double lat, double lng, int maxResultats)` |

**Les points à savoir :**
- La recherche se fait **sur un serveur** : il faut la permission **`INTERNET`** et une
  connexion.
- Les deux méthodes renvoient une **`List<Address>`** (plusieurs réponses possibles,
  limitées par `maxResultats`), qui peut être **vide**.
- Elles peuvent lever une **`IOException`** (pas de réseau, serveur indisponible) : on les
  entoure d'un `try / catch`.
- **Le niveau de détail varie** selon le lieu et les données du serveur : en ville on peut
  avoir le numéro et la rue ; en pleine campagne ou en mer, seulement la ville, la région ou
  le pays, voire rien. *(Annale 1, ex. 4.1d.)*
- Elles sont **lentes** (réseau) : dans une vraie appli, hors du thread principal.
- `Geocoder.isPresent()` dit si le service de géocodage existe sur le téléphone.

**Exemple : géocodage direct** (le sens inverse est l'exercice 8.4 de l'annale) :

```java
public Location adresseVersPosition(String adresse) {
    Geocoder geocoder = new Geocoder(this, Locale.getDefault());
    try {
        List<Address> resultats = geocoder.getFromLocationName(adresse, 1);
        if (resultats != null && !resultats.isEmpty()) {
            Address a = resultats.get(0);                 // le premier résultat
            Location loc = new Location("geocoder");
            loc.setLatitude(a.getLatitude());
            loc.setLongitude(a.getLongitude());
            return loc;
        }
    } catch (IOException e) {
        Log.e("Geo", "Géocodage impossible", e);
    }
    return null;                                          // rien trouvé
}
```

**Les champs d'un objet `Address`** (annale 1, ex. 4.1c : « donnez-en quatre ») :

| Méthode | Contenu | Exemple |
|---|---|---|
| `getAddressLine(0)` | la ligne d'adresse complète | « 33 Bd du Port, 95000 Cergy, France » |
| `getSubThoroughfare()` | le numéro | « 33 » |
| `getThoroughfare()` | la rue | « Boulevard du Port » |
| `getLocality()` | la ville | « Cergy » |
| `getPostalCode()` | le code postal | « 95000 » |
| `getSubAdminArea()` | le département | « Val-d'Oise » |
| `getAdminArea()` | la région | « Île-de-France » |
| `getCountryName()` / `getCountryCode()` | le pays / son code | « France » / « FR » |
| `getFeatureName()` | le nom du lieu | « CY Cergy Paris Université » |
| `getLatitude()` / `getLongitude()` | les coordonnées | 49.03, 2.07 |
| `getPhone()`, `getUrl()` | téléphone, site (rarement remplis) | |

---

## 8. Les cartes

### 8.1 Dans le cours (ancienne API, 🕰️ supprimée depuis 2013)

| Classe | Rôle |
|---|---|
| `MapView` | la vue qui affiche la carte (un `ViewGroup`) |
| `MapActivity` | l'activité **obligatoire** pour contenir une `MapView` ; elle impose `isRouteDisplayed()` |
| `MapController` | déplacer et zoomer : `setCenter(point)`, `setZoom(n)`, `animateTo(point)` |
| `GeoPoint` | une position, en **micro-degrés entiers** : `new GeoPoint((int)(lat * 1E6), (int)(lng * 1E6))` |
| `Overlay` | une couche de dessin par-dessus la carte : `draw(...)`, `onTap(...)` |
| `MyLocationOverlay` | une couche toute faite : la position actuelle (point bleu) et la boussole |
| `ItemizedOverlay` + `OverlayItem` | une couche de **marqueurs** (titre + description) |
| `Projection` | convertit `GeoPoint` (lat/lng) ↔ `Point` (pixels à l'écran) : `toPixels`, `fromPixels` |

Il fallait déclarer `<uses-library android:name="com.google.android.maps" />`, la
permission `INTERNET`, et une **clé d'API** dans le layout (`android:apiKey`).

Réglages d'affichage : `setSatellite(true)`, `setTraffic(true)`,
`setBuiltInZoomControls(true)`. Zoom de 1 (le plus loin) à 21 (le plus près).

### 8.2 Aujourd'hui (pour le projet)

**Google Maps SDK** : un `SupportMapFragment` dans le layout, `getMapAsync(callback)`, puis
dans `onMapReady(GoogleMap map)` : `map.addMarker(new MarkerOptions().position(new
LatLng(49.04, 2.07)).title("Cergy"))` et `map.moveCamera(CameraUpdateFactory.newLatLngZoom(...))`.
Pour la position, Google recommande `FusedLocationProviderClient`, qui mélange GPS, réseau
et capteurs pour économiser la batterie.

---

## 9. À toi (sur papier, fichier fermé)

**Exercice 8.1 :** GPS ou réseau ? Donne deux avantages et deux inconvénients de chacun.

**Exercice 8.2 :** Convertis 48° 51' 24" N, 2° 21' 7" E en degrés décimaux. Puis écris
40° 26' 46" S, 79° 58' 56" O en degrés décimaux signés.

**Exercice 8.3 (annale 2, Q3, 8 points) :** On veut une appli qui surveille la position de
l'appareil et enregistre chaque nouvelle position dans une base. Explique, avec des bouts
de code, comment :
- a. accéder au service de localisation du système ;
- b. surveiller les changements de position avec le **GPS**, avec un intervalle minimum de
  **1 minute** et une distance minimum de **1 kilomètre** entre deux mises à jour ;
- c. ajouter les nouvelles coordonnées à la table `locations(lat VARCHAR(25), lng
  VARCHAR(25))` d'une base SQLite existante ;
- d. t'assurer que l'appli sera autorisée à faire tout cela.

**Exercice 8.4 (annale 1, ex. 4, 6 points) :**
1. a. Écris une méthode `locationToAddress` qui prend un objet `Location` et renvoie la
   **première** adresse correspondante (s'il y en a plusieurs).
   b. Quel est le nom du **processus** que représente cette méthode ?
   c. Donne quatre champs qu'on peut obtenir d'un objet `Address`.
   d. Obtient-on toujours le même niveau de détail dans les résultats de ce processus ?
2. a. Implémente la méthode `onLocationChanged` d'une classe `GPSListener`, qui affiche un
   Toast avec la nouvelle position à chaque changement.
   b. Quand cette méthode est-elle appelée, et par qui (le système, l'utilisateur,
   l'*Activity Manager*...) ?

**Exercice 8.5 :** Ce code plante, et une fois ce premier problème corrigé, il ne fait
toujours pas ce qu'on veut. Trouve les deux erreurs et explique ce qui se passe pour
chacune.

```java
LocationManager lm = (LocationManager) getSystemService(Context.SENSOR_SERVICE);
lm.requestLocationUpdates(LocationManager.GPS_PROVIDER, 5, 10, ecouteur);
// le but : une mise à jour toutes les 5 minutes, ou tous les 10 km
```

**Exercice 8.6 :** Écris une activité qui affiche dans deux `TextView` (`lat` et `lng`) la
position, mise à jour toutes les 10 secondes ou tous les 20 mètres avec le fournisseur
réseau, et qui arrête la localisation quand l'utilisateur quitte l'écran. Permission(s) ?

**Exercice 8.7 :** Dans l'ancienne API des cartes, pourquoi écrit-on
`new GeoPoint((int)(lat * 1E6), (int)(lng * 1E6))` ?
