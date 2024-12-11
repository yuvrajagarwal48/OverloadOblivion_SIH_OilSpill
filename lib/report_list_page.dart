import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'dart:convert';

import 'package:spill_sentinel/report_details_page.dart';

class ReportsGridPage extends StatefulWidget {
  const ReportsGridPage({super.key});

  @override
  State<ReportsGridPage> createState() => _ReportsGridPageState();
}

class _ReportsGridPageState extends State<ReportsGridPage> {
  final int _pageSize = 10; // Number of items per page
  DocumentSnapshot?
      _lastDocument; // Keeps track of the last document for pagination
  final List<DocumentSnapshot> _reports = []; // Stores loaded reports
  bool _isLoading = false;
  bool _hasMore = true; // Tracks if more data is available

  @override
  void initState() {
    super.initState();
    _fetchReports(); // Fetch the first page
  }

  Future<void> _fetchReports() async {
    if (_isLoading || !_hasMore) return;

    setState(() {
      _isLoading = true;
    });

    try {
      Query query = FirebaseFirestore.instance
          .collection('reports')
          .orderBy('timestamp', descending: true)
          .limit(_pageSize);

      if (_lastDocument != null) {
        query = query.startAfterDocument(_lastDocument!);
      }

      final querySnapshot = await query.get();
      final fetchedReports = querySnapshot.docs;

      if (fetchedReports.isNotEmpty) {
        setState(() {
          _lastDocument = fetchedReports.last;
          _reports.addAll(fetchedReports);
        });
      }

      if (fetchedReports.length < _pageSize) {
        setState(() {
          _hasMore = false;
        });
      }
    } catch (e) {
      print('Error fetching reports: $e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Reports'),
        backgroundColor: Colors.blue,
      ),
      body: NotificationListener<ScrollNotification>(
        onNotification: (ScrollNotification scrollInfo) {
          if (!_isLoading &&
              _hasMore &&
              scrollInfo.metrics.pixels == scrollInfo.metrics.maxScrollExtent) {
            _fetchReports(); // Fetch more data when reaching the bottom
          }
          return false;
        },
        child: GridView.builder(
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2, // Number of items in a row
            crossAxisSpacing: 10,
            mainAxisSpacing: 10,
            childAspectRatio: 0.8,
          ),
          padding: const EdgeInsets.all(10),
          itemCount: _reports.length + (_hasMore ? 1 : 0), // Add loader item
          itemBuilder: (context, index) {
            if (index == _reports.length) {
              return const Center(child: CircularProgressIndicator());
            }

            final report = _reports[index].data() as Map<String, dynamic>?;

            if (report == null) {
              return const SizedBox.shrink();
            }

            final shipName = report['ais_data']?['NAME'] ?? 'Unknown';
            final limeImageBase64 =
                report['sar_prediction']?['Original Image'] ?? '';

            return _buildReportCard(context, report, shipName, limeImageBase64);
          },
        ),
      ),
    );
  }

  Widget _buildReportCard(BuildContext context, Map<String, dynamic> report,
      String shipName, String limeImageBase64) {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ReportDetailPage(report: report),
          ),
        );
      },
      child: Card(
        elevation: 4,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Expanded(
              child: ClipRRect(
                borderRadius:
                    const BorderRadius.vertical(top: Radius.circular(12)),
                child: _buildImage(limeImageBase64),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Text(
                shipName,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildImage(String base64String) {
    if (base64String.isEmpty) {
      return const Icon(Icons.image_not_supported,
          size: 50, color: Colors.grey);
    }
    try {
      final imageBytes = base64Decode(base64String);
      return Image.memory(
        imageBytes,
        fit: BoxFit.cover,
        errorBuilder: (context, error, stackTrace) => const Icon(
          Icons.broken_image,
          size: 50,
          color: Colors.grey,
        ),
      );
    } catch (e) {
      print('Error decoding image: $e');
      return const Icon(Icons.broken_image, size: 50, color: Colors.grey);
    }
  }
}
