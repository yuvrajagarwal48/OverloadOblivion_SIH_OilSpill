import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';

Future<void> handler(RemoteMessage message) async {
  print('A new onMessageBackground event was published!');
}

class NotificationService {
  static Future<void> initialize() async {
    NotificationSettings settings =
        await FirebaseMessaging.instance.requestPermission();
    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      print('User granted permission');
      FirebaseMessaging.onBackgroundMessage(handler);
    }
  }

  static Future<void> showNotification(BuildContext context) async {
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      print('Got a message whilst in the foreground!');
      print('Message data: ${message.data}');
      if (message.notification != null) {
        print('Message also contained a notification: ${message.notification}');
      }
      showAboutDialog(context: context, children: [
        Text('Message data: ${message.data}'),
        Text('Message also contained a notification: ${message.notification}'),
      ]);
    });
  }

  static Future<void> getToken() async {
    if (FirebaseAuth.instance.currentUser != null &&
        FirebaseAuth.instance.currentUser!.uid.isNotEmpty) {
      DocumentSnapshot userSnapshot = await FirebaseFirestore.instance
          .collection('users')
          .doc(FirebaseAuth.instance.currentUser!.uid)
          .get();
      if (userSnapshot.exists &&
          (userSnapshot.data() as Map<String, dynamic>)["token"] == null) {
        await FirebaseFirestore.instance
            .collection('users')
            .doc(FirebaseAuth.instance.currentUser!.uid)
            .update({
          'token': await FirebaseMessaging.instance.getToken(),
        });
      }
    }
    String? token = await FirebaseMessaging.instance.getToken();
    print('Token: $token');
  }
}
