package com.cyu.tp1intents;

// imports : laisse Studio les ajouter (Alt + Entrée)

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

    public void previous(View view) {
        finish();
    }
}