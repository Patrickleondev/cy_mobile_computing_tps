// TP5 : tout ce qui touche aux fichiers photo, utilise par plusieurs ecrans
public final class Medias {

    private static final String TAG = "Medias";

    private Medias() { }
    // le dossier de l'appli sur le stockage externe : .../Android/data/<applicationId>/files/Pictures
    public static File dossierPhotos(Context context) {
        return context.getExternalFilesDir(Environment.DIRECTORY_PICTURES);
    }

    // un fichier vide au nom unique, que l'appareil photo remplira
    public static File nouveauFichier(File dossier, String extension) throws IOException {
        String horodatage = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(new Date());
        return File.createTempFile("EVENT_" + horodatage + "_", extension, dossier);
    }// que des methodes static : on ne cree jamais d'objet Medias
    // l'adresse content:// du fichier, la seule que l'autre application peut ouvrir
    public static Uri uriPartageable(Context context, File fichier) {
        return FileProvider.getUriForFile(context, /* À TOI 4 : l'authority du provider */, fichier);
    }
    // toutes les photos prises par l'application, la plus recente en premier
    public static List<File> toutesLesPhotos(Context context) {
        File[] fichiers = dossierPhotos(context).listFiles((dossier, nom) -> nom.endsWith(".jpg"));
        if (fichiers == null) return new ArrayList<>();
        List<File> photos = new ArrayList<>(Arrays.asList(fichiers));
        photos.removeIf(f -> f.length() == 0);   // photo annulee : le fichier est reste vide
        Collections.sort(photos, (a, b) -> Long.compare(b.lastModified(), a.lastModified()));
        return photos;
    }
    /**
     * Lit la photo en memoire, reduite a peu pres a la taille demandee.
     * Une photo de 12 Mpx occupe 48 Mo une fois decodee : sans reduction, la galerie plante.
     */
    public static Bitmap chargerReduite(String chemin, int largeurVoulue, int hauteurVoulue) {
        BitmapFactory.Options options = new BitmapFactory.Options();
        /* À TOI 5 : demander SEULEMENT la taille, sans lire aucun pixel */
        options.inJustDecodeBounds = true;
        BitmapFactory.decodeFile(chemin, options);
        if (options.outWidth <= 0) return null;      // fichier vide ou illisible

        int reduction = 1;                           // 1 = taille reelle, 2 = moitie, 4 = quart...
        while (options.outWidth / (reduction * 2) >= largeurVoulue
                && options.outHeight / (reduction * 2) >= hauteurVoulue) {
            reduction *= 2;
        }
        options.inJustDecodeBounds = false;          // 2e passage : les pixels, en reduisant
        options.inSampleSize = reduction;
        Bitmap image = BitmapFactory.decodeFile(chemin, options);
        return image == null ? null : redresser(chemin, image);
        // l'appareil photo enregistre souvent l'image couchee, avec l'angle note dans l'EXIF
        private static Bitmap redresser(String chemin, Bitmap image) {
            int angle;
            try {
                int orientation = new ExifInterface(chemin).getAttributeInt(
                        ExifInterface.TAG_ORIENTATION, ExifInterface.ORIENTATION_NORMAL);
                switch (orientation) {
                    case ExifInterface.ORIENTATION_ROTATE_90: angle = 90; break;
                    case ExifInterface.ORIENTATION_ROTATE_180: angle = 180; break;
                    case ExifInterface.ORIENTATION_ROTATE_270: angle = 270; break;
                    default: return image;
                }
            } catch (IOException e) {
                Log.w(TAG, "EXIF illisible : " + chemin, e);
                return image;
            }
            Matrix rotation = new Matrix();
            rotation.postRotate(angle);
            return Bitmap.createBitmap(image, 0, 0, image.getWidth(), image.getHeight(), rotation, true);
        }
    }

