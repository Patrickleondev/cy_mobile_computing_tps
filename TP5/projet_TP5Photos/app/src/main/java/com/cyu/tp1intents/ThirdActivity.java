package com.cyu.tp1intents;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import java.util.ArrayList;
import java.util.List;

public class ThirdActivity extends AppCompatActivity {

    private static final String TAG = "ThirdActivity";

    private EventDbHelper db;
    private ListView liste;
    private TextView statut;
    private List<Event> events = new ArrayList<>();

    // recoit le message du service quand le fichier est en base
    private final BroadcastReceiver receveur = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            if (intent.getBooleanExtra(DownloadService.SUCCES, false)) {
                afficher();
            } else {
                statut.setText(R.string.status_error);
            }
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_third);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets barres = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(barres.left, barres.top, barres.right, barres.bottom);
            return insets;
        });

        db = new EventDbHelper(this);
        liste = findViewById(R.id.events);
        statut = findViewById(R.id.status);

        // Au clic sur un element de la liste : ouvre EventActivity avec les infos
        liste.setOnItemClickListener((parent, vue, position, id) -> {
            Event e = events.get(position);
            Intent intent = new Intent(this, EventActivity.class);
            intent.putExtra(EventActivity.EXTRA_NAME, e.name);
            intent.putExtra(EventActivity.EXTRA_LAT, e.lat);
            intent.putExtra(EventActivity.EXTRA_LNG, e.lng);
            intent.putExtra(EventActivity.EXTRA_TYPE, e.type);
            intent.putExtra(EventActivity.EXTRA_PHOTO, e.photo);   // TP5 : null si pas de photo
            intent.putExtra(EventActivity.EXTRA_VIDEO, e.video);
            startActivity(intent);
        });

        // base vide : on lance le telechargement une fois
        if (db.estVide()) {
            statut.setText(R.string.status_loading);
            startService(new Intent(this, DownloadService.class));
        }
    }

    // on n ecoute que quand l ecran est visible
    @Override
    protected void onResume() {
        super.onResume();
        ContextCompat.registerReceiver(this, receveur,
                new IntentFilter(DownloadService.ACTION_FINI), ContextCompat.RECEIVER_NOT_EXPORTED);
        afficher();
    }

    @Override
    protected void onPause() {
        super.onPause();
        unregisterReceiver(receveur);
    }

    @Override
    protected void onDestroy() {
        db.close();
        super.onDestroy();
    }

    // 3.1 : interroge la base, ecrit chaque ligne dans Logcat, puis remplit la liste
    private void afficher() {
        events = db.lireTout();
        if (events.isEmpty()) {
            return;   // pas encore telecharge
        }

        List<String> noms = new ArrayList<>();
        for (Event e : events) {
            Log.d(TAG, e.toString());
            noms.add(e.name);
        }
        liste.setAdapter(new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, noms));
        statut.setText(getString(R.string.status_count, events.size()));
    }

    public void addEvent(View view) {
        startActivity(new Intent(this, AddEventActivity.class));
    }

    // TP5 1 : android:onClick="gallery" dans activity_third.xml
    public void gallery(View view) {
        startActivity(new Intent(this, GalleryActivity.class));
    }

    // finish() suffit pour revenir : un nouvel intent empilerait une 2e SecondActivity
    public void previous(View view) {
        finish();
    }
}