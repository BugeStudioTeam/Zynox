#!/usr/bin/env python3
"""
ZynoxAI - AI-powered file/folder creation tool
Entry point for the application
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from zynox.cli import main

if __name__ == "__main__":
    main()