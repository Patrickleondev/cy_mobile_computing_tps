# 07. Les capteurs

> Source : cours 5 (*Android Sensors*). Corrigé : `10_corriges.md`, partie 07.
> Pas tombé dans les deux annales, mais le schéma « manager + listener + enregistrer /
> désenregistrer » est **exactement le même** que pour le GPS (chapitre 08). Le maîtriser
> ici, c'est déjà réviser le chapitre 08.

---

## 1. Ce qu'est un capteur

Un capteur **mesure une grandeur physique** et la convertit en signal lisible. Un
smartphone en contient beaucoup : micro, caméra, GPS, accéléromètre, gyroscope,
magnétomètre (boussole), proximité, lumière, pression, température...

**Tous les téléphones n'ont pas tous les capteurs.** Il faut toujours vérifier qu'un
capteur existe avant de l'utiliser.

---

## 2. Les types de capteurs (constantes de la classe `Sensor`)

| Constante | Mesure | Unité | Matériel / logiciel |
|---|---|---|---|
| `TYPE_ACCELEROMETER` | accélération sur x, y, z, **gravité comprise** | m/s² | matériel |
| `TYPE_LINEAR_ACCELERATION` | accélération **sans** la gravité | m/s² | logiciel ou matériel |
| `TYPE_GRAVITY` | la gravité seule | m/s² | logiciel ou matériel |
| `TYPE_GYROSCOPE` | **vitesse de rotation** autour des 3 axes | rad/s | matériel |
| `TYPE_MAGNETIC_FIELD` | champ magnétique terrestre (boussole) | µT (microtesla) | matériel |
| `TYPE_ORIENTATION` 🕰️ | angles : azimut, inclinaison (*pitch*), roulis (*roll*) | degrés | logiciel (**déprécié**) |
| `TYPE_ROTATION_VECTOR` | orientation de l'appareil | sans unité | logiciel ou matériel |
| `TYPE_PROXIMITY` | distance d'un objet à l'écran (souvent juste « près / loin ») | cm | matériel |
| `TYPE_LIGHT` | luminosité ambiante | lx (lux) | matériel |
| `TYPE_PRESSURE` | pression de l'air | hPa (= mbar) | matériel |
| `TYPE_AMBIENT_TEMPERATURE` | température de la pièce | °C | matériel |
| `TYPE_RELATIVE_HUMIDITY` | humidité | % | matériel |

**À quoi servent-ils :** la **proximité** éteint l'écran quand tu colles le téléphone à
l'oreille pendant un appel. L'**accéléromètre** détecte une chute, un secouement, compte
les pas. L'**orientation** (accéléromètre + magnétomètre) donne la direction pour une
boussole ou la réalité augmentée. La **lumière** règle la luminosité de l'écran.

**L'accéléromètre ne mesure pas la vitesse**, mais la **variation** de la vitesse. Posé à
plat sur une table, il indique environ **9,81 m/s² sur l'axe z** : c'est la gravité.

---

## 3. Le schéma « manager + listener » (à savoir par cœur)

**Le principe :** les capteurs sont gérés par un **service du système**. Ils envoient des
événements **quand ils le décident**. Ton appli ne « lit » pas un capteur : elle
**s'abonne** en enregistrant un **listener**, et le système l'appelle à chaque nouvelle
mesure. C'est un **rappel asynchrone**.

```
   Ton appli ──── registerListener(listener, capteur, rythme) ───► SensorManager
       ▲                                                              │
       └──────────── onSensorChanged(SensorEvent) ◄───────────────────┘
                     (appelé par le système à chaque mesure)
```

**Les classes :**

| Classe | Rôle |
|---|---|
| `SensorManager` | le service système : donne les capteurs, enregistre les listeners |
| `Sensor` | un capteur précis (nom, portée, résolution, consommation) |
| `SensorEventListener` | l'interface à implémenter : **2 méthodes** |
| `SensorEvent` | une mesure : `sensor`, `accuracy`, **`values`** (tableau de float), `timestamp` (ns) |

> **À savoir écrire par cœur :**

```java
public class CapteurActivity extends Activity implements SensorEventListener {

    private SensorManager sm;
    private Sensor accelero;

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_capteur);
        // 1. Obtenir le manager
        sm = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
        // 2. Obtenir le capteur (null s'il n'existe pas sur ce téléphone)
        accelero = sm.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
    }

    @Override
    protected void onResume() {                // 3. S'abonner quand l'écran est actif
        super.onResume();
        if (accelero != null) {
            sm.registerListener(this, accelero, SensorManager.SENSOR_DELAY_NORMAL);
        }
    }

    @Override
    protected void onPause() {                 // 4. Se désabonner : SINON la batterie fond
        super.onPause();
        sm.unregisterListener(this);
    }

    // 5. Les deux méthodes de SensorEventListener
    @Override
    public void onSensorChanged(SensorEvent event) {
        if (event.sensor.getType() == Sensor.TYPE_ACCELEROMETER) {
            float x = event.values[0];
            float y = event.values[1];
            float z = event.values[2];
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) { }
}
```

**Les points qui comptent :**
- **Désenregistrer dans `onPause`** : le système **ne coupe pas** les capteurs tout seul
  quand l'écran s'éteint. Un capteur oublié vide la batterie.
- **Les deux méthodes** de `SensorEventListener` doivent être écrites, même vide pour
  `onAccuracyChanged`.
- **`values`** : pour les capteurs à 3 axes, `values[0]` = x, `values[1]` = y,
  `values[2]` = z. Pour l'orientation : azimut, *pitch*, *roll*.

**Les rythmes de mesure** (du plus rapide au plus lent) : `SENSOR_DELAY_FASTEST`,
`SENSOR_DELAY_GAME`, `SENSOR_DELAY_UI`, `SENSOR_DELAY_NORMAL`. Plus c'est rapide, plus ça
consomme.

**La précision**, donnée à `onAccuracyChanged` : `SENSOR_STATUS_ACCURACY_LOW`, `MEDIUM`,
`HIGH`, `UNRELIABLE`.

**Autres méthodes utiles :**
- `sm.getSensorList(Sensor.TYPE_ALL)` : la liste de tous les capteurs du téléphone.
- `capteur.getName()`, `getMaximumRange()`, `getResolution()`, `getPower()` (consommation
  en mA), `getMinDelay()`.

---

## 4. Exemple : le « G-mètre » du cours

La force ressentie, en g, se calcule avec la **norme** du vecteur accélération, moins la
gravité :

```java
public void onSensorChanged(SensorEvent event) {
    double x = event.values[0], y = event.values[1], z = event.values[2];
    double a = Math.sqrt(x * x + y * y + z * z);                  // norme
    float actuelle = (float) Math.abs(a - SensorManager.STANDARD_GRAVITY);
    if (actuelle > max) max = actuelle;
}
```

`SensorManager.STANDARD_GRAVITY` vaut 9,81 m/s².

---

## 5. Le vibreur

```java
Vibrator v = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);
v.vibrate(1000);                               // vibre 1 seconde
long[] motif = { 0, 500, 200, 500 };           // attente, vibre, pause, vibre (en ms)
v.vibrate(motif, -1);                          // -1 = ne pas répéter ; 0 = répéter
```

Permission : `<uses-permission android:name="android.permission.VIBRATE" />`.

---

## 6. À toi (sur papier, fichier fermé)

**Exercice 7.1 :** Quelle est la différence entre `TYPE_ACCELEROMETER` et
`TYPE_LINEAR_ACCELERATION` ? Que vaut l'accéléromètre posé à plat sur une table ?

**Exercice 7.2 :** Quel capteur utiliser pour :
1. éteindre l'écran pendant un appel ;
2. une appli de boussole ;
3. détecter que le téléphone est tombé ;
4. régler la luminosité de l'écran.

**Exercice 7.3 :** Écris une activité complète qui affiche dans un `TextView` d'id
`valeur` la luminosité ambiante (capteur de lumière), en mettant à jour l'affichage à
chaque mesure. Elle doit afficher « Pas de capteur de lumière » si le téléphone n'en a pas,
et ne pas vider la batterie quand l'utilisateur quitte l'écran.

**Exercice 7.4 :** Pourquoi enregistrer le listener dans `onResume` et pas dans
`onCreate` ? Que se passe-t-il si on oublie `unregisterListener` ?

**Exercice 7.5 :** Écris le `onSensorChanged` qui fait vibrer le téléphone une demi-seconde
quand la norme de l'accélération dépasse 25 m/s² (secouement fort). Quelle permission
faut-il ?
