"""Flask web application for ZynoxAI - Complete with file icons and forced workspace"""

import os
import sys
import json
import subprocess
import io
import zipfile
import time
import threading
import requests
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, Response, stream_with_context
from contextlib import redirect_stdout

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from zynox.cli import ZynoxAI
from zynox.config import Config
from zynox.memory.session import SessionManager
from zynox.core.file.manager import FileManager

# Get directories
WEB_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(WEB_DIR, 'templates')
STATIC_DIR = os.path.join(WEB_DIR, 'static')

# Create directories if not exist
os.makedirs(TEMPLATE_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, 'css'), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, 'js'), exist_ok=True)

# Download icons from GitHub
ICON_URLS = {
    'folder': 'https://raw.githubusercontent.com/BugeStudioTeam/Zynox/refs/heads/main/images/icons/folder.png',
    'zip': 'https://raw.githubusercontent.com/BugeStudioTeam/Zynox/refs/heads/main/images/icons/zip.png',
    'file': 'https://raw.githubusercontent.com/BugeStudioTeam/Zynox/refs/heads/main/images/icons/file.png'
}

def download_icon(name, url):
    """Download icon from URL to static directory"""
    icon_path = os.path.join(STATIC_DIR, f'{name}.png')
    if not os.path.exists(icon_path):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(icon_path, 'wb') as f:
                    f.write(response.content)
                print(f"[Downloaded icon: {name}.png]")
            else:
                print(f"[Failed to download {name}.png: HTTP {response.status_code}]")
        except Exception as e:
            print(f"[Error downloading {name}.png: {e}]")

# Download icons on startup
for name, url in ICON_URLS.items():
    download_icon(name, url)

# Global ZynoxAI instance
zynox = None
config = None
session_manager = None
file_manager = None

# Global current directory for terminal
global_cwd = os.path.expanduser("~")

# Global stop flag for current task
stop_task_flag = False

# Complete HTML template with icons
INDEX_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="color-scheme" content="dark light">
    <title>ZynoxAI</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --bg-primary: #0a0a0f;
            --bg-secondary: #111115;
            --bg-tertiary: #1a1a20;
            --bg-card: #0f0f14;
            --bg-terminal: #0a0a0c;
            --text-primary: #eaeef2;
            --text-secondary: #8a8f99;
            --text-muted: #5a5f6e;
            --accent: #3b82f6;
            --accent-hover: #2563eb;
            --accent-glow: rgba(59, 130, 246, 0.3);
            --danger: #ef4444;
            --danger-hover: #dc2626;
            --border: #2a2a35;
            --border-light: #2a2a35;
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            --terminal-text: #10b981;
            --transition: all 0.2s ease;
        }

        @media (prefers-color-scheme: light) {
            :root {
                --bg-primary: #f8fafc;
                --bg-secondary: #f1f5f9;
                --bg-tertiary: #e2e8f0;
                --bg-card: #ffffff;
                --bg-terminal: #1e1e24;
                --text-primary: #0f172a;
                --text-secondary: #475569;
                --text-muted: #94a3b8;
                --border: #e2e8f0;
                --border-light: #cbd5e1;
                --accent: #3b82f6;
                --accent-hover: #2563eb;
                --danger: #ef4444;
                --danger-hover: #dc2626;
                --terminal-text: #10b981;
            }
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', monospace;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.5;
        }

        .header {
            background: rgba(var(--bg-secondary-rgb), 0.8);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border);
            padding: 0.75rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .logo h1 {
            font-size: 1.25rem;
            font-weight: 600;
            background: linear-gradient(135deg, #fff, var(--accent));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }

        .nav {
            display: flex;
            gap: 0.5rem;
            background: var(--bg-tertiary);
            padding: 0.25rem;
            border-radius: 12px;
        }

        .nav-link {
            padding: 0.5rem 1rem;
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 0.875rem;
            font-weight: 500;
            border-radius: 8px;
            transition: var(--transition);
            cursor: pointer;
        }

        .nav-link:hover {
            color: var(--text-primary);
            background: var(--bg-card);
        }

        .nav-link.active {
            background: var(--accent);
            color: white;
        }

        .status-badge {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.375rem 0.875rem;
            background: var(--bg-tertiary);
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 500;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--success);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 1rem;
            height: calc(100vh - 60px);
            display: flex;
            flex-direction: column;
        }

        .dashboard-page {
            height: 100%;
            overflow-y: auto;
        }

        .dashboard-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin-bottom: 1rem;
        }

        .stat-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 0.875rem 1rem;
            transition: var(--transition);
        }

        .stat-card:hover {
            border-color: var(--accent);
        }

        .stat-title {
            font-size: 0.65rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-bottom: 0.25rem;
        }

        .stat-value {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
        }

        .sessions-list, .files-list {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 0.875rem;
            margin-bottom: 1rem;
        }

        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border);
        }

        .section-header h3 {
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text-secondary);
        }

        .session-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem;
            border-bottom: 1px solid var(--border-light);
            transition: var(--transition);
            cursor: pointer;
        }

        .session-item:last-child {
            border-bottom: none;
        }

        .session-item:hover {
            background: var(--bg-tertiary);
        }

        .session-id {
            font-family: monospace;
            font-size: 0.7rem;
        }

        .session-date {
            font-size: 0.65rem;
            color: var(--text-muted);
        }

        .file-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem;
            border-bottom: 1px solid var(--border-light);
        }

        .file-name {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            cursor: pointer;
            color: var(--accent);
        }

        .file-name:hover {
            text-decoration: underline;
        }

        .file-icon {
            width: 20px;
            height: 20px;
            object-fit: contain;
        }

        .download-btn {
            background: var(--accent-soft);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 0.2rem 0.6rem;
            font-size: 0.65rem;
            cursor: pointer;
            color: var(--text-secondary);
            transition: var(--transition);
        }

        .download-btn:hover {
            background: var(--accent);
            color: white;
            border-color: var(--accent);
        }

        .chat-page {
            height: 100%;
            display: flex;
            flex-direction: column;
            position: relative;
        }

        .chat-messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 0;
            margin-bottom: 0;
        }

        .chat-messages {
            padding: 1rem;
        }

        .message {
            margin-bottom: 0.75rem;
            display: flex;
            gap: 0.75rem;
        }

        .message.user {
            justify-content: flex-end;
        }

        .message.user .message-content {
            background: var(--accent);
            color: white;
            border-radius: 18px 18px 4px 18px;
        }

        .message.ai {
            justify-content: flex-start;
        }

        .message.ai .message-content {
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 18px 18px 18px 4px;
        }

        .message-content {
            max-width: 80%;
            padding: 0.7rem 1rem;
            font-size: 0.875rem;
            line-height: 1.5;
            word-wrap: break-word;
            overflow-wrap: break-word;
            white-space: pre-wrap;
        }

        .message-content pre {
            background: var(--bg-primary);
            padding: 0.5rem;
            border-radius: 10px;
            overflow-x: auto;
            margin: 0.5rem 0;
            font-size: 0.7rem;
        }

        .file-delivery {
            display: flex;
            gap: 0.75rem;
            margin-bottom: 0.75rem;
            justify-content: flex-start;
        }

        .file-delivery-content {
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 18px 18px 18px 4px;
            padding: 0.7rem 1rem;
            max-width: 80%;
        }

        .file-delivery-header {
            font-size: 0.7rem;
            color: var(--text-muted);
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .file-list {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .file-delivery-item {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.5rem;
            background: var(--bg-card);
            border-radius: 12px;
            border: 1px solid var(--border-light);
            transition: var(--transition);
        }

        .file-delivery-item:hover {
            border-color: var(--accent);
            background: var(--accent-soft);
        }

        .file-delivery-icon {
            width: 24px;
            height: 24px;
            object-fit: contain;
        }

        .file-info {
            flex: 1;
        }

        .file-name-link {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-family: monospace;
            font-size: 0.8rem;
            color: var(--accent);
            text-decoration: none;
            font-weight: 500;
        }

        .file-name-link:hover {
            text-decoration: underline;
        }

        .file-size {
            font-size: 0.6rem;
            color: var(--text-muted);
            margin-top: 0.125rem;
        }

        .download-single-btn {
            background: var(--accent);
            border: none;
            border-radius: 8px;
            padding: 0.25rem 0.75rem;
            color: white;
            font-size: 0.65rem;
            cursor: pointer;
            transition: var(--transition);
        }

        .download-single-btn:hover {
            background: var(--accent-hover);
            transform: scale(0.98);
        }

        .download-folder-btn {
            background: var(--accent);
            border: none;
            border-radius: 8px;
            padding: 0.25rem 0.75rem;
            color: white;
            font-size: 0.65rem;
            cursor: pointer;
            transition: var(--transition);
        }

        .download-folder-btn:hover {
            background: var(--accent-hover);
            transform: scale(0.98);
        }

        .download-all-btn {
            background: var(--accent-soft);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.3rem 1rem;
            color: var(--text-primary);
            font-size: 0.7rem;
            cursor: pointer;
            transition: var(--transition);
            margin-top: 0.5rem;
            width: fit-content;
        }

        .download-all-btn:hover {
            background: var(--accent);
            color: white;
            border-color: var(--accent);
        }

        .chat-input-area {
            position: sticky;
            bottom: 0;
            padding: 1rem;
            border-top: 1px solid var(--border);
            background: var(--bg-card);
            flex-shrink: 0;
            margin-top: auto;
        }

        .input-wrapper {
            display: flex;
            gap: 0.75rem;
            align-items: flex-end;
            background: var(--bg-tertiary);
            border-radius: 20px;
            padding: 0.25rem;
            border: 1px solid var(--border);
            transition: var(--transition);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .input-wrapper:focus-within {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--accent-glow);
            transform: translateY(-1px);
        }

        .chat-input {
            flex: 1;
            background: transparent;
            border: none;
            padding: 0.7rem 1rem;
            color: var(--text-primary);
            font-family: inherit;
            font-size: 0.875rem;
            resize: none;
            outline: none;
            line-height: 1.4;
        }

        .chat-input::placeholder {
            color: var(--text-muted);
            font-size: 0.8rem;
        }

        .send-btn {
            background: var(--accent);
            border: none;
            border-radius: 16px;
            padding: 0.6rem 1.25rem;
            color: white;
            font-weight: 500;
            font-size: 0.875rem;
            cursor: pointer;
            transition: var(--transition);
            margin: 0.25rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .send-btn:hover {
            background: var(--accent-hover);
            transform: scale(0.98);
        }

        .send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        .send-btn.stop {
            background: var(--danger);
        }

        .send-btn.stop:hover {
            background: var(--danger-hover);
        }

        .send-icon {
            font-size: 1rem;
        }

        .streaming-cursor {
            display: inline-block;
            width: 2px;
            height: 1em;
            background: var(--accent);
            margin-left: 2px;
            animation: blink 1s infinite;
            vertical-align: middle;
        }

        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }

        .thinking-indicator {
            display: flex;
            gap: 4px;
            padding: 0.5rem;
        }

        .thinking-indicator span {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--accent);
            animation: bounce 1.4s infinite ease-in-out both;
        }

        .thinking-indicator span:nth-child(1) { animation-delay: -0.32s; }
        .thinking-indicator span:nth-child(2) { animation-delay: -0.16s; }

        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }

        .settings-page {
            height: 100%;
            overflow-y: auto;
        }

        .settings-section {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 0.875rem;
            margin-bottom: 1rem;
        }

        .settings-title {
            font-size: 0.8rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border);
        }

        .setting-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid var(--border-light);
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .setting-item:last-child {
            border-bottom: none;
        }

        .setting-label {
            font-size: 0.8rem;
            font-weight: 500;
        }

        .btn {
            padding: 0.375rem 0.875rem;
            border-radius: 8px;
            border: none;
            font-size: 0.7rem;
            font-weight: 500;
            cursor: pointer;
            transition: var(--transition);
        }

        .btn-primary {
            background: var(--accent);
            color: white;
        }

        .btn-primary:hover {
            background: var(--accent-hover);
        }

        .btn-danger {
            background: var(--error);
            color: white;
        }

        .btn-secondary {
            background: var(--bg-tertiary);
            color: var(--text-secondary);
            border: 1px solid var(--border);
        }

        select, input {
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.4rem 0.7rem;
            color: var(--text-primary);
            font-size: 0.8rem;
            font-family: inherit;
        }

        .terminal {
            background: var(--bg-terminal);
            border-radius: 16px;
            overflow: hidden;
            margin-top: 0.5rem;
            border: 1px solid var(--border);
        }

        .terminal-header {
            background: var(--bg-tertiary);
            padding: 0.5rem 1rem;
            font-size: 0.7rem;
            color: var(--text-muted);
            border-bottom: 1px solid var(--border);
        }

        .terminal-body {
            padding: 0.8rem;
            font-family: monospace;
            font-size: 0.75rem;
            height: 200px;
            overflow-y: auto;
            background: var(--bg-terminal);
        }

        .terminal-line {
            color: var(--terminal-text);
            margin-bottom: 0.2rem;
            white-space: pre-wrap;
            word-break: break-all;
        }

        .terminal-input-line {
            display: flex;
            gap: 0.5rem;
            padding: 0.5rem;
            border-top: 1px solid var(--border);
            background: var(--bg-terminal);
        }

        .terminal-prompt {
            color: var(--terminal-text);
            font-size: 0.75rem;
        }

        .terminal-input {
            background: transparent;
            border: none;
            color: var(--terminal-text);
            flex: 1;
            font-family: monospace;
            font-size: 0.75rem;
            outline: none;
        }

        .hidden {
            display: none;
        }

        .flex {
            display: flex;
            gap: 0.5rem;
        }

        .text-muted {
            color: var(--text-muted);
            font-size: 0.65rem;
        }

        ::-webkit-scrollbar {
            width: 4px;
            height: 4px;
        }

        ::-webkit-scrollbar-track {
            background: var(--bg-tertiary);
            border-radius: 2px;
        }

        ::-webkit-scrollbar-thumb {
            background: var(--border);
            border-radius: 2px;
        }

        @media (max-width: 768px) {
            .container { padding: 0.5rem; height: calc(100vh - 56px); }
            .nav { display: none; }
            .message-content { max-width: 85%; font-size: 0.8rem; }
            .dashboard-stats { grid-template-columns: 1fr 1fr; gap: 0.5rem; }
            .stat-value { font-size: 1rem; }
            .header { padding: 0.5rem 1rem; }
            .chat-input { font-size: 0.8rem; }
            .send-btn { padding: 0.5rem 1rem; }
            .input-wrapper { border-radius: 16px; }
            .file-delivery-content { max-width: 90%; }
            .file-delivery-item { flex-wrap: wrap; }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="logo">
            <h1>ZynoxAI</h1>
        </div>
        <nav class="nav">
            <a class="nav-link active" data-page="dashboard">Dashboard</a>
            <a class="nav-link" data-page="chat">Chat</a>
            <a class="nav-link" data-page="settings">Settings</a>
        </nav>
        <div class="status-badge">
            <div class="status-dot"></div>
            <span id="status-text">Ready</span>
        </div>
    </header>

    <main class="container">
        <div id="dashboard-page" class="dashboard-page">
            <div class="dashboard-stats">
                <div class="stat-card"><div class="stat-title">Status</div><div class="stat-value" id="stat-status">---</div></div>
                <div class="stat-card"><div class="stat-title">Provider</div><div class="stat-value" id="stat-provider">-</div></div>
                <div class="stat-card"><div class="stat-title">Environment</div><div class="stat-value" id="stat-env">-</div></div>
                <div class="stat-card"><div class="stat-title">Package Manager</div><div class="stat-value" id="stat-pm">-</div></div>
            </div>

            <div class="sessions-list">
                <div class="section-header"><h3>Saved Sessions</h3><div class="flex"><button class="btn btn-primary" onclick="newSession()">New</button><button class="btn btn-secondary" onclick="clearMemory()">Clear</button><button class="btn btn-secondary" onclick="loadSessions()">↻</button></div></div>
                <div id="sessions-container">Loading...</div>
            </div>

            <div class="files-list">
                <div class="section-header"><h3>Created Files</h3><button class="btn btn-primary" onclick="downloadAllFiles()" style="font-size:0.65rem;">Download All</button></div>
                <div id="created-files-container">Loading...</div>
            </div>

            <div class="terminal">
                <div class="terminal-header">terminal</div>
                <div class="terminal-body" id="terminal-body"><div class="terminal-line">ZynoxAI Terminal v4.8.15</div><div class="terminal-line">Type commands below (cd, ls, pwd, etc.)</div><div class="terminal-line">---</div></div>
                <div class="terminal-input-line"><span class="terminal-prompt">$</span><input type="text" class="terminal-input" id="terminal-input" placeholder="cd .., ls -la, pwd..."></div>
            </div>
        </div>

        <div id="chat-page" class="chat-page hidden">
            <div class="chat-messages-container"><div class="chat-messages" id="chat-messages"><div class="message ai"><div class="message-content">ZynoxAI ready.<br><br>Examples:<br>• "create a python file called hello.py with print('Hello')"<br>• "find abc.txt and read it"<br>• "list all files"</div></div></div></div>
            <div class="chat-input-area"><div class="input-wrapper"><textarea class="chat-input" id="chat-input" placeholder="Describe what you want..." rows="1"></textarea><button class="send-btn" id="send-btn" onclick="sendMessage()"><span class="send-icon">→</span></button></div></div>
        </div>

        <div id="settings-page" class="settings-page hidden">
            <div class="settings-section"><div class="settings-title">AI Provider</div><div class="setting-item"><span class="setting-label">Default Provider</span><select id="provider-select"><option value="openai">OpenAI</option><option value="gemini">Gemini</option><option value="grok">Grok</option><option value="deepseek">DeepSeek</option></select></div><div class="setting-item"><span class="setting-label">Default Model</span><input type="text" id="model-input" placeholder="e.g., deepseek-chat"></div><div style="margin-top: 0.75rem;"><button class="btn btn-primary" onclick="saveSettings()">Save</button></div></div>
            <div class="settings-section"><div class="settings-title">API Keys</div><div id="api-keys-container"></div><div class="text-muted" style="margin-top: 0.75rem; padding: 0.5rem;">Keys stored locally</div></div>
            <div class="settings-section"><div class="settings-title">About</div><div class="setting-item"><span>Version</span><span>4.8.15</span></div><div class="setting-item"><span>Author</span><span>Buge Studio</span></div><div class="setting-item"><span>GitHub</span><a href="https://github.com/BugeStudioTeam/Zynox" style="color: var(--accent); text-decoration: none;">repo</a></div></div>
        </div>
    </main>

    <script>
        const API_BASE = '';
        let currentDirectory = '';
        let terminalHistory = [];
        let historyIndex = -1;
        let isStreaming = false;
        let currentAbortController = null;

        const ICONS = {
            folder: '/static/folder.png',
            zip: '/static/zip.png',
            file: '/static/file.png'
        };

        function getFileIcon(filename, isDir) {
            if (isDir) return ICONS.folder;
            if (filename && filename.endsWith('.zip')) return ICONS.zip;
            return ICONS.file;
        }

        async function getCurrentDirectory() {
            try {
                const res = await fetch(`${API_BASE}/api/pwd`);
                const data = await res.json();
                currentDirectory = data.cwd;
                return currentDirectory;
            } catch(e) {
                return '';
            }
        }

        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.addEventListener('input', function() { this.style.height = 'auto'; this.style.height = Math.min(this.scrollHeight, 120) + 'px'; });
            chatInput.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } });
        }

        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => { const page = link.getAttribute('data-page'); showPage(page); document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active')); link.classList.add('active'); });
        });

        function showPage(page) {
            document.getElementById('dashboard-page').classList.add('hidden');
            document.getElementById('chat-page').classList.add('hidden');
            document.getElementById('settings-page').classList.add('hidden');
            document.getElementById(`${page}-page`).classList.remove('hidden');
            if (page === 'dashboard') loadDashboard();
            if (page === 'settings') loadSettings();
        }

        async function loadDashboard() {
            try { const res = await fetch(`${API_BASE}/api/status`); const data = await res.json(); document.getElementById('stat-status').innerHTML = '<span style="color: #10b981;">● Running</span>'; document.getElementById('stat-provider').innerText = data.provider || '-'; document.getElementById('stat-env').innerText = data.environment || '-'; document.getElementById('stat-pm').innerText = data.package_manager || '-'; } catch(e) { console.error(e); }
            await loadSessions();
            await loadCreatedFiles();
            await getCurrentDirectory();
        }

        async function loadSessions() {
            try { const res = await fetch(`${API_BASE}/api/sessions`); const data = await res.json(); const container = document.getElementById('sessions-container'); if (data.sessions && data.sessions.length > 0) { container.innerHTML = data.sessions.map(s => `<div class="session-item"><div onclick="loadSession('${s.id}')"><div class="session-id">${escapeHtml(s.id)}</div><div class="session-date">${escapeHtml(s.created || 'Unknown')} | ${s.message_count}</div></div><div class="flex"><button class="btn btn-secondary" onclick="loadSession('${s.id}')">Load</button><button class="btn btn-danger" onclick="deleteSession('${s.id}')">Del</button></div></div>`).join(''); } else { container.innerHTML = '<div class="session-item">No sessions</div>'; } } catch(e) { console.error(e); }
        }

        async function loadCreatedFiles() {
            try { const res = await fetch(`${API_BASE}/api/files/list`); const data = await res.json(); const container = document.getElementById('created-files-container'); if (data.files && data.files.length > 0) { let filesHtml = ''; data.files.forEach(file => { const isDir = file.is_dir; const iconUrl = getFileIcon(file.name, isDir); filesHtml += `<div class="file-item"><span class="file-name" onclick="window.open('/api/files/download?path=${encodeURIComponent(file.path)}', '_blank')"><img src="${iconUrl}" class="file-icon" alt="">${escapeHtml(file.name)}</span><button class="download-btn" onclick="window.open('/api/files/download?path=${encodeURIComponent(file.path)}', '_blank')">Download</button></div>`; }); container.innerHTML = filesHtml; } else { container.innerHTML = '<div class="file-item">No files created yet</div>'; } } catch(e) { console.error(e); }
        }

        async function downloadAllFiles() { window.open(`${API_BASE}/api/files/download-all`, '_blank'); }

        async function loadSettings() {
            try { const res = await fetch(`${API_BASE}/api/config`); const data = await res.json(); document.getElementById('provider-select').value = data.default_provider || 'openai'; document.getElementById('model-input').value = data.default_model || ''; const container = document.getElementById('api-keys-container'); const providers = ['openai', 'gemini', 'grok', 'deepseek']; container.innerHTML = providers.map(p => { const hasKey = data.api_keys && data.api_keys.includes(p); return `<div class="setting-item"><span class="setting-label">${p.toUpperCase()}</span><div class="flex"><input type="password" id="key-${p}" placeholder="API key" style="width: 180px;"><button class="btn btn-primary" onclick="updateApiKey('${p}')">Save</button><span class="text-muted">${hasKey ? '✓' : '—'}</span></div></div>`; }).join(''); } catch(e) { console.error(e); }
        }

        async function saveSettings() { const provider = document.getElementById('provider-select').value; const model = document.getElementById('model-input').value; try { await fetch(`${API_BASE}/api/config`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ default_provider: provider, default_model: model }) }); alert('Saved'); loadStatus(); } catch(e) { alert('Error: ' + e.message); } }
        async function updateApiKey(provider) { const key = document.getElementById(`key-${provider}`).value; if (!key) return; const apiKeys = {}; apiKeys[provider] = key; try { await fetch(`${API_BASE}/api/config`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ api_keys: apiKeys }) }); alert(`${provider.toUpperCase()} key saved`); document.getElementById(`key-${provider}`).value = ''; loadSettings(); } catch(e) { alert('Error: ' + e.message); } }
        async function loadSession(sessionId) { try { await fetch(`${API_BASE}/api/sessions/load`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ session_id: sessionId }) }); alert('Session loaded'); loadSessions(); } catch(e) { alert('Error: ' + e.message); } }
        async function deleteSession(sessionId) { if (!confirm('Delete?')) return; try { await fetch(`${API_BASE}/api/sessions/delete`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ session_id: sessionId }) }); alert('Deleted'); loadSessions(); } catch(e) { alert('Error: ' + e.message); } }
        async function newSession() { try { await fetch(`${API_BASE}/api/sessions/new`, { method: 'POST' }); alert('New session'); loadSessions(); } catch(e) { alert('Error: ' + e.message); } }
        async function clearMemory() { if (!confirm('Clear memory?')) return; try { await fetch(`${API_BASE}/api/sessions/clear`, { method: 'POST' }); alert('Cleared'); loadSessions(); } catch(e) { alert('Error: ' + e.message); } }
        async function clearCreatedFiles() { if (!confirm('Delete all files?')) return; try { await fetch(`${API_BASE}/api/clear-created`, { method: 'POST' }); alert('Cleared'); loadCreatedFiles(); } catch(e) { alert('Error: ' + e.message); } }

        function escapeHtml(text) { if (!text) return ''; return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
        function formatFileSize(bytes) { if (bytes === 0) return '0 B'; const k = 1024; const sizes = ['B', 'KB', 'MB', 'GB']; const i = Math.floor(Math.log(bytes) / Math.log(k)); return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]; }

        async function stopTask() {
            if (!isStreaming) return;
            
            try {
                const response = await fetch(`${API_BASE}/api/stop`, { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    addMessage('ai', '⚠️ Task stopped by user');
                    if (currentAbortController) {
                        currentAbortController.abort();
                        currentAbortController = null;
                    }
                    isStreaming = false;
                    const sendBtn = document.getElementById('send-btn');
                    sendBtn.disabled = false;
                    sendBtn.classList.remove('stop');
                    sendBtn.innerHTML = '<span class="send-icon">→</span>';
                    sendBtn.onclick = sendMessage;
                    const thinkingDiv = document.getElementById('thinking-indicator');
                    if (thinkingDiv) thinkingDiv.remove();
                }
            } catch(e) {
                console.error('Stop failed:', e);
            }
        }

        async function executeCommand(cmd) {
            const termBody = document.getElementById('terminal-body');
            termBody.innerHTML += `<div class="terminal-line">$ ${escapeHtml(cmd)}</div>`;
            termBody.scrollTop = termBody.scrollHeight;
            
            if (cmd.trim().startsWith('cd ')) {
                const path = cmd.trim().substring(3);
                try {
                    const res = await fetch(`${API_BASE}/api/cd`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ path: path })
                    });
                    const data = await res.json();
                    if (data.success) {
                        currentDirectory = data.cwd;
                        termBody.innerHTML += `<div class="terminal-line">Changed to: ${escapeHtml(data.cwd)}</div>`;
                    } else {
                        termBody.innerHTML += `<div class="terminal-line" style="color: #f59e0b;">Error: ${escapeHtml(data.error || 'Failed to change directory')}</div>`;
                    }
                } catch(e) {
                    termBody.innerHTML += `<div class="terminal-line" style="color: #ef4444;">Error: ${escapeHtml(e.message)}</div>`;
                }
                termBody.scrollTop = termBody.scrollHeight;
                terminalHistory.push(cmd);
                historyIndex = terminalHistory.length;
                return;
            }

            let cwd = currentDirectory;
            if (!cwd) {
                const pwdRes = await fetch(`${API_BASE}/api/pwd`);
                const pwdData = await pwdRes.json();
                cwd = pwdData.cwd;
                currentDirectory = cwd;
            }

            try {
                const res = await fetch(`${API_BASE}/api/command`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: cmd, cwd: cwd })
                });
                const data = await res.json();
                if (data.stdout) termBody.innerHTML += `<div class="terminal-line">${escapeHtml(data.stdout)}</div>`;
                if (data.stderr) termBody.innerHTML += `<div class="terminal-line" style="color: #f59e0b;">${escapeHtml(data.stderr)}</div>`;
                termBody.scrollTop = termBody.scrollHeight;
                await loadCreatedFiles();
            } catch(e) {
                termBody.innerHTML += `<div class="terminal-line" style="color: #ef4444;">Error: ${escapeHtml(e.message)}</div>`;
            }
            
            terminalHistory.push(cmd);
            historyIndex = terminalHistory.length;
        }

        const terminalInput = document.getElementById('terminal-input');
        if (terminalInput) {
            terminalInput.addEventListener('keypress', async (e) => {
                if (e.key === 'Enter') {
                    const cmd = terminalInput.value.trim();
                    if (cmd) {
                        await executeCommand(cmd);
                        terminalInput.value = '';
                    }
                }
            });
            terminalInput.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    if (historyIndex > 0) {
                        historyIndex--;
                        terminalInput.value = terminalHistory[historyIndex];
                    }
                } else if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    if (historyIndex < terminalHistory.length - 1) {
                        historyIndex++;
                        terminalInput.value = terminalHistory[historyIndex];
                    } else {
                        historyIndex = terminalHistory.length;
                        terminalInput.value = '';
                    }
                }
            });
        }

        async function sendMessage() {
            const input = document.getElementById('chat-input');
            const message = input.value.trim();
            const sendBtn = document.getElementById('send-btn');
            
            if (!message || isStreaming) return;

            addMessage('user', message);
            input.value = '';
            input.style.height = 'auto';
            sendBtn.disabled = false;
            sendBtn.classList.add('stop');
            sendBtn.innerHTML = '<span class="send-icon">⏹</span>';
            sendBtn.onclick = stopTask;
            isStreaming = true;

            const messagesDiv = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ai';
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            const textSpan = document.createElement('span');
            const cursorSpan = document.createElement('span');
            cursorSpan.className = 'streaming-cursor';
            contentDiv.appendChild(textSpan);
            contentDiv.appendChild(cursorSpan);
            messageDiv.appendChild(contentDiv);
            messagesDiv.appendChild(messageDiv);
            
            let fullText = '';
            const container = document.querySelector('.chat-messages-container');
            if (container) container.scrollTop = container.scrollHeight;

            currentAbortController = new AbortController();

            try {
                const response = await fetch(`${API_BASE}/api/chat/stream`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message }),
                    signal: currentAbortController.signal
                });

                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    
                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\\n');
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const dataStr = line.slice(6);
                            if (dataStr === '[DONE]') continue;
                            
                            try {
                                const parsed = JSON.parse(dataStr);
                                if (parsed.text) {
                                    fullText += parsed.text;
                                    textSpan.innerHTML = escapeHtml(fullText).replace(/\\n/g, '<br>');
                                    if (container) container.scrollTop = container.scrollHeight;
                                }
                                if (parsed.complete) {
                                    cursorSpan.remove();
                                    if (parsed.success) {
                                        await loadCreatedFiles();
                                    }
                                }
                                if (parsed.error) {
                                    textSpan.innerHTML = 'Error: ' + escapeHtml(parsed.error);
                                    cursorSpan.remove();
                                }
                                if (parsed.created_files && parsed.created_files.length > 0) {
                                    addFileDeliveryMessage(parsed.created_files);
                                }
                            } catch(e) {
                                // Ignore parse errors
                            }
                        }
                    }
                }
            } catch(e) {
                if (e.name === 'AbortError') {
                    textSpan.innerHTML = '⚠️ Task stopped by user';
                } else {
                    textSpan.innerHTML = 'Error: ' + escapeHtml(e.message);
                }
                cursorSpan.remove();
            } finally {
                sendBtn.disabled = false;
                sendBtn.classList.remove('stop');
                sendBtn.innerHTML = '<span class="send-icon">→</span>';
                sendBtn.onclick = sendMessage;
                isStreaming = false;
                currentAbortController = null;
            }
        }

        function addFileDeliveryMessage(files) {
            const messagesDiv = document.getElementById('chat-messages');
            const deliveryDiv = document.createElement('div');
            deliveryDiv.className = 'file-delivery';
            let filesHtml = '<div class="file-delivery-content"><div class="file-delivery-header">Files Created</div><div class="file-list">';
            files.forEach(file => {
                const isDir = file.is_dir;
                const iconUrl = getFileIcon(file.name, isDir);
                const sizeText = file.size ? formatFileSize(file.size) : '';
                const downloadUrl = isDir ? `/api/folder/download?path=${encodeURIComponent(file.path)}` : `/api/files/download?path=${encodeURIComponent(file.path)}`;
                filesHtml += `<div class="file-delivery-item"><img src="${iconUrl}" class="file-delivery-icon" alt=""><div class="file-info"><a href="#" class="file-name-link" onclick="window.open('${downloadUrl}', '_blank'); return false;">${escapeHtml(file.name)}</a>${sizeText ? `<div class="file-size">${sizeText}</div>` : ''}</div><button class="${isDir ? 'download-folder-btn' : 'download-single-btn'}" onclick="window.open('${downloadUrl}', '_blank')">Download</button></div>`;
            });
            if (files.length > 1) filesHtml += `<button class="download-all-btn" onclick="downloadAllFiles()">Download All (${files.length} items)</button>`;
            filesHtml += '</div></div>';
            deliveryDiv.innerHTML = filesHtml;
            messagesDiv.appendChild(deliveryDiv);
            const container = document.querySelector('.chat-messages-container');
            if (container) container.scrollTop = container.scrollHeight;
        }

        function addMessage(role, content) {
            const messagesDiv = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;
            const escapedContent = escapeHtml(content).replace(/\\n/g, '<br>');
            messageDiv.innerHTML = `<div class="message-content">${escapedContent}</div>`;
            messagesDiv.appendChild(messageDiv);
            const container = document.querySelector('.chat-messages-container');
            if (container) container.scrollTop = container.scrollHeight;
        }

        async function loadStatus() { try { const res = await fetch(`${API_BASE}/api/status`); const data = await res.json(); document.getElementById('status-text').innerText = data.provider || 'Ready'; } catch(e) {} }

        loadDashboard();
        loadStatus();
    </script>
</body>
</html>
'''

def create_app():
    """Create Flask app with full ZynoxAI integration"""
    global zynox, config, session_manager, file_manager, global_cwd, stop_task_flag
    
    # Initialize ZynoxAI components
    zynox = ZynoxAI()
    config = Config()
    session_manager = SessionManager()
    file_manager = FileManager()
    global_cwd = os.path.expanduser("~")
    stop_task_flag = False
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'zynoxai-secret'
    
    @app.route('/')
    def index():
        return INDEX_HTML
    
    @app.route('/dashboard')
    def dashboard():
        return INDEX_HTML
    
    @app.route('/chat')
    def chat():
        return INDEX_HTML
    
    @app.route('/settings')
    def settings():
        return INDEX_HTML
    
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        return send_file(os.path.join(STATIC_DIR, filename))
    
    @app.route('/api/pwd')
    def api_pwd():
        global global_cwd
        return jsonify({'cwd': global_cwd})
    
    @app.route('/api/cd', methods=['POST'])
    def api_cd():
        global global_cwd
        data = request.json
        path = data.get('path', '')
        
        try:
            if path == '~' or path == '':
                new_path = os.path.expanduser("~")
            elif path.startswith('/'):
                new_path = path
            else:
                new_path = os.path.normpath(os.path.join(global_cwd, path))
            
            if os.path.exists(new_path) and os.path.isdir(new_path):
                global_cwd = new_path
                return jsonify({'success': True, 'cwd': global_cwd})
            else:
                return jsonify({'success': False, 'error': 'Directory not found'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/api/status')
    def api_status():
        return jsonify({
            'status': 'running',
            'provider': zynox.current_provider,
            'environment': zynox.environment,
            'package_manager': zynox.package_manager,
            'version': '4.8.15'
        })
    
    @app.route('/api/stop', methods=['POST'])
    def api_stop():
        global stop_task_flag
        stop_task_flag = True
        return jsonify({'success': True})
    
    @app.route('/api/files/list')
    def api_files_list():
        create_dir = Config.get_create_dir()
        files = []
        
        def scan_directory(path, relative_path=""):
            try:
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    rel_path = os.path.join(relative_path, item) if relative_path else item
                    if os.path.isdir(item_path):
                        files.append({'name': item, 'path': rel_path, 'is_dir': True, 'size': 0})
                        scan_directory(item_path, rel_path)
                    else:
                        files.append({'name': item, 'path': rel_path, 'is_dir': False, 'size': os.path.getsize(item_path)})
            except Exception as e:
                print(f"Error scanning: {e}")
        
        if os.path.exists(create_dir):
            scan_directory(create_dir)
        
        return jsonify({'files': files})
    
    @app.route('/api/files/download')
    def api_file_download():
        filepath = request.args.get('path', '')
        create_dir = Config.get_create_dir()
        full_path = os.path.join(create_dir, filepath)
        
        if not os.path.exists(full_path) or os.path.isdir(full_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(full_path, as_attachment=True, download_name=os.path.basename(full_path))
    
    @app.route('/api/folder/download')
    def api_folder_download():
        folderpath = request.args.get('path', '')
        create_dir = Config.get_create_dir()
        full_path = os.path.join(create_dir, folderpath)
        
        if not os.path.exists(full_path) or not os.path.isdir(full_path):
            return jsonify({'error': 'Folder not found'}), 404
        
        zip_buffer = io.BytesIO()
        folder_name = os.path.basename(full_path)
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(full_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(full_path))
                    zip_file.write(file_path, arcname)
        
        zip_buffer.seek(0)
        return send_file(zip_buffer, as_attachment=True, download_name=f'{folder_name}.zip', mimetype='application/zip')
    
    @app.route('/api/files/download-all')
    def api_files_download_all():
        create_dir = Config.get_create_dir()
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            if os.path.exists(create_dir):
                for root, dirs, files in os.walk(create_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, create_dir)
                        zip_file.write(file_path, arcname)
        
        zip_buffer.seek(0)
        return send_file(zip_buffer, as_attachment=True, download_name='zynoxai_created_files.zip', mimetype='application/zip')
    
    @app.route('/api/sessions')
    def api_sessions():
        sessions = session_manager.list_sessions()
        return jsonify({'sessions': sessions})
    
    @app.route('/api/created')
    def api_created():
        files = file_manager.list_created_files()
        return jsonify({'files': files})
    
    @app.route('/api/config', methods=['GET', 'POST'])
    def api_config():
        if request.method == 'POST':
            data = request.json
            if 'default_provider' in data:
                config.set_default_provider(data['default_provider'])
                zynox.current_provider = data['default_provider']
            if 'default_model' in data:
                config.set_default_model(data['default_model'])
            if 'api_keys' in data:
                for provider, key in data['api_keys'].items():
                    if key:
                        config.set_api_key(provider, key)
            return jsonify({'success': True})
        return jsonify({
            'default_provider': config.get_default_provider(),
            'default_model': config.get_default_model(),
            'api_keys': list(config.data.get('api_keys', {}).keys())
        })
    
    @app.route('/api/sessions/new', methods=['POST'])
    def api_new_session():
        session_manager.new_session()
        return jsonify({'success': True})
    
    @app.route('/api/sessions/clear', methods=['POST'])
    def api_clear_memory():
        session_manager.clear_memory()
        return jsonify({'success': True})
    
    @app.route('/api/sessions/load', methods=['POST'])
    def api_load_session():
        data = request.json
        session_id = data.get('session_id')
        if session_manager.load_session(session_id):
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Session not found'})
    
    @app.route('/api/sessions/delete', methods=['POST'])
    def api_delete_session():
        data = request.json
        session_id = data.get('session_id')
        if session_manager.delete_session(session_id):
            return jsonify({'success': True})
        return jsonify({'success': False})
    
    @app.route('/api/clear-created', methods=['POST'])
    def api_clear_created():
        file_manager.clear_created_files()
        return jsonify({'success': True})
    
    @app.route('/api/command', methods=['POST'])
    def api_command():
        global global_cwd
        data = request.json
        command = data.get('command', '')
        cwd = data.get('cwd', global_cwd)
        
        if command.strip().startswith('zynox'):
            return jsonify({'stdout': 'Use standard Linux commands.', 'stderr': '', 'returncode': 0})
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, executable='/bin/bash', cwd=cwd)
            return jsonify({'stdout': result.stdout, 'stderr': result.stderr, 'returncode': result.returncode})
        except subprocess.TimeoutExpired:
            return jsonify({'stderr': 'Timeout', 'returncode': -1})
        except Exception as e:
            return jsonify({'stderr': str(e), 'returncode': -1})
    
    # Step-by-step streaming chat endpoint with stop support
    @app.route('/api/chat/stream', methods=['POST'])
    def api_chat_stream():
        global stop_task_flag
        data = request.json
        user_msg = data.get('message', '')
        
        # Reset stop flag for new task
        stop_task_flag = False
        
        def generate():
            from ..core.executor.step_executor import StepExecutor
            
            create_dir = Config.get_create_dir()
            files_before = set()
            if os.path.exists(create_dir):
                for root, dirs, files in os.walk(create_dir):
                    for file in files:
                        rel_path = os.path.relpath(os.path.join(root, file), create_dir)
                        files_before.add(rel_path)
            
            output_queue = []
            created_files = []
            
            def callback(text, color="white"):
                output_queue.append(text)
            
            executor = StepExecutor(zynox, callback)
            
            import threading
            success = False
            exception = None
            
            def run_task():
                nonlocal success, exception
                try:
                    if not stop_task_flag:
                        success = executor.run(user_msg, ".")
                except Exception as e:
                    if "stopped" not in str(e):
                        exception = str(e)
            
            thread = threading.Thread(target=run_task)
            thread.start()
            
            while thread.is_alive():
                if stop_task_flag:
                    yield f"data: {json.dumps({'text': '\\n⚠️ Task stopped by user\\n', 'complete': True})}\n\n"
                    return
                if output_queue:
                    for line in output_queue:
                        yield f"data: {json.dumps({'text': line})}\n\n"
                    output_queue.clear()
                time.sleep(0.05)
            
            if output_queue:
                for line in output_queue:
                    yield f"data: {json.dumps({'text': line})}\n\n"
            
            if not stop_task_flag:
                if os.path.exists(create_dir):
                    for root, dirs, files in os.walk(create_dir):
                        for file in files:
                            rel_path = os.path.relpath(os.path.join(root, file), create_dir)
                            if rel_path not in files_before:
                                full_path = os.path.join(root, file)
                                created_files.append({
                                    'name': file,
                                    'path': rel_path,
                                    'size': os.path.getsize(full_path),
                                    'is_dir': False
                                })
                        for dir_name in dirs:
                            rel_path = os.path.relpath(os.path.join(root, dir_name), create_dir)
                            created_files.append({
                                'name': dir_name,
                                'path': rel_path,
                                'size': 0,
                                'is_dir': True
                            })
                
                if created_files:
                    yield f"data: {json.dumps({'created_files': created_files})}\n\n"
            
            if exception:
                yield f"data: {json.dumps({'error': exception, 'complete': True})}\n\n"
            elif stop_task_flag:
                yield f"data: {json.dumps({'complete': True, 'success': False, 'stopped': True})}\n\n"
            else:
                yield f"data: {json.dumps({'complete': True, 'success': success})}\n\n"
        
        return Response(stream_with_context(generate()), mimetype='text/event-stream')
    
    @app.route('/api/chat', methods=['POST'])
    def api_chat():
        global stop_task_flag
        stop_task_flag = False
        data = request.json
        user_msg = data.get('message', '')
        
        create_dir = Config.get_create_dir()
        files_before = set()
        folders_before = set()
        if os.path.exists(create_dir):
            for root, dirs, files in os.walk(create_dir):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), create_dir)
                    files_before.add(rel_path)
                for dir_name in dirs:
                    rel_path = os.path.relpath(os.path.join(root, dir_name), create_dir)
                    folders_before.add(rel_path)
        
        output_buffer = io.StringIO()
        
        with redirect_stdout(output_buffer):
            zynox.memory.add_message("user", user_msg)
            zynox.task_complete = False
            
            file_list = zynox.file_manager.list_files(".")
            prompt = zynox.create_prompt(user_msg, "", file_list)
            response = zynox.call_api(zynox.current_provider, prompt)
            
            if response:
                zynox.memory.add_message("assistant", response[:300])
                zynox.parse_and_execute(response, ".")
        
        result = output_buffer.getvalue()
        if not result or len(result.strip()) == 0:
            result = "Task completed"
        
        created_items = []
        if os.path.exists(create_dir):
            for root, dirs, files in os.walk(create_dir):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), create_dir)
                    if rel_path not in files_before:
                        full_path = os.path.join(root, file)
                        created_items.append({
                            'name': file,
                            'path': rel_path,
                            'size': os.path.getsize(full_path),
                            'is_dir': False
                        })
                for dir_name in dirs:
                    rel_path = os.path.relpath(os.path.join(root, dir_name), create_dir)
                    if rel_path not in folders_before:
                        created_items.append({
                            'name': dir_name,
                            'path': rel_path,
                            'size': 0,
                            'is_dir': True
                        })
        
        return jsonify({
            'response': result,
            'created_files': created_items
        })
    
    return app


def run_web_server(host='127.0.0.1', port=5000, debug=False):
    """Run web server"""
    app = create_app()
    print(f"\n[Web Server Started]")
    print(f"[Access at: http://{host}:{port}]")
    print(f"[Press Ctrl+C to stop]\n")
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    run_web_server()