import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;

class AISApiClient {
  final String _apiUrl;
  final StreamController<dynamic> aisStreamController =
      StreamController.broadcast();
  late Timer _timer;

  AISApiClient(this._apiUrl);

  void startPolling({Duration interval = const Duration(minutes: 2)}) async {
    await _hitApi(); // Hit the API first
    _timer = Timer.periodic(interval, (timer) async {
      await _hitApi(); // Hit the API after every interval
    });
  }

  Future<void> _hitApi() async {
    try {
      final response = await http.get(Uri.parse(_apiUrl));
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        print(response.body);
        for (var item in data) {
          aisStreamController.add(item); // Stream each ship's data
        }
      } else {
        print("Error: ${response.statusCode} - ${response.body}");
      }
    } catch (e) {
      print("Error during API request: $e");
    }
  }

  void stopPolling() {
    _timer.cancel();
    aisStreamController.close();
  }
}
