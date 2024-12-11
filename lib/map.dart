import 'dart:convert';

import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:spill_sentinel/core/theme/app_pallete.dart';
import 'package:spill_sentinel/features/auth/presentation/pages/landing_page.dart';
import 'package:spill_sentinel/services/connection2.dart';
import 'package:spill_sentinel/services/notification_service.dart';
//import 'ais_websocket_client.dart'; // Your WebSocket client class
import 'ship_details_screen.dart';

class MapScreen extends StatefulWidget {
  const MapScreen({super.key});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  late AISWebSocketClient aisClient;
  final Map<int, Map<String, dynamic>> shipDataMap = {}; // Ship data by MMSI
  List<Marker> markers = []; // Dynamically generated markers

  @override
  void initState() {
    super.initState();
    getTokens();
    // Initialize WebSocket client and connect
    aisClient = AISWebSocketClient();
    aisClient.connectAndReceive();

    // Listen to the broadcast stream
    aisClient.stream.listen(
      (aisDataRaw) {
        final parsedData = aisDataRaw;
        final aisData = parsedData['ais_data'];
        final anomalyResult = parsedData['anomaly_result'];
        _processAISData(aisData, anomalyResult);
        _updateMarkers();
        print(shipDataMap);
      },
      onError: (error) {
        print('Stream error: $error');
      },
      onDone: () {
        print('Stream closed.');
      },
    );
    // _addDummyData();
    // _updateMarkers();
  }

  void _addDummyData() {
    // Ship Alpha
    shipDataMap[123456789] = {
      'MMSI': 123456789,
      'ShipName': "Ship Alpha",
      'Position': LatLng(24.5, -90.0),
      'Speed': '15 kn',
      'Heading': '90°',
      'Status': '5', // Anchored
      'ETA': '2024-12-01 10:00 UTC',
      'Destination': 'Port A',
      'Draught': '8.5 m',
      'CallSign': 'CALL123',
      'IMO': 'IMO123456',
      'Timestamp': '2024-11-29 12:30 UTC',
      'Zone': 'Gulf of Mexico',
      'Course': '45°', // Dummy course
      'Type': 52, // Dummy type
      'A': '25 m', // Dummy bow distance
      'B': '30 m', // Dummy stern distance
      'C': '10 m', // Dummy port distance
      'D': '12 m', // Dummy starboard distance
      'LOCODE': 'LOC123', // Dummy LOCODE
      'SRC': 'SAT', // Dummy source
      'ECA': true, // Dummy ECA status
      'DistanceRemaining': '120 nm', // Dummy distance
      'ETAAIS': '12-01 10:00', // Dummy AIS ETA
      'ETAPredicted': '2024-12-01 09:45', // Dummy predicted ETA
      'Anomaly': false,
      'AnomalyProbability': 0.0,
      'OilSpillProbability': 0.0,
    };

    // Ship Beta
    shipDataMap[987654321] = {
      'MMSI': 987654321,
      'ShipName': "Ship Beta",
      'Position': LatLng(25.0, -89.5),
      'Speed': '10 kn',
      'Heading': '45°',
      'Status': '2', // Moored
      'ETA': '2024-11-30 15:00 UTC',
      'Destination': 'Port B',
      'Draught': '10.0 m',
      'CallSign': 'CALL987',
      'IMO': 'IMO987654',
      'Timestamp': '2024-11-29 12:45 UTC',
      'Zone': 'Gulf of Mexico',
      'Course': '90°', // Dummy course
      'Type': 52, // Dummy type
      'A': '20 m', // Dummy bow distance
      'B': '25 m', // Dummy stern distance
      'C': '8 m', // Dummy port distance
      'D': '15 m', // Dummy starboard distance
      'LOCODE': 'LOC456', // Dummy LOCODE
      'SRC': 'TER', // Dummy source
      'ECA': false, // Dummy ECA status
      'DistanceRemaining': '50 nm', // Dummy distance
      'ETAAIS': '11-30 15:00', // Dummy AIS ETA
      'ETAPredicted': '2024-11-30 14:50', // Dummy predicted ETA
      'Anomaly': true,
      'AnomalyProbability': 0.8,
      'OilSpillProbability': 0.5,
    };

    // MANTA
    shipDataMap[205340000] = {
      'MMSI': 205340000,
      'ShipName': "MANTA",
      'Position': LatLng(36.14755, -5.36404),
      'Speed': '0 kn',
      'Heading': '180°',
      'Status': '5', // Anchored
      'ETA': '2024-11-28 07:30:00',
      'Destination': 'GI GIB',
      'Draught': '6.4 m',
      'CallSign': 'ORKJ',
      'IMO': 'IMO9261487',
      'Timestamp': '2024-11-29 16:27:10 UTC',
      'Zone': 'West Mediterranean',
      'Course': '78.3°',
      'Type': 52,
      'A': '19 m',
      'B': '56 m',
      'C': '13 m',
      'D': '5 m',
      'LOCODE': 'GIGIB',
      'SRC': 'TER',
      'ECA': false,
      'DistanceRemaining': '6 nm',
      'ETAAIS': '11-28 07:30',
      'ETAPredicted': '2024-11-28 07:20',
      'Anomaly': false,
      'AnomalyProbability': 0.0,
      'OilSpillProbability': 0.0,
    };
  }

  /// Process AIS data and anomaly results
  void _processAISData(
      Map<String, dynamic> aisData, Map<String, dynamic> anomalyResult) {
    final mmsi = aisData['MMSI'] as int?;
    final latitude = aisData['LATITUDE'] as double?;
    final longitude = aisData['LONGITUDE'] as double?;

    if (mmsi != null && latitude != null && longitude != null) {
      shipDataMap[mmsi] = {
        'MMSI': mmsi,
        'ShipName': aisData['NAME']?.toString() ?? "Unknown Ship",
        'Position': LatLng(latitude, longitude),
        'Speed': "${aisData['SPEED']?.toString() ?? "0"} kn",
        'Heading': "${aisData['HEADING']?.toString() ?? "N/A"}°",
        'Status': aisData['NAVSTAT']?.toString() ?? "N/A",
        'ETA': aisData['ETA']?.toString() ?? "N/A",
        'Destination': aisData['DESTINATION']?.toString() ?? "N/A",
        'Draught': "${aisData['DRAUGHT']?.toString() ?? "Unknown"} m",
        'CallSign': aisData['CALLSIGN']?.toString() ?? "Unknown",
        'IMO': aisData['IMO']?.toString() ?? "Unknown",
        'Timestamp': aisData['TIMESTAMP']?.toString() ?? "N/A",
        'Zone': aisData['ZONE']?.toString() ?? "N/A",
        'Course': "${aisData['COURSE']?.toString() ?? "N/A"}°",
        'Type': aisData['TYPE']?.toString() ?? "Unknown",
        'A': aisData['A']?.toString() ?? "Unknown",
        'B': aisData['B']?.toString() ?? "Unknown",
        'C': aisData['C']?.toString() ?? "Unknown",
        'D': aisData['D']?.toString() ?? "Unknown",
        'LOCODE': aisData['LOCODE']?.toString() ?? "Unknown",
        'SRC': aisData['SRC']?.toString() ?? "Unknown",
        'ECA': aisData['ECA'] ?? false,
        'DistanceRemaining': aisData['DISTANCE_REMAINING']?.toString() ?? "N/A",
        'ETAAIS': aisData['ETA_AIS']?.toString() ?? "Unknown",
        'ETAPredicted': aisData['ETA_PREDICTED']?.toString() ?? "Unknown",
        'Anomaly': anomalyResult['anomaly'] ?? false,
        'AnomalyProbability':
            anomalyResult['anomaly_probability']?.toDouble() ?? 0.0,
        'OilSpillProbability':
            anomalyResult['oil_spill_probability']?.toDouble() ?? 0.0,
      };
    }
  }

  void getTokens() async {
    await NotificationService.getToken();
  }

  /// Updates the markers list
  void _updateMarkers() {
    markers = shipDataMap.values
        .map((shipData) {
          final position = shipData['Position'] as LatLng?;
          if (position == null) return null;

          final isAnomalous = shipData['Anomaly'] as bool;
          final heading = double.tryParse(
                  shipData['Heading']?.toString().replaceAll('°', '') ?? '0') ??
              0;

          return Marker(
            width: isAnomalous ? 60.0 : 40.0,
            height: isAnomalous ? 60.0 : 40.0,
            point: position,
            child: GestureDetector(
              onTap: () => _navigateToShipDetails(shipData),
              child: Stack(
                alignment: Alignment.center,
                children: [
                  // Pulsing effect for anomalous ships
                  if (isAnomalous)
                    TweenAnimationBuilder<double>(
                      tween: Tween(begin: 0.2, end: 0.6),
                      duration: const Duration(milliseconds: 800),
                      builder: (context, scale, child) {
                        return Transform.scale(
                          scale: scale,
                          child: Container(
                            decoration: BoxDecoration(
                              color: Colors.red.withOpacity(0.3),
                              shape: BoxShape.circle,
                            ),
                            width: 60,
                            height: 60,
                          ),
                        );
                      },
                    ),

                  // Ship marker with direction
                  Transform.rotate(
                    angle: (heading * pi / 180), // Convert degrees to radians
                    child: Icon(
                      Icons.navigation,
                      size: isAnomalous ? 30.0 : 20.0,
                      color: isAnomalous ? Colors.red : Colors.blue,
                    ),
                  ),
                ],
              ),
            ),
          );
        })
        .whereType<Marker>()
        .toList();

    setState(() {});
  }

  void _navigateToShipDetails(Map<String, dynamic> shipData) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ShipDetailsScreen(
          shipData: {
            'ShipName': shipData['ShipName'] ?? "Unknown Ship",
            'MMSI': shipData['MMSI']?.toString() ?? "Unknown",
            'Position': shipData['Position'] as LatLng?,
            'Speed': shipData['Speed'] ?? "0 kn",
            'Heading': shipData['Heading'] ?? "N/A",
            'Status': shipData['Status'] ?? "N/A",
            'ETA': shipData['ETA'] ?? "N/A",
            'Destination': shipData['Destination'] ?? "N/A",
            'Draught': shipData['Draught'] ?? "Unknown",
            'CallSign': shipData['CallSign'] ?? "Unknown",
            'IMO': shipData['IMO'] ?? "Unknown",
            'Timestamp': shipData['Timestamp'] ?? "N/A",
            'Zone': shipData['Zone'] ?? "N/A",
            'Course': shipData['Course'] ?? "N/A",
            'Type': shipData['Type'] ?? "Unknown",
            'A': shipData['A'] ?? "Unknown",
            'B': shipData['B'] ?? "Unknown",
            'C': shipData['C'] ?? "Unknown",
            'D': shipData['D'] ?? "Unknown",
            'LOCODE': shipData['LOCODE'] ?? "Unknown",
            'SRC': shipData['SRC'] ?? "Unknown",
            'ECA': shipData['ECA'] ?? false,
            'DistanceRemaining': shipData['DistanceRemaining'] ?? "N/A",
            'ETAAIS': shipData['ETAAIS'] ?? "Unknown",
            'ETAPredicted': shipData['ETAPredicted'] ?? "Unknown",
            'Anomaly': shipData['Anomaly'] ?? false,
            'AnomalyProbability': shipData['AnomalyProbability'] ?? 0.0,
            'OilSpillProbability': shipData['OilSpillProbability'] ?? 0.0,
          },
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: Icon(Icons.logout),
          onPressed: () {
            FirebaseAuth.instance.signOut();
            Navigator.pushReplacement(context,
                MaterialPageRoute(builder: (context) => const LandingPage()));
          },
        ),
        title:
            const Text("Spill Sentinel", style: TextStyle(color: Colors.white)),
        backgroundColor: Pallete.primaryColor,
      ),
      body: FlutterMap(
        options: MapOptions(
            initialCenter: LatLng(24.5, -90.0),
            initialZoom: 5.0,
            interactionOptions: InteractionOptions(
              rotationThreshold: 100.0,
            )),
        children: [
          TileLayer(
            urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
            userAgentPackageName: 'com.example.spill_sentinel',
          ),
          MarkerLayer(markers: markers),
        ],
      ),
    );
  }

  @override
  void dispose() {
    aisClient.closeConnection();
    super.dispose();
  }
}
