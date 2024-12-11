import os
import ee
import base64
import io
import requests
import geopy.distance
from PIL import Image
from datetime import datetime, timedelta
from . import sar_plotting
import dotenv

dotenv.load_dotenv()

class SARImagePipeline:
    def __init__(self):
        try:
            ee.Authenticate()
            ee.Initialize(project=os.getenv("PROJECT_ID"))
            print("Earth Engine initialized successfully.")
        except Exception as e:
            print(f"Earth Engine initialization failed: {e}")

    def generate_polygon_points(self, lat, lon, distance_km=15):
        try:
            center_point = (lat, lon)
            bearings = [0, 90, 180, 270]  # North, East, South, West
            points = []
            
            for bearing in bearings:
                destination = geopy.distance.distance(kilometers=distance_km).destination(center_point, bearing)
                dest_lat, dest_lon = destination.latitude, destination.longitude
                points.extend([round(dest_lat, 5), round(dest_lon, 5)])
            
            return points
        
        except Exception as e:
            print(f"Polygon generation error: {e}")
            return None

    def create_polygon_coordinates(self, lat, lon, distance_km=15):
        try:
            polygon_points = self.generate_polygon_points(lat, lon, distance_km)
            
            if polygon_points is None:
                return None

            polygon_coordinates = [
                [polygon_points[1], polygon_points[0]],  # North point
                [polygon_points[3], polygon_points[2]],  # East point
                [polygon_points[5], polygon_points[4]],  # South point
                [polygon_points[7], polygon_points[6]],  # West point
                [polygon_points[1], polygon_points[0]]   # Close polygon
            ]
            
            return ee.Geometry.Polygon([polygon_coordinates])
        
        except Exception as e:
            print(f"Polygon coordinate creation error: {e}")
            return None

    def calculate_area(self, roi):
        try:
            area = roi.area().getInfo() / 1e6  # Convert from m² to km²
            print(f"Area of ROI: {area:.2f} km²")
            return area
        except Exception as e:
            print(f"Error calculating area: {e}")
            return None

    def displace_coordinates(self, lat, lon, lat_offset=0.0, lon_offset=0.0):
        try:
            displaced_lat = lat + lat_offset
            displaced_lon = lon + lon_offset
            print(f"Displaced coordinates: Latitude {displaced_lat}, Longitude {displaced_lon}")
            return displaced_lat, displaced_lon
        except Exception as e:
            print(f"Error in displacing coordinates: {e}")
            return lat, lon

    def process_sentinel_image(self, roi, end_date, days_back=30):
        try:
            # Parse end date
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            start_datetime = end_datetime - timedelta(days=days_back)
            
            start_date = start_datetime.strftime('%Y-%m-%d')

            # Load and filter Sentinel-1 collection
            sen1_collection = ee.ImageCollection("COPERNICUS/S1_GRD") \
                .filterDate(start_date, end_date) \
                .filterBounds(roi) \
                .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')) \
                .filter(ee.Filter.eq('instrumentMode', 'IW'))

            # Check collection size
            collection_size = sen1_collection.size().getInfo()
            if collection_size == 0:
                print(f"No Sentinel-1 images found between {start_date} and {end_date}")
                return None

            # Create median image
            sen1 = sen1_collection.select('VV').median()
            
            if sen1 is None:
                print("Failed to create median image")
                return None

            # Calculate image statistics
            image_stats = sen1.reduceRegion(
                reducer=ee.Reducer.percentile([2, 98]),
                geometry=roi,
                scale=100,
                maxPixels=1e9
            )

            # Get percentile values
            min_val = image_stats.get('VV_p2').getInfo()
            max_val = image_stats.get('VV_p98').getInfo()

            # Ensure min and max are different
            if min_val == max_val:
                min_val = min_val - 1
                max_val = max_val + 1

            # Visualization parameters
            vis_params = {
                'min': min_val,
                'max': max_val,
                'palette': ['black', 'white']
            }

            # Get download URL
            download_url = sen1.visualize(**vis_params).getDownloadURL({
                'region': roi.getInfo(),
                'scale': 200,
                'format': 'PNG'
            })

            # Download image
            response = requests.get(download_url, timeout=60)
            
            if response.status_code != 200:
                print(f"Image download failed. Status code: {response.status_code}")
                return None

            # Process image
            image_bytes = io.BytesIO(response.content)
            
            with Image.open(image_bytes) as img:
                img = img.convert('L')
                img = img.resize((256, 256), Image.LANCZOS)
                
                buffer = io.BytesIO()
                img.save(buffer, format='PNG', optimize=True, compress_level=9)
                
                base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return base64_image
        
        except Exception as e:
            print(f"SAR image processing error: {e}")
            return None

    def get_sar_image(self, latitude, longitude, end_date, days_back=30, lat_offset=0.0, lon_offset=0.0):
        try:
            # Displace coordinates if needed
            displaced_lat, displaced_lon = self.displace_coordinates(latitude, longitude, lat_offset, lon_offset)

            # Create ROI polygon
            roi = self.create_polygon_coordinates(displaced_lat, displaced_lon)
            
            if roi is None:
                print("Failed to create region of interest")
                return None

            # Calculate area
            area=self.calculate_area(roi)

            # Process and get SAR image
            sar_image = self.process_sentinel_image(roi, end_date, days_back)
            
            annotated_image=sar_plotting.annotate_sar_image(latitude,longitude,sar_image)
            
            
            return {"SAR_image":sar_image,"Annotated_sar_image":annotated_image,"OilSpill_Area":area}
        
        except Exception as e:
            print(f"SAR image pipeline error: {e}")
            return None

# def main():
#     # Example usage
#     pipeline = SARImagePipeline()
    
#     # Input parameters
#     latitude = 22.7  # Example latitude
#     longitude = 75.8  # Example longitude
#     end_date = '2023-12-31'  # Example end date
#     lat_offset = 0.05  # Latitude offset for displacement
#     lon_offset = 0.05  # Longitude offset for displacement

#     # Get SAR image
#     sar_image = pipeline.get_sar_image(latitude, longitude, end_date, lat_offset=lat_offset, lon_offset=lon_offset)
#     with open("annotated.txt",'w') as f:
#         f.write(sar_image['Annotated_sar_image'])
    
#     if sar_image:
#         print("SAR image processed successfully")
#         # print(sar_image)
#     else:
#         print("Failed to retrieve SAR image")

# if __name__ == '__main__':
#     main()