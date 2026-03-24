import os 
from pathlib import Path 
from langchain_ollama import OllamaEmbeddings 
from langchain_chroma import Chroma 
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from loguru import logger 
from app.config import config 
  
# ── Embeddings (always local, always free) ──────────────────────── 
def get_embeddings(): 
    return OllamaEmbeddings( 
        model=config.EMBED_MODEL, 
        base_url=config.OLLAMA_BASE_URL 
    ) 
  
# ── Vector stores ───────────────────────────────────────────────── 
def get_knowledge_store(): 
    """Facility knowledge base — persistent, travels on flash drive.""" 
    return Chroma( 
        collection_name='facility_knowledge', 
        embedding_function=get_embeddings(), 
        persist_directory=config.CHROMA_DB_PATH 
    ) 
  
def get_event_store(): 
    """Event log — stores scan results, sensor anomalies, incidents.""" 
    return Chroma( 
        collection_name='event_log', 
        embedding_function=get_embeddings(), 
        persist_directory=config.CHROMA_DB_PATH 
    ) 
  
# ── Ingestion ───────────────────────────────────────────────────── 
def ingest_documents(folder_path: str = None): 
    """ 
    Ingest all .txt and .md files from the knowledge folder into ChromaDB. 
    Run this once after adding new documents to knowledge/documents/. 
    """ 
    folder = Path(folder_path or config.KNOWLEDGE_PATH) 
    store = get_knowledge_store() 
    splitter = RecursiveCharacterTextSplitter( 
        chunk_size=1000, chunk_overlap=200 
    ) 
    total_chunks = 0 
    for file in folder.glob('**/*.txt') : 
        text = file.read_text(encoding='utf-8', errors='ignore') 
        chunks = splitter.split_text(text) 
        store.add_texts( 
            texts=chunks, 
            metadatas=[{'source': file.name, 'type': 'facility_doc'}] * 
len(chunks) 
        ) 
        total_chunks += len(chunks) 
        logger.info(f'Ingested {file.name}: {len(chunks)} chunks') 
    logger.success(f'RAG ingestion complete: {total_chunks} total chunks') 
    return total_chunks 
  
# ── Retrieval tool (used by LangChain agent) ────────────────────── 
def query_knowledge(question: str, k: int = 4) -> str: 
    """ 
    Query the facility knowledge base. 
    Returns formatted string of relevant passages. 
    Used as a LangChain tool. 
    """ 
    store = get_knowledge_store() 
    docs = store.similarity_search(question, k=k) 
    if not docs: 
        return 'No relevant information found in facility knowledge base.' 
    results = [] 
    for i, doc in enumerate(docs): 
        source = doc.metadata.get('source', 'unknown') 
        results.append(f'[Record {i+1} — Source: {source}]\n{doc.page_content}') 
    return '\n\n'.join(results) 
