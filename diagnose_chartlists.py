"""
Diagnostic script to identify available ChartLists in StockCharts account
This will help determine the correct ChartList names to use in the Excel file
"""

import asyncio
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from src.browser.stockcharts_controller import StockChartsController
import yaml

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def diagnose_chartlists():
    """Find and list all available ChartLists in the account"""

    # Load configuration
    load_dotenv(Path(__file__).parent / "config" / ".env")

    # Load config from yaml
    config_path = Path(__file__).parent / "config" / "settings.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Load credentials
    username = os.getenv("STOCKCHARTS_USERNAME")
    password = os.getenv("STOCKCHARTS_PASSWORD")

    if not all([username, password]):
        logger.error("Missing credentials in .env file")
        return

    # Initialize browser controller
    browser = StockChartsController(
        username=username,
        password=password,
        headless=False,  # Show browser for debugging
        screenshot_dir=os.getenv("SCREENSHOT_DIR", "screenshots"),
        config=config
    )

    try:
        # Initialize and login
        await browser.initialize()
        logger.info("Browser initialized")

        login_success = await browser.login()
        if not login_success:
            logger.error("Login failed")
            return

        logger.info("Login successful!")

        # Navigate to AMZN to access ChartList dropdowns
        logger.info("Navigating to AMZN chart...")
        await browser.enter_ticker_in_search_box("AMZN")

        # Wait for page to load
        await asyncio.sleep(2)

        # Click on ChartList dropdown to open it
        logger.info("\nLooking for ChartList dropdown...")
        chartlist_button = await browser.page.query_selector("#chart-list-dropdown-menu-toggle-button")

        if not chartlist_button:
            logger.error("ChartList dropdown button not found")
            return

        # Open the dropdown
        await chartlist_button.click()
        await asyncio.sleep(1)

        # Get all ChartList items
        logger.info("\nFinding all available ChartLists...")

        # Try different selectors to find ChartList items
        selectors_to_try = [
            ".chart-list-dropdown-menu a",
            ".dropdown-menu a",
            "[role='menu'] a",
            ".dropdown-item"
        ]

        chartlist_items = []
        for selector in selectors_to_try:
            items = await browser.page.locator(selector).all()
            if items:
                logger.info(f"Found {len(items)} items with selector: {selector}")
                chartlist_items = items
                break

        if not chartlist_items:
            logger.warning("No ChartList items found with standard selectors")
            # Try to get all links in the dropdown
            all_links = await browser.page.locator("a").all()
            logger.info(f"Found {len(all_links)} total links on page")

        # Extract ChartList names
        logger.info("\n" + "=" * 60)
        logger.info("AVAILABLE CHARTLISTS IN YOUR ACCOUNT:")
        logger.info("=" * 60)

        chartlist_names = []
        for item in chartlist_items:
            try:
                name = await item.inner_text()
                if name and name.strip():
                    chartlist_names.append(name.strip())
                    logger.info(f"  - {name.strip()}")
            except:
                continue

        logger.info("=" * 60)
        logger.info(f"Total ChartLists found: {len(chartlist_names)}")

        if chartlist_names:
            # Create a corrected Excel file
            import pandas as pd
            corrected_file = Path("config/corrected_chartlists.xlsx")
            df = pd.DataFrame({'ChartList': chartlist_names[:7]})  # Take first 7
            df.to_excel(corrected_file, index=False)
            logger.info(f"\n[SUCCESS] Created corrected Excel file: {corrected_file}")
            logger.info("You can use this file with: python main.py --mode chartlist-viewer --config config/corrected_chartlists.xlsx")

        # Keep browser open for inspection
        logger.info("\nBrowser will stay open for inspection. Press Enter to close...")
        input()

    except Exception as e:
        logger.error(f"Error during diagnosis: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await browser.close()
        logger.info("Diagnosis complete!")

if __name__ == "__main__":
    asyncio.run(diagnose_chartlists())