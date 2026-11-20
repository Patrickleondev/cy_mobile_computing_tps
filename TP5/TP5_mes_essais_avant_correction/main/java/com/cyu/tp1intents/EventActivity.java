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
    public static final String EXTRA_PHOTO = "com.cyu.tp1intents.photo";

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
        // TP5 1 : appele avant qu'Android detruise l'ecran ; le Bundle sera rendu a onCreate
        @Override
        protected void onSaveInstanceState(@NonNull Bundle etat) {
            super.onSaveInstanceState(etat);
            /* À TOI 10 : ranger cheminPhoto et cheminPhotoEnCours sous leurs clés ETAT_... */
            etat.putString(ETAT_PHOTO, cheminPhoto);
            etat.putString(ETAT_PHOTO_EN_COURS, cheminPhotoEnCours);
        }

        nom = getIntent().getStringExtra(EXTRA_NAME);
        lat = getIntent().getStringExtra(EXTRA_LAT);
        lng = getIntent().getStringExtra(EXTRA_LNG);
        String type = getIntent().getStringExtra(EXTRA_TYPE);

        ((TextView) findViewById(R.id.event_name)).setText(nom != null ? nom : "");
        ((TextView) findViewById(R.id.event_type)).setText(getString(R.string.label_type, type != null ? type : ""));
        ((TextView) findViewById(R.id.event_coords)).setText(getString(R.string.label_coords, lat != null ? lat : "", lng != null ? lng : ""));
        adresse = findViewById(R.id.event_address);
        String photo = getIntent().getStringExtra(EXTRA_PHOTO);
        if (photo != null) {
            ImageView vuePhoto = findViewById(R.id.event_photo);
            /* À TOI 12 : mettre l'image réduite (600 x 600) dans vuePhoto, puis la rendre visible */
            vuePhoto.setVisibility(View.VISIBLE);
        }

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