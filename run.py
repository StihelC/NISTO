#!/usr/bin/env python3
import sys
import os

# Add the source directory to the Python path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                     "network-topology-designer", "src")
sys.path.insert(0, src_dir)

# Import the main function from the main module
from main import main

if __name__ == "__main__":
    sys.exit(main())