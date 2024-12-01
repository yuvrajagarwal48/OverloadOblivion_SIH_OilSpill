# import asyncio
# import json
# import websockets
# import logging
# import pandas as pd
# from datetime import datetime
# import signal
# import sys

# # Import the AIS data processor
# from scripts import live_ais_vt

# # Import your anomaly detection modules
# from scripts import anomaly_detection
# from scripts import oil_spill_probability

# class AISAnomalyDetectionServer:
#     def __init__(self, file_path='/home/yuvraj/Coding/sih_main/api_output.txt', host='localhost', port=8765):
#         self.host = host
#         self.port = port
        
#         # Initialize AIS Data Processor
#         self.ais_processor = live_ais_vt.AISDataProcessor(file_path)
        
#         # Initialize anomaly detection components
#         self.anomaly_detector = anomaly_detection.AnomalyDetector()
#         self.oil_spill_probab = oil_spill_probability.OilProbability()
        
#         # Setup logging
#         logging.basicConfig(level=logging.INFO, 
#                             format='%(asctime)s - %(levelname)s - %(message)s')
#         self.logger = logging.getLogger(__name__)
        
#         # Store connected clients
#         self.clients = set()
        
#         # Server and streaming tasks
#         self.server = None
#         self.streaming_task = None
#         self.main_task = None

#     async def stream_ais_data(self):
#         """
#         Continuously stream AIS data with anomaly detection
#         """
#         try:
#             # Read raw data
#             raw_data = self.ais_processor.read_file()
            
#             # Filter data
#             lat_range = (15, 30)  # Example latitude range
#             long_range = (-100, -80)  # Example longitude range
#             filtered_data = self.ais_processor.filter_ais_data(raw_data, lat_range, long_range)

#             # Continuously stream data
#             while True:
#                 for ship_data in filtered_data:
#                     try:
#                         # Prepare data for anomaly detection
#                         anomaly_df = pd.DataFrame([ship_data])
#                         anomaly_df = anomaly_df[['SPEED', 'COURSE', 'LATITUDE', 'LONGITUDE', 'HEADING', 'NAVSTAT']]
                        
#                         # Manually add TIME_OF_DAY based on timestamp
#                         time_of_day = self._categorize_time_of_day(ship_data.get('TIMESTAMP'))
                        
#                         # Rename columns to match model expectations
#                         anomaly_df.rename(columns={
#                             'SPEED': 'SOG_mean',
#                             'COURSE': 'COG_mean',
#                             'LATITUDE': 'LAT_mean',
#                             'LONGITUDE': 'LON_mean',
#                             'HEADING': 'Heading_mean_heading',
#                             'NAVSTAT': 'Status_mode'
#                         }, inplace=True)
                        
#                         # Add time of day to the dataframe
#                         anomaly_df['TimeOfDay_mode'] = time_of_day
        
#                         # Detect anomalies
#                         anomaly_result = self.anomaly_detector.detect_anomaly(anomaly_df.iloc[0])
                        
#                         # Detect oil spill probability
#                         oil_prob = self.oil_spill_probab.detect_oilspill(anomaly_df.iloc[0])
                        
#                         # Combine results
#                         anomaly_result.update(oil_prob)
                        
#                         # Prepare output with JSON serializable data
#                         output = {
#                             "ais_data": {k: self.ais_processor.convert_to_json_serializable(v) for k, v in ship_data.items()},
#                             "anomaly_result": {k: self.ais_processor.convert_to_json_serializable(v) for k, v in anomaly_result.items()}
#                         }
#                         print(output)
                        
#                         # Broadcast to all connected clients
#                         if self.clients:
#                             await asyncio.gather(
#                                 *[client.send(json.dumps(output)) for client in self.clients]
#                             )
                        
#                         # Simulate streaming delay
#                         await asyncio.sleep(0.5)
                    
#                     except Exception as e:
#                         self.logger.error(f"Error processing ship data: {e}")
                
#                 # Restart streaming from the beginning when all data is processed
#                 self.logger.info("Restarting AIS data stream")
        
#         except Exception as e:
#             self.logger.error(f"Streaming error: {e}")

#     def _categorize_time_of_day(self, timestamp):
#         try:
#             if not timestamp:
#                 return "Unknown"
#             # Convert timestamp string to datetime object
#             dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S %Z')
#             hour = dt.hour
#             if 5 <= hour < 12:
#                 return 'Morning'
#             elif 12 <= hour < 17:
#                 return 'Afternoon'
#             elif 17 <= hour < 21:
#                 return 'Evening'
#             else:
#                 return 'Night'
            
#         except Exception as e:
#             self.logger.error(f"Error parsing timestamp: {e}")
#             return "Unknown"

#     async def websocket_handler(self, websocket, path=None):
#         """
#         WebSocket handler to manage client connections
        
#         :param websocket: WebSocket connection
#         :param path: Path for the WebSocket
#         """
#         try:
#             # Add client to the set of connected clients
#             self.clients.add(websocket)
#             self.logger.info(f"New client connected. Total clients: {len(self.clients)}")
            
#             # Keep the connection open
#             await websocket.wait_closed()
        
#         except Exception as e:
#             self.logger.error(f"WebSocket error: {e}")
        
#         finally:
#             # Remove client from the set when connection is closed
#             self.clients.remove(websocket)
#             self.logger.info(f"Client disconnected. Total clients: {len(self.clients)}")

#     async def main(self):
#         """
#         Main async method to set up server and streaming
#         """
#         # Start WebSocket server
#         self.server = await websockets.serve(
#             self.websocket_handler, 
#             self.host, 
#             self.port
#         )
        
#         # Start data streaming task
#         self.streaming_task = asyncio.create_task(self.stream_ais_data())
        
#         self.logger.info(f"Starting server on ws://{self.host}:{self.port}")
        
#         # Wait until the server is closed
#         await self.server.wait_closed()                                                  'SPEED': 'SOG_mean',
                                                #     'COURSE': 'COG_mean',
                                                #     'LATITUDE': 'LAT_mean',
                                                #     'LONGITUDE': 'LON_mean',
                                                #     'HEADING': 'Heading_mean_heading',
                                                #     'NAVSTAT': 'Status_mode'
                                                # }, inplace=True)


#     def run(self):
#         """
#         Run the server with proper event loop management
#         """
#         # Set up event loop
#         loop = asyncio.get_event_loop()
        
#         try:
#             # Create main task
#             self.main_task = loop.create_task(self.main())
            
#             # Run the event loop
#             loop.run_forever()
        
#         except KeyboardInterrupt:
#             print("\nServer stopped by user")
        
#         finally:
#             # Cleanup tasks
#             if self.streaming_task:
#                 self.streaming_task.cancel()
            
#             if self.main_task:
#                 self.main_task.cancel()
            
#             # Close the server
#             if self.server:
#                 self.server.close()
            
#             # Stop the loop
#             loop.stop()

# def handle_exit(sig, frame):
#     """
#     Handle system exit signals
#     """
#     print("\nReceived exit signal. Shutting down...")
#     sys.exit(0)

# if __name__ == "__main__":
#     # Register signal handlers
#     signal.signal(signal.SIGINT, handle_exit)
#     signal.signal(signal.SIGTERM, handle_exit)

#     # Create and run server
#     server = AISAnomalyDetectionServer()
#     server.run()

import asyncio
import json
import websockets
import logging
from datetime import datetime
import signal
import sys
import dotenv
import os
import pandas as pd

dotenv.load_dotenv()

# Import the AIS data processor
from scripts.live_ais_vt import AISDataProcessor

# Import your anomaly detection modules
from scripts import anomaly_detection
from scripts import oil_spill_probability

class AISAnomalyDetectionServer:
    def __init__(self, api_url=None, host='localhost', port=8765):
        self.host = host
        self.port = port
        
        # Initialize AIS Data Processor
        self.ais_processor = AISDataProcessor(api_url)
        
        # Initialize anomaly detection components
        self.anomaly_detector = anomaly_detection.AnomalyDetector()
        self.oil_spill_probab = oil_spill_probability.OilProbability()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Store connected clients
        self.clients = set()
        
        # Server and streaming tasks
        self.server = None
        self.streaming_task = None

    def _categorize_time_of_day(self, timestamp):
        try:
            if not timestamp:
                return "Unknown"
            # Convert timestamp string to datetime object
            dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S %Z')
            hour = dt.hour
            if 5 <= hour < 12:
                return 'Morning'
            elif 12 <= hour < 17:
                return 'Afternoon'
            elif 17 <= hour < 21:
                return 'Evening'
            else:
                return 'Night'
            
        except Exception as e:
            self.logger.error(f"Error parsing timestamp: {e}")
            return "Unknown"
    async def stream_ais_data(self):
        """
        Continuously stream AIS data with anomaly detection.
        """
        # Start the data streaming task
        data_stream_task = asyncio.create_task(self.ais_processor.start_data_stream(interval=120))
        
        try:
            while True:
                # Read data from the queue
                ship_data = await self.ais_processor.read_data()
                if ship_data:
                    # print(ship_data)
                    
                    anomaly_df = pd.DataFrame([ship_data])
                    anomaly_df = anomaly_df[['SPEED', 'COURSE', 'LATITUDE', 'LONGITUDE', 'HEADING', 'NAVSTAT','TIMESTAMP']]
                    anomaly_df['TIMESTAMP']=anomaly_df['TIMESTAMP'].apply(self._categorize_time_of_day)
                    try:
                        # Prepare data for anomaly detection
                        anomaly_df.rename(columns={
                                                    'SPEED': 'SOG_mean',
                                                    'COURSE': 'COG_mean',
                                                    'LATITUDE': 'LAT_mean',
                                                    'LONGITUDE': 'LON_mean',
                                                    'HEADING': 'Heading_mean_heading',
                                                    'NAVSTAT': 'Status_mode',
                                                    'TIMESTAMP':'TimeOfDay_mode'
                                                }, inplace=True)

                        # Detect anomalies
                        anomaly_result = self.anomaly_detector.detect_anomaly(anomaly_df.loc[0])

                        # Detect oil spill probability
                        oil_prob = self.oil_spill_probab.detect_oilspill(anomaly_df.loc[0])

                        # Combine results
                        anomaly_result.update(oil_prob)

                        # Broadcast results to all connected clients
                        output = {
                            "ais_data": {k: self.ais_processor.convert_to_json_serializable(v) for k, v in ship_data.items()},
                            "anomaly_result": {k: self.ais_processor.convert_to_json_serializable(v) for k, v in anomaly_result.items()}
                        }
                        self.logger.info(f"Broadcasting data: {output}")

                        if self.clients:
                            await asyncio.gather(
                                *[client.send(json.dumps(output)) for client in self.clients]
                            )

                        # Small delay to avoid overwhelming the queue
                        await asyncio.sleep(0.5)

                    except Exception as e:
                        self.logger.error(f"Error processing ship data: {e}")

        except Exception as e:
            self.logger.error(f"Streaming error: {e}")
        finally:
            # Cancel the data stream task
            data_stream_task.cancel()


    async def websocket_handler(self, websocket, path=None):
        """
        WebSocket handler to manage client connections
        
        :param websocket: WebSocket connection
        :param path: Path for the WebSocket
        """
        try:
            # Add client to the set of connected clients
            self.clients.add(websocket)
            self.logger.info(f"New client connected. Total clients: {len(self.clients)}")
            
            # Keep the connection open
            await websocket.wait_closed()
        
        except Exception as e:
            self.logger.error(f"WebSocket error: {e}")
        
        finally:
            # Remove client from the set when connection is closed
            self.clients.remove(websocket)
            self.logger.info(f"Client disconnected. Total clients: {len(self.clients)}")

    async def main(self):
        """
        Main async method to set up server and streaming
        """
        # Start WebSocket server
        self.server = await websockets.serve(
            self.websocket_handler, 
            self.host, 
            self.port
        )
        
        # Start data streaming task
        self.streaming_task = asyncio.create_task(self.stream_ais_data())
        
        self.logger.info(f"Starting server on ws://{self.host}:{self.port}")
        
        # Wait until the server is closed
        await self.server.wait_closed()

    def run(self):
        """
        Run the server with proper event loop management
        """
        # Set up event loop
        loop = asyncio.get_event_loop()
        
        try:
            # Create main task
            self.main_task = loop.create_task(self.main())
            
            # Run the event loop
            loop.run_forever()
        
        except KeyboardInterrupt:
            print("\nServer stopped by user")
        
        finally:
            # Cleanup tasks
            if self.streaming_task:
                self.streaming_task.cancel()
            
            if self.main_task:
                self.main_task.cancel()
            
            # Close the server
            if self.server:
                self.server.close()
            
            # Stop the loop
            loop.stop()

def handle_exit(sig, frame):
    """
    Handle system exit signals
    """
    print("\nReceived exit signal. Shutting down...")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    # Create and run server
    server = AISAnomalyDetectionServer(api_url=os.getenv("API_URL"))  # Replace with your actual API URL
    server.run()