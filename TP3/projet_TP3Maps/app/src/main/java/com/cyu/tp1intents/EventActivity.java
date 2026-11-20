package com.cyu.tp1intents;

import android.location.Address;
import android.location.Geocoder;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import java.io.IOException;
import java.util.List;
import java.util.Locale;

public class EventActivity extends AppCompatActivity {
    public static final String TAG = "EventActivity";

    // Les cles des extras : publiques pour que ThirdActivity les utilise aussi
    public static final String EXTRA_NAME = "com.cyu.tp1intents.name";
    public static final String EXTRA_LAT = "com.cyu.tp1intents.lat";
    public static final String EXTRA_LNG = "com.cyu.tp1intents.lng";
    public static final String EXTRA_TYPE = "com.cyu.tp1intents.type";

    private TextView adresse;

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

        String nom = getIntent().getStringExtra(EXTRA_NAME);
        String lat = getIntent().getStringExtra(EXTRA_LAT);
        String lng = getIntent().getStringExtra(EXTRA_LNG);
        String type = getIntent().getStringExtra(EXTRA_TYPE);

        ((TextView) findViewById(R.id.event_name)).setText(nom != null ? nom : "");
        ((TextView) findViewById(R.id.event_type)).setText(getString(R.string.label_type, type != null ? type : ""));
        ((TextView) findViewById(R.id.event_coords)).setText(getString(R.string.label_coords, lat != null ? lat : "", lng != null ? lng : ""));
        adresse = findViewById(R.id.event_address);

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