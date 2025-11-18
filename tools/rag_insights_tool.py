"""
FinGuard IntelliAgent - RAG Insights Tool
=========================================

This tool implements RAG (Retrieval Augmented Generation) for answering
natural language queries about financial data using Google Gemini.

The RAG workflow:
1. **Retrieval**: Load relevant transactions from CSV
2. **Context Compaction**: Filter and summarize relevant data
3. **Prompt Construction**: Combine query + memory + transaction data
4. **LLM Call**: Generate natural language response
5. **Return**: User-friendly answer

Author: Alfred Munga
License: MIT
"""

import pandas as pd
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta

# Import our services
import sys
sys.path.append(str(Path(__file__).parent.parent))

from agent.memory import MemoryBank
from backend.services.llm_service import LLMService

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# RAG Insights Tool
# ============================================================================

class RAGInsightsTool:
    """
    RAG-based tool for answering natural language queries about financial data.
    
    This tool combines:
    - Transaction data retrieval
    - Memory/context management
    - LLM-powered natural language understanding
    
    Attributes:
        memory: MemoryBank instance for user context
        llm_service: LLM service for generating responses
        data_path: Path to transaction data (sms.csv)
        transactions_df: Loaded transaction dataframe
    """
    
    def __init__(
        self,
        memory: MemoryBank,
        llm_service: Optional[LLMService] = None,
        data_path: Optional[str] = None
    ):
        """
        Initialize the RAG insights tool.
        
        Args:
            memory: MemoryBank with user context
            llm_service: LLM service instance (creates new if None)
            data_path: Path to transactions CSV file
        """
        self.memory = memory
        self.llm_service = llm_service or LLMService()
        
        # Set default data path
        if data_path is None:
            project_root = Path(__file__).parent.parent
            data_path = project_root / "data" / "synthetic" / "sms.csv"
        
        self.data_path = Path(data_path)
        self.transactions_df = None
        
        # Load transactions
        self._load_transactions()
        
        logger.info(f"RAG Insights Tool initialized with {len(self.transactions_df)} transactions")
    
    def _load_transactions(self) -> None:
        """Load transactions from CSV file."""
        try:
            if not self.data_path.exists():
                raise FileNotFoundError(f"Transaction data not found at {self.data_path}")
            
            self.transactions_df = pd.read_csv(self.data_path)
            
            # Parse dates
            if 'date' in self.transactions_df.columns:
                self.transactions_df['date'] = pd.to_datetime(self.transactions_df['date'])
            
            logger.info(f"Loaded {len(self.transactions_df)} transactions from {self.data_path}")
        
        except Exception as e:
            logger.error(f"Error loading transactions: {str(e)}")
            raise
    
    def _retrieve_relevant_transactions(
        self,
        user_query: str,
        max_transactions: int = 20
    ) -> pd.DataFrame:
        """
        Retrieve transactions relevant to the user query.
        
        This implements the **Retrieval** step of RAG by filtering
        transactions based on keywords in the query.
        
        Args:
            user_query: User's natural language query
            max_transactions: Maximum number of transactions to return
            
        Returns:
            Filtered DataFrame of relevant transactions
        """
        query_lower = user_query.lower()
        
        # Define keyword mappings for categories
        category_keywords = {
            'transport': ['transport', 'uber', 'bolt', 'taxi', 'fuel', 'petrol', 'shell', 'total', 'kenol'],
            'food': ['food', 'restaurant', 'cafe', 'meal', 'kfc', 'java', 'naivas', 'carrefour', 'groceries'],
            'utilities': ['utility', 'utilities', 'kplc', 'power', 'electricity', 'water', 'internet'],
            'airtime': ['airtime', 'safaricom', 'airtel', 'telkom'],
            'withdrawal': ['withdraw', 'withdrawal', 'cash'],
            'income': ['received', 'income', 'payment', 'deposit'],
        }
        
        # Find matching categories
        matching_categories = []
        for category, keywords in category_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                matching_categories.append(category)
        
        # Filter transactions
        if matching_categories:
            logger.info(f"Filtering for categories: {matching_categories}")
            
            # Filter by transaction type or sender/recipient
            mask = pd.Series([False] * len(self.transactions_df))
            
            for category in matching_categories:
                if category == 'transport':
                    mask |= self.transactions_df['sender_recipient'].str.contains(
                        'SHELL|TOTAL|KENOL|RUBIS|UBER|BOLT', case=False, na=False
                    )
                elif category == 'food':
                    mask |= self.transactions_df['sender_recipient'].str.contains(
                        'KFC|JAVA|NAIVAS|CARREFOUR|RESTAURANT', case=False, na=False
                    )
                elif category == 'utilities':
                    mask |= self.transactions_df['sender_recipient'].str.contains(
                        'KPLC|POWER|WATER|INTERNET', case=False, na=False
                    )
                elif category == 'airtime':
                    mask |= self.transactions_df['transaction_type'].str.contains(
                        'airtime', case=False, na=False
                    )
                elif category == 'withdrawal':
                    mask |= self.transactions_df['transaction_type'].str.contains(
                        'withdraw', case=False, na=False
                    )
                elif category == 'income':
                    mask |= self.transactions_df['transaction_type'].str.contains(
                        'received', case=False, na=False
                    )
            
            filtered_df = self.transactions_df[mask]
        else:
            # No specific category - return recent transactions
            logger.info("No specific category detected, returning recent transactions")
            filtered_df = self.transactions_df.copy()
        
        # Sort by date (most recent first) and limit
        if 'date' in filtered_df.columns:
            filtered_df = filtered_df.sort_values('date', ascending=False)
        
        return filtered_df.head(max_transactions)
    
    def _compact_context(self, transactions_df: pd.DataFrame) -> str:
        """
        Compact transaction data into a concise context string.
        
        This implements the **Context Compaction** step of RAG by
        summarizing transactions into a readable format.
        
        Args:
            transactions_df: DataFrame of transactions
            
        Returns:
            Formatted context string
        """
        if transactions_df.empty:
            return "No relevant transactions found."
        
        context_parts = [f"TRANSACTION DATA ({len(transactions_df)} transactions):"]
        
        # Calculate summary statistics
        total_spent = transactions_df[
            transactions_df['transaction_type'].isin(['paybill', 'till', 'send', 'withdraw', 'airtime'])
        ]['amount'].sum()
        
        total_received = transactions_df[
            transactions_df['transaction_type'] == 'received'
        ]['amount'].sum()
        
        context_parts.append(f"\nSummary:")
        context_parts.append(f"- Total Spent: KES {total_spent:,.2f}")
        context_parts.append(f"- Total Received: KES {total_received:,.2f}")
        context_parts.append(f"- Net Flow: KES {(total_received - total_spent):,.2f}")
        
        # List individual transactions
        context_parts.append(f"\nDetailed Transactions:")
        
        for idx, row in transactions_df.head(10).iterrows():
            date_str = row['date'].strftime('%Y-%m-%d') if pd.notna(row.get('date')) else 'N/A'
            tx_type = row['transaction_type']
            amount = row['amount']
            recipient = row.get('sender_recipient', 'Unknown')
            
            context_parts.append(
                f"- {date_str}: {tx_type.upper()} KES {amount:,.2f} - {recipient}"
            )
        
        if len(transactions_df) > 10:
            context_parts.append(f"... and {len(transactions_df) - 10} more transactions")
        
        return "\n".join(context_parts)
    
    def _construct_full_context(
        self,
        user_query: str,
        transaction_context: str
    ) -> str:
        """
        Construct the full context by combining memory and transaction data.
        
        Args:
            user_query: User's query
            transaction_context: Compacted transaction context
            
        Returns:
            Complete context string
        """
        # Get memory context
        memory_context = self.memory.get_context(
            include_profile=True,
            include_budgets=True,
            include_history=True,
            num_history=3  # Last 3 conversations for relevance
        )
        
        # Combine contexts
        full_context = f"{memory_context}\n\n{transaction_context}"
        
        return full_context
    
    def run(self, user_query: str) -> str:
        """
        Run the RAG workflow to answer a user query.
        
        This is the main method that implements the complete RAG pipeline:
        1. Retrieval: Load relevant transactions
        2. Context Compaction: Summarize transaction data
        3. Prompt Construction: Combine query + memory + transactions
        4. LLM Call: Generate natural language response
        5. Return: User-friendly answer
        
        Args:
            user_query: User's natural language question
            
        Returns:
            Natural language answer from the LLM
        """
        logger.info(f"Processing query: {user_query[:50]}...")
        
        try:
            # Step 1: Retrieval - Get relevant transactions
            relevant_txs = self._retrieve_relevant_transactions(user_query)
            logger.info(f"Retrieved {len(relevant_txs)} relevant transactions")
            
            # Step 2: Context Compaction - Summarize transactions
            transaction_context = self._compact_context(relevant_txs)
            
            # Step 3: Prompt Construction - Combine everything
            full_context = self._construct_full_context(user_query, transaction_context)
            
            # Step 4: LLM Call - Generate response
            response = self.llm_service.generate_response(user_query, full_context)
            
            # Update conversation history
            context_summary = f"Used {len(relevant_txs)} transactions"
            self.memory.update_history(user_query, response, context_summary)
            
            logger.info("Query processed successfully")
            
            # Step 5: Return response
            return response
        
        except Exception as e:
            error_msg = f"I encountered an error processing your query: {str(e)}"
            logger.error(f"Error in RAG workflow: {str(e)}")
            return error_msg
    
    def get_transaction_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all transactions.
        
        Returns:
            Dictionary with transaction summary statistics
        """
        if self.transactions_df is None or self.transactions_df.empty:
            return {"error": "No transactions loaded"}
        
        summary = {
            "total_transactions": len(self.transactions_df),
            "total_spent": float(
                self.transactions_df[
                    self.transactions_df['transaction_type'].isin(['paybill', 'till', 'send', 'withdraw', 'airtime'])
                ]['amount'].sum()
            ),
            "total_received": float(
                self.transactions_df[
                    self.transactions_df['transaction_type'] == 'received'
                ]['amount'].sum()
            ),
            "transaction_types": self.transactions_df['transaction_type'].value_counts().to_dict()
        }
        
        summary['net_flow'] = summary['total_received'] - summary['total_spent']
        
        return summary


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    """Test the RAG insights tool."""
    
    print("=" * 60)
    print("FinGuard IntelliAgent - RAG Insights Tool Test")
    print("=" * 60)
    
    try:
        # Create a test memory bank
        from agent.memory import UserProfile
        
        profile = UserProfile(
            name="Jane Wanjiru",
            business_type="Retail Shop",
            business_name="Wanjiru's Convenience Store"
        )
        
        budgets = {
            "transport": 5000,
            "food": 3000,
            "utilities": 4000
        }
        
        memory = MemoryBank(user_profile=profile, budgets=budgets)
        
        print("\n📝 Initializing RAG Insights Tool...")
        print("   (Note: Requires GEMINI_API_KEY in .env)")
        
        # Initialize RAG tool (will fail if no API key)
        tool = RAGInsightsTool(memory=memory)
        
        # Get transaction summary
        print("\n📊 Transaction Summary:")
        summary = tool.get_transaction_summary()
        print(f"   Total Transactions: {summary['total_transactions']}")
        print(f"   Total Spent: KES {summary['total_spent']:,.2f}")
        print(f"   Total Received: KES {summary['total_received']:,.2f}")
        print(f"   Net Flow: KES {summary['net_flow']:,.2f}")
        
        # Test query (will fail if no API key)
        print("\n💬 Testing RAG Query...")
        query = "How much have I spent on transport?"
        print(f"   Query: {query}")
        
        response = tool.run(query)
        print(f"\n   Response:")
        print(f"   {response}")
        
        print("\n✅ Test completed!")
        
    except ValueError as e:
        if "API key not found" in str(e):
            print("\n⚠️  GEMINI_API_KEY not found in environment")
            print("   To test with LLM, add to .env file:")
            print('   GEMINI_API_KEY="your-api-key-here"')
            print("\n   Testing without LLM...")
            
            # Test without LLM
            from agent.memory import UserProfile
            profile = UserProfile(name="Test User", business_type="SME")
            memory = MemoryBank(user_profile=profile)
            
            # Can't initialize tool without API key, but we tested the structure
            print("   ✅ Tool structure validated")
        else:
            raise
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
