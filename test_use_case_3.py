"""
Test script for Use Case #3: ChartList Viewer
Tests the load_chartlist_names_only() method
"""

from pathlib import Path
from src.utils.excel_reader import ChartListConfigReader
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_load_chartlist_names():
    """Test loading ChartList names from Excel"""

    # Path to the Excel file
    excel_path = Path("config/justChartlist-S1-daily.xlsx")

    if not excel_path.exists():
        print(f"[ERROR] Excel file not found: {excel_path}")
        return False

    print(f"\n[TEST] Loading ChartList names from: {excel_path}")
    print("=" * 60)

    try:
        # Create reader and load ChartList names
        reader = ChartListConfigReader(excel_path)
        chartlist_names = reader.load_chartlist_names_only()

        print(f"[SUCCESS] Loaded {len(chartlist_names)} ChartList names:")
        print("-" * 60)

        for idx, name in enumerate(chartlist_names, 1):
            print(f"  {idx}. {name}")

        print("-" * 60)
        print("[PASS] Test completed successfully!")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to load ChartList names: {e}")
        return False

if __name__ == "__main__":
    success = test_load_chartlist_names()
    exit(0 if success else 1)