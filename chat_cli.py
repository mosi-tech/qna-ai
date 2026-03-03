#!/usr/bin/env python3
"""
Simple CLI tool for testing hybrid chat system

Usage:
    python chat_cli.py "Hello, what is diversification?"
    python chat_cli.py "Yes, run that analysis"
    python chat_cli.py --interactive

Features:
- Hardcoded test session ID
- Clean output format
- Interactive mode for back-and-forth testing
- Shows intent classification and analysis triggering
"""

import asyncio
import aiohttp
import json
import sys
import argparse
from datetime import datetime

# Hardcoded configuration
API_BASE_URL = "http://localhost:8010"
TEST_SESSION_ID = "cli-test-session-123"
TEST_USER_ID = "cli-test-user"

async def send_message(message: str, verbose: bool = False) -> dict:
    """Send message to hybrid chat endpoint and return response"""
    
    payload = {
        "question": message,
        "session_id": TEST_SESSION_ID,
        "user_id": TEST_USER_ID
    }
    
    if verbose:
        print(f"📡 Sending to: {API_BASE_URL}/chat")
        print(f"📝 Payload: {json.dumps(payload, indent=2)}")
        print("⏳ Waiting for response...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_BASE_URL}/chat",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                status = response.status
                
                if status == 200:
                    result = await response.json()
                    if verbose:
                        print(f"✅ HTTP {status} - Success")
                    return result
                else:
                    error_text = await response.text()
                    if verbose:
                        print(f"❌ HTTP {status} - Error")
                        print(f"Error: {error_text}")
                    return {
                        "success": False, 
                        "error": f"HTTP {status}: {error_text}",
                        "status_code": status
                    }
                    
    except asyncio.TimeoutError:
        error_msg = "Request timed out after 30 seconds"
        if verbose:
            print(f"⏰ {error_msg}")
        return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Request failed: {e}"
        if verbose:
            print(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}

def format_response(result: dict, show_metadata: bool = False) -> str:
    """Format response for clean display"""
    
    if not result.get("success", False):
        return f"❌ Error: {result.get('error', 'Unknown error')}"
    
    data = result.get("data", {})
    response_type = data.get("response_type", "unknown")
    content = data.get("content", "")
    metadata = data.get("metadata", {})
    
    # Main response
    output = []
    output.append(f"🤖 Assistant ({response_type}):")
    output.append(f"   {content}")
    
    # Analysis information
    if metadata.get("analysis_triggered"):
        output.append(f"🔄 Analysis Triggered: {metadata.get('analysis_question', 'Unknown')}")
        
    if metadata.get("suggested_analysis"):
        suggestion = metadata["suggested_analysis"]
        output.append(f"💡 Analysis Suggestion: {suggestion.get('topic', 'Unknown')}")
    
    # Intent classification
    if metadata.get("intent"):
        output.append(f"🎯 Intent: {metadata['intent']}")
    
    # Full metadata (if requested)
    if show_metadata and metadata:
        output.append(f"📊 Metadata: {json.dumps(metadata, indent=2)}")
    
    return "\n".join(output)

async def interactive_mode():
    """Interactive chat mode"""
    print("🔄 Interactive Hybrid Chat Mode")
    print(f"📍 Session: {TEST_SESSION_ID}")
    print("Type 'quit', 'exit', or 'q' to stop")
    print("Type '--meta' to toggle metadata display")
    print("Type '--help' for commands")
    print("=" * 50)
    
    show_metadata = False
    
    while True:
        try:
            user_input = input("\n💬 YOU: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input == '--meta':
                show_metadata = not show_metadata
                print(f"🔧 Metadata display: {'ON' if show_metadata else 'OFF'}")
                continue
            elif user_input == '--help':
                print("Commands:")
                print("  --meta    Toggle metadata display")
                print("  --help    Show this help")
                print("  quit/exit Exit interactive mode")
                continue
            elif not user_input:
                continue
            
            print("⏳ Processing...")
            result = await send_message(user_input, verbose=False)
            print(format_response(result, show_metadata))
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

async def single_message_mode(message: str, verbose: bool = False, show_metadata: bool = False):
    """Send a single message and display response"""
    
    if verbose:
        print(f"💬 Sending: '{message}'")
        print(f"📍 Session: {TEST_SESSION_ID}")
    
    result = await send_message(message, verbose=verbose)
    print(format_response(result, show_metadata))
    
    # Return exit code based on success
    return 0 if result.get("success", False) else 1

def main():
    """Main CLI entry point"""
    global TEST_SESSION_ID
    
    parser = argparse.ArgumentParser(
        description="Simple CLI tool for testing hybrid chat system",
        epilog="""
Examples:
  python chat_cli.py "Hello, what is diversification?"
  python chat_cli.py "Yes, run that analysis" --verbose
  python chat_cli.py --interactive
  python chat_cli.py "Analyze AAPL vs MSFT" --meta
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'message', 
        nargs='?', 
        help='Message to send (if not provided, uses interactive mode)'
    )
    parser.add_argument(
        '--interactive', '-i', 
        action='store_true',
        help='Start interactive chat mode'
    )
    parser.add_argument(
        '--verbose', '-v', 
        action='store_true',
        help='Show detailed request/response information'
    )
    parser.add_argument(
        '--meta', '-m', 
        action='store_true',
        help='Show response metadata'
    )
    parser.add_argument(
        '--session-id', 
        default=TEST_SESSION_ID,
        help=f'Session ID (default: {TEST_SESSION_ID})'
    )
    
    args = parser.parse_args()
    
    # Update session ID if provided
    TEST_SESSION_ID = args.session_id
    
    # Show configuration
    if args.verbose:
        print("🔧 Configuration:")
        print(f"   API URL: {API_BASE_URL}")
        print(f"   Session ID: {TEST_SESSION_ID}")
        print(f"   User ID: {TEST_USER_ID}")
        print()
    
    # Run appropriate mode
    if args.interactive or not args.message:
        asyncio.run(interactive_mode())
    else:
        exit_code = asyncio.run(single_message_mode(
            args.message, 
            verbose=args.verbose,
            show_metadata=args.meta
        ))
        sys.exit(exit_code)

if __name__ == "__main__":
    main()