/**
 * ZynoxAI - Main JavaScript
 * Material Design 3 Style with i18n and file attachments
 */

const API_BASE = '';
let currentDirectory = '';
let terminalHistory = [];
let historyIndex = -1;
let isStreaming = false;
let currentAbortController = null;
let attachedFiles = [];
let selectedProvider = 'openai';

// ============ i18n Translations ============
const TRANSLATIONS = {
    en: {
        dashboard_text: "Dashboard", chat_text: "Chat", settings_text: "Settings",
        settings_title: "Settings", status: "Status", status_label: "Status",
        provider: "Provider", environment: "Environment", package_manager: "Package Manager",
        sessions: "Saved Sessions", new: "New", clear: "Clear",
        created_files: "Created Files", download_all: "Download All",
        terminal: "Terminal", terminal_hint: "Type commands below (cd, ls, pwd, etc.)",
        ai_provider: "AI Provider", default_provider: "Default Provider",
        default_model: "Default Model", model_hint: "Model name", save: "Save",
        api_keys: "API Keys", about: "About", version: "Version",
        author: "Author", license: "License", language: "Language",
        chat_welcome: "<strong>ZynoxAI ready.</strong><br><br>Examples:<br>• \"create a python file called hello.py with print('Hello')\"<br>• \"find abc.txt and read it\"<br>• \"list all files\"",
        chat_placeholder: "Describe what you want..."
    },
    zh: {
        dashboard_text: "仪表盘", chat_text: "聊天", settings_text: "设置",
        settings_title: "设置", status: "状态", status_label: "状态",
        provider: "提供商", environment: "环境", package_manager: "包管理器",
        sessions: "保存的会话", new: "新建", clear: "清除",
        created_files: "创建的文件", download_all: "全部下载",
        terminal: "终端", terminal_hint: "在下方输入命令 (cd, ls, pwd 等)",
        ai_provider: "AI 提供商", default_provider: "默认提供商",
        default_model: "默认模型", model_hint: "模型名称", save: "保存",
        api_keys: "API 密钥", about: "关于", version: "版本",
        author: "作者", license: "许可证", language: "语言",
        chat_welcome: "<strong>ZynoxAI 已就绪。</strong><br><br>示例：<br>• \"创建一个名为 hello.py 的 Python 文件\"<br>• \"查找 abc.txt 并读取\"<br>• \"列出所有文件\"",
        chat_placeholder: "描述你想要做什么..."
    },
    de: {
        dashboard_text: "Übersicht", chat_text: "Chat", settings_text: "Einstellungen",
        settings_title: "Einstellungen", status: "Status", status_label: "Status",
        provider: "Anbieter", environment: "Umgebung", package_manager: "Paketmanager",
        sessions: "Gespeicherte Sitzungen", new: "Neu", clear: "Löschen",
        created_files: "Erstellte Dateien", download_all: "Alle herunterladen",
        terminal: "Terminal", terminal_hint: "Befehle unten eingeben",
        ai_provider: "KI-Anbieter", default_provider: "Standardanbieter",
        default_model: "Standardmodell", model_hint: "Modellname", save: "Speichern",
        api_keys: "API-Schlüssel", about: "Über", version: "Version",
        author: "Autor", license: "Lizenz", language: "Sprache",
        chat_welcome: "<strong>ZynoxAI bereit.</strong><br><br>Beispiele:<br>• \"Erstelle eine Python-Datei hello.py\"<br>• \"Finde abc.txt\"<br>• \"Liste alle Dateien auf\"",
        chat_placeholder: "Beschreibe, was du tun möchtest..."
    },
    ru: {
        dashboard_text: "Панель", chat_text: "Чат", settings_text: "Настройки",
        settings_title: "Настройки", status: "Статус", status_label: "Статус",
        provider: "Провайдер", environment: "Окружение", package_manager: "Менеджер пакетов",
        sessions: "Сохранённые сессии", new: "Новая", clear: "Очистить",
        created_files: "Созданные файлы", download_all: "Скачать всё",
        terminal: "Терминал", terminal_hint: "Введите команды ниже",
        ai_provider: "AI Провайдер", default_provider: "Провайдер по умолчанию",
        default_model: "Модель по умолчанию", model_hint: "Имя модели", save: "Сохранить",
        api_keys: "API Ключи", about: "О программе", version: "Версия",
        author: "Автор", license: "Лицензия", language: "Язык",
        chat_welcome: "<strong>ZynoxAI готов.</strong><br><br>Примеры:<br>• \"создай python файл hello.py\"<br>• \"найди abc.txt\"<br>• \"покажи все файлы\"",
        chat_placeholder: "Опишите, что вы хотите..."
    },
    ar: {
        dashboard_text: "لوحة التحكم", chat_text: "محادثة", settings_text: "الإعدادات",
        settings_title: "الإعدادات", status: "الحالة", status_label: "الحالة",
        provider: "المزود", environment: "البيئة", package_manager: "مدير الحزم",
        sessions: "الجلسات المحفوظة", new: "جديد", clear: "مسح",
        created_files: "الملفات المنشأة", download_all: "تحميل الكل",
        terminal: "الطرفية", terminal_hint: "اكتب الأوامر أدناه",
        ai_provider: "مزود الذكاء الاصطناعي", default_provider: "المزود الافتراضي",
        default_model: "النموذج الافتراضي", model_hint: "اسم النموذج", save: "حفظ",
        api_keys: "مفاتيح API", about: "حول", version: "الإصدار",
        author: "المؤلف", license: "الترخيص", language: "اللغة",
        chat_welcome: "<strong>ZynoxAI جاهز.</strong><br><br>أمثلة:<br>• \"أنشئ ملف python\"<br>• \"ابحث عن abc.txt\"<br>• \"اعرض جميع الملفات\"",
        chat_placeholder: "صف ما تريد القيام به..."
    },
    fr: {
        dashboard_text: "Tableau de bord", chat_text: "Discussion", settings_text: "Paramètres",
        settings_title: "Paramètres", status: "Statut", status_label: "Statut",
        provider: "Fournisseur", environment: "Environnement", package_manager: "Gestionnaire de paquets",
        sessions: "Sessions enregistrées", new: "Nouveau", clear: "Effacer",
        created_files: "Fichiers créés", download_all: "Tout télécharger",
        terminal: "Terminal", terminal_hint: "Tapez les commandes ci-dessous",
        ai_provider: "Fournisseur IA", default_provider: "Fournisseur par défaut",
        default_model: "Modèle par défaut", model_hint: "Nom du modèle", save: "Enregistrer",
        api_keys: "Clés API", about: "À propos", version: "Version",
        author: "Auteur", license: "Licence", language: "Langue",
        chat_welcome: "<strong>ZynoxAI prêt.</strong><br><br>Exemples :<br>• \"crée un fichier python\"<br>• \"trouve abc.txt\"<br>• \"liste tous les fichiers\"",
        chat_placeholder: "Décrivez ce que vous voulez faire..."
    },
    pt: {
        dashboard_text: "Painel", chat_text: "Chat", settings_text: "Configurações",
        settings_title: "Configurações", status: "Status", status_label: "Status",
        provider: "Provedor", environment: "Ambiente", package_manager: "Gerenciador de pacotes",
        sessions: "Sessões salvas", new: "Nova", clear: "Limpar",
        created_files: "Arquivos criados", download_all: "Baixar tudo",
        terminal: "Terminal", terminal_hint: "Digite comandos abaixo",
        ai_provider: "Provedor de IA", default_provider: "Provedor padrão",
        default_model: "Modelo padrão", model_hint: "Nome do modelo", save: "Salvar",
        api_keys: "Chaves de API", about: "Sobre", version: "Versão",
        author: "Autor", license: "Licença", language: "Idioma",
        chat_welcome: "<strong>ZynoxAI pronto.</strong><br><br>Exemplos:<br>• \"crie um arquivo python\"<br>• \"encontre abc.txt\"<br>• \"liste todos os arquivos\"",
        chat_placeholder: "Descreva o que você quer fazer..."
    },
    'pt-BR': {
        dashboard_text: "Painel", chat_text: "Chat", settings_text: "Configurações",
        settings_title: "Configurações", status: "Status", status_label: "Status",
        provider: "Provedor", environment: "Ambiente", package_manager: "Gerenciador de pacotes",
        sessions: "Sessões salvas", new: "Nova", clear: "Limpar",
        created_files: "Arquivos criados", download_all: "Baixar tudo",
        terminal: "Terminal", terminal_hint: "Digite comandos abaixo",
        ai_provider: "Provedor de IA", default_provider: "Provedor padrão",
        default_model: "Modelo padrão", model_hint: "Nome do modelo", save: "Salvar",
        api_keys: "Chaves de API", about: "Sobre", version: "Versão",
        author: "Autor", license: "Licença", language: "Idioma",
        chat_welcome: "<strong>ZynoxAI pronto.</strong><br><br>Exemplos:<br>• \"crie um arquivo python\"<br>• \"encontre abc.txt\"<br>• \"liste todos os arquivos\"",
        chat_placeholder: "Descreva o que você quer fazer..."
    }
};

const LANG_LABELS = {
    'en': 'English', 'zh': '中文', 'de': 'Deutsch', 'ru': 'Русский',
    'ar': 'العربية', 'fr': 'Français', 'pt': 'Português', 'pt-BR': 'Português (Brasil)'
};

const RTL_LANGS = ['ar', 'he', 'fa', 'ur'];

function applyLanguage(lang) {
    const t = TRANSLATIONS[lang] || TRANSLATIONS.en;
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (t[key]) el.innerHTML = t[key];
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (t[key]) el.placeholder = t[key];
    });
    document.getElementById('selectedLangText').textContent = LANG_LABELS[lang] || 'English';
    if (RTL_LANGS.includes(lang)) {
        document.documentElement.setAttribute('dir', 'rtl');
        document.documentElement.setAttribute('lang', lang);
    } else {
        document.documentElement.setAttribute('dir', 'ltr');
        document.documentElement.setAttribute('lang', lang);
    }
    localStorage.setItem('zynoxai-lang', lang);
}

function selectLanguage(lang, itemEl) {
    applyLanguage(lang);
    if (itemEl) {
        const parent = itemEl.parentElement;
        parent.querySelectorAll('.md3-menu-item').forEach(el => el.classList.remove('selected'));
        itemEl.classList.add('selected');
    }
    document.getElementById('langDropdownContainer').classList.remove('open');
}

const savedLang = localStorage.getItem('zynoxai-lang') || 'en';
applyLanguage(savedLang);

document.querySelectorAll('#langDropdownContainer .md3-menu-item').forEach((item) => {
    const langs = ['en', 'zh', 'de', 'ru', 'ar', 'fr', 'pt', 'pt-BR'];
    const idx = Array.from(item.parentElement.children).indexOf(item);
    if (langs[idx] === savedLang) item.classList.add('selected');
    else item.classList.remove('selected');
});

// ============ Icons ============
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

function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// ============ Dropdown (Language) ============
function toggleDropdown(containerId) {
    const container = document.getElementById(containerId);
    const isAlreadyOpen = container.classList.contains('open');
    document.querySelectorAll('.md3-dropdown-container').forEach(c => c.classList.remove('open'));
    document.querySelectorAll('.md3-select-container').forEach(c => c.classList.remove('open'));
    if (!isAlreadyOpen) container.classList.add('open');
}

// ============ Custom Select (Provider) ============
function toggleSelect(containerId) {
    const container = document.getElementById(containerId);
    const isAlreadyOpen = container.classList.contains('open');
    document.querySelectorAll('.md3-select-container').forEach(c => c.classList.remove('open'));
    document.querySelectorAll('.md3-dropdown-container').forEach(c => c.classList.remove('open'));
    if (!isAlreadyOpen) container.classList.add('open');
}

function selectProvider(value, label, itemEl) {
    selectedProvider = value;
    document.getElementById('selectedProviderText').textContent = label;
    const parent = itemEl.parentElement;
    parent.querySelectorAll('.md3-select-item').forEach(el => el.classList.remove('selected'));
    itemEl.classList.add('selected');
    document.getElementById('providerSelectContainer').classList.remove('open');
}

// Close all dropdowns when clicking outside
document.addEventListener('click', function(event) {
    if (!event.target.closest('.md3-dropdown-container')) {
        document.querySelectorAll('.md3-dropdown-container').forEach(c => c.classList.remove('open'));
    }
    if (!event.target.closest('.md3-select-container')) {
        document.querySelectorAll('.md3-select-container').forEach(c => c.classList.remove('open'));
    }
});

// ============ Navigation ============
document.querySelectorAll('.m3-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        const page = tab.getAttribute('data-page');
        showPage(page);
        document.querySelectorAll('.m3-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
    });
});

function showPage(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(`${page}-page`).classList.add('active');
    if (page === 'dashboard') loadDashboard();
    if (page === 'settings') loadSettings();
}

// ============ File Attachments ============
function handleFilesSelected(event) {
    const files = Array.from(event.target.files);
    files.forEach(file => {
        if (!attachedFiles.find(f => f.name === file.name && f.size === file.size)) {
            attachedFiles.push(file);
        }
    });
    renderAttachmentPreview();
    event.target.value = '';
}

function removeAttachment(index) {
    attachedFiles.splice(index, 1);
    renderAttachmentPreview();
}

function renderAttachmentPreview() {
    const container = document.getElementById('attachment-preview');
    if (!container) return;
    if (attachedFiles.length === 0) {
        container.innerHTML = '';
        container.style.display = 'none';
        return;
    }
    container.style.display = 'flex';
    container.innerHTML = attachedFiles.map((file, idx) => {
        const iconUrl = getFileIcon(file.name, false);
        return `
            <div class="attachment-chip">
                <img src="${iconUrl}" class="attachment-icon" alt="">
                <span class="attachment-name">${escapeHtml(file.name)}</span>
                <span class="attachment-size">${formatFileSize(file.size)}</span>
                <button class="attachment-remove" onclick="removeAttachment(${idx})">
                    <span class="material-symbols-outlined">close</span>
                </button>
            </div>
        `;
    }).join('');
}

// ============ Dashboard ============
async function loadDashboard() {
    try {
        const res = await fetch(`${API_BASE}/api/status`);
        const data = await res.json();
        document.getElementById('stat-status').innerHTML = '<span style="color: var(--md-sys-color-success);">● Running</span>';
        document.getElementById('stat-provider').innerText = data.provider || '-';
        document.getElementById('stat-env').innerText = data.environment || '-';
        document.getElementById('stat-pm').innerText = data.package_manager || '-';
    } catch(e) { console.error(e); }
    await loadSessions();
    await loadCreatedFiles();
    await getCurrentDirectory();
}

async function getCurrentDirectory() {
    try {
        const res = await fetch(`${API_BASE}/api/pwd`);
        const data = await res.json();
        currentDirectory = data.cwd;
        return currentDirectory;
    } catch(e) { return ''; }
}

async function loadSessions() {
    try {
        const res = await fetch(`${API_BASE}/api/sessions`);
        const data = await res.json();
        const container = document.getElementById('sessions-container');
        if (data.sessions && data.sessions.length > 0) {
            container.innerHTML = data.sessions.map(s => `
                <div class="list-item">
                    <div class="list-item-info" onclick="loadSession('${s.id}')" style="cursor:pointer;">
                        <div class="list-item-title">${escapeHtml(s.id)}</div>
                        <div class="list-item-subtitle">${escapeHtml(s.created || 'Unknown')} · ${s.message_count} messages</div>
                    </div>
                    <div class="list-item-actions">
                        <button class="btn btn-outlined" onclick="loadSession('${s.id}')">Load</button>
                        <button class="btn btn-text" onclick="deleteSession('${s.id}')" style="color: var(--md-sys-color-error);">
                            <span class="material-symbols-outlined">delete</span>
                        </button>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<div class="list-item"><div class="list-item-info"><div class="list-item-subtitle">No sessions</div></div></div>';
        }
    } catch(e) { console.error(e); }
}

async function loadCreatedFiles() {
    try {
        const res = await fetch(`${API_BASE}/api/files/list`);
        const data = await res.json();
        const container = document.getElementById('created-files-container');
        if (data.files && data.files.length > 0) {
            let filesHtml = '';
            data.files.forEach(file => {
                const isDir = file.is_dir;
                const iconUrl = getFileIcon(file.name, isDir);
                const downloadUrl = isDir
                    ? `/api/folder/download?path=${encodeURIComponent(file.path)}`
                    : `/api/files/download?path=${encodeURIComponent(file.path)}`;
                filesHtml += `
                    <div class="list-item">
                        <img src="${iconUrl}" class="file-icon" alt="">
                        <div class="list-item-info">
                            <div class="list-item-title">${escapeHtml(file.name)}</div>
                        </div>
                        <div class="list-item-actions">
                            <button class="btn btn-outlined" onclick="window.open('${downloadUrl}', '_blank')">
                                <span class="material-symbols-outlined" style="font-size:16px;">download</span>
                                ${isDir ? 'ZIP' : 'Download'}
                            </button>
                        </div>
                    </div>
                `;
            });
            container.innerHTML = filesHtml;
        } else {
            container.innerHTML = '<div class="list-item"><div class="list-item-info"><div class="list-item-subtitle">No files created yet</div></div></div>';
        }
    } catch(e) { console.error(e); }
}

async function downloadAllFiles() {
    window.open(`${API_BASE}/api/files/download-all`, '_blank');
}

// ============ Sessions ============
async function loadSession(sessionId) {
    try {
        await fetch(`${API_BASE}/api/sessions/load`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });
        loadSessions();
    } catch(e) { alert('Error: ' + e.message); }
}

async function deleteSession(sessionId) {
    if (!confirm('Delete this session?')) return;
    try {
        await fetch(`${API_BASE}/api/sessions/delete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });
        loadSessions();
    } catch(e) { alert('Error: ' + e.message); }
}

async function newSession() {
    try {
        await fetch(`${API_BASE}/api/sessions/new`, { method: 'POST' });
        loadSessions();
    } catch(e) { alert('Error: ' + e.message); }
}

async function clearMemory() {
    if (!confirm('Clear current memory?')) return;
    try {
        await fetch(`${API_BASE}/api/sessions/clear`, { method: 'POST' });
        loadSessions();
    } catch(e) { alert('Error: ' + e.message); }
}

// ============ Settings ============
async function loadSettings() {
    try {
        const res = await fetch(`${API_BASE}/api/config`);
        const data = await res.json();

        // Update provider custom select
        const provider = data.default_provider || 'openai';
        selectedProvider = provider;
        const providerLabels = { openai: 'OpenAI', gemini: 'Gemini', grok: 'Grok', deepseek: 'DeepSeek' };
        document.getElementById('selectedProviderText').textContent = providerLabels[provider] || 'OpenAI';
        document.querySelectorAll('#providerSelectContainer .md3-select-item').forEach(el => {
            if (el.getAttribute('data-value') === provider) {
                el.classList.add('selected');
            } else {
                el.classList.remove('selected');
            }
        });

        // Update model input
        document.getElementById('model-input').value = data.default_model || '';

        // Update API keys
        const container = document.getElementById('api-keys-container');
        const providers = ['openai', 'gemini', 'grok', 'deepseek'];
        container.innerHTML = providers.map((p) => {
            const hasKey = data.api_keys && data.api_keys.includes(p);
            return `
                <div class="card">
                    <div class="setting-row">
                        <span class="setting-label">${p.toUpperCase()} API Key</span>
                        <div style="display:flex; gap:0.5rem; align-items:center; flex-wrap:wrap;">
                            <div class="md3-textfield">
                                <input type="password" id="key-${p}" class="md3-textfield-input" placeholder=" ">
                                <label class="md3-textfield-label" for="key-${p}">API key</label>
                            </div>
                            <button class="btn btn-filled" onclick="updateApiKey('${p}')">Save</button>
                            <span style="font-size:0.75rem; color: var(--md-sys-color-on-surface-variant);">${hasKey ? '✓ Configured' : '— Not set'}</span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    } catch(e) { console.error(e); }
}

async function saveSettings() {
    const provider = selectedProvider;
    const model = document.getElementById('model-input').value;
    try {
        await fetch(`${API_BASE}/api/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ default_provider: provider, default_model: model })
        });
        loadStatus();
    } catch(e) { alert('Error: ' + e.message); }
}

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
        document.getElementById(`key-${provider}`).value = '';
        loadSettings();
    } catch(e) { alert('Error: ' + e.message); }
}

async function loadStatus() {
    try {
        const res = await fetch(`${API_BASE}/api/status`);
        const data = await res.json();
        const statusText = document.getElementById('status-text');
        if (statusText) statusText.innerText = data.provider || 'Ready';
    } catch(e) {}
}

// ============ Terminal ============
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
                termBody.innerHTML += `<div class="terminal-line" style="color: #f59e0b;">Error: ${escapeHtml(data.error || 'Failed')}</div>`;
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

// ============ Chat ============
const chatInput = document.getElementById('chat-input');
if (chatInput) {
    chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

async function stopTask() {
    if (!isStreaming) return;
    try {
        await fetch(`${API_BASE}/api/stop`, { method: 'POST' });
        if (currentAbortController) {
            currentAbortController.abort();
            currentAbortController = null;
        }
        isStreaming = false;
        const sendBtn = document.getElementById('send-btn');
        sendBtn.disabled = false;
        sendBtn.classList.remove('stop');
        sendBtn.innerHTML = '<span class="material-symbols-outlined">arrow_upward</span>';
        sendBtn.onclick = sendMessage;
        const thinkingDiv = document.getElementById('thinking-indicator');
        if (thinkingDiv) thinkingDiv.remove();
    } catch(e) { console.error(e); }
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    const sendBtn = document.getElementById('send-btn');

    if ((!message && attachedFiles.length === 0) || isStreaming) return;

    let userDisplay = message;
    if (attachedFiles.length > 0) {
        const fileNames = attachedFiles.map(f => f.name).join(', ');
        userDisplay = message ? `${message}\n📎 ${fileNames}` : `📎 ${fileNames}`;
    }
    addMessage('user', userDisplay);

    const filesToUpload = [...attachedFiles];

    input.value = '';
    input.style.height = 'auto';
    attachedFiles = [];
    renderAttachmentPreview();

    sendBtn.disabled = false;
    sendBtn.classList.add('stop');
    sendBtn.innerHTML = '<span class="material-symbols-outlined">stop</span>';
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
        const formData = new FormData();
        formData.append('message', message);
        filesToUpload.forEach(file => {
            formData.append('files', file, file.name);
        });

        const response = await fetch(`${API_BASE}/api/chat/stream`, {
            method: 'POST',
            body: formData,
            signal: currentAbortController.signal
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const dataStr = line.slice(6);
                    if (dataStr === '[DONE]') continue;

                    try {
                        const parsed = JSON.parse(dataStr);
                        if (parsed.text) {
                            fullText += parsed.text;
                            textSpan.innerHTML = escapeHtml(fullText).replace(/\n/g, '<br>');
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
                    } catch(e) {}
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
        sendBtn.innerHTML = '<span class="material-symbols-outlined">arrow_upward</span>';
        sendBtn.onclick = sendMessage;
        isStreaming = false;
        currentAbortController = null;
    }
}

function addFileDeliveryMessage(files) {
    const messagesDiv = document.getElementById('chat-messages');
    const deliveryDiv = document.createElement('div');
    deliveryDiv.className = 'file-delivery';
    let filesHtml = '<div class="file-delivery-content">';
    filesHtml += '<div class="file-delivery-header"><span class="material-symbols-outlined" style="font-size:16px;">attach_file</span> Files Created</div>';
    filesHtml += '<div class="file-list">';
    files.forEach(file => {
        const isDir = file.is_dir;
        const iconUrl = getFileIcon(file.name, isDir);
        const sizeText = file.size ? formatFileSize(file.size) : '';
        const downloadUrl = isDir
            ? `/api/folder/download?path=${encodeURIComponent(file.path)}`
            : `/api/files/download?path=${encodeURIComponent(file.path)}`;
        filesHtml += `
            <div class="file-delivery-item">
                <img src="${iconUrl}" class="file-delivery-icon" alt="">
                <div class="file-info">
                    <a href="#" class="file-name-link" onclick="window.open('${downloadUrl}', '_blank'); return false;">${escapeHtml(file.name)}</a>
                    ${sizeText ? `<div class="file-size">${sizeText}</div>` : ''}
                </div>
                <button class="${isDir ? 'download-folder-btn' : 'download-single-btn'}" onclick="window.open('${downloadUrl}', '_blank')">
                    ${isDir ? 'ZIP' : 'Download'}
                </button>
            </div>
        `;
    });
    if (files.length > 1) {
        filesHtml += `<button class="download-all-btn" onclick="downloadAllFiles()">Download All (${files.length})</button>`;
    }
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
    const escapedContent = escapeHtml(content).replace(/\n/g, '<br>');
    messageDiv.innerHTML = `<div class="message-content">${escapedContent}</div>`;
    messagesDiv.appendChild(messageDiv);
    const container = document.querySelector('.chat-messages-container');
    if (container) container.scrollTop = container.scrollHeight;
}

// ============ Init ============
loadDashboard();
loadStatus();