package com.cyu.tp1intents;

import android.Manifest;
import android.annotation.SuppressLint;
import android.content.pm.PackageManager;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import org.osmdroid.config.Configuration;
import org.osmdroid.tileprovider.tilesource.TileSourceFactory;
import org.osmdroid.util.GeoPoint;
import org.osmdroid.views.MapView;
import org.osmdroid.views.overlay.Marker;

import java.util.Locale;

public class AddEventActivity extends AppCompatActivity {

    private static final String TAG = "AddEventActivity";

    // centre de depart : le campus des Chenes, a Cergy
    private static final GeoPoint CERGY = new GeoPoint(49.0353, 2.0700);

    private MapView carte;
    private Marker epingle;

    private TextView textePosition;
    private EditText champNom;
    private Spinner spinnerType;
    private Button boutonEnregistrer;

    private LocationManager gestionnaire;
    private Location positionActuelle;

    private final ActivityResultLauncher<String[]> demandePermission =
            registerForActivityResult(new ActivityResultContracts.RequestMultiplePermissions(), reponses -> {
                boolean accepte = Boolean.TRUE.equals(reponses.get(Manifest.permission.ACCESS_FINE_LOCATION))
                        || Boolean.TRUE.equals(reponses.get(Manifest.permission.ACCESS_COARSE_LOCATION));
                if (accepte) {
                    demarrerGps();
                } else {
                    Toast.makeText(this, R.string.location_denied, Toast.LENGTH_LONG).show();
                }
            });
    // TP5 1 : l'appareil photo ecrit dans l'Uri qu'on lui donne, puis repond true (photo prise) ou false
    private final /* À TOI 6 : le type du launcher */ prendrePhoto =
    registerForActivityResult(new ActivityResultContracts.TakePicture(), cheminPhotoEnCours, reussi -> {
        if (reussi) {
            cheminPhoto = cheminPhotoEnCours;
            montrerApercu();
        } else {
            /* À TOI 8 : effacer le fichier resté vide */
            Toast.makeText(this, R.string.photo_failed, Toast.LENGTH_SHORT).show();
        }
            Toast.makeText(this, R.string.photo_cancelled, Toast.LENGTH_SHORT).show();
        }
        cheminPhotoEnCours = null;
    });

    private boolean aLaPermission() {
        return ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
                || ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED;
    }

    private final LocationListener ecouteur = new LocationListener() {
        @Override
        public void onLocationChanged(@NonNull Location position) {
            placer(position);
        }

        @Override public void onProviderEnabled(@NonNull String fournisseur) { }
        @Override public void onProviderDisabled(@NonNull String fournisseur) { }
        @Override public void onStatusChanged(String fournisseur, int statut, Bundle extras) { }
    };
// android:onClick="takePhoto" dans activity_add_event.xml
public void takePhoto(View view) {
    File fichier;
    try {
        fichier = Medias.nouveauFichier(Medias.dossierPhotos(this), ".jpg");
    } catch (IOException e) {
        Toast.makeText(this, R.string.file_error, Toast.LENGTH_LONG).show();
        return;
    }
    cheminPhotoEnCours = fichier.getAbsolutePath();
    try {
        /* À TOI 9 : lancer l'appareil photo avec l'adresse content:// du fichier */
        prendrePhoto.launch(Uri.fromFile(fichier));
    } catch (ActivityNotFoundException e) {
        fichier.delete();
        Toast.makeText(this, R.string.no_camera_app, Toast.LENGTH_LONG).show();
    }
}
// TP5 1 : appele avant qu'Android detruise l'ecran ; le Bundle sera rendu a onCreate
    @Override
    protected void onSaveInstanceState(@NonNull Bundle etat) {
        super.onSaveInstanceState(etat);
        /* À TOI 10 : ranger cheminPhoto et cheminPhotoEnCours sous leurs clés ETAT_... */
        etat.putString(ETAT_PHOTO, cheminPhoto);
        etat.putString(ETAT_PHOTO_EN_COURS, cheminPhotoEnCours);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // AVANT setContentView : osmdroid lit sa configuration en creant la MapView
        Configuration.getInstance().load(this, getSharedPreferences("osmdroid", MODE_PRIVATE));
        Configuration.getInstance().setUserAgentValue(getPackageName());

        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_add_event);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets barres = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(barres.left, barres.top, barres.right, barres.bottom);
            return insets;
        });

        carte = findViewById(R.id.map);
        carte.setTileSource(TileSourceFactory.MAPNIK);   // le style standard d'OpenStreetMap
        carte.setMultiTouchControls(true);               // zoom a deux doigts
        carte.getController().setZoom(16.0);
        carte.getController().setCenter(CERGY);

        epingle = new Marker(carte);
        epingle.setPosition(CERGY);
        epingle.setTitle(getString(R.string.you_are_here));
        carte.getOverlays().add(epingle);

        textePosition = findViewById(R.id.position_text);
        champNom = findViewById(R.id.new_name);
        spinnerType = findViewById(R.id.new_type);
        boutonEnregistrer = findViewById(R.id.save);

        if (!aLaPermission()) {
            demandePermission.launch(new String[]{
                    Manifest.permission.ACCESS_FINE_LOCATION,
                    Manifest.permission.ACCESS_COARSE_LOCATION});
        }
    }

    @SuppressLint("MissingPermission")
    private void demarrerGps() {
        if (!aLaPermission()) return;

        gestionnaire = (LocationManager) getSystemService(LOCATION_SERVICE);
        if (gestionnaire == null) return;

        Location derniere = null;
        if (gestionnaire.isProviderEnabled(LocationManager.GPS_PROVIDER)) {
            derniere = gestionnaire.getLastKnownLocation(LocationManager.GPS_PROVIDER);
        }
        if (derniere == null && gestionnaire.isProviderEnabled(LocationManager.NETWORK_PROVIDER)) {
            derniere = gestionnaire.getLastKnownLocation(LocationManager.NETWORK_PROVIDER);
        }
        if (derniere != null) {
            placer(derniere);
        }

        if (gestionnaire.isProviderEnabled(LocationManager.GPS_PROVIDER)) {
            gestionnaire.requestLocationUpdates(LocationManager.GPS_PROVIDER, 2000, 5, ecouteur);
        } else if (gestionnaire.isProviderEnabled(LocationManager.NETWORK_PROVIDER)) {
            gestionnaire.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, 2000, 5, ecouteur);
        }
    }

    private void placer(Location position) {
        positionActuelle = position;
        GeoPoint point = new GeoPoint(position.getLatitude(), position.getLongitude());
        epingle.setPosition(point);
        epingle.setTitle(getString(R.string.you_are_here));
        carte.getController().animateTo(point);
        carte.invalidate();

        if (textePosition != null) {
            textePosition.setText(String.format(Locale.US, "Position : %.4f, %.4f", position.getLatitude(), position.getLongitude()));
        }
        if (boutonEnregistrer != null) {
            boutonEnregistrer.setEnabled(true);
        }
    }

    public void save(View view) {
        String nom = champNom.getText().toString().trim();
        if (nom.isEmpty()) {
            champNom.setError(getString(R.string.empty_event_name));
            return;
        }
        if (positionActuelle == null) {
            return;
        }
        String type = (String) spinnerType.getSelectedItem();

        String lat = String.format(Locale.US, "%.4f", positionActuelle.getLatitude());
        String lng = String.format(Locale.US, "%.4f", positionActuelle.getLongitude());

        Event e = new Event(0, nom, lat, lng, type);
        EventDbHelper db = new EventDbHelper(this);
        db.ajouter(e);
        db.close();

        finish();
    }

    @Override
    protected void onResume() {
        super.onResume();
        carte.onResume();
        if (aLaPermission()) {
            demarrerGps();
        }
    }

    @Override
    protected void onPause() {
        if (gestionnaire != null) {
            gestionnaire.removeUpdates(ecouteur);
        }
        carte.onPause();
        super.onPause();
    }
}