import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:spill_sentinel/widgets/eta_widget.dart';

class ShipDetailsScreen extends StatefulWidget {
  final Map<String, dynamic> shipData;

  const ShipDetailsScreen({required this.shipData, Key? key}) : super(key: key);

  @override
  State<ShipDetailsScreen> createState() => _ShipDetailsScreenState();
}

class _ShipDetailsScreenState extends State<ShipDetailsScreen> {
  String selectedTab = "Vessel"; // Initial tab
  String getStatusDescription(int statusNumber) {
    switch (statusNumber) {
      case 0:
        return "Underway using engine";
      case 1:
        return "At anchor";
      case 2:
        return "Not under command";
      case 3:
        return "Restricted maneuverability";
      case 4:
        return "Constrained by her draught";
      case 5:
        return "Moored";
      case 6:
        return "Aground";
      case 7:
        return "Engaged in fishing";
      case 8:
        return "Underway sailing";
      case 9:
        return "Reserved for future amendment of navigational status for ships carrying dangerous goods (DG), harmful substances(HS), or IMO hazard or pollutant category C, high-speed craft (HSC)";
      case 10:
        return "Reserved for future amendment of navigational status for ships carrying dangerous goods (DG), harmful substances (HS) or marine pollutants (MP), or IMO hazard or pollutant category A, wing in the ground (WIG)";
      case 11:
        return "Power-driven vessel towing astern";
      case 12:
        return "Power-driven vessel pushing ahead or towing alongside";
      case 13:
        return "Reserved for future use";
      case 14:
        return "AIS-SART Active (Search and Rescue Transmitter), AIS-MOB (Man Overboard), AIS-EPIRB (Emergency Position Indicating Radio Beacon)";
      case 15:
        return "Undefined";
      default:
        return "Unknown status";
    }
  }

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
            // Top Navigation Tabs
            _buildTabs(),
            const SizedBox(height: 8),
            // Ship Details and Image Section
            _buildShipDetailsCard(shipData),
            // Status and Metrics Section
            _buildStatusCard(shipData),
            // Map Section
            _buildMapCard(shipData),
            // Action Buttons Section
            _buildActionButtons(),
          ],
        ),
      ),
    );
  }

  /// Builds the top navigation tabs
  Widget _buildTabs() {
    final tabs = ["Vessel", "Voyage", "Position"];
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
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        shipData['ShipName'] ?? "Unknown Ship",
                        style: const TextStyle(
                            fontSize: 20, fontWeight: FontWeight.bold),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    const SizedBox(width: 10),
                    Text(
                      shipData['Flag'] ?? "Unknown",
                      style: const TextStyle(fontSize: 16),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                ETAWidget(eta: shipData['ETA'], progress: 0.5),
                const SizedBox(height: 8),
                // Additional information
                Text('Call Sign: ${shipData['CallSign'] ?? "N/A"}'),
                Text('IMO Number: ${shipData['IMO'] ?? "N/A"}'),
                Text('Destination: ${shipData['Destination'] ?? "N/A"}'),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget shipEtaWidget(String atd, String eta) {
    return Container(
      padding: EdgeInsets.all(16.0),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12.0),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.3),
            spreadRadius: 2,
            blurRadius: 5,
            offset: Offset(0, 3),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'ATD: $atd',
            style: TextStyle(
              fontSize: 16.0,
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(height: 8.0),
          Text(
            'ETA: $eta',
            style: TextStyle(
              fontSize: 16.0,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  /// Builds the status and metrics card
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
            Text(
              'Status: ${shipData['Status'] != null ? getStatusDescription(int.parse(shipData['Status'])) : "Unknown"}',
              style: TextStyle(
                color: Colors.green.shade700,
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Speed: ${shipData['Speed'] ?? "-"}'),
                Text('Draught: ${shipData['Draught'] ?? "-"} m'),
                Text('Heading: ${shipData['Heading'] ?? "-"}°'),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Length: ${shipData['Dimension']['A'] ?? "-"} m'),
                Text('Breadth: ${shipData['Dimension']['B'] ?? "-"} m'),
                Text('Rate of Turn: ${shipData['RateOfTurn'] ?? "-"}°/min'),
              ],
            ),
          ],
        ),
      ),
    );
  }

  /// Builds the map card
  Widget _buildMapCard(Map<String, dynamic> shipData) {
    final position = shipData['Position'];
    if (position == null) {
      return const Center(child: Text("Position data unavailable"));
    }

    return Expanded(
      child: Card(
        margin: const EdgeInsets.all(12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(15),
        ),
        elevation: 4,
        child: FlutterMap(
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
        ),
      ),
    );
  }

  /// Builds the action buttons at the bottom
  Widget _buildActionButtons() {
    return Container(
      padding: const EdgeInsets.all(8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          ElevatedButton(
            onPressed: () {
              // Add to Fleet action
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.teal.shade600,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
              ),
            ),
            child: const Text(
              'Add to Fleet',
              style: TextStyle(color: Colors.white),
            ),
          ),
          ElevatedButton(
            onPressed: () {
              // Vessel Details action
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.teal.shade800,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
              ),
            ),
            child: const Text(
              'Vessel Details',
              style: TextStyle(color: Colors.white),
            ),
          ),
        ],
      ),
    );
  }
}
