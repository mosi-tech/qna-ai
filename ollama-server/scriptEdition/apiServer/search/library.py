#!/usr/bin/env python3
"""
ChromaDB Analysis Library - Pure Python Implementation
Simple storage and search for financial analysis questions and descriptions
"""

import json
import hashlib
import logging
import os
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass, asdict

import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("analysis-library")

@dataclass
class AnalysisData:
    id: str
    question: str
    function_name: str
    docstring: str
    filename: str
    created_date: str
    usage_count: int

class AnalysisLibrary:
    """Pure Python Analysis Library using ChromaDB for vector search"""
    
    def __init__(self, chroma_host: str = None, chroma_port: int = None):
        # Use environment variables or defaults for ChromaDB HTTP client
        if chroma_host is None:
            chroma_host = os.getenv("CHROMA_HOST", "localhost")
        if chroma_port is None:
            chroma_port = int(os.getenv("CHROMA_PORT", "8000"))
        
        # Initialize ChromaDB with HTTP client
        try:
            self.client = chromadb.HttpClient(
                host=chroma_host,
                port=chroma_port,
                settings=Settings(anonymized_telemetry=False)
            )
            logger.info(f"✅ Connected to ChromaDB at {chroma_host}:{chroma_port}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to ChromaDB at {chroma_host}:{chroma_port}: {e}")
            logger.info("💡 Make sure ChromaDB server is running: docker run -p 8000:8000 chromadb/chroma")
            raise
        
        # Setup Ollama embedding function for better similarity
        self.embedding_function = None
        try:
            # Check if Ollama is available
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            embedding_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "qwen3-embedding")
            
            self.embedding_function = OllamaEmbeddingFunction(
                url=ollama_url,
                model_name=embedding_model,
            )
            logger.info(f"✅ Using Ollama embeddings: {embedding_model} at {ollama_url}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to setup Ollama embeddings: {e}")
            logger.info("💡 Falling back to default ChromaDB embeddings")
            self.embedding_function = None
        
        # Create single collection for questions and analysis data
        collection_name = "financial_analyses"
        
        # Handle embedding function conflicts
        try:
            # Try to get existing collection first
            self.collection = self.client.get_collection(collection_name)
            logger.info(f"✅ Using existing collection: {collection_name}")
            
            # Check if we need to migrate to Ollama embeddings
            if self.embedding_function:
                logger.info("🔄 Existing collection found with different embeddings - using as-is")
                logger.info("💡 To use Ollama embeddings, delete collection first or use different name")
        
        except Exception:
            # Collection doesn't exist, create new one
            collection_kwargs = {
                "name": collection_name,
                "metadata": {"description": "Financial analysis questions with descriptions"}
            }
            
            # Add embedding function if available
            if self.embedding_function:
                collection_kwargs["embedding_function"] = self.embedding_function
                logger.info(f"🔧 Creating new collection with Ollama embeddings")
            else:
                logger.info(f"🔧 Creating new collection with default embeddings")
                
            self.collection = self.client.create_collection(**collection_kwargs)
        
        logger.info(f"✅ ChromaDB Analysis Library initialized with HTTP client")
    
    def migrate_to_ollama_embeddings(self) -> dict:
        """Migrate existing collection to use Ollama embeddings"""
        if not self.embedding_function:
            return {"success": False, "error": "Ollama embeddings not available"}
        
        try:
            collection_name = "financial_analyses"
            
            # Get all existing data
            existing_data = self.collection.get(include=["documents", "metadatas"])
            
            if not existing_data['ids']:
                return {"success": True, "message": "No data to migrate"}
            
            # Delete old collection
            self.client.delete_collection(collection_name)
            logger.info(f"🗑️ Deleted existing collection")
            
            # Create new collection with Ollama embeddings
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
                metadata={"description": "Financial analysis questions with Ollama embeddings"}
            )
            logger.info(f"🔧 Created new collection with Ollama embeddings")
            
            # Re-add all data (will use new embeddings)
            self.collection.add(
                documents=existing_data['documents'],
                metadatas=existing_data['metadatas'],
                ids=existing_data['ids']
            )
            
            logger.info(f"✅ Migrated {len(existing_data['ids'])} documents to Ollama embeddings")
            return {
                "success": True, 
                "migrated_count": len(existing_data['ids']),
                "message": "Successfully migrated to Ollama embeddings"
            }
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_analysis_id(self, question: str) -> str:
        """Generate unique ID for analysis"""
        combined = f"{question}_{datetime.now().isoformat()}"
        return hashlib.md5(combined.encode()).hexdigest()[:12]
    
    def save_analysis(self, question: str, function_name: str, docstring: str, filename: str = None) -> dict:
        """Save analysis to the library"""
        try:
            # Generate analysis data
            analysis_id = self._generate_analysis_id(question)
            now = datetime.now().isoformat()
            
            # Generate filename if not provided
            if filename is None:
                filename = f"{function_name}.py"
            
            analysis_data = AnalysisData(
                id=analysis_id,
                question=question,
                function_name=function_name,
                docstring=docstring,
                filename=filename,
                created_date=now,
                usage_count=0
            )
            
            analysis_dict = asdict(analysis_data)
            
            # Focus on question similarity for now - simple and effective
            combined_text = f"Question: {question}\nDescription: {docstring}\nFunction: {function_name}"
            
            self.collection.add(
                documents=[combined_text],
                metadatas=[analysis_dict],
                ids=[analysis_id]
            )
            
            logger.info(f"✅ Saved analysis {analysis_id} for question: {question[:50]}...")
            
            return {
                "success": True,
                "analysis_id": analysis_id,
                "function_name": function_name,
                "message": f"Analysis saved successfully with ID: {analysis_id}"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to save analysis: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_similar(self, query: str, top_k: int = 5, similarity_threshold: float = 0.3) -> dict:
        """Search for similar analyses"""
        try:
            # Search using ChromaDB vector similarity
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k * 2,  # Get more to filter by threshold
                include=["documents", "metadatas", "distances"]
            )
            
            similar_analyses = []
            for i in range(len(results['ids'][0])):
                similarity = 1 - results['distances'][0][i]  # Convert distance to similarity
                
                if similarity >= similarity_threshold:
                    analysis_meta = results['metadatas'][0][i]
                    
                    similar_analyses.append({
                        'analysis_id': analysis_meta['id'],
                        'question': analysis_meta['question'],
                        'similarity': round(similarity, 3),
                        'function_name': analysis_meta['function_name'],
                        'docstring': analysis_meta['docstring'],
                        'filename': analysis_meta.get('filename', f"{analysis_meta['function_name']}.py"),
                        'created_date': analysis_meta['created_date'],
                        'usage_count': analysis_meta['usage_count'],
                        'matched_text': results['documents'][0][i]
                    })
            
            # Sort by similarity and limit to top_k
            similar_analyses.sort(key=lambda x: x['similarity'], reverse=True)
            similar_analyses = similar_analyses[:top_k]
            
            logger.info(f"🔍 Found {len(similar_analyses)} similar analyses for: {query[:50]}...")
            
            return {
                "success": True,
                "found_similar": len(similar_analyses) > 0,
                "analyses": similar_analyses,
                "query": query,
                "threshold": similarity_threshold
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to search analyses: {e}")
            return {
                "success": False,
                "error": str(e),
                "found_similar": False,
                "analyses": []
            }
    
    def get_stats(self) -> dict:
        """Get library statistics"""
        try:
            count = self.collection.count()
            return {
                "success": True,
                "total_analyses": count,
                "status": "operational"
            }
        except Exception as e:
            logger.error(f"❌ Failed to get stats: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_analyses(self, limit: int = 10) -> dict:
        """List recent analyses"""
        try:
            results = self.collection.get(
                limit=limit,
                include=["metadatas"]
            )
            
            analyses = []
            for metadata in results['metadatas']:
                analyses.append({
                    'analysis_id': metadata['id'],
                    'question': metadata['question'],
                    'function_name': metadata['function_name'],
                    'filename': metadata.get('filename', f"{metadata['function_name']}.py"),
                    'created_date': metadata['created_date']
                })
            
            return {
                "success": True,
                "analyses": analyses,
                "count": len(analyses)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to list analyses: {e}")
            return {
                "success": False,
                "error": str(e),
                "analyses": []
            }

# Backward compatibility - alias for old name
AnalysisLibraryMCP = AnalysisLibrary