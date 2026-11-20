# TP4 : corriger mes erreurs et savoir où va chaque bout de code

J'ai relu ton projet `C:\Users\User\AndroidStudioProjects\TP4Calls` le 13/11/2026. Il y a 14 erreurs.
Presque toutes viennent d'**une seule** confusion : des méthodes collées **dans** la petite classe
`EcouteurAppel12`, au lieu d'être dans `EventActivity`.

Cette fiche a trois parties :
- **A.** le plan d'`EventActivity` : où va chaque bloc ;
- **B.** tes 14 erreurs, une par une, avec leur raison ;
- **C.** les fichiers complets, testés sur l'émulateur : tu peux les recopier en entier.

Mon conseil : lis A et B pour comprendre, puis remplace tes fichiers par ceux de C. Ensuite, relis
chaque bloc de C en le comparant au tien.

---

## A. Le plan d'`EventActivity` : une classe, des « tiroirs » dans un ordre précis

Une classe Java, c'est une grande boîte entre `{` et `}`. À l'intérieur, on range des **tiroirs** :
des attributs, des méthodes et parfois une petite classe. Ce qui compte, c'est **dans quelle boîte**
on écrit un bloc. Les accolades décident de tout.

```
package ...                         <- 1. une seule ligne, tout en haut
import ...                          <- 2. tous les imports, avant la classe

public class EventActivity extends AppCompatActivity {      <- la GRANDE boîte s'ouvre

    3. les constantes      (EXTRA_NAME..., ACTION_SMS_SENT)
    4. les attributs       (adresse, nom, lat, lng, numeroSecours, telephonie,
                            ecouteurAppel, dernierEtat, apresPermission, messageRefus)
    5. le launcher         (demandePermissions = registerForActivityResult(...))

    6. onCreate()          (TP3 + 3 lignes TP4 + l'inscription de resultatSms)
    7. onDestroy()         (désinscrit resultatSms et l'écouteur d'appels)

    8. numeroPourType()    TP4 1
    9. call()              TP4 1, le bouton APPELER
   10. ecouterAppels()     TP4 1
   11. arreterEcouteAppels()
   12. class EcouteurAppel12 { onCallStateChanged() }   <- PETITE boîte : UNE seule méthode dedans
   13. montrerEtat()       TP4 1, les Toast d'état

   14. sendSms()           TP4 2, le bouton ENVOYER UN SMS
   15. envoyerSms()
   16. resultatSms         TP4 2, le récepteur « SMS parti ? »

   17. avecPermissions()   les permissions

   18. chercherAdresse(), montrer(), previous()   <- TP3, ne change pas

}                                    <- la GRANDE boîte se ferme : rien après
```

La règle à retenir : `EcouteurAppel12` ne contient **que** `onCallStateChanged`. Sa `}` se ferme
juste après. Tout le reste est au même niveau que `onCreate`.

Pourquoi ? Une méthode écrite dans `EcouteurAppel12` appartient à **l'écouteur**, pas à l'écran.
`call()` ne peut alors pas appeler `ecouterAppels()`. `onDestroy()` n'y a aucun sens : c'est une
méthode d'**activité**, et un `TelephonyCallback` n'est pas une activité. Enfin, dans le Toast,
`this` désignerait l'écouteur au lieu de l'écran.

Astuce Android Studio : clique juste après une `{`. Studio surligne la `}` qui lui correspond. Tu
vois ainsi où une boîte se ferme. **Code > Reformat Code** (Ctrl + Alt + L) réaligne aussi tout le
fichier : un bloc mal rangé saute alors aux yeux par son indentation.

---

## B. Tes 14 erreurs, une par une

| # | Fichier | Ce qui ne va pas | Pourquoi c'est une erreur | Correction |
|---|---|---|---|---|
| 1 | `AndroidManifest.xml` | `<receiver>` est **avant** `<application>`, au niveau des permissions | un récepteur est un composant de l'application, comme une activité ou un service | le déplacer **dans** `<application>`, à côté de `<service>` |
| 2 | `EventActivity.java` | il manque 13 imports (`Manifest`, `Toast`, `Intent`, `EditText`, `SmsManager`, `PendingIntent`, ...) | Java ne connaît une classe que si on l'importe | reprendre le bloc d'imports de C.1, ou **Alt + Entrée** sur chaque mot rouge |
| 3 | `onCreate` | `type = getIntent()...` sans `String` devant | `type` n'est déclaré nulle part. Seuls `nom`, `lat` et `lng` sont devenus des attributs | `String type = getIntent().getStringExtra(EXTRA_TYPE);` |
| 4 | attributs | `numeroSecours` est utilisé mais jamais déclaré | une variable doit être déclarée avant d'être utilisée | `private String numeroSecours;` avec les attributs |
| 5 | `numeroPourType` | `default:` ne renvoie rien | « missing return statement » : la méthode doit renvoyer un `String` dans **tous** les cas, même un type inconnu | `default: return "112";` (les `case 4` et `case 5` deviennent inutiles) |
| 6 | `call` | `new Intent(Intent.ACTION_CALL)` sans numéro | l'appel n'a pas de destinataire | `new Intent(Intent.ACTION_CALL, Uri.parse("tel:" + numeroSecours))` |
| 7 | `EcouteurAppel12` | `ecouterAppels`, `arreterEcouteAppels`, `montrerEtat` et `onDestroy` sont **dans** la petite classe | voir la partie A | les sortir : fermer `EcouteurAppel12` après `onCallStateChanged` |
| 8 | `EcouteurAppel12` | `ecouterAppels()` est écrit **deux fois** | « method is already defined » : un nom = une méthode | n'en garder qu'une |
| 9 | `ecouterAppels` (2ᵉ copie) | `registerTelephonyCallback((TelephonyCallback) ecouteur, ecouteur)` | le 1er paramètre doit être un `Executor` : **sur quel thread** prévenir | `telephonie.registerTelephonyCallback(getMainExecutor(), ecouteur);` |
| 10 | `montrerEtat` | il manque le cas IDLE | « variable message might not have been initialized » : si l'état est IDLE, `message` n'a pas de valeur | ajouter `default: message = R.string.call_idle; break;` |
| 11 | `envoyerSms` | le trou 7 n'est pas rempli | ça compile, mais le SMS ne part **jamais** : seul le Toast « Envoi... » s'affiche | `sms.sendTextMessage(numero, null, texte, quandEnvoye, null);` |
| 12 | `EventActivity` | le récepteur `resultatSms` n'existe pas | sans lui, personne n'écoute la réponse d'Android : pas de Toast « SMS envoye » | ajouter le bloc 16 de C.1 |
| 13 | `onCreate` / `onDestroy` | `resultatSms` n'est ni inscrit ni désinscrit | un récepteur non inscrit ne reçoit rien. Un récepteur oublié reste en mémoire après la fermeture de l'écran | inscription à la fin de `onCreate`, `unregisterReceiver` dans `onDestroy` |
| 14 | `SmsReceiver.java` | les trous 9, 10 et 11 sont vides | `= ;` n'est pas du Java : le fichier entier est rouge | les trois lignes de C.2 |

Les erreurs 7 et 8 provoquent à elles seules une cascade de messages rouges. Une fois les méthodes
remises au bon niveau, la moitié des erreurs disparaît d'un coup.

---

## C. Les fichiers complets (testés sur l'émulateur le 13/11/2026)

Pour chaque fichier : **sélectionne tout (Ctrl + A), colle, enregistre**. Puis **Build > Rebuild
Project**. Les lignes qui étaient des trous sont marquées d'un commentaire `TROU n`. Relis-les en
priorité.

### C.1 `EventActivity.java`

Chemin : `app/src/main/java/com/cyu/tp1intents/EventActivity.java`. Remplace **tout** le fichier.

```java
package com.cyu.tp1intents;

import android.Manifest;
import android.app.Activity;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.location.Address;
import android.location.Geocoder;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.telephony.PhoneStateListener;
import android.telephony.SmsManager;
import android.telephony.TelephonyCallback;
import android.telephony.TelephonyManager;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;

public class EventActivity extends AppCompatActivity {
    public static final String TAG = "EventActivity";

    // Les cles des extras : publiques pour que ThirdActivity les utilise aussi
    public static final String EXTRA_NAME = "com.cyu.tp1intents.name";
    public static final String EXTRA_LAT = "com.cyu.tp1intents.lat";
    public static final String EXTRA_LNG = "com.cyu.tp1intents.lng";
    public static final String EXTRA_TYPE = "com.cyu.tp1intents.type";

    // TP4 2 : l'action du message que Android nous renvoie quand le SMS est parti (ou pas)
    private static final String ACTION_SMS_SENT = "com.cyu.tp1intents.SMS_SENT";

    private TextView adresse;
    private String nom, lat, lng;

    // TP4 1 : le numero des secours, choisi selon le type
    private String numeroSecours;
    private TelephonyManager telephonie;
    // TelephonyCallback (Android 12+) ou PhoneStateListener (avant) : null tant qu'on n'ecoute pas
    private Object ecouteurAppel;
    private int dernierEtat = TelephonyManager.CALL_STATE_IDLE;

    // ce qu'il faut faire une fois les permissions accordees, et le message si elles sont refusees
    private Runnable apresPermission;
    private int messageRefus;
    private final ActivityResultLauncher<String[]> demandePermissions =
            registerForActivityResult(new ActivityResultContracts.RequestMultiplePermissions(), resultat -> {
                if (!resultat.containsValue(false) && apresPermission != null) {
                    apresPermission.run();
                } else {
                    Toast.makeText(this, messageRefus, Toast.LENGTH_LONG).show();
                }
                apresPermission = null;
            });

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_event);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets barres = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(barres.left, barres.top, barres.right, barres.bottom);
            return insets;
        });

        nom = getIntent().getStringExtra(EXTRA_NAME);
        lat = getIntent().getStringExtra(EXTRA_LAT);
        lng = getIntent().getStringExtra(EXTRA_LNG);
        String type = getIntent().getStringExtra(EXTRA_TYPE);

        ((TextView) findViewById(R.id.event_name)).setText(nom != null ? nom : "");
        ((TextView) findViewById(R.id.event_type)).setText(getString(R.string.label_type, type != null ? type : ""));
        ((TextView) findViewById(R.id.event_coords)).setText(getString(R.string.label_coords, lat != null ? lat : "", lng != null ? lng : ""));
        adresse = findViewById(R.id.event_address);

        // TP4 1 : le bouton affiche le numero qu'il va appeler
        numeroSecours = numeroPourType(type);
        ((Button) findViewById(R.id.call)).setText(getString(R.string.action_call, numeroSecours));

        // TP4 2 : le resultat de l'envoi arrive par ce recepteur, tant que l'ecran existe
        ContextCompat.registerReceiver(this, resultatSms, new IntentFilter(ACTION_SMS_SENT),
                ContextCompat.RECEIVER_NOT_EXPORTED);

        if (lat != null && lng != null) {
            try {
                double doubleLat = Double.parseDouble(lat);
                double doubleLng = Double.parseDouble(lng);
                chercherAdresse(doubleLat, doubleLng);
            } catch (NumberFormatException e) {
                Log.e(TAG, "Erreur de conversion des coordonnees", e);
            }
        }
    }

    @Override
    protected void onDestroy() {
        unregisterReceiver(resultatSms);
        arreterEcouteAppels();
        super.onDestroy();
    }

    /* ====================== TP4 1 : appeler les secours ====================== */

    /**
     * TYPE1 -> 15 (SAMU), TYPE2 -> 17 (police), TYPE3 -> 18 (pompiers), TYPE4 et TYPE5 -> 112.
     * Les evenements telecharges ont un type "TYPE1"..."TYPE5" ; ceux du formulaire du TP3,
     * un mot de la liste event_types (concert = 1, forum = 2, ...).
     */
    private String numeroPourType(String type) {
        int numeroType = 0;
        if (type != null) {
            String t = type.trim().toUpperCase(Locale.ROOT);
            if (t.startsWith("TYPE")) {
                try {
                    numeroType = Integer.parseInt(t.substring(4));
                } catch (NumberFormatException e) {
                    numeroType = 0;
                }
            } else {
                List<String> types = Arrays.asList(getResources().getStringArray(R.array.event_types));
                numeroType = types.indexOf(type.trim()) + 1;   // -1 + 1 = 0 si le mot est inconnu
            }
        }
        switch (numeroType) {
            case 1: return "15";
            case 2: return "17";
            case 3: return "18";
            default: return "112";   // TROU 3 : types 4 et 5, et tout type inconnu
        }
    }

    // android:onClick="call" dans activity_event.xml
    public void call(View view) {
        messageRefus = R.string.call_denied;
        avecPermissions(new String[]{Manifest.permission.CALL_PHONE, Manifest.permission.READ_PHONE_STATE},
                () -> {
                    ecouterAppels();
                    Intent appel = new Intent(Intent.ACTION_CALL, Uri.parse("tel:" + numeroSecours));   // TROU 4
                    startActivity(appel);
                });
    }

    private void ecouterAppels() {
        if (ecouteurAppel != null) return;   // deja a l'ecoute
        telephonie = (TelephonyManager) getSystemService(Context.TELEPHONY_SERVICE);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            EcouteurAppel12 ecouteur = new EcouteurAppel12();
            telephonie.registerTelephonyCallback(getMainExecutor(), ecouteur);   // TROU 5
            ecouteurAppel = ecouteur;
        } else {
            PhoneStateListener ecouteur = new PhoneStateListener() {
                @Override
                public void onCallStateChanged(int etat, String numero) {
                    montrerEtat(etat);
                }
            };
            telephonie.listen(ecouteur, PhoneStateListener.LISTEN_CALL_STATE);
            ecouteurAppel = ecouteur;
        }
    }

    private void arreterEcouteAppels() {
        if (ecouteurAppel == null) return;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            telephonie.unregisterTelephonyCallback((TelephonyCallback) ecouteurAppel);
        } else {
            telephonie.listen((PhoneStateListener) ecouteurAppel, PhoneStateListener.LISTEN_NONE);
        }
        ecouteurAppel = null;
    }

    // Android 12+ : PhoneStateListener est remplace par TelephonyCallback
    @RequiresApi(Build.VERSION_CODES.S)
    private class EcouteurAppel12 extends TelephonyCallback implements TelephonyCallback.CallStateListener {
        @Override
        public void onCallStateChanged(int etat) {
            montrerEtat(etat);
        }
    }

    private void montrerEtat(int etat) {
        // a l'inscription, Android donne tout de suite l'etat actuel (IDLE) : ce n'est pas une fin d'appel
        if (etat == dernierEtat) return;
        dernierEtat = etat;
        int message;
        switch (etat) {
            case TelephonyManager.CALL_STATE_RINGING:
                message = R.string.call_ringing;   // TROU 6
                break;
            case TelephonyManager.CALL_STATE_OFFHOOK:
                message = R.string.call_offhook;
                break;
            default:   // TelephonyManager.CALL_STATE_IDLE
                message = R.string.call_idle;
                break;
        }
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show();
    }

    /* ====================== TP4 2 : envoyer un SMS ====================== */

    // android:onClick="sendSms" dans activity_event.xml
    public void sendSms(View view) {
        String numero = ((EditText) findViewById(R.id.sms_number)).getText().toString().trim();
        if (numero.isEmpty()) return;
        String texte = getString(R.string.sms_text, nom, lat, lng);
        messageRefus = R.string.sms_denied;
        // RECEIVE_SMS en meme temps : la partie 3 en a besoin pour voir le SMS revenir
        avecPermissions(new String[]{Manifest.permission.SEND_SMS, Manifest.permission.RECEIVE_SMS},
                () -> envoyerSms(numero, texte));
    }

    private void envoyerSms(String numero, String texte) {
        SmsManager sms = Build.VERSION.SDK_INT >= Build.VERSION_CODES.S
                ? getSystemService(SmsManager.class)
                : SmsManager.getDefault();
        // Android "rappellera" ce PendingIntent quand le SMS sera parti ; setPackage : pour nous seuls
        Intent envoye = new Intent(ACTION_SMS_SENT).setPackage(getPackageName());
        PendingIntent quandEnvoye = PendingIntent.getBroadcast(this, 0, envoye, PendingIntent.FLAG_IMMUTABLE);
        sms.sendTextMessage(numero, null, texte, quandEnvoye, null);   // TROU 7
        Toast.makeText(this, getString(R.string.sms_sending, numero), Toast.LENGTH_SHORT).show();
    }

    private final BroadcastReceiver resultatSms = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            if (getResultCode() == Activity.RESULT_OK) {   // TROU 8
                Toast.makeText(context, R.string.sms_sent, Toast.LENGTH_SHORT).show();
            } else {
                Toast.makeText(context, getString(R.string.sms_failed, getResultCode()), Toast.LENGTH_LONG).show();
            }
        }
    };

    /* ====================== permissions ====================== */

    private void avecPermissions(String[] permissions, Runnable action) {
        boolean toutes = true;
        for (String p : permissions) {
            if (ContextCompat.checkSelfPermission(this, p) != PackageManager.PERMISSION_GRANTED) {
                toutes = false;
            }
        }
        if (toutes) {
            action.run();
        } else {
            apresPermission = action;
            demandePermissions.launch(permissions);
        }
    }

    /* ====================== TP3 : l'adresse ====================== */

    private void chercherAdresse(double lat, double lng) {
        if (!Geocoder.isPresent()) {
            adresse.setText(R.string.address_unavailable);
            return;
        }
        adresse.setText(R.string.address_loading);
        Geocoder geocodeur = new Geocoder(this, Locale.FRANCE);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            // Android 13+ : le resultat arrive plus tard, sur un autre thread
            geocodeur.getFromLocation(lat, lng, 1, resultats -> runOnUiThread(() -> montrer(resultats)));
        } else {
            // avant Android 13 : appel bloquant, donc dans un thread a part
            new Thread(() -> {
                List<Address> resultats = null;
                try {
                    resultats = geocodeur.getFromLocation(lat, lng, 1);
                } catch (IOException e) {
                    Log.e(TAG, "Geocodage impossible", e);
                }
                List<Address> fin = resultats;
                runOnUiThread(() -> montrer(fin));
            }).start();
        }
    }

    // toujours appelee sur le thread principal : elle peut toucher a l'ecran
    private void montrer(List<Address> resultats) {
        if (resultats == null || resultats.isEmpty()) {
            adresse.setText(R.string.address_not_found);
            return;
        }
        Address adresseTrouvee = resultats.get(0);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i <= adresseTrouvee.getMaxAddressLineIndex(); i++) {
            if (i > 0) sb.append("\n");
            sb.append(adresseTrouvee.getAddressLine(i));
        }
        adresse.setText(sb.toString());
    }

    public void previous(View view) {
        finish();
    }
}
```

### C.2 `SmsReceiver.java`

Même dossier. Remplace tout le fichier.

```java
package com.cyu.tp1intents;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.provider.Telephony;
import android.telephony.SmsMessage;
import android.widget.Toast;

// TP4 partie 3 : Android previent ce recepteur a chaque SMS recu (declare dans le manifeste)
public class SmsReceiver extends BroadcastReceiver {

    @Override
    public void onReceive(Context context, Intent intent) {
        if (!Telephony.Sms.Intents.SMS_RECEIVED_ACTION.equals(intent.getAction())) return;

        // un long SMS arrive en plusieurs morceaux : on les recolle
        SmsMessage[] morceaux = Telephony.Sms.Intents.getMessagesFromIntent(intent);   // TROU 9
        if (morceaux == null || morceaux.length == 0) return;

        String expediteur = morceaux[0].getDisplayOriginatingAddress();   // TROU 10
        StringBuilder corps = new StringBuilder();
        for (SmsMessage morceau : morceaux) {
            corps.append(morceau.getMessageBody());   // TROU 11
        }

        Toast.makeText(context, context.getString(R.string.sms_received, expediteur, corps),
                Toast.LENGTH_LONG).show();
    }
}
```

### C.3 `AndroidManifest.xml`

Chemin : `app/src/main/AndroidManifest.xml`. Regarde bien où est `<receiver>` : **dans**
`<application>`, juste avant `<service>`.

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- TP2 2.1 : telecharger le fichier -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />

    <!-- TP4 : appeler, suivre l'etat de l'appel, envoyer et recevoir des SMS -->
    <uses-permission android:name="android.permission.CALL_PHONE" />
    <uses-permission android:name="android.permission.READ_PHONE_STATE" />
    <uses-permission android:name="android.permission.SEND_SMS" />
    <uses-permission android:name="android.permission.RECEIVE_SMS" />

    <!-- la telephonie est utile mais pas obligatoire : l'appli s'installe aussi sur une tablette -->
    <uses-feature
        android:name="android.hardware.telephony"
        android:required="false" />

    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.TP1Intents">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:label="@string/app_name"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />

                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <activity
            android:name=".SecondActivity"
            android:exported="false"
            android:windowSoftInputMode="adjustResize" />

        <activity
            android:name=".ThirdActivity"
            android:exported="false" />

        <activity
            android:name=".EventActivity"
            android:exported="false" />

        <activity
            android:name=".AddEventActivity"
            android:exported="false" />

        <!-- TP4 3 : recoit les SMS. BROADCAST_SMS : seul le systeme peut lui envoyer ce message -->
        <receiver
            android:name=".SmsReceiver"
            android:exported="true"
            android:permission="android.permission.BROADCAST_SMS">
            <intent-filter>
                <action android:name="android.provider.Telephony.SMS_RECEIVED" />
            </intent-filter>
        </receiver>

        <service
            android:name=".DownloadService"
            android:exported="false" />
    </application>

</manifest>
```

### C.4 `activity_event.xml` et `strings.xml`

Ces deux fichiers sont **déjà justes** chez toi : n'y touche pas.

---

## D. Vérifier que c'est réparé

1. **Build > Rebuild Project** : la fenêtre **Build** en bas doit finir par `BUILD SUCCESSFUL`, sans
   ligne rouge.
2. Lance l'application, puis va jusqu'à la liste et ouvre **EVENT3**. Le bouton doit afficher
   **APPELER LE 15**.
3. Appuie dessus, puis accepte la permission. L'appel part, puis tu vois le Toast « Appel : en
   communication », puis « Appel : termine ».
4. Appuie sur **ENVOYER UN SMS**, puis accepte. Tu vois « Envoi du SMS a 5554... », puis « SMS envoye ».
5. Dans le terminal d'Android Studio, tape `adb emu sms send 0612345678 "Bonjour"`. Le Toast
   « SMS de 0612345678 : Bonjour » doit s'afficher.
6. Pour voir « le telephone sonne », tape `adb emu gsm call 0612345678`, puis `adb emu gsm accept
   0612345678`, puis `adb emu gsm cancel 0612345678`. Fais-le après avoir appuyé une première fois
   sur APPELER, pour que l'écoute soit active.

Si une erreur reste après ça, envoie-moi une capture de la fenêtre **Build** : le premier message
rouge suffit.
