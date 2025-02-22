document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('query-form');
    const input = document.getElementById('query');
    const messagesContainer = document.getElementById('messages-container');
    const chatMessages = document.querySelector('.chat-messages');
    const queryChips = document.querySelectorAll('.query-chip');
    
    // Handle query chip clicks
    queryChips.forEach(chip => {
        chip.addEventListener('click', function() {
            input.value = this.dataset.query;
            input.focus();
        });
    });
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const query = input.value.trim();
        if (!query) return;
        
        // Add user message with enhanced animation
        const userMessage = `
            <div class="message user-message animate-message">
                <div class="message-avatar">
                    <img src="/static/images/user-avatar.svg" alt="User" width="40" height="40">
                </div>
                <div class="message-content">
                    <p>${query}</p>
                </div>
            </div>
        `;
        messagesContainer.insertAdjacentHTML('beforeend', userMessage);
        
        // Clear input
        input.value = '';
        
        // Scroll to bottom with smooth animation
        setTimeout(() => {
            chatMessages.scrollTo({
                top: chatMessages.scrollHeight,
                behavior: 'smooth'
            });
        }, 50);
        
        // Show loading indicator with enhanced styling
        const loadingMessage = `
            <div class="message system-message animate-message" id="loading-message">
                <div class="message-avatar">
                    <img src="/static/images/bot-avatar.jpeg" alt="AirlineSQL" width="40" height="40">
                </div>
                <div class="message-content">
                    <div class="loading-indicator">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            </div>
        `;
        messagesContainer.insertAdjacentHTML('beforeend', loadingMessage);
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
        
        // Send AJAX request
        fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'text/event-stream',
                'HX-Request': 'true'
            },
            body: `query=${encodeURIComponent(query)}`
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(html => {
            // Remove loading indicator
            const loadingMessage = document.getElementById('loading-message');
            if (loadingMessage) {
                loadingMessage.remove();
            }
            
            // Add response to the chat
            messagesContainer.insertAdjacentHTML('beforeend', html);
            
            // Highlight code blocks if any
            if (typeof hljs !== 'undefined') {
                document.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightBlock(block);
                });
            }
            
            // Scroll to bottom again with smooth animation
            setTimeout(() => {
                chatMessages.scrollTo({
                    top: chatMessages.scrollHeight,
                    behavior: 'smooth'
                });
            }, 50);
        })
        .catch(error => {
            console.error('Error:', error);
            
            // Remove loading indicator
            const loadingMessage = document.getElementById('loading-message');
            if (loadingMessage) {
                loadingMessage.remove();
            }
            
            // Show error message with enhanced styling
            const errorMessage = `
                <div class="message system-message error-message animate-message">
                    <div class="message-avatar">
                        <img src="/static/images/bot-avatar.jpeg" alt="AirlineSQL" width="40" height="40">
                    </div>
                    <div class="message-content" style="border-left: 3px solid var(--error-color);">
                        <p>Sorry, I encountered an error processing your request. Please try again.</p>
                    </div>
                </div>
            `;
            messagesContainer.insertAdjacentHTML('beforeend', errorMessage);
            chatMessages.scrollTo({
                top: chatMessages.scrollHeight,
                behavior: 'smooth'
            });
        });
    });
    
    // Add focus animation to input
    input.addEventListener('focus', function() {
        this.parentElement.classList.add('input-focused');
    });
    
    input.addEventListener('blur', function() {
        this.parentElement.classList.remove('input-focused');
    });
});