import os
import uvicorn
import hashlib
import cohere
import chromadb
from typing import Dict, Any

import math
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Existing imports from your original script
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chromadb.config import Settings
from rank_bm25 import BM25Okapi
from tqdm import tqdm  # Progress bar library

# Configuration
DOCS_DIR = "Oil_Spill_Docs"
CHROMA_DB_DIR = "data/chroma_db"
COHERE_API_KEY = "Cy87S7RvfuMl7OCv1iFQmg2MyJ3YK1CjVbMnS2UA"

class AISData(BaseModel):
    Latitude: float = Field(..., description="Latitude of the incident")
    Longitude: float = Field(..., description="Longitude of the incident")
    VesselName: str = Field(..., description="Name of the vessel")
    IMO: int = Field(..., description="International Maritime Organization number")
    MMSI: int = Field(..., description="Maritime Mobile Service Identity")
    AffectedArea: float = Field(..., description="Area affected by the oil spill")
    ECA: bool = Field(..., description="Environmental Control Area status")
    Zone: str = Field(..., description="Geographical zone of the incident")

class OilSpillAnalysisResult(BaseModel):
    query: str
    prediction: str
    coral_reef_damage: float
    cleanup_cost: float
    search_results: Dict[str, Any]

def estimate_coral_reef_damage(affected_area):
    """Estimate damage to coral reefs (in sq. km)."""
    coral_impact_ratio = 0.05
    return affected_area * coral_impact_ratio

def estimate_cleanup_cost(affected_area):
    """Estimate cleanup costs based on historical incidents (in USD)."""
    cost_per_sq_km = 20000
    return affected_area * cost_per_sq_km

def load_documents_from_subfolders(root_dir):
    """Load PDF documents from subfolders and associate them with topics."""
    documents = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                file_path = os.path.join(root, file)
                loader = PyPDFLoader(file_path)
                data = loader.load()
                topic = os.path.basename(root)
                for doc in data:
                    doc.metadata['topic'] = topic
                documents.extend(data)
    return documents

def split_documents(documents, chunk_size=700, chunk_overlap=50):
    """Split documents into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return text_splitter.split_documents(documents)

def generate_id(doc):
    """Generate a unique ID for a document based on its content."""
    hash_object = hashlib.md5(doc.page_content.encode('utf-8'))
    return hash_object.hexdigest()

def initialize_chroma_db(chroma_db_dir):
    """Initialize ChromaDB client with persistence."""
    chroma_client = chromadb.PersistentClient(path=chroma_db_dir)
    return chroma_client

def create_or_get_collection(chroma_client, collection_name="oil_spill_docs"):
    """Create or get a collection in ChromaDB."""
    return chroma_client.get_or_create_collection(name=collection_name)

def upsert_documents_with_progress(collection, texts):
    """Upsert documents into the collection with a progress bar."""
    documents = [doc.page_content for doc in texts]
    metadatas = [doc.metadata for doc in texts]
    ids = [generate_id(doc) for doc in texts]

    batch_size = 100
    total_docs = len(documents)
    for i in range(0, total_docs, batch_size):
        batch_docs = documents[i:i+batch_size]
        batch_metadatas = metadatas[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]
        collection.upsert(
            documents=batch_docs,
            metadatas=batch_metadatas,
            ids=batch_ids
        )

def get_all_documents(collection):
    """Retrieve all documents from the collection."""
    all_texts = collection.get()
    return [
        {"page_content": doc, "metadata": meta}
        for doc, meta in zip(all_texts["documents"], all_texts["metadatas"])
    ]

def bm25_search(query, corpus, k=5):
    """BM25 search for relevant documents."""
    corpus_tokenized = [doc['page_content'].split(" ") for doc in corpus]
    bm25 = BM25Okapi(corpus_tokenized)
    query_tokenized = query.split(" ")
    return bm25.get_top_n(query_tokenized, corpus, n=k)

def similarity_search(query, collection, k=5):
    """Similarity search using ChromaDB."""
    results = collection.query(query_texts=[query], n_results=k)
    return [
        {"page_content": doc, "metadata": meta}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]

def keyword_search(query, corpus, k=5):
    """Keyword search in the corpus."""
    results = [
        doc for doc in corpus
        if any(term in doc['page_content'] for term in query.split(" "))
    ]
    return results[:k]

def fuse_results(similarity_results, keyword_results, bm25_results):
    """Combine and deduplicate results from different search methods."""
    all_results = similarity_results + keyword_results + bm25_results
    seen = set()
    unique_results = []
    for result in all_results:
        metadata = result.get('metadata', {})
        unique_key = (metadata.get('source', ''), metadata.get('page', ''))
        if unique_key not in seen:
            unique_results.append(result)
            seen.add(unique_key)
    return unique_results

def generate_response(query, combined_results, cohere_api_key):
    """Generate response using Cohere API."""
    co = cohere.Client(cohere_api_key)
    if combined_results:
        context = "\n".join([doc['page_content'] for doc in combined_results])
        prompt = f"""Context:
{context}

Answer the following question based on the context. Also, add some previous history also dont make it sound so general be specific and stats from your knowledge and understanding apart from the context:
{query}
Answer:"""
    else:
        prompt = f'''You are a professional marine expert specializing in oil spill research.
Analyze the details about the oil spill location and affected area and show numeric format harm to marine life. 
Provide a detailed prediction of environmental impacts, emphasizing the specific information in the query. 
Support predictions with numeric data, historical records, and regional ecosystem knowledge.

User Query:
{query}

Answer:'''

    try:
        response = co.generate(
            model='command-xlarge',
            prompt=prompt,
            max_tokens=450,
            temperature=0.7
        )
        return response.generations[0].text.strip()
    except cohere.CohereError as e:
        print(f"Error generating response: {e.message}")
        return "Unable to generate response."

# Global variables to store ChromaDB client and collection
chroma_client = None
collection = None

def initialize_database():
    global chroma_client, collection
    # Initialize ChromaDB
    chroma_client = initialize_chroma_db(CHROMA_DB_DIR)
    collection = create_or_get_collection(chroma_client)

    # Check if collection is empty and populate if needed
    if collection.count() == 0:
        print("Collection is empty. Processing documents...")
        documents = load_documents_from_subfolders(DOCS_DIR)
        texts = split_documents(documents)
        upsert_documents_with_progress(collection, texts)
        print("Documents have been upserted into ChromaDB.")

# FastAPI Application
app = FastAPI(
    title="Oil Spill Analysis API",
    description="API for performing detailed oil spill environmental impact analysis"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize the database on application startup."""
    initialize_database()

@app.post("/analyze_oil_spill", response_model=OilSpillAnalysisResult)
async def analyze_oil_spill(ais_data: AISData):
    """Endpoint to analyze oil spill based on AIS data."""
    if not COHERE_API_KEY:
        raise HTTPException(status_code=500, detail="Cohere API key is not configured")

    # Prepare query
    query = """I have identified an oil spill in the Gulf of Mexico with the following details:
Location: Latitude {ais_data['Latitude']}, Longitude {ais_data['Longitude']}
Affected Area: {ais_data['Affected Area']} square kilometers
Estimated Coral Reef Damage: {coral_reef_damage} sq. km
Estimated Cleanup Cost: ${cleanup_cost:,.2f}
Environmental Control Area (ECA): {ais_data['ECA']}
Vessel Involved: {ais_data['Vessel Name']} (IMO: {ais_data['IMO']}, MMSI: {ais_data['MMSI']})
Proximity to Sensitive Zones: {ais_data['Zone']}
Please provide a prediction of specific environmental impacts, including the spill's effects on marine ecosystems, water quality, and nearby habitats. Support your analysis with numeric data or historical examples related to similar spills in the region."""

    # Estimate environmental metrics
    coral_reef_damage = estimate_coral_reef_damage(ais_data.AffectedArea)
    cleanup_cost = estimate_cleanup_cost(ais_data.AffectedArea)

    # Retrieve all documents
    all_docs = get_all_documents(collection)

    # Perform searches
    similarity_results = similarity_search(query, collection, k=5)
    keyword_results = keyword_search(query, all_docs, k=5)
    bm25_results = bm25_search(query, all_docs, k=5)

    # Fuse results
    combined_results = fuse_results(similarity_results, keyword_results, bm25_results)

    # Generate response
    prediction = generate_response(query, combined_results, COHERE_API_KEY)

    return OilSpillAnalysisResult(
        query=query,
        prediction=prediction,
        coral_reef_damage=coral_reef_damage,
        cleanup_cost=cleanup_cost,
        search_results={
            "similarity": [doc['page_content'] for doc in similarity_results],
            "keyword": [doc['page_content'] for doc in keyword_results],
            "bm25": [doc['page_content'] for doc in bm25_results]
        }
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)