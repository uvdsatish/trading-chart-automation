"""
Create Excel template for ChartList Batch Viewer
"""

from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.excel_reader import ChartListConfigReader


def main():
    """Create template Excel file"""
    # Ensure config directory exists
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)

    # Create template
    template_path = config_dir / "chartlist_config_template.xlsx"
    ChartListConfigReader.create_template(template_path)
    print(f"[SUCCESS] Template created: {template_path}")

    # Also create a sample config for immediate use
    sample_path = config_dir / "chartlist_config_sample.xlsx"
    ChartListConfigReader.create_template(sample_path)
    print(f"[SUCCESS] Sample config created: {sample_path}")

    print("\nTo use the ChartList Batch Viewer:")
    print("1. Edit the Excel file with your charts")
    print("2. Run: python main.py --mode chartlist-batch --config config/chartlist_config_sample.xlsx")
    print("\nExcel columns:")
    print("  - ChartList: Name of your ChartList (e.g., 'My Watchlist')")
    print("  - Ticker: Stock symbol (e.g., 'AAPL')")
    print("  - TabOrder: Order to open tabs (1, 2, 3...)")
    print("  - TimeframeBox: Optional ChartStyle box number (1-12)")
    print("  - Notes: Optional notes")


if __name__ == "__main__":
    main()