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
from src.browser.browser_session_manager import BrowserSessionManager, WindowPositioner
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
        choices=["analysis", "viewer", "chartlist-batch", "chartlist-viewer", "parallel"],
        default="analysis",
        help="Mode: 'analysis' = AI-powered analysis (default), 'viewer' = manual viewing only, 'chartlist-batch' = open charts from Excel (Use Case 2), 'chartlist-viewer' = open ChartLists from Excel (Use Case 3), 'parallel' = run Use Cases 2 & 3 in parallel"
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to Excel configuration file (required for chartlist-batch mode)"
    )

    parser.add_argument(
        "--batch-config",
        type=str,
        help="Path to Excel file for ChartList Batch (Use Case 2) when using parallel mode"
    )

    parser.add_argument(
        "--viewer-config",
        type=str,
        help="Path to Excel file for ChartList Viewer (Use Case 3) when using parallel mode"
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
    if args.mode == "parallel":
        # Parallel mode - run Use Case 2 and 3 simultaneously
        if not args.batch_config and not args.viewer_config:
            parser.error("At least one of --batch-config or --viewer-config is required for parallel mode")
        asyncio.run(parallel_chartlist_execution(
            chartlist_batch_config=args.batch_config,
            chartlist_viewer_config=args.viewer_config,
            config=config
        ))
    elif args.mode == "chartlist-batch":
        # ChartList batch mode (Use Case 2) requires Excel config file
        if not args.config:
            parser.error("--config is required for chartlist-batch mode")
        asyncio.run(chartlist_batch_viewer(args.config, config))
    elif args.mode == "chartlist-viewer":
        # ChartList viewer mode (Use Case 3) requires Excel config file
        if not args.config:
            parser.error("--config is required for chartlist-viewer mode")
        asyncio.run(chartlist_viewer(args.config, config))
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


async def chartlist_viewer(excel_path: str, config: dict):
    """
    Production Use Case #3: ChartList Viewer
    Opens first chart from each ChartList in separate tabs based on Excel configuration
    """
    logger = logging.getLogger(__name__)
    logger.info(f"=" * 70)
    logger.info(f"CHARTLIST VIEWER (USE CASE #3)")
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
        logger.error("Create an Excel file with column: ChartList")
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

        # Open ChartLists from Excel
        opened_tabs = await browser.open_chartlists_as_tabs(excel_file)

        # Log result but keep browser open regardless
        if not opened_tabs:
            logger.warning("No ChartLists were opened successfully, but keeping browser open for inspection")

        # ALWAYS keep browser open for manual inspection
        logger.info("\n" + "=" * 70)
        logger.info("BROWSER IS NOW OPEN IN FULLSCREEN MODE")
        logger.info("=" * 70)
        logger.info("[NAVIGATION] Switch between tabs: Ctrl+Tab or click tabs")
        logger.info("[EXIT] Use Alt+F4 to close browser")
        logger.info("[ALTERNATIVE] Press Enter in this terminal to close")
        logger.info("=" * 70)

        if opened_tabs:
            logger.info(f"\n{len(opened_tabs)} tab(s) opened successfully")
        else:
            logger.info("\nNo tabs were opened, but browser is ready for manual inspection")

        # Wait for user to finish
        try:
            input("\nPress Enter when done viewing charts...")
        except (EOFError, OSError):
            logger.info("\n[Non-interactive mode detected]")
            logger.info("Browser will stay open until you:")
            logger.info("  1. Close the browser window manually, OR")
            logger.info("  2. Press Ctrl+C in this terminal")
            logger.info("Waiting...")
            try:
                while True:
                    await asyncio.sleep(3600)
            except KeyboardInterrupt:
                logger.info("\nKeyboard interrupt received...")

        logger.info("\nClosing browser...")

    finally:
        await browser.close()
        logger.info("Session complete!")


async def parallel_chartlist_execution(
    chartlist_batch_config: str = None,
    chartlist_viewer_config: str = None,
    config: dict = None
):
    """
    Execute Use Case #2 and Use Case #3 in parallel using separate browser instances

    Args:
        chartlist_batch_config: Excel file path for Use Case #2 (ChartList Batch)
        chartlist_viewer_config: Excel file path for Use Case #3 (ChartList Viewer)
        config: Configuration dictionary
    """
    logger = logging.getLogger(__name__)
    logger.info("=" * 70)
    logger.info("PARALLEL CHARTLIST EXECUTION")
    logger.info("=" * 70)

    # Load credentials
    username = os.getenv("STOCKCHARTS_USERNAME")
    password = os.getenv("STOCKCHARTS_PASSWORD")

    if not username or not password:
        logger.error("StockCharts credentials not found in environment")
        return

    # Create session manager
    session_manager = BrowserSessionManager()

    try:
        # Determine which sessions to create
        sessions_to_create = []
        tasks_to_run = []

        if chartlist_batch_config:
            sessions_to_create.append("batch")
            tasks_to_run.append({
                "session_id": "batch",
                "task_type": "chartlist-batch",
                "params": {"excel_path": chartlist_batch_config}
            })
            logger.info(f"[BATCH] Will run ChartList Batch Viewer with: {chartlist_batch_config}")

        if chartlist_viewer_config:
            sessions_to_create.append("viewer")
            tasks_to_run.append({
                "session_id": "viewer",
                "task_type": "chartlist-viewer",
                "params": {"excel_path": chartlist_viewer_config}
            })
            logger.info(f"[VIEWER] Will run ChartList Viewer with: {chartlist_viewer_config}")

        if not sessions_to_create:
            logger.error("No configuration files provided for parallel execution")
            return

        # Calculate window positions for split screen
        positions = WindowPositioner.get_split_screen_positions(
            len(sessions_to_create),
            monitor_width=1920,
            monitor_height=1080
        )

        # Create browser sessions
        logger.info(f"\nCreating {len(sessions_to_create)} browser sessions...")
        for i, session_id in enumerate(sessions_to_create):
            controller = await session_manager.create_session(
                session_id=session_id,
                username=username,
                password=password,
                headless=False,  # Use headed mode for viewing
                config=config,
                window_position=positions[i] if i < len(positions) else None
            )
            logger.info(f"[SESSION] Created session: {session_id}")

        # Initialize all sessions in parallel
        logger.info("\nInitializing browser sessions in parallel...")
        init_tasks = []
        for session_id in sessions_to_create:
            init_tasks.append(session_manager.initialize_session(session_id, auto_login=True))

        init_results = await asyncio.gather(*init_tasks, return_exceptions=True)

        # Check initialization results
        for session_id, result in zip(sessions_to_create, init_results):
            if isinstance(result, Exception):
                logger.error(f"[SESSION {session_id}] Initialization failed: {result}")
            elif result:
                logger.info(f"[SESSION {session_id}] Initialized and logged in successfully")
            else:
                logger.error(f"[SESSION {session_id}] Initialization failed")

        # Run tasks in parallel
        logger.info("\n" + "=" * 70)
        logger.info("RUNNING TASKS IN PARALLEL")
        logger.info("=" * 70)

        results = await session_manager.run_parallel_tasks(tasks_to_run)

        # Display results
        logger.info("\n" + "=" * 70)
        logger.info("PARALLEL EXECUTION RESULTS")
        logger.info("=" * 70)

        for session_id, result in results.items():
            if "error" in result:
                logger.error(f"[SESSION {session_id}] Error: {result['error']}")
            else:
                logger.info(f"[SESSION {session_id}] Success: {result}")

        # Keep browsers open for manual inspection
        logger.info("\n" + "=" * 70)
        logger.info("BROWSERS ARE NOW OPEN IN SPLIT-SCREEN MODE")
        logger.info("=" * 70)
        logger.info("[NAVIGATION] Switch between windows: Alt+Tab")
        logger.info("[NAVIGATION] Switch between tabs in each browser: Ctrl+Tab")
        logger.info("[EXIT] Close each browser with Alt+F4")
        logger.info("[ALTERNATIVE] Press Enter in this terminal to close all browsers")
        logger.info("=" * 70)

        # Wait for user to finish
        try:
            input("\nPress Enter when done viewing charts...")
        except (EOFError, OSError):
            logger.info("\n[Non-interactive mode detected]")
            logger.info("Browsers will stay open. Press Ctrl+C to close all.")
            try:
                while True:
                    await asyncio.sleep(3600)
            except KeyboardInterrupt:
                logger.info("\nKeyboard interrupt received...")

    except Exception as e:
        logger.error(f"Parallel execution failed: {e}", exc_info=True)

    finally:
        logger.info("\nClosing all browser sessions...")
        await session_manager.close_all_sessions()
        logger.info("All sessions closed!")


if __name__ == "__main__":
    main()
