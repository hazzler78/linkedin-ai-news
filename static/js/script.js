// Get the base URL for API calls
const BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? '' 
    : window.location.origin;

// Add debug logging for API URLs
console.log('Current hostname:', window.location.hostname);
console.log('Using BASE_URL:', BASE_URL);

// Function to handle API responses
function handleApiResponse(response, errorMessage = 'An error occurred') {
    if (response.status === 503) {
        throw new Error('Database service is currently unavailable. Please check if the environment variables are properly set.');
    }
    if (!response.ok) {
        throw new Error(`${errorMessage} (Status: ${response.status})`);
    }
    return response;
}

document.addEventListener('DOMContentLoaded', () => {
    // Chat toggle functionality
    const chatToggleButton = document.querySelector('.chat-toggle-button');
    const chatbotContainer = document.querySelector('.chatbot-container');
    const chatbotToggle = document.querySelector('.chatbot-toggle');
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.querySelector('.send-button');
    const messageContainer = document.querySelector('.message-container');

    let isProcessing = false;
    let userEmail = localStorage.getItem('userEmail');

    // Add error handling for fetch requests
    async function handleFetchWithRetry(url, options, retries = 3) {
        for (let i = 0; i < retries; i++) {
            try {
                console.log(`Attempting request to ${url} (attempt ${i + 1}/${retries})`);
                const response = await fetch(url, options);
                console.log(`Response status: ${response.status}`);
                
                if (!response.ok) {
                    const text = await response.text();
                    console.log(`Error response body: ${text}`);
                    throw new Error(`HTTP error! status: ${response.status}, body: ${text}`);
                }
                
                const data = await response.json();
                return { response, data };
            } catch (error) {
                console.error(`Attempt ${i + 1} failed:`, error);
                if (i === retries - 1) throw error;
                await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
            }
        }
    }

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
        if (!message) {
            console.error('Attempted to add undefined or null message');
            message = "An error occurred while processing the message.";
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type === 'bot' ? 'assistant' : type}`;
        
        try {
            // Convert message to string and handle special characters
            let content = String(message)
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>')
                .replace(/\n/g, '<br>');
            
            messageDiv.innerHTML = content;
        } catch (error) {
            console.error('Error formatting message:', error);
            messageDiv.textContent = "An error occurred while displaying the message.";
        }
        
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
                console.log('Attempting registration with email:', email);
                const { response, data } = await handleFetchWithRetry(`${BASE_URL}/api/register`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ name, email })
                });

                if (response.ok) {
                    console.log('Registration successful');
                    localStorage.setItem('userEmail', email);
                    userEmail = email;
                    registrationForm.remove();
                    addMessage('Registration successful! How can I help you today?', 'assistant');
                    if (messageContainer) {
                        messageContainer.style.display = 'flex';
                    }
                } else {
                    console.error('Registration failed:', data.error);
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
            if (messageContainer) {
                messageContainer.style.display = 'none';
            }
        } else {
            addMessage('Welcome back! How can I help you today?', 'bot');
            if (messageContainer) {
                messageContainer.style.display = 'flex';
            }
        }
    }

    function showTypingIndicator() {
        const messagesContainer = document.getElementById('chat-messages');
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        typingIndicator.innerHTML = `
            <span></span>
            <span></span>
            <span></span>
        `;
        messagesContainer.appendChild(typingIndicator);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function removeTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    async function sendMessage() {
        const messageInput = document.getElementById('message-input');
        const message = messageInput.value.trim();
        const userEmail = localStorage.getItem('userEmail');
        
        if (!message) return;
        
        // Add user message to chat
        addMessage(message, 'user');
        messageInput.value = '';
        
        // Show typing indicator
        showTypingIndicator();
        
        try {
            console.log('Sending message with email:', userEmail);
            const { response, data } = await handleFetchWithRetry(`${BASE_URL}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: userEmail,
                    message: message
                })
            });
            
            removeTypingIndicator();
            
            if (data.error) {
                addMessage(data.error, 'error');
                if (data.error === 'Please register first') {
                    console.log('User needs to register, clearing localStorage and showing form');
                    localStorage.removeItem('userEmail');
                    userEmail = null;
                    // Clear existing messages
                    chatMessages.innerHTML = '';
                    // Show registration form
                    addRegistrationForm();
                    if (messageContainer) {
                        messageContainer.style.display = 'none';
                    }
                }
            } else {
                addMessage(data.response, 'assistant');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            removeTypingIndicator();
            
            // Check if the error is a registration error
            if (error.message.includes('Please register first')) {
                console.log('Registration error detected, showing registration form');
                localStorage.removeItem('userEmail');
                userEmail = null;
                // Clear existing messages
                chatMessages.innerHTML = '';
                // Show registration form
                addRegistrationForm();
                if (messageContainer) {
                    messageContainer.style.display = 'none';
                }
            } else {
                addMessage('Sorry, there was an error processing your message. Please try again.', 'error');
            }
        }
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