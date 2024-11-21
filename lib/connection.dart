import 'dart:convert';
import 'dart:async';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:spill_sentinel/secrets.dart';

class AISStreamWebsocketClient {
  final String _serverUri;
  final StreamController<dynamic> aisStreamController;
  late WebSocketChannel channel;

  AISStreamWebsocketClient(this._serverUri, this.aisStreamController);

  void connect() async {
    channel = WebSocketChannel.connect(
      Uri.parse(_serverUri),
    );

    await channel.ready;
    channel.stream.listen(onMessage);

    // Send the subscription message
    channel.sink.add(jsonEncode({
      "APIKey": Secrets.aisstreamApiKey,
      "BoundingBoxes": [[[10, -98], [31, -81]]]
    }));
  }

  void onMessage(dynamic message) {
    final decodedMessage = jsonDecode(utf8.decode(message));
    aisStreamController.add(decodedMessage);
    print(decodedMessage);
  }

  void disconnect() {
    channel.sink.close();
  }
}
