import 'package:flutter/material.dart';

class TestPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Test Page'),
      ),
      body: Center(
        child: Text(
          'This is a test page',
          style: TextStyle(fontSize: 24),
        ),
      ),
    );
  }
}
