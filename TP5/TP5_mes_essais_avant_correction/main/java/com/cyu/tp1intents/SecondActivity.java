package com.cyu.tp1intents;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

public class SecondActivity extends AppCompatActivity {

    private static final String TAG = "SecondActivity";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_second);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets barres = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(barres.left, barres.top, barres.right, barres.bottom);
            return insets;
        });

        Intent intent = getIntent();
        String nom = intent.getStringExtra(MainActivity.NAME);
        String email = intent.getStringExtra(MainActivity.EMAIL);

        TextView texteNom = findViewById(R.id.name);
        texteNom.setText(nom);

        // le sujet demande l email dans le log, pas a l ecran
        Log.d(TAG, "The user's email is: " + email);
    }

    public void next(View view) {
        startActivity(new Intent(this, ThirdActivity.class));
    }
}
