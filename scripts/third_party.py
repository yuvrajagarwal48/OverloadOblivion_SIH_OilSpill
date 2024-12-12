# import os
# import io
# import cv2
# import base64
# import numpy as np
# from fastapi import FastAPI, File, UploadFile, HTTPException
# from pydantic import BaseModel
# from ultralytics import YOLO
# from PIL import Image
# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI(title="Oil Spill Detection API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],  # Allow only your frontend origin
#     allow_credentials=True,
#     allow_methods=["*"],  # Allow all HTTP methods
#     allow_headers=["*"],  # Allow all headers
# )
# MODEL_PATH = "models/yolo/best.pt"
# model = YOLO(MODEL_PATH)

# class DetectionResponse(BaseModel):
#     image_base64: str

# @app.post("/detect/", response_model=DetectionResponse)
# async def detect_oil_spill(file: UploadFile = File(...)):
#     try:
#         # Read the uploaded file
#         contents = await file.read()

#         # Convert the file contents into an OpenCV image
#         nparr = np.frombuffer(contents, np.uint8)
#         image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#         # Validate the image
#         if image is None:
#             raise HTTPException(status_code=400, detail="Invalid image file")

#         # Perform object detection
#         results = model(image, conf=0.5)[0]

#         # Annotate the image
#         annotated_image = results.plot()

#         # Encode the annotated image as JPEG
#         _, buffer = cv2.imencode('.jpg', annotated_image)

#         # Convert the image to a Base64 string
#         image_base64 = base64.b64encode(buffer).decode('utf-8')

#         return DetectionResponse(image_base64=image_base64)

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/")
# async def root():
#     return {
#         "message": "Oil Spill Detection API",
#         "model": "YOLOv11",
#         "endpoint": "/detect/ - Upload an image for oil spill detection"
#     }

# @app.post("/batch-detect/")
# async def batch_detect_oil_spills(files: list[UploadFile] = File(...)):
#     try:
#         results = []

#         for file in files:
#             contents = await file.read()
#             nparr = np.frombuffer(contents, np.uint8)
#             image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#             if image is None:
#                 continue

#             # Perform object detection
#             detection_results = model(image, conf=0.3)[0]

#             # Annotate the image
#             annotated_image = detection_results.plot()

#             # Encode the annotated image as JPEG
#             _, buffer = cv2.imencode('.jpg', annotated_image)

#             # Convert the image to a Base64 string
#             image_base64 = base64.b64encode(buffer).decode('utf-8')
#             results.append({"image_base64": image_base64})

#         return results

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=5000)

import os
import io
import cv2
import base64
import numpy as np
from ultralytics import YOLO
from pydantic import BaseModel

# Configuration
MODEL_PATH = "models/yolo/best.pt"
model = YOLO(MODEL_PATH)

class DetectionResponse(BaseModel):
    image_base64: str

def detect_oil_spill_single(file_contents):
    """
    Detect oil spills in a single image
    
    Args:
        file_contents (bytes): Image file contents
    
    Returns:
        DetectionResponse: Annotated image in base64 format
    """
    try:
        # Convert the file contents into an OpenCV image
        nparr = np.frombuffer(file_contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Validate the image
        if image is None:
            raise ValueError("Invalid image file")

        # Perform object detection
        results = model(image, conf=0.5)[0]

        # Annotate the image
        annotated_image = results.plot()

        # Encode the annotated image as JPEG
        _, buffer = cv2.imencode('.jpg', annotated_image)

        # Convert the image to a Base64 string
        image_base64 = base64.b64encode(buffer).decode('utf-8')

        return DetectionResponse(image_base64=image_base64)

    except Exception as e:
        raise ValueError(f"Detection error: {str(e)}")

def batch_detect_oil_spills(files_contents):
    """
    Detect oil spills in multiple images
    
    Args:
        files_contents (list): List of image file contents
    
    Returns:
        list: List of detection results
    """
    try:
        results = []

        for contents in files_contents:
            try:
                nparr = np.frombuffer(contents, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if image is None:
                    continue

                # Perform object detection
                detection_results = model(image, conf=0.3)[0]

                # Annotate the image
                annotated_image = detection_results.plot()

                # Encode the annotated image as JPEG
                _, buffer = cv2.imencode('.jpg', annotated_image)

                # Convert the image to a Base64 string
                image_base64 = base64.b64encode(buffer).decode('utf-8')
                results.append({"image_base64": image_base64})

            except Exception as inner_e:
                print(f"Error processing an image: {inner_e}")

        return results

    except Exception as e:
        raise ValueError(f"Batch detection error: {str(e)}")