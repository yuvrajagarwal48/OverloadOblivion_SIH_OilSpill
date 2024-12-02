import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
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
      },
      onError: (error) {
        print('Stream error: $error');
      },
      onDone: () {
        print('Stream closed.');
      },
    );
  }

  /// Process AIS data and anomaly results
  void _processAISData(
      Map<String, dynamic> aisData, Map<String, dynamic> anomalyResult) {
    final mmsi = aisData['MMSI'];
    final latitude = aisData['LATITUDE'];
    final longitude = aisData['LONGITUDE'];

    if (mmsi != null && latitude != null && longitude != null) {
      shipDataMap[mmsi] = {
        'MMSI': mmsi,
        'ShipName': aisData['NAME'] ?? "Unknown Ship",
        'Position': LatLng(latitude, longitude),
        'Speed': '${aisData['SPEED'] ?? "0"} kn',
        'Heading': '${aisData['HEADING'] ?? "N/A"}°',
        'Status': aisData['NAVSTAT']?.toString() ?? "N/A",
        'ETA': aisData['ETA'] ?? "N/A",
        'Destination': aisData['DESTINATION'] ?? "N/A",
        'Draught': aisData['DRAUGHT']?.toString() ?? "Unknown",
        'CallSign': aisData['CALLSIGN'] ?? "Unknown",
        'IMO': aisData['IMO'] ?? "Unknown",
        'Timestamp': aisData['TIMESTAMP'] ?? "N/A",
        'Zone': aisData['ZONE'] ?? "N/A",
        'Anomaly': anomalyResult['anomaly'] ?? false, // Anomaly status
        'AnomalyProbability': anomalyResult['anomaly_probability'] ?? 0.0,
        'OilSpillProbability': anomalyResult['oil_spill_probability'] ?? 0.0,
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

          return Marker(
            width: 30.0,
            height: 30.0,
            point: position,
            child: GestureDetector(
              onTap: () => _navigateToShipDetails(shipData),
              child: Tooltip(
                message:
                    'Ship: ${shipData['ShipName']}\nMMSI: ${shipData['MMSI']}',
                child: Icon(
                  Icons.directions_boat,
                  size: 30.0,
                  color: isAnomalous
                      ? Colors.red
                      : Colors.blue, // Red for anomalies
                ),
              ),
            ),
          );
        })
        .whereType<Marker>()
        .toList();

    setState(() {});
  }

  /// Navigate to ShipDetailsScreen
  void _navigateToShipDetails(Map<String, dynamic> shipData) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ShipDetailsScreen(
          shipData: {
            'ShipName': shipData['ShipName'] ?? "Unknown Ship",
            'MMSI': shipData['MMSI'],
            'Flag': shipData['Flag'] ?? "Unknown",
            'ETA': shipData['ETA'] ?? "N/A",
            'Status': shipData['Status'] ?? "N/A",
            'Speed': shipData['Speed'] ?? "0 kn",
            'Draught': shipData['Draught'] ?? "Unknown",
            'Heading': shipData['Heading'] ?? "N/A",
            'Position': shipData['Position'],
            'CallSign': shipData['CallSign'] ?? "Unknown",
            'IMO': shipData['IMO'] ?? "Unknown",
            'Destination': shipData['Destination'] ?? "N/A",
            'Timestamp': shipData['Timestamp'] ?? "N/A",
            'Zone': shipData['Zone'] ?? "N/A",
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
        title:
            const Text("Spill Sentinel", style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.teal.shade800,
      ),
      body: FlutterMap(
        options: MapOptions(
          initialCenter: LatLng(24.5, -90.0),
          initialZoom: 5.0,
        ),
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
