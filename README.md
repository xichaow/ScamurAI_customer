# NAB Payment Safety Assistant

A Flask-based AI chatbot that helps users identify potentially risky payment requests and scam transactions through conversational AI and expert risk assessment.

## Features

- **Interactive Scam Detection**: 4-question assessment covering payment recipient, purpose, source, and platform verification
- **AI-Powered Risk Analysis**: OpenAI GPT-powered scam risk assessment with LOW/MEDIUM/HIGH classification  
- **NAB Messaging Interface**: Professional banking UI matching NAB brand standards
- **STOP-CHECK-PROTECT Framework**: Standardized safety recommendations following established fraud prevention guidelines
- **Real-time Chat Interface**: Mobile-responsive design with avatar-based messaging
- **Automatic Banker Follow-up**: Integration with NAB customer service workflow

## Tech Stack

- **Backend**: Python Flask with OpenAI GPT-3.5-turbo integration
- **Frontend**: Responsive HTML/CSS/JavaScript with NAB branding
- **Deployment**: Render cloud platform with GitHub CI/CD
- **AI Model**: OpenAI GPT-3.5-turbo for intelligent scam detection

## Quick Start

### Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/xichaow/fraud-chatbot.git
cd fraud-chatbot
```

2. **Install dependencies:**
```bash
pip install flask openai
```

3. **Set up environment variables:**
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

4. **Run the application:**
```bash
python app.py
```

5. **Access the application:**
- Homepage: http://localhost:8000/
- Chat Interface: http://localhost:8000/chat

### Production Deployment

The application is configured for Render deployment with automatic GitHub integration.

**Required Environment Variables:**
- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `PORT` - Port number (defaults to 8000)  
- `DEBUG` - Debug mode (defaults to False)

## How It Works

### User Journey
1. **Welcome**: Professional NAB-branded chat interface
2. **Assessment**: 4 targeted questions about payment details:
   - Who are you paying?
   - What is the payment for?
   - Where did you get the payment link?
   - Which website/platform are you using?
3. **Analysis**: AI-powered scam risk assessment
4. **Recommendations**: STOP-CHECK-PROTECT safety guidelines
5. **Follow-up**: Automatic NAB banker callback notification

### Risk Assessment Framework

**Risk Levels:**
- **LOW**: Payment appears legitimate with minimal risk indicators
- **MEDIUM**: Some concerning factors requiring additional verification
- **HIGH**: Multiple red flags indicating likely scam attempt

**Assessment Criteria:**
- Recipient legitimacy and verification
- Payment purpose and context analysis
- Source credibility of payment requests  
- Platform/website authenticity checks

### Safety Recommendations

**STOP-CHECK-PROTECT Framework:**
- **STOP**: Don't give money or information to anyone if unsure. Scammers pretend to be from trusted organizations.
- **CHECK**: Ask yourself if the message or call is fake. Never click links in messages. Only contact businesses using official website or app contact information.
- **PROTECT**: Act quickly if something feels wrong. Contact your bank immediately if you notice unusual activity or if a scammer gets your information.

## API Documentation

### Endpoints

- `GET /` - Landing page with service overview and scam education
- `GET /chat` - NAB Messaging chat interface
- `POST /api/chat/start` - Initialize conversation session
- `POST /api/chat/respond` - Process user responses and provide next questions
- `GET /static/<filename>` - Serve static assets (NAB branding)
- `GET /health` - Application health check

### Response Format

**Risk Assessment Output:**
```
**RISK LEVEL: [LOW/MEDIUM/HIGH]**

• [Key risk factor or positive indicator 1]
• [Key risk factor or positive indicator 2] 
• [Key risk factor or positive indicator 3]
• Recommendation: [STOP-CHECK-PROTECT framework guidelines]
```

## Features & Enhancements

### Current Features
✅ NAB Messaging UI with professional branding  
✅ Real-time chat with avatars and timestamps  
✅ Intelligent response validation  
✅ Structured risk assessment output  
✅ STOP-CHECK-PROTECT safety framework  
✅ Automatic banker follow-up workflow  

### Future Enhancements
🔄 **NAB Data Integration**: Plans to incorporate NAB's internal fraud database and transaction patterns for enhanced accuracy  
🔄 **Advanced Analytics**: Enhanced scam pattern recognition  
🔄 **Multi-language Support**: Expand accessibility  

## Project Structure

```
fraud-chatbot/
├── app.py                    # Main Flask application
├── static/
│   └── nab-icon.jpg         # NAB branding assets
├── example/
│   ├── chatbot_snapshot.jpg  # UI design references
│   ├── chatbot_snapshot2.png
│   ├── chatbot_snapshot3.PNG
│   ├── customer_chatbot_snapshot.png
│   ├── icon.jpg
│   └── recommendation.jpg   # STOP-CHECK-PROTECT framework
├── requirements.txt         # Python dependencies
├── render.yaml             # Render deployment configuration
└── README.md               # Project documentation
```

## The 4 Scam Detection Questions

1. **Payment Recipient**: "Who are you making this payment to? Please provide the name of the person, organization, or company."

2. **Purpose of Payment**: "What is the purpose of this payment? Please describe what you are paying for (service, product, investment, etc.)"

3. **Source of Payment Link**: "Where did you get the payment link or payment instructions from? Please share the source (email, website, text message, social media post, etc.)"

4. **Website Verification**: "Please provide the website URL or platform where you are making this payment, or describe how you are accessing the payment page."

## Testing

### Local Testing
```bash
# Run the application locally
python app.py

# Test the chat interface
open http://localhost:8000/chat

# Test API endpoints
curl -X POST http://localhost:8000/api/chat/start \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test123"}'
```

### Health Check
```bash
curl http://localhost:8000/health
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Security & Privacy

- No persistent storage of user conversations
- Session-based temporary data only  
- Secure API key management
- Input validation and sanitization
- No logging of sensitive payment information

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For technical support or questions about the NAB Payment Safety Assistant, please contact the development team or create an issue in the GitHub repository.