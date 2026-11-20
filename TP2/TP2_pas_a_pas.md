# TP2 (da20-tp2) : réparer le projet, puis le comprendre de bout en bout

## 0. Avant de tester et de soumettre (vérifié le 01/11/2026)

### Réponse courte : pas encore

Le projet **compile** (`BUILD SUCCESSFUL`, état du 23/10), et l'application fait presque tout ce que
demande le sujet `da20-tp2 (1).pdf`. Mais **trois écarts avec le document** sont à corriger, et
il reste un point à régler avant de rendre quoi que ce soit.

**Le point à régler d'abord.** Les 7 fichiers `.java` ont tous la date du 23/10 à 08:56,
l'heure du dézippage : **personne ne les a modifiés**. C'est le projet du prof de 2020 (paquet
`com.delkappa.manos`), déjà complet. Si le rendu doit être **ton** travail, rendre ce dossier tel quel,
c'est rendre le code du prof. Le sujet dit « modify and extend the application you developed during
TP1 » : l'attendu est donc ton projet du TP1, prolongé. Rien dans tes fichiers ne dit ce que le prof
demande comme rendu (code ? APK ? captures ? sur Moodle ?). **Relis la consigne de rendu sur Moodle**
ou demande-la, avant de soumettre.

### Le sujet, point par point, face au code

| Demande du sujet | Dans le code | Verdict |
|---|---|---|
| **1.** Sauver les infos de MainActivity, et ouvrir directement SecondActivity au lancement suivant | `SharedPreferences` + test dans `onCreate` de `MainActivity` | conforme |
| **2.1** Un Service qui télécharge le fichier | `DownloadService extends IntentService` | conforme |
| **2.1** Une Activity qui communique avec l'IntentService par un BroadcastReceiver | `ThirdActivity` + `eventReceiver` + `LocalBroadcastManager` | conforme |
| **2.1** Le fichier est à l'adresse **donnée dans le sujet** | `URL_PATH = "https://goo.gl/WQQfyP"` : lien mort | **à corriger (1)** |
| **2.1** Sauver dans `/storage/sdcard/Download` | `Environment.getExternalStoragePublicDirectory(DIRECTORY_DOWNLOADS)` : c'est ce dossier (sur les téléphones récents, il s'appelle `/storage/emulated/0/Download`) | conforme |
| **2.1** « Remember to specify the system permissions! » | `INTERNET` et `WRITE_EXTERNAL_STORAGE` dans le manifeste, et la demande **à l'exécution** dans `ThirdActivity` | conforme |
| **2.2** Découper chaque ligne sur `;;` et insérer dans SQLite | `parseEvents()` puis `db.addRow(...)` | conforme, mais **bug (3)** à la lecture du fichier |
| **2.2** Une table **nommée `TABLE_EVENTS`**, colonnes **`ID`, `NAME`, `LAT`, `LNG`, `TYPE`** | table nommée `event`, colonnes `id`, `name`, `latitude`, `longitude`, `type` | **à corriger (2)** |
| **3.1.1** Afficher le contenu de la base dans la console avec `Log` | `printEvents()` | conforme (il écrit longitude puis latitude : inverse-les si tu veux) |
| **3.1.2** Les noms dans une `ListView` de ThirdActivity ; un clic montre coordonnées et type | `listEvents()` + `EventActivity` | conforme |

### Les 3 corrections (fais-les toi-même, dans Android Studio)

**(1) L'adresse du fichier.** Le lien du sujet **marche** : je l'ai testé le 01/11, il renvoie 15
lignes, de `EVENT1;;48.863429;;2.388223;;TYPE3` à `EVENT15;;49.046780;;2.044665;;TYPE3`. Dans
`ThirdActivity.java`, remplace la valeur de `URL_PATH` par l'adresse écrite dans le sujet (section 2.1).
Recopie-la depuis le PDF.

Google répond d'abord « 303 See Other », puis envoie vers `drive.usercontent.google.com`.
`HttpURLConnection` suit ce renvoi tout seul, parce qu'il reste en `https` (il ne suit pas un renvoi de
`http` vers `https`). Le serveur local de la partie B ne sert plus que de **plan B**, si Google bloque un
jour le lien.

**(2) Les noms de la table.** Dans `DatabaseHandler.java`, ne touche pas aux noms des **constantes**
(`TABLE_EVENTS`, `KEY_ID`…), le reste du code les utilise. Change seulement leurs **valeurs** entre
guillemets, pour qu'elles collent au sujet. Question à te poser : pourquoi suffit-il de changer 6 chaînes
pour que `CREATE TABLE`, `insert` et `SELECT` suivent ?

Piège : `onCreate` de `SQLiteOpenHelper` ne tourne **qu'une fois**, quand la base n'existe pas encore. Si
l'application a déjà tourné sur ton émulateur, l'ancienne table `event` y est toujours. Deux solutions :
désinstaller l'application (la base est dans son dossier privé, elle part avec), ou passer
`DATABASE_VERSION` à 2, ce qui appelle `onUpgrade` (qui supprime puis recrée la table).

**(3) La boucle de copie** de `DownloadService` : c'est le bug de la partie D, corrigé en E.7. Écris-le
d'abord sans regarder.

### Tester, dans cet ordre

1. **Partir d'un état propre.** Désinstalle l'application de l'émulateur (ça efface les préférences et
   la base). Supprime aussi `Download/events.txt` s'il existe : il est hors du dossier de l'application.
   Pour ça, utilise *View > Tool Windows > Device Explorer*, `sdcard/Download`, clic droit > *Delete*.
   Sinon, décommente une fois le bloc « Clear the events » de `ThirdActivity`.
2. **Lancer** (bouton ▶, émulateur API 30 à 34, avec Internet). Écran 1 : laisse le nom vide et valide.
   Le message rouge « Name is required » doit s'afficher. Remplis ensuite nom et email.
3. **Écran 2** : ton nom s'affiche. Dans Logcat, filtre `SecondActivity` : ton email apparaît.
4. **Écran 3** : accepte la permission. Dans Logcat, filtre `ThirdActivity|DownloadService`. Tu dois
   voir dans l'ordre `Connecting...`, `Downloading...`, `Done!`, `Event received...`, `Parsing...`,
   `Printing...`, puis **15 lignes** `ID: 1, Name: EVENT1, …`, puis `Listing...`.
5. **La liste** affiche EVENT1 à EVENT15. Clique sur EVENT1 : `48.863429, 2.388223` et `TYPE3`.
6. **Relance l'application** (ferme-la depuis les applications récentes, puis rouvre-la). Elle doit
   s'ouvrir **directement sur l'écran 2** : c'est la partie 1 du sujet.
7. **Refuser la permission** (après une nouvelle désinstallation) : le Toast « Permission denied »
   s'affiche, et la liste reste vide.

Si les 7 étapes donnent ce résultat, et que la question du rendu est réglée, tu peux soumettre.

Plan : **0.** le bilan face au sujet, et comment tester avant de soumettre. **A.** pourquoi le projet ne se synchronisait pas, et la résolution complète. **B.** le deuxième piège,
le téléchargement qui ne marche plus. **C.** ce que fait l'application, écran par écran. **D.** un bug
à corriger toi-même. **E.** les questions pour vérifier que tu maîtrises.

---

## A. Le projet ne se synchronisait pas : ce qui s'est passé, et la résolution

### Trois étages, chacun dépend de celui du dessous

| Étage | Rôle | Où c'est écrit |
|---|---|---|
| **JDK** (Java) | fait **tourner** Gradle | Studio : *Settings > Build Tools > Gradle > Gradle JDK* (fichier `.idea/gradle.xml`) |
| **Gradle** | le moteur de construction : il lit les `build.gradle` et lance les tâches | `gradle/wrapper/gradle-wrapper.properties`, ligne `distributionUrl` |
| **Plugin Android (AGP)** | apprend à Gradle à fabriquer un APK | `build.gradle` **racine**, ligne `classpath 'com.android.tools.build:gradle:…'` |

Et au-dessus des trois, **Android Studio lui-même**, qui n'accepte que les plugins Android assez récents.

### L'état final (ce qui marche)

| Étage | Projet du prof (2020) | **Maintenant** | Pourquoi cette version |
|---|---|---|---|
| Plugin Android | 4.1.0 | **7.4.2** | Studio 2026 exige **7.2.0 au minimum** ; 7.4.2 est la dernière 7.x |
| Gradle | 6.5 | **7.5.1** | AGP 7.4 demande Gradle **7.5 au moins** |
| JDK | (8) | **17** | AGP 7.x a besoin de Java **11 ou plus** ; Gradle 7.5 tourne jusqu'à Java **18** |
| Dépôt de bibliothèques | `jcenter()` | **`mavenCentral()`** | JCenter ne reçoit plus de nouvelles versions depuis 2021 |
| `buildToolsVersion '29.0.2'` | présent | **supprimé** | AGP 7.4 l'ignorait (minimum 30.0.3) et l'écrivait en avertissement |

Le JDK 17 est dans `C:\Users\User\.jdks\temurin-17.0.20.1`. Le Gradle JDK du projet est
**GRADLE_LOCAL_JAVA_HOME** : cette ligne de la liste lit le chemin écrit dans `.gradle/config.properties`
(`java.home=…temurin-17.0.20.1`).

Vérifié sur le projet : `gradlew assembleDebug` → **BUILD SUCCESSFUL**. Deux avertissements jaunes
restent, sans gravité : le `package` du manifeste « deprecated » (en AGP 8 il faudra un `namespace`
dans `app/build.gradle`), et les fichiers `package.xml` du SDK plus récents que ce plugin.

### Les 3 obstacles, dans l'ordre où on les a rencontrés

**Obstacle 1 : « Incompatible Gradle JVM version ».**

> The project's Gradle version 6.5 is incompatible with the Gradle JVM version 25

Studio lançait Gradle 6.5 avec Java 25 (et le projet était même réglé sur `openjdk-27`). Gradle 6.5
date de 2020 : il ne connaît que **Java 8 à 14**. Premier essai : Gradle JDK = **1.8** (Dragonwell, déjà
installé). En ligne de commande, le projet compilait alors sans changer une ligne.

**Obstacle 2 : « Minimum supported version is AGP 7.2.0 ».**

Avec Java 8, la JVM était acceptée, mais **Studio** a refusé le plugin 4.1.0. Le message était coupé à
l'écran (« Mini… ») : la fin, avec le chiffre, se lisait dans le journal de Studio (*Help > Show Log in
Explorer*, fichier `idea.log`). **Changer le JDK ne pouvait plus suffire** : il fallait mettre le projet à
jour, et chaque étage a suivi le précédent (tableau de l'état final).

**Obstacle 3 : « toujours la même erreur ».**

Le Sync suivant a redonné exactement la même erreur, parce que **les fichiers n'avaient pas été
modifiés** : `build.gradle` disait encore 4.1.0 (dernière modification à 08:56, l'heure du
dézippage). Le bouton **Try Again** relance la lecture, il ne change rien. Les fichiers corrigés, le
Sync passe.

### Les 4 leçons à retenir

1. **Lire le message en entier.** La phrase utile (« Minimum supported version is AGP 7.2.0 ») était
   coupée. Élargis le panneau, ou ouvre le journal.
2. **Il y a deux Java différents.** `gradlew --version` dans le terminal affichait `JVM: 1.8.0_461` :
   c'est le Java du **terminal** (la variable `JAVA_HOME` de Windows). Le **Sync de Studio** utilise un
   autre Java, celui du champ *Gradle JDK*. Le terminal peut marcher pendant que Studio échoue.
3. **Dans la liste Gradle JDK, lis le numéro en gris, pas le nom.** « JAVA_HOME » y pointait vers Java 25
   (le Java de Studio), pas vers celui du terminal. Et **« 1.8 » veut dire Java 8** (ancienne
   numérotation ; à partir de Java 9, on écrit 9, 10… 25).
4. **Le Sync ne fait que lire les fichiers.** Après une modification d'un fichier Gradle, le bandeau
   **« Gradle files have changed since last project sync » → Sync Now** doit apparaître. S'il
   n'apparaît pas, tu n'as pas modifié le bon fichier (vue **Project**, pas **Android** ; le
   `build.gradle` **racine**, pas celui de `app/`).

### La méthode, pour résoudre seul la prochaine fois

Ce type d'erreur (« incompatible », « unsupported class file major version », « requires Java 17 »,
« minimum supported version »…) se résout toujours avec les mêmes 5 étapes :

| # | Étape | Ce que tu fais | Dans ce TP |
|---|---|---|---|
| 1 | **Lire le message en entier et y trouver les versions en conflit** | souligne les numéros | « Gradle 6.5 » contre « JVM 25 », puis « AGP 4.1.0 » contre « minimum 7.2.0 » |
| 2 | **Trouver où chaque version est déclarée** | voir le tableau des trois étages | |
| 3 | **Chercher la table de compatibilité officielle** | « gradle java compatibility » (docs.gradle.org), « AGP gradle JDK compatibility » (developer.android.com) | Gradle 6.5 : Java 8 à 14 ; AGP 7.4 : Gradle 7.5+, Java 11+ |
| 4 | **Choisir le plus petit changement** | d'abord changer l'outil (le JDK) ; si l'IDE refuse le plugin, mettre à jour le projet, étage par étage | JDK 8, puis AGP 7.4.2 + Gradle 7.5.1 + JDK 17 |
| 5 | **Vérifier, puis synchroniser** | `.\gradlew --version` (attention : Java du terminal), puis **Sync Now** | |

**Et si le bon JDK n'est pas installé ?** Dans la liste *Gradle JDK*, choisis **Download JDK…**, puis
la version demandée par la table de l'étape 3. Studio la range dans `C:\Users\User\.jdks\`.

**Les correspondances à retenir** (de l'étape 3, en résumé) :

| Plugin Android (AGP) | Gradle | JDK pour faire tourner Gradle |
|---|---|---|
| 4.x | 6.x | **8** (11 accepté) |
| 7.x | 7.x | **11 à 17** |
| 8.x | 8.x | **17** |
| 9.x | 9.x | **17 ou plus** |

Le message **« New Minor Gradle Version Available »** n'est qu'une information : ignore-le.

---

## B. Le deuxième piège : le fichier d'événements n'existe plus

(Plan B seulement : le lien du **sujet** marche, voir la correction (1) de la partie 0. Le lien mort est
celui du **code** du prof.)

Le 3ᵉ écran télécharge une liste d'événements depuis :

```java
public static final String URL_PATH = "https://goo.gl/WQQfyP";
```

J'ai testé ce lien : il redirige vers un fichier Google Drive **supprimé (erreur 404)**. Résultat dans
l'application : `getInputStream()` lève une exception, elle est attrapée et seulement affichée dans
Logcat, aucun fichier n'est écrit, aucun broadcast n'est envoyé. **La liste reste vide, sans aucun
message à l'écran.** C'est le genre de bug qu'on cherche une heure.

### La solution : servir le fichier depuis ton PC

J'ai préparé `da20-tp2/serveur_local/events.txt` (5 événements de test **inventés**, au format attendu) :

```
Concert de rentree;;49.0387;;2.0782;;concert
nom            ;;latitude;;longitude;;type
```

**1.** Dans un terminal, lance un petit serveur web dans ce dossier :

```
cd D:\All\Licence_Cergy\Semestre_5\07_Mineure_Mobile_Computing\da20-tp2\serveur_local
python -m http.server 8000
```

Vérifie dans ton navigateur : `http://localhost:8000/events.txt` doit afficher les 5 lignes.

**2.** Dans `ThirdActivity.java`, change **une ligne** (fais-le toi-même) :

```java
public static final String URL_PATH = "http://10.0.2.2:8000/events.txt";
```

**Pourquoi 10.0.2.2 et pas localhost ?** Dans l'émulateur, `localhost` désigne **l'émulateur
lui-même**. `10.0.2.2` est l'adresse spéciale qui veut dire « le PC qui fait tourner l'émulateur ». Sur
un vrai téléphone, mets plutôt l'adresse IP de ton PC (`ipconfig`), les deux sur le même Wi-Fi.

**Pourquoi `http` est accepté ?** Depuis Android 9, le HTTP non chiffré est interdit par défaut,
**mais seulement pour les applications qui ciblent l'API 28 ou plus**. Ici `targetSdkVersion 26` : il
est encore autorisé.

**3. Si tu as déjà lancé l'application une fois**, un `events.txt` (vide ou faux) existe peut-être déjà
dans *Downloads* : l'application croit alors qu'elle a déjà téléchargé, et ne recommence pas. Décommente
une fois le bloc « Clear the events for testing purposes » dans `onCreate()` de `ThirdActivity`, lance,
puis recommente-le. Désinstaller l'application ne suffit pas : le fichier est dans *Downloads*, pas dans
le dossier de l'application.

### Il te faut un émulateur

Aucun appareil virtuel n'est créé sur ton PC. Dans Studio : **Tools > Device Manager > + > Create
Virtual Device**, un Pixel avec une image **API 30 à 34**. Évite la toute dernière version d'Android
pour ce vieux projet.

---

## C. Ce que fait l'application : le parcours complet

```
MainActivity ──submit()──► SecondActivity ──next()──► ThirdActivity ──clic──► EventActivity
 formulaire                 affiche le nom             liste d'événements      détail d'un événement
 nom + email                                           (service + SQLite)
     │
     └─ déjà inscrit ? ──► saute directement à SecondActivity
```

### 1. `MainActivity` : le formulaire, et SharedPreferences

| Code | Ce qu'il fait | Notion du cours |
|---|---|---|
| `PreferenceManager.getDefaultSharedPreferences(...)` | ouvre un petit fichier clé → valeur, propre à l'application | stockage simple (cours 05, données) |
| test `getString(user_name, "")` non vide **dans `onCreate`** | si l'utilisateur s'est déjà inscrit, on **ne montre pas** le formulaire | |
| `finish()` puis `startActivity(i)` | ferme cet écran **et** ouvre le suivant : Retour ne ramènera pas au formulaire | cycle de vie, pile d'activités |
| `android:onClick="submit"` (XML) → `public void submit(View view)` | le bouton appelle la méthode **par son nom** : signature obligatoire `public void nom(View v)` | interface |
| `setError("Name is required")` | message d'erreur rouge sur le champ | |
| `editor.putString(...)` puis `commit()` | enregistre (`commit` attend la fin de l'écriture ; `apply` le fait en arrière-plan) | |

### 2. `SecondActivity` : relire les préférences

Elle **relit** le nom dans SharedPreferences (pas dans l'Intent : l'Intent ne transporte rien ici) et
l'affiche. L'email part dans **Logcat** (`Log.d`) : regarde-le dans l'onglet Logcat, filtre
`SecondActivity`.

`next()` ajoute deux drapeaux : `FLAG_ACTIVITY_CLEAR_TASK | FLAG_ACTIVITY_NEW_TASK`, qui **vident toute
la pile** avant d'ouvrir ThirdActivity. Depuis le 3ᵉ écran, Retour **quitte** l'application. C'est
voulu : on ne revient pas au formulaire.

### 3. `ThirdActivity` : le cœur du TP

C'est une chaîne de 6 étapes. Chaque étape déclenche la suivante :

| # | Étape | Code | Notion |
|---|---|---|---|
| 1 | Demander la permission d'écrire | `checkSelfPermission` → sinon `requestPermissions` → réponse dans `onRequestPermissionsResult` | permission **dangereuse** = demandée **à l'exécution** (depuis Android 6), pas seulement dans le manifeste |
| 2 | Lancer le téléchargement **hors de l'écran** | `startService(new Intent(this, DownloadService.class))` avec l'URL en extra | **Service** (cours 04) |
| 3 | Télécharger dans un fil séparé | `DownloadService extends IntentService` : `onHandleIntent` tourne **dans un thread à part** | réseau interdit sur le thread principal (`NetworkOnMainThreadException`) |
| 4 | Prévenir l'écran que c'est fini | `LocalBroadcastManager...sendBroadcast(new Intent("filter"))` | **Broadcast** (cours 04) |
| 5 | Recevoir le message | `eventReceiver`, inscrit dans `onResume`, désinscrit dans `onPause` | on n'écoute que quand l'écran est visible |
| 6 | Lire, stocker, afficher | `parseEvents()` découpe chaque ligne sur `;;` → `db.addRow()` dans **SQLite**, puis `listEvents()` remplit la `ListView` avec un `ArrayAdapter` | base locale (cours 05), listes |

### 4. `DatabaseHandler` : SQLite

`extends SQLiteOpenHelper` : `onCreate` crée la table **une seule fois** (premier accès), `onUpgrade` est
appelé si `DATABASE_VERSION` augmente. Table `event(id, name, latitude, longitude, type)`.
`getWritableDatabase()`, `insert`, `rawQuery("SELECT * …")` + `Cursor` qu'on parcourt avec
`moveToFirst` / `moveToNext`.

### 5. `EventActivity` : passer un objet entre écrans

`Event implements Serializable` : on peut le mettre **entier** dans l'Intent
(`putExtra(EVENT_EXTRA, events.get(position))`) et le récupérer avec `getSerializableExtra`. C'est
l'alternative à « passer seulement un identifiant ».

---

## D. Un vrai bug à corriger toi-même

Dans `DownloadService.onHandleIntent` :

```java
byte data[] = new byte[4096];
while (input.read(data) != -1) {
    output.write(data);
}
```

**Indice :** `read(data)` renvoie **le nombre d'octets lus**, qui peut être plus petit que 4096 (le
dernier morceau, par exemple). Que contient alors la fin de `data` ? Qu'est-ce que `write(data)` écrit
dans le fichier ?

Écris la correction, puis compare avec le corrigé en E. Pourquoi l'application « marche quand même » ?
Regarde la condition `line.contains(";;")` de `parseEvents()`.

---

## E. Vérifie que tu maîtrises (réponds avant de lire le corrigé)

1. Quels sont les trois étages de la construction ? Pourquoi changer le JDK n'a pas suffi ?
2. Pourquoi `10.0.2.2` et pas `localhost` ?
3. Qu'est-ce qui empêche le formulaire de réapparaître au deuxième lancement ?
4. Pourquoi le téléchargement est-il dans un Service, et pas directement dans `onCreate` ?
5. Pourquoi le receiver est-il inscrit dans `onResume` et désinscrit dans `onPause` ?
6. Que se passe-t-il si l'utilisateur refuse la permission ?
7. Corrige la boucle de la partie D.

### Corrigé

1. JDK (fait tourner Gradle), Gradle (moteur), plugin Android (fabrique l'APK). D'abord le JDK était
   trop récent pour Gradle 6.5 ; mais ensuite **Studio** refusait le plugin 4.1.0 (minimum 7.2.0) : il a
   fallu monter le plugin, donc Gradle, donc le JDK.
2. Dans l'émulateur, `localhost` est l'émulateur lui-même ; `10.0.2.2` est le PC hôte.
3. Le test dans `onCreate` de MainActivity : si `user_name` existe dans SharedPreferences, `finish()` et
   on passe à SecondActivity.
4. Le réseau est interdit sur le thread principal, et un téléchargement long figerait l'écran (ANR).
   `IntentService` exécute `onHandleIntent` dans un thread à part et s'arrête seul à la fin.
5. Pour ne recevoir le message que quand l'écran est visible, et ne pas garder un receiver vers une
   activité détruite (fuite mémoire).
6. `onRequestPermissionsResult` reçoit `PERMISSION_DENIED` : un Toast « Permission denied », et rien
   n'est téléchargé.
7. ```java
   int n;
   while ((n = input.read(data)) != -1) {
       output.write(data, 0, n);
   }
   ```
   Avant la correction, le dernier `write` recopiait les restes du tour précédent après la fin réelle
   du fichier. Ça « marchait » parce que `parseEvents()` s'arrête à la première ligne sans `;;`.

### Pour aller plus loin (remarque à l'oral)

Ce code date de 2017-2020 : `IntentService`, `LocalBroadcastManager` et
`PreferenceManager.getDefaultSharedPreferences` sont aujourd'hui **dépréciés**. Aujourd'hui, on utilise
**WorkManager** pour le travail en arrière-plan, **LiveData / Flow** pour prévenir l'écran, et
**DataStore** à la place de SharedPreferences. Les principes, eux, n'ont pas changé : travail hors du
thread principal, message vers l'écran, stockage local.
