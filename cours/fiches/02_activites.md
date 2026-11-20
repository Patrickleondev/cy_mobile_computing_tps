# 02. Les activités et leur cycle de vie

> Sources : cours 2 (Activities), TP1. Corrigé : `10_corriges.md`, partie 02.
> Question d'examen directement liée : **annale 1, exercice 1.2** (« A démarre B : donnez
> la séquence des callbacks »).

---

## 1. Pourquoi un cycle de vie ?

Sur un téléphone, ton écran peut être interrompu **à tout moment** : un appel arrive,
l'utilisateur appuie sur Accueil, tourne le téléphone, ou le système manque de mémoire et
tue ton processus.

Le système te **prévient** à chaque changement en appelant une méthode de ton activité.
Ces méthodes s'appellent des **callbacks** (« rappels ») : tu ne les appelles jamais
toi-même, tu les **redéfinis** (`@Override`) pour réagir au bon moment.

Ton travail : **mettre le bon code dans le bon callback.** La plupart des bugs Android
viennent d'un code placé un callback trop tôt ou trop tard.

---

## 2. Les 7 callbacks et les états

```
                  ┌──────────────┐
  lancement ────► │  onCreate()  │  créée
                  └──────┬───────┘
                         ▼
                  ┌──────────────┐ ◄──────────────── onRestart() ◄──┐
                  │  onStart()   │  visible                         │
                  └──────┬───────┘                                  │
                         ▼                                          │
                  ┌──────────────┐ ◄──────────┐                     │
                  │  onResume()  │            │ l'utilisateur       │ l'utilisateur
                  └──────┬───────┘            │ revient (dialogue   │ revient sur
                         ▼                    │ fermé...)           │ l'écran
              ╔══════════════════════╗        │                     │
              ║   EN COURS (RESUMED)  ║        │                     │
              ║ visible + au premier  ║        │                     │
              ║ plan + reçoit le      ║        │                     │
              ║ toucher               ║        │                     │
              ╚══════════╤═══════════╝        │                     │
                         ▼                    │                     │
                  ┌──────────────┐ ───────────┘                     │
                  │  onPause()   │  partiellement cachée            │
                  └──────┬───────┘                                  │
                         ▼                                          │
                  ┌──────────────┐ ─────────────────────────────────┘
                  │   onStop()   │  plus du tout visible
                  └──────┬───────┘
                         ▼
                  ┌──────────────┐
                  │ onDestroy()  │  détruite (peut être SAUTÉE si le
                  └──────────────┘  système tue le processus)
```

**Les paires miroirs** (à retenir absolument) :

| On acquiert dans... | On libère dans... | Durée de vie correspondante |
|---|---|---|
| `onCreate` | `onDestroy` | **toute la vie** de l'objet |
| `onStart` | `onStop` | la vie **visible** |
| `onResume` | `onPause` | la vie **au premier plan** (reçoit le toucher) |

> **La règle d'appariement :** ce que tu démarres dans `onResume`, tu l'arrêtes dans
> `onPause`. Ce que tu démarres dans `onStart`, tu l'arrêtes dans `onStop`. Si tu ne sais
> pas dire dans quel callback tu libères une ressource, elle fuit (et la batterie avec).

**Que mettre où :**

| Callback | On y met | Erreur classique |
|---|---|---|
| `onCreate` | `setContentView`, `findViewById`, les listeners, relire le `Bundle` | démarrer les capteurs ici : ils tournent même quand l'appli est en arrière-plan |
| `onStart` | ce qui doit tourner tant que l'écran est **visible** | croire qu'il ne s'exécute qu'une fois (il revient après chaque `onStop`) |
| `onResume` | **capteurs, GPS, caméra, animations** | y mettre un travail lourd |
| `onPause` | **arrêter capteurs, caméra, animations** ; doit être **rapide** | y sauver en base : ça retarde l'écran suivant |
| `onStop` | **sauvegarder les données**, arrêter la localisation, désinscrire les receivers | l'oublier : c'est l'endroit **fiable** pour sauver |
| `onDestroy` | libérer ce qui reste | compter dessus : si le processus est tué, il n'est **pas appelé** |

**Pause n'est pas Stop.** `onPause` : quelque chose passe devant, mais ton écran peut rester
**partiellement visible** (une boîte de dialogue, le mode écran partagé). `onStop` : ton
écran n'est **plus du tout visible**.

---

## 3. Les séquences à connaître par cœur

Ces séquences sont **la** question type de l'examen. Apprends-les comme des tables de
multiplication.

### 3.1 Lancement de l'appli

```
onCreate → onStart → onResume
```

### 3.2 L'activité A démarre l'activité B (annale 1, ex. 1.2)

```
A.onPause()          ← A perd le premier plan, D'ABORD
B.onCreate()
B.onStart()
B.onResume()         ← B est maintenant au premier plan
A.onStop()           ← A n'est plus visible, EN DERNIER
```

**Pourquoi cet ordre :** le système met A en pause tout de suite, pour que B puisse
s'afficher vite. Il n'arrête A (`onStop`) qu'**une fois B affichée**, car tant que B n'est
pas visible, A l'est encore. C'est pour ça qu'on ne fait **rien de lent dans `onPause`** :
B attend qu'il soit terminé pour démarrer.

*(Détail : `A.onSaveInstanceState()` est appelé juste après `A.onStop()` depuis Android 9.
Si B est une fenêtre transparente ou une boîte de dialogue, A reste visible et **`A.onStop()`
n'est pas appelé**.)*

### 3.3 Retour arrière (Back) de B vers A

```
B.onPause()
A.onRestart()        ← A n'avait pas été détruite : onRestart, PAS onCreate
A.onStart()
A.onResume()
B.onStop()
B.onDestroy()        ← B est retirée de la pile, donc détruite
```

### 3.4 Bouton Accueil, puis retour dans l'appli

```
Accueil :  onPause → onStop
Retour  :  onRestart → onStart → onResume
```

L'instance survit : **pas de `onCreate`** au retour.

### 3.5 Un appel entrant couvre l'écran, puis se termine

Exactement comme Accueil : `onPause → onStop`, puis `onRestart → onStart → onResume`. Du
point de vue de ton activité, une autre activité (celle du téléphone) est simplement passée
devant.

### 3.6 Rotation de l'écran

```
onPause → onStop → onSaveInstanceState → onDestroy
→ onCreate(bundle) → onStart → onRestoreInstanceState → onResume
```

**L'activité est détruite et recréée de zéro.** Les champs (attributs) de ta classe sont
**perdus**. Seul ce qui est dans le `Bundle` (ou un `ViewModel`) survit.

### 3.7 `finish()` (ou dernier Back)

```
onPause → onStop → onDestroy
```

---

## 4. Sauver l'état : où les données survivent

| Où | Survit à la rotation ? | Survit au processus tué ? | Pour quoi |
|---|---|---|---|
| un **champ** de l'activité | non | non | ce qu'on peut recalculer |
| un **ViewModel** | **oui** | non | l'état de l'écran en mémoire |
| le **Bundle** (`onSaveInstanceState`) | **oui** | **oui** | de **petites** choses : texte en cours de frappe, position de défilement (limite ~1 Mo) |
| le **disque** (SharedPreferences, SQLite, fichier) | oui | oui | tout ce que l'utilisateur serait furieux de perdre |

**La question qui décide :** « Si Android tuait mon processus maintenant et que
l'utilisateur revenait dans dix minutes, qu'est-ce qui doit encore être là ? » Tout ce qui
répond « oui » va **sur le disque**.

> **À savoir écrire par cœur :**

```java
private static final String KEY_SAISIE = "saisie";

@Override
protected void onSaveInstanceState(Bundle outState) {
    super.onSaveInstanceState(outState);
    outState.putString(KEY_SAISIE, champ.getText().toString());
}

@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_main);
    champ = (EditText) findViewById(R.id.champ);
    if (savedInstanceState != null) {          // null au premier lancement
        champ.setText(savedInstanceState.getString(KEY_SAISIE));
    }
}
```

Le `Bundle` est rendu **à deux endroits** : dans `onCreate(Bundle)` et dans
`onRestoreInstanceState(Bundle)`. Dans `onCreate`, il faut **tester `null`** (premier
lancement).

---

## 5. Démarrer une autre activité et lui passer des données

C'est le TP1. Trois étapes :

```java
// Dans MainActivity : ENVOYER
public static final String EXTRA_NOM = "fr.cyu.tp1.nom";

Intent i = new Intent(this, SecondActivity.class);  // Intent EXPLICITE (on nomme la classe)
i.putExtra(EXTRA_NOM, "Patrick");                   // on attache une donnée (clé, valeur)
startActivity(i);                                   // on demande au système de lancer B
```

```java
// Dans SecondActivity.onCreate : RECEVOIR
String nom = getIntent().getStringExtra(MainActivity.EXTRA_NOM);
```

```java
// Fermer l'écran courant et revenir au précédent
finish();
```

Et la déclaration obligatoire dans le manifeste :
`<activity android:name=".SecondActivity" />`.

**Obtenir un résultat en retour** (B renvoie une valeur à A) :

```java
// Style du cours (ancien, 🕰️ déprécié mais encore compris partout) :
startActivityForResult(i, CODE_EDITION);             // dans A

@Override
protected void onActivityResult(int requestCode, int resultCode, Intent data) {  // dans A
    super.onActivityResult(requestCode, resultCode, data);
    if (requestCode == CODE_EDITION && resultCode == RESULT_OK) {
        String texte = data.getStringExtra("texte");
    }
}

// Dans B, avant de se fermer :
Intent retour = new Intent();
retour.putExtra("texte", "modifié");
setResult(RESULT_OK, retour);
finish();
```

Le style moderne (cours 2) remplace `startActivityForResult` par
`registerForActivityResult(...)` déclaré comme champ, puis `launcher.launch(intent)`.
**Le côté B ne change pas** (`setResult` + `finish`).

---

## 6. Tâches et pile de retour (back stack)

Ce que l'utilisateur appelle « l'appli » est une **tâche** : une **pile** d'activités.

```
   ┌─────────────────┐
   │ EditActivity    │ ← au sommet : au premier plan
   ├─────────────────┤
   │ DetailActivity  │   arrêtée (onStop)
   ├─────────────────┤
   │ MainActivity    │   arrêtée, racine de la tâche
   └─────────────────┘
```

- `startActivity()` **empile**. Back et `finish()` **dépilent** (l'activité du sommet est
  détruite).
- Dépiler la racine termine la tâche et ramène au lanceur.
- Une pile peut contenir des activités **d'applications différentes** (si tu partages une
  photo, l'écran de l'autre appli vient s'empiler sur le tien).

---

## 7. À toi (sur papier, fichier fermé)

**Exercice 2.1 :** Dessine de mémoire le diagramme du cycle de vie avec les 7 callbacks,
les 3 flèches de retour, et les 3 durées de vie (entière, visible, premier plan).

**Exercice 2.2 :** Donne la séquence **complète** des callbacks, en précisant à chaque fois
l'activité concernée :
1. L'utilisateur lance l'appli (activité A).
2. A démarre B.
3. L'utilisateur appuie sur Back.
4. L'utilisateur appuie sur Accueil.
5. L'utilisateur revient dans l'appli depuis la liste des applis récentes.

**Exercice 2.3 :** Une appli de course à pied utilise le GPS et l'accéléromètre. Dans quel
callback les démarrer, dans lequel les arrêter ? Pourquoi pas `onCreate` / `onDestroy` ?

**Exercice 2.4 :** L'utilisateur tape un message, tourne le téléphone, et le message
disparaît. Explique pourquoi, puis écris le code qui corrige le problème.

**Exercice 2.5 :** Un étudiant enregistre les notes de l'utilisateur en base de données
dans `onDestroy()`. Pourquoi est-ce une mauvaise idée, et où faut-il le faire ?

**Exercice 2.6 :** Écris le code complet pour que `MainActivity` ouvre `ProfilActivity` en
lui passant un `int age = 21` et un `String ville = "Cergy"`, puis le code de
`ProfilActivity.onCreate` qui récupère ces deux valeurs et les affiche dans un `TextView`
d'id `info`. N'oublie pas la ligne du manifeste.

**Exercice 2.7 :** Vrai ou faux ?
1. `onStop()` est toujours appelé avant `onDestroy()`.
2. `onDestroy()` est toujours appelé avant que le processus soit tué.
3. Après une rotation, les attributs de l'activité ont gardé leur valeur.
4. Quand A démarre B, `A.onStop()` est appelé avant `B.onCreate()`.
