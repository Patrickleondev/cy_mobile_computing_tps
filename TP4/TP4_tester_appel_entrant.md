# TP4 : tester un appel entrant avec `adb emu gsm`

Un émulateur n'a pas de vraie carte SIM : personne ne peut l'appeler. La console de l'émulateur
**simule** un réseau téléphonique, et ces trois commandes jouent le rôle de quelqu'un qui appelle :

| Commande | Ce qu'elle simule | État reçu par ton appli | Toast attendu |
|---|---|---|---|
| `adb emu gsm call 0612345678` | le 06 12 34 56 78 t'appelle : le téléphone sonne | `CALL_STATE_RINGING` | « Appel : le telephone sonne » |
| `adb emu gsm accept 0612345678` | l'appel est décroché | `CALL_STATE_OFFHOOK` | « Appel : en communication » |
| `adb emu gsm cancel 0612345678` | l'appelant raccroche | `CALL_STATE_IDLE` | « Appel : termine » |

**Le numéro doit être exactement le même dans les trois commandes.** `accept` et `cancel` désignent
l'appel par son numéro : avec `061234567` (un chiffre en moins), l'émulateur ne trouve pas l'appel
et rien ne se passe.

---

## 1. Préparer l'appli (sinon aucun Toast ne s'affiche)

Dans ton `EventActivity`, l'écoute des appels démarre dans `call()`, au premier appui sur le
bouton d'appel (c'est là que `ecouterAppels()` est appelée), **pas** dans `onCreate`. Donc :

1. Lance l'appli sur l'émulateur, ouvre la liste, puis un événement.
2. Appuie **une fois** sur le bouton d'appel (« Appeler le 18 »…) et accepte les permissions
   (téléphone, et notifications sur Android 13+).
3. L'appel sortant part : raccroche (bouton rouge).
4. **Reste sur l'écran de l'événement.** L'écoute vit jusqu'à `onDestroy` : si tu reviens à la
   liste (bouton Retour), l'écran est détruit et l'écoute s'arrête.

Maintenant ton appli écoute : tu peux simuler l'appel entrant.

## 2. Ouvrir un terminal où `adb` fonctionne

`adb` est dans le SDK Android : `C:\Users\User\AppData\Local\Android\Sdk\platform-tools\adb.exe`.

- **Le plus simple :** le terminal intégré d'Android Studio (onglet *Terminal* en bas). Si
  `adb` n'est pas reconnu, utilise le chemin complet ci-dessous.
- **PowerShell** (le `&` est obligatoire devant un chemin entre guillemets) :

```powershell
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" devices
```

`devices` doit afficher une ligne `emulator-5554   device`. Si la liste est vide, l'émulateur
n'est pas démarré.

## 3. Lancer les trois commandes, une par une

En PowerShell, garde le chemin dans une variable pour ne pas le retaper :

```powershell
$adb = "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe"
& $adb emu gsm call 0612345678
```

→ l'émulateur sonne, l'écran d'appel entrant apparaît, et ton Toast « Appel : le telephone sonne ».
Attends 2 ou 3 secondes, puis :

```powershell
& $adb emu gsm accept 0612345678
```

→ l'appel est en cours (le chrono tourne), Toast « Appel : en communication ». Puis :

```powershell
& $adb emu gsm cancel 0612345678
```

→ l'appel se termine, Toast « Appel : termine ».

Chaque commande doit répondre `OK`. Laisse passer quelques secondes entre deux commandes : un Toast
dure environ 2 secondes, et ils s'affichent l'un après l'autre.

## 4. Sans terminal : les Extended controls

Dans la barre de l'émulateur, **⋯ (Extended controls) > Phone** :

1. tape `0612345678` dans *From*, puis **Call device** → RINGING ;
2. décroche sur l'écran de l'émulateur (bouton vert) → OFFHOOK ;
3. **End call** → IDLE.

C'est la même simulation, avec des boutons.

## 5. Quand ça ne marche pas

| Ce que tu vois | Cause | Solution |
|---|---|---|
| `adb` n'est pas reconnu | `platform-tools` n'est pas dans le PATH | chemin complet (partie 2) ou terminal d'Android Studio |
| `error: more than one device/emulator` | un téléphone branché ou deux émulateurs | `& $adb -s emulator-5554 emu gsm call 0612345678` |
| `KO: ...` ou rien après `accept` / `cancel` | numéro différent de celui du `call` | le même numéro, chiffre pour chiffre |
| Ça sonne mais aucun Toast | l'écoute n'a pas démarré : tu n'as pas appuyé sur le bouton d'appel, ou tu as quitté l'écran de l'événement | partie 1 |
| Aucun Toast pendant que l'écran d'appel est devant | permission des notifications refusée (Android 13+) : Android masque les Toast d'une appli en arrière-plan | Réglages > Applis > TP4Calls > Notifications : activer |
| « Appel : termine » s'affiche à l'ouverture | ancien code, sans le filtre `dernierEtat` | le filtre ignore l'état IDLE initial |
| `gsm cancel` ne termine pas un appel **sortant** | `cancel` ne vaut que pour les appels simulés par la console | raccrocher à l'écran, ou `& $adb shell input keyevent 6` |

## 6. Ce qu'il faut savoir expliquer

- **RINGING n'existe que pour un appel entrant** : c'est pour ça qu'on a besoin de simuler un
  appelant. Un appel sortant passe directement de IDLE à OFFHOOK.
- **Qui appelle ton listener ?** Le système, via le `TelephonyManager`, à chaque changement
  d'état (`onCallStateChanged`), après l'enregistrement de l'écoute. Ton code ne l'appelle jamais.
- **Pourquoi `READ_PHONE_STATE` ?** Depuis Android 12, recevoir les états d'appel avec
  `TelephonyCallback` demande cette permission.
- **Ne jamais tester 15, 17, 18 ou 112 sur un vrai téléphone** : ce sont de vrais numéros
  d'urgence. Toujours l'émulateur.
