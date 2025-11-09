"""
Hybrid Browser Automation for StockCharts.com - Multi-Timeframe Analysis

Production Use Cases:
1. Multi-Timeframe Viewer: Opens 3 tabs (Daily, 60min, 5min) for manual viewing
2. Multi-Timeframe Analysis: Opens 3 tabs + AI-powered analysis with report

Usage:
    python main.py --ticker AEIS                              # AI analysis (default)
    python main.py --ticker AEIS --mode analysis              # AI analysis
    python main.py --ticker AEIS --mode viewer                # Manual viewing only
"""
import asyncio
import argparse
import logging
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.browser.stockcharts_controller import StockChartsController
from src.ai.chart_analyzer import ChartAnalyzer
from src.services.hybrid_chart_service import HybridChartService


def setup_logging(log_level: str = "INFO"):
    """Configure logging"""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('poc_automation.log')
        ]
    )


def load_config() -> dict:
    """Load configuration from yaml file"""
    config_path = Path(__file__).parent / "config" / "settings.yaml"

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


async def multi_timeframe_viewer(ticker: str, config: dict):
    """
    Production Use Case #1: Multi-Timeframe Chart Viewer
    Opens 4 tabs with Daily, Weekly, 60min, 5min charts and keeps browser open for manual inspection
    """
    logger = logging.getLogger(__name__)
    logger.info(f"=" * 70)
    logger.info(f"MULTI-TIMEFRAME VIEWER: {ticker}")
    logger.info(f"=" * 70)

    # Load credentials
    username = os.getenv("STOCKCHARTS_USERNAME")
    password = os.getenv("STOCKCHARTS_PASSWORD")

    if not all([username, password]):
        logger.error("Missing credentials in .env file")
        logger.error("Required: STOCKCHARTS_USERNAME, STOCKCHARTS_PASSWORD")
        return

    # Initialize browser controller
    browser = StockChartsController(
        username=username,
        password=password,
        headless=False,  # Must be visible for manual inspection
        screenshot_dir=os.getenv("SCREENSHOT_DIR", "screenshots"),
        config=config
    )

    try:
        # Initialize browser
        await browser.initialize()

        # Login
        logger.info("Logging in to StockCharts.com...")
        login_success = await browser.login()

        if not login_success:
            logger.error("Login failed")
            return

        logger.info("[SUCCESS] Login successful!\n")

        # Define ChartStyle box numbers (vertical grey boxes on far left edge)
        # Box #1 = Daily (default), Box #7 = 60min, Box #10 = 5min
        chartstyle_box_numbers = [1, 4, 7, 10]  # Enhanced: Added Weekly (box #4)

        logger.info(f"Opening {len(chartstyle_box_numbers)} timeframe tabs for {ticker}...")
        logger.info(f"ChartStyle Box Numbers: {chartstyle_box_numbers} (Box 1=Daily, 4=Weekly, 7=60min, 10=5min)\n")

        # Open multi-timeframe tabs
        pages = await browser.open_multi_timeframe_tabs(ticker, chartstyle_box_numbers)

        logger.info("\n" + "=" * 70)
        logger.info(f"ALL TABS OPENED - {len(pages)}/{len(chartstyle_box_numbers)} successful")
        logger.info("=" * 70)
        logger.info(f"Ticker: {ticker}")
        logger.info(f"Tabs open:")
        for i, preset in enumerate(pages.keys(), 1):
            logger.info(f"  {i}. {preset}")

        logger.info("\n" + "=" * 70)
        logger.info("BROWSER IS NOW OPEN IN KIOSK FULLSCREEN MODE")
        logger.info("=" * 70)
        logger.info("[KIOSK MODE] Browser using entire monitor (no taskbar/UI)")
        logger.info("[NAVIGATION] Switch between tabs: Ctrl+Tab or click tabs")
        logger.info("[EXIT] Use Alt+F4 to close browser (F11 disabled in kiosk)")
        logger.info("[ALTERNATIVE] Press Ctrl+C in this terminal to close")
        logger.info("=" * 70)

        # Robust wait mechanism that works in both interactive and background modes
        try:
            input()  # Try waiting for Enter key
        except (EOFError, OSError):
            # If input() fails (background/redirected mode), wait indefinitely
            logger.info("\n[Non-interactive mode detected]")
            logger.info("Browser will stay open until you:")
            logger.info("  1. Close the browser window manually, OR")
            logger.info("  2. Press Ctrl+C in this terminal")
            logger.info("Waiting...")
            try:
                while True:
                    await asyncio.sleep(3600)  # Sleep in 1-hour chunks
            except KeyboardInterrupt:
                logger.info("\nKeyboard interrupt received...")

        logger.info("\nClosing browser...")

    finally:
        await browser.close()
        logger.info("Session complete!")


async def multi_timeframe_analysis(ticker: str, config: dict):
    """
    Production Use Case #2: Multi-Timeframe AI Analysis
    Opens 3 tabs with Daily, 60min, 5min charts, captures screenshots, and performs
    comprehensive multi-timeframe AI analysis using Claude Vision
    """
    logger = logging.getLogger(__name__)
    logger.info(f"=" * 70)
    logger.info(f"MULTI-TIMEFRAME AI ANALYSIS: {ticker}")
    logger.info(f"=" * 70)

    # Load credentials
    username = os.getenv("STOCKCHARTS_USERNAME")
    password = os.getenv("STOCKCHARTS_PASSWORD")
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not all([username, password, api_key]):
        logger.error("Missing credentials in .env file")
        logger.error("Required: STOCKCHARTS_USERNAME, STOCKCHARTS_PASSWORD, ANTHROPIC_API_KEY")
        return

    # Initialize components
    browser = StockChartsController(
        username=username,
        password=password,
        headless=config.get("browser", {}).get("headless", False),
        screenshot_dir=os.getenv("SCREENSHOT_DIR", "screenshots"),
        config=config
    )

    ai_analyzer = ChartAnalyzer(
        api_key=api_key,
        model=config.get("ai_analysis", {}).get("model", "claude-sonnet-4-5-20250929"),
        max_tokens=config.get("ai_analysis", {}).get("max_tokens", 4096)
    )

    hybrid_service = HybridChartService(
        browser_controller=browser,
        ai_analyzer=ai_analyzer
    )

    try:
        # Initialize browser
        await browser.initialize()

        # Login
        logger.info("Logging in to StockCharts.com...")
        login_success = await browser.login()

        if not login_success:
            logger.error("Login failed")
            return

        logger.info("[SUCCESS] Login successful!\n")

        # Perform multi-timeframe analysis
        logger.info(f"Starting multi-timeframe analysis for {ticker}...")
        logger.info("This will:")
        logger.info("  1. Open tabs with Daily, Weekly, 60min, and 5min charts")
        logger.info("  2. Capture screenshots of all 4 timeframes")
        logger.info("  3. Analyze all charts together using Claude AI")
        logger.info("  4. Generate comprehensive multi-timeframe report\n")

        # Run the analysis
        result = await hybrid_service.analyze_ticker_multi_timeframe(ticker)

        if not result["success"]:
            logger.error(f"Analysis failed: {result.get('error', 'Unknown error')}")
            return

        # Generate and display report
        logger.info("\n" + "=" * 70)
        logger.info("ANALYSIS COMPLETE - GENERATING REPORT")
        logger.info("=" * 70 + "\n")

        report = hybrid_service.generate_report(ticker, multi_timeframe=True)
        print(report)

        # Save to file
        logger.info("\n" + "=" * 70)
        logger.info("Saving analysis to files...")

        saved_files = hybrid_service.save_analysis_to_file(ticker, multi_timeframe=True)

        if "error" not in saved_files:
            logger.info(f"[SUCCESS] Analysis saved:")
            logger.info(f"  JSON: {saved_files['json_path']}")
            logger.info(f"  TXT:  {saved_files['txt_path']}")

        logger.info("=" * 70)

        logger.info("\nScreenshots saved:")
        for timeframe, path in result["screenshots"].items():
            logger.info(f"  [{timeframe}] {path}")

    finally:
        await browser.close()
        logger.info("\nSession complete!")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Multi-Timeframe Chart Analysis for StockCharts.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # AI-powered analysis (default)
  python main.py --ticker AEIS

  # Manual viewing only (browser stays open)
  python main.py --ticker AEIS --mode viewer

  # AI analysis with debug logging
  python main.py --ticker AAPL --mode analysis --log-level DEBUG
        """
    )

    parser.add_argument(
        "--ticker",
        type=str,
        required=False,  # Not required for chartlist-batch mode
        help="Ticker symbol to analyze (e.g., AEIS, AAPL)"
    )

    parser.add_argument(
        "--mode",
        choices=["analysis", "viewer", "chartlist-batch"],
        default="analysis",
        help="Mode: 'analysis' = AI-powered analysis (default), 'viewer' = manual viewing only, 'chartlist-batch' = open charts from Excel"
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to Excel configuration file (required for chartlist-batch mode)"
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)"
    )

    args = parser.parse_args()

    # Setup
    setup_logging(args.log_level)
    load_dotenv(Path(__file__).parent / "config" / ".env")
    config = load_config()

    # Run appropriate mode
    if args.mode == "chartlist-batch":
        # ChartList batch mode requires Excel config file
        if not args.config:
            parser.error("--config is required for chartlist-batch mode")
        asyncio.run(chartlist_batch_viewer(args.config, config))
    else:
        # Other modes require ticker
        if not args.ticker:
            parser.error("--ticker is required for viewer and analysis modes")

        ticker = args.ticker.upper()

        if args.mode == "viewer":
            asyncio.run(multi_timeframe_viewer(ticker, config))
        else:  # analysis (default)
            asyncio.run(multi_timeframe_analysis(ticker, config))


async def chartlist_batch_viewer(excel_path: str, config: dict):
    """
    Production Use Case #2: ChartList Batch Viewer
    Opens multiple charts from different ChartLists in separate tabs based on Excel configuration
    """
    logger = logging.getLogger(__name__)
    logger.info(f"=" * 70)
    logger.info(f"CHARTLIST BATCH VIEWER")
    logger.info(f"=" * 70)

    # Load credentials
    username = os.getenv("STOCKCHARTS_USERNAME")
    password = os.getenv("STOCKCHARTS_PASSWORD")

    if not all([username, password]):
        logger.error("Missing credentials in .env file")
        logger.error("Required: STOCKCHARTS_USERNAME, STOCKCHARTS_PASSWORD")
        return

    # Check if Excel file exists
    excel_file = Path(excel_path)
    if not excel_file.exists():
        logger.error(f"Excel file not found: {excel_file}")
        logger.error("Create an Excel file with columns: ChartList, Ticker, TabOrder, TimeframeBox (optional), Notes (optional)")
        return

    # Initialize browser controller
    browser = StockChartsController(
        username=username,
        password=password,
        headless=False,  # Must be visible for manual inspection
        screenshot_dir=os.getenv("SCREENSHOT_DIR", "screenshots"),
        config=config
    )

    try:
        # Initialize browser
        await browser.initialize()

        # Login
        logger.info("Logging in to StockCharts.com...")
        login_success = await browser.login()

        if not login_success:
            logger.error("Login failed")
            return

        logger.info("[SUCCESS] Login successful!\n")

        # Open charts from Excel
        opened_tabs = await browser.open_charts_from_excel(excel_file)

        if opened_tabs:
            logger.info("\n" + "=" * 70)
            logger.info("BROWSER IS NOW OPEN IN KIOSK FULLSCREEN MODE")
            logger.info("=" * 70)
            logger.info("[KIOSK MODE] Browser using entire monitor (no taskbar/UI)")
            logger.info("[NAVIGATION] Switch between tabs: Ctrl+Tab or click tabs")
            logger.info("[EXIT] Use Alt+F4 to close browser (F11 disabled in kiosk)")
            logger.info("[ALTERNATIVE] Press Ctrl+C in this terminal to close")
            logger.info("=" * 70)

            # Wait for user to finish
            try:
                input()  # Try waiting for Enter key
            except (EOFError, OSError):
                # If input() fails (background/redirected mode), wait indefinitely
                logger.info("\n[Non-interactive mode detected]")
                logger.info("Browser will stay open until you:")
                logger.info("  1. Close the browser window manually, OR")
                logger.info("  2. Press Ctrl+C in this terminal")
                logger.info("Waiting...")
                try:
                    while True:
                        await asyncio.sleep(3600)  # Sleep in 1-hour chunks
                except KeyboardInterrupt:
                    logger.info("\nKeyboard interrupt received...")

            logger.info("\nClosing browser...")
        else:
            logger.error("No charts were opened successfully")

    finally:
        await browser.close()
        logger.info("Session complete!")


if __name__ == "__main__":
    main()
