package com.cyu.tp1intents;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

public class MainActivity extends AppCompatActivity {

    // cles de l intent, prefixees par le package
    public final static String NAME = "com.cyu.tp1intents.name";
    public final static String EMAIL = "com.cyu.tp1intents.email";

    private EditText champNom;
    private EditText champEmail;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets barres = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(barres.left, barres.top, barres.right, barres.bottom);
            return insets;
        });

        champNom = findViewById(R.id.name);
        champEmail = findViewById(R.id.email);
    }

    // liee au bouton par android:onClick="submit"
    public void submit(View view) {
        String nom = champNom.getText().toString().trim();
        String email = champEmail.getText().toString().trim();

        if (nom.isEmpty()) {
            Toast.makeText(this, R.string.empty_name, Toast.LENGTH_SHORT).show();
            return;
        }

        Intent intent = new Intent(this, SecondActivity.class);
        intent.putExtra(NAME, nom);
        intent.putExtra(EMAIL, email);
        startActivity(intent);
    }
}
