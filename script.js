// Form submission handling
document.addEventListener('DOMContentLoaded', function() {
    console.log('Script loaded and running');
    
    // Newsletter form
    const newsletterForm = document.querySelector('.newsletter form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const emailInput = this.querySelector('input[type="email"]');
            const email = emailInput.value.trim();
            
            if (!email) {
                showFormMessage(this, 'Please enter your email address', 'error');
                return;
            }
            
            try {
                const response = await fetch('https://formspree.io/f/xblgwqlg', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email })
                });
                
                if (response.ok) {
                    showFormMessage(this, 'Thank you for subscribing!', 'success');
                    emailInput.value = '';
                } else {
                    throw new Error('Failed to subscribe');
                }
            } catch (error) {
                showFormMessage(this, 'An error occurred. Please try again later.', 'error');
                console.error('Newsletter subscription error:', error);
            }
        });
    }
    
    // Contact form
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = Object.fromEntries(formData.entries());
            
            try {
                const response = await fetch('https://formspree.io/f/xblgwqlg', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    showFormMessage(this, 'Thank you for your message! We\'ll get back to you soon.', 'success');
                    this.reset();
                } else {
                    throw new Error('Failed to send message');
                }
            } catch (error) {
                showFormMessage(this, 'An error occurred. Please try again later.', 'error');
                console.error('Contact form submission error:', error);
            }
        });
    }

    const chatToggle = document.querySelector('.chat-toggle-button');
    const chatbotContainer = document.querySelector('.chatbot-container');
    const chatbotClose = document.querySelector('.chatbot-toggle');
    const chatInput = document.querySelector('.chatbot-input input');
    const sendButton = document.querySelector('.send-button');
    const messagesContainer = document.querySelector('.chatbot-messages');
    let isProcessing = false;

    console.log('Chat elements:', {
        chatToggle: chatToggle,
        chatbotContainer: chatbotContainer,
        chatbotClose: chatbotClose
    });

    // Toggle chatbot visibility
    chatToggle.addEventListener('click', () => {
        console.log('Chat toggle clicked - Opening chat');
        chatbotContainer.classList.add('open');
        chatToggle.style.display = 'none';
        chatInput.focus(); // Focus the input when opening
    });

    chatbotClose.addEventListener('click', () => {
        console.log('Chat close clicked - Closing chat');
        chatbotContainer.classList.remove('open');
        chatToggle.style.display = 'flex';
    });

    // Handle sending messages
    async function sendMessage() {
        const message = chatInput.value.trim();
        if (message && !isProcessing) {
            isProcessing = true;
            
            // Add user message
            addMessage(message, 'user');
            chatInput.value = '';
            
            // Show typing indicator
            const typingIndicator = document.createElement('div');
            typingIndicator.classList.add('typing-indicator');
            typingIndicator.innerHTML = '<span></span><span></span><span></span>';
            messagesContainer.appendChild(typingIndicator);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                
                // Remove typing indicator
                typingIndicator.remove();
                
                if (data.error) {
                    addMessage("I'm sorry, I'm having trouble processing your request. Please try again.", 'bot');
                } else {
                    addMessage(data.response, 'bot');
                }
            } catch (error) {
                console.error('Error:', error);
                typingIndicator.remove();
                addMessage("I'm sorry, I'm having trouble connecting to the server. Please try again.", 'bot');
            }
            
            isProcessing = false;
        }
    }

    // Add message to chat
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chatbot-message', `${sender}-message`);
        
        // Convert URLs to clickable links
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        const formattedText = text.replace(urlRegex, url => `<a href="${url}" target="_blank">${url}</a>`);
        
        // Convert line breaks to <br> tags
        const textWithBreaks = formattedText.replace(/\n/g, '<br>');
        
        messageDiv.innerHTML = `<p>${textWithBreaks}</p>`;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Send message on button click
    sendButton.addEventListener('click', sendMessage);

    // Send message on Enter key
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Add initial bot message
    addMessage("Hello! I'm your AI assistant for LinkedIn AI News Poster. How can I help you today?", 'bot');
});

// Helper function to show form messages
function showFormMessage(form, message, type) {
    let messageElement = form.querySelector('.form-message');
    
    if (!messageElement) {
        messageElement = document.createElement('div');
        messageElement.className = 'form-message';
        form.appendChild(messageElement);
    }
    
    messageElement.textContent = message;
    messageElement.className = `form-message ${type}`;
    
    // Remove message after 5 seconds
    setTimeout(() => {
        messageElement.remove();
    }, 5000);
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            targetElement.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Mobile menu toggle
const mobileMenuButton = document.querySelector('.mobile-menu-button');
const nav = document.querySelector('nav ul');

if (mobileMenuButton && nav) {
    mobileMenuButton.addEventListener('click', function() {
        nav.classList.toggle('show');
        this.classList.toggle('active');
    });
}

// Intersection Observer for fade-in animations
const fadeElements = document.querySelectorAll('.fade-in');
const fadeObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            fadeObserver.unobserve(entry.target);
        }
    });
}, {
    threshold: 0.1
});

fadeElements.forEach(element => {
    fadeObserver.observe(element);
});

// Pricing toggle
const pricingToggle = document.querySelector('.pricing-toggle');
const pricingCards = document.querySelectorAll('.pricing-card');

if (pricingToggle && pricingCards.length > 0) {
    pricingToggle.addEventListener('change', function() {
        const isAnnual = this.checked;
        
        pricingCards.forEach(card => {
            const monthlyPrice = card.getAttribute('data-monthly');
            const annualPrice = card.getAttribute('data-annual');
            
            const priceElement = card.querySelector('.price');
            if (priceElement) {
                priceElement.innerHTML = isAnnual ? 
                    `$${annualPrice}<span>/year</span>` : 
                    `$${monthlyPrice}<span>/month</span>`;
            }
        });
    });
}

// Form validation
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validateForm(form) {
    let isValid = true;
    const emailInputs = form.querySelectorAll('input[type="email"]');
    
    emailInputs.forEach(input => {
        if (!validateEmail(input.value.trim())) {
            showFormMessage(form, 'Please enter a valid email address', 'error');
            isValid = false;
        }
    });
    
    return isValid;
}

// Add loading state to buttons
function setLoadingState(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner"></span> Sending...';
    } else {
        button.disabled = false;
        button.innerHTML = button.getAttribute('data-original-text') || 'Submit';
    }
}

// Initialize tooltips
const tooltips = document.querySelectorAll('[data-tooltip]');
tooltips.forEach(element => {
    element.addEventListener('mouseenter', function() {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = this.getAttribute('data-tooltip');
        
        document.body.appendChild(tooltip);
        
        const rect = this.getBoundingClientRect();
        tooltip.style.top = `${rect.top - tooltip.offsetHeight - 5}px`;
        tooltip.style.left = `${rect.left + (rect.width - tooltip.offsetWidth) / 2}px`;
    });
    
    element.addEventListener('mouseleave', function() {
        const tooltip = document.querySelector('.tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    });
}); 