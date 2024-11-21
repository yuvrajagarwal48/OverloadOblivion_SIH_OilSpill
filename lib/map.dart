import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:spill_sentinel/connection.dart';
import 'package:spill_sentinel/ship_details_screen.dart';

class MapScreen extends StatefulWidget {
  const MapScreen({super.key});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  late AISStreamWebsocketClient aisClient;
  final StreamController<dynamic> aisStreamController = StreamController.broadcast();

  final Map<int, Map<String, dynamic>> shipDataMap = {}; // Store all ship data keyed by MMSI
  List<Marker> markers = []; // Markers dynamically generated from shipDataMap

  @override
  void initState() {
    super.initState();

    // Initialize and connect AIS client
    aisClient = AISStreamWebsocketClient(
      'wss://stream.aisstream.io/v0/stream',
      aisStreamController,
    );
    aisClient.connect();

    // Listen to AIS data and process updates
    aisStreamController.stream.listen((message) {
      if (message['MessageType'] == 'PositionReport') {
        _processPositionReport(message);
      } else if (message['MessageType'] == 'ShipStaticData') {
        _processShipStaticData(message);
      }
    });
  }

  /// Process PositionReport data
  void _processPositionReport(dynamic message) {
    final positionReport = message['Message']['PositionReport'];
    final metadata = message['MetaData'];
    final latitude = positionReport['Latitude'];
    final longitude = positionReport['Longitude'];
    final mmsi = metadata['MMSI'];

    if (latitude != null && longitude != null && mmsi != null) {
      // Update or create a new entry in shipDataMap
      final existingData = shipDataMap[mmsi] ?? {};
      shipDataMap[mmsi] = {
        ...existingData,
        'MMSI': mmsi,
        'ShipName': metadata['ShipName']?.trim() ?? "Unknown Ship",
        'Position': LatLng(latitude, longitude),
        'Speed': '${positionReport['Sog'] ?? "0"} kn',
        'Heading': '${positionReport['TrueHeading'] ?? "N/A"}°',
        'Status': positionReport['NavigationalStatus']?.toString() ?? "N/A",
        'ATD': metadata['time_utc'],
        'RateOfTurn': positionReport['RateOfTurn']?.toString() ?? "N/A",
      };

      _updateMarkers();
    }
  }

  /// Process ShipStaticData
  void _processShipStaticData(dynamic message) {
    final staticData = message['Message']['ShipStaticData'];
    final metadata = message['MetaData'];
    final mmsi = metadata['MMSI'];
    final shipName = metadata['ShipName']?.trim() ?? "Unknown Ship";

    if (mmsi != null) {
      // Update or create a new entry in shipDataMap
      final existingData = shipDataMap[mmsi] ?? {};
      shipDataMap[mmsi] = {
        ...existingData,
        'MMSI': mmsi,
        'ShipName': shipName,
        'CallSign':staticData['CallSign'] ?? "Unknown",
        'Destination': staticData['Destination'] ?? "N/A",
        'IMO': staticData['ImoNumber'] ?? "Unknown",
        'Flag': staticData['Flag'] ?? "Unknown",
        'Draught': staticData['MaximumStaticDraught']?.toString() ?? "Unknown",
        'ETA': staticData['Eta'] ?? "N/A",
        'Dimension': staticData['Dimension'] ?? {},
      };

      _updateMarkers();
    }
  }

  /// Updates the markers list based on the current shipDataMap
  void _updateMarkers() {
    markers = shipDataMap.values.map((shipData) {
      final position = shipData['Position'] as LatLng?;
      if (position == null) return null; // Skip if position is missing

      return Marker(
        width: 30.0,
        height: 30.0,
        point: position,
        child: GestureDetector(
          onTap: () => _navigateToShipDetails(shipData),
          child: Tooltip(
            message: 'Ship: ${shipData['ShipName'] ?? "Unknown Ship"}\nMMSI: ${shipData['MMSI']}',
            child: const Icon(
              Icons.directions_boat,
              size: 30.0,
              color: Colors.blue,
            ),
          ),
        ),
      );
    }).whereType<Marker>().toList(); // Filter out null markers

    setState(() {});
  }

  /// Navigate to ShipDetailsScreen with detailed ship data
  void _navigateToShipDetails(Map<String, dynamic> shipData) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ShipDetailsScreen(
          shipData: {
            'ShipName': shipData['ShipName'] ?? "Unknown Ship",
            'MMSI': shipData['MMSI'],
            'Flag': shipData['Flag'] ?? "Unknown",
            'ATD': shipData['ATD'] ?? "N/A",
            'ETA': shipData['ETA'] ?? "N/A",
            'Status': shipData['Status'] ?? "N/A",
            'Speed': shipData['Speed'] ?? "0 kn",
            'Draught': shipData['Draught'] ?? "Unknown",
            'Heading': shipData['Heading'] ?? "N/A",
            'Position': shipData['Position'],
            'Dimension': shipData['Dimension'] ?? {},
            'CallSign': shipData['CallSign'] ?? "Unknown",
            'IMO': shipData['IMO'] ?? "Unknown",
            'Destination': shipData['Destination'] ?? "N/A",
            'RateOfTurn': shipData['RateOfTurn'] ?? "N/A",
            
          },
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("AIS Ship Map"),
        backgroundColor: Colors.teal.shade800,
      ),
      body: FlutterMap(
        options: MapOptions(
          initialCenter: LatLng(24.5, -90.0), // Default map center
          initialZoom: 5.0, // Default zoom level
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
    aisStreamController.close();
    super.dispose();
  }
}
