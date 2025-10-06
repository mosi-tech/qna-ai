# Analysis Library Search MCP Server

Simple ChromaDB-based MCP server for storing and searching financial analysis questions with descriptions.

## Features

- **Vector Similarity Search**: Find similar analyses using ChromaDB embeddings
- **Simple Storage**: Store question, function name, and description only
- **LLM Integration**: Let LLM handle complex logic via MCP calls

## Installation

```bash
cd mcp-server/search
pip install -r requirements.txt
```

## Usage

### As MCP Server
```bash
python analysis_library_server.py
```

### Available Tools

1. **save_analysis** - Save question with function name and description
2. **search_similar_analyses** - Find similar analyses by question

### Environment Variables

- `ANALYSIS_DB_PATH`: Path to ChromaDB database (default: `./data/analysis_library_db`)

## Integration with API Server

The MCP server is automatically configured in the main API server's MCP configuration.

## Data Schema

Each analysis contains:
- Question 
- Function name
- Docstring/description
- Created date and usage count

## Search Implementation

For optimal search results, the server combines all fields into a single document for embedding:

```
Question: {question}
Description: {docstring}
Function: {function_name}
```

This allows ChromaDB to find matches across question text, function descriptions, and function names, providing much better semantic search results.