# Mobile Computing — TP1 pas à pas

*Activities, Intents, et la chaîne Android complète.*
Construit depuis `da24-tp1.pdf` (Dimitrios Kotzinos, CY Cergy). Vendredi 8h30–11h40, B425.

---

## 0. Ce que le TP1 te demande vraiment

Sous la liste de manipulations, il y a **trois concepts Android** et rien d'autre :

| Concept            | Ce que c'est                                                         | Où tu le vois dans le TP            |
| ------------------ | -------------------------------------------------------------------- | ------------------------------------ |
| **Activity** | un**écran** de l'application, avec son cycle de vie           | `MainActivity`, `SecondActivity` |
| **Layout**   | la**description XML** de ce que l'écran affiche               | `activity_main.xml`                |
| **Intent**   | le **message** qui lance un écran et transporte des données | `submit()`, `getIntent()`        |

Si tu retiens ces trois-là, le TP1 est fait. Le reste est de la souris.

---

## 1. L'installation

```
Android Studio  →  developer.android.com/studio
```

Pendant l'assistant, accepte l'installation du **SDK** et d'un **émulateur**. Compte
8 à 10 Go de disque et 20 à 40 minutes.

> **Si ta machine est lente, saute l'émulateur** et branche ton téléphone :
> Paramètres → À propos → appuyer 7 fois sur « Numéro de build » → Options développeur →
> **Débogage USB**. C'est plus rapide qu'un émulateur sur un portable modeste, et ça marche
> mieux pour les TP suivants (capteurs, GPS, appareil photo).

---

## 2. Créer le projet

```
File > New > New Project > Empty Views Activity
```

| Champ        | Valeur                 | Pourquoi                                     |
| ------------ | ---------------------- | -------------------------------------------- |
| Name         | `TP1Intents`         |                                              |
| Package name | `com.cyu.tp1intents` | **note-le**, tu en auras besoin au §5 |
| Language     | **Java**         | l'énoncé est en Java, pas en Kotlin        |
| Minimum SDK  | API 24                 | couvre ~95 % des appareils                   |

> **Choisis bien « Empty Views Activity »**, pas « Empty Activity ». Depuis 2023, « Empty
> Activity » crée un projet **Jetpack Compose**, sans fichier XML de layout — et tout
> l'énoncé repose sur le XML. C'est le piège d'installation n° 1 cette année.

### Les trois fichiers qui comptent

```
app/src/main/
├── java/com/cyu/tp1intents/
│   ├── MainActivity.java        ← le code du premier écran
│   └── SecondActivity.java      ← à créer
├── res/layout/
│   ├── activity_main.xml        ← l'apparence du premier écran
│   └── activity_second.xml      ← à créer
└── AndroidManifest.xml          ← la liste des écrans de l'app
```

**Le manifeste est le fichier qu'on oublie.** Toute Activity doit y être déclarée, sinon
l'application plante au lancement avec `ActivityNotFoundException`. Android Studio le fait
automatiquement quand tu crées l'Activity par le menu — **pas** si tu crées le fichier `.java` à la main.

---

## 3. Le premier écran — `activity_main.xml`

L'énoncé demande : un titre, deux champs de saisie, un bouton.

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="24dp">

    <TextView
        android:id="@+id/message"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Welcome!\nPlease enter your details below to continue..."
        android:textSize="18sp" />

    <EditText
        android:id="@+id/name"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:inputType="textPersonName"
        android:hint="Name" />

    <EditText
        android:id="@+id/email"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:inputType="textEmailAddress"
        android:hint="Email" />

    <Button
        android:id="@+id/button"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="OK"
        android:onClick="submit" />

</LinearLayout>
```

### Les quatre attributs à comprendre

| Attribut                     | Rôle                                                                                                                                                        |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `android:id="@+id/name"`   | crée un**identifiant** ; le `+` veut dire « je le déclare ici ». C'est lui qui devient `R.id.name` dans le Java                                |
| `layout_width/height`      | `match_parent` = toute la largeur du parent ; `wrap_content` = juste la taille du contenu. **Ces deux attributs sont obligatoires sur chaque vue** |
| `android:inputType`        | change le**clavier** affiché : `textEmailAddress` fait apparaître le `@`                                                                         |
| `android:onClick="submit"` | relie le bouton à la**méthode Java `submit`**. Le nom doit correspondre **exactement**                                                       |

> **Le piège de `onClick`** : si la méthode `submit` n'existe pas, ne s'appelle pas
> exactement pareil, ou n'a pas la signature `public void submit(View view)`, **le projet
> compile** et l'application **plante au clic**. Aucun avertissement du compilateur.

---

## 4. `LinearLayout` ou `ConstraintLayout` ?

Android Studio crée un `ConstraintLayout` par défaut. L'énoncé ne l'impose pas.

|             | `LinearLayout`                                  | `ConstraintLayout`                                |
| ----------- | ------------------------------------------------- | --------------------------------------------------- |
| Principe    | empile les vues, verticalement ou horizontalement | chaque vue est**ancrée** par des contraintes |
| Pour le TP1 | **plus simple** — quatre vues empilées    | plus puissant, plus verbeux                         |

**Prends `LinearLayout` pour le TP1.** Tu passeras au `ConstraintLayout` quand une mise en
page l'exigera — et là, l'éditeur graphique (onglet **Design**) sera plus rapide que le XML
à la main.

> Dans le `ConstraintLayout` par défaut, **une vue sans contrainte se colle en haut à
> gauche**. Si tes quatre widgets se superposent dans un coin, c'est ça — pas un bug.

---

## 5. L'Intent — le cœur du TP

### La méthode `submit`

Dans `MainActivity.java` :

```java
public class MainActivity extends AppCompatActivity {

    // Les CLÉS de l'intent. Convention : préfixer par le package pour éviter les collisions.
    public final static String NAME  = "com.cyu.tp1intents.name";
    public final static String EMAIL = "com.cyu.tp1intents.email";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }

    public void submit(View view) {
        // 1. Créer l'intent : "je veux lancer SecondActivity"
        Intent intent = new Intent(this, SecondActivity.class);

        // 2. Récupérer les vues par leur id
        EditText eTname  = (EditText) findViewById(R.id.name);
        EditText eTemail = (EditText) findViewById(R.id.email);

        // 3. Extraire le texte saisi
        String name  = eTname.getText().toString();
        String email = eTemail.getText().toString();

        // 4. Attacher les données à l'intent
        intent.putExtra(NAME,  name);
        intent.putExtra(EMAIL, email);

        // 5. Partir
        startActivity(intent);
    }
}
```

### Ce qu'il faut comprendre, ligne par ligne

**`new Intent(this, SecondActivity.class)`** — un Intent **explicite** : je nomme la classe
exacte à lancer. (Il existe des intents *implicites*, qui disent *« ouvre une page web »*
sans nommer l'application — c'est ce qui permet à Android de proposer un choix de
navigateur. Hors TP1, mais sache la distinction : **c'est une question d'examen.**)

**`findViewById(R.id.name)`** — fait le pont entre le XML et le Java. `R` est une classe
**générée automatiquement** à la compilation à partir de tes fichiers `res/`. Si `R.id.name`
est souligné en rouge, ce n'est presque jamais une erreur Java : c'est que **ton XML ne
compile pas**. Corrige le XML, puis `Build > Clean Project`.

**`putExtra(clé, valeur)`** — un Intent transporte un dictionnaire. On range sous une clé,
on relit sous la même. D'où les constantes : **si tu écris la chaîne à la main des deux
côtés, une faute de frappe donne `null` sans aucune erreur.**

**`getText().toString()`** — `getText()` rend un `Editable`, pas un `String`. La conversion
est obligatoire.

---

## 6. Le second écran

### Le créer proprement

```
Clic droit sur le package  >  New  >  Activity  >  Empty Views Activity
Nom : SecondActivity
```

**Par le menu, jamais à la main** : c'est ce qui l'inscrit dans `AndroidManifest.xml`.

### `activity_second.xml`

```xml
<LinearLayout ... android:orientation="vertical" android:padding="24dp">

    <TextView android:id="@+id/name"  ... />
    <TextView android:id="@+id/email" ... />

    <ImageView
        android:id="@+id/image"
        android:layout_width="match_parent"
        android:layout_height="200dp"
        android:src="@drawable/photo"
        android:scaleType="centerCrop"
        android:contentDescription="Illustration" />

    <Button
        android:id="@+id/next"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Next"
        android:onClick="goNext" />

</LinearLayout>
```

**Pour l'image** (l'énoncé impose moins de 100 Ko) : glisse ton fichier dans
`app/src/main/res/drawable/`. Le nom doit être **en minuscules, sans espace, sans
accent** — sinon la ressource n'est pas générée.

### `SecondActivity.java`

```java
public class SecondActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_second);

        // Récupérer l'intent qui a lancé cette activity
        Intent intent = getIntent();
        String name  = intent.getStringExtra(MainActivity.NAME);
        String email = intent.getStringExtra(MainActivity.EMAIL);

        TextView tvName  = (TextView) findViewById(R.id.name);
        TextView tvEmail = (TextView) findViewById(R.id.email);

        tvName.setText(name);
        tvEmail.setText(email);
    }

    public void goNext(View view) {
        startActivity(new Intent(this, ThirdActivity.class));
    }
}
```

> **`getIntent()` rend l'intent qui a lancé *cette* activity.** C'est le pendant exact de
> `startActivity(intent)` dans l'autre sens. **Les clés doivent être les mêmes des deux
> côtés** — d'où `MainActivity.NAME`, et pas une chaîne réécrite.

Puis crée `ThirdActivity` de la même façon pour le bouton « Next ».

---

## 7. Les six erreurs du TP1

| Symptôme                                   | Cause                                                        | Correctif                                               |
| ------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------- |
| Plantage au clic sur OK                     | méthode`submit` absente ou mal signée                    | `public void submit(View view)`, nom identique au XML |
| `R.id.xxx cannot be resolved`             | le XML ne compile pas                                        | corriger le XML, puis`Build > Clean Project`          |
| `ActivityNotFoundException`               | Activity absente du manifeste                                | la recréer par le menu New > Activity                  |
| Le second écran affiche vide               | clés différentes entre`putExtra` et `getStringExtra`   | utiliser les constantes`MainActivity.NAME`            |
| `NullPointerException` sur `setText`    | `findViewById` cherche un id absent de **ce** layout | vérifier que l'id est bien dans`activity_second.xml` |
| Tous les widgets empilés en haut à gauche | `ConstraintLayout` sans contraintes                        | passer en`LinearLayout` ou ancrer les vues            |

---

## 8. Ce qu'on peut te demander à l'oral

Le cours est noté **50 % labs et projet, 50 % examen final**. Prépare ces réponses :

1. Qu'est-ce qu'une **Activity** ? Cite trois méthodes de son cycle de vie.
2. Qu'est-ce qu'un **Intent** ? Différence entre **explicite** et **implicite** ?
3. Comment passe-t-on des données d'une Activity à une autre ?
4. À quoi sert `AndroidManifest.xml` ?
5. Que contient la classe `R`, et **qui l'écrit** ?
6. Pourquoi sépare-t-on le layout (XML) du comportement (Java) ?
7. Que se passe-t-il à la **rotation** de l'écran ? *(l'Activity est détruite et recréée —
   c'est le sujet de `onSaveInstanceState`, et la question piège classique)*

---

## 9. Ton retard, et comment le combler

Le TP1 a eu lieu avant ton arrivée. Concrètement :

- [ ] Installer Android Studio **ce week-end** — c'est le plus long, et ça ne demande pas
  de réfléchir
- [ ] Refaire le TP1 en entier, seul : les trois écrans, l'image, les deux intents
- [ ] **Demander à M. Kotzinos** si les TP sont notés individuellement ou en binôme, et si
  le rendu du TP1 est encore possible
- [ ] Lire `2026_Mobile_Computing_Course_Description.docx` pour connaître le projet final —
  c'est lui qui pèse, et il vaut mieux le savoir tôt

> **La bonne nouvelle** : Mobile Computing est la mineure la plus clémente du lot — **50 %
> d'examen final**, donc un démarrage tardif se rattrape. Ce n'est pas le cas de l'anglais
> ni de la SAÉ. **Mets-y le minimum pour suivre, et garde ton énergie pour le partiel
> d'algo du 4 novembre.**

---

## 10. Pour aller plus loin, quand tu auras le temps

Ton axe est la cybersécurité. Android est un terrain direct :

- le **modèle de permissions** et le sandboxing par application
- `Intent` implicites et **intent redirection** — une classe de vulnérabilité réelle
- le stockage : `SharedPreferences` en clair contre `EncryptedSharedPreferences`
- certificate pinning, et pourquoi le trafic d'une app se lit si facilement sans lui

**Rien de tout ça avant décembre.** Mais si tu dois choisir un sujet de projet dans cette
mineure, choisis-en un qui touche à la sécurité : tu travailleras deux objectifs à la fois.
