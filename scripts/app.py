# app.py

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

# Import chatbot functionalities
from chatbot import (
    similarity_search,
    keyword_search,
    bm25_search,
    fuse_results,
    generate_response,
    get_all_documents,
    initialize_chroma_db,
    create_or_get_collection,
    COHERE_API_KEY
)
import chatbot
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the databases on application startup."""
    global chroma_client, collection, all_docs
    
    # Initialize oil spill analysis database
    chroma_client, collection = initialize_database()
    
    # Initialize chatbot database
    chatbot_chroma_client = initialize_chroma_db("data/chroma_db")
    chatbot_collection = create_or_get_collection(chatbot_chroma_client)
    
    if chatbot_collection.count() == 0:
        print("Chatbot collection is empty. Processing documents for the first time...")
        documents = chatbot.load_documents_from_subfolders("Oil_Spill_Docs")
        print(f"Loaded {len(documents)} documents.")
        texts = chatbot.split_documents(documents)
        print(f"Split into {len(texts)} chunks.")
        chatbot.upsert_documents_with_progress(chatbot_collection, texts)
        print("Documents have been upserted into ChromaDB.")
    else:
        print("Chatbot documents are already upserted. Skipping to query execution.")
    
    all_docs = get_all_documents(chatbot_collection)
    print(f"Total chatbot documents retrieved from ChromaDB: {len(all_docs)}")
    
    yield

app = FastAPI(
    title="Comprehensive Oil Spill Management API",
    description="API for oil spill analysis, detection, environmental impact assessment, and chatbot queries",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for databases
chroma_client = None
collection = None
all_docs = []
print(f"Total chatbot documents retrieved from ChromaDB: {len(all_docs)}")

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
async def batch_detect_oil_spills_endpoint(files: List[UploadFile] = File(...)):
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

# Chatbot Query Endpoint
class QueryRequest(BaseModel):
    query: str

@app.post("/query")
def handle_query(request: QueryRequest):
    query = request.query
    similarity_results = similarity_search(query, collection, k=5)
    keyword_results = keyword_search(query, all_docs, k=5)
    bm25_results = bm25_search(query, all_docs, k=5) if all_docs else []
    
    if not all_docs:
        raise HTTPException(status_code=400, detail="No documents available for search.")
    
    combined_results = fuse_results(similarity_results, keyword_results, bm25_results)
    response = generate_response(query, combined_results, COHERE_API_KEY)
    return {"response": response}

# Root endpoint with API information
@app.get("/")
async def root():
    return {
        "message": "Comprehensive Oil Spill Management API",
        "endpoints": {
            "/analyze_oil_spill": "Perform detailed oil spill environmental impact analysis",
            "/detect/": "Upload a single image for oil spill detection",
            "/batch-detect/": "Upload multiple images for oil spill detection",
            "/query": "Ask questions related to oil spill data and analysis"
        },
        "services": [
            "Environmental Impact Analysis",
            "Oil Spill Image Detection",
            "Batch Image Processing",
            "Chatbot Query Handling"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)