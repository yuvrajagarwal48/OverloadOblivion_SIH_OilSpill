import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:spill_sentinel/connection.dart';
import 'dart:async';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  late AISStreamWebsocketClient aisClient;
  List<Marker> markers = [];
  StreamController<dynamic> aisStreamController = StreamController.broadcast();

  @override
  void initState() {
    super.initState();
    aisClient = AISStreamWebsocketClient(
      'wss://stream.aisstream.io/v0/stream',
      aisStreamController,
    );
    aisClient.connect();

    // Listen to the AIS stream and update markers
    aisStreamController.stream.listen((message) {
      if (message['MessageType'] == 'PositionReport') {
        setState(() {
          _addOrUpdateMarker(message);
        });
      }
    });
  }

  // Function to add markers based on AIS data
// Use a Map to store markers with MMSI as the key
  final Map<int, Marker> markersMap = {};

  void _addOrUpdateMarker(dynamic message) {
    final positionReport = message['Message']['PositionReport'];
    final latitude = positionReport['Latitude'];
    final longitude = positionReport['Longitude'];
    final shipName = message['MetaData']['ShipName'] ?? "Unknown Ship";
    final mmsi = message['MetaData']['MMSI'];

    // Check if latitude, longitude, and MMSI are valid
    if (latitude != null && longitude != null && mmsi != null) {
      // If a marker with the same MMSI already exists, update its position
      if (markersMap.containsKey(mmsi)) {
        // Update the marker's position
        markersMap[mmsi] = Marker(
          width: 20.0,
          height: 20.0,
          point: LatLng(latitude, longitude),
          child: Tooltip(
            message: 'Ship: $shipName\nMMSI: $mmsi',
            child: const Icon(
              Icons.directions_boat,
              size: 30.0,
              color: Colors.red,
            ),
          ),
        );
      } else {
        // If it's a new MMSI, add a new marker
        markersMap[mmsi] = Marker(
          width: 20.0,
          height: 20.0,
          point: LatLng(latitude, longitude),
          child: Tooltip(
            message: 'Ship: $shipName\nMMSI: $mmsi',
            child: const Icon(
              Icons.directions_boat,
              size: 30.0,
              color: Colors.blue,
            ),
          ),
        );
      }

      // Update the state to refresh the map
      setState(() {
        markers = markersMap.values.toList();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Spill Sentinel',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: Scaffold(
        appBar: AppBar(
          title: const Text('Spill Sentinel'),
        ),
        body: FlutterMap(
          options: MapOptions(
  initialCenter: LatLng(24.5, -90.0),
  initialZoom: 5.0, // Adjust the zoom level as needed
),
          children: [
            TileLayer(
              urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
              userAgentPackageName: 'com.example.app',
            ),
            MarkerLayer(markers: markers),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    aisStreamController.close();
    super.dispose();
  }
}
