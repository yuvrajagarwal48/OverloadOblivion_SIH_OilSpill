import math
import os
import hashlib
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from chromadb.config import Settings
from rank_bm25 import BM25Okapi
import cohere
from tqdm import tqdm
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

DOCS_DIR = "Oil_Spill_Docs"
CHROMA_DB_DIR = "data/chroma_db"
COHERE_API_KEY = "1LSMe22IMWWCFaM9OtH1nxHomNOStGgRTKFdJDQX"
if not COHERE_API_KEY:
    raise ValueError("Please set the COHERE_API_KEY environment variable.")

app = FastAPI()

def load_documents_from_subfolders(root_dir):
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
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    texts = text_splitter.split_documents(documents)
    return texts

def generate_id(doc):
    hash_object = hashlib.md5(doc.page_content.encode('utf-8'))
    return hash_object.hexdigest()

def initialize_chroma_db(chroma_db_dir):
    chroma_client = chromadb.PersistentClient(path=chroma_db_dir)
    return chroma_client

def create_or_get_collection(chroma_client, collection_name="oil_spill_docs"):
    collection = chroma_client.get_or_create_collection(name=collection_name)
    return collection

def check_collection_empty(collection):
    return collection.count() == 0

def upsert_documents_with_progress(collection, texts):
    documents = []
    metadatas = []
    ids = []
    for doc in texts:
        doc_id = generate_id(doc)
        documents.append(doc.page_content)
        metadatas.append(doc.metadata)
        ids.append(doc_id)
    total_docs = len(documents)
    print(f"Upserting {total_docs} documents into the collection.")
    batch_size = 100
    for i in tqdm(range(0, total_docs, batch_size), desc="Upserting Documents"):
        batch_docs = documents[i:i+batch_size]
        batch_metadatas = metadatas[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]
        collection.upsert(
            documents=batch_docs,
            metadatas=batch_metadatas,
            ids=batch_ids
        )

def get_all_documents(collection):
    all_texts = collection.get()
    if not all_texts["documents"]:
        print("No documents found in the collection.")
        return []
    all_docs = [
        {"page_content": doc, "metadata": meta}
        for doc, meta in zip(all_texts["documents"], all_texts["metadatas"])
    ]
    print(f"Retrieved {len(all_docs)} documents from ChromaDB.")
    return all_docs

def bm25_search(query, corpus, k=5):
    corpus_tokenized = [doc['page_content'].split(" ") for doc in corpus]
    bm25 = BM25Okapi(corpus_tokenized)
    query_tokenized = query.split(" ")
    bm25_results = bm25.get_top_n(query_tokenized, corpus, n=k)
    return bm25_results

def similarity_search(query, collection, k=5):
    results = collection.query(
        query_texts=[query],
        n_results=k
    )
    docs = [
        {"page_content": doc, "metadata": meta}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]
    return docs

def keyword_search(query, corpus, k=5):
    results = []
    query_terms = query.split(" ")
    for doc in corpus:
        if any(term in doc['page_content'] for term in query_terms):
            results.append(doc)
    return results[:k]

def fuse_results(similarity_results, keyword_results, bm25_results):
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
    co = cohere.Client(cohere_api_key)
    if combined_results:
        context = "\n".join([doc['page_content'] for doc in combined_results])
        prompt = f"""Context:
{context}

Answer the following question based on the context. Also, add some previous history also dont make it sound so general be specific and stats from your knowledge and understanding apart from the context:
{query}
Answer:"""
    else:
        print("No relevant documents found. Generating answer based on general knowledge.")
        prompt = f'''You are a professional marine expert specializing in oil spill research.
Analyze the following details provided in the user's query about the oil spill and provided related information

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
        return "I'm sorry, I was unable to generate a response."

class QueryRequest(BaseModel):
    query: str

chroma_client = initialize_chroma_db(CHROMA_DB_DIR)
collection = create_or_get_collection(chroma_client)
if check_collection_empty(collection):
    print("Collection is empty. Processing documents for the first time...")
    documents = load_documents_from_subfolders(DOCS_DIR)
    print(f"Loaded {len(documents)} documents.")
    texts = split_documents(documents)
    print(f"Split into {len(texts)} chunks.")
    upsert_documents_with_progress(collection, texts)
    print("Documents have been upserted into ChromaDB.")
else:
    print("Documents are already upserted. Skipping to query execution.")

all_docs = get_all_documents(collection)
print(f"Total documents retrieved from ChromaDB: {len(all_docs)}")

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
