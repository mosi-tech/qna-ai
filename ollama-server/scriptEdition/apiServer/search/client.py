#!/usr/bin/env python3
"""
Analysis Library Client - Direct Python access (no MCP needed)
Use this for apiServer integration to save analyses after completion
"""

import os
from .library import AnalysisLibrary

class AnalysisLibraryClient:
    """Simple client for direct ChromaDB access without MCP"""
    
    def __init__(self, chroma_host: str = None, chroma_port: int = None):
        """Initialize the analysis library client"""
        self.library = AnalysisLibrary(chroma_host, chroma_port)
    
    def save_analysis(self, question: str, function_name: str, docstring: str, filename: str = None) -> dict:
        """Save a completed analysis to the library"""
        return self.library.save_analysis(question, function_name, docstring, filename)
    
    def search_similar(self, query: str, top_k: int = 5, similarity_threshold: float = 0.3) -> dict:
        """Search for similar analyses"""
        return self.library.search_similar(query, top_k, similarity_threshold)

# Global instance for easy import
analysis_client = AnalysisLibraryClient()

# Convenience functions for direct import
def save_analysis(question: str, function_name: str, docstring: str, filename: str = None) -> dict:
    """Save analysis - convenience function"""
    return analysis_client.save_analysis(question, function_name, docstring, filename)

def search_similar_analyses(query: str, top_k: int = 5, similarity_threshold: float = 0.3) -> dict:
    """Search similar analyses - convenience function"""
    return analysis_client.search_similar(query, top_k, similarity_threshold)

if __name__ == "__main__":
    # Test the direct access
    print("Testing direct analysis library access...")
    
    # Test save
    result = save_analysis(
        question="What happens if I buy AAPL every time it drops 2%?",
        function_name="analyze_aapl_dip_buying_strategy",
        docstring="Analyzes the performance of buying AAPL stock whenever it drops 2% from recent highs."
    )
    print(f"Save result: {result}")
    
    # Test search
    search_result = search_similar_analyses("AAPL dip buying strategy")
    print(f"Search result: {search_result}")