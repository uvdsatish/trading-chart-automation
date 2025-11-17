# Use Case #4: Set Operations Utility

A powerful and flexible Python utility for performing set operations on lists - perfect for managing ticker lists, watchlists, portfolios, and any other list-based data.

## Table of Contents
- [Quick Start](#quick-start)
- [Features](#features)
- [Installation](#installation)
- [Usage Modes](#usage-modes)
- [Input Formats](#input-formats)
- [Operations Reference](#operations-reference)
- [Output Formats](#output-formats)
- [Trading Use Cases](#trading-use-cases)
- [Directory Structure](#directory-structure)
- [Examples](#examples)
- [Batch Scripts](#batch-scripts)
- [Troubleshooting](#troubleshooting)
- [Performance](#performance)

## Quick Start

**New to this utility?** See [QUICK_START.md](QUICK_START.md) for a 5-minute introduction.

### Most Common Use Case
```bash
# A and B from files (columnar), C as comma-separated string
python bin/set_operations.py \
  -a examples/tickers/watchlist_tech.txt \
  -b examples/tickers/portfolio_current.txt \
  -c "PLTR,SNOW,CRWD" \
  --operation "A-B+C" \
  --output output/result.txt \
  --sort
```

## Features

### Multiple Input Formats
- **Columnar** (one item per line) - Best for Excel copy/paste
- **Comma-separated** values - Inline lists
- **Custom delimiters** (pipe, semicolon, tab, etc.)
- **JSON arrays** - For programmatic use
- **File input** (text, CSV, JSON)
- **Mixed format** auto-detection - Mix any formats in one command!

### Flexible Operations
- Default: **A - B + C** (items in A, minus items in B, plus items in C)
- Complex expressions: `(A|B)-C`, `A&B|C`, `A^B`, etc.
- Support for multiple sets (A through Z)
- All standard set operations:
  - Union (+, |)
  - Difference (-)
  - Intersection (&)
  - Symmetric difference (^)

### Output Options
- **Columnar format** - One per line (best for reimport)
- **Comma-separated** - For spreadsheets
- **JSON array** - For programming
- **Custom delimiter** - Any separator you need
- **File output** - Save to disk
- **Clipboard support** - Direct copy (requires pyperclip)

### Additional Features
- Case-sensitive or case-insensitive comparison
- Sorted or unsorted output
- Interactive mode for guided use
- Verbose mode for debugging
- Handles 100,000+ items efficiently

## Installation

```bash
# No installation needed - uses Python standard library

# Optional: For clipboard support
pip install pyperclip
```

## Usage Modes

### 1. Interactive Mode (Easiest)
```bash
python bin/set_operations.py
```
Guides you through the process step-by-step.

### 2. Command Line Mode
```bash
python bin/set_operations.py -a list1.txt -b list2.txt -c list3.txt
```

### 3. Batch Scripts (Windows)
```bash
scripts\batch\ticker_diff.bat list1.txt list2.txt
```

## Input Formats

### Columnar Format (One Per Line)
```
AAPL
MSFT
GOOGL
NVDA
```

### Comma-Separated
```
AAPL,MSFT,GOOGL,NVDA
```
Or directly: `-a "AAPL,MSFT,GOOGL,NVDA"`

### Mixed Formats in One Command
```bash
python bin/set_operations.py \
  -a columnar_file.txt \          # Columnar file
  -b comma_file.txt \              # Comma-separated file
  -c "AAPL,MSFT,GOOGL" \          # Direct comma input
  --operation "A-B+C"
```

## Operations Reference

| Operation | Symbol | Description | Example |
|-----------|--------|-------------|---------|
| Union | `+` or `|` | All items in either set | `A+B` |
| Difference | `-` | Items in first but not second | `A-B` |
| Intersection | `&` | Items in both sets | `A&B` |
| Symmetric Diff | `^` | Items in either but not both | `A^B` |
| Complex | `()` | Grouping for order | `(A+B)-C` |

### Common Patterns
- `A-B+C` - Remove B from A, then add C (default)
- `A&B` - Find common items
- `A+B+C` - Combine all lists
- `(A|B)-C` - Union of A and B, minus C
- `A-(B+C)` - A minus anything in B or C

## Output Formats

### Columnar (Default for Files)
```
AAPL
MSFT
NVDA
```
Use: `--output-format columnar`

### Comma-Separated
```
AAPL,MSFT,NVDA
```
Use: `--output-format comma`

### JSON Array
```json
["AAPL", "MSFT", "NVDA"]
```
Use: `--output-format json`

## Format Conversion (NEW!)

Convert between different list formats without performing set operations.

### Quick Conversion Examples

```bash
# Columnar → Comma-separated
python bin/set_operations.py --convert -a tickers.txt --to-format comma

# Comma → Columnar
python bin/set_operations.py --convert -a "AAPL,MSFT,GOOGL" --to-format columnar

# File → JSON
python bin/set_operations.py --convert -a list.txt --to-format json --output data.json

# With sorting
python bin/set_operations.py --convert -a unsorted.txt --to-format columnar --sort
```

### Batch Conversion Scripts

```bash
# Windows batch scripts for easy conversion
scripts\batch\convert_to_comma.bat input.txt output.csv
scripts\batch\convert_to_columnar.bat comma_list.txt columnar.txt
scripts\batch\convert_interactive.bat  # Interactive wizard
```

### Conversion Use Cases

**Excel Import/Export:**
```bash
# StockCharts columnar → Excel CSV
python bin/set_operations.py --convert -a chartlist.txt --to-format comma --output excel.csv

# Excel CSV → StockCharts columnar
python bin/set_operations.py --convert -a excel.csv --to-format columnar --output chartlist.txt
```

**Quick Format Switch:**
```bash
# Direct conversion (no files)
python bin/set_operations.py --convert -a "SPY,QQQ,DIA,IWM" --to-format columnar
# Output:
# SPY
# QQQ
# DIA
# IWM
```

## Trading Use Cases

### 1. Portfolio Rebalancing
```bash
# What to BUY (in target but not current)
python bin/set_operations.py \
  -a examples/tickers/portfolio_target.txt \
  -b examples/tickers/portfolio_current.txt \
  --operation "A-B" \
  --output output/to_buy.txt

# What to SELL (in current but not target)
python bin/set_operations.py \
  -a examples/tickers/portfolio_current.txt \
  -b examples/tickers/portfolio_target.txt \
  --operation "A-B" \
  --output output/to_sell.txt
```

### 2. Multi-Timeframe Analysis
```bash
# Find tickers strong on BOTH daily AND 60-minute
python bin/set_operations.py \
  -a examples/tickers/chartlist_daily.txt \
  -b examples/tickers/chartlist_60min.txt \
  --operation "A&B" \
  --output output/multi_timeframe.txt
```

### 3. Earnings Exclusion
```bash
# Remove earnings week from swing trades
python bin/set_operations.py \
  -a examples/tickers/breakout_candidates.txt \
  -b examples/tickers/earnings_this_week.txt \
  --operation "A-B" \
  --output output/swing_filtered.txt
```

### 4. Build Master Watchlist
```bash
# Combine all sector watchlists
python bin/set_operations.py \
  -a examples/tickers/watchlist_tech.txt \
  -b examples/tickers/watchlist_energy.txt \
  -c examples/tickers/watchlist_financials.txt \
  --operation "A+B+C" \
  --output output/master_watchlist.txt \
  --sort
```

### 5. Volume Analysis
```bash
# Find your stocks with high volume today
python bin/set_operations.py \
  -a examples/tickers/portfolio_current.txt \
  -b examples/tickers/high_volume_today.txt \
  --operation "A&B" \
  --output output/my_high_volume.txt
```

## Directory Structure

```
04_set_operations/
├── README.md              # This file
├── QUICK_START.md        # 5-minute guide
├── bin/
│   └── set_operations.py # Main utility
├── scripts/
│   ├── demos/            # Demo scripts
│   │   ├── demo_set_operations.py
│   │   └── ticker_examples.py
│   └── batch/            # Windows batch scripts
│       ├── ticker_diff.bat
│       ├── ticker_common.bat
│       ├── ticker_combine.bat
│       └── ticker_interactive.bat
├── examples/
│   ├── basic/            # Simple examples
│   └── tickers/          # Trading examples
├── templates/            # Blank templates
└── output/              # Results (gitignored)
```

## Examples

### Example Files Provided

#### Basic Examples (`examples/basic/`)
- `list_a.txt`, `list_b.txt`, `list_c.txt` - Simple fruit lists
- `comma_list.txt` - Comma-separated example

#### Ticker Examples (`examples/tickers/`)
- **Watchlists**: tech, energy, financials
- **Portfolios**: current, target
- **ChartLists**: daily, 60min
- **Strategies**: momentum, value, breakouts
- **Market Data**: earnings, high_volume

### Run All Examples
```bash
# Run general demonstrations
python scripts/demos/demo_set_operations.py

# Run ticker-specific examples
python scripts/demos/ticker_examples.py
```

## Batch Scripts

Windows batch scripts for common operations:

### ticker_diff.bat
Find items in A but not in B:
```bash
scripts\batch\ticker_diff.bat list1.txt list2.txt
```

### ticker_common.bat
Find items in both A and B:
```bash
scripts\batch\ticker_common.bat list1.txt list2.txt
```

### ticker_combine.bat
Combine multiple lists:
```bash
scripts\batch\ticker_combine.bat list1.txt list2.txt list3.txt
```

### ticker_interactive.bat
Launch interactive mode:
```bash
scripts\batch\ticker_interactive.bat
```

## Troubleshooting

### Common Issues

**"File not found"**
- Use full paths or navigate to correct directory
- Check file exists: `dir filename.txt`

**"Empty result"**
- Use `--verbose` to see set sizes
- Check your operation logic
- Verify input formats are detected correctly

**"Unexpected results"**
- Check for trailing spaces in data
- Use `--ignore-case` if needed
- Verify delimiter is correct

### Debug Mode
```bash
python bin/set_operations.py -a list1.txt -b list2.txt --verbose
```

## Performance

- **Speed**: < 1 second for most operations under 10,000 items
- **Memory**: ~50 bytes per unique item
- **Capacity**: Tested with 100,000+ items
- **Duplicates**: Automatically removed (uses Python sets)

## Integration

### With Excel
```excel
# Export column
=TEXTJOIN(",", TRUE, A:A)
```
Copy result and use directly with `-a` parameter

### With StockCharts
1. Export ChartList to columnar format
2. Process with set_operations
3. Import result using columnar output

### With Python
```python
import subprocess
result = subprocess.run([
    "python", "bin/set_operations.py",
    "-a", "list1.txt",
    "-b", "list2.txt",
    "--operation", "A-B"
], capture_output=True, text=True)
items = result.stdout.strip().split(',')
```

## Advanced Tips

### Chaining Operations
```bash
# Step 1: Combine sources
python bin/set_operations.py -a source1.txt -b source2.txt \
  --operation "A+B" --output temp.txt

# Step 2: Filter
python bin/set_operations.py -a temp.txt -b exclude.txt \
  --operation "A-B" --output final.txt
```

### Case-Insensitive Matching
```bash
python bin/set_operations.py \
  -a "Apple,BANANA,Cherry" \
  -b "banana,CHERRY" \
  --operation "A-B" \
  --ignore-case
# Result: Apple
```

### Using Templates
1. Copy template from `templates/` directory
2. Fill in your data
3. Use as input file

## Support

For issues or questions:
1. Check [QUICK_START.md](QUICK_START.md)
2. Review examples in `scripts/demos/`
3. Use `--verbose` for debugging
4. Refer to main project documentation

---

**Version**: 1.0
**Location**: `use_cases/04_set_operations/`
**Main Script**: `bin/set_operations.py`