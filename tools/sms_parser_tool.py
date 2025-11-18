"""
SMS Parser Tool for FinGuard IntelliAgent

This tool parses M-Pesa and bank SMS messages to extract transaction data.
Supports 7 transaction types: M-Pesa (received, sent, paybill, till, withdrawal, airtime)
and bank transactions (deposits, withdrawals, transfers).

Author: Alfred Munga
Date: November 18, 2025
Milestone: 3 - SMS Parser Tool
"""

import re
from typing import Dict, Optional, List, Tuple
from datetime import datetime
from decimal import Decimal


class SMSParserTool:
    """
    Parses M-Pesa and bank transaction SMS messages.
    
    This parser uses regex patterns to extract structured data from unstructured
    SMS text. It handles various M-Pesa transaction formats and bank notifications.
    
    Attributes:
        transaction_types: List of supported transaction types
        patterns: Compiled regex patterns for each transaction type
    """
    
    # Transaction type constants
    MPESA_RECEIVED = "received"
    MPESA_SENT = "sent"
    MPESA_PAYBILL = "paybill"
    MPESA_TILL = "till"
    MPESA_WITHDRAWAL = "withdrawal"
    MPESA_AIRTIME = "airtime"
    BANK_DEPOSIT = "bank_deposit"
    BANK_WITHDRAWAL = "bank_withdrawal"
    BANK_TRANSFER = "bank_transfer"
    
    def __init__(self):
        """Initialize the SMS parser with regex patterns."""
        self.transaction_types = [
            self.MPESA_RECEIVED,
            self.MPESA_SENT,
            self.MPESA_PAYBILL,
            self.MPESA_TILL,
            self.MPESA_WITHDRAWAL,
            self.MPESA_AIRTIME,
            self.BANK_DEPOSIT,
            self.BANK_WITHDRAWAL,
            self.BANK_TRANSFER,
        ]
        
        # Compile regex patterns for better performance
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile all regex patterns for transaction parsing."""
        
        # M-Pesa Received Pattern
        # Example: "RB90VRG Confirmed. You have received Ksh5,991.87 from STEPHEN WAMBUI 254712531512..."
        self.mpesa_received_pattern = re.compile(
            r'(?P<reference>[A-Z0-9]+)\s+Confirmed\.\s+You have received\s+'
            r'Ksh(?P<amount>[\d,]+\.?\d*)\s+from\s+(?P<sender>[A-Z\s\']+?)\s+'
            r'(?P<phone>254\d{9})\s+on\s+(?P<date>\d{2}/\d{2}/\d{4})\s+at\s+'
            r'(?P<time>\d{2}:\d{2}\s+(?:AM|PM)).*?'
            r'New M-PESA balance is Ksh(?P<balance>-?[\d,]+\.?\d*)',
            re.IGNORECASE | re.DOTALL
        )
        
        # M-Pesa Sent Pattern
        # Example: "SG45KLM Confirmed. Ksh1,234.56 sent to JOHN DOE 254700123456..."
        self.mpesa_sent_pattern = re.compile(
            r'(?P<reference>[A-Z0-9]+)\s+Confirmed\.\s+Ksh(?P<amount>[\d,]+\.?\d*)\s+'
            r'sent to\s+(?P<recipient>[A-Z\s]+?)\s+(?P<phone>254\d{9})\s+on\s+'
            r'(?P<date>\d{2}/\d{2}/\d{4})\s+at\s+(?P<time>\d{2}:\d{2}\s+(?:AM|PM)).*?'
            r'New M-PESA balance is Ksh(?P<balance>-?[\d,]+\.?\d*).*?'
            r'Transaction cost[,\s]+Ksh(?P<cost>[\d,]+\.?\d*)',
            re.IGNORECASE | re.DOTALL
        )
        
        # M-Pesa Paybill Pattern
        # Example: "RF55KXW Confirmed. You have paid Ksh446.84 to RUBIS ENERGY for account 560697..."
        self.mpesa_paybill_pattern = re.compile(
            r'(?P<reference>[A-Z0-9]+)\s+Confirmed\.\s+You have paid\s+'
            r'Ksh(?P<amount>[\d,]+\.?\d*)\s+to\s+(?P<merchant>[A-Z\s&\-]+?)\s+'
            r'for account\s+(?P<account>\d+)\s+on\s+(?P<date>\d{2}/\d{2}/\d{4})\s+at\s+'
            r'(?P<time>\d{2}:\d{2}\s+(?:AM|PM)).*?'
            r'New balance is Ksh(?P<balance>-?[\d,]+\.?\d*).*?'
            r'Transaction cost[,\s]+Ksh(?P<cost>[\d,]+\.?\d*)',
            re.IGNORECASE | re.DOTALL
        )
        
        # M-Pesa Till Pattern
        # Example: "TG29IVS Confirmed. Ksh2,735.54 paid to SHELL PETROL STATION Till Number 060835..."
        self.mpesa_till_pattern = re.compile(
            r'(?P<reference>[A-Z0-9]+)\s+Confirmed\.\s+Ksh(?P<amount>[\d,]+\.?\d*)\s+'
            r'paid to\s+(?P<merchant>[A-Z\s&\-]+?)\s+Till Number\s+(?P<till>\d+)\s+on\s+'
            r'(?P<date>\d{2}/\d{2}/\d{4})\s+at\s+(?P<time>\d{2}:\d{2}\s+(?:AM|PM)).*?'
            r'New balance is Ksh(?P<balance>-?[\d,]+\.?\d*).*?'
            r'Transaction cost[,\s]+Ksh(?P<cost>[\d,]+\.?\d*)',
            re.IGNORECASE | re.DOTALL
        )
        
        # M-Pesa Withdrawal Pattern
        # Example: "HJ71DZN Confirmed. You have withdrawn Ksh1,430.21 from M-PESA Agent SARAH MUGO 254712216091..."
        self.mpesa_withdrawal_pattern = re.compile(
            r'(?P<reference>[A-Z0-9]+)\s+Confirmed\.\s+You have withdrawn\s+'
            r'Ksh(?P<amount>[\d,]+\.?\d*)\s+from\s+(?:M-PESA\s+)?Agent\s+(?P<agent>[A-Z\s]+?)\s+'
            r'(?P<agent_number>254\d{9})\s+on\s+(?P<date>\d{2}/\d{2}/\d{4})\s+at\s+'
            r'(?P<time>\d{2}:\d{2}\s+(?:AM|PM)).*?'
            r'New\s+(?:M-PESA\s+)?balance is Ksh(?P<balance>-?[\d,]+\.?\d*).*?'
            r'Tr',
            re.IGNORECASE | re.DOTALL
        )
        
        # M-Pesa Airtime Pattern
        # Example: "KL21MUM Confirmed. You bought Ksh200.00 airtime for 254756226688..."
        self.mpesa_airtime_pattern = re.compile(
            r'(?P<reference>[A-Z0-9]+)\s+Confirmed\.\s+You bought\s+'
            r'Ksh(?P<amount>[\d,]+\.?\d*)\s+airtime\s+for\s+'
            r'(?P<phone>254\d{9})\s+on\s+(?P<date>\d{2}/\d{2}/\d{4})\s+at\s+'
            r'(?P<time>\d{2}:\d{2}\s+(?:AM|PM)).*?'
            r'New balance is Ksh(?P<balance>-?[\d,]+\.?\d*)',
            re.IGNORECASE | re.DOTALL
        )
        
        # Bank Transaction Patterns
        # Supports multiple Kenyan banks: KCB, Equity, Co-operative, etc.
        
        # Bank Deposit Pattern
        # Example: "KCB Bank: Deposit of KES 10,000.00 received. Acc XXXX1234 Balance: KES 45,678.90..."
        self.bank_deposit_pattern = re.compile(
            r'(?P<bank>(?:KCB|Equity|Co-operative|Barclays|Standard Chartered|NCBA|I&M|DTB|Family|Stanbic)\s+Bank):\s+'
            r'Deposit of KES\s+(?P<amount>[\d,]+\.?\d*)\s+received.*?'
            r'Acc\s+(?P<account>XXXX\d+)\s+Balance:\s+KES\s+(?P<balance>-?[\d,]+\.?\d*).*?'
            r'Ref:\s+(?P<reference>\d+)\s+on\s+(?P<date>\d{2}-[A-Za-z]{3}-\d{4})',
            re.IGNORECASE | re.DOTALL
        )
        
        # Bank Withdrawal Pattern
        # Example: "Equity Bank: Withdrawal of KES 5,000.00 successful. Acc XXXX5678 Balance: KES 12,345.67..."
        self.bank_withdrawal_pattern = re.compile(
            r'(?P<bank>(?:KCB|Equity|Co-operative|Barclays|Standard Chartered|NCBA|I&M|DTB|Family|Stanbic)\s+Bank):\s+'
            r'Withdrawal of KES\s+(?P<amount>[\d,]+\.?\d*)\s+successful.*?'
            r'Acc\s+(?P<account>XXXX\d+)\s+Balance:\s+KES\s+(?P<balance>-?[\d,]+\.?\d*).*?'
            r'Ref:\s+(?P<reference>\d+)\s+on\s+(?P<date>\d{2}-[A-Za-z]{3}-\d{4})',
            re.IGNORECASE | re.DOTALL
        )
        
        # Bank Debit Pattern (Alternative withdrawal format)
        # Example: "Co-operative Bank: Acc XXXX5678 debited KES 14,068.71 on 11-Nov-2025. Balance: KES -24,731.09..."
        self.bank_debit_pattern = re.compile(
            r'(?P<bank>(?:KCB|Equity|Co-operative|Barclays|Standard Chartered|NCBA|I&M|DTB|Family|Stanbic)\s+Bank):\s+'
            r'Acc\s+(?P<account>XXXX\d+)\s+debited\s+KES\s+(?P<amount>[\d,]+\.?\d*)\s+'
            r'on\s+(?P<date>\d{2}-[A-Za-z]{3}-\d{4}).*?'
            r'Balance:\s+KES\s+(?P<balance>-?[\d,]+\.?\d*).*?'
            r'Ref:\s+(?P<reference>\d+)',
            re.IGNORECASE | re.DOTALL
        )
        
        # Bank Transfer Pattern
        # Example: "Co-operative Bank: Transfer of KES 2,730.21 to SAMUEL MWANGI successful..."
        self.bank_transfer_pattern = re.compile(
            r'(?P<bank>(?:KCB|Equity|Co-operative|Barclays|Standard Chartered|NCBA|I&M|DTB|Family|Stanbic)\s+Bank):\s+'
            r'Transfer of KES\s+(?P<amount>[\d,]+\.?\d*)\s+to\s+(?P<recipient>[A-Z\s]+?)\s+successful.*?'
            r'Acc\s+(?P<account>XXXX\d+)\s+Balance:\s+KES\s+(?P<balance>-?[\d,]+\.?\d*).*?'
            r'Ref:\s+(?P<reference>\d+)\s+on\s+(?P<date>\d{2}-[A-Za-z]{3}-\d{4})',
            re.IGNORECASE | re.DOTALL
        )
    
    def parse_sms(self, sms_text: str) -> Optional[Dict]:
        """
        Parse an SMS message and extract transaction details.
        
        This is the main entry point for SMS parsing. It tries all patterns
        and returns the first successful match.
        
        Args:
            sms_text: The SMS message text to parse
            
        Returns:
            Dictionary containing parsed transaction data with the following fields:
            - transaction_type: Type of transaction (received, sent, paybill, etc.)
            - amount: Transaction amount as Decimal
            - reference: Transaction reference code
            - date: Transaction date as datetime object
            - balance: New balance after transaction
            - Additional fields depending on transaction type
            
            Returns None if parsing fails for all patterns.
            
        Example:
            >>> parser = SMSParserTool()
            >>> sms = "RB90VRG Confirmed. You have received Ksh5,991.87..."
            >>> result = parser.parse_sms(sms)
            >>> print(result['transaction_type'])
            'received'
        """
        if not sms_text or not isinstance(sms_text, str):
            return None
        
        # Clean the SMS text
        sms_text = sms_text.strip()
        
        # Try each parser in order of likelihood
        parsers = [
            (self.MPESA_RECEIVED, self._parse_mpesa_received),
            (self.MPESA_SENT, self._parse_mpesa_sent),
            (self.MPESA_PAYBILL, self._parse_mpesa_paybill),
            (self.MPESA_TILL, self._parse_mpesa_till),
            (self.MPESA_WITHDRAWAL, self._parse_mpesa_withdrawal),
            (self.MPESA_AIRTIME, self._parse_mpesa_airtime),
            (self.BANK_TRANSFER, self._parse_bank_transfer),
            (self.BANK_DEPOSIT, self._parse_bank_deposit),
            (self.BANK_WITHDRAWAL, self._parse_bank_withdrawal),
            (self.BANK_WITHDRAWAL, self._parse_bank_debit),  # Alternative bank withdrawal format
        ]
        
        for transaction_type, parser_func in parsers:
            try:
                result = parser_func(sms_text)
                if result:
                    return result
            except Exception as e:
                # Log error but continue trying other parsers
                continue
        
        # No parser matched
        return None
    
    def parse_bulk(self, sms_list: List[str]) -> List[Dict]:
        """
        Parse multiple SMS messages in bulk.
        
        Args:
            sms_list: List of SMS message texts
            
        Returns:
            List of parsed transaction dictionaries. Failed parses are included
            with an 'error' field instead of transaction data.
            
        Example:
            >>> parser = SMSParserTool()
            >>> messages = ["RB90VRG Confirmed...", "TG29IVS Confirmed..."]
            >>> results = parser.parse_bulk(messages)
            >>> print(f"Parsed {len(results)} messages")
        """
        results = []
        for idx, sms_text in enumerate(sms_list):
            parsed = self.parse_sms(sms_text)
            if parsed:
                parsed['sms_index'] = idx
                results.append(parsed)
            else:
                results.append({
                    'sms_index': idx,
                    'error': 'Failed to parse SMS',
                    'original_text': sms_text[:100]  # First 100 chars
                })
        return results
    
    def _parse_mpesa_received(self, sms_text: str) -> Optional[Dict]:
        """Parse M-Pesa money received SMS."""
        match = self.mpesa_received_pattern.search(sms_text)
        if not match:
            return None
        
        data = match.groupdict()
        return {
            'transaction_type': self.MPESA_RECEIVED,
            'reference': data['reference'],
            'amount': self._parse_amount(data['amount']),
            'sender': data['sender'].strip(),
            'phone': data['phone'],
            'date': self._parse_mpesa_datetime(data['date'], data['time']),
            'balance': self._parse_amount(data['balance']),
            'transaction_cost': Decimal('0.00'),  # Typically 0 for receiving
            'raw_text': sms_text
        }
    
    def _parse_mpesa_sent(self, sms_text: str) -> Optional[Dict]:
        """Parse M-Pesa money sent SMS."""
        match = self.mpesa_sent_pattern.search(sms_text)
        if not match:
            return None
        
        data = match.groupdict()
        return {
            'transaction_type': self.MPESA_SENT,
            'reference': data['reference'],
            'amount': self._parse_amount(data['amount']),
            'recipient': data['recipient'].strip(),
            'phone': data['phone'],
            'date': self._parse_mpesa_datetime(data['date'], data['time']),
            'balance': self._parse_amount(data['balance']),
            'transaction_cost': self._parse_amount(data['cost']),
            'raw_text': sms_text
        }
    
    def _parse_mpesa_paybill(self, sms_text: str) -> Optional[Dict]:
        """Parse M-Pesa paybill SMS."""
        match = self.mpesa_paybill_pattern.search(sms_text)
        if not match:
            return None
        
        data = match.groupdict()
        return {
            'transaction_type': self.MPESA_PAYBILL,
            'reference': data['reference'],
            'amount': self._parse_amount(data['amount']),
            'merchant': data['merchant'].strip(),
            'account_number': data['account'],
            'date': self._parse_mpesa_datetime(data['date'], data['time']),
            'balance': self._parse_amount(data['balance']),
            'transaction_cost': self._parse_amount(data['cost']),
            'raw_text': sms_text
        }
    
    def _parse_mpesa_till(self, sms_text: str) -> Optional[Dict]:
        """Parse M-Pesa till number SMS."""
        match = self.mpesa_till_pattern.search(sms_text)
        if not match:
            return None
        
        data = match.groupdict()
        return {
            'transaction_type': self.MPESA_TILL,
            'reference': data['reference'],
            'amount': self._parse_amount(data['amount']),
            'merchant': data['merchant'].strip(),
            'till_number': data['till'],
            'date': self._parse_mpesa_datetime(data['date'], data['time']),
            'balance': self._parse_amount(data['balance']),
            'transaction_cost': self._parse_amount(data['cost']),
            'raw_text': sms_text
        }
    
    def _parse_mpesa_withdrawal(self, sms_text: str) -> Optional[Dict]:
        """Parse M-Pesa withdrawal SMS."""
        match = self.mpesa_withdrawal_pattern.search(sms_text)
        if not match:
            return None
        
        data = match.groupdict()
        return {
            'transaction_type': self.MPESA_WITHDRAWAL,
            'reference': data['reference'],
            'amount': self._parse_amount(data['amount']),
            'agent_name': data['agent'].strip(),
            'agent_number': data['agent_number'],
            'date': self._parse_mpesa_datetime(data['date'], data['time']),
            'balance': self._parse_amount(data['balance']),
            'transaction_cost': Decimal('0.00'),  # Extract from text if needed
            'raw_text': sms_text
        }
    
    def _parse_mpesa_airtime(self, sms_text: str) -> Optional[Dict]:
        """Parse M-Pesa airtime purchase SMS."""
        match = self.mpesa_airtime_pattern.search(sms_text)
        if not match:
            return None
        
        data = match.groupdict()
        return {
            'transaction_type': self.MPESA_AIRTIME,
            'reference': data['reference'],
            'amount': self._parse_amount(data['amount']),
            'phone': data['phone'],
            'date': self._parse_mpesa_datetime(data['date'], data['time']),
            'balance': self._parse_amount(data['balance']),
            'transaction_cost': Decimal('0.00'),  # Included in amount
            'raw_text': sms_text
        }
    
    def _parse_bank_deposit(self, sms_text: str) -> Optional[Dict]:
        """Parse bank deposit SMS."""
        match = self.bank_deposit_pattern.search(sms_text)
        if not match:
            return None
        
        data = match.groupdict()
        return {
            'transaction_type': self.BANK_DEPOSIT,
            'reference': data['reference'],
            'amount': self._parse_amount(data['amount']),
            'bank': data['bank'].strip(),
            'account': data['account'],
            'date': self._parse_bank_date(data['date']),
            'balance': self._parse_amount(data['balance']),
            'raw_text': sms_text
        }
    
    def _parse_bank_withdrawal(self, sms_text: str) -> Optional[Dict]:
        """Parse bank withdrawal SMS."""
        match = self.bank_withdrawal_pattern.search(sms_text)
        if not match:
            return None
        
        data = match.groupdict()
        return {
            'transaction_type': self.BANK_WITHDRAWAL,
            'reference': data['reference'],
            'amount': self._parse_amount(data['amount']),
            'bank': data['bank'].strip(),
            'account': data['account'],
            'date': self._parse_bank_date(data['date']),
            'balance': self._parse_amount(data['balance']),
            'raw_text': sms_text
        }
    
    def _parse_bank_transfer(self, sms_text: str) -> Optional[Dict]:
        """Parse bank transfer SMS."""
        match = self.bank_transfer_pattern.search(sms_text)
        if not match:
            return None
        
        data = match.groupdict()
        return {
            'transaction_type': self.BANK_TRANSFER,
            'reference': data['reference'],
            'amount': self._parse_amount(data['amount']),
            'bank': data['bank'].strip(),
            'recipient': data['recipient'].strip(),
            'account': data['account'],
            'date': self._parse_bank_date(data['date']),
            'balance': self._parse_amount(data['balance']),
            'raw_text': sms_text
        }
    
    def _parse_bank_debit(self, sms_text: str) -> Optional[Dict]:
        """Parse bank debit SMS (alternative withdrawal format)."""
        match = self.bank_debit_pattern.search(sms_text)
        if not match:
            return None
        
        data = match.groupdict()
        return {
            'transaction_type': self.BANK_WITHDRAWAL,
            'reference': data['reference'],
            'amount': self._parse_amount(data['amount']),
            'bank': data['bank'].strip(),
            'account': data['account'],
            'date': self._parse_bank_date(data['date']),
            'balance': self._parse_amount(data['balance']),
            'raw_text': sms_text
        }
    
    def _parse_amount(self, amount_str: str) -> Decimal:
        """
        Parse amount string to Decimal.
        
        Handles comma separators and negative amounts.
        
        Args:
            amount_str: Amount string like "1,234.56" or "-500.00"
            
        Returns:
            Decimal representation of the amount
        """
        # Remove commas and convert to Decimal
        clean_amount = amount_str.replace(',', '')
        return Decimal(clean_amount)
    
    def _parse_mpesa_datetime(self, date_str: str, time_str: str) -> datetime:
        """
        Parse M-Pesa date and time strings to datetime object.
        
        Args:
            date_str: Date string in format "DD/MM/YYYY"
            time_str: Time string in format "HH:MM AM/PM"
            
        Returns:
            datetime object
        """
        datetime_str = f"{date_str} {time_str}"
        return datetime.strptime(datetime_str, "%d/%m/%Y %I:%M %p")
    
    def _parse_bank_date(self, date_str: str) -> datetime:
        """
        Parse bank date string to datetime object.
        
        Args:
            date_str: Date string in format "DD-Mon-YYYY" (e.g., "01-Sep-2025")
            
        Returns:
            datetime object
        """
        return datetime.strptime(date_str, "%d-%b-%Y")
    
    def get_transaction_summary(self, parsed_data: Dict) -> str:
        """
        Generate a human-readable summary of a parsed transaction.
        
        Args:
            parsed_data: Parsed transaction dictionary
            
        Returns:
            Formatted string summary
            
        Example:
            >>> summary = parser.get_transaction_summary(parsed)
            >>> print(summary)
            'Received KES 5,991.87 from STEPHEN WAMBUI on 26/08/2025'
        """
        if not parsed_data or 'error' in parsed_data:
            return "Failed to parse transaction"
        
        trans_type = parsed_data['transaction_type']
        amount = parsed_data['amount']
        date = parsed_data['date'].strftime('%d/%m/%Y')
        
        if trans_type == self.MPESA_RECEIVED:
            return f"Received KES {amount:,.2f} from {parsed_data['sender']} on {date}"
        elif trans_type == self.MPESA_SENT:
            return f"Sent KES {amount:,.2f} to {parsed_data['recipient']} on {date}"
        elif trans_type == self.MPESA_PAYBILL:
            return f"Paid KES {amount:,.2f} to {parsed_data['merchant']} (Paybill) on {date}"
        elif trans_type == self.MPESA_TILL:
            return f"Paid KES {amount:,.2f} to {parsed_data['merchant']} (Till) on {date}"
        elif trans_type == self.MPESA_WITHDRAWAL:
            return f"Withdrew KES {amount:,.2f} from agent on {date}"
        elif trans_type == self.MPESA_AIRTIME:
            return f"Bought KES {amount:,.2f} airtime on {date}"
        elif trans_type == self.BANK_DEPOSIT:
            return f"Deposited KES {amount:,.2f} at {parsed_data['bank']} on {date}"
        elif trans_type == self.BANK_WITHDRAWAL:
            return f"Withdrew KES {amount:,.2f} from {parsed_data['bank']} on {date}"
        elif trans_type == self.BANK_TRANSFER:
            return f"Transferred KES {amount:,.2f} to {parsed_data['recipient']} via {parsed_data['bank']} on {date}"
        
        return f"Transaction of KES {amount:,.2f} on {date}"
    
    def validate_parsed_data(self, parsed_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate parsed transaction data for completeness and correctness.
        
        Args:
            parsed_data: Parsed transaction dictionary
            
        Returns:
            Tuple of (is_valid, list_of_errors)
            
        Example:
            >>> is_valid, errors = parser.validate_parsed_data(parsed)
            >>> if not is_valid:
            ...     print("Validation errors:", errors)
        """
        if not parsed_data:
            return False, ["No data to validate"]
        
        if 'error' in parsed_data:
            return False, [parsed_data['error']]
        
        errors = []
        
        # Check required fields
        required_fields = ['transaction_type', 'amount', 'reference', 'date', 'balance']
        for field in required_fields:
            if field not in parsed_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate amount is positive
        if 'amount' in parsed_data:
            if parsed_data['amount'] <= 0:
                errors.append(f"Invalid amount: {parsed_data['amount']}")
        
        # Validate date is not in the future
        if 'date' in parsed_data:
            if parsed_data['date'] > datetime.now():
                errors.append(f"Transaction date is in the future: {parsed_data['date']}")
        
        # Validate transaction type
        if 'transaction_type' in parsed_data:
            if parsed_data['transaction_type'] not in self.transaction_types:
                errors.append(f"Invalid transaction type: {parsed_data['transaction_type']}")
        
        return len(errors) == 0, errors
    
    def get_statistics(self, parsed_list: List[Dict]) -> Dict:
        """
        Calculate statistics from a list of parsed transactions.
        
        Args:
            parsed_list: List of parsed transaction dictionaries
            
        Returns:
            Dictionary containing:
            - total_transactions: Total number of transactions
            - successful_parses: Number of successfully parsed transactions
            - failed_parses: Number of failed parses
            - total_amount: Sum of all transaction amounts
            - transaction_type_counts: Count by transaction type
            - date_range: Earliest and latest transaction dates
            
        Example:
            >>> stats = parser.get_statistics(parsed_list)
            >>> print(f"Parsed {stats['successful_parses']} out of {stats['total_transactions']}")
        """
        stats = {
            'total_transactions': len(parsed_list),
            'successful_parses': 0,
            'failed_parses': 0,
            'total_amount': Decimal('0.00'),
            'transaction_type_counts': {},
            'date_range': {'earliest': None, 'latest': None}
        }
        
        for parsed in parsed_list:
            if 'error' in parsed:
                stats['failed_parses'] += 1
                continue
            
            stats['successful_parses'] += 1
            
            # Sum amounts
            if 'amount' in parsed:
                stats['total_amount'] += parsed['amount']
            
            # Count transaction types
            trans_type = parsed.get('transaction_type', 'unknown')
            stats['transaction_type_counts'][trans_type] = \
                stats['transaction_type_counts'].get(trans_type, 0) + 1
            
            # Track date range
            if 'date' in parsed:
                date = parsed['date']
                if stats['date_range']['earliest'] is None or date < stats['date_range']['earliest']:
                    stats['date_range']['earliest'] = date
                if stats['date_range']['latest'] is None or date > stats['date_range']['latest']:
                    stats['date_range']['latest'] = date
        
        return stats


# Example usage and testing
if __name__ == "__main__":
    # Initialize parser
    parser = SMSParserTool()
    
    # Test with sample SMS messages
    test_messages = [
        "RB90VRG Confirmed. You have received Ksh5,991.87 from STEPHEN WAMBUI 254712531512 on 26/08/2025 at 04:23 PM. New M-PESA balance is Ksh-30,000.70. Transaction cost, Ksh0.00.",
        "RF55KXW Confirmed. You have paid Ksh446.84 to RUBIS ENERGY for account 560697 on 24/08/2025 at 10:01 AM. New balance is Ksh-30,447.54. Transaction cost, Ksh0.00.",
        "Co-operative Bank: Transfer of KES 2,730.21 to SAMUEL MWANGI successful. Acc XXXX5678 Balance: KES -13,325.38. Ref: 0354499106 on 01-Sep-2025",
    ]
    
    print("Testing SMS Parser Tool\n" + "=" * 50)
    for i, sms in enumerate(test_messages, 1):
        print(f"\nTest {i}:")
        print(f"SMS: {sms[:80]}...")
        
        result = parser.parse_sms(sms)
        if result:
            print(f"✓ Parsed successfully!")
            print(f"  Type: {result['transaction_type']}")
            print(f"  Amount: KES {result['amount']}")
            print(f"  Reference: {result['reference']}")
            print(f"  Summary: {parser.get_transaction_summary(result)}")
        else:
            print(f"✗ Failed to parse")
