#!/usr/bin/env python3
"""
Examples of different ways to pipe subprocess output to current process
"""

import subprocess
import sys
import threading
import queue

def example_1_inherit_streams():
    """Option 1: Simple inheritance - output goes directly to console"""
    print("=== Option 1: Direct inheritance ===")
    
    # This will show output in real-time but you can't capture it
    result = subprocess.run(
        ["echo", "Hello from subprocess"],
        stdout=None,  # Inherits parent's stdout (your console)
        stderr=None   # Inherits parent's stderr (your console)
    )
    print(f"Return code: {result.returncode}")


def example_2_tee_functionality():
    """Option 2: Tee functionality - show AND capture"""
    print("\n=== Option 2: Tee functionality ===")
    
    process = subprocess.Popen(
        ["echo", "Hello from Popen"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout_lines = []
    stderr_lines = []
    
    # Read stdout and print to console while capturing
    for line in process.stdout:
        print(f"STDOUT: {line}", end="")  # Print to console
        stdout_lines.append(line)  # Capture for later use
    
    # Read stderr and print to console while capturing  
    for line in process.stderr:
        print(f"STDERR: {line}", end="", file=sys.stderr)  # Print to console
        stderr_lines.append(line)  # Capture for later use
    
    process.wait()
    
    print(f"Captured stdout: {''.join(stdout_lines)}")
    print(f"Return code: {process.returncode}")


def example_3_real_time_streaming():
    """Option 3: Real-time streaming with threading"""
    print("\n=== Option 3: Real-time streaming ===")
    
    def stream_output(pipe, prefix, output_list):
        """Stream output from pipe to console and capture"""
        for line in iter(pipe.readline, ''):
            if line:
                print(f"{prefix}: {line}", end="")
                output_list.append(line)
        pipe.close()
    
    process = subprocess.Popen(
        ["python", "-c", "import time; [print(f'Line {i}') or time.sleep(0.5) for i in range(5)]"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # Line buffered
    )
    
    stdout_lines = []
    stderr_lines = []
    
    # Start threads to handle stdout and stderr
    stdout_thread = threading.Thread(
        target=stream_output, 
        args=(process.stdout, "OUT", stdout_lines)
    )
    stderr_thread = threading.Thread(
        target=stream_output, 
        args=(process.stderr, "ERR", stderr_lines)
    )
    
    stdout_thread.start()
    stderr_thread.start()
    
    # Wait for process and threads to complete
    process.wait()
    stdout_thread.join()
    stderr_thread.join()
    
    print(f"Captured {len(stdout_lines)} stdout lines")
    print(f"Return code: {process.returncode}")


def example_4_claude_cli_streaming():
    """Option 4: Specific example for Claude CLI"""
    print("\n=== Option 4: Claude CLI streaming example ===")
    
    # This is what you could use for Claude CLI
    cli_command = "echo 'Simulating Claude CLI output...'"
    
    # For real-time viewing (debug mode)
    print("Real-time mode:")
    result = subprocess.run(
        cli_command,
        shell=True,
        stdout=None,  # Goes to console
        stderr=None   # Goes to console
    )
    
    print("\nCapture mode:")
    # For capturing output (production mode)
    result = subprocess.run(
        cli_command,
        shell=True,
        capture_output=True,
        text=True
    )
    print(f"Captured: {result.stdout}")


if __name__ == "__main__":
    print("Subprocess streaming examples:\n")
    
    example_1_inherit_streams()
    example_2_tee_functionality() 
    example_3_real_time_streaming()
    example_4_claude_cli_streaming()
    
    print("\n" + "="*50)
    print("For Claude CLI, you can:")
    print("1. Use stdout=None, stderr=None for real-time viewing")
    print("2. Use capture_output=True for parsing JSON responses")
    print("3. Use Popen with threading for both real-time AND capture")
    print("4. Switch modes based on debug/production environment")