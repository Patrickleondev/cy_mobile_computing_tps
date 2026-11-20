# 09. Les annales et l'examen blanc

> À faire **après** les chapitres 01 à 08. Corrigé : `10_corriges.md`, partie 09.

---

## 1. Les deux annales, en conditions réelles

Tu as déjà rencontré chaque question des annales dans les chapitres. Les refaire **à
froid**, une semaine plus tard, dit si c'est vraiment acquis.

**Conditions :** 2 heures, sur papier, **aucune note**, téléphone dans le sac. Comme le jour
J.

| Quand | Quoi |
|---|---|
| Séance 1 | `cours/Mobile-exam-publish.pdf` (annale 1, 20 points) |
| Séance 2 (un autre jour) | `cours/Mobile Exam Publish 2.pdf` (annale 2, 20 points) |
| Après chaque séance | corrige avec les parties 02 à 08 de `10_corriges.md`, note ton score, remplis le carnet d'erreurs |

**Où sont les corrections de chaque question :**

| Annale 1 | Corrigé | Annale 2 | Corrigé |
|---|---|---|---|
| 1.1 stockage | 5.1 | Q1 a, b, e, f | 1.1, 1.2, cours ch. 01 et 04 |
| 1.2 A démarre B | 2.2 | Q1 c, d | 4.5, 4.4 |
| 1.3 SMS | cours ch. 03, section 6 | Q1 g, h, j | 6.1 |
| Ex. 2 layout | 4.1 | Q1 i | 5.8 et cours ch. 05 |
| Ex. 3 téléphonie | 6.5 | Q2 a | 4.6 |
| Ex. 4 géocodage, GPS | 8.4 | Q2 b | cours ch. 05, section 3 |
| | | Q3 a, b, c, d | 8.3 |
| | | Q4 layout | 4.2 |

---

## 2. Examen blanc inédit (2 heures, 20 points)

Construit sur le modèle des deux annales, avec des questions que tu n'as **pas** encore
vues. Fais-le en dernier, juste avant les examens de décembre.

### Exercice 1 : questions de cours (6 points)

a. (1 pt) Un utilisateur est sur l'activité A de ton appli. Un appel arrive, il répond,
puis raccroche et revient sur A. Donne la séquence des callbacks de A.

b. (1 pt) Quelle est la différence entre un Service et un Thread ? Un Service évite-t-il,
à lui seul, de bloquer l'interface ?

c. (1 pt) Différence entre Intent explicite et Intent implicite. Donne un exemple de code
de chaque.

d. (1 pt) Cite deux permissions **normales** et trois permissions **dangereuses**. Quelle
différence de traitement depuis Android 6 ?

e. (1 pt) Qu'est-ce qu'un Content Provider ? Donne la structure générale de son URI.

f. (1 pt) Vrai ou faux ?
  1. `onPause()` est toujours suivi de `onStop()`.
  2. `ACTION_DIAL` nécessite la permission `CALL_PHONE`.
  3. Un `BroadcastReceiver` déclaré dans le manifeste peut recevoir une annonce même si
     l'appli n'est pas ouverte.
  4. `getLastKnownLocation()` peut renvoyer `null`.

### Exercice 2 : dessiner un layout (4 points)

Dessine le résultat (un lecteur de musique).

```xml
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:padding="8dp">
    <ImageView android:id="@+id/pochette"
        android:layout_width="160dp" android:layout_height="160dp"
        android:layout_alignParentTop="true"
        android:layout_centerHorizontal="true" />
    <TextView android:id="@+id/titre"
        android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:layout_below="@id/pochette"
        android:layout_centerHorizontal="true"
        android:text="Titre du morceau" />
    <TextView android:id="@+id/artiste"
        android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:layout_below="@id/titre"
        android:layout_alignLeft="@id/titre"
        android:text="Artiste" />
    <SeekBar android:id="@+id/barre"
        android:layout_width="match_parent" android:layout_height="wrap_content"
        android:layout_below="@id/artiste" />
    <TextView android:id="@+id/debut"
        android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:layout_below="@id/barre"
        android:layout_alignParentLeft="true"
        android:text="0:00" />
    <TextView android:id="@+id/fin"
        android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:layout_below="@id/barre"
        android:layout_alignParentRight="true"
        android:text="3:45" />
    <Button android:id="@+id/lecture"
        android:layout_width="120dp" android:layout_height="wrap_content"
        android:layout_alignParentBottom="true"
        android:layout_centerHorizontal="true"
        android:text="Lecture" />
    <Button android:id="@+id/precedent"
        android:layout_width="0dp" android:layout_height="wrap_content"
        android:layout_alignParentBottom="true"
        android:layout_alignParentLeft="true"
        android:layout_toLeftOf="@id/lecture"
        android:text="Précédent" />
    <Button android:id="@+id/suivant"
        android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:layout_alignParentBottom="true"
        android:layout_toRightOf="@id/lecture"
        android:text="Suivant" />
</RelativeLayout>
```

Un `SeekBar` est une barre de progression qu'on peut faire glisser : dessine-la comme une
ligne avec un rond.

### Exercice 3 : compléter du code (4 points)

Pendant un appel, quand on colle le téléphone à l'oreille, l'appli doit afficher « Proche »
dans le `TextView` `etat`, et « Loin » sinon. Le capteur de proximité renvoie une distance
en cm dans `values[0]` ; la valeur est « proche » si elle est **inférieure à la portée
maximale** du capteur. Complète les blancs.

```java
public class ProximiteActivity extends Activity implements /* (1) */ {

    private SensorManager sm;
    private Sensor proximite;
    private TextView etat;

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_proximite);
        etat = /* (2) */;
        sm = /* (3) */;
        proximite = /* (4) */;
    }

    @Override
    protected void onResume() {
        super.onResume();
        /* (5) */
    }

    @Override
    protected void onPause() {
        super.onPause();
        /* (6) */
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        /* (7) */
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) { }
}
```

### Exercice 4 : « Où est ma voiture ? » (6 points)

Une appli a deux boutons. **« J'ai garé ma voiture »** enregistre la position actuelle.
**« Où est-elle ? »** affiche l'adresse de la voiture et la distance qui t'en sépare.

a. (1 pt) Quelles permissions faut-il dans le manifeste, et pourquoi chacune ?

b. (1,5 pt) Écris le code du premier bouton : récupérer la dernière position connue du GPS
et l'enregistrer de façon à ce qu'elle survive à la fermeture de l'appli **et** au
redémarrage du téléphone. Justifie le moyen de stockage choisi.

c. (2 pts) Écris le code du second bouton : relire la position enregistrée, la traduire en
adresse, et l'afficher dans un Toast. Comment s'appelle ce processus ?

d. (1,5 pt) L'appli veut afficher la distance **en continu** pendant que l'utilisateur
marche vers sa voiture. Écris le listener et son enregistrement (mise à jour toutes les 5
secondes ou tous les 10 mètres). Dans quels callbacks de l'activité l'enregistrer et le
retirer ? Rappel : `location.distanceTo(autre)` renvoie une distance en mètres.
