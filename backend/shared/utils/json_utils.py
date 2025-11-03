"""
JSON utilities for handling LLM responses with comments and other formatting issues
"""

import json
import re
import logging
from typing import Any, Dict, Union

logger = logging.getLogger(__name__)


def clean_json_comments(json_string: str) -> str:
    """
    Clean JSON comments and markdown code blocks from a string before parsing.
    
    Handles:
    - Markdown code blocks: ```json ... ``` or ```...```
    - Line comments: // comment
    - Trailing commas in objects and arrays
    - Multiple whitespace characters
    
    Args:
        json_string: Raw JSON string that may contain comments and markdown
        
    Returns:
        Cleaned JSON string ready for parsing
        
    Example:
        >>> raw = '```json\n{"key": "value",  // this is a comment\n  "num": 42,}\n```'
        >>> clean = clean_json_comments(raw)
        >>> '{"key": "value", "num": 42}'
    """
    try:
        # Remove markdown code blocks (```json...``` or ```...```)
        # This pattern matches triple backticks, optional language, content, and closing backticks
        cleaned = re.sub(r'```(?:json)?\s*\n?(.*?)\n?```', r'\1', json_string, flags=re.DOTALL)
        
        # Remove line comments (// ...)
        # This pattern matches // followed by any characters until end of line
        cleaned = re.sub(r'//.*?(?=\n|$)', '', cleaned)
        
        # Remove trailing commas before closing braces/brackets
        # Match comma followed by optional whitespace and closing brace/bracket
        cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
        
        # Clean up excessive whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remove any remaining whitespace around braces and brackets
        cleaned = cleaned.strip()
        
        logger.debug(f"JSON cleaned successfully")
        return cleaned
        
    except Exception as e:
        logger.warning(f"Error cleaning JSON comments: {e}")
        # Return original string if cleaning fails
        return json_string


def safe_json_loads(json_string: str, default: Any = None) -> Union[Dict, Any]:
    """
    Safely parse JSON string with automatic comment cleaning.
    
    Args:
        json_string: Raw JSON string that may contain comments
        default: Default value to return if parsing fails
        
    Returns:
        Parsed JSON object or default value
        
    Example:
        >>> result = safe_json_loads('{"key": "value" // comment}')
        >>> {"key": "value"}
    """
    try:
        # First try direct parsing (in case JSON is already clean)
        return json.loads(json_string)
        
    except json.JSONDecodeError:
        logger.debug("Direct JSON parsing failed, attempting to clean comments")
        
        try:
            # Clean comments and try again
            cleaned_json = clean_json_comments(json_string)
            result = json.loads(cleaned_json)
            logger.info("✅ JSON parsed successfully after comment cleaning")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing failed even after cleaning: {e}")
            logger.error(f"Original JSON: {json_string[:200]}...")
            logger.error(f"Cleaned JSON: {cleaned_json[:200]}...")
            
            if default is not None:
                logger.info(f"Returning default value: {default}")
                return default
            else:
                raise
                
    except Exception as e:
        logger.error(f"❌ Unexpected error during JSON parsing: {e}")
        if default is not None:
            return default
        else:
            raise