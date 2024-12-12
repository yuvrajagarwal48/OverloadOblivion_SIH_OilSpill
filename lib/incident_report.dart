import 'dart:convert';
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:spill_sentinel/secrets.dart';

class ReportIncidentPage extends StatefulWidget {
  @override
  _ReportIncidentPageState createState() => _ReportIncidentPageState();
}

class _ReportIncidentPageState extends State<ReportIncidentPage> {
  // Marine color palette
  final Color primaryBlue = const Color(0xFF3498db);
  final Color deepBlue = const Color(0xFF2980b9);
  final Color lightBlue = const Color(0xFF5dade2);
  final Color backgroundBlue = const Color(0xFFe8f4f8);
  final Color accentColor = const Color(0xFF1abc9c);

  final ImagePicker _picker = ImagePicker();
  XFile? _incidentImage;
  final TextEditingController _descriptionController = TextEditingController();
  String? _selectedIncidentType;
  String? _thirdPartyImage;

  final List<String> _incidentTypes = [
    'Oil Spill',
    'Crash',
    'Pollution',
    'Other',
  ];

  Future<String> getThirdPartyImage() async {
    Dio dio = Dio();

    FormData formData = FormData.fromMap({
      if (_incidentImage != null)
        'file': await MultipartFile.fromFile(_incidentImage!.path),
    });

    final response = await dio.post(
      '${Secrets.thirdPartyUrl}/detect/',
      data: formData,
    );
    print('Response: ${response.data}');

    return response.data['image_base64'];
  }

  Future<void> _pickImage() async {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (BuildContext context) {
        return Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [deepBlue, lightBlue],
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
                title: Text('Take a Photo',
                    style: TextStyle(
                        color: Colors.white, fontWeight: FontWeight.bold)),
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
                    style: TextStyle(
                        color: Colors.white, fontWeight: FontWeight.bold)),
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

  void _submitReport() async {
    if (_selectedIncidentType == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Please select an incident type'),
          backgroundColor: accentColor,
        ),
      );
      return;
    }

    if (_incidentImage == null && _selectedIncidentType != 'Other') {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Please upload an image for the incident'),
          backgroundColor: accentColor,
        ),
      );
      return;
    }

    final image = await getThirdPartyImage();
    print('Image: $image');
    setState(() {
      _thirdPartyImage = image;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Report Submitted Successfully'),
        backgroundColor: accentColor,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: backgroundBlue,
      appBar: AppBar(
        title: Text(
          "Report Incident",
          style: TextStyle(
              color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
        ),
        backgroundColor: deepBlue,
        elevation: 0,
        centerTitle: true,
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [primaryBlue, lightBlue],
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
            color: Colors.white.withOpacity(0.2),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: Colors.white, width: 2),
          ),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<String>(
              hint: Text(
                'Choose Incident Type',
                style: TextStyle(color: Colors.white70),
              ),
              value: _selectedIncidentType,
              isExpanded: true,
              dropdownColor: deepBlue,
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
                    _incidentImage = null;
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
                color: Colors.white.withOpacity(0.2),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: Colors.white, width: 2),
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
                        fit: BoxFit.contain,
                        width: double.infinity,
                      ),
                    ),
            ),
          ),
          SizedBox(height: 20),
          _thirdPartyImage != null
              ? Container(
                  height: 180,
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: Colors.white, width: 2),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black26,
                        blurRadius: 10,
                        offset: Offset(5, 5),
                      ),
                    ],
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(20),
                    child: Image.memory(
                      base64Decode(_thirdPartyImage!),
                      fit: BoxFit.contain,
                      width: double.infinity,
                    ),
                  ),
                )
              : SizedBox.shrink(),
        ],
      ),
    );
  }

  Widget _buildSubmitButton() {
    return ElevatedButton(
      style: ElevatedButton.styleFrom(
        backgroundColor: deepBlue,
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
