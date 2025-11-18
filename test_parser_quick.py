"""
Quick test of SMS Parser Tool with synthetic dataset
"""
import sys
sys.path.insert(0, '/home/munga/Desktop/FinGuardIntelliAgent')

import csv
from tools.sms_parser_tool import SMSParserTool
from decimal import Decimal

# Initialize parser
parser = SMSParserTool()

# Load SMS messages
sms_messages = []
with open('/home/munga/Desktop/FinGuardIntelliAgent/data/synthetic/sms.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        sms_messages.append(row)

print(f"Loaded {len(sms_messages)} SMS messages\n")
print("="*70)
print("TESTING SMS PARSER")
print("="*70)

# Parse all messages
results = parser.parse_bulk([msg['sms_text'] for msg in sms_messages])

# Calculate statistics
stats = parser.get_statistics(results)

print(f"\n📊 PARSING RESULTS:\n")
print(f"Total Messages: {stats['total_transactions']}")
print(f"Successfully Parsed: {stats['successful_parses']} ({stats['successful_parses']/stats['total_transactions']*100:.1f}%)")
print(f"Failed to Parse: {stats['failed_parses']} ({stats['failed_parses']/stats['total_transactions']*100:.1f}%)")
print(f"\nTotal Transaction Amount: KES {stats['total_amount']:,.2f}")

print(f"\n📈 TRANSACTION TYPE BREAKDOWN:\n")
for trans_type, count in sorted(stats['transaction_type_counts'].items()):
    percentage = (count / stats['successful_parses'] * 100)
    print(f"  {trans_type:20s}: {count:3d} ({percentage:5.1f}%)")

# Validate accuracy
print(f"\n🔍 ACCURACY VALIDATION:\n")
amount_matches = 0
reference_matches = 0
type_matches = 0

for i, (result, original) in enumerate(zip(results, sms_messages)):
    if 'error' in result:
        continue
    
    # Check amount
    parsed_amount = float(result['amount'])
    original_amount = float(original['amount'])
    if abs(parsed_amount - original_amount) < 0.01:
        amount_matches += 1
    
    # Check reference
    if result['reference'] == original['reference']:
        reference_matches += 1
    
    # Check transaction type
    if result['transaction_type'] == original['transaction_type']:
        type_matches += 1

total_valid = stats['successful_parses']
print(f"Amount Extraction: {amount_matches}/{total_valid} ({amount_matches/total_valid*100:.1f}%)")
print(f"Reference Extraction: {reference_matches}/{total_valid} ({reference_matches/total_valid*100:.1f}%)")
print(f"Transaction Type: {type_matches}/{total_valid} ({type_matches/total_valid*100:.1f}%)")

# Show some examples
print(f"\n📝 SAMPLE PARSED TRANSACTIONS:\n")
for i in [0, 1, 2]:
    result = results[i]
    if 'error' not in result:
        print(f"\n{i+1}. {parser.get_transaction_summary(result)}")
        print(f"   Reference: {result['reference']}, Amount: KES {result['amount']:,.2f}")

print("\n" + "="*70)
print("✅ SMS PARSER TESTING COMPLETE!")
print("="*70)
