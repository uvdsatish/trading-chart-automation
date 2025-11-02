"""
Hybrid Chart Service
Combines browser automation with AI analysis for intelligent chart management
"""
import asyncio
import logging
from typing import Dict, List, Optional
from pathlib import Path

from ..browser.stockcharts_controller import StockChartsController
from ..ai.chart_analyzer import ChartAnalyzer

logger = logging.getLogger(__name__)


class HybridChartService:
    """
    Orchestrates browser automation and AI analysis
    
    Workflow:
    1. Use browser automation to navigate and capture charts (fast, reliable)
    2. Use AI to analyze charts and make intelligent decisions (smart)
    3. Use browser automation to execute decisions (precise)
    """
    
    def __init__(
        self,
        browser_controller: StockChartsController,
        ai_analyzer: ChartAnalyzer
    ):
        self.browser = browser_controller
        self.ai = ai_analyzer
        self.analysis_cache: Dict[str, Dict] = {}
    
    async def analyze_ticker_with_alerts(
        self,
        ticker: str,
        capture_screenshot: bool = True,
        apply_alerts: bool = False
    ) -> Dict:
        """
        Complete workflow: Navigate, capture, analyze, recommend alerts
        
        Args:
            ticker: Stock symbol to analyze
            capture_screenshot: Whether to capture chart screenshot
            apply_alerts: Whether to actually set alerts (future feature)
            
        Returns:
            Dict: Complete analysis with recommendations
        """
        logger.info(f"Starting hybrid analysis for {ticker}")
        
        result = {
            "ticker": ticker,
            "success": False,
            "screenshot_path": None,
            "pattern_analysis": None,
            "indicator_analysis": None,
            "alert_recommendations": None,
            "error": None
        }
        
        try:
            # Step 1: Navigate to chart (Traditional Automation)
            logger.info(f"[{ticker}] Step 1: Navigating to chart...")
            nav_success = await self.browser.navigate_to_chart(ticker)
            
            if not nav_success:
                result["error"] = "Failed to navigate to chart"
                return result
            
            # Wait for chart to fully load
            await asyncio.sleep(3)
            
            # Step 2: Capture screenshot (Traditional Automation)
            logger.info(f"[{ticker}] Step 2: Capturing screenshot...")
            screenshot_path = await self.browser.capture_chart_screenshot(ticker)
            result["screenshot_path"] = str(screenshot_path)
            
            # Step 3: AI Analysis - Pattern Recognition
            logger.info(f"[{ticker}] Step 3: AI analyzing chart patterns...")
            pattern_analysis = await self.ai.analyze_chart_patterns(
                image_path=screenshot_path,
                ticker=ticker
            )
            result["pattern_analysis"] = pattern_analysis
            
            # Step 4: AI Analysis - Technical Indicators
            logger.info(f"[{ticker}] Step 4: AI analyzing technical indicators...")
            indicator_analysis = await self.ai.analyze_technical_indicators(
                image_path=screenshot_path,
                ticker=ticker
            )
            result["indicator_analysis"] = indicator_analysis
            
            # Step 5: AI Recommendations - Alert Levels
            logger.info(f"[{ticker}] Step 5: Getting AI alert recommendations...")
            alert_recommendations = await self.ai.get_alert_recommendations(
                image_path=screenshot_path,
                ticker=ticker
            )
            result["alert_recommendations"] = alert_recommendations
            
            # Cache analysis
            self.analysis_cache[ticker] = result
            
            result["success"] = True
            logger.info(f"[{ticker}] ✓ Hybrid analysis completed successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in hybrid analysis for {ticker}: {e}")
            result["error"] = str(e)
            return result
    
    async def batch_analyze_tickers(
        self,
        tickers: List[str],
        concurrent: bool = False,
        delay_between: float = 2.0
    ) -> Dict[str, Dict]:
        """
        Analyze multiple tickers
        
        Args:
            tickers: List of stock symbols
            concurrent: Whether to analyze concurrently (not recommended for POC)
            delay_between: Delay between tickers in seconds
            
        Returns:
            Dict: Results keyed by ticker
        """
        logger.info(f"Starting batch analysis of {len(tickers)} tickers")
        
        results = {}
        
        if concurrent:
            # Concurrent analysis (advanced - may overwhelm browser)
            tasks = [
                self.analyze_ticker_with_alerts(ticker)
                for ticker in tickers
            ]
            completed = await asyncio.gather(*tasks, return_exceptions=True)
            
            for ticker, result in zip(tickers, completed):
                if isinstance(result, Exception):
                    results[ticker] = {"error": str(result), "success": False}
                else:
                    results[ticker] = result
        else:
            # Sequential analysis (safer for POC)
            for ticker in tickers:
                result = await self.analyze_ticker_with_alerts(ticker)
                results[ticker] = result
                
                # Delay between requests
                if ticker != tickers[-1]:  # Don't delay after last ticker
                    await asyncio.sleep(delay_between)
        
        logger.info(f"Batch analysis completed: {len(results)} tickers processed")
        return results
    
    async def compare_tickers(
        self,
        tickers: List[str],
        comparison_criteria: Optional[List[str]] = None
    ) -> Dict:
        """
        Analyze and compare multiple tickers
        
        Args:
            tickers: List of stock symbols to compare
            comparison_criteria: What to compare (trend_strength, risk_level, etc.)
            
        Returns:
            Dict: Comparison results
        """
        logger.info(f"Comparing {len(tickers)} tickers...")
        
        # Analyze all tickers
        analyses = await self.batch_analyze_tickers(tickers)
        
        # Extract comparison data
        comparison = {
            "tickers": tickers,
            "analyses": analyses,
            "rankings": {}
        }
        
        # Rank by trend strength
        if "trend_strength" in (comparison_criteria or []):
            trend_strengths = {}
            for ticker, analysis in analyses.items():
                if analysis.get("success") and analysis.get("pattern_analysis"):
                    strength = analysis["pattern_analysis"].get("trend", {}).get("strength", 0)
                    trend_strengths[ticker] = strength
            
            comparison["rankings"]["trend_strength"] = sorted(
                trend_strengths.items(),
                key=lambda x: x[1],
                reverse=True
            )
        
        # Rank by risk level
        if "risk_level" in (comparison_criteria or []):
            risk_scores = {"low": 1, "medium": 2, "high": 3}
            risk_levels = {}
            for ticker, analysis in analyses.items():
                if analysis.get("success") and analysis.get("pattern_analysis"):
                    risk = analysis["pattern_analysis"].get("risk_level", "medium")
                    risk_levels[ticker] = risk_scores.get(risk, 2)
            
            comparison["rankings"]["risk_level"] = sorted(
                risk_levels.items(),
                key=lambda x: x[1]
            )
        
        return comparison
    
    async def monitor_ticker_with_updates(
        self,
        ticker: str,
        check_interval: int = 300,
        duration: int = 3600
    ):
        """
        Monitor ticker with periodic updates
        
        Args:
            ticker: Stock symbol to monitor
            check_interval: How often to check (seconds)
            duration: How long to monitor (seconds)
            
        This is useful for intraday monitoring
        """
        logger.info(f"Starting monitoring of {ticker} for {duration}s")
        
        start_time = asyncio.get_event_loop().time()
        check_count = 0
        
        while (asyncio.get_event_loop().time() - start_time) < duration:
            check_count += 1
            logger.info(f"[{ticker}] Check #{check_count}")
            
            # Perform analysis
            analysis = await self.analyze_ticker_with_alerts(ticker)
            
            # Log key findings
            if analysis["success"]:
                patterns = analysis.get("pattern_analysis", {}).get("patterns", [])
                trend = analysis.get("pattern_analysis", {}).get("trend", {})
                
                logger.info(f"[{ticker}] Patterns: {patterns}")
                logger.info(f"[{ticker}] Trend: {trend.get('direction')} (strength: {trend.get('strength')})")
            
            # Wait for next check
            await asyncio.sleep(check_interval)
        
        logger.info(f"Monitoring completed: {check_count} checks performed")
    
    def generate_report(self, ticker: str) -> str:
        """
        Generate human-readable report from cached analysis
        
        Args:
            ticker: Stock symbol
            
        Returns:
            str: Formatted report
        """
        if ticker not in self.analysis_cache:
            return f"No analysis available for {ticker}"
        
        analysis = self.analysis_cache[ticker]
        
        report_lines = [
            f"=" * 60,
            f"CHART ANALYSIS REPORT: {ticker}",
            f"=" * 60,
            ""
        ]
        
        # Pattern Analysis
        pattern_data = analysis.get("pattern_analysis", {})
        if pattern_data and not pattern_data.get("error"):
            report_lines.extend([
                "CHART PATTERNS:",
                f"  Identified: {', '.join(pattern_data.get('patterns', ['None']))}",
                "",
                "TREND ANALYSIS:",
                f"  Direction: {pattern_data.get('trend', {}).get('direction', 'unknown')}",
                f"  Strength: {pattern_data.get('trend', {}).get('strength', 0)}/10",
                "",
                "KEY LEVELS:",
                f"  Support: {', '.join(f'${x:.2f}' for x in pattern_data.get('support_levels', []))}",
                f"  Resistance: {', '.join(f'${x:.2f}' for x in pattern_data.get('resistance_levels', []))}",
                "",
                f"RISK LEVEL: {pattern_data.get('risk_level', 'unknown').upper()}",
                ""
            ])
        
        # Indicator Analysis
        indicator_data = analysis.get("indicator_analysis", {})
        if indicator_data and not indicator_data.get("error"):
            report_lines.extend([
                "TECHNICAL INDICATORS:",
                f"  Recommendation: {indicator_data.get('recommendation', 'hold').upper()}",
                f"  Confidence: {indicator_data.get('confidence', 'medium').upper()}",
                ""
            ])
        
        # Alert Recommendations
        alerts = analysis.get("alert_recommendations", [])
        if alerts:
            report_lines.extend([
                "RECOMMENDED ALERTS:",
            ])
            for i, alert in enumerate(alerts, 1):
                report_lines.append(
                    f"  {i}. ${alert.get('price', 0):.2f} - "
                    f"{alert.get('type', 'unknown')} "
                    f"({alert.get('priority', 'medium')} priority)"
                )
                report_lines.append(f"     Reason: {alert.get('reason', 'N/A')}")
            report_lines.append("")
        
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
