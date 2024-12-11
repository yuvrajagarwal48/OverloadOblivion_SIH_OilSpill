import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

class VoyageDetailsCard extends StatelessWidget {
  final Map<String, dynamic> shipData;
  final double progress;

  const VoyageDetailsCard({
    Key? key,
    required this.shipData,
    this.progress = 0.7,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
      ),
      elevation: 8,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          gradient: LinearGradient(
            colors: [
              Colors.blue.shade50,
              Colors.white,
            ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              _buildHeader(context),

              const SizedBox(height: 20),

              // Journey Progress
              _buildJourneyProgress(context),

              const SizedBox(height: 16),

              // Additional Details
              _buildAdditionalDetails(context),
            ],
          ),
        ),
      ),
    ).animate().fadeIn(duration: 500.ms).slideY(begin: 0.1, end: 0);
  }

  Widget _buildHeader(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          'Voyage Tracking',
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: Colors.blue.shade800,
              ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: Colors.blue.shade100.withOpacity(0.5),
            borderRadius: BorderRadius.circular(15),
          ),
          child: Text(
            'Active',
            style: TextStyle(
              color: Colors.blue.shade900,
              fontWeight: FontWeight.w600,
            ),
          ),
        )
      ],
    );
  }

  Widget _buildJourneyProgress(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Route Information
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              shipData['SRC'] ?? 'Origin',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            Text(
              shipData['Destination'] ?? 'Destination',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ],
        ),

        const SizedBox(height: 8),

        // Progress Bar
        ClipRRect(
          borderRadius: BorderRadius.circular(10),
          child: LinearProgressIndicator(
            value: progress,
            minHeight: 10,
            backgroundColor: Colors.blue.shade100,
            valueColor: AlwaysStoppedAnimation<Color>(Colors.blue.shade600),
          ),
        ),

        const SizedBox(height: 12),

        // Distance and Estimated Details
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Distance Remaining: ${shipData['DistanceRemaining'] ?? 0} nm',
              style: TextStyle(color: Colors.grey.shade700),
            ),
            Text(
              'ETA: ${shipData['ETAAIS'] ?? 'N/A'}',
              style: TextStyle(color: Colors.grey.shade700),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildAdditionalDetails(BuildContext context) {
    return Wrap(
      spacing: 10,
      runSpacing: 10,
      children: [
        _buildDetailChip(
          'Route Code',
          shipData['LOCODE'] ?? 'N/A',
          Icons.route,
        ),
        _buildDetailChip(
          'ECA Status',
          (shipData['ECA'] ?? false) ? 'In ECA' : 'Outside ECA',
          Icons.eco,
        ),
        _buildDetailChip(
          'Predicted ETA',
          shipData['ETAPredicted'] ?? 'N/A',
          Icons.timelapse,
        ),
      ],
    );
  }

  Widget _buildDetailChip(String label, String value, IconData icon) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.blue.shade100, width: 1),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: Colors.blue.shade600),
          const SizedBox(width: 8),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: TextStyle(
                  fontSize: 10,
                  color: Colors.blue.shade800,
                  fontWeight: FontWeight.w600,
                ),
              ),
              Text(
                value,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
