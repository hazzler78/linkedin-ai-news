class Chatbot {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.init();
    }

    init() {
        // Create chatbot container
        this.container = document.createElement('div');
        this.container.className = 'chatbot-container';
        this.container.innerHTML = `
            <div class="chatbot-header">
                <h3>AI Assistant</h3>
                <button class="chatbot-toggle">×</button>
            </div>
            <div class="chatbot-messages"></div>
            <div class="chatbot-input">
                <input type="text" placeholder="Type your message...">
                <button class="send-button">Send</button>
            </div>
        `;
        document.body.appendChild(this.container);

        // Add event listeners
        this.toggleButton = this.container.querySelector('.chatbot-toggle');
        this.input = this.container.querySelector('input');
        this.sendButton = this.container.querySelector('.send-button');
        this.messagesContainer = this.container.querySelector('.chatbot-messages');

        this.toggleButton.addEventListener('click', () => this.toggle());
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });

        // Add initial message
        this.addMessage('Hello! I\'m your AI assistant. How can I help you today?', 'bot');
    }

    toggle() {
        this.isOpen = !this.isOpen;
        this.container.classList.toggle('open', this.isOpen);
        if (this.isOpen) {
            this.input.focus();
        }
    }

    async sendMessage() {
        const message = this.input.value.trim();
        if (!message) return;

        // Add user message
        this.addMessage(message, 'user');
        this.input.value = '';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Call your AI backend here
            const response = await this.getAIResponse(message);
            this.hideTypingIndicator();
            this.addMessage(response, 'bot');
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            console.error('Chatbot error:', error);
        }
    }

    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chatbot-message ${sender}-message`;
        
        // Handle newlines in the text
        if (text.includes('\n')) {
            const lines = text.split('\n');
            lines.forEach((line, index) => {
                if (line.trim()) {
                    const p = document.createElement('p');
                    p.textContent = line;
                    messageDiv.appendChild(p);
                }
            });
        } else {
            messageDiv.textContent = text;
        }
        
        this.messagesContainer.appendChild(messageDiv);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        indicator.innerHTML = '<span></span><span></span><span></span>';
        this.messagesContainer.appendChild(indicator);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    hideTypingIndicator() {
        const indicator = this.messagesContainer.querySelector('.typing-indicator');
        if (indicator) indicator.remove();
    }

    async getAIResponse(message) {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });

        if (!response.ok) {
            throw new Error('Failed to get AI response');
        }

        const data = await response.json();
        return data.response;
    }
}

// Initialize chatbot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new Chatbot();
}); 