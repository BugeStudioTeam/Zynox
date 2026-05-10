"""Logging utilities"""

import logging
import os
from datetime import datetime
from ..config import OUTPUT_DIR

LOG_FILE = os.path.join(OUTPUT_DIR, "logs", f"zynox_{datetime.now().strftime('%Y%m%d')}.log")

def setup_logger():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logger()