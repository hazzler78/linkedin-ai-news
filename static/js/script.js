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

    // Registration form handling
    const registrationFormElement = document.getElementById('chatRegistrationForm');
    registrationFormElement.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const nameInput = document.getElementById('regName');
        const emailInput = document.getElementById('regEmail');
        
        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: nameInput.value,
                    email: emailInput.value
                }),
            });

            const data = await response.json();
            
            if (response.ok) {
                // Store email for future use
                localStorage.setItem('userEmail', emailInput.value);
                userEmail = emailInput.value;
                
                // Hide registration form and show chat
                registrationForm.classList.add('hidden');
                chatInputContainer.style.display = 'flex';
                chatMessages.style.display = 'flex';
                
                // Add welcome message
                addMessage('bot', 'Thank you for registering! How can I help you today?');
            } else {
                alert(data.error || 'Registration failed. Please try again.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Registration failed. Please try again.');
        }
    });

    async function sendMessage() {
        if (isProcessing || !userEmail) return;

        const message = chatInput.value.trim();
        if (!message) return;

        // Clear input
        chatInput.value = '';

        // Add user message
        addMessage('user', message);

        // Show typing indicator
        isProcessing = true;
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing';
        typingDiv.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    message,
                    email: userEmail
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to get response');
            }

            const data = await response.json();
            
            // Remove typing indicator
            typingDiv.remove();
            
            // Add bot message
            addMessage('bot', data.response);
        } catch (error) {
            console.error('Error:', error);
            typingDiv.remove();
            addMessage('bot', 'Sorry, I encountered an error. Please try again.');
        } finally {
            isProcessing = false;
        }
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

    // Add initial bot message if user is not registered
    if (!userEmail) {
        addMessage('bot', 'Welcome! Please register to start chatting with our AI News Assistant.');
    }
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