package com.cyu.tp1intents;

// une ligne de la table TABLE_EVENTS
public class Event {

    public final int id;
    public final String name;
    public final String lat;
    public final String lng;
    public final String type;
    // TP5 : chemins des fichiers sur le telephone, null si l'evenement n'en a pas
    public final String photo;
    public final String video;

    // evenements du fichier telecharge (TP2) : ni photo ni video
    public Event(int id, String name, String lat, String lng, String type) {
        this(id, name, lat, lng, type, null, null);
    }

    public Event(int id, String name, String lat, String lng, String type, String photo, String video) {
        this.id = id;
        this.name = name;
        this.lat = lat;
        this.lng = lng;
        this.type = type;
        this.photo = photo;
        this.video = video;
    }

    @Override
    public String toString() {
        return "ID: " + id + ", NAME: " + name + ", LAT: " + lat + ", LNG: " + lng + ", TYPE: " + type
                + ", PHOTO: " + photo + ", VIDEO: " + video;
    }
}