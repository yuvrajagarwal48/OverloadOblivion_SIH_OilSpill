import asyncio
import json
import websockets
import logging

class AISWebSocketClient:
    def __init__(self, uri='ws://localhost:8765'):
        self.uri = uri
        
        # Configure logging
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    async def connect_and_receive(self):
        """
        Connect to the WebSocket server and receive AIS data
        """
        try:
            async with websockets.connect(self.uri) as websocket:
                # Send filtering parameters
                filter_params = {
                    "lat_range": [15, 30],     # Example latitude range
                    "long_range": [-100, -80]  # Example longitude range
                }
                await websocket.send(json.dumps(filter_params))
                
                # Receive and process AIS data
                while True:
                    try:
                        message = await websocket.recv()
                        ais_data = json.loads(message)
                        self.process_ais_data(ais_data)
                    
                    except json.JSONDecodeError:
                        self.logger.error("Invalid JSON received")
                    except websockets.exceptions.ConnectionClosed:
                        self.logger.warning("Connection closed by server")
                        break
        
        except Exception as e:
            self.logger.error(f"Connection error: {e}")

    def process_ais_data(self, ais_data):
        """
        Process and display received AIS data
        
        :param ais_data: Parsed AIS data dictionary
        """
        try:
            print(ais_data)
            print("------------\n")
        except Exception as e:
            self.logger.error(f"Error processing AIS data: {e}")

def main():
    client = AISWebSocketClient()
    asyncio.run(client.connect_and_receive())

if __name__ == "__main__":
    main()