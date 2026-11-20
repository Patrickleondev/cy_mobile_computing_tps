# 01. Les bases : ce qu'est une application Android

> Sources : cours 1 (introduction) et début du cours 2. Corrigé des exercices :
> `10_corriges.md`, partie 01.

---

## 1. Pourquoi le mobile est un domaine à part

Un téléphone n'est pas un petit ordinateur. Quatre contraintes changent la façon de
programmer, et presque tout le cours en découle :

| Contrainte | Ce qu'elle impose au programmeur | Où tu la retrouves |
|---|---|---|
| **L'énergie** : la batterie est le vrai mur | ne rien laisser tourner pour rien (capteurs, GPS) | ch. 07 et 08 : *désenregistrer* les listeners |
| **Le réseau** est variable, payant, parfois absent | stocker en local, synchroniser quand c'est possible | ch. 05 : SQLite |
| **Le système peut tuer ton appli** (appel, mémoire pleine, rotation) | sauver l'état, réagir aux callbacks | ch. 02 : cycle de vie |
| **Le contexte** : position, mouvement, proximité | les capteurs, la localisation | ch. 07 et 08 |

**La différence la plus importante avec le Java que tu connais :**

| | Programme Java classique | Application Android |
|---|---|---|
| Qui contrôle le programme ? | toi : `main()` tourne jusqu'à la fin | **le système** : il crée, met en pause, arrête et tue tes composants |
| Point d'entrée | `public static void main` | **il n'y a pas de `main`** : le système appelle tes méthodes (`onCreate`...) |
| Interface | construite en code (Swing) | décrite en **XML**, transformée en objets par le système |
| Tâches longues | on peut bloquer, ça attend | **interdit** de bloquer le thread principal : l'appli est déclarée « ne répond pas » (ANR) après 5 s |

On appelle ça **l'inversion de contrôle** : tu n'appelles pas le système, c'est lui qui
t'appelle. Tu ne fais jamais `new MainActivity()`.

---

## 2. Android en quelques faits (questions de cours fréquentes)

- Android est développé par **Google** et l'**Open Handset Alliance** (2007). Première
  version en 2008, sur le HTC Dream.
- Android est **basé sur le noyau Linux**. *(Vrai/faux de l'annale 2.)*
- La version open source s'appelle **AOSP** (Android Open Source Project).
- Le code tourne sur **ART** (Android Runtime), qui a remplacé la machine virtuelle
  **Dalvik** en 2014 (Android 5). Il n'y a pas de JVM sur le téléphone.
- Chaque version d'Android a un numéro entier, le **niveau d'API** (Android 17 = API 37).
- Langages : **Java** (celui du cours) ou **Kotlin** (préféré par Google depuis 2019).
- Outil : **Android Studio**. L'émulateur s'appelle un **AVD**, pour **Android Virtual
  Device**. *(Question de l'annale 2.)*
- Outil en ligne de commande : **adb** (Android Debug Bridge). Le journal du téléphone
  s'appelle **Logcat**.

---

## 3. La pile logicielle Android (à savoir dessiner)

Du bas vers le haut. Ton code est tout en haut et ne parle qu'à la couche juste en dessous.

```
┌─────────────────────────────────────────────────────────────┐
│ 5. Applications : les tiennes ET celles du système          │  ← tu écris ici
│    (Téléphone, Contacts, Appareil photo : mêmes règles)     │
├─────────────────────────────────────────────────────────────┤
│ 4. Framework Java (API Android) + bibliothèques Jetpack     │
│    ActivityManager, WindowManager, PackageManager,          │
│    LocationManager, SensorManager, TelephonyManager,        │
│    NotificationManager, Content Providers, Views            │
├─────────────────────────────────────────────────────────────┤
│ 3. ART (Android Runtime)  +  bibliothèques natives C/C++    │
│    (SQLite, OpenGL, WebKit/WebView, média, libc)            │
├─────────────────────────────────────────────────────────────┤
│ 2. HAL : couche d'abstraction matérielle                    │
│    (interface standard pour caméra, capteurs, audio...)     │
├─────────────────────────────────────────────────────────────┤
│ 1. Noyau Linux                                              │
│    processus, mémoire, pilotes, sécurité, énergie, Binder   │
└─────────────────────────────────────────────────────────────┘
```

**Pourquoi c'est utile pour l'examen :** quand on te demande « quel *manager* », la réponse
est dans la couche 4. Tous les services du système s'obtiennent de la même façon :

```java
LocationManager lm = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
SensorManager   sm = (SensorManager)   getSystemService(Context.SENSOR_SERVICE);
TelephonyManager tm = (TelephonyManager) getSystemService(Context.TELEPHONY_SERVICE);
```

> **À savoir écrire par cœur :** `(XxxManager) getSystemService(Context.XXX_SERVICE)`.
> C'est la porte d'entrée de la moitié des questions de code de l'examen.

**Le bac à sable (sandbox) :** chaque application a son propre **utilisateur Linux (UID)**
et son propre **processus**. Ses fichiers sont privés. Pour toucher à quelque chose de
sensible (position, contacts, SMS), elle doit avoir une **permission**. Pour parler à une
autre application, elle passe par le système, avec un **Intent**.

---

## 4. Les briques d'une application

Une application Android est faite de **4 types de composants**, reliés par des **Intents**
et déclarés dans **un manifeste**.

| Composant | Ce que c'est | Image mentale | Chapitre |
|---|---|---|---|
| **Activity** | **un écran**, avec une interface et un cycle de vie | une page | 02 |
| **Service** | un travail **sans interface**, qui continue même quand l'écran change | un moteur en coulisse | 06 |
| **BroadcastReceiver** | réagit à un **événement du système** (démarrage terminé, batterie faible, SMS reçu) | une boîte aux lettres | 06 |
| **ContentProvider** | **partage des données** avec les autres applications, derrière une adresse `content://` | un guichet | 05 |

Et la colle entre eux :

- **Intent** : le **message** qui démarre un composant (« ouvre cet écran », « affiche cette
  page web », « la batterie est faible »). Les composants ne se connaissent pas entre eux :
  ils envoient des Intents et le système fait le lien. *(Chapitre 03.)*
- **AndroidManifest.xml** : le **contrat avec le système**. Tout composant doit y être
  déclaré, sinon **il n'existe pas** (erreur `ActivityNotFoundException`). C'est aussi là
  qu'on demande les permissions. *(Chapitre 03.)*

**Une notion qui tombe : le `Context`.** C'est l'objet qui donne accès au système
(ressources, services, démarrer une activité, ouvrir un fichier...). La classe `Activity`
**hérite de** `Context` (de même que `Service`). C'est pour ça qu'on peut écrire
`getSystemService(...)` ou `new Intent(this, ...)` directement dans une activité : `this`
est un `Context`. *(Vrai/faux de l'annale 2 : « Activity est une sous-classe de Context »
→ **vrai**.)*

```
Context
  └─ ContextWrapper
       ├─ Service
       └─ ContextThemeWrapper
            └─ Activity
                 └─ ... └─ AppCompatActivity
                              └─ MainActivity (la tienne)
```

---

## 5. Un projet Android : les fichiers qui comptent

```
app/src/main/
├── AndroidManifest.xml          le contrat : composants, permissions, icône
├── java/fr/cyu/monappli/
│   └── MainActivity.java        une classe Java par écran
└── res/                         les RESSOURCES (tout ce qui n'est pas du code)
    ├── layout/activity_main.xml l'interface de l'écran
    ├── values/strings.xml       tous les textes (traduisibles)
    ├── values/colors.xml, themes.xml
    ├── drawable/                images
    └── mipmap-*/                icônes de l'appli
app/build.gradle.kts             minSdk, targetSdk, dépendances
```

**La classe `R` :** à la compilation, chaque ressource reçoit un numéro, rangé dans une
classe générée appelée `R`. On n'écrit jamais `R` à la main.

| Ressource | En Java | En XML |
|---|---|---|
| le layout `activity_main.xml` | `R.layout.activity_main` | `@layout/activity_main` |
| le texte `app_name` | `R.string.app_name` | `@string/app_name` |
| une vue avec `android:id="@+id/nom"` | `R.id.nom` | `@id/nom` |

Le `+` de `@+id/nom` veut dire « **crée** cet identifiant ». Sans `+`, on **fait référence**
à un identifiant qui existe déjà. *(Tu en auras besoin pour lire les RelativeLayout du
chapitre 04.)*

**Les qualificateurs de dossier :** `values-fr/` (textes en français), `layout-land/`
(paysage), `values-night/` (mode sombre). Le système choisit tout seul le bon dossier. On
n'écrit jamais `if (estEnFrancais)`.

**Les trois niveaux d'API du projet :**

| Réglage | Sens |
|---|---|
| `minSdk` | la plus vieille version d'Android sur laquelle l'appli s'installe |
| `targetSdk` | la version pour laquelle l'appli a été testée (le système applique ses règles) |
| `compileSdk` | la version des API utilisées pour compiler (toujours la plus récente) |

---

## 6. Le Hello World, ligne par ligne

```java
public class MainActivity extends AppCompatActivity {          // (1)
    @Override
    protected void onCreate(Bundle savedInstanceState) {        // (2)
        super.onCreate(savedInstanceState);                     // (3)
        setContentView(R.layout.activity_main);                 // (4)
        TextView t = (TextView) findViewById(R.id.greeting);    // (5)
        t.setText("Bonjour");                                   // (6)
        Log.d("MainActivity", "onCreate appelé");               // (7)
    }
}
```

1. Un écran = une classe qui **hérite d'`Activity`** (ici `AppCompatActivity`, sa version
   moderne).
2. `onCreate` est appelée **par le système** quand il crée l'écran. C'est l'équivalent le
   plus proche d'un `main`.
3. **Toujours** appeler `super.onCreate(...)` en premier.
4. `setContentView` **gonfle** (*inflate*) le XML : il transforme le fichier en objets Java
   (`TextView`, `Button`...) et les affiche.
5. `findViewById` **retrouve une vue grâce à son identifiant**. *(Question de l'annale 2 :
   « quelle méthode pour retrouver une View à partir de son id ? » → `findViewById`.)*
   Le cast `(TextView)` est obligatoire dans le style du cours.
6. On agit sur la vue.
7. `Log.d(tag, message)` écrit dans **Logcat**, l'outil de débogage n°1.

**Piège :** appeler `findViewById` **avant** `setContentView` renvoie `null`, car l'arbre
des vues n'existe pas encore. Résultat : `NullPointerException`.

**Du code à l'appli :** `.java` → `javac` → `.class` → **D8** → `.dex` (bytecode Android) →
emballé avec les ressources et le manifeste dans un **APK** signé → installé et exécuté par
**ART**. Pour le Play Store, on envoie un **AAB** (Android App Bundle), à partir duquel
Google génère des APK adaptés à chaque téléphone.

---

## 7. À toi (sur papier, fichier fermé)

**Exercice 1.1 :** Vrai ou faux ? Justifie en une ligne.
1. Android est basé sur le noyau Linux.
2. Une application Android commence par une méthode `main`.
3. La classe `Activity` hérite de la classe `Context`.
4. Deux applications installées peuvent lire librement les fichiers l'une de l'autre.
5. Un composant non déclaré dans le manifeste peut quand même être lancé avec un Intent
   explicite.
6. Dalvik est la machine virtuelle actuelle d'Android.

**Exercice 1.2 :** Que veulent dire **AVD**, **ADB**, **AOSP**, **ART**, **APK** ?

**Exercice 1.3 :** Cite les 4 types de composants d'une application Android et donne pour
chacun un exemple concret d'utilisation dans une appli de livraison de repas.

**Exercice 1.4 :** Dessine de mémoire la pile Android en 5 couches et place dedans :
`SQLite`, `LocationManager`, les pilotes Wi-Fi, ton `MainActivity`, ART.

**Exercice 1.5 :** Écris la ligne qui récupère le `SensorManager`, puis celle qui récupère
le `TelephonyManager`.

**Exercice 1.6 :** Ce code plante. Pourquoi ?

```java
protected void onCreate(Bundle b) {
    super.onCreate(b);
    Button ok = (Button) findViewById(R.id.ok);
    ok.setText("Valider");
    setContentView(R.layout.activity_main);
}
```

**Exercice 1.7 :** Dans un layout, quelle est la différence entre `android:id="@+id/nom"`
et `android:layout_below="@id/nom"` ?
