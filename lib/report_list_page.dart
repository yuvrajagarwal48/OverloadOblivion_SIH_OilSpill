import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'dart:convert';

import 'package:spill_sentinel/report_details_page.dart';

class ReportsGridPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Reports'),
        backgroundColor: Colors.blue,
      ),
      body: StreamBuilder(
        stream: FirebaseFirestore.instance
            .collection('reports')
            .snapshots()
            .where((event) => event.docs.isNotEmpty),
        builder: (BuildContext context, AsyncSnapshot<QuerySnapshot> snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return Center(child: CircularProgressIndicator());
          }

          if (!snapshot.hasData || snapshot.data!.docs.isEmpty) {
            return Center(
              child: Text(
                'No reports found',
                style: TextStyle(fontSize: 18, color: Colors.grey),
              ),
            );
          }

          final reports = snapshot.data!.docs.where((doc) =>
              (doc.data()! as Map<String, dynamic>)['sar_prediction']
                  ['Predicted Class'] ==
              1);

          return GridView.builder(
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2, // Number of items in a row
              crossAxisSpacing: 10,
              mainAxisSpacing: 10,
              childAspectRatio: 0.8,
            ),
            padding: EdgeInsets.all(10),
            itemCount: reports.length,
            itemBuilder: (context, index) {
              final report =
                  reports.elementAt(index).data() as Map<String, dynamic>;
              final shipName = report['ais_data']['NAME'] ?? 'Unknown';
              final limeImageBase64 =
                  report['sar_prediction']['Original Image'] ?? '';

              // Decode the base64 string to display the image
              final limeImage = limeImageBase64.isNotEmpty
                  ? Image.memory(base64Decode(limeImageBase64))
                  : Icon(Icons.image_not_supported,
                      size: 50, color: Colors.grey);

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
                              BorderRadius.vertical(top: Radius.circular(12)),
                          child: limeImageBase64.isNotEmpty
                              ? limeImage
                              : Icon(Icons.image, size: 50, color: Colors.grey),
                        ),
                      ),
                      Padding(
                        padding: EdgeInsets.all(8.0),
                        child: Text(
                          shipName,
                          textAlign: TextAlign.center,
                          style: TextStyle(
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
            },
          );
        },
      ),
    );
  }
}
