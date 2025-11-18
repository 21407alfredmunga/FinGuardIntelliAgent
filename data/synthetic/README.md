# Synthetic Data - FinGuard IntelliAgent

**Milestone 2: Data Generation and Validation**

This directory contains synthetically generated financial datasets for testing and development of the FinGuard IntelliAgent ADK capstone project.

## 📁 Datasets Overview

### 1. SMS Messages (`sms.csv`)

**Purpose:** Synthetic Kenyan mobile money and bank transaction SMS messages for testing the SMS Parser Tool.

**Records:** 50 messages

**Fields:**
- `id`: Unique message identifier
- `sms_text`: Full SMS message text
- `transaction_type`: Type of transaction (received, sent, paybill, till, withdrawal, airtime, bank_*)
- `amount`: Transaction amount in KES
- `reference`: Transaction reference code (e.g., RB12KLM)
- `date`: Transaction timestamp (ISO format)
- `balance`: Account balance after transaction
- `sender_recipient`: Name of sender/recipient/merchant
- `phone`: Phone number involved in transaction

**Transaction Types:**
- **M-Pesa Received** (25%): Money received from another user
- **M-Pesa Sent** (20%): Money sent to another user
- **Paybill** (20%): Payment to business paybill
- **Till** (15%): Payment to merchant till number
- **Withdrawal** (10%): Cash withdrawal from agent
- **Airtime** (5%): Airtime purchase
- **Bank Transactions** (5%): Bank deposits/withdrawals/transfers

**Use Cases:**
- Testing SMS Parser Tool accuracy
- Training pattern recognition algorithms
- Validating transaction extraction logic
- Edge case testing (various formats, amounts, dates)

---

### 2. Invoices (`invoices.json`)

**Purpose:** Synthetic business invoices for testing the Invoice Collection Tool.

**Records:** 20 invoices

**Fields:**
- `invoice_id`: Unique invoice identifier (INV-YYYY-NNNN)
- `customer_name`: Customer/client business name
- `customer_email`: Customer email address
- `customer_phone`: Customer phone number
- `issue_date`: Invoice issue date (ISO format)
- `due_date`: Payment due date (ISO format)
- `amount`: Total invoice amount in KES
- `amount_paid`: Amount already paid
- `amount_outstanding`: Remaining balance
- `currency`: Currency code (KES)
- `status`: Invoice status (paid, unpaid, overdue, partially_paid)
- `description`: Invoice description (services/products)
- `payment_date`: Date payment was received (if paid)
- `payment_method`: How payment was made (M-Pesa, Bank Transfer, etc.)
- `notes`: Additional invoice notes
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp

**Status Distribution:**
- **Paid** (~50%): Fully paid invoices
- **Unpaid** (~20%): Not yet paid, not overdue
- **Overdue** (~20%): Past due date, unpaid
- **Partially Paid** (~10%): Partial payment received

**Realistic Features:**
- Payment terms: Net 7-90 days
- Kenyan business names
- Typical SME service/product descriptions
- Realistic amounts: KES 5,000 - 500,000

**Use Cases:**
- Testing invoice tracking functionality
- Automated follow-up message generation
- Collection analytics and reporting
- Payment status monitoring
- Customer payment behavior analysis

---

### 3. Receipts (`receipts.json`)

**Purpose:** Synthetic business expense receipts for testing expense tracking and categorization.

**Records:** 15 receipts

**Fields:**
- `receipt_id`: Unique receipt identifier (RCP-YYYYMMDD-NNNN)
- `vendor`: Vendor/merchant name
- `category`: Expense category
- `description`: Item/service description
- `date`: Receipt date (ISO format)
- `subtotal`: Amount before tax
- `tax`: VAT amount (16% where applicable)
- `total`: Total amount including tax
- `currency`: Currency code (KES)
- `payment_method`: How payment was made
- `payment_reference`: Transaction reference (for digital payments)
- `receipt_number`: Vendor's receipt number
- `notes`: Additional notes
- `is_reimbursable`: Whether expense is reimbursable
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp

**Expense Categories:**
- **Utilities**: Electricity, water, internet (KPLC, Nairobi Water, Safaricom)
- **Office Supplies**: Stationery, furniture (Nakumatt, Text Book Centre)
- **Transport & Fuel**: Petrol, rides (Shell, Total, Uber)
- **Marketing & Advertising**: Ads, promotions (Google Ads, Nation Media)
- **Meals & Entertainment**: Client meetings, team meals (Java House, KFC)
- **Equipment & Maintenance**: Office equipment, repairs
- **Professional Services**: Accounting, legal, taxes (PWC, KRA)
- **Rent & Facilities**: Office rent, parking
- **Telecommunications**: Airtime, internet packages
- **Licenses & Permits**: Business licenses, certifications

**Realistic Features:**
- 16% VAT on applicable items
- Kenyan vendor names
- Typical SME expense amounts
- Common payment methods (M-Pesa, Bank Transfer, Cash)

**Use Cases:**
- Expense categorization testing
- Spending pattern analysis
- Budget tracking
- Tax deduction identification
- Reimbursement processing

---

## 🎯 Why Synthetic Data?

### 1. Privacy & Compliance
- **No Real Personal Data**: Protects actual customer information
- **GDPR Compliant**: No privacy violations
- **Safe for Development**: Can be shared publicly without concerns
- **Demo-Friendly**: Safe to showcase in presentations

### 2. Controlled Testing
- **Predictable Patterns**: Known ground truth for validation
- **Edge Cases**: Can create specific scenarios for testing
- **Reproducible**: Same data for consistent testing
- **Comprehensive Coverage**: All transaction types included

### 3. Kenyan Context
- **Realistic Formats**: Actual M-Pesa SMS patterns
- **Local Vendors**: Real Kenyan business names
- **Appropriate Amounts**: Typical SME transaction values
- **Cultural Accuracy**: Kenyan names, locations, practices

### 4. Development Efficiency
- **Immediate Availability**: No waiting for real data
- **Complete Control**: Generate any scenario needed
- **No Dependencies**: Works offline, no API requirements
- **Scalable**: Easy to generate more data as needed

---

## 🛠️ Data Generation Scripts

### SMS Generator (`sms_generator.py`)

Generates realistic Kenyan financial SMS messages.

**Features:**
- M-Pesa transaction formats (received, sent, paybill, till, withdrawal, airtime)
- Bank transaction formats (deposits, withdrawals, transfers)
- Realistic Kenyan names (first + last names)
- Kenyan merchant names
- Proper phone number formats (254...)
- Transaction reference codes
- Running balance calculations

**Usage:**
```bash
python sms_generator.py
```

**Output:** `sms.csv` (50 messages)

---

### Invoices Generator (`invoices_generator.py`)

Generates synthetic business invoices.

**Features:**
- Realistic invoice IDs (INV-YYYY-NNNN)
- Kenyan business names
- Service/product descriptions
- Payment status logic (paid/unpaid/overdue/partial)
- Realistic payment timelines
- Collection rate calculations

**Usage:**
```bash
python invoices_generator.py
```

**Output:** `invoices.json` (20 invoices)

---

### Receipts Generator (`receipts_generator.py`)

Generates synthetic expense receipts.

**Features:**
- Kenyan vendor names
- 10 expense categories
- 16% VAT calculations
- Multiple payment methods
- Receipt ID generation
- Reimbursability flags

**Usage:**
```bash
python receipts_generator.py
```

**Output:** `receipts.json` (15 receipts)

---

## 📊 Data Validation

All datasets are validated in the `notebooks/data_preview.ipynb` notebook:

**Validation Checks:**
1. ✅ No missing critical values
2. ✅ All amounts are positive and valid
3. ✅ All dates are valid and properly formatted
4. ✅ Proper data type consistency
5. ✅ Realistic value ranges
6. ✅ Logical relationships (e.g., due_date > issue_date)

**Run Validation:**
```bash
jupyter notebook notebooks/data_preview.ipynb
```

---

## 🚀 Future Use in Milestones

### Milestone 3: SMS Parser Tool
- Parse `sms.csv` messages
- Extract transaction details
- Validate extraction accuracy
- Handle edge cases

### Milestone 4: Insights Tool
- Analyze transaction patterns from SMS data
- Generate cash flow insights
- Identify spending trends
- Create visualizations

### Milestone 5: Invoice Collection Tool
- Track invoices from `invoices.json`
- Generate follow-up messages
- Analyze collection rates
- Identify late-paying customers

### Milestone 6: ADK Agent Integration
- Use all datasets for agent testing
- Multi-tool workflows
- Context management
- Response generation

---

## 📈 Dataset Statistics

### SMS Messages (sms.csv)
- **Total Records:** 50
- **Date Range:** Last 90 days
- **Amount Range:** KES 50 - 50,000
- **Transaction Types:** 7 types
- **Unique Vendors/People:** 30+

### Invoices (invoices.json)
- **Total Records:** 20
- **Total Value:** ~KES 1,000,000
- **Collection Rate:** ~47%
- **Payment Terms:** 7-90 days
- **Status Mix:** Realistic distribution

### Receipts (receipts.json)
- **Total Records:** 15
- **Total Value:** ~KES 850,000
- **Categories:** 10 expense types
- **Tax (VAT):** ~KES 65,000
- **Payment Methods:** 5 types

---

## 🔄 Regenerating Data

To regenerate all datasets:

```bash
cd data/synthetic/

# Generate SMS data
python sms_generator.py

# Generate invoices
python invoices_generator.py

# Generate receipts
python receipts_generator.py

# Validate all data
jupyter notebook ../../notebooks/data_preview.ipynb
```

---

## 📝 Notes

- All amounts are in Kenyan Shillings (KES)
- Dates are in ISO 8601 format for consistency
- Phone numbers use Kenyan format (254...)
- Business names are fictional but realistic
- Transaction patterns reflect actual Kenyan SME behavior
- Data is refreshed with each generation (random seed varies)

---

## 🤝 Contributing

To add new synthetic data types:

1. Create a new generator script (e.g., `expense_tracker_generator.py`)
2. Follow the pattern of existing generators
3. Document fields and use cases in this README
4. Add validation checks to `data_preview.ipynb`
5. Update statistics section

---

**Generated:** Milestone 2 - November 2025  
**Status:** Ready for Milestone 3+ development  
**Quality:** Validated and production-ready
