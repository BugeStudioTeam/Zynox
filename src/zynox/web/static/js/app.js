// Main JavaScript for ZynoxAI Web Interface

// API endpoints
const API_BASE = '';

// Load dashboard data
async function loadDashboard() {
    try {
        const res = await fetch(`${API_BASE}/api/status`);
        const data = await res.json();
        document.getElementById('stat-status').innerHTML = '<span style="color: #00ff9d;">● Running</span>';
        document.getElementById('stat-provider').innerText = data.provider || '-';
        document.getElementById('stat-env').innerText = data.environment || '-';
        document.getElementById('stat-pm').innerText = data.package_manager || '-';
    } catch(e) { console.error(e); }

    await loadSessions();
    await loadCreatedFiles();
}

// Load sessions list
async function loadSessions() {
    try {
        const res = await fetch(`${API_BASE}/api/sessions`);
        const data = await res.json();
        const container = document.getElementById('sessions-container');
        if (data.sessions && data.sessions.length > 0) {
            container.innerHTML = data.sessions.map(s => `
                <div class="session-item">
                    <div class="session-info" onclick="loadSession('${s.id}')">
                        <div class="session-id">${s.id}</div>
                        <div class="session-date">${s.created || 'Unknown'} | ${s.message_count} messages</div>
                    </div>
                    <button class="btn btn-secondary" onclick="event.stopPropagation(); deleteSession('${s.id}')">Delete</button>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<div class="session-item">No saved sessions</div>';
        }
    } catch(e) { console.error(e); }
}

// Load created files
async function loadCreatedFiles() {
    try {
        const res = await fetch(`${API_BASE}/api/created`);
        const data = await res.json();
        const container = document.getElementById('created-files-container');
        if (data.files && data.files !== 'No files created yet') {
            container.innerHTML = `<pre style="white-space: pre-wrap; padding: 12px;">${data.files}</pre>`;
        } else {
            container.innerHTML = '<div class="session-item">No files created yet</div>';
        }
    } catch(e) { console.error(e); }
}

// Load settings
async function loadSettings() {
    try {
        const res = await fetch(`${API_BASE}/api/config`);
        const data = await res.json();
        document.getElementById('provider-select').value = data.default_provider || 'openai';
        document.getElementById('model-input').value = data.default_model || '';

        const container = document.getElementById('api-keys-container');
        const providers = ['openai', 'gemini', 'grok', 'deepseek'];
        container.innerHTML = providers.map(p => `
            <div class="setting-item">
                <span>${p.toUpperCase()} API Key</span>
                <div>
                    <input type="password" id="key-${p}" placeholder="Enter ${p} API key">
                    <button class="btn btn-primary" onclick="updateApiKey('${p}')">Save</button>
                </div>
            </div>
        `).join('');
    } catch(e) { console.error(e); }
}

// Save settings
async function saveSettings() {
    const provider = document.getElementById('provider-select').value;
    const model = document.getElementById('model-input').value;
    try {
        await fetch(`${API_BASE}/api/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ default_provider: provider, default_model: model })
        });
        alert('Settings saved');
    } catch(e) { alert('Error: ' + e.message); }
}

// Update API key
async function updateApiKey(provider) {
    const key = document.getElementById(`key-${provider}`).value;
    if (!key) return;
    const apiKeys = {};
    apiKeys[provider] = key;
    try {
        await fetch(`${API_BASE}/api/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_keys: apiKeys })
        });
        alert(`${provider.toUpperCase()} API key saved`);
        document.getElementById(`key-${provider}`).value = '';
    } catch(e) { alert('Error: ' + e.message); }
}

// Load session
async function loadSession(sessionId) {
    try {
        await fetch(`${API_BASE}/api/sessions/load`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });
        alert('Session loaded');
        loadSessions();
    } catch(e) { alert('Error: ' + e.message); }
}

// Delete session
async function deleteSession(sessionId) {
    if (!confirm('Delete this session?')) return;
    try {
        await fetch(`${API_BASE}/api/sessions/delete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });
        alert('Session deleted');
        loadSessions();
    } catch(e) { alert('Error: ' + e.message); }
}

// New session
async function newSession() {
    try {
        await fetch(`${API_BASE}/api/sessions/new`, { method: 'POST' });
        alert('New session created');
        loadSessions();
    } catch(e) { alert('Error: ' + e.message); }
}

// Clear memory
async function clearMemory() {
    if (!confirm('Clear current memory?')) return;
    try {
        await fetch(`${API_BASE}/api/sessions/clear`, { method: 'POST' });
        alert('Memory cleared');
        loadSessions();
    } catch(e) { alert('Error: ' + e.message); }
}

// Clear created files
async function clearCreatedFiles() {
    if (!confirm('Delete all created files?')) return;
    try {
        await fetch(`${API_BASE}/api/clear-created`, { method: 'POST' });
        alert('Created files cleared');
        loadCreatedFiles();
    } catch(e) { alert('Error: ' + e.message); }
}

// Send chat message
async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    const messagesDiv = document.getElementById('chat-messages');
    messagesDiv.innerHTML += `<div class="message user"><div class="message-content">${message}</div></div>`;
    input.value = '';
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    try {
        const res = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        const data = await res.json();
        messagesDiv.innerHTML += `<div class="message ai"><div class="message-content">${data.response || 'Task completed'}</div></div>`;
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    } catch(e) {
        messagesDiv.innerHTML += `<div class="message ai"><div class="message-content">Error: ${e.message}</div></div>`;
    }
}

// Execute command
async function executeCommand(command) {
    const terminalBody = document.getElementById('terminal-body');
    terminalBody.innerHTML += `<div class="terminal-line">$ ${command}</div>`;
    terminalBody.scrollTop = terminalBody.scrollHeight;

    try {
        const res = await fetch(`${API_BASE}/api/command`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: command })
        });
        const data = await res.json();
        if (data.stdout) {
            terminalBody.innerHTML += `<div class="terminal-line">${data.stdout}</div>`;
        }
        if (data.stderr) {
            terminalBody.innerHTML += `<div class="terminal-line" style="color: #ffaa00;">${data.stderr}</div>`;
        }
        terminalBody.scrollTop = terminalBody.scrollHeight;
    } catch(e) {
        terminalBody.innerHTML += `<div class="terminal-line" style="color: #ff5a5f;">Error: ${e.message}</div>`;
    }
}

// Initialize based on current page
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('stat-status')) loadDashboard();
    if (document.getElementById('provider-select')) loadSettings();
    
    // Setup terminal if exists
    const terminalInput = document.getElementById('terminal-input');
    if (terminalInput) {
        terminalInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                executeCommand(terminalInput.value);
                terminalInput.value = '';
            }
        });
    }
    
    // Setup chat if exists
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
});