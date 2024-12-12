from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Import from your local modules
from rag_chatbot import AISData, OilSpillAnalysisResult, initialize_database, analyze_oil_spill
from third_party import (
    detect_oil_spill_single, 
    batch_detect_oil_spills, 
    DetectionResponse
)

app = FastAPI(
    title="Comprehensive Oil Spill Management API",
    description="API for oil spill analysis, detection, and environmental impact assessment"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for database
chroma_client = None
collection = None

@app.on_event("startup")
async def startup_event():
    """Initialize the database on application startup."""
    global chroma_client, collection
    chroma_client, collection = initialize_database()

# Oil Spill Analysis Endpoint
@app.post("/analyze_oil_spill", response_model=OilSpillAnalysisResult)
async def analyze_oil_spill_endpoint(ais_data: AISData):
    """Endpoint to analyze oil spill based on AIS data."""
    return analyze_oil_spill(ais_data, chroma_client, collection)

# Oil Spill Detection Endpoints
@app.post("/detect/", response_model=DetectionResponse)
async def detect_oil_spill(file: UploadFile = File(...)):
    try:
        # Read the uploaded file contents
        contents = await file.read()
        
        # Perform detection
        result = detect_oil_spill_single(contents)
        
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/batch-detect/")
async def batch_detect_oil_spills(files: List[UploadFile] = File(...)):
    try:
        # Read contents of all uploaded files
        files_contents = [await file.read() for file in files]
        
        # Perform batch detection
        results = batch_detect_oil_spills(files_contents)
        
        return results

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

# Root endpoint with API information
@app.get("/")
async def root():
    return {
        "message": "Comprehensive Oil Spill Management API",
        "endpoints": {
            "/analyze_oil_spill": "Perform detailed oil spill environmental impact analysis",
            "/detect/": "Upload a single image for oil spill detection",
            "/batch-detect/": "Upload multiple images for oil spill detection"
        },
        "services": [
            "Environmental Impact Analysis",
            "Oil Spill Image Detection",
            "Batch Image Processing"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)