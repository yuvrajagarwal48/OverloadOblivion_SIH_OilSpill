import 'package:flutter/material.dart';
import 'dart:convert';

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

            // Anomaly Result Section
            _buildSectionTitle('Anomaly Result'),
            _buildKeyValue('Anomaly Detected', anomalyResult['anomaly']),
            _buildKeyValue(
                'Anomaly Probability', anomalyResult['anomaly_probability']),
            SizedBox(height: 10),
            _buildKeyValue('Oil Spill Probability',
                anomalyResult['oil_spill_probability']),
            SizedBox(height: 10),

            _buildImageSection(
              'Force Plot',
              anomalyResult['force_plot'],
            ),
            _buildImageSection(
              'Waterfall Plot',
              anomalyResult['waterfall_plot'],
            ),
            _buildImageSection(
              'Feature Contribution Plot',
              anomalyResult['feature_contribution_plot'],
            ),
            SizedBox(height: 20),

            // SAR Prediction Section
            _buildSectionTitle('SAR Prediction'),
            _buildKeyValue('Predicted Class', sarPrediction['Predicted Class']),
            _buildImageSection(
                'Original Image', sarPrediction['Original Image']),
            _buildImageSection(
                'LIME Explanation', sarPrediction['LIME Explanation']),
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
