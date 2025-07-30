class ChatBot {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.chatMessages = document.getElementById('chatMessages');
        this.userInput = document.getElementById('userInput');
        this.sendButton = document.getElementById('sendButton');
        this.loading = document.getElementById('loading');
        
        this.bindEvents();
        this.startConversation();
    }
    
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    bindEvents() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }
    
    async startConversation() {
        try {
            const response = await fetch('/api/chat/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ session_id: this.sessionId })
            });
            
            const data = await response.json();
            
            if (data.success && data.message) {
                this.addMessage(data.message, 'bot');
                this.enableInput();
            }
        } catch (error) {
            console.error('Error starting conversation:', error);
            this.addMessage('Sorry, I encountered an error. Please refresh and try again.', 'bot');
        }
    }
    
    async sendMessage() {
        const message = this.userInput.value.trim();
        if (!message) return;
        
        this.addMessage(message, 'user');
        this.userInput.value = '';
        this.disableInput();
        this.showLoading();
        
        try {
            const response = await fetch('/api/chat/respond', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    message: message
                })
            });
            
            const data = await response.json();
            this.hideLoading();
            
            if (data.success) {
                this.addMessage(data.message, 'bot');
                
                if (data.completed) {
                    this.handleConversationComplete(data);
                } else {
                    this.enableInput();
                }
            } else {
                this.addMessage(data.message || 'Sorry, I encountered an error. Please try again.', 'bot');
                this.enableInput();
            }
        } catch (error) {
            this.hideLoading();
            console.error('Error sending message:', error);
            this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            this.enableInput();
        }
    }
    
    addMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = text;
        
        messageDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    handleConversationComplete(data) {
        if (data.fraud_analysis) {
            setTimeout(() => {
                this.addMessage('Based on your responses, here is my fraud risk assessment:', 'bot');
                setTimeout(() => {
                    this.addMessage(data.fraud_analysis, 'bot');
                }, 1000);
            }, 1000);
        }
        this.disableInput();
    }
    
    enableInput() {
        this.userInput.disabled = false;
        this.sendButton.disabled = false;
        this.userInput.focus();
    }
    
    disableInput() {
        this.userInput.disabled = true;
        this.sendButton.disabled = true;
    }
    
    showLoading() {
        this.loading.style.display = 'flex';
    }
    
    hideLoading() {
        this.loading.style.display = 'none';
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ChatBot();
});