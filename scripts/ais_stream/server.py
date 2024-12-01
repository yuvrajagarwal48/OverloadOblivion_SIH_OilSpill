import asyncio
import websockets
import json
import pandas as pd
import logging
from datetime import datetime
import traceback
import numpy as np
from scripts import anomaly_detection 
from scripts import oil_spill_probability

class AISAnomalyServer:
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.anomaly_detector = anomaly_detection.AnomalyDetector()
        self.oil_spill_probab = oil_spill_probability.OilProbability()
        
        # Configure logging
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def convert_to_timeofday(self, timestamp):
        """Convert timestamp to time of day category."""
        hour = datetime.fromtimestamp(timestamp).hour
        if 5 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 17:
            return 'Afternoon'
        elif 17 <= hour < 21:
            return 'Evening'
        else:
            return 'Night'

    def convert_numpy_types(self, obj):
        """Convert NumPy types to standard Python types."""
        if isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.int_):
            return int(obj)
        elif isinstance(obj, np.float_):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    async def handler(self, websocket):
        """
        Handle individual WebSocket connections.
        """
        try:
            # Add this client to our set of clients
            self.clients.add(websocket)
            self.logger.info(f"New client connected. Total clients: {len(self.clients)}")

            # Simulate AIS data streaming
            async with websockets.connect('wss://stream.aisstream.io/v0/stream') as ais_websocket:
                subscribe_message = {
                    "APIKEY": "",
                    "BoundingBoxes": [[[-90, 15], [30, -90]]],
                    "FilterMessageTypes": ["PositionReport"]
                }
                await ais_websocket.send(json.dumps(subscribe_message))
                self.logger.info("Subscribed to AIS stream.")

                async for message_json in ais_websocket:
                    try:
                        message = json.loads(message_json)
                        if "PositionReport" in message["Message"]:
                            position_data = message["Message"]["PositionReport"]
                            timestamp = position_data["Timestamp"]

                            # Prepare AIS data
                            ais_data = {
                                'SOG_mean': position_data["Sog"],
                                'COG_mean': position_data["Cog"],
                                'LAT_mean': position_data["Latitude"],
                                'LON_mean': position_data["Longitude"],
                                'Heading_mean_heading': position_data["TrueHeading"],
                                'Status_mode': position_data["NavigationalStatus"],
                                'TimeOfDay_mode': self.convert_to_timeofday(timestamp),
                            }

                            # Perform anomaly detection
                            ais_df = pd.DataFrame([ais_data])
                            anomaly_result = self.anomaly_detector.detect_anomaly(ais_df.loc[0])
                            oil_probability = self.oil_spill_probab.detect_oilspill(ais_df.loc[0])
                            anomaly_result.update(oil_probability)

                            # Prepare unified output
                            output = {
                                "ais_data": ais_data,
                                "anomaly_result": anomaly_result,
                            }

                            # Convert output values to standard Python types
                            converted_output = {
                                k: self.convert_numpy_types(v) for k, v in output.items()
                            }

                            # Convert anomaly_result specifically to ensure all types are handled
                            converted_output['anomaly_result'] = {
                                k: self.convert_numpy_types(v) for k, v in anomaly_result.items()
                            }

                            # Send data to all connected clients
                            json_data = json.dumps(converted_output)
                            await websocket.send(json_data)

                    except Exception as e:
                        self.logger.error(f"Error processing AIS message: {e}")
                        self.logger.error(traceback.format_exc())

        except websockets.exceptions.ConnectionClosed:
            self.logger.warning("Client connection closed")
        except Exception as e:
            self.logger.error(f"Unexpected error in handler: {e}")
        finally:
            # Remove the client from our set
            self.clients.discard(websocket)
            self.logger.info(f"Client disconnected. Remaining clients: {len(self.clients)}")

    async def start_server(self):
        """
        Start the WebSocket server.
        """
        server = await websockets.serve(
            self.handler, 
            self.host, 
            self.port,
            ping_interval=20,   # Send ping every 20 seconds
            ping_timeout=20     # Timeout after 20 seconds if no pong received
        )
        
        self.logger.info(f"WebSocket server started on {self.host}:{self.port}")
        await server.wait_closed()

def main():
    """
    Main entry point to start the AIS Anomaly Server.
    """
    server = AISAnomalyServer()
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    main()