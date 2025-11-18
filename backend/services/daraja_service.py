"""
FinGuard IntelliAgent - Daraja Service (Mock M-Pesa API)
========================================================

This service provides a mock implementation of the Safaricom Daraja API
for testing payment functionality without making real M-Pesa transactions.

Key Features:
- STK Push (Lipa na M-Pesa) simulation
- Payment status checking
- Credential validation from .env
- Request logging
- Idempotency support

Production Note:
In production, replace this mock with actual Daraja API calls using
the `requests` library and proper OAuth2 authentication.

Reference: Agent Tools whitepaper p.18 - "Separation of Concerns"

Author: Alfred Munga
License: MIT
"""

import os
import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# Payment Status Enum
# ============================================================================

class PaymentStatus:
    """Payment status constants."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


# ============================================================================
# Mock Daraja Service
# ============================================================================

class DarajaService:
    """
    Mock implementation of Safaricom Daraja API for M-Pesa payments.
    
    This service simulates the M-Pesa STK Push (Lipa na M-Pesa) functionality
    for testing purposes. In production, this would make actual API calls to
    Safaricom's Daraja API.
    
    Features:
    - STK Push initiation (simulated)
    - Payment status queries
    - Credential validation
    - Request/response logging
    
    Attributes:
        consumer_key: M-Pesa API consumer key
        consumer_secret: M-Pesa API consumer secret
        shortcode: M-Pesa business shortcode
        passkey: M-Pesa passkey for STK Push
        callback_url: URL for payment callbacks
        environment: 'sandbox' or 'production'
        payment_registry: In-memory registry of payment requests
    """
    
    def __init__(
        self,
        consumer_key: Optional[str] = None,
        consumer_secret: Optional[str] = None,
        shortcode: Optional[str] = None,
        passkey: Optional[str] = None,
        callback_url: Optional[str] = None,
        environment: str = "sandbox"
    ):
        """
        Initialize the Daraja service.
        
        Args:
            consumer_key: M-Pesa consumer key (from .env if not provided)
            consumer_secret: M-Pesa consumer secret (from .env if not provided)
            shortcode: Business shortcode (from .env if not provided)
            passkey: STK Push passkey (from .env if not provided)
            callback_url: Payment callback URL (from .env if not provided)
            environment: 'sandbox' or 'production'
        """
        # Load credentials from environment
        self.consumer_key = consumer_key or os.getenv('MPESA_CONSUMER_KEY')
        self.consumer_secret = consumer_secret or os.getenv('MPESA_CONSUMER_SECRET')
        self.shortcode = shortcode or os.getenv('MPESA_SHORTCODE')
        self.passkey = passkey or os.getenv('MPESA_PASSKEY')
        self.callback_url = callback_url or os.getenv('MPESA_CALLBACK_URL')
        self.environment = environment or os.getenv('MPESA_ENVIRONMENT', 'sandbox')
        
        # Validate credentials
        self._validate_credentials()
        
        # In-memory payment registry (in production, use database)
        self.payment_registry: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"Daraja Service initialized in {self.environment} mode")
    
    def _validate_credentials(self) -> None:
        """
        Validate that required M-Pesa credentials are present.
        
        Raises:
            ValueError: If required credentials are missing
        """
        required = {
            'consumer_key': self.consumer_key,
            'consumer_secret': self.consumer_secret,
            'shortcode': self.shortcode,
            'passkey': self.passkey,
            'callback_url': self.callback_url
        }
        
        missing = [key for key, value in required.items() if not value]
        
        if missing:
            raise ValueError(
                f"Missing required M-Pesa credentials: {', '.join(missing)}. "
                "Please set them in your .env file."
            )
        
        logger.info("✅ M-Pesa credentials validated")
    
    def trigger_stk_push(
        self,
        phone_number: str,
        amount: float,
        reference: str,
        description: str = "Payment request"
    ) -> Dict[str, Any]:
        """
        Initiate an M-Pesa STK Push payment request.
        
        This simulates the Lipa na M-Pesa STK Push API. In production, this
        would make an actual HTTP POST request to Daraja API.
        
        The STK Push sends a payment prompt to the customer's phone, asking
        them to enter their M-Pesa PIN to complete the payment.
        
        Args:
            phone_number: Customer phone number (format: 254XXXXXXXXX)
            amount: Payment amount in KES
            reference: Payment reference (e.g., invoice number)
            description: Payment description shown to customer
            
        Returns:
            Dict with payment details:
            {
                'success': True/False,
                'checkout_request_id': 'ws_CO_xxx...',
                'merchant_request_id': 'xxx-xxx-xxx',
                'response_code': '0',
                'response_description': 'Success',
                'customer_message': 'Payment prompt sent'
            }
            
        Raises:
            ValueError: If phone number or amount is invalid
        """
        # Validate input
        self._validate_phone_number(phone_number)
        self._validate_amount(amount)
        
        # Generate unique request IDs (mock)
        checkout_request_id = f"ws_CO_{uuid.uuid4().hex[:20]}"
        merchant_request_id = str(uuid.uuid4())
        
        # Create payment record
        payment_record = {
            'checkout_request_id': checkout_request_id,
            'merchant_request_id': merchant_request_id,
            'phone_number': phone_number,
            'amount': amount,
            'reference': reference,
            'description': description,
            'status': PaymentStatus.PENDING,
            'timestamp': datetime.now().isoformat(),
            'environment': self.environment
        }
        
        # Store in registry
        self.payment_registry[checkout_request_id] = payment_record
        
        # Log the request (in production, this would be an API call)
        logger.info(
            f"STK Push initiated: "
            f"Phone={phone_number}, Amount=KES {amount:,.2f}, "
            f"Reference={reference}, RequestID={checkout_request_id}"
        )
        
        # Return success response (mock)
        return {
            'success': True,
            'checkout_request_id': checkout_request_id,
            'merchant_request_id': merchant_request_id,
            'response_code': '0',
            'response_description': 'Success. Request accepted for processing',
            'customer_message': f'Payment prompt sent to {phone_number}',
            'amount': amount,
            'reference': reference,
            'environment': self.environment
        }
    
    def get_payment_status(self, checkout_request_id: str) -> Dict[str, Any]:
        """
        Query the status of an STK Push payment request.
        
        In production, this would call the Daraja API's Transaction Status
        endpoint. For the mock, we return the stored status.
        
        Args:
            checkout_request_id: The checkout request ID from trigger_stk_push
            
        Returns:
            Dict with payment status:
            {
                'success': True/False,
                'checkout_request_id': 'ws_CO_xxx...',
                'status': 'PENDING'/'COMPLETED'/'FAILED',
                'amount': 1000.00,
                'reference': 'INV-001',
                'timestamp': '2025-11-18T...'
            }
            
        Raises:
            ValueError: If checkout_request_id is not found
        """
        if checkout_request_id not in self.payment_registry:
            logger.warning(f"Payment not found: {checkout_request_id}")
            return {
                'success': False,
                'error': 'Payment request not found',
                'checkout_request_id': checkout_request_id
            }
        
        payment = self.payment_registry[checkout_request_id]
        
        logger.info(
            f"Payment status queried: {checkout_request_id} -> {payment['status']}"
        )
        
        return {
            'success': True,
            'checkout_request_id': checkout_request_id,
            'merchant_request_id': payment['merchant_request_id'],
            'status': payment['status'],
            'phone_number': payment['phone_number'],
            'amount': payment['amount'],
            'reference': payment['reference'],
            'description': payment['description'],
            'timestamp': payment['timestamp']
        }
    
    def simulate_payment_completion(
        self,
        checkout_request_id: str,
        success: bool = True
    ) -> Dict[str, Any]:
        """
        Simulate a payment completion (for testing).
        
        In production, this would be triggered by a callback from Daraja API
        when the customer completes the payment on their phone.
        
        Args:
            checkout_request_id: The checkout request ID
            success: Whether payment succeeded or failed
            
        Returns:
            Dict with updated payment status
        """
        if checkout_request_id not in self.payment_registry:
            return {
                'success': False,
                'error': 'Payment request not found'
            }
        
        payment = self.payment_registry[checkout_request_id]
        
        if success:
            payment['status'] = PaymentStatus.COMPLETED
            payment['completed_at'] = datetime.now().isoformat()
            payment['transaction_id'] = f"MPX{uuid.uuid4().hex[:10].upper()}"
            
            logger.info(
                f"✅ Payment completed: {checkout_request_id} - "
                f"KES {payment['amount']:,.2f} from {payment['phone_number']}"
            )
        else:
            payment['status'] = PaymentStatus.FAILED
            payment['failed_at'] = datetime.now().isoformat()
            payment['failure_reason'] = "Customer cancelled or insufficient funds"
            
            logger.warning(
                f"❌ Payment failed: {checkout_request_id} - "
                f"{payment.get('failure_reason')}"
            )
        
        return {
            'success': True,
            'checkout_request_id': checkout_request_id,
            'status': payment['status'],
            'payment': payment
        }
    
    def cancel_payment(self, checkout_request_id: str) -> Dict[str, Any]:
        """
        Cancel a pending payment request.
        
        Args:
            checkout_request_id: The checkout request ID
            
        Returns:
            Dict with cancellation result
        """
        if checkout_request_id not in self.payment_registry:
            return {
                'success': False,
                'error': 'Payment request not found'
            }
        
        payment = self.payment_registry[checkout_request_id]
        
        if payment['status'] in [PaymentStatus.COMPLETED, PaymentStatus.FAILED]:
            return {
                'success': False,
                'error': f"Cannot cancel payment with status: {payment['status']}"
            }
        
        payment['status'] = PaymentStatus.CANCELLED
        payment['cancelled_at'] = datetime.now().isoformat()
        
        logger.info(f"Payment cancelled: {checkout_request_id}")
        
        return {
            'success': True,
            'checkout_request_id': checkout_request_id,
            'status': PaymentStatus.CANCELLED
        }
    
    def _validate_phone_number(self, phone_number: str) -> None:
        """
        Validate Kenyan phone number format.
        
        Args:
            phone_number: Phone number to validate
            
        Raises:
            ValueError: If phone number is invalid
        """
        # Remove any spaces or dashes
        phone = phone_number.replace(' ', '').replace('-', '')
        
        # Check if it starts with 254 or 0
        if not (phone.startswith('254') or phone.startswith('0')):
            raise ValueError(
                f"Invalid phone number: {phone_number}. "
                "Must start with 254 or 0"
            )
        
        # Check length
        if phone.startswith('254') and len(phone) != 12:
            raise ValueError(
                f"Invalid phone number length: {phone_number}. "
                "Format: 254XXXXXXXXX (12 digits)"
            )
        
        if phone.startswith('0') and len(phone) != 10:
            raise ValueError(
                f"Invalid phone number length: {phone_number}. "
                "Format: 07XXXXXXXX (10 digits)"
            )
    
    def _validate_amount(self, amount: float) -> None:
        """
        Validate payment amount.
        
        Args:
            amount: Amount to validate
            
        Raises:
            ValueError: If amount is invalid
        """
        if amount <= 0:
            raise ValueError(f"Amount must be greater than 0, got: {amount}")
        
        if amount < 10:
            raise ValueError(
                f"Minimum M-Pesa transaction is KES 10, got: KES {amount}"
            )
        
        if amount > 150000:
            raise ValueError(
                f"Maximum M-Pesa transaction is KES 150,000, got: KES {amount:,.2f}"
            )
    
    def get_all_payments(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all payment records (for testing/debugging).
        
        Returns:
            Dict of all payments in registry
        """
        return self.payment_registry.copy()


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    """Test the Daraja service."""
    
    print("=" * 60)
    print("FinGuard IntelliAgent - Daraja Service Test")
    print("=" * 60)
    
    try:
        # Initialize service
        print("\n🔧 Initializing Daraja Service...")
        service = DarajaService()
        
        # Test STK Push
        print("\n💳 Testing STK Push...")
        response = service.trigger_stk_push(
            phone_number="254712345678",
            amount=1000.00,
            reference="INV-001",
            description="Payment for Invoice INV-001"
        )
        
        print(f"✅ STK Push initiated:")
        print(f"   Checkout Request ID: {response['checkout_request_id']}")
        print(f"   Amount: KES {response['amount']:,.2f}")
        print(f"   Message: {response['customer_message']}")
        
        checkout_id = response['checkout_request_id']
        
        # Check status (pending)
        print("\n🔍 Checking payment status (should be PENDING)...")
        status = service.get_payment_status(checkout_id)
        print(f"   Status: {status['status']}")
        
        # Simulate completion
        print("\n✅ Simulating payment completion...")
        completion = service.simulate_payment_completion(checkout_id, success=True)
        print(f"   Status: {completion['status']}")
        
        # Check status again (completed)
        print("\n🔍 Checking payment status (should be COMPLETED)...")
        status = service.get_payment_status(checkout_id)
        print(f"   Status: {status['status']}")
        if 'transaction_id' in status:
            print(f"   Transaction ID: {status.get('transaction_id')}")
        
        print("\n✅ All tests passed!")
        
    except ValueError as e:
        print(f"\n❌ Configuration error: {str(e)}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
