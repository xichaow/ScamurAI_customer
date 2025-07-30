"""
Simple Flask-based fraud detection chatbot for easier deployment.
"""
import os
import json
import time
from typing import Dict, Optional
from flask import Flask, request, jsonify, render_template_string
import openai

# Set up OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# The 4 fraud detection questions
FRAUD_QUESTIONS = [
    {
        "id": "payment_recipient",
        "question": "Who are you making this payment to? Please provide the name of the person, organization, or company.",
        "validation": "payment_recipient"
    },
    {
        "id": "purpose_of_payment", 
        "question": "What is the purpose of this payment? Please describe what you are paying for (service, product, investment, etc.)",
        "validation": "purpose_of_payment"
    },
    {
        "id": "source_of_payment_link",
        "question": "Where did you get the payment link or payment instructions from? Please share the source (email, website, text message, social media post, etc.)",
        "validation": "source_of_payment_link"
    },
    {
        "id": "website_verification",
        "question": "Please provide the website URL or platform where you are making this payment, or describe how you are accessing the payment page.",
        "validation": "website_verification"
    }
]

# In-memory session storage
sessions = {}

def validate_response(user_message: str, question: dict) -> bool:
    """Validate if user response is relevant to the current question."""
    if not user_message or len(user_message.strip()) < 3:
        return False
    
    try:
        prompt = f"""
Evaluate if this user response is relevant to the fraud detection question asked.

Question context: {question['validation']}
Question: {question['question']}
User response: {user_message}

Return only "true" if the response is relevant and provides meaningful information related to the question, or "false" if it's off-topic, too vague, or doesn't address the question.

Consider these as VALID responses:
- Specific names, organizations, or entities for recipient questions
- Clear descriptions of services, products, or purposes for purpose questions
- Specific sources like "email from company X", "text message", "website link", "social media post" for source of payment link questions
- URLs or descriptions of websites/platforms for website verification questions

Consider these as INVALID responses:
- Generic responses like "yes", "no", "maybe", "I don't know"
- Single words that don't provide context
- Completely off-topic responses
- Responses that ask questions back instead of answering
"""

        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=10,
            temperature=0
        )
        
        return response['choices'][0]['message']['content'].strip().lower() == 'true'
    except Exception as e:
        print(f"Error validating response: {e}")
        return True

def perform_fraud_analysis(answers: Dict[str, str]) -> str:
    """Perform fraud risk analysis using OpenAI."""
    try:
        prompt = f"""
You are a fraud detection expert. Analyze these payment details and provide a risk assessment.

Payment Details:
- Recipient: {answers.get('payment_recipient', 'Not provided')}
- Purpose: {answers.get('purpose_of_payment', 'Not provided')}
- Source of Payment Link: {answers.get('source_of_payment_link', 'Not provided')}
- Website/Platform: {answers.get('website_verification', 'Not provided')}

Provide a clear, concise fraud risk assessment (LOW, MEDIUM, or HIGH) with a brief explanation of key risk factors or positive indicators. Keep your response under 150 words and focus on actionable insights for the user.

Format your response as:
RISK LEVEL: [LOW/MEDIUM/HIGH]
ANALYSIS: [Your assessment and recommendations]
"""

        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=200,
            temperature=0.3
        )
        
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error performing fraud analysis: {e}")
        return 'RISK LEVEL: UNKNOWN\nANALYSIS: Unable to complete fraud analysis due to technical issues. Please verify payment details independently and consult with your bank if you have concerns.'

@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fraud Detection Chatbot</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px;
        }
        .chat-container {
            background: white; border-radius: 20px; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            width: 100%; max-width: 500px; height: 600px; display: flex; flex-direction: column; overflow: hidden;
        }
        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 30px 25px; text-align: center;
        }
        .chat-header h1 { font-size: 24px; font-weight: 600; margin-bottom: 8px; }
        .chat-header p { font-size: 14px; opacity: 0.9; }
        .chat-messages { 
            flex: 1; padding: 20px; overflow-y: auto; scroll-behavior: smooth; 
        }
        .message { margin-bottom: 20px; animation: fadeIn 0.3s ease-in; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .message-content {
            padding: 15px 20px; border-radius: 18px; max-width: 85%; word-wrap: break-word; line-height: 1.4;
        }
        .bot-message .message-content { background: #f1f3f4; color: #333; margin-right: auto; }
        .user-message .message-content { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; margin-left: auto; 
        }
        .chat-input-container { padding: 20px; border-top: 1px solid #e0e0e0; display: flex; gap: 12px; }
        .chat-input {
            flex: 1; padding: 15px 20px; border: 1px solid #e0e0e0; border-radius: 25px;
            font-size: 16px; outline: none; transition: border-color 0.3s ease;
        }
        .chat-input:focus { border-color: #667eea; }
        .chat-input:disabled { background-color: #f5f5f5; cursor: not-allowed; }
        .send-button {
            padding: 15px 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; border-radius: 25px; font-size: 16px; font-weight: 600;
            cursor: pointer; transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .send-button:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); }
        .send-button:disabled { opacity: 0.5; cursor: not-allowed; transform: none; box-shadow: none; }
        .loading { display: none; justify-content: center; padding: 20px; }
        .loading-dots { display: flex; gap: 5px; }
        .loading-dots span {
            width: 8px; height: 8px; background: #667eea; border-radius: 50%;
            animation: loading 1.4s infinite ease-in-out both;
        }
        .loading-dots span:nth-child(1) { animation-delay: -0.32s; }
        .loading-dots span:nth-child(2) { animation-delay: -0.16s; }
        @keyframes loading { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>Payment Safety Assistant</h1>
            <p>Let me help you verify if your transaction is secure</p>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message bot-message">
                <div class="message-content">
                    Hello! I'm here to help protect you from fraudulent transactions. I'll ask you a few questions to assess the safety of your payment. Let's start!
                </div>
            </div>
        </div>
        
        <div class="chat-input-container">
            <input type="text" id="userInput" class="chat-input" placeholder="Type your response here..." disabled>
            <button id="sendButton" class="send-button" disabled>Send</button>
        </div>
        
        <div class="loading" id="loading">
            <div class="loading-dots"><span></span><span></span><span></span></div>
        </div>
    </div>

    <script>
        class ChatBot {
            constructor() {
                this.sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                this.chatMessages = document.getElementById('chatMessages');
                this.userInput = document.getElementById('userInput');
                this.sendButton = document.getElementById('sendButton');
                this.loading = document.getElementById('loading');
                
                this.bindEvents();
                this.startConversation();
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
                        headers: { 'Content-Type': 'application/json' },
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
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ session_id: this.sessionId, message: message })
                    });
                    
                    const data = await response.json();
                    this.hideLoading();
                    
                    if (data.success) {
                        this.addMessage(data.message, 'bot');
                        if (data.completed && data.fraud_analysis) {
                            setTimeout(() => {
                                this.addMessage('Based on your responses, here is my fraud risk assessment:', 'bot');
                                setTimeout(() => this.addMessage(data.fraud_analysis, 'bot'), 1000);
                            }, 1000);
                            this.disableInput();
                        } else if (!data.completed) {
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
            
            enableInput() { this.userInput.disabled = false; this.sendButton.disabled = false; this.userInput.focus(); }
            disableInput() { this.userInput.disabled = true; this.sendButton.disabled = true; }
            showLoading() { this.loading.style.display = 'flex'; }
            hideLoading() { this.loading.style.display = 'none'; }
            scrollToBottom() { this.chatMessages.scrollTop = this.chatMessages.scrollHeight; }
        }

        document.addEventListener('DOMContentLoaded', () => new ChatBot());
    </script>
</body>
</html>
    """)

@app.route('/api/chat/start', methods=['POST'])
def start_chat():
    """Start a new conversation session."""
    data = request.get_json()
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({'success': False, 'message': 'Session ID is required'}), 400
    
    sessions[session_id] = {
        'current_question_index': 0,
        'answers': {},
        'retry_count': 0,
        'completed': False,
        'start_time': time.time()
    }
    
    return jsonify({
        'success': True,
        'message': FRAUD_QUESTIONS[0]['question'],
        'session_id': session_id
    })

@app.route('/api/chat/respond', methods=['POST'])
def respond_chat():
    """Process user response."""
    data = request.get_json()
    session_id = data.get('session_id')
    user_message = data.get('message')
    
    if not session_id or not user_message:
        return jsonify({'success': False, 'message': 'Session ID and message are required'}), 400
    
    session = sessions.get(session_id)
    if not session:
        return jsonify({'success': False, 'message': 'Session not found. Please refresh and start again.'}), 404
    
    if session['completed']:
        return jsonify({'success': True, 'message': 'Thank you! Your fraud assessment has been completed.', 'completed': True})
    
    current_question = FRAUD_QUESTIONS[session['current_question_index']]
    
    # Validate response relevance
    is_valid_response = validate_response(user_message, current_question)
    
    if not is_valid_response:
        session['retry_count'] += 1
        
        if session['retry_count'] >= 3:
            # Move to next question after 3 failed attempts
            session['retry_count'] = 0
            session['answers'][current_question['id']] = 'User unable to provide relevant answer after multiple attempts'
            return move_to_next_question(session)
        
        contexts = {
            'payment_recipient': 'who you are paying',
            'purpose_of_payment': 'what you are paying for',
            'source_of_payment_link': 'where you got the payment link from',
            'website_verification': 'the website or platform you are using'
        }
        context = contexts.get(current_question['id'], 'this question')
        
        return jsonify({
            'success': True,
            'message': f"I need a more specific answer about {context}. Could you please provide more details?"
        })
    
    # Store valid response
    session['answers'][current_question['id']] = user_message
    session['retry_count'] = 0
    
    return move_to_next_question(session)

def move_to_next_question(session):
    """Move to the next question or complete the conversation."""
    session['current_question_index'] += 1
    
    if session['current_question_index'] >= len(FRAUD_QUESTIONS):
        # All questions completed, perform fraud analysis
        session['completed'] = True
        fraud_analysis = perform_fraud_analysis(session['answers'])
        
        return jsonify({
            'success': True,
            'message': 'Thank you for answering all the questions. Let me analyze this information for potential fraud indicators.',
            'completed': True,
            'fraud_analysis': fraud_analysis
        })
    
    next_question = FRAUD_QUESTIONS[session['current_question_index']]
    return jsonify({
        'success': True,
        'message': next_question['question']
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'fraud-detection-chatbot'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG', 'False').lower() == 'true')