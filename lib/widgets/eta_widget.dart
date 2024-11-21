import 'package:flutter/material.dart';
import 'package:intl/intl.dart'; // For formatting dates and times
import 'package:intl/intl.dart' as intl;
import 'package:flutter/cupertino.dart';

class ETAWidget extends StatelessWidget {
  final Map<String, dynamic> eta; // ETA in {Day, Hour, Minute, Month} format
  final double
      progress; // Progress from 0.0 to 1.0 (0.0 = ship just started, 1.0 = ETA reached)

  const ETAWidget({
    required this.eta,
    required this.progress,
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final etaDate = _convertToDate(eta);

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
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
            // Circular Progress Bar
            Stack(
              alignment: Alignment.center,
              children: [
                SizedBox(
                  height: 120,
                  width: 120,
                  child: CircularProgressIndicator(
                    value: progress,
                    strokeWidth: 8,
                    valueColor:
                        AlwaysStoppedAnimation<Color>(Colors.teal.shade400),
                    backgroundColor: Colors.teal.shade100,
                  ),
                ),
                Text(
                  _formatETA(etaDate),
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.teal,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            // Time Remaining Section
            Text(
              "Time remaining: ${_calculateTimeRemaining(etaDate)}",
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w500,
                color: Colors.teal.shade700,
              ),
            ),
          ],
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

  // Formats the ETA into a human-readable format (e.g., "21 Nov, 4:30 AM")
  String _formatETA(DateTime etaDate) {
    final DateFormat dateFormat = DateFormat('d MMM, h:mm a');
    return dateFormat.format(etaDate);
  }

  // Calculates the remaining time until the ETA
  String _calculateTimeRemaining(DateTime etaDate) {
    final now = DateTime.now();
    final difference = etaDate.difference(now);

    if (difference.isNegative) {
      return "Already Arrived"; // If ETA has passed
    }

    final hoursLeft = difference.inHours;
    final minutesLeft = difference.inMinutes % 60;

    return "$hoursLeft hr $minutesLeft min";
  }
}
