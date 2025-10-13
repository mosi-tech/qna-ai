#!/usr/bin/env python3
"""
Check available Ollama models
"""

try:
    import ollama
    
    # Create client
    client = ollama.Client(host="http://localhost:11434")
    
    # List available models
    models = client.list()
    
    print("Available Ollama models:")
    for model in models.get('models', []):
        print(f"  - {model.get('name', 'unknown')}")
        
    if not models.get('models'):
        print("No models found. You may need to pull a model first:")
        print("  ollama pull llama3.1")
        
except ImportError:
    print("Ollama library not installed. Install with: pip install ollama")
except Exception as e:
    print(f"Error checking models: {e}")
    print("Make sure Ollama is running at http://localhost:11434")