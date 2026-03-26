const API_BASE_URL = 'http://localhost:8000';
let currentConversationId = null;

const messagesContainer = document.getElementById('messages-container');
const ideaInput = document.getElementById('idea-input');
const chatForm = document.getElementById('chat-form');
const sendBtn = document.getElementById('send-btn');
const spinner = document.getElementById('loading-spinner');
const toast = document.getElementById('toast');
const conversationIdDisplay = document.getElementById('conversation-id-display');
const redisStatusEl = document.getElementById('redis-status');

chatForm.addEventListener('submit', sendMessage);
ideaInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
        sendMessage(e);
    }
});

window.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    loadConversations();
});

async function startNewConversation() {
    showSpinner(true);
    try {
        const response = await fetch(`${API_BASE_URL}/conversation/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            throw new Error('Failed to start conversation');
        }

        const data = await response.json();
        currentConversationId = data.Conversation_Id;

        messagesContainer.innerHTML = `
            <div class="welcome-message">
                <h3>Welcome</h3>
                <p>Describe your business idea. Analysis includes:</p>
                <ul>
                    <li>Viability Score (0-10)</li>
                    <li>Market Opportunity</li>
                    <li>Risk Assessment</li>
                    <li>Growth Potential</li>
                    <li>Competitive Analysis</li>
                    <li>Action Steps</li>
                </ul>
            </div>
        `;

        conversationIdDisplay.textContent = `ID: ${currentConversationId.substring(0, 8)}...`;
        ideaInput.focus();
        ideaInput.value = '';

        showToast('New conversation started', 'success');
        loadConversations();
        showSpinner(false);
    } catch (error) {
        console.error('Error starting conversation:', error);
        showToast('Failed to start new conversation', 'error');
        showSpinner(false);
    }
}

async function sendMessage(event) {
    event.preventDefault();

    const idea = ideaInput.value.trim();

    if (idea.length < 10) {
        showToast('Minimum 10 characters required', 'error');
        return;
    }

    if (idea.length > 500) {
        showToast('Maximum 500 characters allowed', 'error');
        return;
    }

    if (!currentConversationId) {
        showToast('Please start a new conversation first', 'error');
        return;
    }

    addMessage(idea, 'user');
    ideaInput.value = '';
    sendBtn.disabled = true;
    showSpinner(true);

    try {
        const payload = {
            idea: idea,
            conversation_id: currentConversationId
        };

        const response = await fetch(`${API_BASE_URL}/chat/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to validate idea');
        }

        const result = await response.json();
        addValidationMessage(result);
        showToast('Analysis complete', 'success');
    } catch (error) {
        console.error('Error sending message:', error);
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        sendBtn.disabled = false;
        showSpinner(false);
        ideaInput.focus();
    }
}

function addMessage(content, role) {
    const messageEl = document.createElement('div');
    messageEl.className = `message ${role}`;

    const contentEl = document.createElement('div');
    contentEl.className = 'message-content';
    contentEl.textContent = content;

    messageEl.appendChild(contentEl);
    messagesContainer.appendChild(messageEl);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function addValidationMessage(result) {
    const messageEl = document.createElement('div');
    messageEl.className = 'message assistant';

    const contentEl = document.createElement('div');
    contentEl.className = 'message-content';

    const scoreColor = getScoreColor(result.score);
    const scoreClass = scoreColor === 'excellent' ? 'excellent' : 
                       scoreColor === 'good' ? 'good' : 
                       scoreColor === 'moderate' ? 'moderate' : 'poor';

    contentEl.innerHTML = `
        <div class="validation-result">
            <div class="result-header">
                <div class="score-badge">
                    <div class="score-circle ${scoreClass}">
                        ${result.score.toFixed(1)}
                    </div>
                </div>
                <div class="verdict">${result.verdict || 'Assessment'}</div>
            </div>

            <div class="result-grid">
                <div class="result-item">
                    <div class="result-item-label">Market</div>
                    <div class="result-item-value">${result.market}</div>
                </div>
                <div class="result-item">
                    <div class="result-item-label">Risk</div>
                    <div class="result-item-value">${result.risk}</div>
                </div>
                <div class="result-item">
                    <div class="result-item-label">Opportunities</div>
                    <div class="result-item-value">${result.opportunities || 'N/A'}</div>
                </div>
                <div class="result-item">
                    <div class="result-item-label">Competition</div>
                    <div class="result-item-value">${result.competition}</div>
                </div>
            </div>

            <div class="result-item" style="border-left-color: #10b981;">
                <div class="result-item-label">First Step</div>
                <div class="result-item-value">${result.first_step}</div>
            </div>

            <div class="result-summary" style="margin-top: 12px;">
                <div class="result-summary-label">Summary</div>
                <div class="result-item-value">${result.summary}</div>
            </div>
        </div>
    `;

    messageEl.appendChild(contentEl);
    messagesContainer.appendChild(messageEl);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showSpinner(show) {
    if (show) {
        spinner.classList.remove('hidden');
    } else {
        spinner.classList.add('hidden');
    }
}

function showToast(message, type = 'info') {
    toast.textContent = message;
    toast.className = `toast show ${type}`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function getScoreColor(score) {
    if (score >= 7.5) return 'excellent';
    if (score >= 5) return 'good';
    if (score >= 3) return 'moderate';
    return 'poor';
}

async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();

        if (data.redis_status === 'Connected') {
            redisStatusEl.textContent = 'Redis: Connected';
        } else {
            redisStatusEl.textContent = 'Redis: Disconnected';
        }
    } catch (error) {
        console.error('Health check failed:', error);
        redisStatusEl.textContent = 'Server: Offline';
    }
}

setInterval(checkHealth, 10000);

async function loadConversations() {
    try {
        const response = await fetch(`${API_BASE_URL}/conversations`);
        const data = await response.json();

        const conversationsContainer = document.getElementById('conversations-container');
        
        if (!data.conversations || data.conversations.length === 0) {
            conversationsContainer.innerHTML = '<p class="no-conversations">No previous chats</p>';
            return;
        }

        conversationsContainer.innerHTML = '';
        data.conversations.forEach(conversationId => {
            const item = document.createElement('div');
            item.className = 'conversation-item';
            item.textContent = conversationId.substring(0, 8) + '...';
            item.title = conversationId;
            item.onclick = () => loadConversationHistory(conversationId);
            conversationsContainer.appendChild(item);
        });
    } catch (error) {
        console.error('Error loading conversations:', error);
    }
}

async function loadConversationHistory(conversationId) {
    try {
        showSpinner(true);
        
        const response = await fetch(`${API_BASE_URL}/chat/history/${conversationId}`);
        
        if (!response.ok) {
            throw new Error('Failed to load conversation');
        }

        const data = await response.json();
        currentConversationId = conversationId;

        messagesContainer.innerHTML = '';
        
        if (data.History && data.History.length > 0) {
            data.History.forEach(message => {
                if (message.role === 'user') {
                    addMessage(message.content, 'user');
                } else if (message.role === 'assistant') {
                    try {
                        const result = JSON.parse(message.content);
                        addValidationMessage(result);
                    } catch {
                        addMessage(message.content, 'assistant');
                    }
                }
            });
        } else {
            messagesContainer.innerHTML = `
                <div class="welcome-message">
                    <h3>Conversation Loaded</h3>
                    <p>This conversation has no messages.</p>
                </div>
            `;
        }

        conversationIdDisplay.textContent = `ID: ${conversationId.substring(0, 8)}...`;
        ideaInput.focus();
        showToast('Conversation loaded', 'success');
        showSpinner(false);
    } catch (error) {
        console.error('Error loading conversation history:', error);
        showToast(`Error: ${error.message}`, 'error');
        showSpinner(false);
    }
}
