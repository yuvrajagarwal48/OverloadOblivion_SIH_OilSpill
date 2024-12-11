import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import geopy.distance
from PIL import Image

def ultra_compress_image(image, max_size_bytes=1_000_000, min_quality=10, resize_threshold=0.5):
    # Create a copy of the image to avoid modifying the original
    img = image.copy()
    
    # Try different compression strategies
    compression_strategies = [
        # Strategy 1: Direct quality reduction
        lambda img, quality: _compress_by_quality(img, quality),
        
        # Strategy 2: Resize and compress
        lambda img, quality: _compress_by_resize(img, quality),
        
        # Strategy 3: Convert to more efficient format
        lambda img, quality: _compress_by_format(img, quality)
    ]
    
    # Try each compression strategy
    for strategy in compression_strategies:
        # Reset image
        img = image.copy()
        
        # Try different quality levels
        for quality in range(95, min_quality, -5):
            try:
                # Attempt compression
                compressed_bytes = strategy(img, quality)
                
                # Check if size is acceptable
                if len(compressed_bytes) <= max_size_bytes:
                    return compressed_bytes
            except Exception:
                # If compression fails, continue to next iteration
                continue
    
    # If all strategies fail, return a minimal representation
    return _minimal_compress(image, max_size_bytes)

def _compress_by_quality(img, quality):
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', optimize=True, quality=quality)
    buffer.seek(0)
    return buffer.getvalue()

def _compress_by_resize(img, quality):
    # Calculate new dimensions
    width, height = img.size
    new_width = int(width * 0.8)  # Reduce to 80% of original size
    new_height = int(height * 0.8)
    
    # Resize with high-quality downsampling
    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
    
    buffer = io.BytesIO()
    resized_img.save(buffer, format='JPEG', optimize=True, quality=quality)
    buffer.seek(0)
    return buffer.getvalue()

def _compress_by_format(img, quality):
    buffer = io.BytesIO()
    # Try WebP which often provides better compression
    img.save(buffer, format='WEBP', quality=quality, method=6)
    buffer.seek(0)
    return buffer.getvalue()

def _minimal_compress(img, max_size):
    buffer = io.BytesIO()
    
    # Try extreme compression techniques
    attempts = [
        # 1. Extremely low quality JPEG
        lambda: img.save(buffer, format='JPEG', quality=10, optimize=True),
        
        # 2. Very small resize
        lambda: img.resize((img.width // 4, img.height // 4), Image.LANCZOS) \
                   .save(buffer, format='JPEG', quality=20, optimize=True),
        
        # 3. Grayscale conversion
        lambda: img.convert('L').save(buffer, format='JPEG', quality=15, optimize=True)
    ]
    
    for attempt in attempts:
        buffer.seek(0)
        buffer.truncate(0)
        attempt()
        
        if len(buffer.getvalue()) <= max_size:
            return buffer.getvalue()
    
    # Absolute last resort: return the smallest possible representation
    buffer.seek(0)
    buffer.truncate(0)
    img.resize((10, 10)).save(buffer, format='JPEG', quality=10, optimize=True)
    return buffer.getvalue()

def annotate_sar_image(lat, lon, base64_image_string, distance_km=15, max_size_bytes=1_000_000):
    try:
        # Decode base64 image string
        if base64_image_string.startswith('data:image'):
            base64_image_string = base64_image_string.split(',')[1]
        
        # Decode base64 to image
        image_bytes = base64.b64decode(base64_image_string)
        img = Image.open(io.BytesIO(image_bytes))
        
        # Generate bounding box points
        def generate_polygon_points(center_lat, center_lon, distance_km):
            center_point = (center_lat, center_lon)
            bearings = [0, 90, 180, 270]  # North, East, South, West
            points = []
            
            for bearing in bearings:
                destination = geopy.distance.distance(kilometers=distance_km).destination(center_point, bearing)
                dest_lat, dest_lon = destination.latitude, destination.longitude
                points.extend([round(dest_lat, 5), round(dest_lon, 5)])
            
            return points
        
        points = generate_polygon_points(lat, lon, distance_km)
        
        # Create a new figure with the same size as the image
        plt.figure(figsize=(10, 10), dpi=100)
        
        # Display the image
        plt.imshow(img)
        
        # Get image dimensions
        img_width, img_height = img.size
        
        # Calculate min/max for bounding box
        lat_min = min(points[::2])
        lat_max = max(points[::2])
        lon_min = min(points[1::2])
        lon_max = max(points[1::2])
        
        # Normalize lat/lon to pixel coordinates
        def lat_lon_to_pixel(lat_val, lon_val):
            x = int((lon_val - lon_min) / (lon_max - lon_min) * img_width)
            y = int((lat_max - lat_val) / (lat_max - lat_min) * img_height)
            return x, y
        
        # Plot grid lines and label them
        num_lat_lines = 5
        num_lon_lines = 5
        
        for i in range(num_lat_lines + 1):
            lat_line = lat_min + (lat_max - lat_min) * (i / num_lat_lines)
            y_pixel = lat_lon_to_pixel(lat_line, lon_min)[1]
            plt.axhline(y=y_pixel, color='white', linestyle='--', linewidth=0.5)
            
            plt.text(5, y_pixel + 5, f'{lat_line:.2f}°N', fontsize=8,
                     color='blue', bbox=dict(facecolor='white', alpha=0.5))

        for i in range(num_lon_lines + 1):
            lon_line = lon_min + (lon_max - lon_min) * (i / num_lon_lines)
            x_pixel = lat_lon_to_pixel(lat_min, lon_line)[0]
            plt.axvline(x=x_pixel, color='white', linestyle='--', linewidth=0.5)
            
            plt.text(x_pixel + 5, img_height - 15, f'{lon_line:.2f}°E', fontsize=8,
                     color='blue', bbox=dict(facecolor='white', alpha=0.5))

        # Mark the input point with a larger red marker and label it
        input_x_pixel, input_y_pixel = lat_lon_to_pixel(lat, lon)
        plt.plot(input_x_pixel, input_y_pixel, 'ro', markersize=10)
        plt.text(input_x_pixel + 40, input_y_pixel - 40, f'Anomaly\n({lat}, {lon})', fontsize=8,
                 color='black', bbox=dict(facecolor='yellow', alpha=0.7))

        plt.title('SAR Image Annotation')
        plt.axis('off')
        
        # Save plot to a buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0)
        buffer.seek(0)

        # Read the plot image
        plot_img = Image.open(buffer)
        
        # Compress the plotted image
        compressed_plot_bytes = ultra_compress_image(plot_img, max_size_bytes)
        
        # Encode the compressed image to base64
        plot_base64 = base64.b64encode(compressed_plot_bytes).decode('utf-8')
        
        plt.close()  # Close the plot to free memory

        return plot_base64
    
    except Exception as e:
        print(f"Error in annotating image: {e}")
        return None

def compress_base64_image(base64_image_string, max_size_bytes=1_000_000):

    # Remove data URL prefix if present
    if base64_image_string.startswith('data:image'):
        base64_image_string = base64_image_string.split(',')[1]
    
    # Decode the image
    image_bytes = base64.b64decode(base64_image_string)
    
    # Open the image
    img = Image.open(io.BytesIO(image_bytes))
    
    # Compress the image
    compressed_bytes = ultra_compress_image(img, max_size_bytes)
    
    # Encode back to base64
    return base64.b64encode(compressed_bytes).decode('utf-8')

# Example usage functions
def get_base64_image_from_path(image_path, max_size_bytes=1_000_000):

    # Open the image
    img = Image.open(image_path)
    
    # Compress the image
    compressed_bytes = ultra_compress_image(img, max_size_bytes)
    
    # Convert to base64
    return base64.b64encode(compressed_bytes).decode('utf-8')