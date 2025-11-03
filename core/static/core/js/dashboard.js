// Dashboard.js - Handles all client-side functionality for the AgriGuide dashboard

document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initLanguageSelector();
    initCropPrediction();
    initChatbot();
    
    // Set up navigation
    setupNavigation();
});

// Language selection functionality
function initLanguageSelector() {
    const languageSelector = document.getElementById('language-selector');
    if (languageSelector) {
        languageSelector.addEventListener('change', function() {
            const selectedLanguage = this.value;
            // Store language preference
            localStorage.setItem('agriGuideLanguage', selectedLanguage);
            // Update UI language (would require more comprehensive implementation)
            console.log(`Language changed to: ${selectedLanguage}`);
        });
        
        // Set initial value from localStorage if available
        const savedLanguage = localStorage.getItem('agriGuideLanguage');
        if (savedLanguage) {
            languageSelector.value = savedLanguage;
        }
    }
}

// Crop prediction functionality
function initCropPrediction() {
    const predictionForm = document.getElementById('crop-prediction-form');
    const resultContainer = document.getElementById('prediction-result');
    
    if (predictionForm) {
        predictionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show loading state
            resultContainer.innerHTML = '<div class="text-center"><div class="spinner-border text-success" role="status"></div><p>Analyzing soil and weather data...</p></div>';
            
            // Collect form data
            const formData = {
                nitrogen: document.getElementById('nitrogen').value,
                phosphorus: document.getElementById('phosphorus').value,
                potassium: document.getElementById('potassium').value,
                temperature: document.getElementById('temperature').value,
                humidity: document.getElementById('humidity').value,
                ph: document.getElementById('ph').value,
                rainfall: document.getElementById('rainfall').value
            };
            
            // Send data to API
            fetch('/api/crop-prediction/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                // Display prediction result
                if (data.crop) {
                    resultContainer.innerHTML = `
                        <div class="alert alert-success">
                            <h4 class="alert-heading">Recommended Crop: ${data.crop}</h4>
                            <p>${data.description}</p>
                        </div>
                    `;
                } else if (data.error) {
                    resultContainer.innerHTML = `
                        <div class="alert alert-danger">
                            <h4 class="alert-heading">Error</h4>
                            <p>${data.error}</p>
                        </div>
                    `;
                }
            })
            .catch(error => {
                resultContainer.innerHTML = `
                    <div class="alert alert-danger">
                        <h4 class="alert-heading">Error</h4>
                        <p>Failed to get prediction: ${error.message}</p>
                    </div>
                `;
            });
        });
    }
}

// Chatbot functionality
function initChatbot() {
    const chatForm = document.getElementById('chat-form');
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message-input');
    
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const message = messageInput.value.trim();
            if (!message) return;
            
            // Add user message to chat
            addMessage('user', message);
            messageInput.value = '';
            
            // Show typing indicator
            const typingIndicator = document.createElement('div');
            typingIndicator.className = 'message-container bot-typing';
            typingIndicator.innerHTML = `
                <div class="message bot-message">
                    <div class="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            `;
            chatMessages.appendChild(typingIndicator);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // Get language preference
            const languageSelector = document.getElementById('language-selector');
            const language = languageSelector ? languageSelector.value : 'en';
            
            // Send message to API
            fetch('/api/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    message: message,
                    language: language
                })
            })
            .then(response => response.json())
            .then(data => {
                // Remove typing indicator
                chatMessages.removeChild(typingIndicator);
                
                // Add bot response
                if (data.response) {
                    addMessage('bot', data.response);
                } else if (data.error) {
                    addMessage('bot', `Sorry, I encountered an error: ${data.error}`);
                }
            })
            .catch(error => {
                // Remove typing indicator
                chatMessages.removeChild(typingIndicator);
                
                // Add error message
                addMessage('bot', `Sorry, I couldn't process your request: ${error.message}`);
            });
        });
    }
}

// Helper function to add a message to the chat
function addMessage(sender, text) {
    const chatMessages = document.getElementById('chat-messages');
    const messageContainer = document.createElement('div');
    messageContainer.className = `message-container ${sender}-message-container`;
    
    messageContainer.innerHTML = `
        <div class="message ${sender}-message">
            <p>${text}</p>
            <small class="message-time">${new Date().toLocaleTimeString()}</small>
        </div>
    `;
    
    chatMessages.appendChild(messageContainer);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Setup navigation between sections
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.dashboard-section');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get target section
            const targetId = this.getAttribute('data-target');
            
            // Hide all sections
            sections.forEach(section => {
                section.classList.remove('active');
            });
            
            // Show target section
            document.getElementById(targetId).classList.add('active');
            
            // Update active nav link
            navLinks.forEach(navLink => {
                navLink.classList.remove('active');
            });
            this.classList.add('active');
        });
    });
    
    // Set initial active section
    if (navLinks.length > 0 && sections.length > 0) {
        navLinks[0].classList.add('active');
        sections[0].classList.add('active');
    }
}

// Helper function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}