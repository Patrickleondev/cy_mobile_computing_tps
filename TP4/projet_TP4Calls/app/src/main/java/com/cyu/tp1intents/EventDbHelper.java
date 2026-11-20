package com.cyu.tp1intents;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.DatabaseUtils;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

import java.util.ArrayList;
import java.util.List;

public class EventDbHelper extends SQLiteOpenHelper {

    private static final String DB_NAME = "events.db";
    private static final int DB_VERSION = 1;

    // noms imposes par le sujet (2.2)
    public static final String TABLE_EVENTS = "TABLE_EVENTS";
    public static final String ID = "ID";
    public static final String NAME = "NAME";
    public static final String LAT = "LAT";
    public static final String LNG = "LNG";
    public static final String TYPE = "TYPE";

    public EventDbHelper(Context context) {
        super(context, DB_NAME, null, DB_VERSION);
    }

    // appele une seule fois, quand le fichier events.db n existe pas encore
    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE " + TABLE_EVENTS + " ("
                + ID + " INTEGER PRIMARY KEY, "
                + NAME + " TEXT, "
                + LAT + " TEXT, "
                + LNG + " TEXT, "
                + TYPE + " TEXT)");
    }

    // appele quand DB_VERSION augmente
    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_EVENTS);
        onCreate(db);
    }

    // vide la table puis insere les evenements du fichier, tout ou rien
    public void remplacer(List<Event> events) {
        SQLiteDatabase db = getWritableDatabase();
        db.beginTransaction();
        try {
            db.delete(TABLE_EVENTS, null, null);
            for (Event e : events) {
                ContentValues ligne = new ContentValues();
                ligne.put(NAME, e.name);
                ligne.put(LAT, e.lat);
                ligne.put(LNG, e.lng);
                ligne.put(TYPE, e.type);
                db.insert(TABLE_EVENTS, null, ligne);
            }
            db.setTransactionSuccessful();
        } finally {
            db.endTransaction();
        }
    }

    public boolean estVide() {
        return DatabaseUtils.queryNumEntries(getReadableDatabase(), TABLE_EVENTS) == 0;
    }

    // 2.3 : insere un evenement cree sur le telephone, renvoie son ID (-1 si echec)
    public long ajouter(Event e) {
        ContentValues ligne = new ContentValues();
        ligne.put(NAME, e.name);
        ligne.put(LAT, e.lat);
        ligne.put(LNG, e.lng);
        ligne.put(TYPE, e.type);
        return getWritableDatabase().insert(TABLE_EVENTS, null, ligne);
    }

    // SELECT * FROM TABLE_EVENTS ORDER BY ID
    public List<Event> lireTout() {
        List<Event> events = new ArrayList<>();
        try (Cursor c = getReadableDatabase().query(TABLE_EVENTS, null, null, null, null, null, ID)) {
            while (c.moveToNext()) {
                events.add(new Event(
                        c.getInt(c.getColumnIndexOrThrow(ID)),
                        c.getString(c.getColumnIndexOrThrow(NAME)),
                        c.getString(c.getColumnIndexOrThrow(LAT)),
                        c.getString(c.getColumnIndexOrThrow(LNG)),
                        c.getString(c.getColumnIndexOrThrow(TYPE))));
            }
        }
        return events;
    }
}
