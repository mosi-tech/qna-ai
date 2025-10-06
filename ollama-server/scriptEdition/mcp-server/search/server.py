#!/usr/bin/env python3
"""
ChromaDB Analysis Library MCP Server
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
import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("analysis-search-server")

@dataclass
class AnalysisData:
    id: str
    question: str
    function_name: str
    docstring: str
    created_date: str
    usage_count: int

class AnalysisLibraryMCP:
    def __init__(self, db_path: str = None):
        # Use environment variable or default path
        if db_path is None:
            db_path = os.getenv("ANALYSIS_DB_PATH", "./data/analysis_library_db")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create single collection for questions and analysis data
        self.collection = self.client.get_or_create_collection(
            name="financial_analyses",
            metadata={"description": "Financial analysis questions with descriptions"}
        )
        
        logger.info(f"✅ ChromaDB Analysis Library MCP Server initialized at {db_path}")
    
    def _generate_analysis_id(self, question: str) -> str:
        """Generate unique ID for analysis"""
        combined = f"{question}_{datetime.now().isoformat()}"
        return hashlib.md5(combined.encode()).hexdigest()[:12]
    
    def save_analysis_direct(self, question: str, function_name: str, docstring: str) -> dict:
        """Direct Python method to save analysis (non-MCP)"""
        try:
            # Generate analysis data
            analysis_id = self._generate_analysis_id(question)
            now = datetime.now().isoformat()
            
            analysis_data = AnalysisData(
                id=analysis_id,
                question=question,
                function_name=function_name,
                docstring=docstring,
                created_date=now,
                usage_count=0
            )
            
            analysis_dict = asdict(analysis_data)
            
            # Combine fields into one text for better embedding search
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
    
    def search_similar_direct(self, query: str, top_k: int = 5, similarity_threshold: float = 0.6) -> dict:
        """Direct Python method to search similar analyses (non-MCP)"""
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
                "total_found": len(similar_analyses),
                "search_query": query,
                "analyses": similar_analyses
            }
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Initialize MCP Server
server = Server("analysis-search-server")
analysis_library = AnalysisLibraryMCP()

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="save_analysis",
            description="Save a new financial analysis question with function name and description",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The original user question that prompted this analysis"
                    },
                    "function_name": {
                        "type": "string", 
                        "description": "The name of the analysis function created"
                    },
                    "docstring": {
                        "type": "string",
                        "description": "Description explaining what the analysis does"
                    }
                },
                "required": ["question", "function_name", "docstring"]
            }
        ),
        
        types.Tool(
            name="search_similar_analyses",
            description="Search for analyses similar to a given question using vector similarity",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question to search for similar analyses"
                    },
                    "top_k": {
                        "type": "integer",
                        "default": 5,
                        "description": "Number of top similar analyses to return"
                    },
                    "similarity_threshold": {
                        "type": "number",
                        "default": 0.6,
                        "description": "Minimum similarity score (0.0-1.0) to include in results"
                    }
                },
                "required": ["query"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    
    if name == "save_analysis":
        question = arguments["question"]
        function_name = arguments["function_name"]
        docstring = arguments["docstring"]
        
        # Generate analysis data
        analysis_id = analysis_library._generate_analysis_id(question)
        now = datetime.now().isoformat()
        
        analysis_data = AnalysisData(
            id=analysis_id,
            question=question,
            function_name=function_name,
            docstring=docstring,
            created_date=now,
            usage_count=0
        )
        
        # Save to ChromaDB
        try:
            analysis_dict = asdict(analysis_data)
            
            # Combine fields into one text for better embedding search
            combined_text = f"Question: {question}\nDescription: {docstring}\nFunction: {function_name}"
            
            analysis_library.collection.add(
                documents=[combined_text],  # Use combined text for vector search
                metadatas=[analysis_dict],
                ids=[analysis_id]
            )
            
            logger.info(f"✅ Saved analysis {analysis_id} for question: {question[:50]}...")
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "analysis_id": analysis_id,
                    "function_name": function_name,
                    "message": f"Analysis saved successfully with ID: {analysis_id}"
                }, indent=2)
            )]
            
        except Exception as e:
            logger.error(f"❌ Failed to save analysis: {e}")
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": str(e)
                }, indent=2)
            )]
    
    elif name == "search_similar_analyses":
        query = arguments["query"]
        top_k = arguments.get("top_k", 5)
        similarity_threshold = arguments.get("similarity_threshold", 0.6)
        
        try:
            # Search using ChromaDB vector similarity
            results = analysis_library.collection.query(
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
                        'question': analysis_meta['question'],  # Use original question from metadata
                        'similarity': round(similarity, 3),
                        'function_name': analysis_meta['function_name'],
                        'docstring': analysis_meta['docstring'],
                        'created_date': analysis_meta['created_date'],
                        'usage_count': analysis_meta['usage_count'],
                        'matched_text': results['documents'][0][i]  # Show what text was matched
                    })
            
            # Sort by similarity and limit to top_k
            similar_analyses.sort(key=lambda x: x['similarity'], reverse=True)
            similar_analyses = similar_analyses[:top_k]
            
            logger.info(f"🔍 Found {len(similar_analyses)} similar analyses for: {query[:50]}...")
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "found_similar": len(similar_analyses) > 0,
                    "total_found": len(similar_analyses),
                    "search_query": query,
                    "analyses": similar_analyses
                }, indent=2)
            )]
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": str(e)
                }, indent=2)
            )]
    
    else:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"Unknown tool: {name}"
            }, indent=2)
        )]

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="analysis-search-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())