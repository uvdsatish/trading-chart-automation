# Templates Guide

## Purpose
These templates provide starting points for different input formats. Copy and modify as needed.

## Available Templates

### 1. Columnar Template (`template_columnar.txt`)
Best for:
- Copy/paste from Excel columns
- Importing from StockCharts
- One ticker per line format

**Usage:**
1. Copy to your working directory
2. Rename (e.g., `my_watchlist.txt`)
3. Replace items with your data
4. Use with set_operations.py

### 2. Comma-Separated Template (`template_comma.txt`)
Best for:
- Inline lists
- Quick manual entry
- Exporting to spreadsheets

**Usage:**
1. Copy template
2. Replace with comma-separated values
3. Can be used directly or saved to file

### 3. JSON Template (`template_json.txt`)
Best for:
- Programmatic generation
- API integration
- Structured data

**Usage:**
1. Copy template
2. Replace array items
3. Ensure valid JSON format

## Examples

### From Excel to Columnar
1. Select ticker column in Excel
2. Copy (Ctrl+C)
3. Open `template_columnar.txt`
4. Delete comment lines
5. Paste tickers
6. Save as `watchlist.txt`

### Quick Comma List
```bash
# Direct use without file
python ../bin/set_operations.py -a "AAPL,MSFT,GOOGL" -b "MSFT"
```

### JSON for Scripts
```python
import json
with open('template_json.txt', 'r') as f:
    tickers = json.load(f)
```

## Tips
- Remove all comment lines before using
- Check for trailing spaces
- Ensure consistent formatting
- Test with small dataset first