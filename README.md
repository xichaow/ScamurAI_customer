# Fraud Investment Chatbot

A defensive security chatbot designed to help users identify potentially fraudulent transactions through guided questioning and AI-powered fraud detection.

## Features

- **Sequential Question Flow**: Presents 4 core fraud detection questions one at a time
- **Input Validation**: Validates user responses and re-prompts when answers are off-topic
- **AI-Powered Analysis**: Uses OpenAI API to assess fraud likelihood
- **Session Management**: Maintains conversation state throughout the interaction
- **Responsive UI**: Clean, mobile-friendly chat interface

## Setup

1. **Create Virtual Environment**:
   ```bash
   python3 -m venv venv_linux
   source venv_linux/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   PORT=8000
   DEBUG=True
   ```

4. **Start the Application**:
   ```bash
   # Development mode
   source venv_linux/bin/activate
   python main.py
   
   # Or using uvicorn directly
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Access the Application**:
   Open your browser and navigate to `http://localhost:8000`

## How It Works

### The 4 Fraud Detection Questions

1. **Payment Recipient**: Who are you making this payment to?
2. **Purpose of Payment**: What is the purpose of this payment?
3. **Source of Payment Link**: Where did you get the payment link or instructions from?
4. **Website Verification**: What website or platform are you using for the payment?

### Response Validation

The system validates each response using OpenAI to ensure:
- Responses are relevant to the current question
- Answers provide meaningful information
- Users aren't giving generic or off-topic responses

### Fraud Analysis

After collecting all responses, the system:
- Sends collected data to OpenAI for fraud risk assessment
- Provides a risk level (LOW/MEDIUM/HIGH)
- Offers actionable insights and recommendations

## Project Structure

```
app/
├── models/
│   └── schemas.py           # Pydantic models for request/response validation
├── routes/
│   └── chat.py              # FastAPI routes for chat functionality
├── services/
│   └── conversation_engine.py # Core conversation logic and AI integration
└── utils/
    └── dependencies.py      # Dependency injection utilities

static/
├── css/
│   └── style.css            # Application styling
├── js/
│   └── app.js               # Frontend JavaScript
└── index.html               # Main HTML file

tests/
├── test_conversation_engine.py # Unit tests for conversation engine
└── test_chat_routes.py      # Unit tests for API routes

main.py                      # FastAPI application entry point
requirements.txt             # Python dependencies
```

## API Endpoints

- `POST /api/chat/start` - Initialize new conversation
- `POST /api/chat/respond` - Submit user response
- `GET /api/chat/status/{session_id}` - Get conversation status (debug)
- `GET /health` - Health check endpoint

## Testing

Run smoke tests to verify basic functionality:
```bash
source venv_linux/bin/activate
python run_tests.py
```

Run the full test suite (some tests may need OpenAI API key):
```bash
source venv_linux/bin/activate
pytest tests/ -v
```

## Security Features

- Input validation and sanitization
- Session-based conversation management
- Secure API key handling
- Rate limiting considerations built-in

## Development

The application is built with:
- **Backend**: Python, FastAPI
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **AI Integration**: OpenAI GPT-3.5-turbo
- **Session Management**: In-memory storage with automatic cleanup
- **Validation**: Pydantic models
- **Testing**: Pytest with asyncio support

## Contributing

This is a defensive security tool designed to help users identify fraud. All contributions should maintain this focus on user protection and security.