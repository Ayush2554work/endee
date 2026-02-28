/**
 * HemaV MedAssist — Frontend JavaScript
 * Handles chat interactions, API calls, and UI state management.
 */

// ── State ──────────────────────────────────────────────────
let isProcessing = false;
let chatHistory = [];

// ── DOM Elements ───────────────────────────────────────────
const queryInput = document.getElementById('query-input');
const sendBtn = document.getElementById('send-btn');
const chatMessages = document.getElementById('chat-messages');
const welcomeScreen = document.getElementById('welcome');
const sidebar = document.getElementById('sidebar');
const menuToggle = document.getElementById('menu-toggle');

// ── Initialization ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    setupTextarea();
    setupNavigation();
    setupMobileMenu();
    checkHealth();
});

// ── Textarea Auto-Resize ───────────────────────────────────
function setupTextarea() {
    queryInput.addEventListener('input', () => {
        queryInput.style.height = 'auto';
        queryInput.style.height = Math.min(queryInput.scrollHeight, 120) + 'px';
    });

    queryInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendQuery();
        }
    });
}

// ── Navigation ─────────────────────────────────────────────
function setupNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const section = item.dataset.section;

            // Update nav active state
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            item.classList.add('active');

            // Show selected section
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.getElementById(`section-${section}`).classList.add('active');

            // Close mobile menu
            sidebar.classList.remove('open');
        });
    });
}

// ── Mobile Menu ────────────────────────────────────────────
function setupMobileMenu() {
    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });

        // Close sidebar when clicking outside
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768 &&
                !sidebar.contains(e.target) &&
                !menuToggle.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        });
    }
}

// ── Health Check ───────────────────────────────────────────
async function checkHealth() {
    const endeeStatus = document.getElementById('endee-status');
    const groqStatus = document.getElementById('groq-status');

    try {
        const res = await fetch('/api/health');
        const data = await res.json();

        if (data.endee_connected) {
            endeeStatus.classList.add('connected');
            endeeStatus.classList.remove('disconnected');
        } else {
            endeeStatus.classList.add('disconnected');
            endeeStatus.classList.remove('connected');
        }

        // Groq status — we'll mark it as connected since key is configured
        groqStatus.classList.add('connected');
        groqStatus.classList.remove('disconnected');
    } catch (err) {
        endeeStatus.classList.add('disconnected');
        groqStatus.classList.add('disconnected');
    }
}

// ── Ask a Pre-defined Question ─────────────────────────────
function askQuestion(question) {
    queryInput.value = question;
    sendQuery();
}

// ── Start New Chat ─────────────────────────────────────────
function startNewChat() {
    chatMessages.innerHTML = '';
    if (welcomeScreen) {
        welcomeScreen.style.display = 'block';
    }
    isProcessing = false;
    sendBtn.disabled = false;
    queryInput.value = '';
    queryInput.style.height = 'auto';

    // Ensure we are on the Chat tab
    const chatNavItem = document.querySelector('.nav-item[data-section="chat"]');
    if (chatNavItem && !chatNavItem.classList.contains('active')) {
        chatNavItem.click();
    }
}

// ── Settings Modal Logic ───────────────────────────────────
const settingsBtn = document.getElementById('settings-toggle');
const settingsModal = document.getElementById('settings-modal');
const settingsClose = document.getElementById('settings-close');
const saveSettingsBtn = document.getElementById('save-settings');
const apiKeyInput = document.getElementById('api-key-input');

// Load saved key on startup
const savedApiKey = localStorage.getItem('hemav_api_key');
if (savedApiKey) {
    apiKeyInput.value = savedApiKey;
}

settingsBtn.addEventListener('click', () => {
    settingsModal.classList.add('show');
});

settingsClose.addEventListener('click', () => {
    settingsModal.classList.remove('show');
});

// Close when clicking outside modal
settingsModal.addEventListener('click', (e) => {
    if (e.target === settingsModal) {
        settingsModal.classList.remove('show');
    }
});

saveSettingsBtn.addEventListener('click', () => {
    const key = apiKeyInput.value.trim();
    if (key) {
        localStorage.setItem('hemav_api_key', key);
    } else {
        localStorage.removeItem('hemav_api_key');
    }
    settingsModal.classList.remove('show');

    // Optional feedback
    saveSettingsBtn.textContent = 'Saved!';
    setTimeout(() => {
        saveSettingsBtn.textContent = 'Save Settings';
    }, 1500);
});

// ── Send Query ─────────────────────────────────────────────
async function sendQuery() {
    const question = queryInput.value.trim();
    if (!question || isProcessing) return;

    isProcessing = true;
    sendBtn.disabled = true;

    // Hide welcome screen
    if (welcomeScreen) {
        welcomeScreen.style.display = 'none';
    }

    // Add user message
    addMessage('user', question);

    // Clear input
    queryInput.value = '';
    queryInput.style.height = 'auto';

    // Add loading indicator
    const loadingId = addLoadingMessage();

    try {
        const payload = { question: question };
        const storedKey = localStorage.getItem('hemav_api_key');
        if (storedKey) {
            payload.api_key = storedKey;
        }

        const response = await fetch('/api/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        const data = await response.json();

        // Remove loading
        removeMessage(loadingId);

        if (response.ok) {
            addMessage('assistant', data.answer, data.sources);
        } else {
            addMessage('assistant', `<p style="color: #f87171;">❌ ${data.error || 'Something went wrong. Please try again.'}</p>`);
        }
    } catch (error) {
        removeMessage(loadingId);
        addMessage('assistant', `<p style="color: #f87171;">❌ Failed to connect to the server. Please check if the Flask app and Endee server are running.</p>`);
    } finally {
        isProcessing = false;
        sendBtn.disabled = false;
        queryInput.focus();
    }
}

// ── Add Message to Chat ────────────────────────────────────
function addMessage(role, content, sources = null) {
    const msgId = 'msg-' + Date.now();
    const isUser = role === 'user';

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    messageDiv.id = msgId;

    let sourcesHtml = '';
    if (sources && sources.length > 0) {
        const sourceItems = sources.map(s => `
            <div class="source-item">
                <div class="source-meta">
                    <span class="source-file">📄 ${s.source} — Page ${s.page}</span>
                    <span class="source-similarity">${(s.similarity * 100).toFixed(1)}% match</span>
                </div>
                <div class="source-text">${escapeHtml(s.text.substring(0, 200))}${s.text.length > 200 ? '...' : ''}</div>
            </div>
        `).join('');

        sourcesHtml = `
            <div class="sources-panel">
                <button class="sources-toggle" onclick="toggleSources(this)">
                    <span>📚 ${sources.length} Sources Retrieved from Endee</span>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
                </button>
                <div class="sources-list">${sourceItems}</div>
            </div>
        `;
    }

    messageDiv.innerHTML = `
        <div class="message-header">
            <div class="message-avatar ${isUser ? 'user' : 'assistant'}">
                ${isUser ? 'You' : '🩺'}
            </div>
            <span class="message-sender">${isUser ? 'You' : 'HemaV MedAssist'}</span>
        </div>
        <div class="message-body">
            <div class="message-content">${isUser ? `<p>${escapeHtml(content)}</p>` : content}</div>
            ${sourcesHtml}
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    scrollToBottom();
    return msgId;
}

// ── Loading Message ────────────────────────────────────────
function addLoadingMessage() {
    const msgId = 'loading-' + Date.now();

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    messageDiv.id = msgId;

    messageDiv.innerHTML = `
        <div class="message-header">
            <div class="message-avatar assistant">🩺</div>
            <span class="message-sender">HemaV MedAssist</span>
        </div>
        <div class="message-body">
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                </div>
                <span style="font-size: 12px; color: var(--text-muted);">Searching Endee vector database & generating answer...</span>
            </div>
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    scrollToBottom();
    return msgId;
}

// ── Remove Message ─────────────────────────────────────────
function removeMessage(msgId) {
    const el = document.getElementById(msgId);
    if (el) el.remove();
}

// ── Toggle Sources ─────────────────────────────────────────
function toggleSources(btn) {
    btn.classList.toggle('open');
    const list = btn.nextElementSibling;
    list.classList.toggle('show');
}

// ── Helpers ────────────────────────────────────────────────
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function scrollToBottom() {
    const container = document.querySelector('.chat-container');
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
}
