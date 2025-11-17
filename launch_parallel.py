"""
Parallel Launcher for Use Cases #2 and #3

This script provides a simple way to launch both use cases in parallel
with split-screen browser windows.

Usage:
    python launch_parallel.py

    Or with specific config files:
    python launch_parallel.py --batch config/chartlist_config_sample.xlsx --viewer config/justChartlist-S1-daily.xlsx
"""

import sys
import os
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Main launcher for parallel execution"""
    parser = argparse.ArgumentParser(
        description="Launch Use Cases #2 and #3 in parallel with split-screen browsers"
    )

    parser.add_argument(
        "--batch",
        type=str,
        default="config/chartlist_config_S1.xlsx",
        help="Excel config file for ChartList Batch Viewer (Use Case #2)"
    )

    parser.add_argument(
        "--viewer",
        type=str,
        default="config/justChartlist-S1-daily.xlsx",
        help="Excel config file for ChartList Viewer (Use Case #3)"
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)"
    )

    args = parser.parse_args()

    # Check if config files exist
    batch_path = Path(args.batch)
    viewer_path = Path(args.viewer)

    if not batch_path.exists():
        print(f"[ERROR] Batch config file not found: {batch_path}")
        print(f"Please ensure the file exists or specify a different file with --batch")
        sys.exit(1)

    if not viewer_path.exists():
        print(f"[ERROR] Viewer config file not found: {viewer_path}")
        print(f"Please ensure the file exists or specify a different file with --viewer")
        sys.exit(1)

    print("=" * 70)
    print("PARALLEL CHARTLIST LAUNCHER")
    print("=" * 70)
    print(f"[USE CASE #2] ChartList Batch: {batch_path}")
    print(f"[USE CASE #3] ChartList Viewer: {viewer_path}")
    print("=" * 70)
    print("")

    # Get Python executable path from conda environment
    python_exe = r"C:\Users\uvdsa\.conda\envs\browser_automation\python.exe"

    # Check if conda environment python exists
    if not Path(python_exe).exists():
        print(f"[ERROR] Conda environment Python not found at: {python_exe}")
        print("Please activate the browser_automation conda environment first:")
        print("    conda activate browser_automation")
        sys.exit(1)

    # Build the command
    cmd = [
        python_exe,
        "main.py",
        "--mode", "parallel",
        "--batch-config", str(batch_path),
        "--viewer-config", str(viewer_path),
        "--log-level", args.log_level
    ]

    # Convert to string for Windows
    cmd_str = ' '.join([f'"{c}"' if ' ' in c else c for c in cmd])

    print(f"Executing: {cmd_str}")
    print("")

    # Execute the command
    import subprocess
    result = subprocess.run(cmd_str, shell=True)

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())