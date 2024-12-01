import asyncio
import websockets
import json
import logging

class AISAnomalyClient:
    def __init__(self, server_url='ws://localhost:8765'):
        """
        Initialize the AIS Anomaly Client.
        
        :param server_url: WebSocket server URL to connect to
        """
        self.server_url = server_url
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    async def connect_and_receive(self):
        """
        Connect to the WebSocket server and continuously receive AIS anomaly data.
        """
        try:
            async with websockets.connect(self.server_url) as websocket:
                self.logger.info(f"Connected to AIS Anomaly Server at {self.server_url}")
                
                while True:
                    try:
                        # Receive message from the server
                        message = await websocket.recv()
                        
                        # Parse the JSON message
                        data = json.loads(message)
                        
                        # Process and log the received data
                        self.process_ais_data(data)
                    
                    except json.JSONDecodeError:
                        self.logger.error("Failed to decode JSON message")
                    except Exception as e:
                        self.logger.error(f"Error receiving message: {e}")
                        break
        
        except websockets.exceptions.ConnectionClosed:
            self.logger.error("Connection to server was closed")
        except Exception as e:
            self.logger.error(f"Connection error: {e}")

    def process_ais_data(self, data):
        """
        Process and log the received AIS anomaly data.
        
        :param data: Dictionary containing AIS data and anomaly results
        """
        try:
            # Extract AIS data and anomaly results
            ais_data = data.get('ais_data', {})
            anomaly_result = data.get('anomaly_result', {})
            
            # Log AIS Position Information
            self.logger.info("AIS Position Data:")
            self.logger.info(f"Latitude: {ais_data.get('LAT_mean', 'N/A')}")
            self.logger.info(f"Longitude: {ais_data.get('LON_mean', 'N/A')}")
            self.logger.info(f"Speed Over Ground: {ais_data.get('SOG_mean', 'N/A')} knots")
            self.logger.info(f"Course Over Ground: {ais_data.get('COG_mean', 'N/A')} degrees")
            self.logger.info(f"True Heading: {ais_data.get('Heading_mean_heading', 'N/A')}")
            self.logger.info(f"Navigational Status: {ais_data.get('Status_mode', 'N/A')}")
            self.logger.info(f"Time of Day: {ais_data.get('TimeOfDay_mode', 'N/A')}")
            
            # Log Anomaly Detection Results
            self.logger.info("\nAnomaly Detection Results:")
            for key, value in anomaly_result.items():
                self.logger.info(f"{key}: {value}")
            
            print("\n" + "-"*50 + "\n")  # Separator for readability
        
        except Exception as e:
            self.logger.error(f"Error processing AIS data: {e}")

async def main():
    """
    Main function to run the AIS Anomaly Client.
    """
    client = AISAnomalyClient()
    await client.connect_and_receive()

if __name__ == "__main__":
    asyncio.run(main())