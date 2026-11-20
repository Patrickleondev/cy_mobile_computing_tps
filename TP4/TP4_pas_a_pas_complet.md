# TP4 pas à pas complet : appeler les secours, envoyer et recevoir un SMS

Chaque fichier est donné **en entier** (Ctrl + A, coller). « Ce qui a été ajouté » montre les
lignes nouvelles par rapport au TP3.

Ce que fait l'appli en plus : depuis l'écran d'un événement, appeler le numéro de secours qui
correspond à son type (15, 17, 18 ou 112) et afficher l'état de l'appel ; envoyer un SMS avec le
nom et la position de l'événement ; afficher les SMS reçus.

**Sécurité** : 15, 17, 18 et 112 sont de vrais numéros. Teste **uniquement sur l'émulateur**.

## 0. Préparer le projet

1. Ferme Android Studio. Copie `AndroidStudioProjects\TP3Maps` en `AndroidStudioProjects\TP4Calls`.
2. Dans la copie, supprime `build`, `app\build`, `.gradle` et `.idea` (ils seront recréés).
3. Ouvre `TP4Calls` (**File > Open**) et attends la fin du Sync Gradle.
4. Change **seulement** ces lignes :
   - `settings.gradle.kts` : `rootProject.name = "TP4Calls"` ;
   - `app/build.gradle.kts` : `applicationId = "com.cyu.tp4calls"` ;
   - `res/values/strings.xml` : `<string name="app_name">TP4Calls</string>`.

**Ne touche jamais** à `namespace = "com.cyu.tp1intents"` dans `app/build.gradle.kts`. C'est le
paquet Java où Android génère la classe `R`. S'il change, tout le projet affiche
« package R does not exist ». Si Studio propose « Rename package », refuse.

`applicationId` est l'identité de l'appli sur le téléphone : en le changeant, le TP4
s'installe **à côté** du TP précédent au lieu de l'écraser.

## 1. Manifeste et textes

### 1.1 AndroidManifest.xml

**Remplace tout** le contenu de `app/src/main/AndroidManifest.xml` par :

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
    <!-- Android 13+ : sans elle, les Toast d'etat d'appel sont bloques pendant l'appel -->
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

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

**Ce qui a été ajouté ou changé** par rapport au TP précédent :

```xml

    <!-- TP4 : appeler, suivre l'etat de l'appel, envoyer et recevoir des SMS -->
    <uses-permission android:name="android.permission.CALL_PHONE" />
    <uses-permission android:name="android.permission.READ_PHONE_STATE" />
    <uses-permission android:name="android.permission.SEND_SMS" />
    <uses-permission android:name="android.permission.RECEIVE_SMS" />
    <!-- Android 13+ : sans elle, les Toast d'etat d'appel sont bloques pendant l'appel -->
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <!-- la telephonie est utile mais pas obligatoire : l'appli s'installe aussi sur une tablette -->
    <uses-feature
        android:name="android.hardware.telephony"
        android:required="false" />
```

```xml
        <!-- TP4 3 : recoit les SMS. BROADCAST_SMS : seul le systeme peut lui envoyer ce message -->
        <receiver
            android:name=".SmsReceiver"
            android:exported="true"
            android:permission="android.permission.BROADCAST_SMS">
            <intent-filter>
                <action android:name="android.provider.Telephony.SMS_RECEIVED" />
            </intent-filter>
        </receiver>

```

**Pourquoi :**

- `CALL_PHONE` : appeler sans passer par le clavier. `READ_PHONE_STATE` : être prévenu des états
  de l'appel. `SEND_SMS`, `RECEIVE_SMS` : envoyer et recevoir. Toutes **dangereuses** : à demander
  aussi à l'exécution.
- `POST_NOTIFICATIONS` : depuis Android 13, sans elle les Toast d'une appli en arrière-plan
  (pendant l'appel) ne s'affichent pas.
- `uses-feature telephony required="false"` : l'appli s'installe aussi sur une tablette.
- `<receiver .SmsReceiver>` : `exported="true"` car le message vient du système ;
  `permission="BROADCAST_SMS"` : seul le système (qui a cette permission) peut l'appeler, une autre
  appli ne peut pas envoyer de faux SMS ; l'`intent-filter` `SMS_RECEIVED`.

**Pourquoi à cet endroit :**

Permissions et `uses-feature` avant `<application>` ; le `<receiver>` dedans, à côté du `<service>`.

### 1.2 strings.xml

**Remplace tout** le contenu de `app/src/main/res/values/strings.xml` par :

```xml
<resources>
    <string name="app_name">TP4Calls</string>
    <string name="welcome">Welcome!\nPlease enter your details below to continue...</string>
    <string name="hint_name">Name</string>
    <string name="hint_email">Email</string>
    <string name="action_ok">OK</string>
    <string name="hello">Hello</string>
    <string name="action_next">NEXT</string>
    <string name="action_previous">PREVIOUS</string>
    <string name="action_add">AJOUTER</string>
    <string name="third_title">Evenements</string>
    <string name="photo_description">Photo illustrant le second ecran</string>
    <string name="empty_name">Entrez au moins un nom</string>
    <string name="status_loading">Telechargement des evenements...</string>
    <string name="status_error">Echec du telechargement (voir Logcat)</string>
    <string name="status_count">%1$d evenements</string>
    <string name="event_details">Latitude : %1$s\nLongitude : %2$s\nType : %3$s</string>
    <string name="event_title">Evenement</string>
    <string name="label_type">Type: %1$s</string>
    <string name="label_coords">Coordonnees : %1$s, %2$s</string>
    <string name="address_loading">Recherche de l\'adresse...</string>
    <string name="address_not_found">Adresse introuvable</string>
    <string name="address_unavailable">Geocodeur indisponible sur cet appareil</string>
    <string name="location_denied">Sans la permission de localisation, impossible de placer l\'evenement</string>
    <string name="you_are_here">Vous etes ici</string>
    <string name="hint_event_name">Nom de l\'evenement</string>
    <string name="waiting_position">En attente de la position GPS...</string>
    <string name="action_save">ENREGISTRER</string>
    <string name="empty_event_name">Donne un nom a l\'evenement</string>
    <!-- TP4 : appels et SMS -->
    <string name="action_call">APPELER LE %1$s</string>
    <string name="hint_sms_number">Numero du destinataire</string>
    <string name="action_send_sms">ENVOYER UN SMS</string>
    <string name="sms_text">Evenement %1$s, position %2$s, %3$s</string>
    <string name="call_ringing">Appel : le telephone sonne</string>
    <string name="call_offhook">Appel : en communication</string>
    <string name="call_idle">Appel : termine</string>
    <string name="call_denied">Sans la permission d\'appeler, impossible de joindre les secours</string>
    <string name="sms_sending">Envoi du SMS a %1$s...</string>
    <string name="sms_sent">SMS envoye</string>
    <string name="sms_failed">Echec de l\'envoi du SMS (code %1$d)</string>
    <string name="sms_denied">Sans la permission SMS, impossible d\'envoyer le message</string>
    <string name="sms_received">SMS de %1$s : %2$s</string>
    <string-array name="event_types">
        <item>concert</item>
        <item>forum</item>
        <item>conference</item>
        <item>sport</item>
        <item>exposition</item>
    </string-array>
</resources>
```

**Ce qui a été ajouté ou changé** par rapport au TP précédent :

```xml
    <string name="app_name">TP4Calls</string>
```

```xml
    <!-- TP4 : appels et SMS -->
    <string name="action_call">APPELER LE %1$s</string>
    <string name="hint_sms_number">Numero du destinataire</string>
    <string name="action_send_sms">ENVOYER UN SMS</string>
    <string name="sms_text">Evenement %1$s, position %2$s, %3$s</string>
    <string name="call_ringing">Appel : le telephone sonne</string>
    <string name="call_offhook">Appel : en communication</string>
    <string name="call_idle">Appel : termine</string>
    <string name="call_denied">Sans la permission d\'appeler, impossible de joindre les secours</string>
    <string name="sms_sending">Envoi du SMS a %1$s...</string>
    <string name="sms_sent">SMS envoye</string>
    <string name="sms_failed">Echec de l\'envoi du SMS (code %1$d)</string>
    <string name="sms_denied">Sans la permission SMS, impossible d\'envoyer le message</string>
    <string name="sms_received">SMS de %1$s : %2$s</string>
```

**Pourquoi :**

- Les textes des boutons, des Toast d'état d'appel et de SMS. `%1$s` / `%1$d` : valeurs insérées
  par `getString(id, valeur)`.

**Pourquoi à cet endroit :**

Avec les autres textes, avant le `string-array`.

### 1.3 activity_event.xml

**Remplace tout** le contenu de `app/src/main/res/layout/activity_event.xml` par :

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp"
    tools:context=".EventActivity">


    <TextView
        android:id="@+id/event_name"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:textSize="22sp"
        android:textStyle="bold"
        tools:text="Concert de rentree"
        />
    <TextView
        android:id="@+id/event_type"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="8dp"
        tools:text="Type: Concert"
        />

    <TextView
        android:id="@+id/event_coords"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="4dp"
        tools:text="Coordonnees : 49.0387, 2.0782" />
    <!-- TP4 1 : le numero depend du type de l'evenement, le texte est mis par EventActivity -->
    <Button
        android:id="@+id/call"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="16dp"
        android:onClick="call"
        tools:text="APPELER LE 15" />
    <!-- TP4 2 : destinataire du SMS (5554 = l'emulateur lui-meme) -->
    <EditText
        android:id="@+id/sms_number"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="8dp"
        android:hint="@string/hint_sms_number"
        android:inputType="phone"
        android:text="5554" />

    <Button
        android:id="@+id/send_sms"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:onClick="sendSms"
        android:text="@string/action_send_sms" />
<!--  La partie du 1 du sujet : L'adresse trouvee par le Geocoder -->
    <TextView
        android:id="@+id/event_address"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"
        android:layout_marginTop="16dp"
        android:textSize="16sp"
        tools:text="Boulevard du Port, 95000 Cergy" />

    <Button
        android:id="@+id/back"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="24dp"
        android:onClick="previous"
        android:text="@string/action_previous"/>
</LinearLayout>
```

**Ce qui a été ajouté ou changé** par rapport au TP précédent :

```xml
    <!-- TP4 1 : le numero depend du type de l'evenement, le texte est mis par EventActivity -->
    <Button
        android:id="@+id/call"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="16dp"
        android:onClick="call"
        tools:text="APPELER LE 15" />
    <!-- TP4 2 : destinataire du SMS (5554 = l'emulateur lui-meme) -->
    <EditText
        android:id="@+id/sms_number"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="8dp"
        android:hint="@string/hint_sms_number"
        android:inputType="phone"
        android:text="5554" />

    <Button
        android:id="@+id/send_sms"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:onClick="sendSms"
        android:text="@string/action_send_sms" />
```

**Pourquoi :**

- Bouton `call` : son texte (APPELER LE 15...) est mis par le Java, d'où `tools:text`.
- `EditText sms_number` : `inputType="phone"` (clavier numérique), `5554` = l'émulateur lui-même.
- Bouton ENVOYER UN SMS (`onClick="sendSms"`).

**Pourquoi à cet endroit :**

Sous les coordonnées et avant l'adresse : les actions de l'événement restent visibles en haut.

## 2. L'écran de l'événement

### 2.1 EventActivity.java

**Remplace tout** le contenu de `app/src/main/java/com/cyu/tp1intents/EventActivity.java` par :

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
            default: return "112";   // types 4 et 5, et tout type inconnu
        }
    }

    // android:onClick="call" dans activity_event.xml
    public void call(View view) {
        messageRefus = R.string.call_denied;
        // Android 13+ : pendant l'appel, l'ecran du telephone passe devant et notre appli est en
        // arriere-plan. Ses Toast n'y sont affiches que si elle a le droit d'envoyer des notifications.
        String[] permissions = Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU
                ? new String[]{Manifest.permission.CALL_PHONE, Manifest.permission.READ_PHONE_STATE,
                        Manifest.permission.POST_NOTIFICATIONS}
                : new String[]{Manifest.permission.CALL_PHONE, Manifest.permission.READ_PHONE_STATE};
        avecPermissions(permissions,
                () -> {
                    ecouterAppels();
                    Intent appel = new Intent(Intent.ACTION_CALL, Uri.parse("tel:" + numeroSecours));
                    startActivity(appel);
                });
    }

    private void ecouterAppels() {
        if (ecouteurAppel != null) return;   // deja a l'ecoute
        telephonie = (TelephonyManager) getSystemService(Context.TELEPHONY_SERVICE);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            EcouteurAppel12 ecouteur = new EcouteurAppel12();
            telephonie.registerTelephonyCallback(getMainExecutor(), ecouteur);
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
                message = R.string.call_ringing;
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
        sms.sendTextMessage(numero, null, texte, quandEnvoye, null);
        Toast.makeText(this, getString(R.string.sms_sending, numero), Toast.LENGTH_SHORT).show();
    }

    private final BroadcastReceiver resultatSms = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            if (getResultCode() == Activity.RESULT_OK) {
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

**Ce qui a été ajouté ou changé** par rapport au TP précédent :

```java
import android.Manifest;
import android.app.Activity;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
```

```java
import android.net.Uri;
```

```java
import android.telephony.PhoneStateListener;
import android.telephony.SmsManager;
import android.telephony.TelephonyCallback;
import android.telephony.TelephonyManager;
```

```java
import android.widget.Button;
import android.widget.EditText;
```

```java
import android.widget.Toast;
```

```java
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.annotation.RequiresApi;
```

```java
import androidx.core.content.ContextCompat;
```

```java
import java.util.Arrays;
```

```java
    // TP4 2 : l'action du message que Android nous renvoie quand le SMS est parti (ou pas)
    private static final String ACTION_SMS_SENT = "com.cyu.tp1intents.SMS_SENT";

```

```java
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
```

```java
        nom = getIntent().getStringExtra(EXTRA_NAME);
        lat = getIntent().getStringExtra(EXTRA_LAT);
        lng = getIntent().getStringExtra(EXTRA_LNG);
```

```java

        // TP4 1 : le bouton affiche le numero qu'il va appeler
        numeroSecours = numeroPourType(type);
        ((Button) findViewById(R.id.call)).setText(getString(R.string.action_call, numeroSecours));

        // TP4 2 : le resultat de l'envoi arrive par ce recepteur, tant que l'ecran existe
        ContextCompat.registerReceiver(this, resultatSms, new IntentFilter(ACTION_SMS_SENT),
                ContextCompat.RECEIVER_NOT_EXPORTED);
```

```java

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
            default: return "112";   // types 4 et 5, et tout type inconnu
        }
    }

    // android:onClick="call" dans activity_event.xml
    public void call(View view) {
        messageRefus = R.string.call_denied;
        // Android 13+ : pendant l'appel, l'ecran du telephone passe devant et notre appli est en
        // arriere-plan. Ses Toast n'y sont affiches que si elle a le droit d'envoyer des notifications.
        String[] permissions = Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU
                ? new String[]{Manifest.permission.CALL_PHONE, Manifest.permission.READ_PHONE_STATE,
                        Manifest.permission.POST_NOTIFICATIONS}
                : new String[]{Manifest.permission.CALL_PHONE, Manifest.permission.READ_PHONE_STATE};
        avecPermissions(permissions,
                () -> {
                    ecouterAppels();
                    Intent appel = new Intent(Intent.ACTION_CALL, Uri.parse("tel:" + numeroSecours));
                    startActivity(appel);
                });
    }

    private void ecouterAppels() {
        if (ecouteurAppel != null) return;   // deja a l'ecoute
        telephonie = (TelephonyManager) getSystemService(Context.TELEPHONY_SERVICE);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            EcouteurAppel12 ecouteur = new EcouteurAppel12();
            telephonie.registerTelephonyCallback(getMainExecutor(), ecouteur);
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
                message = R.string.call_ringing;
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
        sms.sendTextMessage(numero, null, texte, quandEnvoye, null);
        Toast.makeText(this, getString(R.string.sms_sending, numero), Toast.LENGTH_SHORT).show();
    }

    private final BroadcastReceiver resultatSms = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            if (getResultCode() == Activity.RESULT_OK) {
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
```

**Pourquoi :**

- `nom`, `lat`, `lng` deviennent des **attributs** (plus des variables de `onCreate`) : `sendSms`
  en a besoin plus tard.
- `apresPermission` + `messageRefus` + `demandePermissions` : **une seule** demande de permissions
  réutilisée pour l'appel et le SMS. `messageRefus` est déclaré **avant** le launcher qui l'utilise
  (sinon « illegal forward reference »).
- `avecPermissions(permissions, action)` : si tout est accordé, l'action tout de suite ; sinon on
  la garde et on demande.
- `numeroPourType` : ramène `TYPE1`..`TYPE5` (téléchargés) et `concert`... (formulaire) à un
  numéro 1 à 5, puis `switch` : 15, 17, 18, et `default` 112 (types 4, 5 et inconnus).
- `call` : `Intent.ACTION_CALL` + `tel:15` (appel direct, demande `CALL_PHONE`). On écoute l'état
  **avant** d'appeler pour ne rien rater.
- `ecouterAppels` : Android 12+ `TelephonyCallback` (classe interne `EcouteurAppel12`), avant
  `PhoneStateListener`, déprécié. `getMainExecutor()` : rappels sur le thread de l'écran (Toast).
- `montrerEtat` : `dernierEtat` filtre l'état IDLE donné dès l'inscription.
- `envoyerSms` : `SmsManager.sendTextMessage(numero, null, texte, quandEnvoye, null)`. Le
  `PendingIntent` est renvoyé par Android quand l'envoi est fini ; `resultatSms` le lit avec
  `getResultCode()`.
- `onDestroy` : désinscriptions. `onDestroy` et pas `onPause` : pendant l'appel, l'écran du
  téléphone passe devant (onPause), et on raterait les états à afficher.

**Pourquoi à cet endroit :**

Tout est dans `EventActivity` parce que le sujet dit « depuis l'événement qu'il regarde » : le
type, le nom et la position sont déjà dans ses extras.

### 2.2 SmsReceiver.java

**Nouveau fichier.** Clic droit sur le paquet > **New > Java Class** > `SmsReceiver`. Colle **tout** ce contenu :

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
        SmsMessage[] morceaux = Telephony.Sms.Intents.getMessagesFromIntent(intent);
        if (morceaux == null || morceaux.length == 0) return;

        String expediteur = morceaux[0].getOriginatingAddress() /* À TOI 10 : le numéro de l'expéditeur, lu dans le premier morceau */;
        StringBuilder corps = new StringBuilder();
        for (SmsMessage morceau : morceaux) {
            corps.append(morceau.getMessageBody());
        }

        Toast.makeText(context, context.getString(R.string.sms_received, expediteur, corps),
                Toast.LENGTH_LONG).show();
    }
}
```

**Pourquoi :**

- `extends BroadcastReceiver` : `onReceive` est appelée à chaque SMS reçu.
- `Telephony.Sms.Intents.getMessagesFromIntent` : les morceaux du SMS (un long message arrive en
  plusieurs SMS de 160 caractères), recollés dans l'ordre.
- `getDisplayOriginatingAddress` : l'expéditeur ; `getMessageBody` : le texte.

**Pourquoi à cet endroit :**

Déclaré dans le **manifeste** (et pas inscrit en Java) : Android réveille l'appli pour lui, même
quand aucun écran n'est ouvert.

### 2.3 app/build.gradle.kts

**Remplace tout** le contenu de `app/build.gradle.kts` par :

```kotlin
plugins {
    alias(libs.plugins.android.application)
}

android {
    namespace = "com.cyu.tp1intents"
    compileSdk {
        version = release(37)
    }

    defaultConfig {
        applicationId = "com.cyu.tp4calls"
        minSdk = 24
        targetSdk = 37
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            optimization {
                enable = false
            }
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
}

dependencies {
    implementation(libs.androidx.activity.ktx)
    implementation(libs.androidx.appcompat)
    implementation(libs.material)
    implementation(libs.androidx.constraintlayout)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    implementation(libs.osmdroid.android)
}
```

**Ce qui a été ajouté ou changé** par rapport au TP précédent :

```kotlin
        applicationId = "com.cyu.tp4calls"
```

**Pourquoi :**

- `applicationId = "com.cyu.tp4calls"`. `namespace` ne change pas.

**Pourquoi à cet endroit :**

Dans `defaultConfig`.

## 3. Tester (émulateur seulement)

EVENT3 (TYPE1) : APPELER LE 15, accepte la permission : Toast « en communication », puis
« termine ». Appel entrant : `adb emu gsm call 0612345678`, `adb emu gsm accept ...`,
`adb emu gsm cancel ...` : sonne, en communication, termine. ENVOYER UN SMS vers 5554 : « SMS
envoye ». Réception : `adb emu sms send 0612345678 "Bonjour"`.
