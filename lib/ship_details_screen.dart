import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:spill_sentinel/anomaly_tab.dart';
import 'package:spill_sentinel/core/theme/app_pallete.dart';
import 'package:spill_sentinel/features/auth/presentation/widgets/auth_button.dart';
import 'package:spill_sentinel/report_details_page.dart';
import 'package:spill_sentinel/utils.dart';
import 'package:spill_sentinel/widgets/voyage_details_card_widget.dart';

class ShipDetailsScreen extends StatefulWidget {
  final Map<String, dynamic> shipData;

  const ShipDetailsScreen({required this.shipData, Key? key}) : super(key: key);

  @override
  _ShipDetailsScreenState createState() => _ShipDetailsScreenState();
}

class _ShipDetailsScreenState extends State<ShipDetailsScreen>
    with TickerProviderStateMixin {
  late TabController _tabController;
  Map<String, dynamic> get shipData => widget.shipData;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Pallete.primaryColor,
      appBar: AppBar(
        title: Text(
          shipData['ShipName'] ?? "Unknown Ship",
          style: const TextStyle(color: Colors.white),
        ),
        backgroundColor: Pallete.secondaryColor,
        bottom: TabBar(
          overlayColor: WidgetStatePropertyAll(Pallete.primaryColor),
          dividerHeight: 0,
          controller: _tabController,
          indicatorColor: Pallete.whiteColor,
          labelColor: Pallete.whiteColor,
          unselectedLabelColor: Pallete.whiteColor.withOpacity(0.5),
          tabs: const [
            Tab(text: 'Vessel'),
            Tab(text: 'Position'),
            Tab(text: 'Anomaly'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildVesselTab(),
          _buildPositionTab(),
          AnomalyTab(shipData: shipData)
        ],
      ),
    );
  }

  /// Builds the Vessel tab content, including vessel and voyage data
  Widget _buildVesselTab() {
    return SingleChildScrollView(
      child: Column(
        children: [
          _buildShipDetailsCard(),
          const SizedBox(height: 8),
          VoyageDetailsCard(shipData: shipData),
          const SizedBox(height: 8),
          _buildStatusCard(),
        ],
      ),
    );
  }

  /// Builds the Position tab content
  Widget _buildPositionTab() {
    final position = shipData['Position'];
    if (position == null) {
      return const Center(child: Text("Position data unavailable"));
    }

    return Stack(
      children: [
        // Map background
        Positioned.fill(
          child: _buildMap(),
        ),
        // Draggable sheet with position metrics
        DraggableScrollableSheet(
          initialChildSize: 0.3,
          minChildSize: 0.1,
          maxChildSize: 0.6,
          builder: (context, scrollController) {
            return Container(
              decoration: BoxDecoration(
                color: Pallete.primaryColor,
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(20),
                ),
              ),
              child: SingleChildScrollView(
                controller: scrollController,
                child: _buildPositionMetrics(),
              ),
            );
          },
        ),
      ],
    );
  }

  /// Builds the Anomaly tab content

  /// Builds the ship details card
  Widget _buildShipDetailsCard() {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(15),
      ),
      elevation: 6,
      child: Column(
        children: [
          // Ship image placeholder
          Container(
            decoration: BoxDecoration(
              border: Border.all(
                color: Pallete.whiteColor,
                width: 0.01,
              ),
            ),
            child: ClipRRect(
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(15),
              ),
              child: Image.asset('assets/ship_placeholder.jpg'),
            ),
          ),
          Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  Colors.blue.shade50,
                  Colors.white,
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(15),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  Text(
                    shipData['ShipName'] ?? "Unknown Ship",
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Type: ${shipData['Type'] != null ? int.parse(shipData['Type']) : "Unknown"}',
                    style: TextStyle(
                      fontSize: 16,
                      color: Pallete.primaryColor,
                    ),
                  ),
                  const SizedBox(height: 16),
                  // Vessel information table
                  _buildInfoTable([
                    {
                      'label': 'Call Sign',
                      'value': shipData['CallSign'] ?? "N/A"
                    },
                    {'label': 'IMO Number', 'value': shipData['IMO'] ?? "N/A"},
                    {'label': 'MMSI', 'value': shipData['MMSI'].toString()},
                    {'label': 'Flag', 'value': shipData['Flag'] ?? "N/A"},
                    {'label': 'Zone', 'value': shipData['Zone'] ?? "N/A"},
                  ]),
                ],
              ),
            ),
          ),
        ],
      ),
    ).animate().fadeIn(duration: 500.ms).slideY(begin: 0.1, end: 0);
  }

  Widget _buildVoyageDetailsCard() {
    double progress = 0.7; // Arbitrary progress value between 0.0 and 1.0

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(15),
      ),
      elevation: 6,
      color: Pallete.whiteColor.withOpacity(0.95),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Text(
                'Voyage Details',
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: Pallete.primaryColor,
                ),
              ),
            ),
            const SizedBox(height: 20),
            // Progress Bar Section
            Row(
              children: [
                Text(
                  shipData['SRC'] ?? "Source",
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: Pallete.primaryColor,
                  ),
                ),
                Expanded(
                  child: Stack(
                    children: [
                      Container(
                        height: 10,
                        decoration: BoxDecoration(
                          color: Colors.grey[300],
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                      Positioned.fill(
                        child: FractionallySizedBox(
                          alignment: Alignment.centerLeft,
                          widthFactor: progress,
                          child: Container(
                            decoration: BoxDecoration(
                              color: Pallete.primaryColor,
                              borderRadius: BorderRadius.circular(10),
                            ),
                          ),
                        ),
                      ),
                      Positioned(
                        left:
                            progress * (MediaQuery.of(context).size.width - 80),
                        child: Transform.translate(
                          offset: const Offset(-12, -15),
                          child: Icon(
                            Icons.directions_boat,
                            color: Colors.blueAccent,
                            size: 24,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  shipData['Destination'] ?? "Destination",
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: Pallete.primaryColor,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              'Distance Remaining: ${shipData['DistanceRemaining'] ?? "0"} nm',
              style: TextStyle(fontSize: 14, color: Colors.grey[700]),
            ),
            const SizedBox(height: 20),
            // Additional Details Section
            Wrap(
              spacing: 12,
              runSpacing: 12,
              children: [
                _buildDetailChip('ETAAIS', shipData['ETAAIS'] ?? "N/A"),
                _buildDetailChip(
                    'ETAPredicted', shipData['ETAPredicted'] ?? "N/A"),
                _buildDetailChip('LOCODE', shipData['LOCODE'] ?? "N/A"),
                _buildDetailChip(
                    'ECA', (shipData['ECA'] ?? false) ? "Yes" : "No"),
              ],
            ),
          ],
        ),
      ),
    );
  }

// Helper widget to create styled chips
  Widget _buildDetailChip(String label, String value) {
    return Chip(
      backgroundColor: Pallete.primaryColor.withOpacity(0.1),
      label: Text(
        '$label: $value',
        style: TextStyle(color: Pallete.primaryColor),
      ),
    );
  }

  /// Builds the status card with additional metrics
  Widget _buildStatusCard() {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(15),
      ),
      elevation: 6,
      child: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              Colors.blue.shade50,
              Colors.white,
            ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(15),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Status Section
              Text(
                'Status: ${shipData['Status'] != null ? getStatusDescription(int.parse(shipData['Status'])) : "Unknown"}',
                style: TextStyle(
                  color: Pallete.primaryColor,
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                ),
              ),
              const SizedBox(height: 16),
              // Grid View for metrics
              GridView.count(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisCount: 3,
                crossAxisSpacing: 16.0,
                mainAxisSpacing: 16.0,
                children: [
                  _buildStatusGridItem('Speed', '${shipData['Speed']} kn'),
                  _buildStatusGridItem('Draught', '${shipData['Draught']} m'),
                  _buildStatusGridItem('Heading', '${shipData['Heading']}°'),
                  _buildStatusGridItem(
                      'Latitude',
                      shipData['Position']?.latitude?.toStringAsFixed(4) ??
                          '-'),
                  _buildStatusGridItem(
                      'Longitude',
                      shipData['Position']?.longitude?.toStringAsFixed(4) ??
                          '-'),
                  _buildStatusGridItem('Course', '${shipData['Course']}'),
                ],
              ),
            ],
          ),
        ),
      ),
    ).animate().fadeIn(duration: 500.ms).slideY(begin: 0.1, end: 0);
  }

  /// Helper method to build an info table
  Widget _buildInfoTable(List<Map<String, String>> rows) {
    return Table(
      columnWidths: const {
        0: FlexColumnWidth(2),
        1: FlexColumnWidth(3),
      },
      border: TableBorder.all(
        color: Pallete.primaryColor.withOpacity(0.2),
        width: 1,
      ),
      children: rows
          .map(
            (row) => TableRow(
              children: [
                Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Text(
                    row['label']!,
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Pallete.primaryColor,
                    ),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Text(row['value'] ?? 'N/A'),
                ),
              ],
            ),
          )
          .toList(),
    );
  }

  /// Helper widget to create grid items
  Widget _buildStatusGridItem(String label, String value) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
      decoration: BoxDecoration(
        color: Pallete.primaryColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: Pallete.primaryColor.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            label,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: Pallete.primaryColor,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  /// Builds the map widget for the Position tab
  Widget _buildMap() {
    final position = shipData['Position'];
    return FlutterMap(
      options: MapOptions(
        initialCenter: LatLng(position.latitude, position.longitude),
        initialZoom: 10,
      ),
      children: [
        TileLayer(
          urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        ),
        MarkerLayer(
          markers: [
            Marker(
              point: LatLng(position.latitude, position.longitude),
              width: 30,
              height: 30,
              child: Tooltip(
                message:
                    '${shipData['ShipName']} (${shipData['Flag']})\nSpeed: ${shipData['Speed']} kn\nHeading: ${shipData['Heading']}°',
                child: Icon(
                  Icons.location_on,
                  color: Pallete.primaryColor,
                  size: 30,
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  /// Builds the position metrics for the draggable sheet
  Widget _buildPositionMetrics() {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          Container(
            width: 40,
            height: 5,
            decoration: BoxDecoration(
              color: Pallete.whiteColor,
              borderRadius: BorderRadius.circular(5),
            ),
          ),
          const SizedBox(height: 16),
          Container(
            color: Pallete.whiteColor,
            child: Column(
              children: [
                Text(
                  'Position Metrics',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Pallete.primaryColor,
                  ),
                ),
                _buildInfoTable([
                  {
                    'label': 'Latitude',
                    'value':
                        shipData['Position']?.latitude?.toStringAsFixed(4) ??
                            '-'
                  },
                  {
                    'label': 'Longitude',
                    'value':
                        shipData['Position']?.longitude?.toStringAsFixed(4) ??
                            '-'
                  },
                  {
                    'label': 'Course Over Ground',
                    'value': shipData['Course'] ?? "N/A"
                  },
                  {
                    'label': 'Timestamp',
                    'value': shipData['Timestamp'] ?? "N/A"
                  },
                  {'label': 'Speed', 'value': '${shipData['Speed']} kn'},
                  {'label': 'Heading', 'value': '${shipData['Heading']}°'},
                  {'label': 'Draught', 'value': '${shipData['Draught']} m'},
                  {'label': 'Zone', 'value': shipData['Zone'] ?? "N/A"},
                ]),
              ],
            ),
          ),
          const SizedBox(height: 16),
          // Position information table
        ],
      ),
    );
  }

  /// Builds a probability indicator for the Anomaly tab
  Widget _buildProbabilityIndicator(String label, double probability,
      {Color color = Colors.redAccent}) {
    return Column(
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 18,
            color: Pallete.whiteColor,
          ),
        ),
        const SizedBox(height: 12),
        Stack(
          alignment: Alignment.center,
          children: [
            SizedBox(
              width: 150,
              height: 150,
              child: CircularProgressIndicator(
                value: probability,
                strokeWidth: 12,
                backgroundColor: Pallete.whiteColor.withOpacity(0.2),
                valueColor: AlwaysStoppedAnimation<Color>(color),
              ),
            ),
            Text(
              '${(probability * 100).toStringAsFixed(1)}%',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Pallete.whiteColor,
              ),
            ),
          ],
        ),
      ],
    );
  }
}
