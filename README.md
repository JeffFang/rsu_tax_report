# Stock Transaction Tracker 📈

A Python tool to track ESPP, RSU, and stock sale transactions while automatically calculating Adjusted Cost Base (ACB), capital gains/losses, and annual summaries for Canadian tax reporting.

---

## Features
- 🧮 Automated ACB tracking for ESPP and RSU vesting events
- 💸 Capital gain/loss calculations using FIFO (First-In-First-Out) methodology
- 📊 Generates detailed transaction history and annual tax summaries
- 💰 Handles USD-to-CAD conversions using historical exchange rates
- 📁 Excel output with two sheets: `Transactions` and `Annual Summary`

---

## Prerequisites
- Python 3.10+
- Required packages:
  ```bash
  pandas openpyxl

## Installations
1. Clone the repository:
```bash
git clone https://github.com/yourusername/stock-tracker.git
cd stock-tracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt  # If you have a requirements file
# OR
pip install pandas openpyxl
```

## Usage
1. Prepare ESPP and RSU confirmation PDFs
Download RSU release confirmation and ESPP confirmation pdfs and place into `/pdfs/` dir.

2. Prepare sells cvs
Create a CSV file `./sells.csv` with this format:
```
Transaction,Date & Time,Sale Quantity,Price
Order Executed,03/10/2025 10:42:26 AM ET,114,71.415
```

2. Run the Script
Execute the program:

```bash
python main.py
```
