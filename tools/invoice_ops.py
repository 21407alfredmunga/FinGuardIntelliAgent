"""
FinGuard IntelliAgent - Invoice Operations Tools
================================================

This module implements task-oriented tools for invoice management and
payment collection, following ADK best practices.

Key Concepts Implemented:
1. **Task-Oriented Design**: Tools represent business tasks ("Send Reminder")
   rather than raw API calls [Ref: Agent Tools p.18]
2. **Idempotency**: Payment requests check status to prevent duplicates
   [Ref: Prototype to Production p.21]
3. **Separation of Concerns**: External API logic isolated from tool definitions

Tools:
- GetUnpaidInvoicesTool: Retrieve unpaid/overdue invoices
- SendPaymentRequestTool: Initiate M-Pesa payment collection

Author: Alfred Munga
License: MIT
"""

import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

# Import Daraja service
import sys
sys.path.append(str(Path(__file__).parent.parent))

from backend.services.daraja_service import DarajaService, PaymentStatus

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# Pydantic Models for Tool Inputs
# ============================================================================

class GetUnpaidInvoicesInput(BaseModel):
    """
    Input schema for GetUnpaidInvoicesTool.
    
    Attributes:
        user_id: User ID (for multi-tenant systems, currently unused)
        include_pending: Whether to include invoices with pending payments
    """
    user_id: Optional[str] = Field(
        default="default_user",
        description="User ID to filter invoices (for future multi-tenant support)"
    )
    include_pending: bool = Field(
        default=False,
        description="Include invoices with payment status PROCESSING"
    )


class SendPaymentRequestInput(BaseModel):
    """
    Input schema for SendPaymentRequestTool.
    
    Attributes:
        invoice_id: The invoice ID to collect payment for
        force: Whether to bypass idempotency checks (use with caution)
    """
    invoice_id: str = Field(
        ...,
        description="The invoice ID (e.g., 'INV-2025-1804')"
    )
    force: bool = Field(
        default=False,
        description="Force payment request even if already processing (dangerous!)"
    )
    
    @field_validator('invoice_id')
    @classmethod
    def validate_invoice_id(cls, v):
        """Validate invoice ID format."""
        if not v or not v.startswith('INV-'):
            raise ValueError(
                f"Invalid invoice ID format: {v}. Must start with 'INV-'"
            )
        return v


# ============================================================================
# Invoice Data Manager
# ============================================================================

class InvoiceDataManager:
    """
    Manages invoice data persistence and retrieval.
    
    This class handles reading and writing invoice data to/from JSON files,
    with proper error handling and data validation.
    
    Attributes:
        data_path: Path to invoices.json file
        invoices: Cached list of invoices
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the invoice data manager.
        
        Args:
            data_path: Path to invoices.json (uses default if not provided)
        """
        if data_path is None:
            project_root = Path(__file__).parent.parent
            data_path = project_root / "data" / "synthetic" / "invoices.json"
        
        self.data_path = Path(data_path)
        self.invoices: List[Dict[str, Any]] = []
        self._load_invoices()
    
    def _load_invoices(self) -> None:
        """Load invoices from JSON file."""
        try:
            if not self.data_path.exists():
                logger.warning(f"Invoice file not found: {self.data_path}")
                self.invoices = []
                return
            
            with open(self.data_path, 'r') as f:
                self.invoices = json.load(f)
            
            logger.info(f"Loaded {len(self.invoices)} invoices from {self.data_path}")
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {self.data_path}: {str(e)}")
            self.invoices = []
        except Exception as e:
            logger.error(f"Error loading invoices: {str(e)}")
            self.invoices = []
    
    def save_invoices(self) -> None:
        """Save invoices to JSON file."""
        try:
            with open(self.data_path, 'w') as f:
                json.dump(self.invoices, f, indent=2)
            
            logger.info(f"Saved {len(self.invoices)} invoices to {self.data_path}")
        
        except Exception as e:
            logger.error(f"Error saving invoices: {str(e)}")
            raise
    
    def get_invoice_by_id(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single invoice by ID.
        
        Args:
            invoice_id: The invoice ID
            
        Returns:
            Invoice dict or None if not found
        """
        for invoice in self.invoices:
            if invoice.get('invoice_id') == invoice_id:
                return invoice
        return None
    
    def update_invoice_status(
        self,
        invoice_id: str,
        status: str,
        payment_info: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update invoice status and optionally payment information.
        
        Args:
            invoice_id: The invoice ID
            status: New status ('paid', 'processing', 'overdue', etc.)
            payment_info: Optional payment details to store
            
        Returns:
            True if updated successfully, False if invoice not found
        """
        invoice = self.get_invoice_by_id(invoice_id)
        
        if not invoice:
            logger.warning(f"Invoice not found for update: {invoice_id}")
            return False
        
        invoice['status'] = status.lower()
        invoice['updated_at'] = datetime.now().isoformat()
        
        if payment_info:
            invoice['payment_info'] = payment_info
        
        self.save_invoices()
        
        logger.info(f"Updated invoice {invoice_id}: status={status}")
        return True
    
    def get_unpaid_invoices(
        self,
        include_pending: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all unpaid invoices.
        
        Args:
            include_pending: Include invoices with status 'processing'
            
        Returns:
            List of unpaid invoices
        """
        unpaid_statuses = ['unpaid', 'overdue', 'pending']
        
        if include_pending:
            unpaid_statuses.append('processing')
        
        return [
            inv for inv in self.invoices
            if inv.get('status', '').lower() in unpaid_statuses
        ]


# ============================================================================
# Tool 1: Get Unpaid Invoices
# ============================================================================

class GetUnpaidInvoicesTool:
    """
    Tool to retrieve unpaid invoices from the system.
    
    This tool implements task-oriented design by focusing on the business
    task ("Get unpaid invoices") rather than raw data access.
    
    Context Optimization:
    Returns only essential fields (ID, Customer, Amount, Due Date) to save
    context tokens for LLM processing [Ref: Context Engineering p.23].
    
    Usage:
        tool = GetUnpaidInvoicesTool()
        result = tool.run(GetUnpaidInvoicesInput(user_id="user123"))
    """
    
    name = "get_unpaid_invoices"
    description = """
    Retrieves a list of all unpaid or overdue invoices for the business.
    
    Use this tool when:
    - User asks "Who owes me money?"
    - User wants to see outstanding invoices
    - User asks about receivables or aged debt
    
    This tool ONLY retrieves information. It does NOT send any messages
    or requests to customers.
    
    Returns: List of invoices with ID, customer name, amount due, and due date.
    """
    
    def __init__(self, data_manager: Optional[InvoiceDataManager] = None):
        """
        Initialize the tool.
        
        Args:
            data_manager: Invoice data manager (creates new if not provided)
        """
        self.data_manager = data_manager or InvoiceDataManager()
    
    def run(self, input_data: GetUnpaidInvoicesInput) -> Dict[str, Any]:
        """
        Execute the tool to get unpaid invoices.
        
        Args:
            input_data: Tool input parameters
            
        Returns:
            Dict with:
            {
                'success': True/False,
                'invoices': [...],
                'total_count': int,
                'total_amount': float
            }
        """
        try:
            # Get unpaid invoices
            unpaid = self.data_manager.get_unpaid_invoices(
                include_pending=input_data.include_pending
            )
            
            # Extract only essential fields (context optimization)
            essential_fields = []
            total_amount = 0.0
            
            for inv in unpaid:
                essential_fields.append({
                    'invoice_id': inv.get('invoice_id'),
                    'customer_name': inv.get('customer_name'),
                    'customer_phone': inv.get('customer_phone'),
                    'amount_outstanding': inv.get('amount_outstanding', inv.get('amount', 0)),
                    'due_date': inv.get('due_date'),
                    'status': inv.get('status'),
                    'days_overdue': self._calculate_days_overdue(inv.get('due_date'))
                })
                
                total_amount += inv.get('amount_outstanding', inv.get('amount', 0))
            
            # Sort by days overdue (most overdue first)
            essential_fields.sort(key=lambda x: x['days_overdue'], reverse=True)
            
            logger.info(
                f"Retrieved {len(essential_fields)} unpaid invoices, "
                f"Total: KES {total_amount:,.2f}"
            )
            
            return {
                'success': True,
                'invoices': essential_fields,
                'total_count': len(essential_fields),
                'total_amount': total_amount,
                'currency': 'KES'
            }
        
        except Exception as e:
            logger.error(f"Error retrieving unpaid invoices: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'invoices': [],
                'total_count': 0,
                'total_amount': 0
            }
    
    def _calculate_days_overdue(self, due_date_str: str) -> int:
        """
        Calculate number of days overdue.
        
        Args:
            due_date_str: Due date as ISO string
            
        Returns:
            Number of days overdue (0 if not overdue)
        """
        if not due_date_str:
            return 0
        
        try:
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            days = (datetime.now() - due_date).days
            return max(0, days)
        except Exception:
            return 0


# ============================================================================
# Tool 2: Send Payment Request
# ============================================================================

class SendPaymentRequestTool:
    """
    Tool to initiate M-Pesa payment collection for an invoice.
    
    This tool implements:
    1. **Task-Oriented Design**: Represents the business task "Collect Payment"
    2. **Idempotency**: Checks if payment is already processing before initiating
    3. **Separation of Concerns**: Uses DarajaService for external API calls
    
    Critical Safety Features:
    - Pre-checks invoice status (PAID or PROCESSING)
    - Validates phone number and amount
    - Updates invoice state atomically
    - Logs all payment requests
    
    Usage:
        tool = SendPaymentRequestTool()
        result = tool.run(SendPaymentRequestInput(invoice_id="INV-2025-1804"))
    
    Reference: Agent Tools p.19 - "Idempotency in Action Tools"
    """
    
    name = "send_payment_request"
    description = """
    Initiates an M-Pesa STK Push payment request to collect payment for a specific invoice.
    
    ⚠️  IMPORTANT: Use this tool ONLY when:
    - User explicitly confirms they want to request payment
    - User says "send payment request", "collect payment", or similar
    
    DO NOT use this tool for:
    - Just viewing unpaid invoices (use get_unpaid_invoices instead)
    - Getting invoice information
    - Checking payment status
    
    This tool will:
    1. Validate the invoice exists and is unpaid
    2. Check if payment is already being processed (idempotency)
    3. Send M-Pesa payment prompt to customer's phone
    4. Update invoice status to PROCESSING
    
    The customer will receive a payment prompt on their phone and must
    enter their M-Pesa PIN to complete the payment.
    
    Returns: Payment request details including checkout request ID.
    """
    
    def __init__(
        self,
        data_manager: Optional[InvoiceDataManager] = None,
        daraja_service: Optional[DarajaService] = None
    ):
        """
        Initialize the tool.
        
        Args:
            data_manager: Invoice data manager
            daraja_service: Daraja M-Pesa service
        """
        self.data_manager = data_manager or InvoiceDataManager()
        self.daraja_service = daraja_service or DarajaService()
    
    def run(self, input_data: SendPaymentRequestInput) -> Dict[str, Any]:
        """
        Execute the tool to send a payment request.
        
        This implements the idempotency pattern:
        1. Check if invoice is already PAID or PROCESSING
        2. If so, return error explaining why
        3. Otherwise, proceed with payment request
        
        Args:
            input_data: Tool input parameters
            
        Returns:
            Dict with payment request result
        """
        invoice_id = input_data.invoice_id
        
        try:
            # Step 1: Get invoice
            invoice = self.data_manager.get_invoice_by_id(invoice_id)
            
            if not invoice:
                logger.warning(f"Invoice not found: {invoice_id}")
                return {
                    'success': False,
                    'error': f"Invoice {invoice_id} not found",
                    'invoice_id': invoice_id
                }
            
            # Step 2: Idempotency check - is it already paid?
            if invoice.get('status', '').lower() == 'paid':
                logger.info(f"Invoice {invoice_id} is already PAID")
                return {
                    'success': False,
                    'error': f"Invoice {invoice_id} is already PAID",
                    'reason': 'idempotency_check',
                    'invoice_id': invoice_id,
                    'status': 'paid',
                    'message': (
                        f"Cannot send payment request for invoice {invoice_id}. "
                        f"This invoice was already paid on {invoice.get('payment_date', 'unknown date')}."
                    )
                }
            
            # Step 3: Idempotency check - is payment already processing?
            if invoice.get('status', '').lower() == 'processing' and not input_data.force:
                logger.info(f"Invoice {invoice_id} is already PROCESSING")
                payment_info = invoice.get('payment_info', {})
                checkout_id = payment_info.get('checkout_request_id', 'unknown')
                
                return {
                    'success': False,
                    'error': f"Payment request already in progress for invoice {invoice_id}",
                    'reason': 'idempotency_check',
                    'invoice_id': invoice_id,
                    'status': 'processing',
                    'checkout_request_id': checkout_id,
                    'message': (
                        f"Cannot send duplicate payment request for invoice {invoice_id}. "
                        f"A payment request is already being processed (Checkout ID: {checkout_id}). "
                        f"Please wait for the customer to complete the current request or check "
                        f"its status before sending another."
                    )
                }
            
            # Step 4: Validate invoice has required fields
            phone = invoice.get('customer_phone')
            amount = invoice.get('amount_outstanding', invoice.get('amount'))
            
            if not phone:
                return {
                    'success': False,
                    'error': f"Invoice {invoice_id} has no customer phone number",
                    'invoice_id': invoice_id
                }
            
            # Normalize phone number: Remove + prefix if present
            phone = phone.strip()
            if phone.startswith('+'):
                phone = phone[1:]  # Remove the '+' prefix
            
            if not amount or amount <= 0:
                return {
                    'success': False,
                    'error': f"Invoice {invoice_id} has invalid amount: {amount}",
                    'invoice_id': invoice_id
                }
            
            # Step 5: Initiate STK Push via Daraja Service
            logger.info(
                f"Initiating payment request: {invoice_id} - "
                f"KES {amount:,.2f} to {phone}"
            )
            
            payment_response = self.daraja_service.trigger_stk_push(
                phone_number=phone,
                amount=amount,
                reference=invoice_id,
                description=f"Payment for {invoice.get('description', 'Invoice')}"
            )
            
            if not payment_response.get('success'):
                return {
                    'success': False,
                    'error': 'Failed to initiate payment request',
                    'details': payment_response,
                    'invoice_id': invoice_id
                }
            
            # Step 6: Update invoice status to PROCESSING
            self.data_manager.update_invoice_status(
                invoice_id=invoice_id,
                status='processing',
                payment_info={
                    'checkout_request_id': payment_response.get('checkout_request_id'),
                    'merchant_request_id': payment_response.get('merchant_request_id'),
                    'payment_initiated_at': datetime.now().isoformat(),
                    'phone_number': phone,
                    'amount': amount
                }
            )
            
            logger.info(
                f"✅ Payment request sent successfully: {invoice_id} - "
                f"Checkout ID: {payment_response.get('checkout_request_id')}"
            )
            
            # Step 7: Return success response
            return {
                'success': True,
                'invoice_id': invoice_id,
                'customer_name': invoice.get('customer_name'),
                'customer_phone': phone,
                'amount': amount,
                'currency': 'KES',
                'checkout_request_id': payment_response.get('checkout_request_id'),
                'merchant_request_id': payment_response.get('merchant_request_id'),
                'status': 'processing',
                'message': (
                    f"Payment request sent successfully to {invoice.get('customer_name')} "
                    f"({phone}) for KES {amount:,.2f}. "
                    f"The customer will receive a payment prompt on their phone."
                )
            }
        
        except Exception as e:
            logger.error(f"Error sending payment request for {invoice_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'invoice_id': invoice_id
            }


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    """Test the invoice operations tools."""
    
    print("=" * 60)
    print("FinGuard IntelliAgent - Invoice Operations Tools Test")
    print("=" * 60)
    
    # Test 1: Get Unpaid Invoices
    print("\n📋 Test 1: Get Unpaid Invoices")
    print("-" * 60)
    
    tool1 = GetUnpaidInvoicesTool()
    result1 = tool1.run(GetUnpaidInvoicesInput(user_id="test_user"))
    
    if result1['success']:
        print(f"✅ Found {result1['total_count']} unpaid invoices")
        print(f"   Total Outstanding: KES {result1['total_amount']:,.2f}")
        
        if result1['invoices']:
            print("\n   Top 3 Most Overdue:")
            for inv in result1['invoices'][:3]:
                print(f"   - {inv['invoice_id']}: {inv['customer_name']}")
                print(f"     Amount: KES {inv['amount_outstanding']:,.2f}")
                print(f"     Days Overdue: {inv['days_overdue']}")
    else:
        print(f"❌ Error: {result1.get('error')}")
    
    # Test 2: Send Payment Request (First Time)
    if result1['success'] and result1['invoices']:
        print("\n\n💳 Test 2: Send Payment Request (First Time)")
        print("-" * 60)
        
        test_invoice_id = result1['invoices'][0]['invoice_id']
        print(f"   Invoice: {test_invoice_id}")
        
        tool2 = SendPaymentRequestTool()
        result2 = tool2.run(SendPaymentRequestInput(invoice_id=test_invoice_id))
        
        if result2['success']:
            print(f"✅ Payment request sent successfully!")
            print(f"   Checkout ID: {result2['checkout_request_id']}")
            print(f"   Customer: {result2['customer_name']}")
            print(f"   Amount: KES {result2['amount']:,.2f}")
        else:
            print(f"❌ Error: {result2.get('error')}")
        
        # Test 3: Try Again (Idempotency Check)
        print("\n\n🔒 Test 3: Send Payment Request Again (Should Fail)")
        print("-" * 60)
        print("   Testing idempotency protection...")
        
        result3 = tool2.run(SendPaymentRequestInput(invoice_id=test_invoice_id))
        
        if not result3['success']:
            print(f"✅ Idempotency check worked!")
            print(f"   Reason: {result3.get('reason')}")
            message = result3.get('message', '')
            if message:
                print(f"   Message: {message[:100]}...")
            else:
                print(f"   Error: {result3.get('error')}")
        else:
            print(f"❌ Idempotency check failed - duplicate request sent!")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
