import json
import websockets
from datetime import datetime
import signal
import sys
import dotenv
import os
import pandas as pd
dotenv.load_dotenv()

from scripts.live_ais_vt import AISDataProcessor
from scripts import anomaly_detection, oil_spill_probability, notification, sar_oilspill, sarlive,firebase_storing,logger,anomaly_xai

class AISAnomalyDetectionServer:
    def __init__(self, api_url=None, host='localhost', port=5000):
        self.host = host
        self.port = port
        
        # Initialize AIS Data Processor
        self.ais_processor = AISDataProcessor(api_url)
        
        # Initialize anomaly detection components
        self.anomaly_detector = anomaly_detection.AnomalyDetector()
        self.oil_spill_probab = oil_spill_probability.OilProbability()
        
        # # Setup logging
        # logging.basicConfig(level=logging.INFO, 
        #                     format='%(asctime)s - %(levelname)s - %(message)s')
        # self.logger = logging.getLogger(__name__)
        self.logger=logger.setup_colored_logging()
        
        # Store connected clients
        self.clients = set()
        
        # Server and streaming tasks
        self.server = None
        self.streaming_task = None
        
        # Create a queue for oil spill processing
        self.oil_spill_queue = asyncio.Queue()

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
    
    def sar_oil_spill(self, data):
        ship_data= data[0]
        anomaly_result= data[1]
        anomaly_df= data[2]

        
        anomaly_xai_result=anomaly_xai.explain_prediction(anomaly_df.loc[[0]])
        anomaly_result.update(anomaly_xai_result)        
        
        lat = ship_data.get('LATITUDE')
        long = ship_data.get('LONGITUDE')
        timestamp = ship_data.get('TIMESTAMP')
        print(lat, long, timestamp)
        
        parsed_datetime = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S %Z')

        # Extract just the date
        date_only = parsed_datetime.date()
        date_string = date_only.strftime('%Y-%m-%d')
        
        live_sar_pipeline = sarlive.SARImagePipeline()
        sar_output = live_sar_pipeline.get_sar_image(lat, long, date_string)
        
        sar_image=sar_output['SAR_image']
        if sar_image:
            sar_prediction = sar_oilspill.oilspill_pipeline(sar_image)
        else:
            sar_prediction=None
        
        sar_prediction.update({"Annotated_image":sar_output['Annotated_sar_image'],"Oilspill_Area":sar_output['OilSpill_Area']})
        # Store data in Firebase
        self.logger.info("Storing data in Firebase")
        firebase_storing.store_data_in_firebase(ship_data,anomaly_result,sar_prediction,self.logger)
        
        return sar_prediction

    async def process_oil_spill_queue(self):

        while True:
            try:
                # Wait for and retrieve ship data from the queue
                ship_data = await self.oil_spill_queue.get()
                
                # Process oil spill in a separate thread
                oil_prediction = await asyncio.to_thread(self.sar_oil_spill, ship_data)
                
                # Broadcast oil prediction if clients are connected
                if self.clients and oil_prediction is not None:
                    output = {
                        "mmsi": ship_data.get('MMSI'),
                        "oil_spill_prediction": oil_prediction
                    }
                    await asyncio.gather(
                        *[client.send(json.dumps(output)) for client in self.clients]
                    )
                
                # Mark the queue task as done
                self.oil_spill_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"Error in oil spill processing: {e}")
                # Ensure the task is marked as done even if an error occurs
                self.oil_spill_queue.task_done()
    
    async def stream_ais_data(self):

        # Start the data streaming task
        data_stream_task = asyncio.create_task(self.ais_processor.start_data_stream(interval=120))

        try:
            while True:
                # Read data from the queue
                ship_data = await self.ais_processor.read_data()
                if ship_data:
                    anomaly_df = pd.DataFrame([ship_data])
                    anomaly_df = anomaly_df[['SPEED', 'COURSE', 'LATITUDE', 'LONGITUDE', 'HEADING', 'NAVSTAT','TIMESTAMP']]
                    anomaly_df['TIMESTAMP'] = anomaly_df['TIMESTAMP'].apply(self._categorize_time_of_day)
                    
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

                        # Send notification if anomaly is detected
                        if anomaly_result['anomaly']:
                            tokens = notification.get_tokens_from_firestore()
                            if tokens:
                                notification.send_push_notification(tokens, 'Anomaly Detected', 
                                    f'Anomaly found for ship of MMSI:{ship_data["MMSI"]} Name:{ship_data["NAME"]} at latitude: {anomaly_df["LAT_mean"].loc[0]} and longitude:{anomaly_df["LON_mean"].loc[0]}')
                                self.logger.info("Notifications sent")
                            else:
                                self.logger.error('No tokens found in Firestore.')

                        # If anomaly detected, add to oil spill processing queue
                        if anomaly_result['anomaly']:
                            await self.oil_spill_queue.put((ship_data,anomaly_result,anomaly_df))
                            self.logger.info(f"Added ship {ship_data['MMSI']} to oil spill processing queue")

                        # Broadcast results to all connected clients
                        output = {
                            "ais_data": {k: self.ais_processor.convert_to_json_serializable(v) for k, v in ship_data.items()},
                            "anomaly_result": {k: self.ais_processor.convert_to_json_serializable(v) for k, v in anomaly_result.items()}
                        }
                        print(f"Broadcasting data: {output}")

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
        
        # Start oil spill processing queue task
        self.oil_spill_queue_task = asyncio.create_task(self.process_oil_spill_queue())
        
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
            
            if self.oil_spill_queue_task:
                self.oil_spill_queue_task.cancel()
            
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