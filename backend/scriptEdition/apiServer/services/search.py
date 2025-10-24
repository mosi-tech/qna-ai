#!/usr/bin/env python3
"""
Search Service - Handles analysis library search and enhancement

Note: This is different from services/analysis.py which handles LLM-based analysis.
This service focuses on ChromaDB search, message enhancement, and analysis saving.
"""

import os
import sys
import re
import logging
from search.library import get_analysis_library

logger = logging.getLogger("search-service")

class SearchService:
    """Service for managing analysis library search and enhancement"""
    
    def __init__(self):
        """Initialize the search service"""
        try:
            # Use lazy initialization via get_analysis_library()
            self.library_client = None  # Will be created lazily when needed
            logger.info("✅ Search service initialized (lazy mode)")
        except Exception as e:
            logger.error(f"❌ Failed to initialize search service: {e}")
            self.library_client = None
    
    def _get_library_client(self):
        """Get library instance, creating lazily if needed"""
        if self.library_client is None:
            try:
                self.library_client = get_analysis_library()
                logger.info("✅ Analysis library initialized on first use")
            except Exception as e:
                logger.error(f"❌ Failed to create analysis library: {e}")
                return None
        return self.library_client
    
    def search_and_enhance_message(self, user_question: str) -> tuple[str, list]:
        """Search for similar analyses and enhance user message with context"""
        library_client = self._get_library_client()
        if not library_client:
            return user_question, []
        
        try:
            # Search for similar analyses
            search_result = library_client.search_similar(
                query=user_question,
                top_k=3,
                similarity_threshold=0.3  # Lower threshold to find more potential matches
            )
            
            if not search_result.get("success") or not search_result.get("found_similar"):
                logger.info("🔍 No similar analyses found")
                return user_question, []
            
            similar_analyses = search_result["analyses"]
            logger.info(f"🔍 Found {len(similar_analyses)} similar analyses")
            
            # Build enhanced context with question first
            context_lines = [
                "🎯 ORIGINAL QUESTION:",
                user_question,
                "",
                "📋 RELEVANT EXISTING ANALYSES:",
                "The following similar analyses exist in your library:"
            ]
            
            for i, analysis in enumerate(similar_analyses, 1):
                similarity_pct = int(analysis['similarity'] * 100)
                filename = analysis.get('filename', f"{analysis['function_name']}.py")
                context_lines.extend([
                    f"",
                    f"{i}. {analysis['function_name']} (similarity: {similarity_pct}%)",
                    f"   File: {filename}",
                    f"   Question: {analysis['question']}",
                    f"   Description: {analysis['docstring'][:200]}{'...' if len(analysis['docstring']) > 200 else ''}"
                ])
            
            context_lines.extend([
                "",
                "💡 INSTRUCTION: Consider these existing analyses when creating your solution.",
                "If the question is very similar to an existing analysis, you may:",
                "- Reference the existing approach and extend it",
                "- Use similar parameter structure", 
                "- Build upon the existing methodology",
                "- Create a variation that addresses the specific differences"
            ])
            
            enhanced_message = "\n".join(context_lines)
            
            return enhanced_message, similar_analyses
            
        except Exception as e:
            logger.error(f"❌ Error searching similar analyses: {e}")
            return user_question, []
    
    def extract_function_name_from_script(self, script_content: str) -> str:
        """Extract main function name from generated script"""
        try:
            # Look for function definitions, prioritize ones with 'analyze' in name
            matches = re.findall(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', script_content)
            
            for match in matches:
                if 'analyze' in match.lower():
                    return match
            
            # Return first function found or default
            return matches[0] if matches else "unknown_function"
            
        except Exception as e:
            logger.error(f"❌ Error extracting function name: {e}")
            return "unknown_function"
    
    def extract_docstring_from_content(self, script_content: str) -> str:
        """Extract or generate docstring from LLM content or script"""
        try:
            # First try to extract docstring from script
            docstring_match = re.search(r'"""(.*?)"""', script_content, re.DOTALL)
            if docstring_match:
                docstring = docstring_match.group(1).strip()
                if len(docstring) > 50:  # Good docstring found
                    return docstring
            
        except Exception as e:
            logger.error(f"❌ Error extracting docstring: {e}")
            return "Financial analysis function"
    
    def extract_filename_from_tool_calls(self, tool_calls: list) -> str:
        """Extract filename from write_file tool calls"""
        try:
            for tool_call in tool_calls:
                func_name = tool_call.get("function", {}).get("name", "")
                if "write_file" in func_name:
                    args = tool_call.get("function", {}).get("arguments", {})
                    filename = args.get("filename", "")
                    if filename:
                        # Extract just the filename, not the full path
                        return os.path.basename(filename)
            return None
        except Exception as e:
            logger.error(f"❌ Error extracting filename: {e}")
            return None
    
    def save_completed_analysis(self, original_question: str, script_path: str, addn_meta: dict = None) -> dict:
        """Save analysis after successful completion"""
        library_client = self._get_library_client()
        if not library_client:
            return {"success": False, "error": "Analysis library not available"}
        
        try:
            script_content = ""
            # if script_path:
            #     try:
            #         # Get absolute path to MCP scripts directory from environment
            #         scripts_dir = os.getenv("MCP_SCRIPTS_DIR", "/Users/shivc/Documents/Workspace/JS/qna-ai-admin/mcp-server/scripts")
                    
            #         # If script_path is already absolute, use it; otherwise join with scripts_dir
            #         if os.path.isabs(script_path):
            #             full_script_path = script_path
            #         else:
            #             full_script_path = os.path.join(scripts_dir, script_path)
                    
            #         with open(full_script_path, 'r') as f:
            #             script_content = f.read()
            #         logger.info(f"📄 Read script content from: {full_script_path}")
            #     except Exception as e:
            #         logger.error(f"❌ Failed to read script file {script_path}: {e}")
            #         # Fallback: check if content is still available (old format)
            
                # Extract function name from script
                # function_name = self.extract_function_name_from_script(script_content)
                
                # Extract or generate docstring
                # docstring = self.extract_docstring_from_content(script_content)
                
                # Get analysis description from metadata if available
                # analysis_description = ""
                # if addn_meta and isinstance(addn_meta, dict):
                #     analysis_description = addn_meta.get("description", "")
                
                # Use analysis_description if available, otherwise fall back to docstring
                # final_description = analysis_description or docstring
                
            # Save to library
            result = library_client.save_analysis(
                question=original_question,
                # function_name=function_name,
                # docstring=final_description,
                # filename=os.path.basename(script_path),  # Store just filename, not full path
                metadata=addn_meta  # Pass additional metadata
            )
            
            if result.get("success"):
                logger.info(f"✅ Saved analysis for (ID: {addn_meta['analysisId']})")
            else:
                logger.error(f"❌ Failed to save analysis: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error saving completed analysis: {e}")
            return {"success": False, "error": str(e)}
    
    def get_library_stats(self) -> dict:
        """Get analysis library statistics"""
        library_client = self._get_library_client()
        if not library_client:
            return {"success": False, "error": "Analysis library not available"}
        
        try:
            # Get basic count from ChromaDB using the library's get_stats method
            stats = library_client.get_stats()
            if stats.get("success"):
                return {
                    "success": True, 
                    "total_analyses": stats["total_analyses"],
                    "status": "operational"
                }
            else:
                return stats
        except Exception as e:
            logger.error(f"❌ Error getting library stats: {e}")
            return {"success": False, "error": str(e)}

