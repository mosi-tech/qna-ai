#!/usr/bin/env python3
"""
Analysis Service - Handles analysis library integration for apiServer
"""

import os
import sys
import re
import logging
from search.client import AnalysisLibraryClient

logger = logging.getLogger("analysis-service")

class AnalysisService:
    """Service for managing analysis library integration"""
    
    def __init__(self):
        """Initialize the analysis service"""
        try:
            if AnalysisLibraryClient is None:
                logger.warning("AnalysisLibraryClient not available - analysis library features disabled")
                self.library_client = None
            else:
                self.library_client = AnalysisLibraryClient()
                logger.info("✅ Analysis library service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize analysis library: {e}")
            self.library_client = None
    
    def search_and_enhance_message(self, user_question: str) -> tuple[str, list]:
        """Search for similar analyses and enhance user message with context"""
        if not self.library_client:
            return user_question, []
        
        try:
            # Search for similar analyses
            search_result = self.library_client.search_similar(
                query=user_question,
                top_k=3,
                similarity_threshold=0.3  # Lower threshold to find more potential matches
            )
            
            if not search_result.get("success") or not search_result.get("found_similar"):
                logger.info("🔍 No similar analyses found")
                return user_question, []
            
            similar_analyses = search_result["analyses"]
            logger.info(f"🔍 Found {len(similar_analyses)} similar analyses")
            
            # Build enhanced context
            context_lines = [
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
                "- Create a variation that addresses the specific differences",
                "",
                "🎯 ORIGINAL QUESTION:"
            ])
            
            enhanced_message = "\n".join(context_lines) + "\n" + user_question
            
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
    
    def extract_docstring_from_content(self, llm_content: str, script_content: str) -> str:
        """Extract or generate docstring from LLM content or script"""
        try:
            # First try to extract docstring from script
            docstring_match = re.search(r'"""(.*?)"""', script_content, re.DOTALL)
            if docstring_match:
                docstring = docstring_match.group(1).strip()
                if len(docstring) > 50:  # Good docstring found
                    return docstring
            
            # Fallback: generate from LLM content
            lines = llm_content.split('\n')
            description_lines = []
            
            for line in lines:
                line = line.strip()
                if (line and 
                    not line.startswith('#') and 
                    'def ' not in line and
                    'import ' not in line and
                    not line.startswith('```')):
                    description_lines.append(line)
                    if len(description_lines) >= 2:  # Limit length
                        break
            
            if description_lines:
                return '. '.join(description_lines)
            else:
                return "Financial analysis function generated from user query"
                
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
    
    def save_completed_analysis(self, original_question: str, script_content: str, llm_content: str, tool_calls: list = None) -> dict:
        """Save analysis after successful completion"""
        if not self.library_client:
            return {"success": False, "error": "Analysis library not available"}
        
        try:
            # Extract function name from script
            function_name = self.extract_function_name_from_script(script_content)
            
            # Extract or generate docstring
            docstring = self.extract_docstring_from_content(llm_content, script_content)
            
            # Extract filename from tool calls if available
            filename = None
            if tool_calls:
                filename = self.extract_filename_from_tool_calls(tool_calls)
            
            # Save to library
            result = self.library_client.save_analysis(
                question=original_question,
                function_name=function_name,
                docstring=docstring,
                filename=filename
            )
            
            if result.get("success"):
                logger.info(f"✅ Saved analysis: {function_name} (ID: {result['analysis_id']})")
            else:
                logger.error(f"❌ Failed to save analysis: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error saving completed analysis: {e}")
            return {"success": False, "error": str(e)}
    
    def get_library_stats(self) -> dict:
        """Get analysis library statistics"""
        if not self.library_client:
            return {"success": False, "error": "Analysis library not available"}
        
        try:
            # Get basic count from ChromaDB
            count = self.library_client.library.collection.count()
            return {
                "success": True, 
                "total_analyses": count,
                "status": "operational"
            }
        except Exception as e:
            logger.error(f"❌ Error getting library stats: {e}")
            return {"success": False, "error": str(e)}

# Global service instance
analysis_service = AnalysisService()