package com.cyu.tp1intents;

import android.app.IntentService;
import android.content.Intent;
import android.os.Environment;
import android.util.Log;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

// onHandleIntent tourne dans un thread a part : le reseau y est permis
public class DownloadService extends IntentService {

    private static final String TAG = "DownloadService";

    // adresse donnee dans le sujet (2.1)
    public static final String URL_EVENTS =
            "https://drive.google.com/uc?export=download&id=1oa5a6P8nJ6aQgsbjurdiRorzAF92V2wP";
    public static final String FICHIER = "events.txt";

    // message envoye a ThirdActivity quand c est fini
    public static final String ACTION_FINI = "com.cyu.tp1intents.EVENTS_READY";
    public static final String SUCCES = "com.cyu.tp1intents.succes";

    public DownloadService() {
        super("DownloadService");
    }

    @Override
    protected void onHandleIntent(Intent intent) {
        boolean succes = false;
        try {
            File fichier = telecharger();
            List<Event> events = lire(fichier);
            new EventDbHelper(this).remplacer(events);
            Log.d(TAG, events.size() + " evenements enregistres dans la base");
            succes = true;
        } catch (IOException e) {
            Log.e(TAG, "echec du telechargement", e);
        }

        Intent fini = new Intent(ACTION_FINI);
        fini.setPackage(getPackageName());   // seule notre application le recoit
        fini.putExtra(SUCCES, succes);
        sendBroadcast(fini);
    }

    // 2.1 : copie le fichier du web dans le dossier Download de l application
    private File telecharger() throws IOException {
        File dossier = getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS);
        if (dossier == null) {
            throw new IOException("stockage externe indisponible");
        }
        File fichier = new File(dossier, FICHIER);

        Log.d(TAG, "Connexion a " + URL_EVENTS);
        HttpURLConnection connexion = (HttpURLConnection) new URL(URL_EVENTS).openConnection();
        connexion.setConnectTimeout(10000);
        connexion.setReadTimeout(10000);
        try {
            int code = connexion.getResponseCode();
            if (code != HttpURLConnection.HTTP_OK) {
                throw new IOException("reponse HTTP " + code);
            }
            try (InputStream in = new BufferedInputStream(connexion.getInputStream());
                 OutputStream out = new FileOutputStream(fichier)) {
                byte[] tampon = new byte[4096];
                int n;
                // read renvoie le nombre d octets lus : on n ecrit que ceux-la
                while ((n = in.read(tampon)) != -1) {
                    out.write(tampon, 0, n);
                }
            }
        } finally {
            connexion.disconnect();
        }

        Log.d(TAG, "Fichier enregistre : " + fichier.getAbsolutePath());
        return fichier;
    }

    // 2.2 : une ligne = NOM;;LAT;;LNG;;TYPE
    private List<Event> lire(File fichier) throws IOException {
        List<Event> events = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(fichier))) {
            String ligne;
            while ((ligne = br.readLine()) != null) {
                ligne = ligne.trim();
                if (ligne.isEmpty()) {
                    continue;
                }
                String[] morceaux = ligne.split(";;");
                if (morceaux.length == 4) {
                    events.add(new Event(0, morceaux[0], morceaux[1], morceaux[2], morceaux[3]));
                } else {
                    Log.w(TAG, "Ligne ignoree : " + ligne);
                }
            }
        }
        return events;
    }
}
