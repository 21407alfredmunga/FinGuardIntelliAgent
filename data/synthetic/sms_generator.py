"""
FinGuard IntelliAgent - SMS Generator
=====================================

This module generates synthetic Kenyan financial SMS messages for testing
and development of the SMS parser tool.

Supports:
- M-Pesa transactions (received, sent, paybill, till, withdrawal, airtime)
- Bank transactions (deposits, transfers, withdrawals)
- Realistic Kenyan names, amounts, and patterns

Author: Alfred Munga
License: MIT
"""

import random
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import os


# ============================================================================
# Configuration and Data
# ============================================================================

# Kenyan common names for realistic data
KENYAN_FIRST_NAMES = [
    "John", "Mary", "Peter", "Jane", "David", "Grace", "James", "Sarah",
    "Daniel", "Lucy", "Michael", "Faith", "Joseph", "Anne", "Samuel", "Rose",
    "Paul", "Elizabeth", "Mark", "Margaret", "Stephen", "Catherine", "Moses",
    "Rebecca", "Patrick", "Joyce", "Francis", "Agnes", "Anthony", "Nancy"
]

KENYAN_LAST_NAMES = [
    "Kamau", "Wanjiru", "Mwangi", "Njeri", "Ochieng", "Akinyi", "Kipchoge",
    "Chebet", "Mugo", "Wambui", "Otieno", "Adhiambo", "Kimani", "Nyambura",
    "Mutua", "Muthoni", "Omondi", "Awuor", "Karanja", "Wairimu", "Kibet",
    "Jepkoech", "Ndung'u", "Wangari", "Onyango", "Akoth", "Korir", "Jemutai"
]

# Business and merchant names
KENYAN_MERCHANTS = [
    "NAIVAS SUPERMARKET", "CARREFOUR KENYA", "TUSKYS", "CHANDARANA",
    "JAVA HOUSE", "ARTCAFFE", "KFC KENYA", "DOMINOS PIZZA",
    "SAFARICOM LTD", "KENYA POWER", "NAIROBI WATER", "KENGEN",
    "SHELL PETROL STATION", "TOTAL ENERGIES", "RUBIS ENERGY",
    "NAKUMATT PHARMACY", "GOODLIFE PHARMACY", "KITENGELA GLASS",
    "UCHUMI SUPERMARKET", "QUICKMART", "CLEANSHELF SUPERMARKET"
]

# Transaction reference patterns
MPESA_PREFIXES = ["RB", "QC", "RF", "TG", "HJ", "KL", "MN", "OP", "PQ", "RS"]

# Phone number patterns (Kenyan format)
def generate_phone_number() -> str:
    """Generate a realistic Kenyan phone number."""
    prefix = random.choice(["254712", "254723", "254734", "254745", "254756"])
    suffix = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    return prefix + suffix


# ============================================================================
# Helper Functions
# ============================================================================

def random_date(start_days_ago: int = 90, end_days_ago: int = 0) -> datetime:
    """
    Generate a random date within a specified range.
    
    Args:
        start_days_ago: Number of days in the past to start from
        end_days_ago: Number of days in the past to end at
        
    Returns:
        Random datetime within the range
    """
    start_date = datetime.now() - timedelta(days=start_days_ago)
    end_date = datetime.now() - timedelta(days=end_days_ago)
    time_between = end_date - start_date
    random_days = random.randint(0, time_between.days)
    random_seconds = random.randint(0, 86400)  # Seconds in a day
    
    return start_date + timedelta(days=random_days, seconds=random_seconds)


def random_amount(min_amount: int = 50, max_amount: int = 50000) -> float:
    """
    Generate a random amount typical for Kenyan SME transactions.
    
    Args:
        min_amount: Minimum amount in KES
        max_amount: Maximum amount in KES
        
    Returns:
        Random amount rounded to 2 decimal places
    """
    # Weight towards common amounts
    amount_ranges = [
        (50, 500, 0.3),      # Small transactions
        (500, 5000, 0.4),    # Medium transactions
        (5000, 20000, 0.2),  # Large transactions
        (20000, 50000, 0.1)  # Very large transactions
    ]
    
    selected_range = random.choices(
        amount_ranges,
        weights=[r[2] for r in amount_ranges]
    )[0]
    
    amount = random.uniform(selected_range[0], selected_range[1])
    return round(amount, 2)


def format_amount(amount: float) -> str:
    """Format amount with comma separators."""
    return f"{amount:,.2f}"


def generate_reference_code(prefix: str = None) -> str:
    """
    Generate M-Pesa style reference code.
    
    Args:
        prefix: Optional prefix (e.g., 'RB', 'QC')
        
    Returns:
        Reference code like 'RB12KLM'
    """
    if prefix is None:
        prefix = random.choice(MPESA_PREFIXES)
    
    digits = ''.join([str(random.randint(0, 9)) for _ in range(2)])
    letters = ''.join([random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(3)])
    
    return f"{prefix}{digits}{letters}"


def random_balance(last_balance: float = None) -> float:
    """
    Generate a random account balance.
    
    Args:
        last_balance: Previous balance to base new balance on
        
    Returns:
        Random balance amount
    """
    if last_balance is None:
        return random.uniform(1000, 100000)
    return last_balance


def get_random_name() -> str:
    """Generate a random Kenyan full name."""
    first = random.choice(KENYAN_FIRST_NAMES)
    last = random.choice(KENYAN_LAST_NAMES)
    return f"{first} {last}".upper()


# ============================================================================
# SMS Generation Functions
# ============================================================================

def generate_mpesa_received_sms(balance: float = None) -> Tuple[str, float, Dict]:
    """
    Generate M-Pesa money received SMS.
    
    Args:
        balance: Current balance (optional)
        
    Returns:
        Tuple of (SMS text, new balance, metadata dict)
    """
    ref_code = generate_reference_code("RB")
    amount = random_amount(100, 20000)
    sender_name = get_random_name()
    sender_phone = generate_phone_number()
    trans_date = random_date()
    
    if balance is None:
        balance = random_balance()
    
    new_balance = balance + amount
    
    sms = (
        f"{ref_code} Confirmed. You have received Ksh{format_amount(amount)} from "
        f"{sender_name} {sender_phone} on {trans_date.strftime('%d/%m/%Y')} at "
        f"{trans_date.strftime('%I:%M %p')}. New M-PESA balance is "
        f"Ksh{format_amount(new_balance)}. Transaction cost, Ksh0.00."
    )
    
    metadata = {
        "transaction_type": "received",
        "amount": amount,
        "sender": sender_name,
        "phone": sender_phone,
        "reference": ref_code,
        "date": trans_date.isoformat(),
        "balance": new_balance
    }
    
    return sms, new_balance, metadata


def generate_mpesa_sent_sms(balance: float = None) -> Tuple[str, float, Dict]:
    """
    Generate M-Pesa money sent SMS.
    
    Args:
        balance: Current balance (optional)
        
    Returns:
        Tuple of (SMS text, new balance, metadata dict)
    """
    ref_code = generate_reference_code("QC")
    amount = random_amount(100, 15000)
    recipient_name = get_random_name()
    recipient_phone = generate_phone_number()
    trans_date = random_date()
    cost = round(amount * 0.01, 2)  # Typical M-Pesa cost ~1%
    
    if balance is None:
        balance = random_balance()
    
    new_balance = balance - amount - cost
    
    sms = (
        f"{ref_code} Confirmed. Ksh{format_amount(amount)} sent to "
        f"{recipient_name} {recipient_phone} on {trans_date.strftime('%d/%m/%Y')} at "
        f"{trans_date.strftime('%I:%M %p')}. New M-PESA balance is "
        f"Ksh{format_amount(new_balance)}. Transaction cost, Ksh{format_amount(cost)}."
    )
    
    metadata = {
        "transaction_type": "sent",
        "amount": amount,
        "recipient": recipient_name,
        "phone": recipient_phone,
        "reference": ref_code,
        "date": trans_date.isoformat(),
        "balance": new_balance,
        "cost": cost
    }
    
    return sms, new_balance, metadata


def generate_mpesa_paybill_sms(balance: float = None) -> Tuple[str, float, Dict]:
    """
    Generate M-Pesa paybill payment SMS.
    
    Args:
        balance: Current balance (optional)
        
    Returns:
        Tuple of (SMS text, new balance, metadata dict)
    """
    ref_code = generate_reference_code("RF")
    amount = random_amount(200, 10000)
    merchant = random.choice(KENYAN_MERCHANTS)
    account_number = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    trans_date = random_date()
    
    if balance is None:
        balance = random_balance()
    
    new_balance = balance - amount
    
    sms = (
        f"{ref_code} Confirmed. You have paid Ksh{format_amount(amount)} to "
        f"{merchant} for account {account_number} on {trans_date.strftime('%d/%m/%Y')} "
        f"at {trans_date.strftime('%I:%M %p')}. New balance is "
        f"Ksh{format_amount(new_balance)}. Transaction cost, Ksh0.00."
    )
    
    metadata = {
        "transaction_type": "paybill",
        "amount": amount,
        "merchant": merchant,
        "account": account_number,
        "reference": ref_code,
        "date": trans_date.isoformat(),
        "balance": new_balance
    }
    
    return sms, new_balance, metadata


def generate_mpesa_till_sms(balance: float = None) -> Tuple[str, float, Dict]:
    """
    Generate M-Pesa till number payment SMS.
    
    Args:
        balance: Current balance (optional)
        
    Returns:
        Tuple of (SMS text, new balance, metadata dict)
    """
    ref_code = generate_reference_code("TG")
    amount = random_amount(50, 5000)
    merchant = random.choice(KENYAN_MERCHANTS)
    till_number = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    trans_date = random_date()
    
    if balance is None:
        balance = random_balance()
    
    new_balance = balance - amount
    
    sms = (
        f"{ref_code} Confirmed. Ksh{format_amount(amount)} paid to "
        f"{merchant} Till Number {till_number} on {trans_date.strftime('%d/%m/%Y')} "
        f"at {trans_date.strftime('%I:%M %p')}. New balance is "
        f"Ksh{format_amount(new_balance)}. Transaction cost, Ksh0.00."
    )
    
    metadata = {
        "transaction_type": "till",
        "amount": amount,
        "merchant": merchant,
        "till_number": till_number,
        "reference": ref_code,
        "date": trans_date.isoformat(),
        "balance": new_balance
    }
    
    return sms, new_balance, metadata


def generate_mpesa_withdrawal_sms(balance: float = None) -> Tuple[str, float, Dict]:
    """
    Generate M-Pesa agent withdrawal SMS.
    
    Args:
        balance: Current balance (optional)
        
    Returns:
        Tuple of (SMS text, new balance, metadata dict)
    """
    ref_code = generate_reference_code("HJ")
    amount = random_amount(500, 10000)
    agent_name = get_random_name()
    agent_phone = generate_phone_number()
    trans_date = random_date()
    cost = round(amount * 0.012, 2)  # Withdrawal cost ~1.2%
    
    if balance is None:
        balance = random_balance()
    
    new_balance = balance - amount - cost
    
    sms = (
        f"{ref_code} Confirmed. You have withdrawn Ksh{format_amount(amount)} from "
        f"M-PESA Agent {agent_name} {agent_phone} on {trans_date.strftime('%d/%m/%Y')} "
        f"at {trans_date.strftime('%I:%M %p')}. New balance is "
        f"Ksh{format_amount(new_balance)}. Transaction cost, Ksh{format_amount(cost)}."
    )
    
    metadata = {
        "transaction_type": "withdrawal",
        "amount": amount,
        "agent": agent_name,
        "phone": agent_phone,
        "reference": ref_code,
        "date": trans_date.isoformat(),
        "balance": new_balance,
        "cost": cost
    }
    
    return sms, new_balance, metadata


def generate_mpesa_airtime_sms(balance: float = None) -> Tuple[str, float, Dict]:
    """
    Generate M-Pesa airtime purchase SMS.
    
    Args:
        balance: Current balance (optional)
        
    Returns:
        Tuple of (SMS text, new balance, metadata dict)
    """
    ref_code = generate_reference_code("KL")
    amount = random.choice([50, 100, 200, 500, 1000])  # Common airtime amounts
    phone = generate_phone_number()
    trans_date = random_date()
    
    if balance is None:
        balance = random_balance()
    
    new_balance = balance - amount
    
    sms = (
        f"{ref_code} Confirmed. You bought Ksh{format_amount(amount)} airtime for "
        f"{phone} on {trans_date.strftime('%d/%m/%Y')} at "
        f"{trans_date.strftime('%I:%M %p')}. New balance is "
        f"Ksh{format_amount(new_balance)}. Transaction cost, Ksh0.00."
    )
    
    metadata = {
        "transaction_type": "airtime",
        "amount": amount,
        "phone": phone,
        "reference": ref_code,
        "date": trans_date.isoformat(),
        "balance": new_balance
    }
    
    return sms, new_balance, metadata


def generate_bank_sms(balance: float = None) -> Tuple[str, float, Dict]:
    """
    Generate bank transaction SMS.
    
    Args:
        balance: Current balance (optional)
        
    Returns:
        Tuple of (SMS text, new balance, metadata dict)
    """
    banks = ["KCB", "Equity Bank", "Co-operative Bank", "NCBA", "Stanbic Bank"]
    bank = random.choice(banks)
    
    trans_types = ["deposit", "withdrawal", "transfer"]
    trans_type = random.choice(trans_types)
    
    amount = random_amount(1000, 50000)
    trans_date = random_date()
    ref_code = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    
    if balance is None:
        balance = random_balance()
    
    if trans_type == "deposit":
        new_balance = balance + amount
        sms = (
            f"{bank}: Acc XXXX5678 credited with KES {format_amount(amount)} on "
            f"{trans_date.strftime('%d-%b-%Y')}. Balance: KES {format_amount(new_balance)}. "
            f"Ref: {ref_code}"
        )
    elif trans_type == "withdrawal":
        new_balance = balance - amount
        sms = (
            f"{bank}: Acc XXXX5678 debited KES {format_amount(amount)} on "
            f"{trans_date.strftime('%d-%b-%Y')}. Balance: KES {format_amount(new_balance)}. "
            f"Ref: {ref_code}"
        )
    else:  # transfer
        recipient = get_random_name()
        new_balance = balance - amount
        sms = (
            f"{bank}: Transfer of KES {format_amount(amount)} to {recipient} successful. "
            f"Acc XXXX5678 Balance: KES {format_amount(new_balance)}. "
            f"Ref: {ref_code} on {trans_date.strftime('%d-%b-%Y')}"
        )
    
    metadata = {
        "transaction_type": f"bank_{trans_type}",
        "amount": amount,
        "bank": bank,
        "reference": ref_code,
        "date": trans_date.isoformat(),
        "balance": new_balance
    }
    
    return sms, new_balance, metadata


# ============================================================================
# Main Generation Function
# ============================================================================

def generate_synthetic_sms_dataset(num_messages: int = 50, output_file: str = None) -> List[Dict]:
    """
    Generate a complete synthetic SMS dataset.
    
    Args:
        num_messages: Number of SMS messages to generate
        output_file: Optional CSV file path to save dataset
        
    Returns:
        List of SMS data dictionaries
    """
    print(f"Generating {num_messages} synthetic SMS messages...")
    
    # Transaction type distribution (realistic for Kenyan SME)
    transaction_generators = [
        (generate_mpesa_received_sms, 0.25),  # 25% received
        (generate_mpesa_sent_sms, 0.20),      # 20% sent
        (generate_mpesa_paybill_sms, 0.20),   # 20% paybill
        (generate_mpesa_till_sms, 0.15),      # 15% till
        (generate_mpesa_withdrawal_sms, 0.10), # 10% withdrawal
        (generate_mpesa_airtime_sms, 0.05),   # 5% airtime
        (generate_bank_sms, 0.05),            # 5% bank
    ]
    
    dataset = []
    current_balance = random_balance()
    
    for i in range(num_messages):
        # Select transaction type based on weights
        generator = random.choices(
            [g[0] for g in transaction_generators],
            weights=[g[1] for g in transaction_generators]
        )[0]
        
        # Generate SMS
        sms_text, new_balance, metadata = generator(current_balance)
        current_balance = new_balance
        
        # Create record
        record = {
            "id": i + 1,
            "sms_text": sms_text,
            "transaction_type": metadata["transaction_type"],
            "amount": metadata["amount"],
            "reference": metadata.get("reference", ""),
            "date": metadata["date"],
            "balance": metadata["balance"],
            "sender_recipient": metadata.get("sender", metadata.get("recipient", metadata.get("merchant", metadata.get("agent", metadata.get("bank", ""))))),
            "phone": metadata.get("phone", ""),
        }
        
        dataset.append(record)
    
    # Sort by date
    dataset.sort(key=lambda x: x["date"])
    
    # Save to CSV if output file specified
    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ["id", "sms_text", "transaction_type", "amount", "reference", 
                         "date", "balance", "sender_recipient", "phone"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(dataset)
        
        print(f"✅ Dataset saved to {output_file}")
    
    print(f"✅ Generated {len(dataset)} SMS messages")
    print(f"   - M-Pesa Received: {sum(1 for d in dataset if d['transaction_type'] == 'received')}")
    print(f"   - M-Pesa Sent: {sum(1 for d in dataset if d['transaction_type'] == 'sent')}")
    print(f"   - Paybill: {sum(1 for d in dataset if d['transaction_type'] == 'paybill')}")
    print(f"   - Till: {sum(1 for d in dataset if d['transaction_type'] == 'till')}")
    print(f"   - Withdrawal: {sum(1 for d in dataset if d['transaction_type'] == 'withdrawal')}")
    print(f"   - Airtime: {sum(1 for d in dataset if d['transaction_type'] == 'airtime')}")
    print(f"   - Bank: {sum(1 for d in dataset if 'bank_' in d['transaction_type'])}")
    
    return dataset


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    # Generate dataset
    output_path = os.path.join(os.path.dirname(__file__), "sms.csv")
    dataset = generate_synthetic_sms_dataset(num_messages=50, output_file=output_path)
    
    print("\n" + "="*60)
    print("Sample SMS Messages:")
    print("="*60)
    for i, record in enumerate(dataset[:3], 1):
        print(f"\n{i}. {record['transaction_type'].upper()}")
        print(f"   {record['sms_text'][:100]}...")
