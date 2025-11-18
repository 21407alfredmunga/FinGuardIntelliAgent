"""
FinGuard IntelliAgent - Receipts Generator
==========================================

This module generates synthetic receipt data for testing expense
tracking and categorization features.

Generates realistic Kenyan SME receipts with:
- Receipt IDs
- Vendor information
- Amounts
- Categories
- Payment methods
- Dates

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

# Expense categories common for Kenyan SMEs
EXPENSE_CATEGORIES = {
    "Utilities": [
        "KENYA POWER - KPLC",
        "NAIROBI WATER",
        "SAFARICOM - Internet",
        "AIRTEL - Data Bundle",
        "ZUKU FIBER"
    ],
    "Office Supplies": [
        "NAKUMATT STATIONERS",
        "TEXT BOOK CENTRE",
        "PRESTIGE PLAZA",
        "OFFICE DEPOT KENYA",
        "CLASSIC STATIONERY"
    ],
    "Transport & Fuel": [
        "SHELL PETROL STATION",
        "TOTAL ENERGIES",
        "RUBIS ENERGY",
        "UBER KENYA",
        "BOLT RIDES"
    ],
    "Marketing & Advertising": [
        "GOOGLE ADS",
        "FACEBOOK ADS",
        "NATION MEDIA GROUP",
        "STANDARD GROUP",
        "ROYAL MEDIA SERVICES"
    ],
    "Meals & Entertainment": [
        "JAVA HOUSE",
        "ARTCAFFE",
        "KFC KENYA",
        "DOMINOS PIZZA",
        "ABOUT THYME CAFE"
    ],
    "Equipment & Maintenance": [
        "COMPUTER PLANET",
        "HOTPOINT APPLIANCES",
        "CHANDARANA",
        "UCHUMI TECHNICAL",
        "GAME STORES"
    ],
    "Professional Services": [
        "PWC KENYA",
        "DELOITTE KENYA",
        "KRA - Tax Payment",
        "NHIF PAYMENT",
        "NSSF CONTRIBUTION"
    ],
    "Rent & Facilities": [
        "WESTLANDS SQUARE",
        "KILIMANI BUSINESS CENTER",
        "UPPERHILL TOWERS",
        "PARKLANDS OFFICE COMPLEX",
        "CBD COMMERCIAL BUILDING"
    ],
    "Telecommunications": [
        "SAFARICOM LTD",
        "AIRTEL KENYA",
        "TELKOM KENYA",
        "JAMII TELECOM",
        "LIQUID TELECOM"
    ],
    "Licenses & Permits": [
        "COUNTY GOVERNMENT - Business Permit",
        "NEMA - Environmental License",
        "PUBLIC HEALTH - Inspection",
        "FIRE DEPARTMENT - Safety Certificate",
        "WEIGHTS & MEASURES - Verification"
    ]
}

# Payment methods common in Kenya
PAYMENT_METHODS = [
    "M-Pesa",
    "Bank Transfer",
    "Cash",
    "Debit Card",
    "Credit Card",
    "Airtel Money",
    "Cheque"
]


# ============================================================================
# Helper Functions
# ============================================================================

def generate_receipt_id() -> str:
    """
    Generate a realistic receipt ID.
    
    Returns:
        Receipt ID in format RCP-YYYYMMDD-NNNN
    """
    date_str = datetime.now().strftime("%Y%m%d")
    number = random.randint(1000, 9999)
    return f"RCP-{date_str}-{number}"


def random_receipt_date(days_ago_range: tuple = (1, 90)) -> datetime:
    """
    Generate a random receipt date.
    
    Args:
        days_ago_range: Range of days in the past (min, max)
        
    Returns:
        Receipt date
    """
    days_ago = random.randint(days_ago_range[0], days_ago_range[1])
    return datetime.now() - timedelta(days=days_ago)


def generate_receipt_amount(category: str) -> float:
    """
    Generate realistic receipt amount based on category.
    
    Args:
        category: Expense category
        
    Returns:
        Receipt amount in KES
    """
    # Different price ranges for different categories
    category_ranges = {
        "Utilities": (1500, 15000),
        "Office Supplies": (500, 5000),
        "Transport & Fuel": (500, 8000),
        "Marketing & Advertising": (5000, 50000),
        "Meals & Entertainment": (500, 5000),
        "Equipment & Maintenance": (2000, 50000),
        "Professional Services": (10000, 100000),
        "Rent & Facilities": (20000, 150000),
        "Telecommunications": (1000, 10000),
        "Licenses & Permits": (2000, 20000)
    }
    
    amount_range = category_ranges.get(category, (1000, 10000))
    amount = random.uniform(amount_range[0], amount_range[1])
    return round(amount, 2)


def generate_description(category: str, vendor: str) -> str:
    """
    Generate receipt description based on category and vendor.
    
    Args:
        category: Expense category
        vendor: Vendor name
        
    Returns:
        Receipt description
    """
    descriptions = {
        "Utilities": [
            f"Electricity bill - {random.choice(['October', 'November', 'December'])} 2025",
            f"Water bill - {random.choice(['October', 'November', 'December'])} 2025",
            f"Internet service - Monthly subscription",
            f"Data bundle - {random.choice(['10GB', '20GB', '50GB'])} package"
        ],
        "Office Supplies": [
            f"Printer paper - {random.randint(5, 20)} reams",
            f"Stationery supplies - Bulk order",
            f"Office furniture - {random.choice(['Desk', 'Chair', 'Cabinet'])}",
            f"Printer toner cartridges - {random.randint(2, 5)} units"
        ],
        "Transport & Fuel": [
            f"Petrol - {random.randint(20, 60)} liters",
            f"Diesel - {random.randint(30, 80)} liters",
            f"Ride to {random.choice(['Westlands', 'CBD', 'Airport', 'Karen'])}",
            f"Vehicle maintenance and service"
        ],
        "Marketing & Advertising": [
            f"Digital advertising campaign - {random.choice(['November', 'December'])} 2025",
            f"Social media promotion - {random.randint(7, 30)} days",
            f"Newspaper advertisement - {random.choice(['Daily Nation', 'Standard'])}",
            f"Radio spot - {random.choice(['Capital FM', 'Classic 105'])} - 1 week"
        ],
        "Meals & Entertainment": [
            f"Client lunch meeting",
            f"Team lunch - {random.randint(5, 15)} people",
            f"Coffee and snacks - Office meeting",
            f"Dinner with client - {random.choice(['Westlands', 'Karen', 'CBD'])}"
        ],
        "Equipment & Maintenance": [
            f"Office equipment - {random.choice(['Printer', 'Scanner', 'Projector'])}",
            f"Computer repairs and maintenance",
            f"Air conditioning service",
            f"Generator maintenance and fuel"
        ],
        "Professional Services": [
            f"Accounting services - {random.choice(['Monthly', 'Quarterly'])} filing",
            f"Legal consultation - {random.choice(['Contract review', 'Compliance'])}",
            f"Tax payment - {random.choice(['VAT', 'PAYE', 'Corporate Tax'])}",
            f"Audit services - Annual compliance"
        ],
        "Rent & Facilities": [
            f"Office rent - {random.choice(['November', 'December'])} 2025",
            f"Parking fee - Monthly",
            f"Security deposit",
            f"Service charge - Quarterly"
        ],
        "Telecommunications": [
            f"Mobile airtime - Bulk purchase",
            f"Internet package - {random.choice(['Monthly', 'Quarterly'])}",
            f"Phone system maintenance",
            f"Conference call service"
        ],
        "Licenses & Permits": [
            f"Business license renewal - {random.choice(['2025', '2026'])}",
            f"Fire safety inspection and certification",
            f"Health inspection and permit",
            f"Annual operating license"
        ]
    }
    
    category_descriptions = descriptions.get(category, [f"Purchase from {vendor}"])
    return random.choice(category_descriptions)


# ============================================================================
# Main Generation Function
# ============================================================================

def generate_synthetic_receipts(num_receipts: int = 15, output_file: str = None) -> List[Dict]:
    """
    Generate synthetic receipts dataset.
    
    Args:
        num_receipts: Number of receipts to generate
        output_file: Optional JSON file path to save dataset
        
    Returns:
        List of receipt dictionaries
    """
    print(f"Generating {num_receipts} synthetic receipts...")
    
    receipts = []
    
    for i in range(num_receipts):
        # Select category and vendor
        category = random.choice(list(EXPENSE_CATEGORIES.keys()))
        vendor = random.choice(EXPENSE_CATEGORIES[category])
        
        # Generate receipt date
        receipt_date = random_receipt_date()
        
        # Generate amount
        amount = generate_receipt_amount(category)
        
        # Generate tax (16% VAT is common in Kenya)
        include_tax = random.choice([True, False])
        if include_tax:
            tax_amount = round(amount * 0.16, 2)
            total_amount = round(amount + tax_amount, 2)
        else:
            tax_amount = 0.0
            total_amount = amount
        
        # Payment method
        payment_method = random.choice(PAYMENT_METHODS)
        
        # Create receipt
        receipt = {
            "receipt_id": generate_receipt_id(),
            "vendor": vendor,
            "category": category,
            "description": generate_description(category, vendor),
            "date": receipt_date.isoformat(),
            "subtotal": amount,
            "tax": tax_amount,
            "total": total_amount,
            "currency": "KES",
            "payment_method": payment_method,
            "payment_reference": f"TXN{random.randint(100000, 999999)}" if payment_method in ["M-Pesa", "Bank Transfer"] else "",
            "receipt_number": f"{random.randint(10000, 99999)}",
            "notes": f"Business expense - {category}",
            "is_reimbursable": random.choice([True, False]),
            "created_at": receipt_date.isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        receipts.append(receipt)
    
    # Sort by date
    receipts.sort(key=lambda x: x["date"])
    
    # Save to JSON if output file specified
    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(receipts, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Dataset saved to {output_file}")
    
    # Print statistics
    print(f"✅ Generated {len(receipts)} receipts")
    
    # Category breakdown
    print("\n   Category Breakdown:")
    for category in EXPENSE_CATEGORIES.keys():
        count = sum(1 for r in receipts if r['category'] == category)
        if count > 0:
            print(f"   - {category}: {count}")
    
    # Financial summary
    total_spent = sum(r['total'] for r in receipts)
    total_tax = sum(r['tax'] for r in receipts)
    reimbursable = sum(r['total'] for r in receipts if r['is_reimbursable'])
    
    print(f"\n   Total Spent: KES {total_spent:,.2f}")
    print(f"   Total Tax (VAT): KES {total_tax:,.2f}")
    print(f"   Reimbursable: KES {reimbursable:,.2f}")
    
    # Payment method breakdown
    print("\n   Payment Methods:")
    for method in set(r['payment_method'] for r in receipts):
        count = sum(1 for r in receipts if r['payment_method'] == method)
        print(f"   - {method}: {count}")
    
    return receipts


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    # Generate dataset
    output_path = os.path.join(os.path.dirname(__file__), "receipts.json")
    receipts = generate_synthetic_receipts(num_receipts=15, output_file=output_path)
    
    print("\n" + "="*60)
    print("Sample Receipts:")
    print("="*60)
    for i, receipt in enumerate(receipts[:3], 1):
        print(f"\n{i}. {receipt['receipt_id']}")
        print(f"   Vendor: {receipt['vendor']}")
        print(f"   Category: {receipt['category']}")
        print(f"   Amount: KES {receipt['total']:,.2f}")
        print(f"   Payment: {receipt['payment_method']}")
        print(f"   Date: {receipt['date'][:10]}")
