package com.cyu.tp1intents;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.provider.Telephony;
import android.telephony.SmsMessage;
import android.widget.Toast;

// TP4 partie 3 : Android previent ce recepteur a chaque SMS recu (declare dans le manifeste)
public class SmsReceiver extends BroadcastReceiver {

    @Override
    public void onReceive(Context context, Intent intent) {
        if (!Telephony.Sms.Intents.SMS_RECEIVED_ACTION.equals(intent.getAction())) return;

        // un long SMS arrive en plusieurs morceaux : on les recolle
        SmsMessage[] morceaux = Telephony.Sms.Intents.getMessagesFromIntent(intent);
        if (morceaux == null || morceaux.length == 0) return;

        String expediteur = morceaux[0].getOriginatingAddress() /* À TOI 10 : le numéro de l'expéditeur, lu dans le premier morceau */;
        StringBuilder corps = new StringBuilder();
        for (SmsMessage morceau : morceaux) {
            corps.append(morceau.getMessageBody());
        }

        Toast.makeText(context, context.getString(R.string.sms_received, expediteur, corps),
                Toast.LENGTH_LONG).show();
    }
}