import asyncio
import websockets
import json
import logging
from datetime import datetime

class LiveAISStream:
    def __init__(self, api_key, bounding_boxes=None, filter_message_types=None):
        """
        Initialize AIS Live Stream
        
        :param api_key: AIS Stream API Key
        :param bounding_boxes: List of bounding box coordinates
        :param filter_message_types: List of message types to filter
        """
        self.api_key = api_key
        self.bounding_boxes = bounding_boxes or [[[-90, 15], [30, -90]]]
        self.filter_message_types = filter_message_types or ["PositionReport"]
        
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

    async def connect_and_stream(self, message_handler):
        """
        Connect to AIS stream and process messages
        
        :param message_handler: Async function to handle each AIS message
        """
        try:
            async with websockets.connect('wss://stream.aisstream.io/v0/stream') as ais_websocket:
                # Prepare subscription message
                subscribe_message = {
                    "APIKEY": self.api_key,
                    "BoundingBoxes": self.bounding_boxes,
                    "FilterMessageTypes": self.filter_message_types
                }
                
                # Send subscription message
                await ais_websocket.send(json.dumps(subscribe_message))
                self.logger.info("Subscribed to AIS stream.")

                # Stream messages
                async for message_json in ais_websocket:
                    try:
                        message = json.loads(message_json)
                        
                        # Only process Position Reports
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

                            # Call message handler with processed AIS data
                            await message_handler(ais_data)

                    except Exception as e:
                        self.logger.error(f"Error processing AIS message: {e}")

        except Exception as e:
            self.logger.error(f"AIS Stream connection error: {e}")