"""
FinGuard IntelliAgent - SMS Parser Tool
=======================================

This tool extracts structured transaction data from SMS messages sent by
M-Pesa and Airtel Money mobile money platforms in Kenya.

Milestone 1 Scope:
    - Tool structure and interface definition
    - Basic SMS pattern recognition framework
    - Placeholder implementation
    
Full Implementation: Milestone 2+

Author: Alfred Munga
License: MIT
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re
import logging

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Constants
# ============================================================================

class ServiceProvider(Enum):
    """Mobile money service providers supported."""
    MPESA = "mpesa"
    AIRTEL_MONEY = "airtel_money"
    UNKNOWN = "unknown"


class TransactionType(Enum):
    """Types of mobile money transactions."""
    RECEIVED = "received"
    SENT = "sent"
    PAID = "paid"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"
    AIRTIME = "airtime"
    REVERSAL = "reversal"
    UNKNOWN = "unknown"


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class ParsedTransaction:
    """
    Structured transaction data extracted from SMS.
    
    Attributes:
        transaction_id: Unique transaction reference code
        transaction_type: Type of transaction (sent/received/paid/etc)
        amount: Transaction amount in KES
        other_party: Name of sender/recipient/merchant
        phone_number: Phone number involved (if available)
        balance: Account balance after transaction
        timestamp: Transaction timestamp
        service_provider: M-Pesa or Airtel Money
        raw_sms: Original SMS text
        confidence_score: Parsing confidence (0-1)
    """
    transaction_id: str
    transaction_type: TransactionType
    amount: float
    other_party: str
    phone_number: Optional[str]
    balance: Optional[float]
    timestamp: datetime
    service_provider: ServiceProvider
    raw_sms: str
    confidence_score: float


@dataclass
class ParsingResult:
    """
    Result of SMS parsing operation.
    
    Attributes:
        success: Whether parsing was successful
        transaction: Parsed transaction data (if successful)
        error: Error message (if unsuccessful)
        warnings: List of warnings encountered during parsing
    """
    success: bool
    transaction: Optional[ParsedTransaction] = None
    error: Optional[str] = None
    warnings: List[str] = None


# ============================================================================
# SMS Parser Tool Class
# ============================================================================

class SMSParserTool:
    """
    Tool for parsing M-Pesa and Airtel Money SMS messages.
    
    This tool handles:
    - Service provider detection
    - Transaction type identification
    - Amount and reference extraction
    - Party name and contact extraction
    - Timestamp parsing
    """
    
    def __init__(self):
        """Initialize the SMS parser tool."""
        self.supported_providers = [ServiceProvider.MPESA, ServiceProvider.AIRTEL_MONEY]
        logger.info("SMS Parser Tool initialized (Milestone 1 - Placeholder)")
    
    def parse_sms(self, sms_text: str) -> ParsingResult:
        """
        Parse an SMS message to extract transaction data.
        
        This is a placeholder implementation. Milestone 2 will include:
        - Comprehensive M-Pesa format support (10+ message types)
        - Airtel Money format support
        - Fuzzy matching for merchant names
        - Multi-language support (English/Swahili)
        - Advanced error handling
        
        Args:
            sms_text: Raw SMS message text
            
        Returns:
            ParsingResult containing extracted transaction data or error
        """
        logger.info("Parsing SMS (Milestone 1 placeholder)")
        
        # Validate input
        if not sms_text or not sms_text.strip():
            return ParsingResult(
                success=False,
                error="SMS text cannot be empty"
            )
        
        # Detect service provider
        provider = self._detect_provider(sms_text)
        
        # TODO Milestone 2: Implement full parsing logic
        # TODO Milestone 2: Add regex patterns for different message types
        # TODO Milestone 2: Extract transaction details
        # TODO Milestone 2: Validate extracted data
        # TODO Milestone 2: Calculate confidence score
        
        return ParsingResult(
            success=False,
            error="Full SMS parsing will be implemented in Milestone 2",
            warnings=[
                f"Detected provider: {provider.value}",
                "Placeholder implementation active"
            ]
        )
    
    def _detect_provider(self, sms_text: str) -> ServiceProvider:
        """
        Detect the mobile money service provider from SMS text.
        
        Args:
            sms_text: Raw SMS message text
            
        Returns:
            ServiceProvider enum value
        """
        sms_lower = sms_text.lower()
        
        # M-Pesa indicators
        mpesa_indicators = ["mpesa", "m-pesa", "safaricom"]
        if any(indicator in sms_lower for indicator in mpesa_indicators):
            return ServiceProvider.MPESA
        
        # Airtel Money indicators
        airtel_indicators = ["airtel money", "airtel", "airtelmoney"]
        if any(indicator in sms_lower for indicator in airtel_indicators):
            return ServiceProvider.AIRTEL_MONEY
        
        return ServiceProvider.UNKNOWN
    
    def _extract_amount(self, text: str) -> Optional[float]:
        """
        Extract monetary amount from text.
        
        Args:
            text: Text containing amount
            
        Returns:
            Extracted amount or None
        """
        # TODO Milestone 2: Implement robust amount extraction
        # Patterns to handle: "KES 5,000", "Ksh5000", "5000.00", etc.
        return None
    
    def _extract_transaction_id(self, text: str) -> Optional[str]:
        """
        Extract transaction reference code.
        
        Args:
            text: SMS text
            
        Returns:
            Transaction ID or None
        """
        # TODO Milestone 2: Implement transaction ID extraction
        # M-Pesa format: RB12KLM, QC34XYZ, etc.
        return None
    
    def _identify_transaction_type(self, text: str) -> TransactionType:
        """
        Identify the type of transaction from SMS text.
        
        Args:
            text: SMS text
            
        Returns:
            TransactionType enum value
        """
        text_lower = text.lower()
        
        # TODO Milestone 2: Comprehensive pattern matching
        
        if "received" in text_lower or "sent you" in text_lower:
            return TransactionType.RECEIVED
        elif "sent to" in text_lower or "paid to" in text_lower:
            return TransactionType.SENT
        elif "paid for" in text_lower or "purchased" in text_lower:
            return TransactionType.PAID
        elif "withdraw" in text_lower:
            return TransactionType.WITHDRAWAL
        
        return TransactionType.UNKNOWN
    
    def batch_parse(self, sms_messages: List[str]) -> List[ParsingResult]:
        """
        Parse multiple SMS messages in batch.
        
        Args:
            sms_messages: List of SMS message texts
            
        Returns:
            List of ParsingResult objects
        """
        results = []
        for sms in sms_messages:
            result = self.parse_sms(sms)
            results.append(result)
        
        logger.info(f"Batch parsed {len(sms_messages)} messages")
        return results
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """
        Get information about supported SMS formats.
        
        Returns:
            Dict mapping providers to supported message types
        """
        return {
            "mpesa": [
                "Payment received",
                "Payment sent",
                "Paybill payment",
                "Till number payment",
                "Withdrawal from agent",
                "Airtime purchase",
                "Reversal notification"
            ],
            "airtel_money": [
                "Money received",
                "Money sent",
                "Bill payment",
                "Agent withdrawal"
            ],
            "implementation_status": "Placeholder - Milestone 2"
        }


# ============================================================================
# Tool Interface Functions
# ============================================================================

def parse_transaction_sms(sms_text: str) -> Dict[str, Any]:
    """
    Convenience function to parse a single SMS message.
    
    Args:
        sms_text: Raw SMS message text
        
    Returns:
        Dict containing parsing result
    """
    parser = SMSParserTool()
    result = parser.parse_sms(sms_text)
    
    return {
        "success": result.success,
        "transaction": result.transaction.__dict__ if result.transaction else None,
        "error": result.error,
        "warnings": result.warnings
    }


# ============================================================================
# Example Usage (for testing)
# ============================================================================

if __name__ == "__main__":
    """
    Example usage and testing of the SMS parser tool.
    """
    # Sample M-Pesa SMS messages
    sample_sms = [
        "RB12KLM Confirmed. You have received Ksh5,000.00 from JOHN DOE 254712345678 on 18/11/2025 at 10:30 AM. New M-PESA balance is Ksh15,000.00",
        "QC34XYZ Confirmed. Ksh2,500.00 sent to JANE SMITH 254723456789 on 18/11/2025 at 2:15 PM. New M-PESA balance is Ksh12,500.00",
        "RF45ABC Confirmed. You have paid Ksh1,200.00 to SUPERMARKET LTD for account 123456 on 18/11/2025. New balance is Ksh11,300.00"
    ]
    
    # Initialize parser
    parser = SMSParserTool()
    
    print("=" * 60)
    print("SMS Parser Tool - Test Run (Milestone 1)")
    print("=" * 60)
    
    # Show supported formats
    print("\nSupported Formats:")
    formats = parser.get_supported_formats()
    for provider, types in formats.items():
        if provider != "implementation_status":
            print(f"\n{provider.upper()}:")
            for msg_type in types:
                print(f"  - {msg_type}")
    
    # Test parsing
    print("\n" + "=" * 60)
    print("Testing SMS Parsing:")
    print("=" * 60)
    
    for i, sms in enumerate(sample_sms, 1):
        print(f"\nTest {i}:")
        print(f"SMS: {sms[:70]}...")
        result = parser.parse_sms(sms)
        print(f"Success: {result.success}")
        if result.error:
            print(f"Error: {result.error}")
        if result.warnings:
            print(f"Warnings: {result.warnings}")
    
    print("\n" + "=" * 60)
    print("Note: Full implementation coming in Milestone 2")
    print("=" * 60)
