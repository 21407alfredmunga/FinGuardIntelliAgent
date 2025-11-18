"""
FinGuard IntelliAgent - Memory Service
======================================

This module implements the MemoryBank for storing and retrieving
user context, budgets, and conversation history for RAG.

The MemoryBank:
- Stores user profile information
- Manages budget data
- Maintains conversation history (last 5 interactions)
- Provides context for LLM queries

Author: Alfred Munga
License: MIT
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class UserProfile:
    """
    User profile information.
    
    Attributes:
        name: User's name
        business_type: Type of business (e.g., "Retail Shop", "Restaurant")
        business_name: Name of the business
        location: Business location
        joined_date: Date user joined the system
        preferences: Additional user preferences
    """
    name: str
    business_type: str
    business_name: Optional[str] = None
    location: Optional[str] = "Kenya"
    joined_date: str = field(default_factory=lambda: datetime.now().isoformat())
    preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationEntry:
    """
    Single conversation entry.
    
    Attributes:
        timestamp: When the conversation occurred
        user_query: User's question/request
        assistant_response: Assistant's response
        context_used: Brief summary of context used
    """
    timestamp: str
    user_query: str
    assistant_response: str
    context_used: Optional[str] = None


# ============================================================================
# Memory Bank Class
# ============================================================================

class MemoryBank:
    """
    Memory bank for storing user context and conversation history.
    
    This class implements the memory system for the RAG architecture,
    storing user profiles, budgets, and recent conversations to provide
    context for LLM queries.
    
    Attributes:
        user_profile: User profile information
        budgets: Budget limits by category (e.g., {"transport": 5000})
        conversation_history: Last 5 conversation entries
        max_history: Maximum number of conversations to store
    """
    
    def __init__(
        self,
        user_profile: Optional[UserProfile] = None,
        budgets: Optional[Dict[str, float]] = None,
        max_history: int = 5
    ):
        """
        Initialize the memory bank.
        
        Args:
            user_profile: User profile information
            budgets: Budget limits by category
            max_history: Maximum number of conversations to keep
        """
        self.user_profile = user_profile or UserProfile(
            name="User",
            business_type="SME"
        )
        self.budgets = budgets or {}
        self.conversation_history: List[ConversationEntry] = []
        self.max_history = max_history
        
        logger.info(f"MemoryBank initialized for user: {self.user_profile.name}")
    
    def get_context(
        self,
        include_profile: bool = True,
        include_budgets: bool = True,
        include_history: bool = True,
        num_history: Optional[int] = None
    ) -> str:
        """
        Get formatted context string for LLM queries.
        
        This method compiles all relevant context into a formatted string
        that can be passed to the LLM along with the user's query.
        
        Args:
            include_profile: Include user profile information
            include_budgets: Include budget information
            include_history: Include conversation history
            num_history: Number of history entries to include (default: all)
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # User profile
        if include_profile and self.user_profile:
            profile_str = f"""USER PROFILE:
- Name: {self.user_profile.name}
- Business Type: {self.user_profile.business_type}"""
            
            if self.user_profile.business_name:
                profile_str += f"\n- Business Name: {self.user_profile.business_name}"
            
            if self.user_profile.location:
                profile_str += f"\n- Location: {self.user_profile.location}"
            
            context_parts.append(profile_str)
        
        # Budgets
        if include_budgets and self.budgets:
            budget_lines = [
                f"- {category.title()}: KES {amount:,.2f}"
                for category, amount in self.budgets.items()
            ]
            budget_str = "BUDGETS:\n" + "\n".join(budget_lines)
            context_parts.append(budget_str)
        
        # Conversation history
        if include_history and self.conversation_history:
            num = num_history or len(self.conversation_history)
            recent_history = self.conversation_history[-num:]
            
            history_lines = []
            for i, entry in enumerate(recent_history, 1):
                history_lines.append(
                    f"{i}. User: {entry.user_query}\n"
                    f"   Assistant: {entry.assistant_response[:100]}..."
                )
            
            history_str = "RECENT CONVERSATION:\n" + "\n".join(history_lines)
            context_parts.append(history_str)
        
        return "\n\n".join(context_parts)
    
    def update_history(
        self,
        user_query: str,
        assistant_response: str,
        context_used: Optional[str] = None
    ) -> None:
        """
        Add a new entry to conversation history.
        
        Maintains a sliding window of the most recent conversations.
        When max_history is reached, oldest entries are removed.
        
        Args:
            user_query: User's question/request
            assistant_response: Assistant's response
            context_used: Brief summary of context used
        """
        entry = ConversationEntry(
            timestamp=datetime.now().isoformat(),
            user_query=user_query,
            assistant_response=assistant_response,
            context_used=context_used
        )
        
        self.conversation_history.append(entry)
        
        # Maintain max history size
        if len(self.conversation_history) > self.max_history:
            removed = self.conversation_history.pop(0)
            logger.debug(f"Removed oldest conversation entry from {removed.timestamp}")
        
        logger.info(f"Added conversation entry. History size: {len(self.conversation_history)}")
    
    def set_user_profile(self, profile: UserProfile) -> None:
        """
        Update user profile.
        
        Args:
            profile: New user profile
        """
        self.user_profile = profile
        logger.info(f"User profile updated: {profile.name}")
    
    def update_budget(self, category: str, amount: float) -> None:
        """
        Update or add a budget for a category.
        
        Args:
            category: Budget category (e.g., "transport", "food")
            amount: Budget amount in KES
        """
        self.budgets[category.lower()] = amount
        logger.info(f"Budget updated: {category} = KES {amount:,.2f}")
    
    def get_budget(self, category: str) -> Optional[float]:
        """
        Get budget for a specific category.
        
        Args:
            category: Budget category
            
        Returns:
            Budget amount or None if not set
        """
        return self.budgets.get(category.lower())
    
    def clear_history(self) -> None:
        """Clear all conversation history."""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert memory bank to dictionary for serialization.
        
        Returns:
            Dictionary representation
        """
        return {
            "user_profile": asdict(self.user_profile),
            "budgets": self.budgets,
            "conversation_history": [asdict(entry) for entry in self.conversation_history],
            "max_history": self.max_history
        }
    
    def save_to_file(self, filepath: str) -> None:
        """
        Save memory bank to JSON file.
        
        Args:
            filepath: Path to save file
        """
        data = self.to_dict()
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Memory bank saved to {filepath}")
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'MemoryBank':
        """
        Load memory bank from JSON file.
        
        Args:
            filepath: Path to load file
            
        Returns:
            MemoryBank instance
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Reconstruct user profile
        profile = UserProfile(**data['user_profile'])
        
        # Create memory bank
        memory = cls(
            user_profile=profile,
            budgets=data['budgets'],
            max_history=data.get('max_history', 5)
        )
        
        # Restore conversation history
        for entry_data in data.get('conversation_history', []):
            entry = ConversationEntry(**entry_data)
            memory.conversation_history.append(entry)
        
        logger.info(f"Memory bank loaded from {filepath}")
        return memory
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the memory bank.
        
        Returns:
            Summary dictionary
        """
        return {
            "user": self.user_profile.name,
            "business_type": self.user_profile.business_type,
            "num_budgets": len(self.budgets),
            "total_budget": sum(self.budgets.values()),
            "conversation_entries": len(self.conversation_history),
            "max_history": self.max_history
        }


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    """Test the memory bank."""
    
    print("=" * 60)
    print("FinGuard IntelliAgent - Memory Bank Test")
    print("=" * 60)
    
    # Create user profile
    profile = UserProfile(
        name="Jane Wanjiru",
        business_type="Retail Shop",
        business_name="Wanjiru's Convenience Store",
        location="Nairobi, Kenya"
    )
    
    # Create budgets
    budgets = {
        "transport": 5000,
        "food": 3000,
        "utilities": 4000,
        "supplies": 10000
    }
    
    # Initialize memory bank
    print("\n📝 Creating Memory Bank...")
    memory = MemoryBank(user_profile=profile, budgets=budgets)
    
    # Add some conversation history
    print("\n💬 Adding conversation history...")
    memory.update_history(
        "How much have I spent on transport?",
        "You've spent KES 3,500 on transport this month, which is 70% of your KES 5,000 budget.",
        "Retrieved 5 transport transactions"
    )
    
    memory.update_history(
        "Am I over budget?",
        "No, you're within budget for all categories. Great job!",
        "Compared all spending to budgets"
    )
    
    # Get context
    print("\n📋 Getting full context...")
    print("-" * 60)
    context = memory.get_context()
    print(context)
    print("-" * 60)
    
    # Get summary
    print("\n📊 Memory Bank Summary:")
    summary = memory.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Test save/load
    print("\n💾 Testing save/load...")
    test_file = "/tmp/test_memory.json"
    memory.save_to_file(test_file)
    
    loaded_memory = MemoryBank.load_from_file(test_file)
    print(f"✅ Loaded memory for: {loaded_memory.user_profile.name}")
    print(f"   Conversation entries: {len(loaded_memory.conversation_history)}")
    
    # Cleanup
    Path(test_file).unlink(missing_ok=True)
    
    print("\n✅ All tests passed!")
    print("=" * 60)
