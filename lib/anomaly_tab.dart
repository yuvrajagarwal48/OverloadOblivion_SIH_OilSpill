import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/material.dart';
import 'package:spill_sentinel/core/theme/app_pallete.dart';
import 'package:spill_sentinel/features/auth/presentation/widgets/auth_button.dart';
import 'package:spill_sentinel/report_details_page.dart';

class AnomalyTab extends StatefulWidget {
  final Map<String, dynamic> shipData;

  const AnomalyTab({required this.shipData, Key? key}) : super(key: key);

  @override
  State<AnomalyTab> createState() => _AnomalyTabState();
}

class _AnomalyTabState extends State<AnomalyTab> {
  late Future<Map<String, dynamic>?> _reportFuture;

  @override
  void initState() {
    super.initState();
    _reportFuture = _fetchAnomalyReport(int.parse(widget.shipData['MMSI']));
    print('MMSI: ${widget.shipData['MMSI']}');
  }

  Future<Map<String, dynamic>?> _fetchAnomalyReport(int mmsi) async {
    try {
      final querySnapshot = await FirebaseFirestore.instance
          .collection('reports')
          .where('MMSI', isEqualTo: mmsi)
          .limit(1)
          .get();

      if (querySnapshot.docs.isNotEmpty) {
        // Return the first document as a map
        print(querySnapshot.docs.first.data());
        return querySnapshot.docs.first.data();
      } else {
        // Return null if no document is found
        return null;
      }
    } catch (e) {
      print('Error fetching report: $e');
      return null;
    }
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Map<String, dynamic>?>(
      future: _reportFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }

        if (snapshot.hasError) {
          return Center(
            child: Text(
              'Error fetching data: ${snapshot.error}',
              style: const TextStyle(color: Colors.red),
            ),
          );
        }

        final report = snapshot.data;

        return Center(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Card(
              color: Pallete.secondaryColor.withOpacity(0.9),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(20),
              ),
              elevation: 6,
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'Anomaly Detection',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Pallete.whiteColor,
                      ),
                    ),
                    const SizedBox(height: 24),
                    _buildProbabilityIndicator(
                      'Anomaly Probability',
                      widget.shipData['AnomalyProbability'] ?? 0.0,
                    ),
                    const SizedBox(height: 24),
                    AuthButton(
                      text: 'See Anomaly Report',
                      onPressed: report != null
                          ? () {
                              Navigator.of(context).push(
                                MaterialPageRoute(
                                  builder: (context) =>
                                      ReportDetailPage(report: report),
                                ),
                              );
                            }
                          : null,
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildProbabilityIndicator(String label, double probability) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        LinearProgressIndicator(
          value: probability,
          color: Colors.green,
          backgroundColor: Colors.grey[300],
        ),
        const SizedBox(height: 8),
        Text('${(probability * 100).toStringAsFixed(1)}%'),
      ],
    );
  }
}
