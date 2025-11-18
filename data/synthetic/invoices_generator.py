"""
FinGuard IntelliAgent - Invoices Generator
==========================================

This module generates synthetic invoice data for testing the invoice
collection tool.

Generates realistic Kenyan SME invoices with:
- Invoice IDs
- Customer information
- Amounts
- Due dates
- Payment status
- Descriptions

Author: Alfred Munga
License: MIT
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict
import os


# ============================================================================
# Configuration and Data
# ============================================================================

# Kenyan business names
KENYAN_BUSINESSES = [
    "Mwangi Enterprises Ltd",
    "Nairobi Trading Co",
    "Kiambu Construction",
    "Coastal Logistics Ltd",
    "Highland Coffee Exporters",
    "Rift Valley Traders",
    "Safari Tech Solutions",
    "Jambo Hardware Ltd",
    "Makini School Supplies",
    "Tumaini Medical Supplies",
    "Furaha Events Ltd",
    "Upendo Catering Services",
    "Amani Security Services",
    "Baraka Transport Ltd",
    "Zawadi Gift Shop",
    "Rafiki Motors Ltd",
    "Habari Media Group",
    "Ujuzi Consultants",
    "Fahari Fashion House",
    "Malaika Beauty Salon"
]

# Service/product descriptions
SERVICE_DESCRIPTIONS = [
    "Website Development Services",
    "Mobile App Development",
    "Graphic Design Package",
    "Social Media Management - Q4 2025",
    "SEO Optimization Services",
    "Consulting Services - November 2025",
    "Software Maintenance - Annual",
    "IT Support Services - Monthly",
    "Network Infrastructure Setup",
    "Database Migration Project",
    "Content Writing Services",
    "Video Production Package",
    "Photography Services - Corporate Event",
    "Legal Advisory Services",
    "Accounting Services - Q4 2025",
    "Marketing Campaign Management",
    "Office Supplies - Bulk Order",
    "Printing Services - Business Cards",
    "Training Workshop - Digital Marketing",
    "Cloud Storage Services - Annual"
]

PRODUCT_DESCRIPTIONS = [
    "Office Furniture - 10 Desks & Chairs",
    "Computer Equipment - 5 Laptops",
    "Printer & Accessories",
    "Network Equipment - Routers & Switches",
    "Security Cameras - 8 Units",
    "Air Conditioning Units - 3 Units",
    "Generator - 20KVA",
    "Solar Panel Installation",
    "Water Dispenser - 2 Units",
    "Office Supplies - Monthly Stock",
    "Cleaning Equipment & Supplies",
    "Fire Safety Equipment",
    "Coffee Machine & Supplies",
    "Projector & Screen",
    "Whiteboard & Markers",
    "Filing Cabinets - 5 Units",
    "Chairs - Conference Room Set",
    "LED TV - 55 inch",
    "Sound System",
    "Stationery - Bulk Purchase"
]


# ============================================================================
# Helper Functions
# ============================================================================

def generate_invoice_id() -> str:
    """
    Generate a realistic invoice ID.
    
    Returns:
        Invoice ID in format INV-YYYY-NNNN
    """
    year = datetime.now().year
    number = random.randint(1000, 9999)
    return f"INV-{year}-{number}"


def random_due_date(issued_date: datetime = None, days_range: tuple = (7, 90)) -> datetime:
    """
    Generate a random due date.
    
    Args:
        issued_date: Invoice issue date (defaults to recent past)
        days_range: Range of days from issue date (min, max)
        
    Returns:
        Due date
    """
    if issued_date is None:
        issued_date = datetime.now() - timedelta(days=random.randint(1, 60))
    
    days_until_due = random.randint(days_range[0], days_range[1])
    return issued_date + timedelta(days=days_until_due)


def generate_invoice_amount() -> float:
    """
    Generate realistic invoice amount for Kenyan SME.
    
    Returns:
        Invoice amount in KES
    """
    # Weight towards different price ranges
    amount_ranges = [
        (5000, 20000, 0.3),      # Small invoices
        (20000, 50000, 0.35),    # Medium invoices
        (50000, 150000, 0.25),   # Large invoices
        (150000, 500000, 0.1)    # Very large invoices
    ]
    
    selected_range = random.choices(
        amount_ranges,
        weights=[r[2] for r in amount_ranges]
    )[0]
    
    amount = random.uniform(selected_range[0], selected_range[1])
    return round(amount, 2)


def determine_status(due_date: datetime, issue_date: datetime) -> str:
    """
    Determine invoice status based on dates.
    
    Args:
        due_date: Invoice due date
        issue_date: Invoice issue date
        
    Returns:
        Status: 'paid', 'unpaid', 'overdue', 'partially_paid'
    """
    now = datetime.now()
    
    # Realistic distribution
    statuses = ['paid', 'unpaid', 'overdue', 'partially_paid']
    
    # If due date has passed
    if due_date < now:
        # 60% chance paid even if overdue, 30% overdue, 10% partially paid
        return random.choices(
            ['paid', 'overdue', 'partially_paid'],
            weights=[0.6, 0.3, 0.1]
        )[0]
    else:
        # Future due date
        # 40% already paid, 50% unpaid, 10% partially paid
        return random.choices(
            ['paid', 'unpaid', 'partially_paid'],
            weights=[0.4, 0.5, 0.1]
        )[0]


def generate_payment_date(issue_date: datetime, due_date: datetime, status: str) -> str:
    """
    Generate payment date if invoice is paid.
    
    Args:
        issue_date: Invoice issue date
        due_date: Invoice due date
        status: Invoice status
        
    Returns:
        Payment date ISO string or empty string
    """
    if status == 'paid':
        # Payment typically between issue and due date, or shortly after
        days_range = (due_date - issue_date).days
        days_to_payment = random.randint(0, days_range + 14)  # +14 for late payments
        payment_date = issue_date + timedelta(days=days_to_payment)
        return payment_date.isoformat()
    elif status == 'partially_paid':
        # Partial payment typically closer to due date
        days_range = (due_date - issue_date).days
        days_to_payment = random.randint(int(days_range * 0.5), days_range + 7)
        payment_date = issue_date + timedelta(days=days_to_payment)
        return payment_date.isoformat()
    
    return ""


# ============================================================================
# Main Generation Function
# ============================================================================

def generate_synthetic_invoices(num_invoices: int = 20, output_file: str = None) -> List[Dict]:
    """
    Generate synthetic invoice dataset.
    
    Args:
        num_invoices: Number of invoices to generate
        output_file: Optional JSON file path to save dataset
        
    Returns:
        List of invoice dictionaries
    """
    print(f"Generating {num_invoices} synthetic invoices...")
    
    invoices = []
    
    for i in range(num_invoices):
        # Generate dates
        issue_date = datetime.now() - timedelta(days=random.randint(1, 90))
        due_date = random_due_date(issue_date)
        
        # Determine status
        status = determine_status(due_date, issue_date)
        
        # Generate amounts
        total_amount = generate_invoice_amount()
        
        if status == 'partially_paid':
            amount_paid = round(total_amount * random.uniform(0.2, 0.8), 2)
        elif status == 'paid':
            amount_paid = total_amount
        else:
            amount_paid = 0.0
        
        # Generate description
        description = random.choice(SERVICE_DESCRIPTIONS + PRODUCT_DESCRIPTIONS)
        
        # Create invoice
        invoice = {
            "invoice_id": generate_invoice_id(),
            "customer_name": random.choice(KENYAN_BUSINESSES),
            "customer_email": f"accounts@{random.choice(KENYAN_BUSINESSES).lower().replace(' ', '').replace('ltd', '')}.co.ke",
            "customer_phone": f"+254{random.randint(700000000, 799999999)}",
            "issue_date": issue_date.isoformat(),
            "due_date": due_date.isoformat(),
            "amount": total_amount,
            "amount_paid": amount_paid,
            "amount_outstanding": round(total_amount - amount_paid, 2),
            "currency": "KES",
            "status": status,
            "description": description,
            "payment_date": generate_payment_date(issue_date, due_date, status),
            "payment_method": random.choice(["M-Pesa", "Bank Transfer", "Cash", "Cheque"]) if status in ['paid', 'partially_paid'] else "",
            "notes": f"Payment terms: Net {(due_date - issue_date).days} days",
            "created_at": issue_date.isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        invoices.append(invoice)
    
    # Sort by issue date
    invoices.sort(key=lambda x: x["issue_date"])
    
    # Save to JSON if output file specified
    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(invoices, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Dataset saved to {output_file}")
    
    # Print statistics
    print(f"✅ Generated {len(invoices)} invoices")
    print(f"   - Paid: {sum(1 for inv in invoices if inv['status'] == 'paid')}")
    print(f"   - Unpaid: {sum(1 for inv in invoices if inv['status'] == 'unpaid')}")
    print(f"   - Overdue: {sum(1 for inv in invoices if inv['status'] == 'overdue')}")
    print(f"   - Partially Paid: {sum(1 for inv in invoices if inv['status'] == 'partially_paid')}")
    
    total_value = sum(inv['amount'] for inv in invoices)
    total_paid = sum(inv['amount_paid'] for inv in invoices)
    total_outstanding = sum(inv['amount_outstanding'] for inv in invoices)
    
    print(f"\n   Total Value: KES {total_value:,.2f}")
    print(f"   Total Paid: KES {total_paid:,.2f}")
    print(f"   Total Outstanding: KES {total_outstanding:,.2f}")
    print(f"   Collection Rate: {(total_paid/total_value*100):.1f}%")
    
    return invoices


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    # Generate dataset
    output_path = os.path.join(os.path.dirname(__file__), "invoices.json")
    invoices = generate_synthetic_invoices(num_invoices=20, output_file=output_path)
    
    print("\n" + "="*60)
    print("Sample Invoices:")
    print("="*60)
    for i, invoice in enumerate(invoices[:3], 1):
        print(f"\n{i}. {invoice['invoice_id']}")
        print(f"   Customer: {invoice['customer_name']}")
        print(f"   Amount: KES {invoice['amount']:,.2f}")
        print(f"   Status: {invoice['status'].upper()}")
        print(f"   Due: {invoice['due_date'][:10]}")
