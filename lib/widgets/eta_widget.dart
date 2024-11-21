import 'package:flutter/material.dart';
import 'package:intl/intl.dart'; // For formatting dates and times

class ETAWidget extends StatelessWidget {
  final Map<String, dynamic> eta; // ETA in {Day, Hour, Minute, Month} format

  const ETAWidget({
    required this.eta,
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final etaDate = _convertToDate(eta);

    return SizedBox(
      width: double.infinity,
      child: Card(
        margin: const EdgeInsets.symmetric(
          vertical: 8,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(15),
        ),
        elevation: 4,
        child: Container(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const Text(
                "Estimated Time of Arrival",
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.teal,
                ),
              ),
              const SizedBox(height: 8),
              // ETA as a label
              _buildETALabel(etaDate),
              const SizedBox(height: 12),
              // Time Remaining Section
              _buildTimeRemaining(etaDate),
            ],
          ),
        ),
      ),
    );
  }

  // Converts the ETA map into a DateTime object
  DateTime _convertToDate(Map<String, dynamic> eta) {
    // Construct a DateTime object from the ETA map (assuming current year and day provided)
    DateTime now = DateTime.now();
    return DateTime(
      now.year,
      eta['Month'] ?? now.month,
      eta['Day'] ?? now.day,
      eta['Hour'] ?? 0,
      eta['Minute'] ?? 0,
    );
  }

  // Builds the ETA label
  Widget _buildETALabel(DateTime etaDate) {
    final formattedETA = _formatETA(etaDate);

    return Container(
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
      decoration: BoxDecoration(
        color: Colors.teal.shade50,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        "ETA: $formattedETA",
        style: TextStyle(
          fontSize: 22,
          fontWeight: FontWeight.bold,
          color: Colors.teal.shade800,
        ),
      ),
    );
  }

  // Formats the ETA into a human-readable format (e.g., "21 Nov, 4:30 AM")
  String _formatETA(DateTime etaDate) {
    final DateFormat dateFormat = DateFormat('d MMM, h:mm a');
    return dateFormat.format(etaDate);
  }

  // Builds the time remaining section
  Widget _buildTimeRemaining(DateTime etaDate) {
    final remainingTime = _calculateTimeRemaining(etaDate);

    return Text(
      remainingTime,
      style: TextStyle(
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: remainingTime.contains("Already Arrived")
            ? Colors.green.shade700
            : Colors.teal.shade700,
      ),
    );
  }

  // Calculates the remaining time until the ETA
  String _calculateTimeRemaining(DateTime etaDate) {
    final now = DateTime.now();
    final difference = etaDate.difference(now);

    if (difference.isNegative) {
      return "Already Arrived"; // If ETA has passed
    }

    final daysLeft = difference.inDays;
    final hoursLeft = difference.inHours % 24;
    final minutesLeft = difference.inMinutes % 60;

    if (daysLeft > 0) {
      return "$daysLeft days $hoursLeft hrs $minutesLeft min remaining";
    } else {
      return "$hoursLeft hrs $minutesLeft min remaining";
    }
  }
}
