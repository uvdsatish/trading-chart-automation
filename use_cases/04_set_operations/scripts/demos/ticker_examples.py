#!/usr/bin/env python3
"""
Ticker List Set Operations - Practical Examples
Demonstrates common ticker list management scenarios for traders
"""

import subprocess
import sys
import os
from pathlib import Path

def run_operation(description, cmd_args, base_path=""):
    """Run a set operation and display results"""
    print("\n" + "=" * 70)
    print(f"EXAMPLE: {description}")
    print("-" * 70)

    # Build full command
    script_path = os.path.join(base_path, "set_operations.py")
    cmd = [sys.executable, script_path] + cmd_args
    print("Command:", " ".join(cmd_args))
    print("-" * 70)

    # Run command
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("Result:")
        print(result.stdout)
    else:
        print("Error:")
        print(result.stderr)

    return result.stdout

def main():
    """Run all ticker list examples"""

    print("=" * 70)
    print("TICKER LIST SET OPERATIONS - PRACTICAL EXAMPLES")
    print("=" * 70)

    # Navigate to examples/tickers directory
    ticker_dir = Path(__file__).parent.parent.parent / "examples" / "tickers"
    if ticker_dir.exists():
        os.chdir(ticker_dir)
        base_path = "../../bin/"
    else:
        print("Error: Cannot find examples/tickers directory")
        return

    # Example 1: Portfolio Rebalancing - What to BUY
    print("\n" + "#" * 70)
    print("# SCENARIO 1: PORTFOLIO REBALANCING")
    print("#" * 70)

    run_operation(
        "Find tickers to BUY (in target but not in current)",
        ["-a", "portfolio_target.txt",
         "-b", "portfolio_current.txt",
         "--operation", "A-B",
         "--sort"],
        base_path
    )

    run_operation(
        "Find tickers to SELL (in current but not in target)",
        ["-a", "portfolio_current.txt",
         "-b", "portfolio_target.txt",
         "--operation", "A-B",
         "--sort"],
        base_path
    )

    # Example 2: Multi-Strategy Intersection
    print("\n" + "#" * 70)
    print("# SCENARIO 2: MULTI-STRATEGY ANALYSIS")
    print("#" * 70)

    run_operation(
        "Find stocks that are BOTH breakout candidates AND high momentum",
        ["-a", "breakout_candidates.txt",
         "-b", "momentum_stocks.txt",
         "--operation", "A&B",
         "--sort"],
        base_path
    )

    run_operation(
        "Find pure momentum plays (momentum but NOT value)",
        ["-a", "momentum_stocks.txt",
         "-b", "value_picks.txt",
         "--operation", "A-B",
         "--sort"],
        base_path
    )

    # Example 3: Earnings Exclusion
    print("\n" + "#" * 70)
    print("# SCENARIO 3: EARNINGS WEEK MANAGEMENT")
    print("#" * 70)

    run_operation(
        "Remove earnings week tickers from daily chartlist",
        ["-a", "chartlist_daily.txt",
         "-b", "earnings_this_week.txt",
         "--operation", "A-B",
         "--sort"],
        base_path
    )

    # Example 4: Volume Analysis
    print("\n" + "#" * 70)
    print("# SCENARIO 4: VOLUME AND LIQUIDITY")
    print("#" * 70)

    run_operation(
        "Find high volume tickers that are also in portfolio",
        ["-a", "high_volume_today.txt",
         "-b", "portfolio_current.txt",
         "--operation", "A&B",
         "--sort"],
        base_path
    )

    # Example 5: Sector Watchlist Building
    print("\n" + "#" * 70)
    print("# SCENARIO 5: SECTOR ANALYSIS")
    print("#" * 70)

    run_operation(
        "Build master sector watchlist (Tech + Energy + Financials)",
        ["-a", "watchlist_tech.txt",
         "-b", "watchlist_energy.txt",
         "-c", "watchlist_financials.txt",
         "--operation", "A+B+C",
         "--sort",
         "--output-format", "comma"],
        base_path
    )

    # Example 6: Multi-Timeframe Alignment
    print("\n" + "#" * 70)
    print("# SCENARIO 6: MULTI-TIMEFRAME ALIGNMENT")
    print("#" * 70)

    run_operation(
        "Find tickers appearing on BOTH daily AND 60-minute charts",
        ["-a", "chartlist_daily.txt",
         "-b", "chartlist_60min.txt",
         "--operation", "A&B",
         "--sort"],
        base_path
    )

    # Example 7: Complex Operation
    print("\n" + "#" * 70)
    print("# SCENARIO 7: COMPLEX FILTERING")
    print("#" * 70)

    run_operation(
        "Tech watchlist minus portfolio plus high volume = opportunities",
        ["-a", "watchlist_tech.txt",
         "-b", "portfolio_current.txt",
         "-c", "high_volume_today.txt",
         "--operation", "(A-B)&C",
         "--sort"],
        base_path
    )

    # Example 8: Finding Unique Items
    print("\n" + "#" * 70)
    print("# SCENARIO 8: UNIQUE IDENTIFICATION")
    print("#" * 70)

    run_operation(
        "Find tech stocks NOT in any other sector list",
        ["-a", "watchlist_tech.txt",
         "-b", "watchlist_energy.txt",
         "-c", "watchlist_financials.txt",
         "--operation", "A-(B+C)",
         "--sort"],
        base_path
    )

    # Example 9: Mixed Input Formats
    print("\n" + "#" * 70)
    print("# SCENARIO 9: MIXED INPUT FORMATS")
    print("#" * 70)

    print("\n" + "=" * 70)
    print("EXAMPLE: Columnar files + comma-separated direct input")
    print("-" * 70)
    print("Command: -a portfolio_current.txt -b 'SPY,QQQ,DIA' --operation A-B")
    print("-" * 70)

    # Direct comma-separated input
    script_path = "../../bin/set_operations.py"
    cmd = [sys.executable, script_path,
           "-a", "portfolio_current.txt",
           "-b", "SPY,QQQ,DIA",
           "--operation", "A-B",
           "--sort"]

    result = subprocess.run(cmd, capture_output=True, text=True)
    print("Result:")
    print(result.stdout)

    # Example 10: Output Formats
    print("\n" + "#" * 70)
    print("# SCENARIO 10: DIFFERENT OUTPUT FORMATS")
    print("#" * 70)

    # Get a sample result
    sample_tickers = ["AAPL", "MSFT", "NVDA"]

    run_operation(
        "JSON format output (for programming)",
        ["-a", "momentum_stocks.txt",
         "-b", "value_picks.txt",
         "--operation", "A-B",
         "--output-format", "json",
         "--sort"],
        base_path
    )

    # Summary Statistics
    print("\n" + "=" * 70)
    print("EXAMPLE FILES SUMMARY")
    print("=" * 70)

    files = [
        ("Tech Watchlist", "watchlist_tech.txt"),
        ("Energy Watchlist", "watchlist_energy.txt"),
        ("Financial Watchlist", "watchlist_financials.txt"),
        ("Current Portfolio", "portfolio_current.txt"),
        ("Target Portfolio", "portfolio_target.txt"),
        ("Daily Charts", "chartlist_daily.txt"),
        ("60min Charts", "chartlist_60min.txt"),
        ("Breakout Candidates", "breakout_candidates.txt"),
        ("Momentum Stocks", "momentum_stocks.txt"),
        ("Value Picks", "value_picks.txt"),
    ]

    for name, filename in files:
        if Path(filename).exists():
            with open(filename, 'r') as f:
                content = f.read()
                # Count lines or commas
                if ',' in content:
                    count = len(content.split(','))
                else:
                    count = len([l for l in content.splitlines() if l.strip()])
                print(f"  {name:25} {count:3} tickers")

    print("\n" + "=" * 70)
    print("QUICK TIPS")
    print("=" * 70)
    print("1. Use --sort to alphabetize output")
    print("2. Use --output filename.txt to save results")
    print("3. Use --ignore-case for case-insensitive matching")
    print("4. Use --verbose to see operation details")
    print("5. Use --clipboard to copy results (requires pyperclip)")
    print("\n" + "=" * 70)
    print("For interactive mode, run: python set_operations.py")
    print("For help, run: python set_operations.py --help")
    print("=" * 70)

if __name__ == "__main__":
    main()