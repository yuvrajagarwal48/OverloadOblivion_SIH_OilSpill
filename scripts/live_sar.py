# import os
# import time
# import ee
# import base64
# import io
# import requests
# import geopy.distance
# from PIL import Image
# from flask import Flask, request, jsonify
# from flask_cors import CORS

# def generate_polygon_points(lat, lon, distance_km=15):
#     """
#     Generate 4 points around the center point to form a polygon.
    
#     Args:
#         lat (float): Latitude of the center point
#         lon (float): Longitude of the center point
#         distance_km (float, optional): Distance from center to polygon vertices. Defaults to 15 km.
    
#     Returns:
#         list: A list of 8 coordinates representing the polygon vertices
#                [north_lat, north_lon, east_lat, east_lon, south_lat, south_lon, west_lat, west_lon]
#     """
#     if lat is None or lon is None:
#         return None

#     try:
#         center_point = (lat, lon)
#         bearings = [0, 90, 180, 270]  # North, East, South, West
#         points = []
        
#         for bearing in bearings:
#             # Calculate destination point
#             destination = geopy.distance.distance(kilometers=distance_km).destination(center_point, bearing)
#             dest_lat, dest_lon = destination.latitude, destination.longitude
#             points.extend([round(dest_lat, 5), round(dest_lon, 5)])
        
#         return points
    
#     except Exception as e:
#         print(f"Error generating polygon points for ({lat}, {lon}): {str(e)}")
#         return None

# def create_polygon_coordinates(coordinates, distance_km=15):
#     """
#     Create a complete set of coordinates for the polygon.
    
#     Args:
#         coordinates (list): List of [longitude, latitude] coordinates
#         distance_km (float, optional): Distance from center to polygon vertices. Defaults to 15 km.
    
#     Returns:
#         dict: A dictionary containing the center point and polygon vertices
#     """
#     # Extract first coordinate if multiple are provided
#     if isinstance(coordinates[0], list):
#         center_lon, center_lat = coordinates[0]
#     else:
#         center_lon, center_lat = coordinates

#     # Generate polygon points
#     polygon_points = generate_polygon_points(center_lat, center_lon, distance_km)
    
#     if polygon_points is None:
#         return None
    
#     # Organize points for the polygon
#     polygon_coordinates = [
#         [center_lon, center_lat],  # Center point first
#         [polygon_points[1], polygon_points[0]],  # North point
#         [polygon_points[3], polygon_points[2]],  # East point
#         [polygon_points[5], polygon_points[4]],  # South point
#         [polygon_points[7], polygon_points[6]],  # West point
#         [center_lon, center_lat]   # Close the polygon by returning to center
#     ]
    
#     return {
#         'center_point': [center_lon, center_lat],
#         'polygon_vertices': polygon_coordinates
#     }

# class SentinelImageProcessor:
#     @staticmethod
#     def initialize_earth_engine():
#         """
#         Authenticate and initialize Earth Engine.
#         """
#         try:
#             ee.Authenticate()
#             ee.Initialize(project='own-rushabhkhandhar38')
#             print("Earth Engine initialized successfully.")
#         except Exception as e:
#             print(f"Earth Engine initialization failed: {e}")

   
#     @staticmethod
#     def process_sentinel_image(roi, start_date, end_date):
#         """
#         Process Sentinel-1 image and return base64 encoded string.
        
#         Args:
#             roi (ee.Geometry): Region of interest
#             start_date (str): Start date for image collection
#             end_date (str): End date for image collection
        
#         Returns:
#             str: Base64 encoded image string
#         """
#         try:
#             # Load Sentinel-1 GRD data and filter it
#             sen1_collection = ee.ImageCollection("COPERNICUS/S1_GRD") \
#                 .filterDate(start_date, end_date) \
#                 .filterBounds(roi) \
#                 .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')) \
#                 .filter(ee.Filter.eq('instrumentMode', 'IW'))

#             # Check if collection is empty
#             collection_size = sen1_collection.size().getInfo()
#             if collection_size == 0:
#                 raise Exception(f"No Sentinel-1 images found for the given date range and region")

#             # Create median image with VV polarization
#             sen1 = sen1_collection.select('VV').median()
            
#             # Check if image is valid
#             if sen1 is None:
#                 raise Exception("Failed to create median image from Sentinel-1 collection")

#             # Calculate image statistics
#             image_stats = sen1.reduceRegion(
#                 reducer=ee.Reducer.percentile([2, 98]),
#                 geometry=roi,
#                 scale=100,  # Increased scale to reduce computation
#                 maxPixels=1e9
#             )

#             # Get percentile values
#             min_val = image_stats.get('VV_p2').getInfo()
#             max_val = image_stats.get('VV_p98').getInfo()

#             # Ensure min and max values are different
#             if min_val == max_val:
#                 min_val = min_val - 1
#                 max_val = max_val + 1

#             # Use visualization parameters to create a displayable image
#             vis_params = {
#                 'min': min_val,
#                 'max': max_val,
#                 'palette': ['black', 'white']  # Simple grayscale palette
#             }

#             # Get download URL with visualization parameters
#             download_url = sen1.visualize(**vis_params).getDownloadURL({
#                 'region': roi,
#                 'scale': 200,  # Significantly reduced scale
#                 'format': 'PNG'
#             })

#             # Download the image
#             response = requests.get(download_url, timeout=60)
            
#             if response.status_code != 200:
#                 raise Exception(f"Failed to download image. Status code: {response.status_code}")

#             # Save the image to a bytes buffer
#             image_bytes = io.BytesIO(response.content)
            
#             # Open the image with Pillow
#             with Image.open(image_bytes) as img:
#                 # Convert to grayscale
#                 img = img.convert('L')
                
#                 # Resize to a very small image
#                 img = img.resize((256, 256), Image.LANCZOS)
                
#                 # Save to a bytes buffer with high compression
#                 buffer = io.BytesIO()
#                 img.save(buffer, format='PNG', optimize=True, compress_level=9)
                
#                 # Encode to base64
#                 base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
#             return base64_image
        
#         except Exception as e:
#             print(f"Image processing error: {e}")
#             return None

# # Rest of the code remains the same as in the previous version
# class FlaskApp:
#     def __init__(self):
#         self.app = Flask(__name__)
#         CORS(self.app)  # Enable CORS for all routes
        
#         # Initialize routes
#         self.init_routes()

#     def init_routes(self):
#         """
#         Initialize Flask routes
#         """
#         @self.app.route('/process-sentinel-image', methods=['POST'])
#         def process_image():
#             """
#             API endpoint to process Sentinel-1 image
#             """
#             try:
#                 # Get request data
#                 data = request.json
                
#                 # Validate input
#                 required_keys = ['coordinates', 'start_date', 'end_date']
#                 if not all(key in data for key in required_keys):
#                     return jsonify({
#                         'error': 'Missing required parameters',
#                         'required': required_keys
#                     }), 400
                
#                 # Extract coordinates
#                 coordinates = data['coordinates']
#                 start_date = data['start_date']
#                 end_date = data['end_date']

#                 # Generate polygon coordinates with smaller radius
#                 polygon_data = create_polygon_coordinates(coordinates, distance_km=15)
                
#                 if polygon_data is None:
#                     return jsonify({
#                         'error': 'Failed to generate polygon coordinates'
#                     }), 500

#                 # Create ROI geometry
#                 roi = ee.Geometry.Polygon(polygon_data['polygon_vertices'])

#                 # Process image
#                 base64_image = SentinelImageProcessor.process_sentinel_image(
#                     roi, start_date, end_date
#                 )

#                 if base64_image:
#                     return jsonify({
#                         'status': 'success',
#                         'base64_image': base64_image,
#                         'center_point': polygon_data['center_point'],
#                         'polygon_vertices': polygon_data['polygon_vertices']
#                     })
#                 else:
#                     return jsonify({
#                         'error': 'Failed to process image'
#                     }), 500

#             except Exception as e:
#                 return jsonify({
#                     'error': str(e)
#                 }), 500

#         @self.app.route('/health', methods=['GET'])
#         def health_check():
#             """
#             Health check endpoint
#             """
#             return jsonify({
#                 'status': 'healthy',
#                 'message': 'Sentinel Image Processing API is running'
#             }), 200

#     def run(self, host='0.0.0.0', port=5000, debug=True):
#         """
#         Run the Flask application
#         """
#         # Initialize Earth Engine before starting the server
#         SentinelImageProcessor.initialize_earth_engine()
        
#         # Run the Flask app
#         self.app.run(host=host, port=port, debug=debug)

# def main():
#     """
#     Main function to start the Flask application
#     """
#     flask_app = FlaskApp()
#     flask_app.run()

# if __name__ == '__main__':
#     main()


import os
import time
import ee
import base64
import io
import requests
import geopy.distance
import numpy as np
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS

def generate_polygon_points(lat, lon, distance_km=15):
    """
    Generate 4 points around the center point to form a polygon.
    
    Args:
        lat (float): Latitude of the center point
        lon (float): Longitude of the center point
        distance_km (float, optional): Distance from center to polygon vertices. Defaults to 15 km.
    
    Returns:
        list: A list of 8 coordinates representing the polygon vertices
               [north_lat, north_lon, east_lat, east_lon, south_lat, south_lon, west_lat, west_lon]
    """
    if lat is None or lon is None:
        return None

    try:
        center_point = (lat, lon)
        bearings = [0, 90, 180, 270]  # North, East, South, West
        points = []
        
        for bearing in bearings:
            # Calculate destination point
            destination = geopy.distance.distance(kilometers=distance_km).destination(center_point, bearing)
            dest_lat, dest_lon = destination.latitude, destination.longitude
            points.extend([round(dest_lat, 5), round(dest_lon, 5)])
        
        return points
    
    except Exception as e:
        print(f"Error generating polygon points for ({lat}, {lon}): {str(e)}")
        return None

def create_polygon_coordinates(coordinates, distance_km=15):
    """
    Create a complete set of coordinates for the polygon.
    
    Args:
        coordinates (list): List of [longitude, latitude] coordinates
        distance_km (float, optional): Distance from center to polygon vertices. Defaults to 15 km.
    
    Returns:
        dict: A dictionary containing the center point and polygon vertices
    """
    # Extract first coordinate if multiple are provided
    if isinstance(coordinates[0], list):
        center_lon, center_lat = coordinates[0]
    else:
        center_lon, center_lat = coordinates

    # Generate polygon points
    polygon_points = generate_polygon_points(center_lat, center_lon, distance_km)
    
    if polygon_points is None:
        return None
    
    # Organize points for the polygon
    polygon_coordinates = [
        [center_lon, center_lat],  # Center point first
        [polygon_points[1], polygon_points[0]],  # North point
        [polygon_points[3], polygon_points[2]],  # East point
        [polygon_points[5], polygon_points[4]],  # South point
        [polygon_points[7], polygon_points[6]],  # West point
        [center_lon, center_lat]   # Close the polygon by returning to center
    ]
    
    return {
        'center_point': [center_lon, center_lat],
        'polygon_vertices': polygon_coordinates
    }

class SentinelImageProcessor:
    @staticmethod
    def initialize_earth_engine():
        """
        Authenticate and initialize Earth Engine.
        """
        try:
            ee.Authenticate()
            ee.Initialize(project='own-rushabhkhandhar38')
            print("Earth Engine initialized successfully.")
        except Exception as e:
            print(f"Earth Engine initialization failed: {e}")

    @staticmethod
    def lee_sigma_filter(image, lookNumber=4, sigmaThreshold=0.5):
        """
        Apply Lee Sigma despeckle filter to the Sentinel-1 image.
        
        Args:
            image (ee.Image): Input SAR image
            lookNumber (int): Number of looks in the image
            sigmaThreshold (float): Threshold for filtering
        
        Returns:
            ee.Image: Despeckled image
        """
        def sigma_filter(image):
            # Calculate local mean
            localMean = image.reduceNeighborhood(
                reducer=ee.Reducer.mean(),
                kernel=ee.Kernel.square(1)
            )
            
            # Calculate local variance
            localVariance = image.reduceNeighborhood(
                reducer=ee.Reducer.variance(),
                kernel=ee.Kernel.square(1)
            )
            
            # Calculate coefficient of variation squared
            cu = localVariance.divide(localMean.pow(2))
            
            # Calculate theoretical coefficient of variation
            cu_teorico = 1.0 / lookNumber
            
            # Create mask based on sigma threshold
            mask = cu.lte(cu_teorico * (sigmaThreshold ** 2 + 1))
            
            # Apply filter
            filtered = localMean.updateMask(mask)
            return filtered.unmask(image)
        
        return sigma_filter(image)

    @staticmethod
    def calculate_oil_area(image, roi, threshold_percentile=90, scale=100):
        """
        Calculate the oil area based on image thresholding.
        
        Args:
            image (ee.Image): Input SAR image
            roi (ee.Geometry): Region of interest
            threshold_percentile (int): Percentile for thresholding
            scale (int): Scale for calculation
        
        Returns:
            float: Estimated oil area in square kilometers
        """
        try:
            # Ensure the image has the correct band name
            if 'VV' not in image.bandNames().getInfo():
                image = image.select([0], ['VV'])
            
            # Calculate image statistics with robust error handling
            try:
                # Use multiple reducers to get a comprehensive view
                reducers = ee.Reducer.min().combine(
                    ee.Reducer.max(), 
                    sharedInputs=True
                ).combine(
                    ee.Reducer.percentile([threshold_percentile]), 
                    sharedInputs=True
                )
                
                image_stats = image.reduceRegion(
                    reducer=reducers,
                    geometry=roi,
                    scale=scale,
                    maxPixels=1e9
                )
                
                # Print out the full stats for debugging
                print("Image Statistics (Raw):", image_stats.getInfo())
                
                # Extract threshold value
                if f'VV_p{threshold_percentile}' in image_stats.keys():
                    threshold_value = image_stats.get(f'VV_p{threshold_percentile}').getInfo()
                else:
                    # Fallback to min or a computed threshold
                    threshold_value = image_stats.get('VV_min').getInfo() + \
                        0.5 * (image_stats.get('VV_max').getInfo() - image_stats.get('VV_min').getInfo())
            
            except Exception as stats_error:
                print(f"Error calculating image statistics: {stats_error}")
                # Absolute fallback thresholding
                threshold_value = image.reduceRegion(
                    reducer=ee.Reducer.percentile([threshold_percentile]),
                    geometry=roi,
                    scale=scale,
                    maxPixels=1e9
                ).values().get(0).getInfo()
            
            print(f"Threshold Value: {threshold_value}")
            
            # Create binary mask of potential oil areas
            oil_mask = image.lt(threshold_value)
            
            # Calculate area of the mask
            area_image = oil_mask.multiply(ee.Image.pixelArea())
            
            # Reduce the area within the ROI
            area_result = area_image.reduceRegion(
                reducer=ee.Reducer.sum(),
                geometry=roi,
                scale=scale,
                maxPixels=1e9
            )
            
            # Convert to square kilometers
            oil_area_sqkm = area_result.values().get(0).getInfo() / 1000000
            
            return round(oil_area_sqkm, 2)
        
        except Exception as e:
            print(f"Comprehensive error calculating oil area: {e}")
            return None

    @staticmethod
    def process_sentinel_image(roi, start_date, end_date):
        """
        Process Sentinel-1 image and return base64 encoded string with additional analysis.
        
        Args:
            roi (ee.Geometry): Region of interest
            start_date (str): Start date for image collection
            end_date (str): End date for image collection
        
        Returns:
            dict: Dictionary containing base64 image and additional information
        """
        try:
            # Load Sentinel-1 GRD data and filter it
            sen1_collection = ee.ImageCollection("COPERNICUS/S1_GRD") \
                .filterDate(start_date, end_date) \
                .filterBounds(roi) \
                .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')) \
                .filter(ee.Filter.eq('instrumentMode', 'IW'))

            # Check if collection is empty
            collection_size = sen1_collection.size().getInfo()
            if collection_size == 0:
                raise Exception(f"No Sentinel-1 images found for the given date range and region")

            # Create median image with VV polarization
            sen1 = sen1_collection.select('VV').median()
            
            # Apply despeckle filter
            despeckled_image = SentinelImageProcessor.lee_sigma_filter(sen1)
            
            # Check if image is valid
            if sen1 is None:
                raise Exception("Failed to create median image from Sentinel-1 collection")

            # Calculate oil area first (before visualization)
            oil_area = SentinelImageProcessor.calculate_oil_area(
                despeckled_image, roi, threshold_percentile=90, scale=200
            )

            # Robust image statistics retrieval
            def safe_get_stat(reducer):
                try:
                    stat = despeckled_image.reduceRegion(
                        reducer=reducer,
                        geometry=roi,
                        scale=100,
                        maxPixels=1e9
                    ).values().get(0).getInfo()
                    return stat
                except Exception as e:
                    print(f"Error retrieving statistic: {e}")
                    return None

            # Get min and max values
            min_val = safe_get_stat(ee.Reducer.min()) or -20
            max_val = safe_get_stat(ee.Reducer.max()) or 0

            # Ensure min and max values are different
            if min_val == max_val:
                min_val = min_val - 1
                max_val = max_val + 1

            # Use visualization parameters to create a displayable image
            vis_params = {
                'min': min_val,
                'max': max_val,
                'palette': ['black', 'white']  # Simple grayscale palette
            }

            # Get download URL with visualization parameters
            download_url = despeckled_image.visualize(**vis_params).getDownloadURL({
                'region': roi,
                'scale': 200,  # Significantly reduced scale
                'format': 'PNG'
            })

            # Download the image
            response = requests.get(download_url, timeout=60)
            
            if response.status_code != 200:
                raise Exception(f"Failed to download image. Status code: {response.status_code}")

            # Save the image to a bytes buffer
            image_bytes = io.BytesIO(response.content)
            
            # Open the image with Pillow
            with Image.open(image_bytes) as img:
                # Convert to grayscale
                img = img.convert('L')
                
                # Resize to a very small image
                img = img.resize((256, 256), Image.LANCZOS)
                
                # Save to a bytes buffer with high compression
                buffer = io.BytesIO()
                img.save(buffer, format='PNG', optimize=True, compress_level=9)
                
                # Encode to base64
                base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return {
                'base64_image': base64_image,
                'oil_area_sqkm': oil_area
            }
        
        except Exception as e:
            print(f"Comprehensive image processing error: {e}")
            return None

# Rest of the code (FlaskApp, main function) remains the same as in the previous version

class FlaskApp:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for all routes
        
        # Initialize routes
        self.init_routes()

    def init_routes(self):
        """
        Initialize Flask routes
        """
        @self.app.route('/process-sentinel-image', methods=['POST'])
        def process_image():
            """
            API endpoint to process Sentinel-1 image
            """
            try:
                # Get request data
                data = request.json
                
                # Validate input
                required_keys = ['coordinates', 'start_date', 'end_date']
                if not all(key in data for key in required_keys):
                    return jsonify({
                        'error': 'Missing required parameters',
                        'required': required_keys
                    }), 400
                
                # Extract coordinates
                coordinates = data['coordinates']
                start_date = data['start_date']
                end_date = data['end_date']

                # Generate polygon coordinates with smaller radius
                polygon_data = create_polygon_coordinates(coordinates, distance_km=15)
                
                if polygon_data is None:
                    return jsonify({
                        'error': 'Failed to generate polygon coordinates'
                    }), 500

                # Create ROI geometry
                roi = ee.Geometry.Polygon(polygon_data['polygon_vertices'])

                # Process image
                processed_result = SentinelImageProcessor.process_sentinel_image(
                    roi, start_date, end_date
                )

                if processed_result:
                    return jsonify({
                        'status': 'success',
                        'base64_image': processed_result['base64_image'],
                        'oil_area_sqkm': processed_result['oil_area_sqkm'],
                        'center_point': polygon_data['center_point'],
                        'polygon_vertices': polygon_data['polygon_vertices']
                    })
                else:
                    return jsonify({
                        'error': 'Failed to process image'
                    }), 500

            except Exception as e:
                return jsonify({
                    'error': str(e)
                }), 500

        @self.app.route('/health', methods=['GET'])
        def health_check():
            """
            Health check endpoint
            """
            return jsonify({
                'status': 'healthy',
                'message': 'Sentinel Image Processing API is running'
            }), 200

    def run(self, host='0.0.0.0', port=5000, debug=True):
        """
        Run the Flask application
        """
        # Initialize Earth Engine before starting the server
        SentinelImageProcessor.initialize_earth_engine()
        
        # Run the Flask app
        self.app.run(host=host, port=port, debug=debug)

def main():
    """
    Main function to start the Flask application
    """
    flask_app = FlaskApp()
    flask_app.run()

if __name__ == '__main__':
    main()
    