// Terminal emulator for ZynoxAI Web Interface

let terminalHistory = [];
let historyIndex = -1;

function initTerminal() {
    const terminalInput = document.getElementById('terminal-input');
    if (!terminalInput) return;

    terminalInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            const command = terminalInput.value;
            if (command.trim()) {
                terminalHistory.push(command);
                historyIndex = terminalHistory.length;
                executeCommand(command);
                terminalInput.value = '';
            }
        } else if (e.key === 'ArrowUp') {
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

async function executeCommand(command) {
    const terminalBody = document.getElementById('terminal-body');
    terminalBody.innerHTML += `<div class="terminal-line">$ ${command}</div>`;
    terminalBody.scrollTop = terminalBody.scrollHeight;

    try {
        const res = await fetch('/api/command', {
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

// Initialize on page load
document.addEventListener('DOMContentLoaded', initTerminal);