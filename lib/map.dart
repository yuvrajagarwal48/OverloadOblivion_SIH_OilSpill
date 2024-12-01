import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:spill_sentinel/connection.dart';
import 'package:spill_sentinel/secrets.dart';
//import 'ais_api_client.dart'; // Import the AISApiClient class
import 'ship_details_screen.dart';

class MapScreen extends StatefulWidget {
  const MapScreen({super.key});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  late AISApiClient aisClient; // Use AISApiClient for data polling
  final Map<int, Map<String, dynamic>> shipDataMap = {}; // Ship data by MMSI
  List<Marker> markers = []; // Markers dynamically generated from shipDataMap

  @override
  void initState() {
    super.initState();

    // Initialize AISApiClient with the API URL
    aisClient = AISApiClient(
        "https://api.vtexplorer.com/vesselslist?userkey=${Secrets.aisstreamApiKey}"); // Replace with your API URL
    aisClient.startPolling(); // Start API polling

    // Listen to the AIS data stream
    aisClient.aisStreamController.stream.listen((aisDataRaw) {
      _processAISData(aisDataRaw['AIS']); // Process individual AIS dat ca
      _updateMarkers();
    });
  }

  /// Process individual AIS data and update the shipDataMap
  void _processAISData(Map<String, dynamic> aisData) {
    final mmsi = aisData['MMSI'];
    final latitude = aisData['LATITUDE'];
    final longitude = aisData['LONGITUDE'];

    if (mmsi != null && latitude != null && longitude != null) {
      // Update or add ship data
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
        'DistanceRemaining': aisData['DISTANCE_REMAINING']?.toString() ?? "N/A",
        'ETA_Predicted': aisData['ETA_PREDICTED'] ?? "N/A",
        'Type': aisData['TYPE'] ?? "Unknown",
        'A': aisData['A'] ?? "Unknown",
        'B': aisData['B'] ?? "Unknown",
        'C': aisData['C'] ?? "Unknown",
        'D': aisData['D'] ?? "Unknown",
      };
    }
  }

  /// Updates the markers list based on the current shipDataMap
  void _updateMarkers() {
    markers = shipDataMap.values
        .map((shipData) {
          final position = shipData['Position'] as LatLng?;
          if (position == null) return null; // Skip if position is missing

          return Marker(
            width: 30.0,
            height: 30.0,
            point: position,
            child: GestureDetector(
              onTap: () => _navigateToShipDetails(shipData),
              child: Tooltip(
                message:
                    'Ship: ${shipData['ShipName'] ?? "Unknown Ship"}\nMMSI: ${shipData['MMSI']}',
                child: const Icon(
                  Icons.directions_boat,
                  size: 30.0,
                  color: Colors.blue,
                ),
              ),
            ),
          );
        })
        .whereType<Marker>()
        .toList(); // Filter out null markers

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
            'ETA': shipData['ETA'] ?? "N/A",
            'Status': shipData['Status'] ?? "N/A",
            'Speed': shipData['Speed'] ?? "0 kn",
            'Draught': shipData['Draught'] ?? "Unknown",
            'Heading': shipData['Heading'] ?? "N/A",
            'Position': shipData['Position'],
            'CallSign': shipData['CallSign'] ?? "Unknown",
            'IMO': shipData['IMO'] ?? "Unknown",
            'Destination': shipData['Destination'] ?? "N/A",
            'DistanceRemaining': shipData['DistanceRemaining'] ?? "N/A",
            'ETA_Predicted': shipData['ETA_Predicted'] ?? "N/A",
            'Timestamp': shipData['Timestamp'] ?? "N/A",
            'Zone': shipData['Zone'] ?? "N/A",
            'Type': shipData['Type'] ?? "Unknown",
            'A': shipData['A'] ?? "Unknown",
            'B': shipData['B'] ?? "Unknown",
            'C': shipData['C'] ?? "Unknown",
            'D': shipData['D'] ?? "Unknown",
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
    aisClient.stopPolling(); // Stop polling and close the stream
    super.dispose();
  }
}
