# 03. Les Intents, le manifeste et les permissions

> Sources : cours 2 (Intents), cours 4 (manifeste des services), cours 6 (permissions de
> localisation). Corrigé : `10_corriges.md`, partie 03.
> Questions d'examen liées : **annale 1, ex. 1.3** (permission d'envoyer des SMS),
> **annale 2, Q2b et Q3d** (permissions à déclarer).

---

## 1. L'Intent : un message, pas un appel

Un **Intent** est un petit objet **passif** qui décrit une demande : « démarre cet écran »,
« affiche cette page web », « compose ce numéro ». Le créer ne fait **rien**. Il faut le
**remettre au système** avec l'une de ces trois méthodes :

| Méthode | Démarre quoi |
|---|---|
| `startActivity(intent)` | une **Activity** |
| `startService(intent)` | un **Service** |
| `sendBroadcast(intent)` | tous les **BroadcastReceivers** intéressés |

**Ce qu'il y a dans un Intent :**

| Champ | Sens | Exemple |
|---|---|---|
| **Composant** | la classe précise à lancer. S'il est rempli, l'Intent est **explicite** | `new Intent(this, DetailActivity.class)` |
| **Action** | **ce qu'on veut faire** (une chaîne constante) | `Intent.ACTION_VIEW`, `ACTION_DIAL`, `ACTION_SEND` |
| **Data** | **sur quoi** agir : une URI (et éventuellement son type MIME) | `Uri.parse("tel:0130736000")` |
| **Catégorie** | précision sur le type de cible | `CATEGORY_LAUNCHER`, `CATEGORY_DEFAULT` |
| **Extras** | des données en plus, en paires clé/valeur | `putExtra("noteId", 42)` |
| **Flags** | consignes sur la pile d'activités | `FLAG_ACTIVITY_NEW_TASK` |

---

## 2. Explicite ou implicite

**Explicite : « démarre CETTE classe ».** On nomme la classe. C'est pour naviguer **dans
ta propre appli**. Aucune recherche, aucun risque d'échec.

```java
Intent i = new Intent(this, DetailActivity.class);
startActivity(i);
```

**Implicite : « que quelqu'un AFFICHE ceci ».** On décrit **le travail**, et le système
cherche une appli capable de le faire. C'est pour utiliser **les autres applis**
(navigateur, téléphone, cartes, mail).

```java
Intent i = new Intent(Intent.ACTION_VIEW, Uri.parse("https://cyu.fr"));
startActivity(i);   // le navigateur ? lequel ? le système décide
```

**Pourquoi c'est malin :** ton appli ne sait pas quel navigateur ou quelle appli de cartes
est installé, et n'a pas besoin de le savoir. C'est un **couplage faible** imposé par le
système.

**Les actions courantes :**

| Action | Data | Résultat | Permission ? |
|---|---|---|---|
| `ACTION_VIEW` | `https://...` | ouvre le navigateur | non |
| `ACTION_VIEW` | `geo:48.85,2.35` | ouvre une carte à ce point | non |
| `ACTION_DIAL` | `tel:0130736000` | ouvre le **clavier** avec le numéro, sans appeler | **non** |
| `ACTION_CALL` | `tel:0130736000` | **passe l'appel** directement | **oui** : `CALL_PHONE` |
| `ACTION_SENDTO` | `smsto:0612345678` ou `mailto:...` | ouvre l'appli SMS ou mail | non |
| `ACTION_SEND` | type `text/plain` + `EXTRA_TEXT` | menu de partage | non |
| `ACTION_MAIN` | (avec `CATEGORY_LAUNCHER`) | point d'entrée affiché dans le lanceur | non |

**Toujours se protéger** : un Intent implicite peut ne trouver **aucune** appli.

```java
try {
    startActivity(i);
} catch (ActivityNotFoundException e) {
    Toast.makeText(this, "Aucune appli pour ouvrir ça", Toast.LENGTH_SHORT).show();
}
```

---

## 3. Les filtres d'Intent : comment une appli dit « je sais faire ça »

Une appli **annonce** ce qu'elle sait faire avec un `<intent-filter>` dans son manifeste.
Pour un Intent implicite, le système teste **chaque filtre** de chaque appli. Un filtre
convient s'il passe **les trois tests** :

1. **Action** : le filtre liste l'action de l'Intent.
2. **Catégorie** : le filtre liste **toutes** les catégories de l'Intent. Le système ajoute
   `CATEGORY_DEFAULT` à tout Intent implicite : **un filtre qui veut recevoir des Intents
   implicites doit donc déclarer `DEFAULT`**.
3. **Data** : le schéma (`geo`, `https`, `tel`...), l'hôte, le chemin et le type MIME
   correspondent.

Résultat : **un** filtre convient → l'appli s'ouvre ; **plusieurs** → l'utilisateur choisit
(sélecteur) ; **aucun** → `ActivityNotFoundException`.

```xml
<activity android:name=".CarteActivity" android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <data android:scheme="geo" />
    </intent-filter>
</activity>
```

**L'icône dans le lanceur :** une activité apparaît dans la liste des applis **si et
seulement si** elle a un filtre avec l'action `MAIN` et la catégorie `LAUNCHER`.

---

## 4. Le manifeste : le contrat avec le système

Tout composant doit y être déclaré. **La structure, à savoir écrire de mémoire :**

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="fr.cyu.monappli">

    <!-- 1. LES PERMISSIONS : enfants de <manifest>, AVANT et HORS de <application> -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />

    <application
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name">

        <!-- 2. L'ÉCRAN DE DÉMARRAGE (icône dans le lanceur) -->
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- 3. LES AUTRES COMPOSANTS -->
        <activity android:name=".DetailActivity" />
        <service  android:name=".MonService" />
        <receiver android:name=".MonReceiver" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
            </intent-filter>
        </receiver>
        <provider android:name=".MonProvider"
                  android:authorities="fr.cyu.monappli.provider" />
    </application>
</manifest>
```

**Les 4 balises de composants :** `<activity>`, `<service>`, `<receiver>`, `<provider>`.
Une par composant, toutes **à l'intérieur** de `<application>`.

**`android:name=".MainActivity"`** : le point veut dire « dans le package de l'appli ».

**`android:exported`** : obligatoire (depuis Android 12) sur tout composant qui a un
filtre. `true` si **une autre appli** a le droit de le lancer.

---

## 5. Les permissions

**Pourquoi :** chaque appli vit dans son bac à sable. Pour toucher à quelque chose de
sensible (position, SMS, contacts, appareil photo, Internet), elle doit le **déclarer**
dans le manifeste. L'utilisateur sait ainsi ce que l'appli peut faire.

**Où :** `<uses-permission android:name="android.permission.XXX" />`, enfant direct de
`<manifest>`, en dehors de `<application>`.

**Le tableau à connaître** (toutes les permissions qui apparaissent dans les cours et les
annales) :

| Pour... | Permission | Chapitre |
|---|---|---|
| accéder à Internet (et donc au géocodage, aux cartes) | `INTERNET` | 08 |
| position **précise** (GPS) | `ACCESS_FINE_LOCATION` | 08 |
| position **approximative** (réseau, antennes) | `ACCESS_COARSE_LOCATION` | 08 |
| **envoyer** des SMS | `SEND_SMS` | ici |
| recevoir / lire des SMS | `RECEIVE_SMS` / `READ_SMS` | |
| passer un appel directement | `CALL_PHONE` | ici |
| connaître l'état du téléphone (appel entrant...) | `READ_PHONE_STATE` | 06 |
| lire le numéro de l'appelant (Android 10+) | `READ_CALL_LOG` | 06 |
| lire les contacts | `READ_CONTACTS` | 05 |
| écrire sur le stockage externe (carte SD) | `WRITE_EXTERNAL_STORAGE` | 05 |
| être prévenu de la fin du démarrage | `RECEIVE_BOOT_COMPLETED` | 06 |
| faire vibrer | `VIBRATE` | 07 |
| garder le processeur éveillé | `WAKE_LOCK` | 06 |
| caméra | `CAMERA` | |
| afficher des notifications (Android 13+) | `POST_NOTIFICATIONS` | |

**Deux familles :**

| | Permissions **normales** | Permissions **dangereuses** |
|---|---|---|
| Exemples | `INTERNET`, `VIBRATE`, `WAKE_LOCK`, `RECEIVE_BOOT_COMPLETED` | localisation, SMS, contacts, appels, caméra, micro |
| Accordées | **automatiquement** à l'installation | l'utilisateur doit **accepter une fenêtre**, à l'exécution |
| Ce qu'il faut écrire | la ligne du manifeste suffit | la ligne du manifeste **ET** une demande dans le code |

**Depuis Android 6 (API 23)**, une permission dangereuse se demande **à l'exécution** :

```java
private static final int CODE_PERM_SMS = 1;

// 1. Vérifier si on l'a déjà
if (ContextCompat.checkSelfPermission(this, Manifest.permission.SEND_SMS)
        != PackageManager.PERMISSION_GRANTED) {
    // 2. Sinon, la demander : le système affiche une fenêtre à l'utilisateur
    ActivityCompat.requestPermissions(this,
            new String[]{ Manifest.permission.SEND_SMS }, CODE_PERM_SMS);
} else {
    envoyerSms();
}

// 3. Recevoir la réponse de l'utilisateur
@Override
public void onRequestPermissionsResult(int requestCode, String[] permissions,
                                       int[] grantResults) {
    super.onRequestPermissionsResult(requestCode, permissions, grantResults);
    if (requestCode == CODE_PERM_SMS && grantResults.length > 0
            && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
        envoyerSms();
    }
}
```

> **À l'examen :** quand on te demande « assurez-vous que l'application sera autorisée »,
> écris **les lignes du manifeste**, puis ajoute la **demande à l'exécution** pour les
> permissions dangereuses. Les deux ensemble, c'est la réponse complète.

---

## 6. Exemple complet : envoyer un SMS (annale 1, ex. 1.3)

« Créez la partie nécessaire pour enregistrer la capacité de votre appli à envoyer des
SMS. » La partie attendue est **dans le manifeste** :

```xml
<manifest ...>
    <uses-permission android:name="android.permission.SEND_SMS" />
    <application ...> ... </application>
</manifest>
```

Pour aller plus loin (et montrer que tu as compris), le code qui s'en sert :

```java
SmsManager sms = SmsManager.getDefault();
sms.sendTextMessage("0612345678", null, "Bonjour", null, null);
//                  destinataire  centre SMS  texte   accusé envoi  accusé réception
```

**L'alternative sans permission :** passer par l'appli SMS de l'utilisateur avec un Intent
implicite. C'est lui qui appuie sur « Envoyer », donc aucune permission n'est nécessaire :

```java
Intent i = new Intent(Intent.ACTION_SENDTO, Uri.parse("smsto:0612345678"));
i.putExtra("sms_body", "Bonjour");
startActivity(i);
```

Même logique pour `ACTION_DIAL` (sans permission) contre `ACTION_CALL` (avec `CALL_PHONE`).

---

## 7. À toi (sur papier, fichier fermé)

**Exercice 3.1 :** Explicite ou implicite ? Écris l'Intent dans chaque cas.
1. Ouvrir ton écran `ParametresActivity`.
2. Ouvrir la page `https://www.cyu.fr` dans le navigateur.
3. Ouvrir le clavier du téléphone avec le numéro du secrétariat (01 34 25 10 10), sans
   appeler.
4. Ouvrir une carte centrée sur Cergy (latitude 49.0389, longitude 2.0749).
5. Ouvrir l'appli SMS avec le message « J'arrive » pour le 06 12 34 56 78.

**Exercice 3.2 :** Pour chacune des 5 actions de l'exercice 3.1, faut-il une permission ?
Laquelle ?

**Exercice 3.3 :** Écris le manifeste **complet** d'une appli `fr.cyu.suivi` qui :
- a un écran de démarrage `MainActivity` et un second écran `HistoriqueActivity` ;
- a un service `SuiviService` ;
- a un receiver `DemarrageReceiver` qui doit être prévenu quand le téléphone a fini de
  démarrer ;
- utilise le GPS, Internet, et fait vibrer le téléphone.

**Exercice 3.4 :** Une appli veut passer un appel directement au 112 quand on appuie sur un
bouton. Écris la ligne du manifeste, le code de la vérification et de la demande de
permission, puis l'Intent.

**Exercice 3.5 :** Pourquoi la ligne du manifeste ne suffit-elle plus, depuis Android 6,
pour `ACCESS_FINE_LOCATION`, alors qu'elle suffit pour `INTERNET` ?

**Exercice 3.6 :** `startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("geo:48.86,2.33")))`
plante sur le téléphone d'un camarade. Quelle est la cause la plus probable, quelle
exception voit-on, et comment protéger le code ?

**Exercice 3.7 :** Ton activité `LecteurActivity` doit apparaître dans le sélecteur quand
une autre appli veut ouvrir un lien `https://notes.cyu.fr/...`. Écris son filtre d'Intent.
Quelle catégorie ne faut-il surtout pas oublier, et pourquoi ?
