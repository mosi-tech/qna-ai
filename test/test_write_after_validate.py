#!/usr/bin/env python3
"""
Test case where write_file comes AFTER validation - validation should be excluded
"""

def _contains_tool_calls(content) -> bool:
    """Check if message content contains tool calls"""
    if not content:
        return False
    
    # Handle different content formats
    if isinstance(content, list):
        # Content is a list of tool use objects
        for item in content:
            if isinstance(item, dict) and item.get("type") == "tool_use":
                return True
    elif isinstance(content, str):
        # Content is a string representation - check for tool indicators
        tool_indicators = ["tool_use", "function_name", "mcp__", "write_file", "validate_python_script"]
        return any(indicator in content for indicator in tool_indicators)
    elif isinstance(content, dict):
        # Content is a single tool use object
        if content.get("type") == "tool_use":
            return True
    
    return False

def _contains_tool_results(content) -> bool:
    """Check if message content contains tool results"""
    if not content:
        return False
    
    # Handle different content formats
    if isinstance(content, list):
        # Content is a list of objects, check for tool_result type
        for item in content:
            if isinstance(item, dict) and item.get("type") == "tool_result":
                return True
    elif isinstance(content, str):
        # Content is a string representation - check for tool result indicators
        tool_result_indicators = ["tool_result", "tool_use_id"]
        return any(indicator in content for indicator in tool_result_indicators)
    elif isinstance(content, dict):
        # Content is a single tool result object
        if content.get("type") == "tool_result":
            return True
    
    return False

def _message_contains_function(content, function_name: str) -> bool:
    """Check if message content contains a specific function call"""
    if not content:
        return False
    
    # Handle different content formats
    if isinstance(content, list):
        # Content is a list of tool use objects
        for item in content:
            if isinstance(item, dict) and item.get("type") == "tool_use":
                tool_name = item.get("name", "")
                if function_name in tool_name:
                    return True
    elif isinstance(content, str):
        # Content is a string representation
        return function_name in content
    elif isinstance(content, dict):
        # Content is a single tool use object
        if content.get("type") == "tool_use":
            tool_name = content.get("name", "")
            return function_name in tool_name
    
    return False

def _filter_messages_for_context(messages):
    """Filter messages to keep only recent relevant tool interactions for conversation context"""
    try:
        # Always keep the first user message (original question)
        if not messages:
            return messages
        
        filtered_messages = [messages[0]]  # Keep original user message
        
        # Find assistant messages with tool calls and corresponding tool results
        tool_interaction_pairs = []
        i = 1
        while i < len(messages):
            msg = messages[i]
            if (msg.get("role") == "assistant" and 
                _contains_tool_calls(msg.get("content", ""))):
                
                # Look for the corresponding tool result message
                if (i + 1 < len(messages) and 
                    messages[i + 1].get("role") == "user" and
                    _contains_tool_results(messages[i + 1].get("content", ""))):
                    tool_interaction_pairs.append((i, i + 1, msg))  # (assistant_idx, tool_idx, assistant_msg)
                    i += 2  # Skip both messages
                else:
                    i += 1
            else:
                i += 1
        
        # Define functions that should be prioritized
        relevant_functions = {
            "write_file", "validate_python_script", "get_function_docstring",
            "read_file", "list_files", "delete_file"
        }
        
        # Find the most recent write_file and validate_python_script interactions
        last_write_pair = None
        last_write_idx = -1
        last_validate_pair = None
        last_validate_idx = -1
        docstring_pairs = []
        
        for assistant_idx, tool_idx, assistant_msg in tool_interaction_pairs:
            content = assistant_msg.get("content", "")
            
            # Check if this contains write_file or validate_python_script
            if _message_contains_function(content, "write_file"):
                last_write_pair = (assistant_idx, tool_idx)
                last_write_idx = assistant_idx
            elif _message_contains_function(content, "validate_python_script"):
                last_validate_pair = (assistant_idx, tool_idx)
                last_validate_idx = assistant_idx
            elif _message_contains_function(content, "get_function_docstring"):
                # Keep all docstring calls as they provide important context
                docstring_pairs.append((assistant_idx, tool_idx))
        
        # Collect pairs to keep
        pairs_to_keep = set()
        
        # Include all docstring interactions (they provide important context)
        for pair in docstring_pairs:
            pairs_to_keep.add(pair)
        
        # Include the most recent write_file
        if last_write_pair:
            pairs_to_keep.add(last_write_pair)
        
        # Only include validation if it comes AFTER the last write_file
        # (if write_file comes after validation, the validation is for an old script version)
        if last_validate_pair and (last_write_idx == -1 or last_validate_idx > last_write_idx):
            pairs_to_keep.add(last_validate_pair)
        
        # Add the filtered tool interactions to messages
        for assistant_idx, tool_idx in sorted(pairs_to_keep):
            if assistant_idx < len(messages):
                filtered_messages.append(messages[assistant_idx])
            if tool_idx < len(messages):
                filtered_messages.append(messages[tool_idx])
        
        print(f"Filtered {len(messages)} messages down to {len(filtered_messages)} for context")
        return filtered_messages
        
    except Exception as e:
        print(f"Error filtering messages for context: {e}")
        # Fallback: keep first message + last 6 messages (3 tool interactions)
        if len(messages) <= 7:
            return messages
        return [messages[0]] + messages[-6:]

# Create test messages where write_file comes AFTER validation
test_messages = [
    {
        "role": "user",
        "content": [{"type": "text", "text": "What's the best weekday to trade AAPL?"}]
    },
    {
        "role": "assistant", 
        "content": [
            {"type": "tool_use", "id": "1", "name": "mcp__mcp-validation-server__write_file", "input": {"filename": "script.py", "content": "first version..."}}
        ]
    },
    {
        "role": "user",
        "content": [{"tool_use_id": "1", "type": "tool_result", "content": [{"type": "text", "text": "File written successfully"}]}]
    },
    {
        "role": "assistant",
        "content": [
            {"type": "tool_use", "id": "2", "name": "mcp__mcp-validation-server__validate_python_script", "input": {"script_filename": "script.py"}}
        ]
    },
    {
        "role": "user",
        "content": [{"tool_use_id": "2", "type": "tool_result", "content": [{"type": "text", "text": "Validation failed - syntax error"}]}]
    },
    {
        "role": "assistant",
        "content": [
            {"type": "tool_use", "id": "3", "name": "mcp__mcp-validation-server__write_file", "input": {"filename": "script.py", "content": "FIXED version..."}}
        ]
    },
    {
        "role": "user",
        "content": [{"tool_use_id": "3", "type": "tool_result", "content": [{"type": "text", "text": "File written successfully - fixed version"}]}]
    }
]

def test_write_after_validate():
    print("Original messages:")
    for i, msg in enumerate(test_messages):
        role = msg.get("role")
        content = msg.get("content", [])
        if role == "assistant" and isinstance(content, list):
            tool_names = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "tool_use":
                    tool_names.append(item.get("name", "unknown"))
            if tool_names:
                print(f"{i}: {role} - {tool_names}")
            else:
                print(f"{i}: {role} - text only")
        else:
            print(f"{i}: {role}")
    
    print("\n" + "="*50)
    
    # Test filtering with standalone function
    filtered = _filter_messages_for_context(test_messages)
    
    print("\nFiltered messages:")
    original_indices = []
    for filtered_msg in filtered:
        for i, original_msg in enumerate(test_messages):
            if filtered_msg is original_msg:
                original_indices.append(i)
                break
    
    print(f"Kept message indices: {original_indices}")
    
    for i, idx in enumerate(original_indices):
        msg = test_messages[idx]
        role = msg.get("role")
        content = msg.get("content", [])
        if role == "assistant" and isinstance(content, list):
            tool_names = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "tool_use":
                    tool_names.append(item.get("name", "unknown"))
            if tool_names:
                print(f"Filtered[{i}] = Original[{idx}]: {role} - {tool_names}")
            else:
                print(f"Filtered[{i}] = Original[{idx}]: {role} - text only")
        else:
            print(f"Filtered[{i}] = Original[{idx}]: {role}")
    
    # Should NOT include validation (messages 3-4) since write_file (messages 5-6) comes after it
    expected_to_exclude = [3, 4]  # validation that's followed by write_file
    expected_to_include = [0, 1, 2, 5, 6]  # original question + last write_file
    
    print(f"\nExpected exclusion check:")
    print(f"Should exclude validation messages {expected_to_exclude}: {not any(idx in original_indices for idx in expected_to_exclude)}")
    print(f"Should include last write_file {[5, 6]}: {all(idx in original_indices for idx in [5, 6])}")

if __name__ == "__main__":
    test_write_after_validate()