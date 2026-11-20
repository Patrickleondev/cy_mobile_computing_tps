# Mobile Computing - CY Cergy Paris Université (L3 Informatique, 2026-2027)

TPs et supports de cours de la mineure Mobile Computing. Projets Android en Java
(Android Studio, minSdk 24, targetSdk 37). Chaque TP repart du projet du TP précédent.

| TP | Sujet | Projet | Ce qui est ajouté |
| --- | --- | --- | --- |
| [TP1](TP1) | Activités, Intents | `projet_TP1Intents` | formulaire, passage d'extras entre écrans |
| [TP2](TP2) | Données, services | `projet_TP2Events` | SharedPreferences, téléchargement en service, base SQLite, liste |
| [TP3](TP3) | Localisation, cartes | `projet_TP3Maps` | GPS, carte osmdroid, géocodage, ajout d'événement |
| [TP4](TP4) | Téléphonie | `projet_TP4Calls` | appels d'urgence, états d'appel, envoi et réception de SMS |
| [TP5](TP5) | Multimédia | `projet_TP5Photos` | photo et vidéo d'un événement (FileProvider), galerie |

Dans chaque dossier : le sujet (`sujet_tpN.pdf`), le projet Android et le rendu (rapport, captures, APK).

**Guides à suivre** : `TPn_pas_a_pas_complet.md` / `.pdf` (TP5 : `TP5_pas_a_pas.md`). Chaque fichier
nouveau ou modifié y est donné **en entier**, avec les lignes ajoutées depuis le TP précédent,
pourquoi, et pourquoi à cet endroit. Ils sont générés depuis les projets par `outils/generer_guides.py`.
Les anciens guides à trous (`TPn_pas_a_pas.md`) sont gardés pour mémoire.

Pour ouvrir un projet : Android Studio, **File > Open**, choisir le dossier `projet_...`.

`cours/` : supports du cours (`supports/`), fiches de révision (`fiches/`), photos du tableau.
