# Set Operations - Quick Start Guide (5 Minutes)

## 1. Navigate to Directory (30 seconds)
```bash
cd use_cases/04_set_operations
```

## 2. Test Basic Operation (1 minute)
```bash
# Simple A - B + C operation
python bin/set_operations.py -a "AAPL,MSFT,GOOGL" -b "MSFT" -c "NVDA,AMD"
# Result: AAPL, GOOGL, NVDA, AMD
```

## 3. Try Interactive Mode (2 minutes)
```bash
python bin/set_operations.py

# Follow the prompts:
# 1. Enter items for Set A (paste or type)
# 2. Enter items for Set B (what to remove)
# 3. Enter items for Set C (what to add)
# 4. Choose output format
```

## 4. Use Example Files (1 minute)
```bash
# Find what tickers to BUY (portfolio rebalancing)
python bin/set_operations.py \
  -a examples/tickers/portfolio_target.txt \
  -b examples/tickers/portfolio_current.txt \
  --operation "A-B" \
  --output output/to_buy.txt \
  --sort

# View result
type output\to_buy.txt
```

## 5. Quick Windows Batch Scripts (30 seconds)
```bash
# Use batch script for common operations
cd scripts\batch
ticker_diff.bat ..\..\examples\tickers\watchlist_tech.txt ..\..\examples\tickers\portfolio_current.txt
```

## 6. Format Conversion (NEW! - 30 seconds)
```bash
# Convert columnar list to comma-separated
python bin/set_operations.py --convert -a examples/tickers/watchlist_tech.txt --to-format comma

# Convert comma to columnar
python bin/set_operations.py --convert -a "AAPL,MSFT,GOOGL,NVDA" --to-format columnar

# Use batch script for quick conversion
scripts\batch\convert_to_comma.bat input.txt output.csv
```

## Next Steps
- Read full documentation: [README.md](README.md)
- Try ticker examples: `python scripts/demos/ticker_examples.py`
- Explore batch scripts: [scripts/batch/](scripts/batch/)
- Use templates: [templates/](templates/)

## Most Common Use Case
**"I have two ticker lists in columnar format and one comma-separated. How do I do A - B + C?"**

```bash
python bin/set_operations.py \
  -a your_list_A.txt \
  -b your_list_B.txt \
  -c "AAPL,MSFT,GOOGL,NVDA" \
  --operation "A-B+C" \
  --output output/result.txt \
  --output-format columnar \
  --sort
```

That's it! You're ready to use the Set Operations utility.