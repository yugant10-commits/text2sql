// Theme Toggle
function toggleTheme() {
    document.documentElement.classList.toggle('dark');
    const isDark = document.documentElement.classList.contains('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

// Auto-resize textarea
document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.querySelector('.input-field');
    if (textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    }
});

// Clear chat
document.querySelector('.clear-btn')?.addEventListener('click', function() {
    const messagesContainer = document.querySelector('#messages-container');
    if (messagesContainer) {
        messagesContainer.innerHTML = '';
    }
});

// Handle form submission
document.querySelector('.input-form')?.addEventListener('submit', function() {
    const textarea = this.querySelector('.input-field');
    if (textarea) {
        textarea.style.height = 'auto';
    }
});

// Initialize theme from localStorage
document.addEventListener('DOMContentLoaded', function() {
    const theme = localStorage.getItem('theme') || 'dark';
    if (theme === 'light') {
        document.documentElement.classList.remove('dark');
    }
});

document.body.addEventListener('htmx:afterSwap', function() {
    const chatMessages = document.querySelector('.chat-messages');
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});

// Initial scroll to bottom
window.addEventListener('load', function() {
    const chatMessages = document.querySelector('.chat-messages');
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});

// Add these event listeners
document.body.addEventListener('htmx:beforeRequest', function(evt) {
    const form = evt.detail.elt;
    const input = form.querySelector('input[name="query"]');
    const query = input.value;

    // Immediately add the user message
    const messagesContainer = document.querySelector('#messages-container');
    const userMessage = `
        <div class="message user-message">
            <div class="message-avatar">
                <img src="/static/images/user-avatar.svg" alt="User" width="36" height="36">
            </div>
            <div class="message-content">
                <p>${query}</p>
            </div>
        </div>
    `;
    messagesContainer.insertAdjacentHTML('beforeend', userMessage);
    
    // Clear the input
    input.value = '';

    // Scroll to bottom
    const chatMessages = document.querySelector('.chat-messages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
});

// Add streaming response handling
document.body.addEventListener('htmx:beforeRequest', function(evt) {
    evt.detail.headers['Accept'] = 'text/event-stream';
});

let currentMessageContainer = null;
let isProcessing = false;

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        const input = document.querySelector('#query');
        if (document.activeElement === input && input.value.trim()) {
            e.preventDefault();
            document.querySelector('#query-form').dispatchEvent(new Event('submit'));
        }
    }
});

// Clear conversation
document.querySelector('.clear-history').addEventListener('click', () => {
    document.querySelector('#messages-container').innerHTML = '';
});

document.body.addEventListener('htmx:beforeRequest', function(evt) {
    if (isProcessing) return; // Prevent multiple submissions
    isProcessing = true;

    const form = evt.detail.elt;
    const input = form.querySelector('input[name="query"]');
    const query = input.value.trim();
    
    if (!query) {
        evt.preventDefault();
        return;
    }

    // Clear input and disable
    input.value = '';
    input.disabled = true;
    
    // Add user message
    const messagesContainer = document.querySelector('#messages-container');
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    const userMessage = `
        <div class="message user-message animate-message">
            <div class="message-avatar">
                <img src="/static/images/user-avatar.svg" alt="User" width="36" height="36">
            </div>
            <div class="message-content">
                <p>${query}</p>
                <div class="message-timestamp">${timestamp}</div>
            </div>
        </div>
    `;
    messagesContainer.insertAdjacentHTML('beforeend', userMessage);
    
    // Create new system message container
    currentMessageContainer = document.createElement('div');
    currentMessageContainer.className = 'message system-message animate-message';
    currentMessageContainer.innerHTML = `
        <div class="message-avatar">
            <img src="/static/images/bot-avatar.jpeg" alt="AirlineSQL" width="36" height="36">
        </div>
        <div class="message-content">
            <div class="bot-response">
                <div class="steps-container"></div>
                <div class="message-timestamp">${timestamp}</div>
            </div>
        </div>
    `;
    messagesContainer.appendChild(currentMessageContainer);
    
    smoothScrollToBottom();
});

document.body.addEventListener('htmx:afterOnLoad', function(evt) {
    const input = document.querySelector('#query');
    input.disabled = false;
    input.focus();
    isProcessing = false;

    if (evt.detail.xhr.getResponseHeader("Content-Type") === "text/event-stream") {
        const lines = evt.detail.xhr.response.split("\n\n");
        lines.forEach(line => {
            if (line.trim()) {
                const stepsContainer = currentMessageContainer.querySelector('.steps-container');
                if (stepsContainer) {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(line, 'text/html');
                    const stepContent = doc.querySelector('.processing-step');
                    if (stepContent) {
                        stepsContainer.appendChild(stepContent);
                        smoothScrollToBottom();
                    }
                }
            }
        });
    }
});

document.body.addEventListener('htmx:error', function(evt) {
    isProcessing = false;
    const input = document.querySelector('#query');
    input.disabled = false;
    
    const messagesContainer = document.querySelector('#messages-container');
    const errorMessage = `
        <div class="message system-message error-message animate-message">
            <div class="message-avatar">
                <img src="/static/images/bot-avatar.jpeg" alt="AirlineSQL" width="36" height="36">
            </div>
            <div class="message-content">
                <p>Sorry, something went wrong. Please try again.</p>
                <div class="message-timestamp">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
            </div>
        </div>
    `;
    messagesContainer.insertAdjacentHTML('beforeend', errorMessage);
    smoothScrollToBottom();
});

function smoothScrollToBottom() {
    const chatMessages = document.querySelector('.chat-messages');
    chatMessages.scrollTo({
        top: chatMessages.scrollHeight,
        behavior: 'smooth'
    });
}

// Add resize observer for mobile
const resizeObserver = new ResizeObserver(() => {
    const chatMessages = document.querySelector('.chat-messages');
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});

resizeObserver.observe(document.body);