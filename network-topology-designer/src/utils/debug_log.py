import logging
import sys

def debug(message):
    """Print debug message with timestamp."""
    print(f"DEBUG: {message}")
    sys.stdout.flush()  # Force immediate output