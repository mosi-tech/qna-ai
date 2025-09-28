"""
MCP Schema Generation Utilities

Shared utilities for extracting MCP tool schemas from function docstrings
and type hints. Used by both analytics and financial servers.
"""

import inspect
import re
import logging
from typing import Dict, List, Any, Optional, get_type_hints

logger = logging.getLogger(__name__)


def extract_schema_from_docstring(func) -> Optional[Dict[str, Any]]:
    """Extract complete MCP tool schema from function docstring and type hints.
    
    Parses Google-style docstrings to extract parameter descriptions, return type info,
    and annotations to generate complete MCP tool schema with all supported fields.
    
    Args:
        func: Function to analyze
        
    Returns:
        Dict containing complete MCP tool schema with description, inputSchema, 
        outputSchema, and annotations
    """
    try:
        # Get function signature and type hints
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        docstring = inspect.getdoc(func)
        
        if not docstring:
            return None
            
        # Parse docstring sections
        lines = docstring.strip().split('\n')
        
        # Extract title (first line) and description (following lines until first section)
        title = lines[0].strip()
        description_lines = []
        
        # Find description (lines after title until first section marker)
        description_start = 1
        for line in lines[1:]:
            line_stripped = line.strip()
            if line_stripped.startswith(('Args:', 'Parameters:', 'Returns:', 'Annotations:', 'Hints:', 'Raises:', 'Example:', 'Examples:', 'Note:', 'Notes:')):
                break
            elif line_stripped:  # Non-empty line
                description_lines.append(line_stripped)
                description_start += 1
            else:
                description_start += 1
        
        # Join description lines, using title as fallback if no description
        description = ' '.join(description_lines).strip() if description_lines else title
        
        # Initialize section trackers
        sections = {
            'args': [],
            'returns': [],
            'annotations': []
        }
        current_section = None
        
        # Parse all sections (start from where description ended)
        section_start = description_start + len(description_lines)
        for line in lines[section_start:]:
            line_stripped = line.strip()
            
            if line_stripped.startswith('Args:'):
                current_section = 'args'
                continue
            elif line_stripped.startswith('Returns:'):
                current_section = 'returns'
                continue
            elif line_stripped.startswith('Annotations:') or line_stripped.startswith('Hints:'):
                current_section = 'annotations'
                continue
            elif line_stripped.startswith(('Raises:', 'Example:', 'Note:', 'Examples:')):
                current_section = None
                continue
            elif current_section and line_stripped:
                sections[current_section].append(line_stripped)
        
        # Parse parameter descriptions
        param_descriptions = {}
        current_param = None
        
        for line in sections['args']:
            # Match parameter definition: "param_name: description"
            param_match = re.match(r'^(\w+):\s*(.+)', line)
            if param_match:
                current_param = param_match.group(1)
                param_descriptions[current_param] = param_match.group(2)
            elif current_param and line.startswith(' '):
                # Continuation of previous parameter description
                param_descriptions[current_param] += ' ' + line.strip()
        
        # Build inputSchema properties
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name in ['self', 'cls']:
                continue
                
            # Get type information
            param_type = type_hints.get(param_name, param.annotation)
            json_type = python_type_to_json_type(param_type)
            
            # Get description
            param_desc = param_descriptions.get(param_name, f"Parameter {param_name}")
            
            # Build property schema
            prop_schema = {
                "type": json_type,
                "description": param_desc
            }
            
            # Add default value if available
            if param.default != inspect.Parameter.empty:
                prop_schema["default"] = param.default
            else:
                required.append(param_name)
            
            properties[param_name] = prop_schema
        
        # Build complete MCP tool schema
        schema = {
            "name": func.__name__,  # Include function name for completeness
            "title": title,  # First line of docstring
            "description": description,  # Detailed description
            "inputSchema": {
                "type": "object",
                "properties": properties
            }
        }
        
        if required:
            schema["inputSchema"]["required"] = required
        
        # Add outputSchema if Returns section is present
        if sections['returns']:
            output_schema = _parse_returns_section(sections['returns'], type_hints.get('return'))
            if output_schema:
                schema["outputSchema"] = output_schema
        
        # Add annotations if present
        annotations = _parse_annotations_section(sections['annotations'])
        if annotations:
            schema["annotations"] = annotations
            
        return schema
        
    except Exception as e:
        logger.warning(f"Failed to extract schema for {func.__name__}: {e}")
        return None


def _parse_returns_section(returns_lines: List[str], return_type_hint=None) -> Optional[Dict[str, Any]]:
    """Parse Returns section to generate outputSchema.
    
    Args:
        returns_lines: Lines from the Returns section
        return_type_hint: Type hint for return value
        
    Returns:
        OutputSchema dict or None
    """
    if not returns_lines:
        return None
    
    # Get return type
    json_type = python_type_to_json_type(return_type_hint) if return_type_hint else "object"
    
    # Join all return description lines
    description = ' '.join(returns_lines).strip()
    
    # Basic output schema structure
    output_schema = {
        "type": json_type,
        "description": description
    }
    
    # If it's an object type, try to infer structure from description
    if json_type == "object" and any(keyword in description.lower() for keyword in ['dict', 'dictionary', 'object', 'json']):
        # Look for property descriptions in the returns section
        properties = {}
        
        # Simple pattern matching for common return formats
        # Example: "Dict with 'result': calculation result, 'metadata': additional info"
        prop_matches = re.findall(r"['\"](\w+)['\"]:\s*([^,]+)", description)
        
        if prop_matches:
            for prop_name, prop_desc in prop_matches:
                properties[prop_name] = {
                    "type": "string",  # Default to string, could be enhanced
                    "description": prop_desc.strip()
                }
            
            output_schema["properties"] = properties
    
    return output_schema


def _parse_annotations_section(annotations_lines: List[str]) -> Optional[Dict[str, Any]]:
    """Parse Annotations/Hints section to generate tool annotations.
    
    Args:
        annotations_lines: Lines from the Annotations section
        
    Returns:
        Annotations dict or None
    """
    if not annotations_lines:
        return None
    
    annotations = {}
    
    for line in annotations_lines:
        # Parse annotation entries like "destructive: true" or "title: Calculate metrics"
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            
            # Map common annotation keys to MCP standard names
            key_mapping = {
                'destructive': 'destructiveHint',
                'readonly': 'readOnlyHint', 
                'read_only': 'readOnlyHint',
                'idempotent': 'idempotentHint',
                'open_world': 'openWorldHint',
                'title': 'title'
            }
            
            mcp_key = key_mapping.get(key, key)
            
            # Convert string boolean values
            if value.lower() in ('true', 'false'):
                annotations[mcp_key] = value.lower() == 'true'
            else:
                annotations[mcp_key] = value
    
    return annotations if annotations else None


def python_type_to_json_type(python_type) -> str:
    """Convert Python type hints to JSON schema types.
    
    Handles common Python types including pandas DataFrame and Series
    which are frequently used in analytics functions.
    """
    if python_type == inspect.Parameter.empty:
        return "string"
    
    # Handle string representation of types
    if isinstance(python_type, str):
        python_type = python_type.lower()
        if 'int' in python_type:
            return "integer"
        elif 'float' in python_type or 'number' in python_type:
            return "number"
        elif 'bool' in python_type:
            return "boolean"
        elif 'list' in python_type or 'array' in python_type:
            return "array"
        elif 'dict' in python_type or 'dataframe' in python_type or 'series' in python_type:
            return "object"
        else:
            return "string"
    
    # Handle actual type objects
    type_str = str(python_type).lower()
    
    # Check for pandas types first (most specific)
    if 'dataframe' in type_str or 'series' in type_str:
        return "object"
    # Check for numpy types
    elif 'ndarray' in type_str or 'numpy' in type_str:
        return "array"
    # Check for Union types (common in analytics functions)
    elif 'union' in type_str:
        # For Union types, default to object since they can accept multiple types
        return "object"
    # Standard Python types
    elif 'int' in type_str:
        return "integer"
    elif 'float' in type_str or 'number' in type_str:
        return "number"
    elif 'bool' in type_str:
        return "boolean"
    elif 'list' in type_str or 'array' in type_str:
        return "array"
    elif 'dict' in type_str:
        return "object"
    else:
        return "string"


def initialize_schema_cache(functions_dict: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Initialize schema cache for a dictionary of functions.
    
    Args:
        functions_dict: Dictionary mapping function names to function objects
        
    Returns:
        Dictionary mapping function names to their MCP schemas
    """
    schema_cache = {}
    
    logger.info(f"Generating schemas for {len(functions_dict)} functions...")
    
    for func_name, func in functions_dict.items():
        try:
            schema = extract_schema_from_docstring(func)
            if schema:
                schema_cache[func_name] = schema
                logger.debug(f"Cached schema for {func_name}")
            else:
                # Fallback schema for functions without proper docstrings
                schema_cache[func_name] = {
                    "name": func_name,
                    "title": func_name.replace('_', ' ').title(),
                    "description": f"Function: {func_name}",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "data": {"type": "array", "description": "Input data"}
                        },
                        "required": ["data"]
                    }
                }
                logger.warning(f"Using fallback schema for {func_name}")
        except Exception as e:
            logger.error(f"Failed to generate schema for {func_name}: {e}")
            continue
    
    logger.info(f"Schema cache initialized with {len(schema_cache)} functions")
    return schema_cache