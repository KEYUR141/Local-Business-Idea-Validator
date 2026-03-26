const API_BASE_URL = window.location.origin;
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

    if (sendBtn.disabled) {
        return;
    }

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
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(errorData.detail || 'Failed to validate idea');
        }

        const result = await response.json();
        addValidationMessage(result);
        showToast('Analysis complete', 'success');
    } catch (error) {
        console.error('Error sending message:', error);
        showToast(error.message || 'Error processing request', 'error');
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

    // Check if response is properly formatted with all required fields
    const hasProperFormat = result.title && result.score !== undefined && result.verdict && result.summary;

    if (hasProperFormat) {
        // Formatted response with insights
        const scoreColor = getScoreColor(result.score);
        const scoreClass = scoreColor === 'excellent' ? 'excellent' : 
                           scoreColor === 'good' ? 'good' : 
                           scoreColor === 'moderate' ? 'moderate' : 'poor';

        contentEl.innerHTML = `
            <div class="validation-result">
                <div class="result-title">${result.title}</div>
                
                <div class="result-header">
                    <div class="score-badge">
                        <div class="score-circle ${scoreClass}">
                            ${result.score.toFixed(1)}
                        </div>
                    </div>
                    <div class="result-verdict">
                        <div class="verdict-label">Verdict</div>
                        <div class="verdict-text">${result.verdict || 'Assessment'}</div>
                    </div>
                </div>

                <div class="result-summary-box">
                    <div class="result-summary-label">Summary</div>
                    <div class="result-item-value">${result.summary}</div>
                </div>

                <button class="details-toggle" onclick="toggleDetails(this)">Show Details</button>

                <div class="details-section hidden">
                    <div class="result-grid">
                        <div class="result-item">
                            <div class="result-item-label">Market Opportunity</div>
                            <div class="result-item-value">${result.market}</div>
                        </div>
                        <div class="result-item">
                            <div class="result-item-label">Key Risk</div>
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

                    <div class="result-item" style="border-left-color: #4CAF50; margin-top: 12px;">
                        <div class="result-item-label">First Step</div>
                        <div class="result-item-value">${result.first_step}</div>
                    </div>
                </div>
            </div>
        `;
    } else {
        // Fallback for incomplete responses
        contentEl.innerHTML = `
            <div class="validation-result plain">
                <div class="plain-response">
                    <p>${typeof result === 'string' ? result : JSON.stringify(result, null, 2)}</p>
                </div>
            </div>
        `;
    }

    messageEl.appendChild(contentEl);
    messagesContainer.appendChild(messageEl);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function toggleDetails(button) {
    const detailsSection = button.nextElementSibling;
    const isHidden = detailsSection.classList.contains('hidden');
    
    if (isHidden) {
        detailsSection.classList.remove('hidden');
        button.textContent = 'Hide Details';
    } else {
        detailsSection.classList.add('hidden');
        button.textContent = 'Show Details';
    }
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

        if (data.conversation_status === 'Connected') {
            redisStatusEl.textContent = 'Memory: Connected';
        } else {
            redisStatusEl.textContent = 'Memory: Disconnected';
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
        data.conversations.forEach(conv => {
            const conversationId = conv.id || conv;
            const title = conv.title || conversationId.substring(0, 8) + '...';
            
            const item = document.createElement('div');
            item.className = 'conversation-item';
            
            const textSpan = document.createElement('span');
            textSpan.className = 'conversation-item-text';
            textSpan.textContent = title;
            textSpan.title = conversationId;
            textSpan.style.cursor = 'pointer';
            textSpan.onclick = () => loadConversationHistory(conversationId);
            
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'conversation-item-delete';
            deleteBtn.textContent = 'Delete';
            deleteBtn.onclick = (e) => {
                e.stopPropagation();
                deleteConversation(conversationId);
            };
            
            item.appendChild(textSpan);
            item.appendChild(deleteBtn);
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

async function deleteConversation(conversationId) {
    try {
        const response = await fetch(`${API_BASE_URL}/conversation/${conversationId}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            throw new Error('Failed to delete conversation');
        }

        showToast('Conversation deleted', 'success');
        loadConversations();
        
        if (currentConversationId === conversationId) {
            currentConversationId = null;
            conversationIdDisplay.textContent = 'No active chat';
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
        }
    } catch (error) {
        console.error('Error deleting conversation:', error);
        showToast(`Error: ${error.message}`, 'error');
    }
}
