# 04. L'interface : vues, layouts, événements

> Sources : cours 2 (Views & layouts, menus, notifications), TP1. Corrigé :
> `10_corriges.md`, partie 04.
> Questions d'examen liées : **annale 1, ex. 2** et **annale 2, Q4** (dessiner un
> RelativeLayout : **3,5 et 5 points**), **annale 2, Q1 c, d, e** et **Q2a**.

---

## 1. Un écran est un arbre

- Une **View** est une feuille qui **se dessine** : `TextView`, `Button`, `EditText`,
  `ImageView`, `CheckBox`, `Spinner`...
- Un **ViewGroup** est une branche qui **place ses enfants** : ce sont les **layouts**
  (`LinearLayout`, `RelativeLayout`...). Un ViewGroup est lui-même une View, donc on peut
  les imbriquer.

```
RelativeLayout                ← racine, passée à setContentView
├── TextView   (titre)
├── EditText   (saisie)
└── LinearLayout              ← un groupe dans le groupe
    ├── Button (Annuler)
    └── Button (Valider)
```

Chaque nœud est **mesuré**, puis **placé**, puis **dessiné**. Plus l'arbre est profond, plus
c'est lent : c'est pour ça qu'on évite d'imbriquer trop de layouts.

---

## 2. Les unités et les attributs de tous les jours

| Valeur | Sens |
|---|---|
| `match_parent` (ancien nom : `fill_parent`) | aussi grand que le parent le permet (moins son *padding*) |
| `wrap_content` | juste assez grand pour son contenu |
| `0dp` | « pas de taille propre » : la taille vient des poids (LinearLayout) ou des contraintes (ConstraintLayout, RelativeLayout) |
| `dp` | pixel **indépendant de la densité** : pour **toutes les tailles et marges** |
| `sp` | comme `dp`, mais suit la taille de police choisie par l'utilisateur : **pour le texte, toujours** |
| `px` | pixel réel de l'écran : à éviter |

| Attribut | Effet |
|---|---|
| `layout_width`, `layout_height` | **obligatoires** sur chaque vue |
| `padding` | espace **à l'intérieur** de la vue (entre son bord et son contenu) |
| `layout_margin` | espace **à l'extérieur** de la vue (entre elle et ses voisines) |
| `gravity` | où se place **mon contenu** à l'intérieur de moi |
| `layout_gravity` | où **je** me place dans mon parent |
| `visibility` | `visible`, `invisible` (cachée mais **garde sa place**), `gone` (cachée et **libère sa place**) |
| `hint` | texte grisé affiché dans un champ vide |

**Repère :** tout attribut qui commence par `layout_` parle de la relation avec **le
parent**. Sans `layout_`, il parle de la vue elle-même.

---

## 3. Les types de layout (annale 2, Q1d : « citez-en cinq »)

| Layout | Principe | Usage |
|---|---|---|
| **LinearLayout** | enfants **en ligne ou en colonne** (`orientation`), partage de l'espace avec `layout_weight` | formulaires simples, barres de boutons |
| **RelativeLayout** | chaque enfant est placé **par rapport au parent ou à un frère** | le layout des annales |
| **ConstraintLayout** | comme Relative, en plus puissant : **contraintes** sur chaque bord, arbre plat | le choix par défaut aujourd'hui |
| **FrameLayout** | enfants **empilés** les uns sur les autres | un conteneur à un seul enfant, un badge sur une image |
| **TableLayout** | lignes (`TableRow`) et colonnes | tableaux, anciens formulaires |
| **GridLayout** | grille de lignes et colonnes | claviers, grilles |
| **AbsoluteLayout** 🕰️ | coordonnées x, y fixes | **déprécié**, ne marche pas sur des écrans de tailles différentes |

Et pour les listes : **ListView** (ancien) et **RecyclerView** (actuel), qui affichent une
liste défilante à partir d'un **adaptateur**.

---

## 4. LinearLayout et les poids

```xml
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="horizontal">
    <Button android:layout_width="0dp" android:layout_height="wrap_content"
            android:layout_weight="1" android:text="Annuler" />
    <Button android:layout_width="0dp" android:layout_height="wrap_content"
            android:layout_weight="2" android:text="Valider" />
</LinearLayout>
```

```
┌───────────────────────────────────────────────┐
│┌─────────────┐┌──────────────────────────────┐│
││   Annuler   ││           Valider            ││   largeurs 1/3 et 2/3
│└─────────────┘└──────────────────────────────┘│
└───────────────────────────────────────────────┘
```

- `width="0dp"` + `weight` : « pas de largeur propre, partagez l'espace libre **1 : 2** ».
- Les poids ne jouent **que dans le sens de l'orientation**.
- Sans `orientation`, c'est **horizontal** par défaut : le piège classique du « mon deuxième
  bouton a disparu » (il est sorti de l'écran à droite).

---

## 5. RelativeLayout : la méthode pour dessiner (le cœur de ce chapitre)

### 5.1 Les attributs

**Par rapport au PARENT** (valeur `"true"`) :

| Attribut | La vue se colle... |
|---|---|
| `layout_alignParentTop` | en **haut** du parent |
| `layout_alignParentBottom` | en **bas** du parent |
| `layout_alignParentLeft` / `layout_alignParentStart` | à **gauche** du parent |
| `layout_alignParentRight` / `layout_alignParentEnd` | à **droite** du parent |
| `layout_centerHorizontal` | au **centre horizontal** |
| `layout_centerVertical` | au **centre vertical** |
| `layout_centerInParent` | au **centre** des deux |

**Par rapport à un FRÈRE** (valeur `"@id/autreVue"`) :

| Attribut | La vue se place... |
|---|---|
| `layout_below="@id/X"` | **sous** X (son haut touche le bas de X) |
| `layout_above="@id/X"` | **au-dessus** de X |
| `layout_toLeftOf` / `layout_toStartOf="@id/X"` | **à gauche** de X (son bord droit touche le bord gauche de X) |
| `layout_toRightOf` / `layout_toEndOf="@id/X"` | **à droite** de X |
| `layout_alignTop="@id/X"` | son haut **aligné** sur le haut de X |
| `layout_alignBottom` / `alignLeft` / `alignRight` / `alignStart` / `alignEnd` | même idée, sur l'autre bord |
| `layout_alignBaseline="@id/X"` | les lignes de texte alignées |

**Start et End :** dans une langue écrite de gauche à droite (français, anglais), **Start =
gauche** et **End = droite**. Elles s'inversent pour l'arabe ou l'hébreu.

### 5.2 Les quatre règles qui font tout le dessin

1. **Par défaut, une vue va en haut à gauche** (dans la zone intérieure, donc après le
   *padding*). Une vue sans aucune règle verticale se met **en haut**, même s'il y a déjà
   quelque chose : **les vues se superposent** dans un RelativeLayout, elles ne se poussent
   pas.
2. **Une vue contrainte des DEUX côtés sur un axe s'étire entre les deux**, quelle que soit
   sa `layout_width` (`wrap_content` ou `0dp`). Exemple : `alignParentStart` +
   `alignParentEnd` → toute la largeur. `alignParentLeft` + `toLeftOf="@id/X"` → du bord
   gauche jusqu'à X.
3. **`match_parent`** = toute la largeur intérieure du parent (largeur moins le *padding*).
4. **Les vues sont lues dans l'ordre**, mais une vue peut faire référence à une vue écrite
   **plus bas** dans le fichier (c'est là qu'on voit `@+id/` dans un `layout_toLeftOf` :
   l'identifiant est créé à l'avance).

### 5.3 La méthode en 4 étapes

1. **Dessine le cadre du parent.** Note son *padding* : trace une ligne pointillée à
   l'intérieur, tout se place dans cette zone.
2. **Pour chaque vue, dans l'ordre, fais un tableau** : règle horizontale, règle
   verticale, largeur, hauteur, contenu (texte, *hint*).
3. **Place d'abord les vues accrochées au parent seul**, puis celles qui dépendent d'une
   autre vue (on ne peut placer « sous X » qu'une fois X placé).
4. **Dessine des rectangles étiquetés** avec leur contenu, et indique les tailles fixes
   (96dp, 160dp). Le prof veut voir que tu as compris **la position et la taille**, pas un
   joli dessin.

### 5.4 Exemple corrigé (fais-le d'abord seul, puis compare)

```xml
<RelativeLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:padding="16dp">

    <TextView android:id="@+id/titre"
        android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:layout_alignParentTop="true"
        android:layout_centerHorizontal="true"
        android:text="Connexion" />

    <EditText android:id="@+id/login"
        android:layout_width="match_parent" android:layout_height="wrap_content"
        android:layout_below="@id/titre"
        android:hint="Identifiant" />

    <EditText android:id="@+id/mdp"
        android:layout_width="match_parent" android:layout_height="wrap_content"
        android:layout_below="@id/login"
        android:hint="Mot de passe" />

    <Button android:id="@+id/annuler"
        android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:layout_below="@id/mdp"
        android:layout_alignParentLeft="true"
        android:text="Annuler" />

    <Button android:id="@+id/valider"
        android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:layout_below="@id/mdp"
        android:layout_alignParentRight="true"
        android:text="Valider" />

    <TextView android:id="@+id/oubli"
        android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:layout_below="@id/annuler"
        android:layout_centerHorizontal="true"
        android:text="Mot de passe oublié ?" />
</RelativeLayout>
```

**Étape 2, le tableau :**

| Vue | Horizontal | Vertical | Largeur | Contenu |
|---|---|---|---|---|
| `titre` | centré | en haut | son texte | « Connexion » |
| `login` | toute la largeur | sous `titre` | match_parent | *Identifiant* (grisé) |
| `mdp` | toute la largeur | sous `login` | match_parent | *Mot de passe* (grisé) |
| `annuler` | à gauche | sous `mdp` | son texte | « Annuler » |
| `valider` | à droite | sous `mdp` | son texte | « Valider » |
| `oubli` | centré | sous `annuler` | son texte | « Mot de passe oublié ? » |

**Étape 4, le dessin :**

```
┌─────────────────────────────────────────────┐   padding de 16dp tout autour :
│                  Connexion                  │   rien ne touche le bord
│  ┌───────────────────────────────────────┐  │
│  │ Identifiant                (grisé)    │  │
│  └───────────────────────────────────────┘  │
│  ┌───────────────────────────────────────┐  │
│  │ Mot de passe               (grisé)    │  │
│  └───────────────────────────────────────┘  │
│  ┌─────────┐                   ┌─────────┐  │
│  │ Annuler │                   │ Valider │  │
│  └─────────┘                   └─────────┘  │
│            Mot de passe oublié ?            │
│                                             │
│                 (vide)                      │
│                                             │
└─────────────────────────────────────────────┘
```

**Question piège :** si on retirait `layout_below="@id/mdp"` du bouton Valider, où
irait-il ? **En haut à droite**, par-dessus le titre (règle 1 : pas de règle verticale →
en haut).

---

## 6. Réagir aux clics (annale 2, Q1c : « deux façons de définir un ClickListener »)

Un **listener** est une interface à une méthode, que le système appelle quand l'événement
se produit. Il y a **quatre façons** de l'écrire pour un bouton :

```java
// 1. Classe anonyme (le style des cours)
bouton.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        valider();
    }
});

// 2. Lambda (Java 8+, la même chose en plus court)
bouton.setOnClickListener(v -> valider());

// 3. L'activité implémente l'interface
public class MainActivity extends Activity implements View.OnClickListener {
    ...  bouton.setOnClickListener(this);  ...
    @Override
    public void onClick(View v) {
        if (v.getId() == R.id.bouton) { valider(); }
    }
}
```

```xml
<!-- 4. Dans le XML (c'est ce que fait le TP1) -->
<Button android:id="@+id/bouton" android:onClick="valider" ... />
```

```java
// ... avec, dans l'activité, une méthode PUBLIQUE qui prend une View :
public void valider(View view) { ... }
```

**Les autres listeners utiles :**

| Listener | Déclenché quand |
|---|---|
| `OnClickListener` | un appui court se termine |
| `OnLongClickListener` | appui long (~0,5 s). Renvoie `true` si l'événement est traité |
| `OnTouchListener` | chaque événement brut du toucher |
| `TextWatcher` | le texte d'un `EditText` change |
| `OnCheckedChangeListener` | une case ou un interrupteur change d'état |
| `OnItemClickListener` | un élément d'une `ListView` est touché |

**Règle d'or :** le listener s'exécute sur le **thread principal** (le thread de
l'interface). Tout ce qui est lent (réseau, base de données, fichier) doit partir dans un
autre thread, sinon l'appli gèle (ANR au bout de 5 s). *(Chapitre 06.)*

---

## 7. Les listes : ListView et ArrayAdapter (annale 2, Q2a)

**Le problème :** afficher 1 000 éléments sans créer 1 000 vues. **La solution :** un
**adaptateur** fait le lien entre **les données** (une liste Java) et **la vue** (la
liste à l'écran). Il fabrique une ligne à la demande, pour les éléments visibles.

```java
String[] villes = { "Cergy", "Pontoise", "Paris", "Lomé" };
ListView liste = (ListView) findViewById(R.id.liste);

liste.setAdapter(new ArrayAdapter<>(this,
        android.R.layout.simple_list_item_1,   // layout d'UNE ligne, fourni par Android
        villes));                              // les données

liste.setOnItemClickListener(new AdapterView.OnItemClickListener() {
    @Override
    public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
        Toast.makeText(MainActivity.this, villes[position], Toast.LENGTH_SHORT).show();
    }
});
```

- `android.R.layout.simple_list_item_1` : un layout **du système** (d'où `android.R` et
  non `R`) qui contient **un seul TextView**. Chaque élément de la liste devient une ligne
  de texte.
- `MainActivity.this` : dans une classe anonyme, `this` désigne le listener. Pour passer
  l'activité comme `Context`, on écrit `MainActivity.this`.

🕰️ Aujourd'hui on utilise **RecyclerView** (adaptateur + `ViewHolder` + `LayoutManager`),
qui **recycle** les lignes sorties de l'écran. L'idée de l'adaptateur est la même.

---

## 8. Parler à l'utilisateur

| Moyen | Interrompt... | Code |
|---|---|---|
| **Toast** | rien : un message flottant qui disparaît seul | `Toast.makeText(this, "Enregistré", Toast.LENGTH_SHORT).show();` |
| **Snackbar** | rien, mais peut proposer **une action** (ANNULER) | `Snackbar.make(vue, "Supprimé", Snackbar.LENGTH_LONG).setAction("Annuler", v -> ...).show();` |
| **Dialog** | **tout** : l'utilisateur doit répondre | `new AlertDialog.Builder(this).setTitle(...).setMessage(...).setPositiveButton("OK", null).show();` |
| **Notification** | rien, et **s'affiche même quand l'appli est fermée** | canal + `NotificationCompat.Builder` + permission `POST_NOTIFICATIONS` |

> **Piège du Toast à l'examen :** ne pas oublier **`.show()`** à la fin. Sans lui, rien ne
> s'affiche. Et la durée est `Toast.LENGTH_SHORT` ou `Toast.LENGTH_LONG`, pas un nombre.

**Les menus (style du cours) :**

```java
@Override
public boolean onCreateOptionsMenu(Menu menu) {
    getMenuInflater().inflate(R.menu.menu_main, menu);   // res/menu/menu_main.xml
    return true;
}

@Override
public boolean onOptionsItemSelected(MenuItem item) {
    if (item.getItemId() == R.id.action_parametres) {
        startActivity(new Intent(this, ParametresActivity.class));
        return true;
    }
    return super.onOptionsItemSelected(item);
}
```

---

## 9. À toi (sur papier, fichier fermé)

**Exercice 4.1 (annale 1, ex. 2, 3,5 points) :** dessine le résultat.

```xml
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:paddingLeft="16dp"
    android:paddingRight="16dp" >
    <EditText
        android:id="@+id/name"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="@string/reminder" />
    <Spinner
        android:id="@+id/dates"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_below="@id/name"
        android:layout_alignParentLeft="true"
        android:layout_toLeftOf="@+id/times" />
    <Spinner
        android:id="@id/times"
        android:layout_width="96dp"
        android:layout_height="wrap_content"
        android:layout_below="@id/name"
        android:layout_alignParentRight="true" />
    <Button
        android:layout_width="96dp"
        android:layout_height="wrap_content"
        android:layout_below="@id/times"
        android:layout_alignParentRight="true"
        android:text="@string/done" />
</RelativeLayout>
```

Aide : `@string/reminder` vaut « Reminder name » et `@string/done` vaut « Done ». Un
`Spinner` est une liste déroulante (dessine-le comme un champ avec un ▾).
Question bonus : pourquoi `layout_toLeftOf="@+id/times"` a-t-il un `+` ?

**Exercice 4.2 (annale 2, Q4, 5 points) :** dessine le résultat (l'interface d'une petite
annonce). Le sujet original a des balises mal fermées et des tailles manquantes : suppose
`wrap_content` partout où rien n'est indiqué.

```xml
<RelativeLayout android:layout_width="match_parent" android:layout_height="match_parent">
  <TextView android:id="@+id/tv_titre"
    android:layout_width="wrap_content" android:layout_height="wrap_content"
    android:layout_alignParentStart="true"
    android:layout_alignParentEnd="true"
    android:layout_alignParentTop="true"
    android:text="Vends trépied photographique"
    android:textAlignment="center"/>
  <RelativeLayout android:id="@+id/rl_middle"
    android:layout_width="wrap_content" android:layout_height="wrap_content"
    android:layout_alignParentStart="true"
    android:layout_alignParentEnd="true"
    android:layout_below="@id/tv_titre">
    <ImageView android:id="@+id/imageView_ann"
      android:layout_width="wrap_content" android:layout_height="160dp"
      android:layout_alignParentStart="true"
      android:layout_alignParentTop="true"
      android:layout_toStartOf="@id/tv_prix" />
    <TextView android:id="@+id/tv_prix"
      android:layout_alignParentEnd="true"
      android:layout_alignParentTop="true"
      android:text="300 €" />
    <TextView android:id="@+id/tv_date"
      android:layout_alignParentEnd="true"
      android:layout_below="@id/tv_prix"
      android:text="04-07-2019" />
  </RelativeLayout>
  <TextView android:id="@+id/tv_vendeur"
    android:layout_alignParentStart="true"
    android:layout_alignParentEnd="true"
    android:layout_below="@id/rl_middle"
    android:text="Pro16 - Pontoise" />
</RelativeLayout>
```

**Exercice 4.3 (dans l'autre sens) :** écris le XML d'un RelativeLayout qui donne ceci :

```
┌──────────────────────────────────────┐
│ [Photo 80dp x 80dp]  Awa Mensah      │   nom : à droite de la photo, en haut
│                      Licence 3       │   statut : sous le nom, aligné à gauche du nom
│                                      │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │            Se déconnecter        │ │   bouton toute la largeur, collé en BAS
│ └──────────────────────────────────┘ │
└──────────────────────────────────────┘
```

**Exercice 4.4 :** Cite cinq types de layout, avec une phrase sur chacun.

**Exercice 4.5 :** Écris **trois** façons différentes d'associer un clic à un bouton d'id
`envoyer`, qui appelle la méthode `envoyer()`.

**Exercice 4.6 (annale 2, Q2a) :** Que fait ce code ? Explique chaque argument.

```java
listview.setAdapter(new ArrayAdapter<>(MyActivity.this,
        android.R.layout.simple_list_item_1, myList));
```

Puis ajoute le code qui affiche un Toast avec l'élément touché.

**Exercice 4.7 :** Différence entre : `dp` et `sp` ; `padding` et `margin` ; `gravity` et
`layout_gravity` ; `invisible` et `gone`.

**Exercice 4.8 :** Trouve les **trois** erreurs de ce code.

```java
Toast.makeText(this, "Sauvegardé", 2000);
TextView t = findViewById(R.id.titre);
setContentView(R.layout.activity_main);
```
