import asyncio
import websockets
import json
from datetime import datetime

def convert_to_timeofday(timestamp):
    # Convert timestamp to time of day
    time_of_day = datetime.utcfromtimestamp(timestamp).strftime('%H:%M:%S')

    # Extract the hour from the time_of_day
    hour = int(datetime.utcfromtimestamp(timestamp).strftime('%H'))

    # Define time ranges and categorize the time
    if 5 <= hour < 12:
        time_category = 'morning'
    elif 12 <= hour < 17:
        time_category = 'afternoon'
    elif 17 <= hour < 21:
        time_category = 'evening'
    else:
        time_category = 'night'

    return time_category


async def connect_ais_stream():
    async with websockets.connect('wss://stream.aisstream.io/v0/stream') as websocket:
        subscribe_message = {
            "APIKEY": "",
            "BoundingBoxes": [[[-90, 15], [30, -90]]],
            "FilterMessageTypes": ["PositionReport"]
        }
        subscribe_message_json = json.dumps(subscribe_message)
        await websocket.send(subscribe_message_json)

        print("Listening for AIS data...")

        # Continuously receive and process messages
        async for message_json in websocket:
            try:
                message = json.loads(message_json)
                if "PositionReport" in message["Message"]:
                    position_data = message["Message"]["PositionReport"]
                    meta_data = message["MetaData"]

                    # Extract the required fields
                    sog = position_data["Sog"]
                    cog = position_data["Cog"]
                    latitude = position_data["Latitude"]
                    longitude = position_data["Longitude"]
                    heading = position_data["TrueHeading"]
                    status = position_data["NavigationalStatus"]

                    # Convert the timestamp to a time of day format
                    timestamp = position_data["Timestamp"]
                    # time_of_day = datetime.utcfromtimestamp(timestamp).strftime('%H:%M:%S')
                    time_of_day=convert_to_timeofday(timestamp)

                    # Prepare the output in dictionary format
                    output_dict = {
                        'SOG_mean': sog,
                        'COG_mean': cog,
                        'LAT_mean': latitude,
                        'LON_mean': longitude,
                        'Heading_mean_heading': heading,
                        'Status_mode': status,
                        'TimeOfDay_mode': time_of_day
                    }
                    print(output_dict)

            except json.JSONDecodeError as e:
                print(f"Error decoding message: {e}")
                continue

if __name__ == "__main__":
    asyncio.run(connect_ais_stream())


