"""
FinGuard IntelliAgent - Agent Orchestrator
==========================================

This module implements the main FinGuard IntelliAgent orchestrator that
coordinates the "Think, Act, Observe" loop with all tools and services.

Key Concepts Implemented:
1. **Think, Act, Observe Loop**: Standard agentic reasoning loop
   [Ref: Intro to Agents p.11]
2. **Context Lifecycle**: Fetch → Prepare → Invoke → Update
   [Ref: Context Engineering p.9]
3. **Observability**: Structured logging of agent trajectory
   [Ref: Prototype to Production p.30]

Author: Alfred Munga
License: MIT
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import Google Gemini
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool

# Import agent components
from agent.memory import MemoryBank, UserProfile
from backend.utils.logger import AgentLogger, SessionStore

# Import tools
from tools.sms_parser_tool import SMSParserTool
from tools.rag_insights_tool import RAGInsightsTool
from tools.invoice_ops import GetUnpaidInvoicesTool, SendPaymentRequestTool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FinGuardIntelliAgent:
    """
    The main FinGuard IntelliAgent orchestrator.
    
    This class implements the "Think, Act, Observe" loop, coordinating
    all tools and managing context lifecycle for multi-turn conversations.
    
    Architecture:
    ```
    User Query
        ↓
    [Fetch Context from Memory]
        ↓
    [Prepare System Prompt + History]
        ↓
    [Think, Act, Observe Loop]
        ↓  ↑ (iterate until done)
        ↓  ↑
    [Update Session & Memory]
        ↓
    Final Response
    ```
    
    Attributes:
        model: Google Gemini model instance
        memory: MemoryBank for user profiles and context
        session_store: SessionStore for conversation history
        tools: Dictionary of available tools
        max_iterations: Maximum loop iterations (prevents infinite loops)
    """
    
    def __init__(
        self,
        api_key: str,
        memory: Optional[MemoryBank] = None,
        session_store: Optional[SessionStore] = None,
        max_iterations: int = 5
    ):
        """
        Initialize the FinGuard IntelliAgent.
        
        Args:
            api_key: Google Gemini API key
            memory: MemoryBank instance (creates new if not provided)
            session_store: SessionStore instance (creates new if not provided)
            max_iterations: Maximum iterations for Think-Act-Observe loop
        """
        self.max_iterations = max_iterations
        
        # Initialize memory and session store
        self.memory = memory or MemoryBank()
        self.session_store = session_store or SessionStore()
        
        # Initialize tools
        self._initialize_tools()
        
        # Initialize Gemini model with tools
        self._initialize_model(api_key)
        
        logger.info("FinGuardIntelliAgent initialized successfully")
    
    def _initialize_tools(self) -> None:
        """Initialize all available tools."""
        self.tools = {
            'sms_parser': SMSParserTool(),
            'rag_insights': RAGInsightsTool(memory=self.memory),
            'get_unpaid_invoices': GetUnpaidInvoicesTool(),
            'send_payment_request': SendPaymentRequestTool()
        }
        
        logger.info(f"Initialized {len(self.tools)} tools: {list(self.tools.keys())}")
    
    def _initialize_model(self, api_key: str) -> None:
        """
        Initialize Google Gemini model with function calling.
        
        Args:
            api_key: Google Gemini API key
        """
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Define function declarations for Gemini
        functions = [
            FunctionDeclaration(
                name="parse_sms",
                description=(
                    "Parse an M-Pesa or Airtel Money SMS message to extract "
                    "structured transaction data (type, amount, sender, recipient, etc.). "
                    "Use this tool when the user provides an SMS message or mentions "
                    "receiving a transaction notification."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "sms_text": {
                            "type": "string",
                            "description": "The SMS message text to parse"
                        }
                    },
                    "required": ["sms_text"]
                }
            ),
            FunctionDeclaration(
                name="get_financial_insights",
                description=(
                    "Query financial data and get insights about spending, budgets, "
                    "transactions, or receive financial advice. Use this tool when the "
                    "user asks questions like 'How much did I spend on X?', 'Am I over "
                    "budget?', 'Show me recent transactions', or 'What financial advice "
                    "do you have?'"
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The user's financial question or query"
                        }
                    },
                    "required": ["query"]
                }
            ),
            FunctionDeclaration(
                name="get_unpaid_invoices",
                description=(
                    "Retrieve a list of unpaid or overdue invoices. Use this tool when "
                    "the user asks 'Who owes me money?', 'Show me unpaid invoices', "
                    "'What are my receivables?', or similar questions about outstanding "
                    "payments. This tool ONLY retrieves information; it does NOT send "
                    "any messages or payment requests."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID (defaults to 'default_user' if not specified)"
                        },
                        "include_pending": {
                            "type": "boolean",
                            "description": "Whether to include invoices with pending payments (default: false)"
                        }
                    },
                    "required": []
                }
            ),
            FunctionDeclaration(
                name="send_payment_request",
                description=(
                    "Initiate an M-Pesa STK Push payment request to collect payment for "
                    "a specific invoice. ⚠️ IMPORTANT: Use this tool ONLY when the user "
                    "explicitly confirms they want to request payment, such as saying "
                    "'Send payment request to X', 'Collect payment from Y', or 'Request "
                    "payment for invoice Z'. DO NOT use this for just viewing invoices. "
                    "This tool has idempotency protection and will refuse duplicate requests."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "invoice_id": {
                            "type": "string",
                            "description": "The invoice ID to collect payment for (e.g., 'INV-2025-1804')"
                        }
                    },
                    "required": ["invoice_id"]
                }
            )
        ]
        
        # Create tool for Gemini
        gemini_tool = Tool(function_declarations=functions)
        
        # Initialize model with tools
        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            tools=[gemini_tool]
        )
        
        logger.info(f"Gemini model initialized with {len(functions)} function declarations")
    
    def _build_system_prompt(self, user_profile: Optional[UserProfile] = None) -> str:
        """
        Build the system prompt with persona and context.
        
        This implements the "Persona" best practice from the ADK whitepaper.
        [Ref: Intro to Agents p.23]
        
        Args:
            user_profile: User profile for personalization
            
        Returns:
            System prompt string
        """
        # Base persona
        prompt = """You are FinGuard, a helpful and intelligent financial assistant designed specifically for Kenyan Small and Medium Enterprises (SMEs).

Your capabilities:
- Parse M-Pesa and Airtel Money SMS messages to extract transaction data
- Provide financial insights about spending, budgets, and cash flow
- Track unpaid invoices and outstanding payments
- Initiate payment collection via M-Pesa STK Push

Your personality:
- Professional yet friendly and approachable
- Proactive in suggesting actions (but always ask for confirmation before taking actions)
- Clear and concise in explanations
- Knowledgeable about Kenyan business practices and M-Pesa

Important guidelines:
1. **Always confirm before taking actions**: When initiating payment requests or other actions, summarize what you're about to do and get user confirmation.
2. **Be explicit about tool selection**: Explain why you're using a specific tool.
3. **Handle errors gracefully**: If a tool fails, explain the issue clearly and suggest alternatives.
4. **Respect idempotency**: Never send duplicate payment requests. If a payment is already processing, inform the user clearly.
5. **Provide context**: When showing financial data, add context (e.g., "This is 20% over your budget").

"""
        
        # Add user profile if available
        if user_profile:
            prompt += f"""
User Profile:
- Name: {user_profile.name}
- Business Type: {user_profile.business_type}
- Location: {user_profile.location}

"""
        
        # Add current date/time for context
        current_time = datetime.now()
        prompt += f"""
Current Date and Time: {current_time.strftime('%B %d, %Y at %I:%M %p EAT')}

Remember: Always be helpful, accurate, and respectful of the user's time and business needs.
"""
        
        return prompt
    
    def run(
        self,
        user_query: str,
        user_id: str = "default_user",
        trace_logger: Optional[AgentLogger] = None
    ) -> Dict[str, Any]:
        """
        Execute the agent with a user query using the Think-Act-Observe loop.
        
        This implements the core agentic loop with full observability.
        
        Process:
        1. **Fetch Context**: Retrieve user profile and memories
        2. **Prepare Prompt**: Build system instruction with context
        3. **Think-Act-Observe Loop**: Iteratively reason and use tools
        4. **Update Context**: Save conversation to session history
        
        Args:
            user_query: The user's question or request
            user_id: User identifier for context retrieval
            trace_logger: Optional logger (creates new if not provided)
            
        Returns:
            Dict with:
            {
                'success': True/False,
                'response': str (final answer),
                'trajectory': List[Dict] (execution trace),
                'trace_id': str,
                'error': Optional[str]
            }
        """
        # Initialize logger
        if trace_logger is None:
            trace_logger = AgentLogger()
        
        try:
            # ================================================================
            # STEP 1: FETCH CONTEXT (Context Lifecycle)
            # ================================================================
            logger.info(f"[STEP 1] Fetching context for user: {user_id}")
            
            # Get user profile
            user_profile = self.memory.user_profile
            
            # Get conversation history
            history = self.session_store.get_history(user_id)
            
            # Log context fetch
            trace_logger.log_context({
                'user_id': user_id,
                'user_profile': {
                    'name': user_profile.name if user_profile else None,
                    'business': user_profile.business_type if user_profile else None
                },
                'history_turns': len(history)
            })
            
            # ================================================================
            # STEP 2: PREPARE PROMPT (System Instruction + History)
            # ================================================================
            logger.info("[STEP 2] Preparing system prompt and chat history")
            
            system_prompt = self._build_system_prompt(user_profile)
            
            # Build chat history for Gemini
            chat_history = []
            for turn in history:
                chat_history.append({
                    'role': turn['role'],
                    'parts': [turn['content']]
                })
            
            # Start chat session
            chat = self.model.start_chat(history=chat_history)
            
            # ================================================================
            # STEP 3: THINK-ACT-OBSERVE LOOP
            # ================================================================
            logger.info("[STEP 3] Starting Think-Act-Observe loop")
            
            # Combine system prompt with user query
            full_query = f"{system_prompt}\n\nUser Query: {user_query}"
            
            iteration = 0
            response = None
            
            while iteration < self.max_iterations:
                iteration += 1
                logger.info(f"[LOOP] Iteration {iteration}/{self.max_iterations}")
                
                # === THINK: Send query to Gemini ===
                try:
                    response = chat.send_message(full_query)
                except Exception as e:
                    error_msg = f"Gemini API error: {str(e)}"
                    trace_logger.log_error(error_msg)
                    return {
                        'success': False,
                        'error': error_msg,
                        'trace_id': trace_logger.trace_id
                    }
                
                # Check if model wants to call functions
                if not response.candidates:
                    error_msg = "No response candidates from model"
                    trace_logger.log_error(error_msg)
                    return {
                        'success': False,
                        'error': error_msg,
                        'trace_id': trace_logger.trace_id
                    }
                
                candidate = response.candidates[0]
                
                # Check for function calls
                if not candidate.content.parts:
                    error_msg = "No content parts in response"
                    trace_logger.log_error(error_msg)
                    return {
                        'success': False,
                        'error': error_msg,
                        'trace_id': trace_logger.trace_id
                    }
                
                # Process each part
                has_function_calls = False
                function_responses = []
                
                for part in candidate.content.parts:
                    # If it's text, we might be done
                    if hasattr(part, 'text') and part.text:
                        trace_logger.log_think(
                            f"Model reasoning: {part.text}",
                            metadata={'iteration': iteration}
                        )
                    
                    # If it's a function call, execute it
                    if hasattr(part, 'function_call') and part.function_call:
                        has_function_calls = True
                        function_call = part.function_call
                        
                        # === ACT: Execute tool ===
                        tool_name = function_call.name
                        tool_args = dict(function_call.args)
                        
                        trace_logger.log_act(
                            tool_name=tool_name,
                            tool_input=tool_args,
                            metadata={'iteration': iteration}
                        )
                        
                        # Execute the tool
                        tool_result = self._execute_tool(tool_name, tool_args)
                        
                        # === OBSERVE: Log tool output ===
                        trace_logger.log_observe(
                            tool_name=tool_name,
                            tool_output=tool_result,
                            success=tool_result.get('success', True),
                            metadata={'iteration': iteration}
                        )
                        
                        # Prepare function response for Gemini
                        function_responses.append({
                            'name': tool_name,
                            'response': tool_result
                        })
                
                # If no function calls, we're done
                if not has_function_calls:
                    # Extract final text response
                    final_text = ""
                    for part in candidate.content.parts:
                        if hasattr(part, 'text'):
                            final_text += part.text
                    
                    trace_logger.log_final(
                        final_text,
                        metadata={
                            'total_iterations': iteration,
                            'tools_used': len([log for log in trace_logger.logs if log['step'] == 'act'])
                        }
                    )
                    
                    # ========================================================
                    # STEP 4: UPDATE CONTEXT (Save to session)
                    # ========================================================
                    logger.info("[STEP 4] Updating session context")
                    
                    self.session_store.add_turn(user_id, 'user', user_query)
                    self.session_store.add_turn(user_id, 'assistant', final_text)
                    
                    return {
                        'success': True,
                        'response': final_text,
                        'trajectory': trace_logger.get_trajectory(),
                        'trace_id': trace_logger.trace_id,
                        'summary': trace_logger.get_summary()
                    }
                
                # Send function results back to model
                if function_responses:
                    # Build function response message using Google's protos
                    import google.generativeai.protos as protos
                    
                    response_parts = []
                    for func_resp in function_responses:
                        response_parts.append(
                            protos.Part(function_response=protos.FunctionResponse(
                                name=func_resp['name'],
                                response=func_resp['response']
                            ))
                        )
                    
                    # Continue conversation with function results
                    try:
                        response = chat.send_message(
                            response_parts
                        )
                    except Exception as e:
                        error_msg = f"Error sending function results: {str(e)}"
                        trace_logger.log_error(error_msg)
                        return {
                            'success': False,
                            'response': error_msg,
                            'error': error_msg,
                            'trace_id': trace_logger.trace_id,
                            'trace_logger': trace_logger,
                            'trajectory': trace_logger.get_trajectory()
                        }
            
            # If we hit max iterations
            warning_msg = f"Reached maximum iterations ({self.max_iterations}). Stopping."
            trace_logger.log_error(warning_msg)
            logger.warning(warning_msg)
            
            return {
                'success': False,
                'response': "I've reached my maximum thinking steps. Let me summarize what I found.",
                'error': warning_msg,
                'trace_id': trace_logger.trace_id,
                'trace_logger': trace_logger,
                'trajectory': trace_logger.get_trajectory()
            }
        
        except Exception as e:
            error_msg = f"Unexpected error in agent execution: {str(e)}"
            trace_logger.log_error(error_msg, {'exception': str(e)})
            logger.error(error_msg, exc_info=True)
            
            return {
                'success': False,
                'response': "I encountered an error while processing your request.",
                'error': error_msg,
                'trace_id': trace_logger.trace_id,
                'trace_logger': trace_logger
            }
    
    def _execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by name with given arguments.
        
        This method handles tool routing and error handling.
        
        Args:
            tool_name: Name of the tool to execute
            tool_args: Arguments for the tool
            
        Returns:
            Tool execution result
        """
        try:
            # Route to appropriate tool
            if tool_name == 'parse_sms':
                tool = self.tools['sms_parser']
                sms_text = tool_args.get('sms_text', '')
                result = tool.parse_sms(sms_text)
                if result is None:
                    return {
                        'success': False,
                        'error': 'Could not parse SMS message. Please ensure it is a valid M-Pesa or bank SMS.'
                    }
                return {
                    'success': True,
                    'parsed_data': result
                }
            
            elif tool_name == 'get_financial_insights':
                tool = self.tools['rag_insights']
                query = tool_args.get('query', '')
                return tool.run(query)
            
            elif tool_name == 'get_unpaid_invoices':
                from tools.invoice_ops import GetUnpaidInvoicesInput
                tool = self.tools['get_unpaid_invoices']
                input_data = GetUnpaidInvoicesInput(
                    user_id=tool_args.get('user_id', 'default_user'),
                    include_pending=tool_args.get('include_pending', False)
                )
                return tool.run(input_data)
            
            elif tool_name == 'send_payment_request':
                from tools.invoice_ops import SendPaymentRequestInput
                tool = self.tools['send_payment_request']
                input_data = SendPaymentRequestInput(
                    invoice_id=tool_args['invoice_id']
                )
                return tool.run(input_data)
            
            else:
                return {
                    'success': False,
                    'error': f"Unknown tool: {tool_name}"
                }
        
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f"Tool execution failed: {str(e)}"
            }


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    """Test the orchestrator."""
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in .env")
        sys.exit(1)
    
    print("=" * 70)
    print("FinGuard IntelliAgent Orchestrator Test")
    print("=" * 70)
    
    # Initialize agent
    print("\n1️⃣ Initializing agent...")
    agent = FinGuardIntelliAgent(api_key=api_key)
    print("✅ Agent initialized!")
    
    # Test query 1: Get unpaid invoices
    print("\n2️⃣ Testing: Get unpaid invoices")
    print("-" * 70)
    result = agent.run(
        user_query="Who owes me money? Show me my unpaid invoices.",
        user_id="test_user"
    )
    
    if result['success']:
        print(f"\n✅ Success!")
        print(f"Response: {result['response'][:200]}...")
        print(f"\nTools used: {len([log for log in result['trajectory'] if log['step'] == 'act'])}")
    else:
        print(f"\n❌ Failed: {result.get('error')}")
    
    print("\n" + "=" * 70)
    print("✅ Test complete!")
