# 06. Travailler en arrière-plan : services, threads, broadcasts, téléphonie

> Source : cours 4 (*Services and Broadcast Receivers*). La téléphonie n'est pas dans les
> diapos mais **tombe à l'annale 1 (ex. 3, 4,5 points)** : elle est expliquée ici en
> section 6. Corrigé : `10_corriges.md`, partie 06.
> Autres questions liées : **annale 2, Q1 g, h, j** (démarrer un service au démarrage du
> téléphone).

---

## 1. Le thread principal, et pourquoi il ne faut jamais le bloquer

Toute ton interface tourne sur **un seul thread**, le **thread principal** (ou thread UI).
C'est lui qui dessine l'écran et qui exécute tes listeners et tes callbacks.

**S'il est bloqué** (téléchargement, grosse requête en base, calcul long, `Thread.sleep`),
l'écran gèle. Au bout de **5 secondes** sans réaction, le système affiche « L'application
ne répond pas » : c'est l'**ANR** (*Application Not Responding*).

**Donc :** tout travail long part dans un **autre thread**. Mais **seul le thread principal
a le droit de toucher à l'interface** : le résultat doit y être renvoyé.

```java
new Thread(new Runnable() {
    @Override
    public void run() {
        final String resultat = telechargerPage();      // long : hors du thread UI
        runOnUiThread(new Runnable() {                   // retour sur le thread UI
            @Override
            public void run() {
                texte.setText(resultat);                 // toucher l'interface : OK ici
            }
        });
    }
}).start();
```

### AsyncTask (le style du cours) 🕰️

`AsyncTask<Params, Progress, Result>` emballe ce schéma en trois méthodes :

| Méthode | Thread | Rôle |
|---|---|---|
| `doInBackground(Params...)` | **arrière-plan** | le travail long. **Ne touche pas à l'interface.** Peut appeler `publishProgress(...)` |
| `onProgressUpdate(Progress...)` | **principal** | affiche l'avancement (barre de progression) |
| `onPostExecute(Result)` | **principal** | reçoit le résultat de `doInBackground` et met à jour l'écran |

```java
private class Telechargement extends AsyncTask<String, Integer, Long> {
    @Override
    protected Long doInBackground(String... urls) {
        long total = 0;
        for (int i = 0; i < urls.length; i++) {
            total += telecharger(urls[i]);
            publishProgress((i + 1) * 100 / urls.length);
        }
        return total;
    }
    @Override
    protected void onProgressUpdate(Integer... p) { barre.setProgress(p[0]); }
    @Override
    protected void onPostExecute(Long total) { texte.setText(total + " octets"); }
}

new Telechargement().execute("https://a.fr/1", "https://a.fr/2");
```

🕰️ `AsyncTask` est **déprécié** depuis Android 11. Aujourd'hui : `Executors` + `Handler`,
ou **WorkManager** pour un travail qui doit survivre à la fermeture de l'appli.

---

## 2. Les Services

**Un Service est un composant qui travaille en arrière-plan, sans interface**, pour une
durée indéterminée (lecture de musique, suivi GPS, synchronisation).

- Il a une **priorité plus élevée** qu'une activité invisible : le système le tue moins
  facilement. S'il est tué, il peut être **relancé automatiquement**.
- Il doit être **déclaré** dans le manifeste : `<service android:name=".MonService" />`.
- **Piège n°1 :** un Service **s'exécute dans le thread principal** de l'appli. Ce n'est
  **pas** un thread séparé. Pour un travail lourd, il doit lui-même lancer un thread.

### 2.1 Le cycle de vie d'un service démarré

```
startService(intent)
        │
        ▼
   onCreate()            ← une seule fois, à la création
        │
        ▼
   onStartCommand()      ← à CHAQUE startService (peut donc être appelée plusieurs fois)
        │
   ... le service tourne ...
        │
   stopService(intent)  ou  stopSelf()
        ▼
   onDestroy()
```

> **À savoir écrire par cœur :**

```java
public class MonService extends Service {

    @Override
    public void onCreate() {
        super.onCreate();
        // préparer ce qui sert pendant toute la vie du service
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        new Thread(new Runnable() {                  // le travail lourd : dans un thread
            @Override
            public void run() {
                faireLeTravail();
                stopSelf();                          // le service s'arrête quand il a fini
            }
        }).start();
        return START_STICKY;                         // relancer le service s'il est tué
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;                                 // null = pas de liaison (service démarré)
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        // libérer les ressources, arrêter le thread
    }
}
```

**La valeur de retour de `onStartCommand`** dit au système quoi faire si le service est tué :

| Valeur | Si le service est tué... |
|---|---|
| `START_STICKY` | il est **relancé** (avec un Intent `null`) |
| `START_NOT_STICKY` | il **n'est pas** relancé |
| `START_REDELIVER_INTENT` | il est relancé **avec le dernier Intent** |

**Démarrer et arrêter, depuis une activité :**

```java
Intent i = new Intent(this, MonService.class);   // Intent EXPLICITE (obligatoire pour un
startService(i);                                 // service depuis Android 5)
...
stopService(i);
```

🕰️ Les exemples du cours redéfinissent `onStart(Intent, int)` : c'est l'ancien nom de
`onStartCommand`, déprécié. Depuis Android 8, un service lancé en arrière-plan est limité :
on utilise un **service de premier plan** (avec une notification visible) ou WorkManager.

### 2.2 Service démarré ou service lié

| | Service **démarré** | Service **lié** (*bound*) |
|---|---|---|
| Lancé par | `startService()` | `bindService()` |
| Vit | jusqu'à `stopService()` / `stopSelf()` | tant qu'au moins un composant y est lié |
| Communication | à sens unique (on lui envoie un Intent) | l'activité **appelle ses méthodes** directement |
| `onBind` renvoie | `null` | un `IBinder` |

**Le service lié, en résumé** (cours 4, diapos 12 à 14) :

```java
// Dans le service
private final IBinder binder = new MonBinder();
public class MonBinder extends Binder {
    MonService getService() { return MonService.this; }
}
@Override
public IBinder onBind(Intent intent) { return binder; }

// Dans l'activité
private MonService service;
private ServiceConnection connexion = new ServiceConnection() {
    public void onServiceConnected(ComponentName nom, IBinder b) {
        service = ((MonService.MonBinder) b).getService();   // on a la référence
    }
    public void onServiceDisconnected(ComponentName nom) {
        service = null;
    }
};
// dans onCreate (ou onStart) :
bindService(new Intent(this, MonService.class), connexion, Context.BIND_AUTO_CREATE);
```

---

## 3. Les BroadcastReceivers

**Un BroadcastReceiver réagit à une annonce diffusée à tout le système** : écran éteint,
batterie faible, démarrage terminé, SMS reçu, ou une annonce envoyée par une autre appli.

- Il **n'a pas d'interface** (mais peut afficher une notification).
- Il n'a **qu'un seul callback** : `onReceive(Context context, Intent intent)`.
- Il n'est **actif que pendant `onReceive`**. Dès qu'elle se termine, il est inactif.
- **Il doit finir en moins de 10 secondes.** C'est une **passerelle** : il fait le minimum
  et confie le vrai travail à un service.

```java
public class MonReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        String donnee = intent.getStringExtra("cle");
        // réagir vite, ou démarrer un service
    }
}
```

**Deux façons de l'enregistrer :**

| | **Statique** (manifeste) | **Dynamique** (code) |
|---|---|---|
| Où | `<receiver>` + `<intent-filter>` dans le manifeste | `registerReceiver(receiver, filtre)` |
| Actif | même quand l'appli est **fermée** | seulement tant qu'il est enregistré |
| Désinscription | aucune | **obligatoire** : `unregisterReceiver(receiver)` (dans le callback miroir) |
| Exemple | démarrage du téléphone | mises à jour envoyées par ton propre service |

```java
// Dynamique : dans onResume (ou onCreate)
IntentFilter filtre = new IntentFilter("fr.cyu.action.POSITION");
registerReceiver(monReceiver, filtre);
// ... dans onPause (ou onDestroy)
unregisterReceiver(monReceiver);
```

**Envoyer sa propre annonce** (c'est ainsi que le service GPS du cours 6 envoie la position
à l'activité) :

```java
Intent annonce = new Intent("fr.cyu.action.POSITION");   // action inventée, nommée
annonce.putExtra("latitude", 49.03);                     // d'après son package
sendBroadcast(annonce);
```

**Les annonces du système à connaître :**

| Action | Quand |
|---|---|
| `Intent.ACTION_BOOT_COMPLETED` (`android.intent.action.BOOT_COMPLETED`) | **le téléphone a fini de démarrer** |
| `ACTION_SCREEN_ON` / `ACTION_SCREEN_OFF` | l'écran s'allume / s'éteint |
| `ACTION_BATTERY_LOW` | batterie faible |
| `ACTION_TIME_CHANGED`, `ACTION_DATE_CHANGED`, `ACTION_TIMEZONE_CHANGED` | heure, date, fuseau changés |
| `ACTION_MEDIA_MOUNTED` / `UNMOUNTED` | carte SD insérée / retirée |
| `android.provider.Telephony.SMS_RECEIVED` | un SMS est arrivé |

---

## 4. Démarrer un service au démarrage du téléphone (annale 2, Q1 g, h, j)

**Le raisonnement :** au démarrage du téléphone, ton appli n'est pas ouverte, donc **aucune
activité ne tourne** : `onCreate` de ta `MainActivity` n'est pas appelé. Le seul moyen
d'être réveillé, c'est d'écouter l'annonce **`BOOT_COMPLETED`** avec un receiver
**déclaré dans le manifeste**, qui démarre le service.

```xml
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />

<application ...>
    <service android:name=".SuiviService" />
    <receiver android:name=".DemarrageReceiver" android:exported="true">
        <intent-filter>
            <action android:name="android.intent.action.BOOT_COMPLETED" />
        </intent-filter>
    </receiver>
</application>
```

```java
public class DemarrageReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        if (Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction())) {
            context.startService(new Intent(context, SuiviService.class));
        }
    }
}
```

**Trois éléments, à donner tous les trois :** la **permission**, le **receiver avec son
filtre** dans le manifeste, et le **`startService`** dans `onReceive`.

---

## 5. WakeLock : empêcher le téléphone de s'endormir

**Le problème :** un code qui marche branché au PC pendant le développement **échoue en
usage réel**, parce que le téléphone se met en veille et coupe le processeur.

**La solution :** un **WakeLock** garde le processeur (ou l'écran) allumé. À utiliser **le
moins longtemps possible** : il vide la batterie.

```java
PowerManager pm = (PowerManager) getSystemService(Context.POWER_SERVICE);
PowerManager.WakeLock wl = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "app:tag");
wl.acquire();          // PARTIAL : processeur allumé, écran éteint
// ... travail qui doit aller au bout ...
wl.release();          // TOUJOURS libérer
```

Permission : `<uses-permission android:name="android.permission.WAKE_LOCK" />`.

---

## 6. La téléphonie : écouter les appels (annale 1, ex. 3)

**Le gestionnaire :** `TelephonyManager`, obtenu comme tous les autres services système.
**Le listener :** une classe qui hérite de **`PhoneStateListener`** et redéfinit
**`onCallStateChanged(int state, String incomingNumber)`**.

**Les trois états d'appel, à connaître par cœur :**

| Constante | Le téléphone... | Quand |
|---|---|---|
| `TelephonyManager.CALL_STATE_RINGING` | **sonne** | un appel **entrant** arrive. `incomingNumber` contient le numéro de l'appelant |
| `TelephonyManager.CALL_STATE_OFFHOOK` | est **décroché** | une communication est **en cours** (appel entrant accepté, ou appel sortant) |
| `TelephonyManager.CALL_STATE_IDLE` | est **au repos** | aucun appel : soit rien ne s'est passé, soit **un appel vient de se terminer** |

**Les enchaînements d'états** (c'est ce qui permet de raisonner) :

```
Appel entrant décroché :   IDLE → RINGING → OFFHOOK → IDLE
Appel entrant manqué   :   IDLE → RINGING → IDLE
Appel sortant          :   IDLE → OFFHOOK → IDLE
```

**Le raisonnement pour l'annale :**
- Le numéro de l'appelant n'est connu qu'en **RINGING**.
- Une communication **commence** au passage en **OFFHOOK** : c'est là qu'on note l'heure de
  début (`System.currentTimeMillis()`).
- Une communication **se termine** au retour en **IDLE**. Mais IDLE arrive aussi quand **il
  ne s'est rien passé** (et au tout premier enregistrement du listener). D'où le
  **booléen `onCall`** de l'énoncé : il dit si on sort **vraiment** d'un appel. La durée =
  heure de fin moins heure de début.

**Enregistrer le listener :**

```java
TelephonyManager tm = (TelephonyManager) getSystemService(Context.TELEPHONY_SERVICE);
tm.listen(new MyPhoneListener(), PhoneStateListener.LISTEN_CALL_STATE);
// pour arrêter d'écouter : tm.listen(listener, PhoneStateListener.LISTEN_NONE);
```

**Permissions :** `READ_PHONE_STATE` (et `READ_CALL_LOG` pour obtenir le numéro depuis
Android 10). Ce sont des permissions **dangereuses** : demande à l'exécution aussi.

**Un squelette pour s'entraîner** (affiche juste l'état ; l'exercice 6.5 te demande la
version complète de l'annale) :

```java
private class EspionAppels extends PhoneStateListener {
    @Override
    public void onCallStateChanged(int state, String incomingNumber) {
        switch (state) {
            case TelephonyManager.CALL_STATE_RINGING:
                Log.d("Tel", "Ça sonne : " + incomingNumber);
                break;
            case TelephonyManager.CALL_STATE_OFFHOOK:
                Log.d("Tel", "Décroché");
                break;
            case TelephonyManager.CALL_STATE_IDLE:
                Log.d("Tel", "Au repos");
                break;
            default:
                break;
        }
    }
}
```

> **Piège du `switch` :** sans `break;` à la fin de chaque `case`, l'exécution **continue
> dans le `case` suivant**. Le squelette de l'annale ne met pas de `break` : à toi de les
> ajouter.

🕰️ `PhoneStateListener` est déprécié depuis Android 12, remplacé par `TelephonyCallback`.
L'examen utilise `PhoneStateListener`.

---

## 7. À toi (sur papier, fichier fermé)

**Exercice 6.1 :** Vrai ou faux ? Justifie.
1. Un Service s'exécute dans un thread séparé du thread principal.
2. `onStartCommand` n'est appelée qu'une seule fois dans la vie d'un service.
3. Pour démarrer automatiquement un service au démarrage du téléphone, il faut appeler
   `startService()` dans `onCreate` de l'activité principale.
4. Un service peut être démarré au démarrage du téléphone grâce à un intent-filter dans le
   manifeste.
5. Un BroadcastReceiver peut faire un téléchargement de 30 secondes dans `onReceive`.
6. Quelle annonce est envoyée quand le téléphone a fini de démarrer ?

**Exercice 6.2 :** Écris un service `CompteurService` qui, une fois démarré, écrit
« tic » dans Logcat toutes les secondes pendant 60 secondes, **sans bloquer le thread
principal**, puis s'arrête tout seul. Écris aussi le code de l'activité qui le démarre et
la ligne du manifeste.

**Exercice 6.3 :** Ton service envoie la valeur d'un compteur à l'activité avec un
broadcast d'action `fr.cyu.action.COMPTEUR`. Écris :
1. l'envoi dans le service ;
2. le receiver dans l'activité, qui affiche la valeur dans un `TextView` ;
3. l'enregistrement et la désinscription du receiver, dans les bons callbacks.

**Exercice 6.4 :** Écris tout ce qu'il faut (manifeste + Java) pour qu'une appli lance
`SauvegardeService` à chaque démarrage du téléphone.

**Exercice 6.5 (annale 1, ex. 3, 4,5 points) :** Complète les blancs pour que le listener
affiche le numéro de l'appelant pour un appel entrant, et la durée de l'appel à la fin d'un
appel. Ajoute ensuite le code qui enregistre ce listener, et les permissions.

```java
private class MyPhoneListener extends PhoneStateListener {
    private boolean onCall = false;

    @Override
    public void onCallStateChanged(int state, String incomingNumber) {
        switch (state) {
            case TelephonyManager.CALL_STATE_RINGING:
                // ADD CODE HERE
            case TelephonyManager.CALL_STATE_OFFHOOK:
                // ADD CODE HERE
            case TelephonyManager.CALL_STATE_IDLE:
                // ADD CODE HERE
            default:
                break;
        }
    }
}
```

**Exercice 6.6 :** Donne les trois méthodes d'une `AsyncTask`, sur quel thread chacune
s'exécute, et laquelle n'a pas le droit de toucher à l'interface.

**Exercice 6.7 :** Ce code d'activité fait geler l'appli. Pourquoi, et comment le corriger ?

```java
bouton.setOnClickListener(v -> {
    String page = telechargerPage("https://cyu.fr");   // 8 secondes
    texte.setText(page);
});
```
