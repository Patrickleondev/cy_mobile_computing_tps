package com.cyu.tp1intents;

// une ligne de la table TABLE_EVENTS
public class Event {

    public final int id;
    public final String name;
    public final String lat;
    public final String lng;
    public final String type;
    public final String photo;

    public Event(int id, String name, String lat, String lng, String type, String photo) {
        this.id = id;
        this.name = name;
        this.lat = lat;
        this.lng = lng;
        this.type = type;
        this.photo = photo;
    }

    @Override
    public String toString() {
        return "ID: " + id + ", NAME: " + name + ", LAT: " + lat + ", LNG: " + lng + ", TYPE: " + type;
}
