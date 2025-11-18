"""
FinGuard IntelliAgent - LLM Service
===================================

This service handles interactions with Google Gemini for generating
natural language responses using RAG (Retrieval Augmented Generation).

The service:
- Initializes Google Gemini client securely
- Constructs prompts for financial assistance
- Generates context-aware responses
- Handles API errors gracefully

Author: Alfred Munga
License: MIT
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("google-generativeai not installed. LLM features will be disabled.")

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class LLMService:
    """
    Service for interacting with Google Gemini LLM.
    
    This service provides a wrapper around the Google Gemini API,
    specifically configured for financial assistance queries for Kenyan SMEs.
    
    Attributes:
        api_key: Google Gemini API key
        model: Gemini model instance
        generation_config: Configuration for text generation
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM service.
        
        Args:
            api_key: Google Gemini API key. If not provided, loads from GEMINI_API_KEY env var.
            
        Raises:
            ValueError: If API key is not provided and not found in environment
            ImportError: If google-generativeai is not installed
        """
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "google-generativeai is not installed. "
                "Install it with: pip install google-generativeai"
            )
        
        # Get API key
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Google Gemini API key not found. "
                "Please set GEMINI_API_KEY environment variable or pass api_key parameter."
            )
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model
        self.model_name = 'gemini-pro'
        self.model = genai.GenerativeModel(self.model_name)
        
        # Generation configuration
        self.generation_config = {
            'temperature': 0.7,
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': 1024,
        }
        
        logger.info(f"LLM Service initialized with model: {self.model_name}")
    
    def generate_response(
        self,
        prompt: str,
        context: str = "",
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a response using Google Gemini.
        
        This method constructs a complete prompt by combining the system prompt,
        context, and user query, then generates a response using Gemini.
        
        Args:
            prompt: User's query or question
            context: Additional context (transactions, memory, etc.)
            system_prompt: Custom system prompt. If None, uses default financial assistant prompt.
            
        Returns:
            Generated response text
            
        Raises:
            Exception: If API call fails
        """
        # Default system prompt for financial assistant
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt()
        
        # Construct full prompt
        full_prompt = self._construct_prompt(system_prompt, context, prompt)
        
        try:
            # Generate response
            logger.info(f"Generating response for query: {prompt[:50]}...")
            response = self.model.generate_content(
                full_prompt,
                generation_config=self.generation_config
            )
            
            # Extract text
            if response and response.text:
                logger.info("Response generated successfully")
                return response.text.strip()
            else:
                logger.warning("Empty response from Gemini")
                return "I apologize, but I couldn't generate a response. Please try rephrasing your question."
        
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I encountered an error: {str(e)}. Please try again."
    
    def _get_default_system_prompt(self) -> str:
        """
        Get the default system prompt for the financial assistant.
        
        Returns:
            System prompt text
        """
        return """You are a helpful financial assistant for Kenyan SME (Small and Medium Enterprise) owners.

Your role:
- Analyze financial transaction data (M-Pesa, bank SMS)
- Provide insights on spending patterns and cash flow
- Help users understand their financial health
- Give practical advice for Kenyan business context
- Answer questions about budgets and expenses
- Use Kenyan Shillings (KES) for all amounts

Guidelines:
- Be concise and clear
- Use simple language
- Provide specific numbers when available
- Give actionable advice
- Be culturally aware of Kenyan business practices
- When data is insufficient, ask for clarification
- Always be encouraging and supportive

Context: You have access to the user's transaction history, budget information, 
and conversation history. Use this context to provide personalized responses."""
    
    def _construct_prompt(
        self,
        system_prompt: str,
        context: str,
        user_query: str
    ) -> str:
        """
        Construct the complete prompt for Gemini.
        
        Args:
            system_prompt: System instructions
            context: Transaction data and memory context
            user_query: User's question
            
        Returns:
            Complete prompt string
        """
        prompt_parts = [
            system_prompt,
            "\n\n---\n\n"
        ]
        
        if context:
            prompt_parts.extend([
                "CONTEXT:",
                context,
                "\n\n---\n\n"
            ])
        
        prompt_parts.extend([
            "USER QUESTION:",
            user_query,
            "\n\nASSISTANT:"
        ])
        
        return "\n".join(prompt_parts)
    
    def test_connection(self) -> bool:
        """
        Test the connection to Gemini API.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.model.generate_content("Hello")
            return response and response.text is not None
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False


# ============================================================================
# Convenience Functions
# ============================================================================

# Global LLM service instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """
    Get or create the global LLM service instance.
    
    Returns:
        LLMService instance
    """
    global _llm_service
    
    if _llm_service is None:
        _llm_service = LLMService()
    
    return _llm_service


def generate_response(prompt: str, context: str = "") -> str:
    """
    Convenience function to generate a response.
    
    Args:
        prompt: User's query
        context: Additional context
        
    Returns:
        Generated response
    """
    service = get_llm_service()
    return service.generate_response(prompt, context)


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    """Test the LLM service."""
    
    print("=" * 60)
    print("FinGuard IntelliAgent - LLM Service Test")
    print("=" * 60)
    
    # Check if API key is available
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("\n❌ GEMINI_API_KEY not found in environment")
        print("Please set it in your .env file:")
        print('GEMINI_API_KEY="your-api-key-here"')
        exit(1)
    
    try:
        # Initialize service
        print("\n📡 Initializing LLM Service...")
        service = LLMService()
        
        # Test connection
        print("🔍 Testing connection...")
        if service.test_connection():
            print("✅ Connection successful!")
        else:
            print("❌ Connection failed")
            exit(1)
        
        # Test query
        print("\n💬 Testing query...")
        context = """
        User Profile: Kenyan SME Owner, Business: Retail Shop
        Recent Transactions:
        - Spent KES 3,500 on fuel (Shell)
        - Spent KES 2,000 on groceries (Naivas)
        - Received KES 15,000 from customer
        Budget: Transport KES 5,000/month
        """
        
        query = "How much have I spent on transport this month?"
        
        print(f"Query: {query}")
        print("\nResponse:")
        print("-" * 60)
        
        response = service.generate_response(query, context)
        print(response)
        
        print("-" * 60)
        print("\n✅ Test completed successfully!")
        
    except ValueError as e:
        print(f"\n❌ Configuration error: {str(e)}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
