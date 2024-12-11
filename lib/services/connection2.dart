import 'dart:async';
import 'dart:convert';
import 'package:spill_sentinel/secrets.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

class AISWebSocketClient {
  final String uri;
  late WebSocketChannel channel;
  final StreamController<dynamic> _streamController =
      StreamController.broadcast();

  AISWebSocketClient({this.uri = Secrets.anomalyUrl});

  Stream<dynamic> get stream => _streamController.stream;

  Future<void> connectAndReceive() async {
    try {
      channel = WebSocketChannel.connect(Uri.parse(uri));

      // Send filtering parameters
      final filterParams = {
        "lat_range": [18, 30], // Gulf of Mexico latitude range
        "long_range": [-98, -82], // Gulf of Mexico longitude range
      };
      channel.sink.add(jsonEncode(filterParams));

      // Listen for incoming messages and add them to the broadcast stream
      channel.stream.listen(
        (message) {
          try {
            final aisData = jsonDecode(message);
            _streamController.add(aisData); // Add data to the broadcast stream
            print(aisData);
          } catch (e) {
            print('Error decoding JSON: $e');
          }
        },
        onDone: () {
          print('Connection closed by server.');
          _streamController.close();
        },
        onError: (error) {
          print('Connection error: $error');
          _streamController.close();
        },
      );
    } catch (e) {
      print('Failed to connect: $e');
      _streamController.close();
    }
  }

  void closeConnection() {
    channel.sink.close();
    _streamController.close();
  }
}
