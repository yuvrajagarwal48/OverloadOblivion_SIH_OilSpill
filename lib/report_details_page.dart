import 'package:flutter/material.dart';
import 'dart:convert';

import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

class ReportDetailPage extends StatelessWidget {
  final Map<String, dynamic> report;

  const ReportDetailPage({Key? key, required this.report}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final aisData = report['ais_data'] ?? {};
    final anomalyResult = report['anomaly_result'] ?? {};
    final sarPrediction = report['sar_prediction'] ?? {};

    return Scaffold(
      appBar: AppBar(
        title: Text(aisData['NAME'] ?? 'Report Details'),
        backgroundColor: Colors.blue,
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Ship Information Section
            _buildSectionTitle('Ship Information'),
            _buildKeyValue('Name', aisData['NAME']),
            _buildKeyValue('MMSI', aisData['MMSI']),
            _buildKeyValue('IMO', aisData['IMO']),
            _buildKeyValue('Latitude', aisData['LATITUDE']),
            _buildKeyValue('Longitude', aisData['LONGITUDE']),
            _buildKeyValue('Course', aisData['COURSE']),
            _buildKeyValue('Speed', aisData['SPEED']),
            _buildKeyValue('Heading', aisData['HEADING']),
            _buildKeyValue('NavStat', aisData['NAVSTAT']),
            _buildKeyValue('Destination', aisData['DESTINATION']),
            _buildKeyValue('ETA', aisData['ETA']),
            SizedBox(height: 20),
            _buildMap(aisData['LATITUDE'], aisData['LONGITUDE']),
            // Anomaly Result Section
            _buildSectionTitle('Anomaly Result'),
            _buildKeyValue('Anomaly Detected', anomalyResult['anomaly']),
            _buildKeyValue(
                'Anomaly Probability', anomalyResult['anomaly_probability']),
            SizedBox(height: 10),

            _buildKeyValue('Oil Spill Area', sarPrediction['Oilspill_area']),
            SizedBox(height: 10),
            _buildImageSection(
                'Annotated Image', sarPrediction['Annotated_image']),
            _buildImageSection(
              'Force Plot',
              anomalyResult['force_plot'],
            ),
            _buildImageSection(
              'Waterfall Plot',
              anomalyResult['waterfall_plot'],
            ),
            // _buildImageSection(
            //   'Feature Contribution Plot',
            //   anomalyResult['feature_contribution_plot'],
            // ),
            SizedBox(height: 20),

            // SAR Prediction Section
            _buildSectionTitle('SAR Prediction'),
            _buildKeyValue('Predicted Class', sarPrediction['Predicted Class']),
            _buildImageSection(
                'Original Image', sarPrediction['Original Image']),
            _buildImageSection('SAR Mask', sarPrediction['SAR_mask']),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: TextStyle(
          fontSize: 20, fontWeight: FontWeight.bold, color: Colors.blue),
    );
  }

  Widget _buildKeyValue(String key, dynamic value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        children: [
          Expanded(
            flex: 3,
            child: Text(
              key,
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
          ),
          Expanded(
            flex: 5,
            child: Text(
              value != null ? value.toString() : 'N/A',
              style: TextStyle(fontSize: 16),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildImageSection(String title, String? base64String) {
    if (base64String == null || base64String.isEmpty) {
      return SizedBox.shrink();
    }

    try {
      final imageBytes = base64Decode(base64String);
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(height: 10),
          Text(
            title,
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w500),
          ),
          SizedBox(height: 10),
          Container(
            height: 200,
            width: double.infinity,
            decoration: BoxDecoration(
              border: Border.all(color: Colors.grey),
              borderRadius: BorderRadius.circular(8),
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Image.memory(imageBytes, fit: BoxFit.cover),
            ),
          ),
          SizedBox(height: 20),
        ],
      );
    } catch (e) {
      return Text('Error displaying $title image');
    }
  }
}

Widget _buildMap(double latitude, double longitude) {
  return Container(
    height: 300,
    decoration: BoxDecoration(
      border: Border.all(color: Colors.grey),
      borderRadius: BorderRadius.circular(8),
    ),
    child: Stack(
      children: [
        // Map Display
        FlutterMap(
          options: MapOptions(
            initialCenter: LatLng(latitude, longitude),
            initialZoom: 5.0,
            interactionOptions: InteractionOptions(
                flags: InteractiveFlag.none), // Disables movement/zoom
          ),
          children: [
            TileLayer(
              urlTemplate: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
              subdomains: ['a', 'b', 'c'],
            ),
            MarkerLayer(
              markers: [
                Marker(
                  point: LatLng(latitude, longitude),
                  child: Icon(
                    Icons.location_on,
                    size: 30,
                    color: Colors.red,
                  ),
                ),
              ],
            ),
            // Horizontal Latitude Lines
            PolylineLayer(
              polylines: [
                Polyline(
                  points: [
                    LatLng(latitude, -180),
                    LatLng(latitude, 180),
                  ],
                  color: Colors.blue,
                  strokeWidth: 2.0,
                ),
                Polyline(
                  points: [
                    LatLng(latitude - 2, -180),
                    LatLng(latitude - 2, 180),
                  ],
                  color: Colors.lightBlue,
                  strokeWidth: 1.0,
                ),
                Polyline(
                  points: [
                    LatLng(latitude + 2, -180),
                    LatLng(latitude + 2, 180),
                  ],
                  color: Colors.lightBlue,
                  strokeWidth: 1.0,
                ),
                Polyline(
                  points: [
                    LatLng(latitude - 4, -180),
                    LatLng(latitude - 4, 180),
                  ],
                  color: Colors.lightBlue,
                  strokeWidth: 1.0,
                ),
                Polyline(
                  points: [
                    LatLng(latitude + 4, -180),
                    LatLng(latitude + 4, 180),
                  ],
                  color: Colors.lightBlue,
                  strokeWidth: 1.0,
                ),
                Polyline(
                  points: [
                    LatLng(latitude - 6, -180),
                    LatLng(latitude - 6, 180),
                  ],
                  color: Colors.lightBlue,
                  strokeWidth: 1.0,
                ),
                Polyline(
                  points: [
                    LatLng(latitude + 6, -180),
                    LatLng(latitude + 6, 180),
                  ],
                  color: Colors.lightBlue,
                  strokeWidth: 1.0,
                ),
              ],
            ),
            // Vertical Longitude Lines
            PolylineLayer(
              polylines: [
                Polyline(
                  points: [
                    LatLng(-90, longitude),
                    LatLng(90, longitude),
                  ],
                  color: Colors.blue,
                  strokeWidth: 2.0,
                ),
                Polyline(
                  points: [
                    LatLng(-90, longitude - 2),
                    LatLng(90, longitude - 2),
                  ],
                  color: Colors.lightBlue,
                  strokeWidth: 1.0,
                ),
                Polyline(
                  points: [
                    LatLng(-90, longitude + 2),
                    LatLng(90, longitude + 2),
                  ],
                  color: Colors.lightBlue,
                  strokeWidth: 1.0,
                ),
                Polyline(
                  points: [
                    LatLng(-90, longitude - 4),
                    LatLng(90, longitude - 4),
                  ],
                  color: Colors.lightBlue,
                  strokeWidth: 1.0,
                ),
                Polyline(
                  points: [
                    LatLng(-90, longitude + 4),
                    LatLng(90, longitude + 4),
                  ],
                  color: Colors.lightBlue,
                  strokeWidth: 1.0,
                ),
                Polyline(
                  points: [
                    LatLng(-90, longitude - 6),
                    LatLng(90, longitude - 6),
                  ],
                  color: Colors.lightBlue,
                  strokeWidth: 1.0,
                ),
                Polyline(
                  points: [
                    LatLng(-90, longitude + 6),
                    LatLng(90, longitude + 6),
                  ],
                  color: Colors.lightBlue,
                  strokeWidth: 1.0,
                ),
              ],
            ),
          ],
        ),
        // Bounding Box
        Positioned(
          left: 160, // Center the box on the marker
          top: 130,
          child: Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              border: Border.all(color: Colors.blue, width: 2),
              color: Colors.transparent,
            ),
          ),
        ),
        // Latitude and Longitude Labels
        Positioned(
          left: 10,
          top: 120, // Align with marker latitude
          child: Text(
            '${latitude.toStringAsFixed(2)}°',
            style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold),
          ),
        ),
        Positioned(
          left: 140,
          top: 10, // Align with marker longitude
          child: Text(
            '${longitude.toStringAsFixed(2)}°',
            style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold),
          ),
        ),
        // Labels for Parallel Latitude Lines
        Positioned(
          left: 10,
          top: 90, // Slightly above marker
          child: Text(
            '${(latitude - 2).toStringAsFixed(2)}°',
            style: TextStyle(color: Colors.grey, fontSize: 12),
          ),
        ),
        Positioned(
          left: 10,
          top: 150, // Slightly below marker
          child: Text(
            '${(latitude + 2).toStringAsFixed(2)}°',
            style: TextStyle(color: Colors.grey, fontSize: 12),
          ),
        ),
        // Labels for Parallel Longitude Lines
        Positioned(
          left: 110, // Slightly left of marker
          top: 10,
          child: Text(
            '${(longitude - 2).toStringAsFixed(2)}°',
            style: TextStyle(color: Colors.grey, fontSize: 12),
          ),
        ),
        Positioned(
          left: 170, // Slightly right of marker
          top: 10,
          child: Text(
            '${(longitude + 2).toStringAsFixed(2)}°',
            style: TextStyle(color: Colors.grey, fontSize: 12),
          ),
        ),
      ],
    ),
  );
}
