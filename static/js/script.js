document.addEventListener('DOMContentLoaded', () => {
    // Chat toggle functionality
    const chatToggleButton = document.querySelector('.chat-toggle-button');
    const chatbotContainer = document.querySelector('.chatbot-container');
    const chatbotToggle = document.querySelector('.chatbot-toggle');
    const chatMessages = document.querySelector('.chatbot-messages');
    const chatInput = document.querySelector('.chatbot-input input');
    const sendButton = document.querySelector('.send-button');
    const registrationForm = document.querySelector('.registration-form');
    const chatInputContainer = document.querySelector('.chatbot-input');
    const openChatButton = document.getElementById('openChat');

    let isProcessing = false;
    let userEmail = localStorage.getItem('userEmail');

    // Hide chat input until registered
    if (!userEmail) {
        chatInputContainer.style.display = 'none';
        chatMessages.style.display = 'none';
    } else {
        registrationForm.classList.add('hidden');
        chatInputContainer.style.display = 'flex';
        chatMessages.style.display = 'flex';
    }

    function toggleChat() {
        chatbotContainer.classList.toggle('active');
        chatToggleButton.classList.toggle('hidden');
    }

    chatToggleButton.addEventListener('click', toggleChat);
    chatbotToggle.addEventListener('click', toggleChat);
    if (openChatButton) {
        openChatButton.addEventListener('click', (e) => {
            e.preventDefault();
            if (!chatbotContainer.classList.contains('active')) {
                toggleChat();
            }
        });
    }

    // Add registration form HTML dynamically
    function addRegistrationForm() {
        const chatMessages = document.getElementById('chat-messages');
        const registrationForm = document.createElement('div');
        registrationForm.className = 'registration-form';
        registrationForm.innerHTML = `
            <h3>Welcome to LinkedIn AI News Poster</h3>
            <p>Please register to start chatting:</p>
            <form id="registration-form">
                <input type="text" id="reg-name" placeholder="Your Name" required>
                <input type="email" id="reg-email" placeholder="Your Email" required>
                <button type="submit">Register</button>
            </form>
        `;
        chatMessages.appendChild(registrationForm);

        // Handle registration form submission
        document.getElementById('registration-form').addEventListener('submit', async (e) => {
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
                } else {
                    alert(data.error || 'Registration failed. Please try again.');
                }
            } catch (error) {
                alert('Error during registration. Please try again.');
            }
        });
    }

    // Initialize chat interface
    function initializeChat() {
        if (!userEmail) {
            addRegistrationForm();
        } else {
            addMessage('Welcome back! How can I help you today?', 'bot');
        }
    }

    // Update sendMessage function
    async function sendMessage() {
        if (isProcessing) return;
        
        const messageInput = document.getElementById('message-input');
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
        typingIndicator.className = 'message bot typing';
        typingIndicator.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
        document.getElementById('chat-messages').appendChild(typingIndicator);

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
                } else {
                    addMessage('Sorry, I encountered an error. Please try again later.', 'bot');
                }
            }
        } catch (error) {
            typingIndicator.remove();
            addMessage('Sorry, I encountered an error. Please try again later.', 'bot');
        }

        isProcessing = false;
    }

    function addMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        // Convert URLs to clickable links
        content = content.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
        
        // Replace line breaks with <br> tags
        content = content.replace(/\n/g, '<br>');
        
        messageDiv.innerHTML = content;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Event listeners for sending messages
    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Initialize chat when the page loads
    initializeChat();
});

// Newsletter form submission
const newsletterForm = document.querySelector('.newsletter form');
if (newsletterForm) {
    newsletterForm.addEventListener('submit', (e) => {
        e.preventDefault();
        alert('Thank you for subscribing to our newsletter!');
        newsletterForm.reset();
    });
}

// Contact form submission
const contactForm = document.querySelector('.contact form');
if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        alert('Thank you for your message. We\'ll get back to you soon!');
        contactForm.reset();
    });
} 