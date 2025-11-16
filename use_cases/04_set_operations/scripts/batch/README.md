# Batch Scripts for Set Operations

Quick Windows batch scripts for common set operations.

## Available Scripts

### ticker_diff.bat
**Purpose:** Find tickers in List A that are NOT in List B (A - B)

**Usage:**
```batch
ticker_diff.bat list_a.txt list_b.txt
```

**Interactive Mode:**
```batch
ticker_diff.bat
# Then enter file paths when prompted
```

**Example:**
```batch
ticker_diff.bat ..\..\examples\tickers\watchlist_tech.txt ..\..\examples\tickers\portfolio_current.txt
# Result: Tech stocks you don't own
```

### ticker_common.bat
**Purpose:** Find tickers that appear in BOTH lists (A & B)

**Usage:**
```batch
ticker_common.bat list_a.txt list_b.txt
```

**Example:**
```batch
ticker_common.bat ..\..\examples\tickers\momentum_stocks.txt ..\..\examples\tickers\value_picks.txt
# Result: Stocks that are both momentum AND value
```

### ticker_combine.bat
**Purpose:** Combine multiple ticker lists (A + B + C)

**Usage:**
```batch
ticker_combine.bat
# Then enter up to 3 file paths
```

**Example:**
```batch
ticker_combine.bat
# Enter: watchlist_tech.txt
# Enter: watchlist_energy.txt
# Enter: watchlist_financials.txt
# Result: All tickers combined (duplicates removed)
```

### ticker_interactive.bat
**Purpose:** Launch the set operations utility in interactive mode

**Usage:**
```batch
ticker_interactive.bat
```

**What it does:**
- Launches interactive mode
- Guides you through entering sets
- Helps choose operations
- Assists with output format

## Tips for Using Batch Scripts

### File Paths
When using batch scripts, you can use:
- **Relative paths**: `..\..\examples\tickers\list.txt`
- **Absolute paths**: `C:\Users\name\Documents\tickers.txt`
- **Current directory**: `list.txt` (if in same folder)

### Output Location
By default, results are saved to the `output` directory:
- `ticker_diff.bat` → `output\diff_result.txt`
- `ticker_common.bat` → `output\common_result.txt`
- `ticker_combine.bat` → `output\combined_result.txt`

### Customizing Scripts
You can edit the batch files to:
- Change default output locations
- Add sorting by default
- Change output format
- Add verbose mode

**Example customization:**
```batch
REM Add --sort and --output-format columnar to any script
python ..\..\bin\set_operations.py -a %1 -b %2 --operation "A-B" --sort --output-format columnar
```

## Common Use Cases

### Daily Workflow
```batch
REM Morning: Find new opportunities
ticker_diff.bat todays_scan.txt yesterdays_watchlist.txt

REM Check overlap with portfolio
ticker_common.bat opportunities.txt portfolio.txt

REM Combine all watchlists for monitoring
ticker_combine.bat daily.txt hourly.txt alerts.txt
```

### Portfolio Management
```batch
REM What to buy
ticker_diff.bat target_portfolio.txt current_portfolio.txt

REM What to sell
ticker_diff.bat current_portfolio.txt target_portfolio.txt
```

### Multi-Timeframe Analysis
```batch
REM Find stocks strong on multiple timeframes
ticker_common.bat daily_breakouts.txt hourly_breakouts.txt
```

## Troubleshooting

**"File not found"**
- Check file path is correct
- Use full path if needed
- Ensure .txt extension is included

**"Python not found"**
- Edit .bat file to use your Python path
- Default: `C:\Users\uvdsa\.conda\envs\browser_automation\python.exe`

**Empty results**
- Check your input files have content
- Verify operation logic is correct
- Try with --verbose flag for debugging

## Advanced Usage

### Chaining Operations
```batch
REM First operation
ticker_diff.bat all_stocks.txt excluded.txt
REM Output saved to output\diff_result.txt

REM Use result in next operation
ticker_common.bat output\diff_result.txt high_volume.txt
```

### Creating Custom Scripts
Copy any existing script and modify:
```batch
@echo off
REM My custom momentum filter
python ..\..\bin\set_operations.py ^
  -a momentum_scores.txt ^
  -b low_volume.txt ^
  -c high_risk.txt ^
  --operation "A-(B+C)" ^
  --output output\filtered_momentum.txt ^
  --sort
pause
```