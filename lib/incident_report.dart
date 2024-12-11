import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

class ReportIncidentPage extends StatefulWidget {
  @override
  _ReportIncidentPageState createState() => _ReportIncidentPageState();
}

class _ReportIncidentPageState extends State<ReportIncidentPage> {
  final ImagePicker _picker = ImagePicker();
  XFile? _incidentImage;
  final TextEditingController _descriptionController = TextEditingController();
  String? _selectedIncidentType;

  final List<String> _incidentTypes = [
    'Oil Spill',
    'Crash',
    'Pollution',
    'Other',
  ];

  Future<void> _pickImage() async {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (BuildContext context) {
        return Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.cyan.shade700, Colors.blueAccent.shade100],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.vertical(top: Radius.circular(25)),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: Icon(Icons.camera_alt, color: Colors.white),
                title:
                    Text('Take a Photo', style: TextStyle(color: Colors.white)),
                onTap: () async {
                  final XFile? image =
                      await _picker.pickImage(source: ImageSource.camera);
                  setState(() {
                    _incidentImage = image;
                  });
                  Navigator.pop(context);
                },
              ),
              ListTile(
                leading: Icon(Icons.photo_library, color: Colors.white),
                title: Text('Choose from Gallery',
                    style: TextStyle(color: Colors.white)),
                onTap: () async {
                  final XFile? image =
                      await _picker.pickImage(source: ImageSource.gallery);
                  setState(() {
                    _incidentImage = image;
                  });
                  Navigator.pop(context);
                },
              ),
              SizedBox(height: 10),
            ],
          ),
        );
      },
    );
  }

  void _submitReport() {
    if (_selectedIncidentType == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Please select an incident type')),
      );
      return;
    }

    if (_incidentImage == null && _selectedIncidentType != 'Other') {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Please upload an image for the incident')),
      );
      return;
    }

    String incidentType = _selectedIncidentType!;
    String description = _descriptionController.text;

    // Implement your submission logic here (e.g., upload to backend)

    // Clear the fields after submission
    setState(() {
      _incidentImage = null;
      _descriptionController.clear();
      _selectedIncidentType = null;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Report Submitted Successfully')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.cyan.shade50,
      appBar: AppBar(
        title: Text(
          "Report Incident",
          style: TextStyle(
              color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
        ),
        backgroundColor: Colors.cyan.shade700,
        elevation: 0,
        centerTitle: true,
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [Colors.cyan.shade300, Colors.blueAccent.shade100],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: SingleChildScrollView(
            child: Column(
              children: [
                _buildDropdownSection(),
                SizedBox(height: 20),
                _buildImageUploadSection(),
                SizedBox(height: 20),
                _buildDescriptionSection(),
                SizedBox(height: 30),
                _buildSubmitButton(),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildDropdownSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          "Select Incident Type",
          style: TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.w600,
            color: Colors.white,
            shadows: [
              Shadow(
                blurRadius: 10.0,
                color: Colors.black45,
                offset: Offset(2.0, 2.0),
              ),
            ],
          ),
        ),
        SizedBox(height: 10),
        Container(
          padding: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
          decoration: BoxDecoration(
            color: Colors.cyan.shade100.withOpacity(0.8),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: Colors.white, width: 3),
          ),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<String>(
              hint: Text(
                'Choose Incident Type',
                style: TextStyle(color: Colors.white70),
              ),
              value: _selectedIncidentType,
              isExpanded: true,
              dropdownColor: Colors.cyan.shade700,
              icon: Icon(Icons.arrow_drop_down, color: Colors.white),
              items: _incidentTypes.map((String type) {
                return DropdownMenuItem<String>(
                  value: type,
                  child: Text(
                    type,
                    style: TextStyle(color: Colors.white),
                  ),
                );
              }).toList(),
              onChanged: (String? newValue) {
                setState(() {
                  _selectedIncidentType = newValue;
                  if (_selectedIncidentType == 'Other') {
                    _incidentImage =
                        null; // Optionally handle image differently for 'Other'
                  }
                });
              },
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildImageUploadSection() {
    return Visibility(
      visible:
          _selectedIncidentType != null && _selectedIncidentType != 'Other',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            "Upload Image",
            style: TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.w600,
              color: Colors.white,
              shadows: [
                Shadow(
                  blurRadius: 10.0,
                  color: Colors.black45,
                  offset: Offset(2.0, 2.0),
                ),
              ],
            ),
          ),
          SizedBox(height: 10),
          GestureDetector(
            onTap: _pickImage,
            child: Container(
              height: 180,
              decoration: BoxDecoration(
                color: Colors.cyan.shade100.withOpacity(0.8),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: Colors.white, width: 3),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black26,
                    blurRadius: 10,
                    offset: Offset(5, 5),
                  ),
                ],
              ),
              child: _incidentImage == null
                  ? Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.upload_file,
                              size: 50, color: Colors.white70),
                          SizedBox(height: 10),
                          Text(
                            "Tap to upload or capture image",
                            style: TextStyle(
                              fontSize: 16,
                              color: Colors.white70,
                            ),
                          ),
                        ],
                      ),
                    )
                  : ClipRRect(
                      borderRadius: BorderRadius.circular(20),
                      child: Image.file(
                        File(_incidentImage!.path),
                        fit: BoxFit.cover,
                        width: double.infinity,
                      ),
                    ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDescriptionSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          "Description",
          style: TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.w600,
            color: Colors.white,
            shadows: [
              Shadow(
                blurRadius: 10.0,
                color: Colors.black45,
                offset: Offset(2.0, 2.0),
              ),
            ],
          ),
        ),
        SizedBox(height: 10),
        TextField(
          controller: _descriptionController,
          maxLines: 6,
          decoration: InputDecoration(
            hintText: "Write about the incident...",
            filled: true,
            fillColor: Colors.cyan.shade50.withOpacity(0.8),
            hintStyle: TextStyle(color: Colors.cyan.shade200),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(20),
              borderSide: BorderSide.none,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSubmitButton() {
    return ElevatedButton(
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.cyan.shade700,
        padding: EdgeInsets.symmetric(horizontal: 60, vertical: 15),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(30),
        ),
        elevation: 5,
      ),
      onPressed: _submitReport,
      child: Text(
        "Submit",
        style: TextStyle(fontSize: 20, color: Colors.white),
      ),
    );
  }
}
