#!/usr/bin/env python3
"""Wrapper script for PM2 - runs execution worker as module"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Run the worker as a module
import shared.queue.execution_worker