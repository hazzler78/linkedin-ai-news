import config from './config.js';

document.addEventListener('DOMContentLoaded', () => {
    const chatToggle = document.querySelector('.chat-toggle-button');
    const chatbotContainer = document.querySelector('.chatbot-container');
    const chatbotClose = document.querySelector('.chatbot-toggle');
    const chatInput = document.querySelector('.chatbot-input input');
    const sendButton = document.querySelector('.send-button');
    const messagesContainer = document.querySelector('.chatbot-messages');
    let isProcessing = false;

    // Check if we're on GitHub Pages
    const isGitHubPages = window.location.hostname.includes('github.io');
    
    if (isGitHubPages) {
        // Show a message about the demo limitations
        addMessage("Note: This is a demo version. For full chat functionality, please run the application locally or use our deployed version.", false);
    }

    // Toggle chat visibility
    chatToggle.addEventListener('click', () => {
        chatbotContainer.classList.add('open');
        chatToggle.style.display = 'none';
        chatInput.focus();
    });

    chatbotClose.addEventListener('click', () => {
        chatbotContainer.classList.remove('open');
        chatToggle.style.display = 'flex';
    });

    // Function to add a message to the chat
    function addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chatbot-message');
        messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');
        
        // Convert URLs to clickable links and handle line breaks
        const messageText = message.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
        messageDiv.innerHTML = `<p>${messageText.replace(/\n/g, '<br>')}</p>`;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Function to show/hide typing indicator
    function toggleTypingIndicator(show) {
        let indicator = document.querySelector('.typing-indicator');
        if (show) {
            if (!indicator) {
                indicator = document.createElement('div');
                indicator.className = 'typing-indicator';
                indicator.innerHTML = '<span></span><span></span><span></span>';
                messagesContainer.appendChild(indicator);
            }
        } else if (indicator) {
            indicator.remove();
        }
        if (indicator) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    // Function to send message
    async function sendMessage() {
        if (isProcessing || !chatInput.value.trim()) return;
        
        const message = chatInput.value.trim();
        chatInput.value = '';
        
        addMessage(message, true);
        isProcessing = true;
        toggleTypingIndicator(true);

        try {
            if (isGitHubPages && !config.production.apiUrl.startsWith('https://')) {
                // If we're on GitHub Pages and don't have a proper backend URL
                setTimeout(() => {
                    toggleTypingIndicator(false);
                    addMessage("I'm a demo version running on GitHub Pages. To use the full chat functionality, please run the application locally or use our deployed version. Visit our GitHub repository for setup instructions.");
                    isProcessing = false;
                }, 1000);
                return;
            }

            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            toggleTypingIndicator(false);
            addMessage(data.response);
        } catch (error) {
            console.error('Error:', error);
            toggleTypingIndicator(false);
            addMessage('Sorry, I encountered an error. Please try again.');
        } finally {
            isProcessing = false;
        }
    }

    // Event listeners for sending messages
    sendButton.addEventListener('click', sendMessage);

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Add initial greeting
    addMessage('Hello! I\'m your AI News Assistant. How can I help you today?', false);
}); 