"""
POC Main Script - Hybrid Browser Automation for StockCharts.com

This demonstrates the hybrid approach:
1. Traditional automation (Playwright) for reliable chart access
2. AI analysis (Claude) for intelligent pattern recognition
3. Combined workflow for smart trading decisions

Usage:
    python main.py --mode single --ticker AAPL
    python main.py --mode batch --tickers AAPL MSFT GOOGL
    python main.py --mode compare --tickers SPY QQQ DIA
"""
import asyncio
import argparse
import logging
import sys
from pathlib import Path
from typing import List

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


async def demo_single_ticker(ticker: str, config: dict):
    """
    Demo: Analyze a single ticker with full hybrid workflow
    """
    logger = logging.getLogger(__name__)
    logger.info(f"=" * 70)
    logger.info(f"DEMO: Single Ticker Analysis - {ticker}")
    logger.info(f"=" * 70)
    
    # Load credentials
    username = os.getenv("STOCKCHARTS_USERNAME")
    password = os.getenv("STOCKCHARTS_PASSWORD")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not all([username, password, api_key]):
        logger.error("Missing credentials in .env file")
        return
    
    # Initialize components
    browser = StockChartsController(
        username=username,
        password=password,
        headless=os.getenv("HEADLESS", "false").lower() == "true",
        screenshot_dir=os.getenv("SCREENSHOT_DIR", "screenshots"),
        config=config
    )
    
    ai_analyzer = ChartAnalyzer(
        api_key=api_key,
        model=os.getenv("AI_MODEL", "claude-sonnet-4-5-20250929"),
        max_tokens=int(os.getenv("MAX_TOKENS", "4096"))
    )
    
    hybrid_service = HybridChartService(browser, ai_analyzer)
    
    try:
        # Initialize browser
        await browser.initialize()
        
        # Login
        logger.info("Logging in to StockCharts.com...")
        login_success = await browser.login()
        
        if not login_success:
            logger.error("Login failed. Please check credentials and try again.")
            return
        
        logger.info("✓ Login successful!")
        
        # Perform hybrid analysis
        logger.info(f"\nStarting hybrid analysis for {ticker}...")
        result = await hybrid_service.analyze_ticker_with_alerts(ticker)
        
        if result["success"]:
            logger.info(f"\n✓ Analysis completed successfully!")
            logger.info(f"Screenshot saved: {result['screenshot_path']}")
            
            # Generate and display report
            report = hybrid_service.generate_report(ticker)
            print("\n" + report)
            
            # Display AI insights
            pattern_analysis = result.get("pattern_analysis", {})
            if "raw_analysis" in pattern_analysis:
                print("\n" + "=" * 70)
                print("AI DETAILED ANALYSIS:")
                print("=" * 70)
                print(pattern_analysis.get("raw_analysis", "No detailed analysis"))
        else:
            logger.error(f"Analysis failed: {result.get('error')}")
        
    except Exception as e:
        logger.error(f"Error in demo: {e}", exc_info=True)
    finally:
        await browser.close()


async def demo_batch_analysis(tickers: List[str], config: dict):
    """
    Demo: Analyze multiple tickers in batch
    """
    logger = logging.getLogger(__name__)
    logger.info(f"=" * 70)
    logger.info(f"DEMO: Batch Analysis - {len(tickers)} tickers")
    logger.info(f"=" * 70)
    
    # Load credentials
    username = os.getenv("STOCKCHARTS_USERNAME")
    password = os.getenv("STOCKCHARTS_PASSWORD")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not all([username, password, api_key]):
        logger.error("Missing credentials in .env file")
        return
    
    # Initialize components
    browser = StockChartsController(
        username=username,
        password=password,
        headless=os.getenv("HEADLESS", "false").lower() == "true",
        screenshot_dir=os.getenv("SCREENSHOT_DIR", "screenshots"),
        config=config
    )
    
    ai_analyzer = ChartAnalyzer(
        api_key=api_key,
        model=os.getenv("AI_MODEL", "claude-sonnet-4-5-20250929")
    )
    
    hybrid_service = HybridChartService(browser, ai_analyzer)
    
    try:
        await browser.initialize()
        
        # Login
        if not await browser.login():
            logger.error("Login failed")
            return
        
        logger.info("✓ Login successful!")
        
        # Batch analysis
        logger.info(f"\nAnalyzing {len(tickers)} tickers...")
        results = await hybrid_service.batch_analyze_tickers(tickers, delay_between=3.0)
        
        # Summary
        successful = sum(1 for r in results.values() if r.get("success"))
        logger.info(f"\n✓ Batch analysis completed: {successful}/{len(tickers)} successful")
        
        # Generate reports
        for ticker in tickers:
            if results[ticker].get("success"):
                report = hybrid_service.generate_report(ticker)
                print("\n" + report)
        
    except Exception as e:
        logger.error(f"Error in batch demo: {e}", exc_info=True)
    finally:
        await browser.close()


async def demo_ticker_comparison(tickers: List[str], config: dict):
    """
    Demo: Compare multiple tickers
    """
    logger = logging.getLogger(__name__)
    logger.info(f"=" * 70)
    logger.info(f"DEMO: Ticker Comparison")
    logger.info(f"=" * 70)
    
    # Load credentials
    username = os.getenv("STOCKCHARTS_USERNAME")
    password = os.getenv("STOCKCHARTS_PASSWORD")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not all([username, password, api_key]):
        logger.error("Missing credentials in .env file")
        return
    
    # Initialize components
    browser = StockChartsController(
        username=username,
        password=password,
        headless=os.getenv("HEADLESS", "false").lower() == "true",
        screenshot_dir=os.getenv("SCREENSHOT_DIR", "screenshots"),
        config=config
    )
    
    ai_analyzer = ChartAnalyzer(api_key=api_key)
    hybrid_service = HybridChartService(browser, ai_analyzer)
    
    try:
        await browser.initialize()
        
        if not await browser.login():
            logger.error("Login failed")
            return
        
        logger.info("✓ Login successful!")
        
        # Compare tickers
        logger.info(f"\nComparing {len(tickers)} tickers...")
        comparison = await hybrid_service.compare_tickers(
            tickers,
            comparison_criteria=["trend_strength", "risk_level"]
        )
        
        # Display comparison results
        print("\n" + "=" * 70)
        print("TICKER COMPARISON RESULTS")
        print("=" * 70)
        
        if "trend_strength" in comparison.get("rankings", {}):
            print("\nRANKED BY TREND STRENGTH:")
            for i, (ticker, strength) in enumerate(comparison["rankings"]["trend_strength"], 1):
                print(f"  {i}. {ticker}: {strength}/10")
        
        if "risk_level" in comparison.get("rankings", {}):
            print("\nRANKED BY RISK (LOW TO HIGH):")
            for i, (ticker, risk_score) in enumerate(comparison["rankings"]["risk_level"], 1):
                risk_names = {1: "LOW", 2: "MEDIUM", 3: "HIGH"}
                print(f"  {i}. {ticker}: {risk_names.get(risk_score, 'UNKNOWN')}")
        
    except Exception as e:
        logger.error(f"Error in comparison demo: {e}", exc_info=True)
    finally:
        await browser.close()


async def demo_interactive_mode(config: dict):
    """
    Demo: Interactive mode for testing
    """
    logger = logging.getLogger(__name__)
    
    # Load credentials
    username = os.getenv("STOCKCHARTS_USERNAME")
    password = os.getenv("STOCKCHARTS_PASSWORD")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not all([username, password, api_key]):
        logger.error("Missing credentials in .env file")
        return
    
    browser = StockChartsController(
        username=username,
        password=password,
        headless=False,  # Always show browser in interactive mode
        screenshot_dir=os.getenv("SCREENSHOT_DIR", "screenshots"),
        config=config
    )
    
    ai_analyzer = ChartAnalyzer(api_key=api_key)
    hybrid_service = HybridChartService(browser, ai_analyzer)
    
    try:
        await browser.initialize()
        
        if not await browser.login():
            logger.error("Login failed")
            return
        
        logger.info("✓ Login successful!")
        print("\n" + "=" * 70)
        print("INTERACTIVE MODE")
        print("=" * 70)
        print("Commands:")
        print("  analyze <TICKER>  - Analyze a ticker")
        print("  batch <TICK1> <TICK2> ... - Batch analyze")
        print("  compare <TICK1> <TICK2> ... - Compare tickers")
        print("  quit - Exit")
        print("=" * 70 + "\n")
        
        while True:
            try:
                cmd = input(">>> ").strip()
                
                if not cmd:
                    continue
                
                if cmd.lower() == "quit":
                    break
                
                parts = cmd.split()
                command = parts[0].lower()
                args = parts[1:]
                
                if command == "analyze" and args:
                    ticker = args[0].upper()
                    result = await hybrid_service.analyze_ticker_with_alerts(ticker)
                    if result["success"]:
                        print(hybrid_service.generate_report(ticker))
                
                elif command == "batch" and args:
                    tickers = [t.upper() for t in args]
                    await hybrid_service.batch_analyze_tickers(tickers)
                    for ticker in tickers:
                        print(hybrid_service.generate_report(ticker))
                
                elif command == "compare" and args:
                    tickers = [t.upper() for t in args]
                    comparison = await hybrid_service.compare_tickers(
                        tickers,
                        comparison_criteria=["trend_strength", "risk_level"]
                    )
                    print("\nComparison completed - see logs for details")
                
                else:
                    print("Unknown command or missing arguments")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error: {e}")
        
    finally:
        await browser.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="POC: Hybrid Browser Automation for StockCharts.com"
    )
    
    parser.add_argument(
        "--mode",
        choices=["single", "batch", "compare", "interactive"],
        default="single",
        help="Demo mode to run"
    )
    
    parser.add_argument(
        "--ticker",
        type=str,
        help="Ticker symbol for single mode (e.g., AAPL)"
    )
    
    parser.add_argument(
        "--tickers",
        nargs="+",
        help="Multiple ticker symbols for batch/compare mode"
    )
    
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Setup
    setup_logging(args.log_level)
    load_dotenv(Path(__file__).parent / "config" / ".env")
    config = load_config()
    
    # Run appropriate demo
    if args.mode == "single":
        ticker = args.ticker or config.get("poc_test_tickers", ["AAPL"])[0]
        asyncio.run(demo_single_ticker(ticker, config))
    
    elif args.mode == "batch":
        tickers = args.tickers or config.get("poc_test_tickers", ["AAPL", "MSFT", "SPY"])
        asyncio.run(demo_batch_analysis(tickers, config))
    
    elif args.mode == "compare":
        tickers = args.tickers or ["SPY", "QQQ", "DIA"]
        asyncio.run(demo_ticker_comparison(tickers, config))
    
    elif args.mode == "interactive":
        asyncio.run(demo_interactive_mode(config))


if __name__ == "__main__":
    main()
