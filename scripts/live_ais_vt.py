import json
import logging
import numpy as np
import asyncio
import requests
import os
import dotenv
from concurrent.futures import ThreadPoolExecutor

dotenv.load_dotenv()

class AISDataProcessor:
    def __init__(self, api_url=None):
        self._api_url = api_url #or os.getenv("API_URL")
        
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Thread pool for running blocking I/O operations
        self.executor = ThreadPoolExecutor(max_workers=1)
        
        # Queue to store incoming AIS data
        self.ais_data_queue = asyncio.Queue()

    def _fetch_ais_data(self):
        """
        Synchronous method to fetch AIS data from the API
        """
        try:
            response = requests.get(self._api_url)
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"API request failed with status {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"Error fetching AIS data: {e}")
            return []

    async def fetch_ais_data(self):
        """
        Asynchronous wrapper for API data fetching
        """
        # Run the blocking request in a thread pool
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, self._fetch_ais_data)
    
    async def start_data_stream(self, interval=120):
        """
        Continuously fetch and stream AIS data
        """
        while True:
            try:
                # Fetch data from API
                data = await self.fetch_ais_data()
                
                # Process and filter data
                filtered_data = self.filter_ais_data(data)
                
                # Add filtered data to queue one by one with a small delay
                for entry in filtered_data:
                    await self.ais_data_queue.put(entry)
                    # Add a small delay between putting items to simulate streaming
                    await asyncio.sleep(0.5)
                
                # Log completion of a batch fetch
                self.logger.info(f"Added {len(filtered_data)} entries to the queue.")
                
                # Wait for the next interval
                await asyncio.sleep(interval)
            
            except Exception as e:
                self.logger.error(f"Error in data streaming: {e}")
                await asyncio.sleep(interval)

    def filter_ais_data(self, data, lat_range=(15, 30), long_range=(-100, -80)):
        """
        Filter AIS data based on latitude and longitude ranges
        """
        print(data)
        filtered_ais_data = []

        for entry in data:
            try:
                # Handle different API response structures
                ais_data = entry.get("AIS", entry)
                
                # Check if latitude and longitude are within the specified ranges
                latitude = ais_data.get("LATITUDE")
                longitude = ais_data.get("LONGITUDE")
                
                if (latitude is not None and longitude is not None and
                    lat_range[0] <= latitude <= lat_range[1] and 
                    long_range[0] <= longitude <= long_range[1]):
                    
                    # Create a dictionary for the valid entry
                    ais_dict = {
                        "MMSI": ais_data.get("MMSI"),
                        "TIMESTAMP": ais_data.get("TIMESTAMP"),
                        "LATITUDE": latitude,
                        "LONGITUDE": longitude,
                        "COURSE": ais_data.get("COURSE"),
                        "SPEED": ais_data.get("SPEED"),
                        "HEADING": ais_data.get("HEADING"),
                        "NAVSTAT": ais_data.get("NAVSTAT"),
                        "IMO": ais_data.get("IMO"),
                        "NAME": ais_data.get("NAME"),
                        "CALLSIGN": ais_data.get("CALLSIGN"),
                        "TYPE": ais_data.get("TYPE"),
                        "A": ais_data.get("A"),
                        "B": ais_data.get("B"),
                        "C": ais_data.get("C"),
                        "D": ais_data.get("D"),
                        "DRAUGHT": ais_data.get("DRAUGHT"),
                        "DESTINATION": ais_data.get("DESTINATION"),
                        "LOCODE": ais_data.get("LOCODE"),
                        "ETA_AIS": ais_data.get("ETA_AIS"),
                        "ETA": ais_data.get("ETA"),
                        "SRC": ais_data.get("SRC"),
                        "ZONE": ais_data.get("ZONE"),
                        "ECA": ais_data.get("ECA"),
                        "DISTANCE_REMAINING": ais_data.get("DISTANCE_REMAINING"),
                        "ETA_PREDICTED": ais_data.get("ETA_PREDICTED"),
                    }
                    
                    # Add the valid dictionary to the filtered list
                    filtered_ais_data.append(ais_dict)
            
            except Exception as e:
                self.logger.error(f"Error processing entry: {e}")

        return filtered_ais_data

    async def read_data(self, lat_range=(15, 30), long_range=(-100, -80)):
        """
        Read and filter data from the queue with timeout
        """
        try:
            # Use asyncio.wait_for to prevent indefinite waiting
            data = await asyncio.wait_for(self.ais_data_queue.get(), timeout=5.0)
            return data
        except asyncio.TimeoutError:
            self.logger.info("No data available in the queue")
            return None
        except Exception as e:
            self.logger.error(f"Error reading data: {e}")
            return None
        
    def read_file(self):
        """
        Backward compatibility method to read from file
        """
        try:
            with open(self._api_url, 'r') as file:
                return json.load(file)
        except Exception as e:
            self.logger.error(f"Error reading file: {e}")
            return []

    @staticmethod
    def convert_to_json_serializable(obj):
        """
        Convert numpy types to native Python types for JSON serialization
        """
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        return obj