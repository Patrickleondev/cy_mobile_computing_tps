# Mobile Computing : le cours pas à pas, depuis zéro

> Construit depuis les 6 cours de Dimitris Kotzinos (`cours/`), le TP1 et les **deux sujets
> d'examen** (`Mobile-exam-publish.pdf`, `Mobile Exam Publish 2.pdf`).
> Les réponses aux exercices sont dans `10_corriges.md`. Ne l'ouvre qu'après avoir écrit.

---

## 1. Comment tu es noté, et ce que ça change pour réviser

| Part | Quoi | Conséquence |
|---|---|---|
| **50 %** | examen écrit final : *concepts, architecture, lecture de code* | **sur papier, sans ordinateur, sans IA**. Tu dois écrire du Java Android **de mémoire** |
| **50 %** | projet en binôme (proposition, démo, code, rapport) | tu dois pouvoir **expliquer chaque ligne** à l'oral, même celles écrites avec une IA |

Le prof le dit lui-même (cours 1, diapo 11) : *« Exam: no AI tools, no devices [...] you will read
and write code on paper. »*

Donc réviser = **écrire à la main**. Lire le cours ne suffit pas : à l'examen, personne ne
complète `getSystemService(...)` à ta place.

---

## 2. Ce qui tombe : l'analyse des deux annales

J'ai classé chaque question des deux sujets. Le même noyau revient :

| Thème | Annale 1 | Annale 2 | Points | Chapitre |
|---|---|---|---|---|
| Questions de cours (vrai/faux, définitions, citer) | 1.1 | Q1 (10 questions), Q2 | ~9 | 01 à 06 |
| **Cycle de vie** (séquence A démarre B) | 1.2 | | 2 | **02** |
| **Manifeste et permissions** | 1.3 (SMS) | Q2b, Q3d | ~4 | **03** |
| **Dessiner un RelativeLayout** | Ex. 2 | Q4 | **3,5 + 5** | **04** |
| **Stockage** (lister les moyens, insérer en SQLite) | 1.1 | Q3c | ~4 | **05** |
| Services, BroadcastReceiver, démarrage | | Q1 g, h, j | ~1,5 | **06** |
| **Téléphonie** (PhoneStateListener à compléter) | Ex. 3 | | 4,5 | **06** |
| **Localisation** (GPS, géocodage inverse, onLocationChanged) | Ex. 4 | Q3 a, b | **6 + 4** | **08** |

**Les trois blocs qui rapportent le plus :** la localisation (chapitre 08), le dessin de
layout (chapitre 04) et les permissions du manifeste (chapitre 03). Si tu manques de temps,
ce sont les trois à blinder.

**Ce qui n'est pas tombé dans les annales :** les capteurs (chapitre 07) et les cartes
Google Maps. Le prof peut changer, donc on les voit, mais plus vite.

---

## 3. Un point important sur les cours

Le cours 1 et le cours 2 sont à jour (2026). Les cours 3 à 6 sont **anciens** (2013) : ils
utilisent `AsyncTask`, `MapActivity`, `fill_parent`, `onStart()` pour les services, des
permissions déclarées sans demande à l'exécution...

**Ce que ça change pour toi :** les annales sont écrites dans ce style ancien. À l'examen,
tu écris le code **comme dans les cours**, c'est ce que le prof attend. Quand une API est
obsolète, je le signale avec 🕰️, pour que tu saches ce qui a changé (utile pour le projet et
pour l'oral), mais ce n'est pas à apprendre en priorité.

---

## 4. Le parcours

Fais les chapitres **dans l'ordre** : chacun s'appuie sur le précédent.

| # | Fichier | Contenu | Temps |
|---|---|---|---|
| 01 | `01_bases.md` | qu'est-ce qu'Android, la pile logicielle, les 4 composants, le manifeste, le projet | 1 h 30 |
| 02 | `02_activites.md` | le cycle de vie, les séquences à connaître par cœur, sauver l'état | 1 h 30 |
| 03 | `03_intents_manifeste.md` | les Intents, les filtres, **le manifeste et les permissions** | 1 h 30 |
| 04 | `04_interface.md` | Views, layouts, unités, **la méthode pour dessiner un RelativeLayout**, listeners, listes | 2 h |
| 05 | `05_donnees.md` | SharedPreferences, Bundle, fichiers, **SQLite**, Content Provider | 2 h |
| 06 | `06_services_broadcast.md` | Services, threads, BroadcastReceiver, démarrage au boot, **téléphonie**, WakeLock | 1 h 30 |
| 07 | `07_capteurs.md` | SensorManager, types de capteurs, listener, vibreur | 1 h |
| 08 | `08_localisation.md` | **LocationManager, GPS, géocodage**, cartes | 2 h |
| 09 | `09_annales.md` | les deux sujets, en conditions réelles | 2 × 2 h |

Ton `TP1_pas_a_pas.md` (dossier du dessus) reste valable : il complète les chapitres 02 à
04 avec la pratique dans Android Studio.

Soit environ **15 h de travail**, plus les deux annales. Réparti sur les semaines qui
restent avant les examens de décembre (du 14 au 18), ça fait moins d'une heure par jour.

---

## 5. La méthode, pour chaque chapitre

1. **Lis** une section. Elle commence toujours par *pourquoi* la chose existe : si tu sais à
   quel problème elle répond, tu retrouves le code tout seul.
2. **Ferme le fichier** et fais la partie « À toi » **sur papier**, comme à l'examen.
3. **Corrige** avec `10_corriges.md`. Chaque erreur va dans ton carnet d'erreurs, au format
   « ce que j'ai écrit / la bonne réponse / pourquoi ».
4. **Le lendemain**, avant le chapitre suivant, réécris de mémoire les encadrés « À savoir
   écrire par cœur » du chapitre de la veille. C'est ce rappel espacé qui fixe le code.

**La règle d'or pour le code à l'examen :** un code presque juste qui montre que tu as
compris (le bon service système, le bon listener, la bonne permission) rapporte la majorité
des points. Une parenthèse oubliée ne coûte presque rien. Un `LocationManager` remplacé par
un `SensorManager`, si.
