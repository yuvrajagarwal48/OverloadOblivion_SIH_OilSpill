import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:spill_sentinel/utils.dart';
import 'package:spill_sentinel/widgets/eta_widget.dart';

class ShipDetailsScreen extends StatefulWidget {
  final Map<String, dynamic> shipData;

  const ShipDetailsScreen({required this.shipData, Key? key}) : super(key: key);

  @override
  State<ShipDetailsScreen> createState() => _ShipDetailsScreenState();
}

class _ShipDetailsScreenState extends State<ShipDetailsScreen> {
  String selectedTab = "Vessel"; // Initial tab

  // Get a descriptive status from the status number

  @override
  Widget build(BuildContext context) {
    final shipData = widget.shipData;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          shipData['ShipName'] ?? "Unknown Ship",
          style: const TextStyle(color: Colors.white),
        ),
        backgroundColor: Colors.teal.shade700,
      ),
      body: Container(
        height: MediaQuery.of(context).size.height * 1.5,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [Colors.teal.shade800, Colors.teal.shade400],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: Column(
          children: [
            // Tab navigation
            _buildTabs(),
            const SizedBox(height: 8),
            // Dynamically display content based on selected tab
            Expanded(child: _buildTabContent(shipData)),
          ],
        ),
      ),
    );
  }

  /// Builds the top navigation tabs
  Widget _buildTabs() {
    final tabs = ["Vessel", "Position", "Voyage"];
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: tabs.map((tab) {
        return ElevatedButton(
          onPressed: () {
            setState(() {
              selectedTab = tab; // Update selected tab
            });
          },
          style: ElevatedButton.styleFrom(
            backgroundColor:
                selectedTab == tab ? Colors.white : Colors.teal.shade600,
            foregroundColor:
                selectedTab == tab ? Colors.teal.shade800 : Colors.white,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(20),
            ),
            elevation: selectedTab == tab ? 2 : 0,
          ),
          child: Text(tab),
        );
      }).toList(),
    );
  }

  /// Build content based on the selected tab
  Widget _buildTabContent(Map<String, dynamic> shipData) {
    switch (selectedTab) {
      case "Vessel":
        return _buildVesselTabContent(shipData);
      case "Voyage":
        return _buildVoyageTabContent(shipData);
      case "Position":
        return _buildPositionTabContent(shipData);
      default:
        return Container(); // Default case to handle errors
    }
  }

  /// Vessel information tab content
  Widget _buildVesselTabContent(Map<String, dynamic> shipData) {
    return SingleChildScrollView(
      child: Column(
        children: [
          _buildShipDetailsCard(shipData),
          const SizedBox(height: 8),
          _buildStatusCard(shipData),
        ],
      ),
    );
  }

  /// Voyage information tab content
  Widget _buildVoyageTabContent(Map<String, dynamic> shipData) {
    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Title
            Text(
              'Voyage Details',
              style: TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            SizedBox(
                height: 200,
                width: double.infinity,
                child: _buildMapCard(shipData)),
            const SizedBox(height: 16),
            if (shipData['ETA'] != null &&
                shipData['ETA'] is Map<String, dynamic>)
              ETAWidget(eta: shipData['ETA']),
            // Card for voyage details
            Card(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(15),
              ),
              elevation: 4,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Destination
                    Row(
                      children: [
                        Icon(Icons.location_on, color: Colors.teal.shade600),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'Destination',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: Colors.teal.shade700,
                            ),
                          ),
                        ),
                        Expanded(
                          child: Text(
                            shipData['Destination'] ?? "N/A",
                            textAlign: TextAlign.end,
                            style: const TextStyle(fontSize: 16),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),

                    // IMO Number
                    Row(
                      children: [
                        Icon(Icons.numbers, color: Colors.teal.shade600),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'IMO Number',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: Colors.teal.shade700,
                            ),
                          ),
                        ),
                        Expanded(
                          child: Text(
                            shipData['IMO'].toString() ?? "N/A",
                            textAlign: TextAlign.end,
                            style: const TextStyle(fontSize: 16),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),

                    // Call Sign
                    Row(
                      children: [
                        Icon(Icons.call, color: Colors.teal.shade600),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'Call Sign',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: Colors.teal.shade700,
                            ),
                          ),
                        ),
                        Expanded(
                          child: Text(
                            shipData['CallSign'] ?? "N/A",
                            textAlign: TextAlign.end,
                            style: const TextStyle(fontSize: 16),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 8),

            // Additional card for notes or summary (optional)
            Card(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(15),
              ),
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Icon(Icons.info_outline,
                        color: Colors.teal.shade600, size: 28),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'This section provides voyage-specific information like the destination, IMO number, call sign, and estimated time of arrival.',
                        style: const TextStyle(
                            fontSize: 14, color: Colors.black54),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Position information tab content

  Widget _buildPositionTabContent(Map<String, dynamic> shipData) {
    final position = shipData['Position'];
    if (position == null) {
      return const Center(child: Text("Position data unavailable"));
    }

    return Stack(
      children: [
        // Map as background
        Positioned.fill(
          child: _buildMapCard(shipData),
        ),

        // DraggableScrollableSheet for position metrics card
        DraggableScrollableSheet(
          initialChildSize: 0.3, // Start size of the drawer
          minChildSize: 0.1, // Minimum size the drawer can shrink to
          maxChildSize: 0.7, // Maximum size the drawer can expand to
          builder: (BuildContext context, ScrollController scrollController) {
            return Container(
              decoration: BoxDecoration(
                color: Colors.teal.shade600,
                borderRadius: BorderRadius.only(
                  topLeft: Radius.circular(20),
                  topRight: Radius.circular(20),
                ),
              ),
              child: Stack(
                children: [
                  // Content of the position metrics card
                  Container(
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(
                          0.85), // Slightly transparent background for the drawer
                      borderRadius: BorderRadius.only(
                        topLeft: Radius.circular(20),
                        topRight: Radius.circular(20),
                      ),
                    ),
                    child: SingleChildScrollView(
                      controller: scrollController,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Container(
                            width: MediaQuery.of(context).size.width,
                            height: 30,
                            decoration: BoxDecoration(
                                color: Colors.teal.shade600,
                                borderRadius: BorderRadius.only(
                                  topLeft: Radius.circular(20),
                                  topRight: Radius.circular(20),
                                )),
                          ),
                          SizedBox(height: 8),
                          Padding(
                            padding: const EdgeInsets.all(16.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Position Metrics',
                                  style: TextStyle(
                                    fontSize: 20,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.teal,
                                  ),
                                ),
                                const SizedBox(height: 10),

                                // Latitude and Longitude
                                Row(
                                  children: [
                                    Expanded(
                                      child: Text(
                                        'Latitude: ',
                                        style: TextStyle(
                                            fontSize: 16,
                                            fontWeight: FontWeight.bold),
                                      ),
                                    ),
                                    Expanded(
                                      child: Text(
                                        '${position.latitude != null ? position.latitude.toStringAsFixed(4) : "-"}',
                                        style: TextStyle(fontSize: 16),
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 10),
                                Row(
                                  children: [
                                    Expanded(
                                      child: Text(
                                        'Longitude: ',
                                        style: TextStyle(
                                            fontSize: 16,
                                            fontWeight: FontWeight.bold),
                                      ),
                                    ),
                                    Expanded(
                                      child: Text(
                                        '${position.longitude != null ? position.longitude.toStringAsFixed(4) : "-"}',
                                        style: TextStyle(fontSize: 16),
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 10),

                                // Course Over Ground, Position Accuracy
                                Row(
                                  children: [
                                    Expanded(
                                      child: Text(
                                        'Course Over Ground: ',
                                        style: TextStyle(
                                            fontSize: 16,
                                            fontWeight: FontWeight.bold),
                                      ),
                                    ),
                                    Expanded(
                                      child: Text(
                                        '${shipData['CourseOverGround'] ?? "N/A"}',
                                        style: TextStyle(fontSize: 16),
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 10),
                                Row(
                                  children: [
                                    Expanded(
                                      child: Text(
                                        'Position Accuracy: ',
                                        style: TextStyle(
                                            fontSize: 16,
                                            fontWeight: FontWeight.bold),
                                      ),
                                    ),
                                    Expanded(
                                      child: Text(
                                        '${shipData['PositionAccuracy'] ?? "N/A"}',
                                        style: TextStyle(fontSize: 16),
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 10),

                                // RAIM, Special Maneuver Indicator
                                Row(
                                  children: [
                                    Expanded(
                                      child: Text(
                                        'RAIM: ',
                                        style: TextStyle(
                                            fontSize: 16,
                                            fontWeight: FontWeight.bold),
                                      ),
                                    ),
                                    Expanded(
                                      child: Text(
                                        '${shipData['Raim'] ?? "N/A"}',
                                        style: TextStyle(fontSize: 16),
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 10),
                                Row(
                                  children: [
                                    Expanded(
                                      child: Text(
                                        'Special Maneuver Indicator: ',
                                        style: TextStyle(
                                            fontSize: 16,
                                            fontWeight: FontWeight.bold),
                                      ),
                                    ),
                                    Expanded(
                                      child: Text(
                                        '${shipData['SpecialManeuverIndicator'] ?? "N/A"}',
                                        style: TextStyle(fontSize: 16),
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 10),

                                // Repeat Indicator, Communication State
                                Row(
                                  children: [
                                    Expanded(
                                      child: Text(
                                        'Repeat Indicator: ',
                                        style: TextStyle(
                                            fontSize: 16,
                                            fontWeight: FontWeight.bold),
                                      ),
                                    ),
                                    Expanded(
                                      child: Text(
                                        '${shipData['RepeatIndicator'] ?? "N/A"}',
                                        style: TextStyle(fontSize: 16),
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 10),
                                Row(
                                  children: [
                                    Expanded(
                                      child: Text(
                                        'Communication State: ',
                                        style: TextStyle(
                                            fontSize: 16,
                                            fontWeight: FontWeight.bold),
                                      ),
                                    ),
                                    Expanded(
                                      child: Text(
                                        '${shipData['CommunicationState'] ?? "N/A"}',
                                        style: TextStyle(fontSize: 16),
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 10),

                                // Timestamp, Time
                                Row(
                                  children: [
                                    Expanded(
                                      child: Text(
                                        'Timestamp: ',
                                        style: TextStyle(
                                            fontSize: 16,
                                            fontWeight: FontWeight.bold),
                                      ),
                                    ),
                                    Expanded(
                                      child: Text(
                                        '${shipData['Timestamp'] ?? "N/A"}',
                                        style: TextStyle(fontSize: 16),
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 10),
                                Row(
                                  children: [
                                    Expanded(
                                      child: Text(
                                        'Time: ',
                                        style: TextStyle(
                                            fontSize: 16,
                                            fontWeight: FontWeight.bold),
                                      ),
                                    ),
                                    Expanded(
                                      child: Text(
                                        '${shipData['time'] ?? "N/A"}',
                                        style: TextStyle(fontSize: 16),
                                      ),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  // Handle bar at the top of the sheet
                  Positioned(
                    top: 12,
                    left: MediaQuery.of(context).size.width / 2 -
                        20, // Center the handle
                    child: Container(
                      width: 40,
                      height: 5,
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(5),
                      ),
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ],
    );
  }

  Widget _buildMapCard(Map<String, dynamic> shipData) {
    final position = shipData['Position'];
    return FlutterMap(
      options: MapOptions(
        initialCenter: position,
        initialZoom: 10,
      ),
      children: [
        TileLayer(
          urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        ),
        MarkerLayer(
          markers: [
            Marker(
              point: position,
              width: 30,
              height: 30,
              child: Tooltip(
                message: '${shipData['ShipName']} (${shipData['Flag']})\n'
                    'Speed: ${shipData['Speed']}\nHeading: ${shipData['Heading']}',
                child: const Icon(
                  Icons.location_on,
                  color: Colors.red,
                  size: 30,
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  /// Builds the ship details card
  Widget _buildShipDetailsCard(Map<String, dynamic> shipData) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(15),
      ),
      elevation: 4,
      child: Column(
        children: [
          Image.asset(
            'assets/ship_placeholder.jpg', // Replace with actual image
            height: 150,
            fit: BoxFit.cover,
            width: double.infinity,
          ),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      shipData['ShipName'] ?? "Unknown Ship",
                      style: const TextStyle(
                          fontSize: 20, fontWeight: FontWeight.bold),
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(width: 16),
                    Row(
                      children: [
                        Text('Type : ',
                            style: const TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                color: Colors.teal)),
                        Text(
                          shipData['Type'] != null && shipData['Type'] is int
                              ? getTypeDescription(shipData['Type'])
                              : "Unknown",
                          style: const TextStyle(fontSize: 16),
                        ),
                      ],
                    ),
                  ],
                ),
                const SizedBox(height: 8),

                // Add Container with a table-like layout
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.teal.shade50,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: Colors.teal.shade300,
                      width: 1,
                    ),
                  ),
                  child: Column(
                    children: [
                      _buildTableRow(
                          'Call Sign', shipData['CallSign'] ?? "N/A"),
                      _buildTableRow(
                          'IMO Number', shipData['IMO'].toString() ?? "N/A"),
                      _buildTableRow(
                          'MMSI', shipData['MMSI'].toString() ?? "N/A"),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Helper method to create table-like rows
  Widget _buildTableRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: Colors.teal,
            ),
          ),
          Text(
            value,
            style: const TextStyle(fontSize: 16),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusCard(Map<String, dynamic> shipData) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(15),
      ),
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Status Section
            Text(
              'Status: ${shipData['Status'] != null ? getStatusDescription(int.parse(shipData['Status'])) : "Unknown"}',
              style: TextStyle(
                color: Colors.green.shade700,
                fontWeight: FontWeight.bold,
                fontSize: 18,
              ),
            ),
            const SizedBox(height: 16),
            // Grid View for Speed, Draught, and Heading
            GridView.builder(
              shrinkWrap: true,
              physics: NeverScrollableScrollPhysics(),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 3,
                crossAxisSpacing: 16.0,
                mainAxisSpacing: 16.0,
                // To make items more square-like
              ),
              itemCount: 3,
              itemBuilder: (context, index) {
                switch (index) {
                  case 0:
                    return _buildStatusGridItem(
                        'Speed', shipData['Speed'] ?? '-');
                  case 1:
                    return _buildStatusGridItem(
                        'Draught', '${shipData['Draught'] ?? '-'} m');
                  case 2:
                    return _buildStatusGridItem(
                        'Heading', '${shipData['Heading'] ?? '-'}°');
                  default:
                    return Container();
                }
              },
            ),
            const SizedBox(height: 16),
            // Grid View for Length, Breadth, and Rate of Turn
            GridView.builder(
              shrinkWrap: true,
              physics: NeverScrollableScrollPhysics(),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 3,
                crossAxisSpacing: 16.0,
                mainAxisSpacing: 16.0,
                // To make items more square-like
              ),
              itemCount: 3,
              itemBuilder: (context, index) {
                switch (index) {
                  case 0:
                    return _buildStatusGridItem(
                        'Length', '${shipData['Dimension']['A'] ?? '-'} m');
                  case 1:
                    return _buildStatusGridItem(
                        'Breadth', '${shipData['Dimension']['B'] ?? '-'} m');
                  case 2:
                    return _buildStatusGridItem('Rate of Turn',
                        '${shipData['RateOfTurn'] ?? '-'}°/min');
                  default:
                    return Container();
                }
              },
            ),
          ],
        ),
      ),
    );
  }

  /// Helper widget to create grid items
  Widget _buildStatusGridItem(String label, String value) {
    return Container(
      height: 200,
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
      decoration: BoxDecoration(
        color: Colors.teal.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.teal.shade300, width: 1),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            label,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: Colors.teal,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
          ),
        ],
      ),
    );
  }

  /// Position metrics card to display additional info
}
