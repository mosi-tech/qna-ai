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

import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("analysis-library")


class AnalysisLibrary:
    """Pure Python Analysis Library using ChromaDB for vector search"""
    
    def __init__(self, chroma_host: str = None, chroma_port: int = None):
        # Use environment variables or defaults for ChromaDB HTTP client
        if chroma_host is None:
            chroma_host = os.getenv("CHROMA_HOST", "localhost")
        if chroma_port is None:
            chroma_port = int(os.getenv("CHROMA_PORT", "8050"))
        
        # Initialize ChromaDB with HTTP client
        try:
            self.client = chromadb.HttpClient(
                host=chroma_host,
                port=chroma_port,
                settings=Settings(anonymized_telemetry=False)
            )
            # Test the connection with a heartbeat
            heartbeat = self.client.heartbeat()
            logger.info(f"✅ Connected to ChromaDB at {chroma_host}:{chroma_port} (heartbeat: {heartbeat})")
        except Exception as e:
            logger.error(f"❌ Failed to connect to ChromaDB at {chroma_host}:{chroma_port}")
            logger.error(f"   Error: {type(e).__name__}: {e}")
            logger.info(f"💡 Make sure ChromaDB server is running:")
            logger.info(f"   docker run -d -p 8050:8050 chromadb/chroma")
            logger.info(f"   Or check if port {chroma_port} is already in use")
            raise ConnectionError(f"Cannot connect to ChromaDB at {chroma_host}:{chroma_port}") from e
        
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

    def _flatten_metadata(self, metadata: dict, parent_key: str = '', sep: str = '__') -> dict:
        """
        Flatten nested metadata dict for ChromaDB compatibility.
        ChromaDB only supports simple types (str, int, float, bool) in metadata.

        Example:
            {"workflow": {"step1": "fetch", "step2": "compute"}}
        Becomes:
            {"workflow__step1": "fetch", "workflow__step2": "compute"}
        """
        flat_dict = {}

        for key, value in metadata.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key

            if isinstance(value, dict):
                # Recursively flatten nested dicts
                flat_dict.update(self._flatten_metadata(value, new_key, sep=sep))
            elif isinstance(value, (list, tuple)):
                # Convert lists to JSON string
                flat_dict[new_key] = json.dumps(value)
            elif isinstance(value, (str, int, float, bool)):
                # Keep simple types as-is
                flat_dict[new_key] = value
            elif value is None:
                # Convert None to string
                flat_dict[new_key] = "null"
            else:
                # Convert other types to JSON string
                flat_dict[new_key] = json.dumps(value)

        return flat_dict

    def _unflatten_metadata(self, flat_dict: dict, sep: str = '__') -> dict:
        """
        Unflatten a flat dictionary back to nested structure.
        Reverses the flattening done by _flatten_metadata.

        Example:
            {"workflow__step1": "fetch", "workflow__step2": "compute"}
        Becomes:
            {"workflow": {"step1": "fetch", "step2": "compute"}}
        """
        nested_dict = {}

        for flat_key, value in flat_dict.items():
            # Split the key by separator
            keys = flat_key.split(sep)

            # Navigate/create nested structure
            current = nested_dict
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]

            # Set the final value
            final_key = keys[-1]

            # Try to parse JSON strings back to lists/objects
            if isinstance(value, str):
                # Check if it looks like JSON
                if (value.startswith('[') and value.endswith(']')) or \
                   (value.startswith('{') and value.endswith('}')):
                    try:
                        current[final_key] = json.loads(value)
                    except json.JSONDecodeError:
                        # Not valid JSON, keep as string
                        current[final_key] = value
                elif value == "null":
                    current[final_key] = None
                else:
                    current[final_key] = value
            else:
                current[final_key] = value

        return nested_dict
    
    def save_analysis(self,  analysis_id: str, question: str, metadata: dict = None) -> dict:
        """Save analysis to the library"""
        try:
            now = datetime.now().isoformat()
            if metadata is None:
                metadata = {}

            # Build analysis dict directly (no need for AnalysisData class)
            analysis_dict = {
                "id": analysis_id,
                "question": question,
                "created_date": now,
                "usage_count": 0
            }

            # Flatten the nested metadata dict for ChromaDB compatibility
            # ChromaDB only supports simple types (str, int, float, bool) in metadata
            if metadata:
                flattened_metadata = self._flatten_metadata(metadata)    
                # Add flattened metadata with 'meta_' prefix to avoid conflicts
                for key, value in flattened_metadata.items():
                    analysis_dict[key] = value
            
            document = f"Question: {question}\nDescription: {analysis_dict["description"]}"
            self.collection.add(
                documents=[document],
                metadatas=[analysis_dict],
                ids=[analysis_id]
            )

            logger.info(f"✅ Saved analysis {analysis_id} for question: {question[:50]}...")

            return {
                "success": True,
                "analysis_id": analysis_id,
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
                    analysis_meta = results['metadatas'][0][i].copy()

                    # Unflatten the metadata to restore nested structure
                    unflattened = self._unflatten_metadata(analysis_meta)

                    # Add similarity score
                    unflattened["similarity"] = similarity

                    similar_analyses.append(unflattened)

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

# Module-level library instance (created lazily)
_analysis_library = None
def get_analysis_library(chroma_host: str = None, chroma_port: int = None) -> AnalysisLibrary:
    """Get or create analysis library instance"""
    global _analysis_library
    if _analysis_library is None:
        _analysis_library = AnalysisLibrary(chroma_host, chroma_port)
    return _analysis_library

# Convenience functions for direct import
def save_analysis(question: str, analysis_id: str, metadata: Dict) -> dict:
    """Save analysis - convenience function"""
    library = get_analysis_library()
    return library.save_analysis(question, analysis_id, metadata)

def search_similar_analyses(query: str, top_k: int = 5, similarity_threshold: float = 0.3) -> dict:
    """Search similar analyses - convenience function"""
    library = get_analysis_library()
    return library.search_similar(query, top_k, similarity_threshold)

if __name__ == "__main__":
    # Test the library
    print("Testing AnalysisLibrary...")
    
    # Test direct usage
    library = AnalysisLibrary()
    result = library.save_analysis(
        question="What's the best momentum strategy for AAPL?",
        function_name="analyze_aapl_momentum_strategy",
        docstring="Analyzes various momentum indicators for AAPL trading strategy optimization."
    )
    print(f"Direct save result: {result}")
    
    search_result = library.search_similar("AAPL momentum", top_k=3)
    print(f"Direct search result: {search_result}")
    
    # Test convenience functions
    print("\nTesting convenience functions...")
    result2 = save_analysis(
        question="What happens if I buy AAPL every time it drops 2%?",
        function_name="analyze_aapl_dip_buying_strategy",
        docstring="Analyzes the performance of buying AAPL stock whenever it drops 2% from recent highs."
    )
    print(f"Convenience save result: {result2}")
    
    search_result2 = search_similar_analyses("AAPL dip buying strategy")
    print(f"Convenience search result: {search_result2}")
    
    stats = get_analysis_library().get_stats()
    print(f"Library stats: {stats}")
