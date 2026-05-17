"""Streaming output handler for real-time display"""

import queue
import threading
from typing import Callable, Optional

class StreamHandler:
    """Handle streaming output with callbacks"""
    
    def __init__(self):
        self.output_queue = queue.Queue()
        self.callback = None
        self.running = False
        self.thread = None
    
    def set_callback(self, callback: Callable):
        """Set callback for output"""
        self.callback = callback
    
    def write(self, text: str):
        """Write output to queue"""
        if self.callback:
            self.callback(text)
        self.output_queue.put(text)
    
    def writeln(self, text: str):
        """Write line to queue"""
        self.write(text + "\n")
    
    def start(self):
        """Start streaming thread"""
        self.running = True
        self.thread = threading.Thread(target=self._process_queue, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop streaming"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
    
    def _process_queue(self):
        """Process output queue in background"""
        while self.running:
            try:
                output = self.output_queue.get(timeout=0.1)
                if self.callback:
                    self.callback(output)
            except queue.Empty:
                continue
    
    def flush(self):
        """Flush queue"""
        while not self.output_queue.empty():
            try:
                output = self.output_queue.get_nowait()
                if self.callback:
                    self.callback(output)
            except queue.Empty:
                break

# Global stream handler instance
stream_handler = StreamHandler()