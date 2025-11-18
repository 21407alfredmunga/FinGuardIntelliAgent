"""
FinGuard IntelliAgent - Invoice Collection Tool
===============================================

This tool manages invoice tracking, payment monitoring, and automated
collection follow-ups for Kenyan SMEs.

Milestone 1 Scope:
    - Tool structure and interface definition
    - Invoice tracking framework
    - Placeholder implementation
    
Full Implementation: Milestone 2+

Author: Alfred Munga
License: MIT
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Constants
# ============================================================================

class InvoiceStatus(Enum):
    """Invoice payment status."""
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentMethod(Enum):
    """Payment collection methods."""
    MPESA = "mpesa"
    AIRTEL_MONEY = "airtel_money"
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    OTHER = "other"


class FollowUpAction(Enum):
    """Types of follow-up actions."""
    SEND_REMINDER = "send_reminder"
    CALL_CUSTOMER = "call_customer"
    GENERATE_STATEMENT = "generate_statement"
    ESCALATE = "escalate"
    NEGOTIATE_PAYMENT_PLAN = "negotiate_payment_plan"


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class Invoice:
    """
    Invoice data model.
    
    Attributes:
        invoice_id: Unique invoice identifier
        customer_name: Customer/client name
        customer_phone: Customer phone number
        amount: Invoice amount in KES
        amount_paid: Amount already paid
        due_date: Payment due date
        issue_date: Invoice issue date
        status: Current invoice status
        description: Invoice description/items
        payment_method: Preferred payment method
    """
    invoice_id: str
    customer_name: str
    customer_phone: str
    amount: float
    amount_paid: float
    due_date: datetime
    issue_date: datetime
    status: InvoiceStatus
    description: str
    payment_method: Optional[PaymentMethod] = None


@dataclass
class FollowUpMessage:
    """
    Automated follow-up message.
    
    Attributes:
        message_type: Type of follow-up action
        recipient: Customer name
        phone_number: Customer phone
        message_text: Generated message content
        scheduled_time: When to send the message
        invoice_reference: Related invoice ID
    """
    message_type: FollowUpAction
    recipient: str
    phone_number: str
    message_text: str
    scheduled_time: datetime
    invoice_reference: str


@dataclass
class CollectionReport:
    """
    Invoice collection performance report.
    
    Attributes:
        total_invoices: Total number of invoices
        total_outstanding: Total outstanding amount
        overdue_count: Number of overdue invoices
        overdue_amount: Total overdue amount
        collection_rate: Percentage of invoices paid on time
        average_days_to_payment: Average payment delay
        upcoming_due: Invoices due in next 7 days
    """
    total_invoices: int
    total_outstanding: float
    overdue_count: int
    overdue_amount: float
    collection_rate: float
    average_days_to_payment: float
    upcoming_due: List[Invoice]


# ============================================================================
# Invoice Collection Tool Class
# ============================================================================

class InvoiceCollectionTool:
    """
    Tool for managing invoice tracking and automated collection.
    
    This tool provides:
    - Invoice status tracking
    - Payment monitoring
    - Automated follow-up generation
    - Collection analytics
    - Customer communication templates
    """
    
    def __init__(self):
        """Initialize the invoice collection tool."""
        self.message_templates = self._load_message_templates()
        logger.info("Invoice Collection Tool initialized (Milestone 1 - Placeholder)")
    
    def _load_message_templates(self) -> Dict[str, str]:
        """
        Load SMS message templates for follow-ups.
        
        Returns:
            Dict of message templates
        """
        # TODO Milestone 2: Load from configuration/database
        # TODO Milestone 2: Support multiple languages
        # TODO Milestone 2: Allow custom templates
        
        return {
            "polite_reminder": (
                "Hello {customer_name}, this is a friendly reminder that invoice "
                "{invoice_id} for KES {amount} is due on {due_date}. "
                "Please send payment via M-Pesa to {mpesa_number}. Thank you!"
            ),
            "overdue_notice": (
                "Dear {customer_name}, invoice {invoice_id} for KES {amount} "
                "was due on {due_date} and remains unpaid. Please settle this at your "
                "earliest convenience. Contact us if you need assistance."
            ),
            "payment_plan": (
                "Hi {customer_name}, we understand payment challenges. We're happy to "
                "discuss a payment plan for invoice {invoice_id} (KES {amount}). "
                "Please call or text to arrange."
            ),
            "thank_you": (
                "Thank you {customer_name}! We've received your payment of KES {amount} "
                "for invoice {invoice_id}. We appreciate your business!"
            )
        }
    
    def track_invoice(
        self,
        invoice_id: str,
        customer_name: str,
        amount: float,
        due_date: datetime,
        **kwargs
    ) -> Invoice:
        """
        Create and track a new invoice.
        
        Args:
            invoice_id: Unique invoice identifier
            customer_name: Customer name
            amount: Invoice amount
            due_date: Payment due date
            **kwargs: Additional invoice details
            
        Returns:
            Invoice object
        """
        logger.info(f"Tracking invoice {invoice_id} (placeholder)")
        
        # TODO Milestone 2: Store invoice in database
        # TODO Milestone 2: Set up automated follow-up schedule
        # TODO Milestone 2: Send initial invoice notification
        
        invoice = Invoice(
            invoice_id=invoice_id,
            customer_name=customer_name,
            customer_phone=kwargs.get("customer_phone", ""),
            amount=amount,
            amount_paid=0.0,
            due_date=due_date,
            issue_date=datetime.utcnow(),
            status=InvoiceStatus.DRAFT,
            description=kwargs.get("description", ""),
            payment_method=kwargs.get("payment_method")
        )
        
        return invoice
    
    def update_payment(
        self,
        invoice_id: str,
        payment_amount: float,
        payment_method: PaymentMethod,
        transaction_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update invoice with payment received.
        
        Args:
            invoice_id: Invoice to update
            payment_amount: Amount paid
            payment_method: How payment was received
            transaction_id: Transaction reference (e.g., M-Pesa code)
            
        Returns:
            Dict with update status and new invoice state
        """
        logger.info(f"Updating payment for invoice {invoice_id} (placeholder)")
        
        # TODO Milestone 2: Fetch invoice from database
        # TODO Milestone 2: Update payment records
        # TODO Milestone 2: Send payment confirmation
        # TODO Milestone 2: Cancel scheduled follow-ups if fully paid
        
        return {
            "success": False,
            "message": "Payment tracking will be implemented in Milestone 2",
            "invoice_id": invoice_id,
            "amount_received": payment_amount
        }
    
    def get_outstanding_invoices(
        self,
        status_filter: Optional[List[InvoiceStatus]] = None
    ) -> List[Invoice]:
        """
        Get list of outstanding invoices.
        
        Args:
            status_filter: Filter by specific statuses
            
        Returns:
            List of Invoice objects
        """
        logger.info("Fetching outstanding invoices (placeholder)")
        
        # TODO Milestone 2: Query database for invoices
        # TODO Milestone 2: Apply status filters
        # TODO Milestone 2: Sort by due date/amount
        
        return []
    
    def generate_follow_up(
        self,
        invoice: Invoice,
        action_type: FollowUpAction = FollowUpAction.SEND_REMINDER
    ) -> FollowUpMessage:
        """
        Generate automated follow-up message for an invoice.
        
        Args:
            invoice: Invoice to follow up on
            action_type: Type of follow-up action
            
        Returns:
            FollowUpMessage object
        """
        logger.info(f"Generating follow-up for invoice {invoice.invoice_id} (placeholder)")
        
        # Determine appropriate template
        days_overdue = (datetime.utcnow() - invoice.due_date).days
        
        if days_overdue <= 0:
            template_key = "polite_reminder"
        elif days_overdue <= 7:
            template_key = "overdue_notice"
        else:
            template_key = "payment_plan"
        
        # TODO Milestone 2: Format message with invoice details
        # TODO Milestone 2: Schedule message delivery
        # TODO Milestone 2: Track follow-up history
        
        message = FollowUpMessage(
            message_type=action_type,
            recipient=invoice.customer_name,
            phone_number=invoice.customer_phone,
            message_text="[Placeholder] Follow-up message will be generated in Milestone 2",
            scheduled_time=datetime.utcnow() + timedelta(hours=1),
            invoice_reference=invoice.invoice_id
        )
        
        return message
    
    def generate_collection_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> CollectionReport:
        """
        Generate invoice collection performance report.
        
        Args:
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            CollectionReport object
        """
        logger.info("Generating collection report (placeholder)")
        
        # TODO Milestone 2: Query invoice data
        # TODO Milestone 2: Calculate collection metrics
        # TODO Milestone 2: Identify trends and patterns
        # TODO Milestone 2: Generate actionable insights
        
        return CollectionReport(
            total_invoices=0,
            total_outstanding=0.0,
            overdue_count=0,
            overdue_amount=0.0,
            collection_rate=0.0,
            average_days_to_payment=0.0,
            upcoming_due=[]
        )
    
    def send_batch_reminders(
        self,
        criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send batch reminders based on criteria.
        
        Args:
            criteria: Filter criteria for invoices
            
        Returns:
            Dict with batch operation results
        """
        logger.info("Sending batch reminders (placeholder)")
        
        # TODO Milestone 2: Fetch invoices matching criteria
        # TODO Milestone 2: Generate messages for each
        # TODO Milestone 2: Queue for SMS delivery
        # TODO Milestone 2: Track delivery status
        
        return {
            "success": False,
            "message": "Batch reminder sending will be implemented in Milestone 2"
        }
    
    def get_customer_payment_history(
        self,
        customer_name: str
    ) -> Dict[str, Any]:
        """
        Get payment history for a specific customer.
        
        Args:
            customer_name: Customer to look up
            
        Returns:
            Dict with customer payment history and reliability score
        """
        logger.info(f"Fetching payment history for {customer_name} (placeholder)")
        
        # TODO Milestone 2: Query customer invoices
        # TODO Milestone 2: Calculate reliability metrics
        # TODO Milestone 2: Identify payment patterns
        
        return {
            "customer": customer_name,
            "total_invoices": 0,
            "paid_on_time": 0,
            "average_delay_days": 0,
            "reliability_score": 0.0,
            "message": "Customer history tracking will be implemented in Milestone 2"
        }


# ============================================================================
# Tool Interface Functions
# ============================================================================

def create_invoice_reminder(invoice_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to create an invoice and schedule reminder.
    
    Args:
        invoice_data: Invoice details
        
    Returns:
        Dict with creation status
    """
    tool = InvoiceCollectionTool()
    
    try:
        invoice = tool.track_invoice(
            invoice_id=invoice_data.get("invoice_id"),
            customer_name=invoice_data.get("customer_name"),
            amount=invoice_data.get("amount"),
            due_date=invoice_data.get("due_date")
        )
        
        return {
            "success": True,
            "invoice_id": invoice.invoice_id,
            "message": "Invoice tracked (Milestone 1 placeholder)"
        }
    except Exception as e:
        logger.error(f"Failed to create invoice: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# Example Usage (for testing)
# ============================================================================

if __name__ == "__main__":
    """
    Example usage and testing of the invoice collection tool.
    """
    # Initialize tool
    tool = InvoiceCollectionTool()
    
    print("=" * 60)
    print("Invoice Collection Tool - Test Run (Milestone 1)")
    print("=" * 60)
    
    # Create sample invoice
    print("\nCreating sample invoice...")
    invoice = tool.track_invoice(
        invoice_id="INV-001",
        customer_name="ABC Enterprises",
        customer_phone="254712345678",
        amount=15000.0,
        due_date=datetime.utcnow() + timedelta(days=30),
        description="Website development services"
    )
    
    print(f"Invoice ID: {invoice.invoice_id}")
    print(f"Customer: {invoice.customer_name}")
    print(f"Amount: KES {invoice.amount:,.2f}")
    print(f"Status: {invoice.status.value}")
    
    # Generate follow-up
    print("\nGenerating follow-up message...")
    follow_up = tool.generate_follow_up(invoice)
    print(f"Message Type: {follow_up.message_type.value}")
    print(f"Recipient: {follow_up.recipient}")
    print(f"Scheduled: {follow_up.scheduled_time}")
    
    # Show message templates
    print("\nAvailable message templates:")
    for template_name in tool.message_templates.keys():
        print(f"  - {template_name}")
    
    # Generate collection report
    print("\nGenerating collection report...")
    report = tool.generate_collection_report()
    print(f"Total Invoices: {report.total_invoices}")
    print(f"Total Outstanding: KES {report.total_outstanding:,.2f}")
    
    print("\n" + "=" * 60)
    print("Note: Full implementation coming in Milestone 2")
    print("=" * 60)
