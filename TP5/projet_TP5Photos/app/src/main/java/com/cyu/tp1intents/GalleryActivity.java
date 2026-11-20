package com.cyu.tp1intents;

import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AbsListView;
import android.widget.ArrayAdapter;
import android.widget.GridView;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import java.io.File;
import java.util.List;

// TP5 1 : la page d'apercu de toutes les photos prises par l'application
public class GalleryActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_gallery);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets barres = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(barres.left, barres.top, barres.right, barres.bottom);
            return insets;
        });

        List<File> photos = Medias.toutesLesPhotos(this);
        TextView statut = findViewById(R.id.gallery_status);
        statut.setText(photos.isEmpty()
                ? getString(R.string.gallery_empty)
                : getString(R.string.gallery_count, photos.size()));

        GridView grille = findViewById(R.id.gallery_grid);
        grille.setAdapter(new AdaptateurPhotos(photos));
    }

    // ArrayAdapter sait afficher du texte (toString) : pour une image, on fabrique la vue nous-memes
    private class AdaptateurPhotos extends ArrayAdapter<File> {

        AdaptateurPhotos(List<File> photos) {
            super(GalleryActivity.this, 0, photos);
        }

        @NonNull
        @Override
        public View getView(int position, View vueRecyclee, @NonNull ViewGroup parent) {
            ImageView vignette;
            if (vueRecyclee == null) {
                // premiere fois : on cree la case
                vignette = new ImageView(getContext());
                int cote = ((GridView) parent).getColumnWidth();   // case carree
                vignette.setLayoutParams(new AbsListView.LayoutParams(cote, cote));
                vignette.setScaleType(ImageView.ScaleType.CENTER_CROP);
            } else {
                // la case est sortie de l'ecran en defilant : on la reutilise
                vignette = (ImageView) vueRecyclee;
            }
            File photo = getItem(position);
            vignette.setImageBitmap(Medias.chargerReduite(photo.getAbsolutePath(), 300, 300));
            vignette.setContentDescription(photo.getName());
            return vignette;
        }
    }

    public void previous(View view) {
        finish();
    }
}
