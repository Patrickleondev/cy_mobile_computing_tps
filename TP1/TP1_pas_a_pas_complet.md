# TP1 pas à pas complet : trois écrans reliés par des Intents

Chaque fichier est donné **en entier** : ouvre-le dans Android Studio, **Ctrl + A**, colle.
Après chaque fichier : pourquoi ce code, et pourquoi à cet endroit.

Ce que fait l'appli : un formulaire (nom, email), un 2e écran qui dit « Hello <nom> » avec une
photo et écrit l'email dans Logcat, un 3e écran avec un bouton PREVIOUS.

## 0. Créer le projet

**File > New > New Project > Empty Views Activity**. Name `TP1Intents`, package
`com.cyu.tp1intents`, langage **Java**, Minimum SDK **API 24**. Studio crée `MainActivity`,
`activity_main.xml`, le manifeste et les fichiers Gradle.

Ajoute une image `photo.jpg` dans `app/src/main/res/drawable/` (glisser-déposer dans Studio).
Le nom doit être en minuscules, sans espace ni tiret : il devient `R.drawable.photo`.

## 1. Les ressources

### 1.1 strings.xml

**Remplace tout** le contenu du fichier par :

```xml
<resources>
    <string name="app_name">TP1Intents</string>
    <string name="welcome">Welcome!\nPlease enter your details below to continue...</string>
    <string name="hint_name">Name</string>
    <string name="hint_email">Email</string>
    <string name="action_ok">OK</string>
    <string name="hello">Hello</string>
    <string name="action_next">NEXT</string>
    <string name="action_previous">PREVIOUS</string>
    <string name="third_title">Troisieme ecran</string>
    <string name="photo_description">Photo illustrant le second ecran</string>
    <string name="empty_name">Entrez au moins un nom</string>
</resources>
```

**Pourquoi :**

- Tous les textes affichés sont ici, pas dans le Java ni dans les layouts : on peut traduire
  l'appli sans toucher au code, et Studio ne met plus d'avertissement « Hardcoded string ».
- `\n` dans `welcome` : un retour à la ligne.
- `empty_name` : le message du Toast si le nom est vide.

**Pourquoi à cet endroit :**

`res/values/` est le dossier des valeurs simples (textes, couleurs, dimensions). Android y cherche
`R.string.xxx` ; ailleurs, la ressource n'existerait pas.

### 1.2 activity_main.xml (1er écran)

**Remplace tout** le contenu du fichier par :

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:gravity="center_horizontal"
    android:padding="16dp">

    <TextView
        android:id="@+id/message"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="16dp"
        android:gravity="center"
        android:text="@string/welcome" />

    <EditText
        android:id="@+id/name"
        android:layout_width="240dp"
        android:layout_height="wrap_content"
        android:layout_marginTop="32dp"
        android:autofillHints="name"
        android:hint="@string/hint_name"
        android:inputType="textPersonName" />

    <EditText
        android:id="@+id/email"
        android:layout_width="240dp"
        android:layout_height="wrap_content"
        android:layout_marginTop="16dp"
        android:autofillHints="emailAddress"
        android:hint="@string/hint_email"
        android:inputType="textEmailAddress" />

    <Button
        android:id="@+id/button"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="24dp"
        android:onClick="submit"
        android:text="@string/action_ok" />

</LinearLayout>
```

**Pourquoi :**

- `LinearLayout` vertical : les éléments s'empilent de haut en bas. `gravity="center_horizontal"`
  les centre.
- `android:id="@+id/main"` sur la racine : `MainActivity` s'en sert pour les marges des barres
  système (EdgeToEdge).
- Deux `EditText` avec un `id` (`name`, `email`) : le Java les retrouve par `findViewById`.
  `inputType` choisit le clavier (email : avec @). `hint` : le texte gris quand le champ est vide.
- Le `Button` a `android:onClick="submit"` : au clic, Android appelle la méthode
  `public void submit(View view)` de l'Activity.

**Pourquoi à cet endroit :**

Dans `res/layout/` : c'est là qu'Android cherche `R.layout.activity_main`, que `setContentView`
charge dans `onCreate`.

### 1.3 activity_second.xml (2e écran)

**Nouveau fichier.** Clic droit sur `res/layout` > **New > Layout Resource File** > `activity_second`. Colle **tout** ce contenu :

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:gravity="center_horizontal"
    android:padding="16dp"
    tools:context=".SecondActivity">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="16dp"
        android:text="@string/hello" />

    <TextView
        android:id="@+id/name"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:textStyle="bold"
        tools:text="Patrick" />

    <ImageView
        android:id="@+id/photo"
        android:layout_width="240dp"
        android:layout_height="240dp"
        android:layout_marginTop="24dp"
        android:contentDescription="@string/photo_description"
        android:scaleType="centerCrop"
        android:src="@drawable/photo" />

    <Button
        android:id="@+id/next"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="40dp"
        android:onClick="next"
        android:text="@string/action_next" />

</LinearLayout>
```

**Pourquoi :**

- Un `TextView` fixe « Hello », puis un `TextView` avec `id="name"` que le Java remplit.
- `tools:text="Patrick"` : visible seulement dans l'aperçu de Studio, jamais sur le téléphone.
- `ImageView` avec `src="@drawable/photo"` : la photo ajoutée au point 0.
  `contentDescription` : le texte lu par TalkBack (accessibilité).
- Bouton `onClick="next"` vers le 3e écran.

**Pourquoi à cet endroit :**

Un écran = une Activity + son layout. Celui-ci est chargé par `SecondActivity`.

### 1.4 activity_third.xml (3e écran)

**Nouveau fichier.** Clic droit sur `res/layout` > **New > Layout Resource File** > `activity_third`. Colle **tout** ce contenu :

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:gravity="center"
    android:background="#FFF3E0"
    android:padding="16dp"
    tools:context=".ThirdActivity">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="@string/third_title"
        android:textSize="20sp"
        android:textStyle="bold" />

    <Button
        android:id="@+id/previous"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="32dp"
        android:onClick="previous"
        android:text="@string/action_previous" />

</LinearLayout>
```

**Pourquoi :**

- Un titre et un bouton PREVIOUS (`onClick="previous"`). Le fond orange clair montre qu'on a
  bien changé d'écran.

**Pourquoi à cet endroit :**

Chargé par `ThirdActivity`.

## 2. Les Activities

### 2.1 MainActivity.java

**Remplace tout** le contenu du fichier par :

```java
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
```

**Pourquoi :**

- `public final static String NAME = "com.cyu.tp1intents.name"` : la **clé** de l'extra.
  `public static` : `SecondActivity` la lit avec `MainActivity.NAME`, sans créer d'objet.
  `final` : constante. Préfixée par le paquet pour ne jamais entrer en conflit avec une autre clé.
- `private EditText champNom` : attribut, parce que `onCreate` le trouve et `submit` le lit.
- `onCreate` : `setContentView` affiche le layout, **puis** `findViewById` (avant, les vues
  n'existent pas encore).
- `submit(View view)` : signature imposée par `android:onClick` (`public void`, un `View`).
  `trim()` enlève les espaces. Si le nom est vide : un `Toast` et `return`.
- `new Intent(this, SecondActivity.class)` : un Intent **explicite** (on nomme l'écran visé).
  `putExtra` y range le nom et l'email ; `startActivity` ouvre l'écran.

**Pourquoi à cet endroit :**

`MainActivity` est l'écran de lancement (déclaré `LAUNCHER` dans le manifeste) : c'est lui qui
porte le formulaire et qui envoie les données.

### 2.2 SecondActivity.java

**Nouveau fichier.** Clic droit sur le paquet `com.cyu.tp1intents` > **New > Java Class** > `SecondActivity`. Colle **tout** ce contenu :

```java
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
```

**Pourquoi :**

- `private static final String TAG` : l'étiquette des messages Logcat (filtrer sur « SecondActivity »).
- `getIntent()` rend l'Intent qui a ouvert l'écran ; `getStringExtra(MainActivity.NAME)` lit
  l'extra avec **la même clé** que `putExtra`.
- `Log.d(TAG, ...)` : le sujet demande l'email dans le log, pas à l'écran.
- `next(View)` : ouvre `ThirdActivity`.

**Pourquoi à cet endroit :**

La lecture des extras se fait dans `onCreate`, après `setContentView`, parce qu'il faut afficher
le nom dès l'ouverture de l'écran.

### 2.3 ThirdActivity.java

**Nouveau fichier.** Clic droit sur le paquet > **New > Java Class** > `ThirdActivity`. Colle **tout** ce contenu :

```java
package com.cyu.tp1intents;

import android.os.Bundle;
import android.view.View;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

public class ThirdActivity extends AppCompatActivity {

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
    }

    // finish() suffit pour revenir : un nouvel intent empilerait une 2e SecondActivity
    public void previous(View view) {
        finish();
    }
}
```

**Pourquoi :**

- `previous(View)` appelle `finish()` : l'écran se ferme et Android réaffiche celui d'en dessous
  dans la pile. Un `new Intent` vers `SecondActivity` empilerait un **deuxième** exemplaire.

**Pourquoi à cet endroit :**

Le bouton PREVIOUS est dans `activity_third.xml`, donc sa méthode est dans l'Activity qui charge
ce layout.

## 3. Le manifeste

### 3.1 AndroidManifest.xml

**Remplace tout** le contenu du fichier par :

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

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
    </application>

</manifest>
```

**Pourquoi :**

- **Chaque** Activity doit être déclarée, sinon `ActivityNotFoundException` au clic.
- `MainActivity` a l'`intent-filter` `MAIN` + `LAUNCHER` : c'est l'icône du lanceur.
  `exported="true"` : obligatoire pour une Activity avec `intent-filter`.
- `SecondActivity` et `ThirdActivity` : `exported="false"`, seule ton appli les ouvre.
- `windowSoftInputMode="adjustResize"` : l'écran se réduit quand le clavier s'ouvre, les champs
  restent visibles.

**Pourquoi à cet endroit :**

Les `<activity>` vont **dans** `<application>`. Le manifeste est à la racine de `app/src/main/`.

## 4. Tester

Run : tape un nom et un email, OK. « Hello <nom> » et la photo s'affichent ; dans **Logcat**,
filtre `SecondActivity` : « The user's email is: ... ». NEXT, puis PREVIOUS : retour au 2e écran.
Nom vide : le Toast « Entrez au moins un nom ».
