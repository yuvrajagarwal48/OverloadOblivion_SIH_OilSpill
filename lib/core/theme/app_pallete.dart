import 'package:flutter/material.dart';

class Pallete {
  static const Color backgroundColor =
      Color.fromARGB(255, 202, 228, 255); // Dark shade as background
  static const Color primaryColor =
      Color.fromARGB(255, 56, 189, 248); // Deep blue as primary color
  static const Color secondaryColor =
      Color.fromARGB(255, 0, 159, 227); // Bold red as secondary color

  static const Color inactiveColor =
      Color(0xFFD9D8D8); // Light grey for inactive elements
  static const Color whiteColor = Colors.white; // White color for contrast
  static const Color greyColor =
      Colors.grey; // Grey color for subtler text/icons
  static const Color errorColor =
      Colors.redAccent; // Error color remains red for visibility
  static const Color transparentColor = Colors.transparent;

  static const Color inactiveSeekColor =
      Colors.white38; // Inactive state for seekbars/sliders
}
