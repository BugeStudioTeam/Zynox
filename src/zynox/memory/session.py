"""Session memory management"""

import os
import json
from datetime import datetime
from ..config import MEMORY_DIR

class SessionManager:
    """Manage conversation sessions"""
    
    def __init__(self):
        self.current_session = self.load_current_session()
    
    def load_current_session(self) -> dict:
        """Load current session from file"""
        session_file = os.path.join(MEMORY_DIR, "current_session.json")
        if os.path.exists(session_file):
            try:
                with open(session_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "messages": [],
            "created_at": datetime.now().isoformat()
        }
    
    def save_current_session(self):
        """Save current session"""
        session_file = os.path.join(MEMORY_DIR, "current_session.json")
        with open(session_file, 'w') as f:
            json.dump(self.current_session, f, indent=2)
    
    def add_message(self, role: str, content: str):
        """Add a message to current session"""
        self.current_session["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.save_current_session()
    
    def get_conversation_context(self, limit: int = 5) -> str:
        """Get recent conversation context"""
        messages = self.current_session["messages"][-limit:]
        if not messages:
            return ""
        context = "\n"
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            context += f"{role}: {msg['content'][:200]}\n"
        return context
    
    def new_session(self):
        """Start a new session"""
        # Save old session to history
        if self.current_session["messages"]:
            history_file = os.path.join(MEMORY_DIR, f"{self.current_session['session_id']}.json")
            with open(history_file, 'w') as f:
                json.dump(self.current_session, f, indent=2)
        
        # Create new session
        self.current_session = {
            "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "messages": [],
            "created_at": datetime.now().isoformat()
        }
        self.save_current_session()
        print(f"[New session created: {self.current_session['session_id']}]")
    
    def list_sessions(self) -> list:
        """List all saved sessions"""
        sessions = []
        for file in os.listdir(MEMORY_DIR):
            if file.endswith('.json') and file != "current_session.json":
                with open(os.path.join(MEMORY_DIR, file), 'r') as f:
                    data = json.load(f)
                    sessions.append({
                        "id": data.get("session_id", file.replace('.json', '')),
                        "created": data.get("created_at", "Unknown"),
                        "message_count": len(data.get("messages", []))
                    })
        return sessions
    
    def load_session(self, session_id: str) -> bool:
        """Load a specific session"""
        session_file = os.path.join(MEMORY_DIR, f"{session_id}.json")
        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                self.current_session = json.load(f)
            self.save_current_session()
            return True
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a specific session"""
        session_file = os.path.join(MEMORY_DIR, f"{session_id}.json")
        if os.path.exists(session_file):
            os.remove(session_file)
            return True
        return False
    
    def clear_memory(self):
        """Clear current session memory"""
        self.current_session = {
            "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "messages": [],
            "created_at": datetime.now().isoformat()
        }
        self.save_current_session()
        print("[Memory cleared, new session started]")