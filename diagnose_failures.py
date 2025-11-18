"""
Diagnose failed SMS parses
"""
import sys
sys.path.insert(0, '/home/munga/Desktop/FinGuardIntelliAgent')

import csv
from tools.sms_parser_tool import SMSParserTool

# Initialize parser
parser = SMSParserTool()

# Load SMS messages
sms_messages = []
with open('/home/munga/Desktop/FinGuardIntelliAgent/data/synthetic/sms.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        sms_messages.append(row)

print(f"Diagnosing failed parses...\n")

# Parse all messages
for i, msg in enumerate(sms_messages):
    result = parser.parse_sms(msg['sms_text'])
    
    if result is None or 'error' in result:
        print(f"\n{'='*70}")
        print(f"FAILED PARSE #{i+1}")
        print(f"Expected Type: {msg['transaction_type']}")
        print(f"SMS Text: {msg['sms_text'][:150]}...")
        print(f"{'='*70}")
