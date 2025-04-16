document.addEventListener('DOMContentLoaded', () => {
    // Chat toggle functionality
    const chatToggleButton = document.querySelector('.chat-toggle-button');
    const chatbotContainer = document.querySelector('.chatbot-container');
    const chatbotToggle = document.querySelector('.chatbot-toggle');
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.querySelector('.send-button');

    let isProcessing = false;
    let userEmail = localStorage.getItem('userEmail');

    function toggleChat() {
        chatbotContainer.classList.toggle('active');
        if (chatToggleButton) {
            chatToggleButton.classList.toggle('hidden');
        }
    }

    if (chatToggleButton) {
        chatToggleButton.addEventListener('click', toggleChat);
    }
    if (chatbotToggle) {
        chatbotToggle.addEventListener('click', toggleChat);
    }

    const openChatButton = document.getElementById('openChat');
    if (openChatButton) {
        openChatButton.addEventListener('click', (e) => {
            e.preventDefault();
            if (!chatbotContainer.classList.contains('active')) {
                toggleChat();
            }
        });
    }

    // Add message to chat
    function addMessage(message, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type === 'bot' ? 'assistant' : type}`;
        
        // Convert URLs to clickable links
        let content = message.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
        
        // Replace line breaks with <br> tags
        content = content.replace(/\n/g, '<br>');
        
        messageDiv.innerHTML = content;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Add registration form
    function addRegistrationForm() {
        const registrationForm = document.createElement('div');
        registrationForm.className = 'registration-form';
        registrationForm.innerHTML = `
            <h3>Welcome to LinkedIn AI News Poster</h3>
            <p>Please register to start chatting:</p>
            <form id="chat-registration-form">
                <input type="text" id="reg-name" placeholder="Your Name" required>
                <input type="email" id="reg-email" placeholder="Your Email" required>
                <button type="submit">Register</button>
            </form>
        `;
        chatMessages.appendChild(registrationForm);

        // Handle registration form submission
        document.getElementById('chat-registration-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('reg-name').value;
            const email = document.getElementById('reg-email').value;

            try {
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ name, email })
                });

                const data = await response.json();
                if (response.ok) {
                    localStorage.setItem('userEmail', email);
                    userEmail = email;
                    registrationForm.remove();
                    addMessage('Registration successful! How can I help you today?', 'bot');
                    // Show message input after successful registration
                    const messageContainer = document.querySelector('.message-container');
                    if (messageContainer) {
                        messageContainer.style.display = 'flex';
                    }
                } else {
                    alert(data.error || 'Registration failed. Please try again.');
                }
            } catch (error) {
                console.error('Registration error:', error);
                alert('Error during registration. Please try again.');
            }
        });
    }

    // Initialize chat interface
    function initializeChat() {
        if (!userEmail) {
            addRegistrationForm();
            // Hide message input until registered
            const messageContainer = document.querySelector('.message-container');
            if (messageContainer) {
                messageContainer.style.display = 'none';
            }
        } else {
            addMessage('Welcome back! How can I help you today?', 'bot');
        }
    }

    // Send message function
    async function sendMessage() {
        if (isProcessing || !messageInput) return;
        
        const message = messageInput.value.trim();
        if (!message) return;
        
        if (!userEmail) {
            alert('Please register first to use the chat.');
            return;
        }

        isProcessing = true;
        messageInput.value = '';

        // Add user message
        addMessage(message, 'user');

        // Add typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'message typing';
        typingIndicator.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
        chatMessages.appendChild(typingIndicator);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    message: message,
                    email: userEmail
                })
            });

            // Remove typing indicator
            typingIndicator.remove();

            const data = await response.json();
            if (response.ok) {
                addMessage(data.response, 'bot');
            } else {
                if (response.status === 401) {
                    localStorage.removeItem('userEmail');
                    userEmail = null;
                    addRegistrationForm();
                    addMessage('Your session has expired. Please register again.', 'bot');
                    // Hide message input
                    const messageContainer = document.querySelector('.message-container');
                    if (messageContainer) {
                        messageContainer.style.display = 'none';
                    }
                } else {
                    addMessage('Sorry, I encountered an error. Please try again later.', 'bot');
                }
            }
        } catch (error) {
            console.error('Chat error:', error);
            typingIndicator.remove();
            addMessage('Sorry, I encountered an error. Please try again later.', 'bot');
        }

        isProcessing = false;
    }

    // Event listeners for sending messages
    if (sendButton && messageInput) {
        sendButton.addEventListener('click', sendMessage);
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    // Initialize chat
    initializeChat();
});

// Newsletter form submission
const newsletterForm = document.getElementById('newsletter-form');
if (newsletterForm) {
    newsletterForm.addEventListener('submit', (e) => {
        e.preventDefault();
        alert('Thank you for subscribing to our newsletter!');
        newsletterForm.reset();
    });
}

// Contact form submission
const contactForm = document.getElementById('contact-form');
if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        alert('Thank you for your message! We will get back to you soon.');
        contactForm.reset();
    });
} 