"""
Conversation engine for fraud detection chatbot.
Handles question flow, response validation, and fraud analysis.
"""
import time
from typing import Dict, Optional, Tuple
from ..models.schemas import ConversationSession, FraudQuestion, ChatStartResponse, ChatResponseResponse


# The 4 fraud detection questions as specified in requirements
FRAUD_QUESTIONS = [
    FraudQuestion(
        id="payment_recipient",
        question="Who are you making this payment to? Please provide the name of the person, organization, or company.",
        validation="payment_recipient"
    ),
    FraudQuestion(
        id="purpose_of_payment",
        question="What is the purpose of this payment? Please describe what you are paying for (service, product, investment, etc.)",
        validation="purpose_of_payment"
    ),
    FraudQuestion(
        id="source_of_payment_link",
        question="Where did you get the payment link or payment instructions from? Please share the source (email, website, text message, social media post, etc.)",
        validation="source_of_payment_link"
    ),
    FraudQuestion(
        id="website_verification",
        question="Please provide the website URL or platform where you are making this payment, or describe how you are accessing the payment page.",
        validation="website_verification"
    )
]


class ConversationEngine:
    """
    Manages conversation flow for fraud detection.
    
    Handles session management, question sequencing, response validation,
    and fraud analysis using OpenAI API.
    """
    
    def __init__(self, openai_client):
        """
        Initialize conversation engine.
        
        Args:
            openai_client: OpenAI client module.
        """
        self.openai_client = openai_client
        self.sessions: Dict[str, ConversationSession] = {}
    
    def start_session(self, session_id: str) -> ChatStartResponse:
        """
        Start a new conversation session.
        
        Args:
            session_id (str): Unique session identifier.
            
        Returns:
            ChatStartResponse: Response with first question.
        """
        session = ConversationSession(
            session_id=session_id,
            current_question_index=0,
            answers={},
            retry_count=0,
            completed=False,
            start_time=time.time()
        )
        
        self.sessions[session_id] = session
        
        return ChatStartResponse(
            success=True,
            message=FRAUD_QUESTIONS[0].question,
            session_id=session_id
        )
    
    async def process_response(self, session_id: str, user_message: str) -> ChatResponseResponse:
        """
        Process user response and return next question or fraud analysis.
        
        Args:
            session_id (str): Session identifier.
            user_message (str): User's response message.
            
        Returns:
            ChatResponseResponse: Next question or fraud analysis result.
        """
        session = self.sessions.get(session_id)
        
        if not session:
            return ChatResponseResponse(
                success=False,
                message="Session not found. Please refresh and start again."
            )
        
        if session.completed:
            return ChatResponseResponse(
                success=True,
                message="Thank you! Your fraud assessment has been completed.",
                completed=True
            )
        
        current_question = FRAUD_QUESTIONS[session.current_question_index]
        
        # Validate response relevance
        is_valid_response = self._validate_response(user_message, current_question)
        
        if not is_valid_response:
            session.retry_count += 1
            
            if session.retry_count >= 3:
                # Move to next question after 3 failed attempts
                session.retry_count = 0
                session.answers[current_question.id] = "User unable to provide relevant answer after multiple attempts"
                return await self._move_to_next_question(session)
            
            return ChatResponseResponse(
                success=True,
                message=f"I need a more specific answer about {self._get_question_context(current_question)}. Could you please provide more details?"
            )
        
        # Store valid response
        session.answers[current_question.id] = user_message
        session.retry_count = 0
        
        return await self._move_to_next_question(session)
    
    async def _move_to_next_question(self, session: ConversationSession) -> ChatResponseResponse:
        """
        Move to the next question or complete the conversation.
        
        Args:
            session (ConversationSession): Current session.
            
        Returns:
            ChatResponseResponse: Next question or completion response.
        """
        session.current_question_index += 1
        
        if session.current_question_index >= len(FRAUD_QUESTIONS):
            # All questions completed, perform fraud analysis
            session.completed = True
            fraud_analysis = self._perform_fraud_analysis(session.answers)
            
            return ChatResponseResponse(
                success=True,
                message="Thank you for answering all the questions. Let me analyze this information for potential fraud indicators.",
                completed=True,
                fraud_analysis=fraud_analysis
            )
        
        next_question = FRAUD_QUESTIONS[session.current_question_index]
        return ChatResponseResponse(
            success=True,
            message=next_question.question
        )
    
    def _validate_response(self, user_message: str, question: FraudQuestion) -> bool:
        """
        Validate if user response is relevant to the current question.
        
        Args:
            user_message (str): User's response.
            question (FraudQuestion): Current question being answered.
            
        Returns:
            bool: True if response is valid, False otherwise.
        """
        if not user_message or len(user_message.strip()) < 3:
            return False
        
        try:
            prompt = f"""
Evaluate if this user response is relevant to the fraud detection question asked.

Question context: {question.validation}
Question: {question.question}
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

            response = self.openai_client.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=10,
                temperature=0
            )
            
            return response['choices'][0]['message']['content'].strip().lower() == 'true'
        except Exception as e:
            print(f"Error validating response: {e}")
            # Default to accepting response if validation fails
            return True
    
    def _perform_fraud_analysis(self, answers: Dict[str, str]) -> str:
        """
        Perform fraud risk analysis using OpenAI.
        
        Args:
            answers (Dict[str, str]): User's answers to all questions.
            
        Returns:
            str: Fraud risk assessment.
        """
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

            response = self.openai_client.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"Error performing fraud analysis: {e}")
            return 'RISK LEVEL: UNKNOWN\nANALYSIS: Unable to complete fraud analysis due to technical issues. Please verify payment details independently and consult with your bank if you have concerns.'
    
    def _get_question_context(self, question: FraudQuestion) -> str:
        """
        Get contextual description for question re-prompting.
        
        Args:
            question (FraudQuestion): The question being asked.
            
        Returns:
            str: Context description for the question.
        """
        contexts = {
            'payment_recipient': 'who you are paying',
            'purpose_of_payment': 'what you are paying for', 
            'source_of_payment_link': 'where you got the payment link from',
            'website_verification': 'the website or platform you are using'
        }
        return contexts.get(question.id, 'this question')
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """
        Get session by ID.
        
        Args:
            session_id (str): Session identifier.
            
        Returns:
            Optional[ConversationSession]: Session if found, None otherwise.
        """
        return self.sessions.get(session_id)
    
    def cleanup_old_sessions(self) -> None:
        """
        Remove sessions older than 1 hour.
        
        # Reason: Prevents memory leaks from abandoned sessions
        """
        one_hour_ago = time.time() - (60 * 60)
        sessions_to_remove = [
            session_id for session_id, session in self.sessions.items()
            if session.start_time < one_hour_ago
        ]
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]