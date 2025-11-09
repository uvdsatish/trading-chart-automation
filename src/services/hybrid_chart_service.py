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
            logger.info(f"[{ticker}] [SUCCESS] Hybrid analysis completed successfully")
            
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
    
    async def analyze_ticker_multi_timeframe(
        self,
        ticker: str,
        chartstyle_box_numbers: List[int] = [1, 4, 7, 10]
    ) -> Dict:
        """
        Complete multi-timeframe workflow: Open tabs, capture screenshots, AI analysis

        Args:
            ticker: Stock symbol to analyze
            chartstyle_box_numbers: Which ChartStyle boxes to use for timeframes
                                    Default [1, 4, 7, 10] = Daily, Weekly, 60min, 5min

        Returns:
            Dict: Multi-timeframe analysis with cross-timeframe insights
        """
        logger.info(f"Starting multi-timeframe analysis for {ticker}")

        result = {
            "ticker": ticker,
            "success": False,
            "timeframes": {},
            "screenshots": {},
            "multi_timeframe_analysis": None,
            "error": None
        }

        try:
            # Step 1: Open multi-timeframe tabs (Browser Automation)
            logger.info(f"[{ticker}] Step 1: Opening multi-timeframe tabs...")
            pages_dict = await self.browser.open_multi_timeframe_tabs(
                ticker=ticker,
                chartstyle_box_numbers=chartstyle_box_numbers
            )

            if not pages_dict:
                result["error"] = "Failed to open multi-timeframe tabs"
                return result

            # Step 2: Collect screenshot paths
            logger.info(f"[{ticker}] Step 2: Collecting screenshots...")
            screenshots = {}
            for timeframe, page_info in pages_dict.items():
                screenshot_path = page_info.get("screenshot_path")
                if screenshot_path:
                    screenshots[timeframe] = Path(screenshot_path)
                    result["screenshots"][timeframe] = str(screenshot_path)
                    logger.info(f"  [{timeframe}] Screenshot: {screenshot_path}")

            if not screenshots:
                result["error"] = "No screenshots captured"
                return result

            result["timeframes"] = list(screenshots.keys())

            # Step 3: Multi-Timeframe AI Analysis (Single API Call)
            logger.info(f"[{ticker}] Step 3: AI analyzing all timeframes together...")
            multi_analysis = await self.ai.analyze_multi_timeframe_chart(
                screenshots=screenshots,
                ticker=ticker
            )
            result["multi_timeframe_analysis"] = multi_analysis

            # Cache the result
            cache_key = f"{ticker}_multi_timeframe"
            self.analysis_cache[cache_key] = result

            result["success"] = True
            logger.info(f"[{ticker}] [SUCCESS] Multi-timeframe analysis completed")

            return result

        except Exception as e:
            logger.error(f"Error in multi-timeframe analysis for {ticker}: {e}")
            result["error"] = str(e)
            return result

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
    
    def generate_report(self, ticker: str, multi_timeframe: bool = False) -> str:
        """
        Generate human-readable report from cached analysis

        Args:
            ticker: Stock symbol
            multi_timeframe: Whether to generate multi-timeframe report

        Returns:
            str: Formatted report
        """
        # Check for multi-timeframe analysis
        cache_key = f"{ticker}_multi_timeframe" if multi_timeframe else ticker

        if cache_key not in self.analysis_cache:
            return f"No analysis available for {ticker}"

        analysis = self.analysis_cache[cache_key]

        # Multi-timeframe report
        if multi_timeframe:
            return self._generate_multi_timeframe_report(ticker, analysis)

        # Single-timeframe report (existing)
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

    def _generate_multi_timeframe_report(self, ticker: str, analysis: Dict) -> str:
        """Generate report for multi-timeframe analysis"""
        mtf = analysis.get("multi_timeframe_analysis", {})

        report_lines = [
            f"=" * 70,
            f"MULTI-TIMEFRAME ANALYSIS REPORT: {ticker}",
            f"=" * 70,
            ""
        ]

        # Timeframes analyzed
        timeframes = analysis.get("timeframes", [])
        report_lines.append(f"Timeframes Analyzed: {', '.join(timeframes)}")
        report_lines.append("")

        # Trend Alignment
        trend_align = mtf.get("trend_alignment", {})
        if trend_align:
            report_lines.extend([
                "TREND ALIGNMENT:",
                f"  Consensus: {trend_align.get('consensus', 'unknown').upper()}",
                f"  Strength: {trend_align.get('strength', 'unknown').upper()}",
                f"  Details: {trend_align.get('details', 'N/A')}",
                ""
            ])

            # Individual timeframe trends
            tf_trends = trend_align.get("timeframe_trends", {})
            if tf_trends:
                report_lines.append("  Individual Timeframe Trends:")
                for tf, trend in tf_trends.items():
                    report_lines.append(f"    {tf}: {trend}")
                report_lines.append("")

        # Confluence Levels
        confluence = mtf.get("confluence_levels", [])
        if confluence:
            report_lines.extend([
                "SUPPORT/RESISTANCE CONFLUENCE:",
            ])
            for level in confluence:
                price = level.get("price", 0)
                level_type = level.get("type", "unknown")
                timeframes_list = level.get("timeframes", [])
                significance = level.get("significance", "unknown")
                notes = level.get("notes", "")

                report_lines.append(
                    f"  ${price:.2f} ({level_type.upper()}) - "
                    f"Significance: {significance.upper()}"
                )
                report_lines.append(f"    Timeframes: {', '.join(timeframes_list)}")
                if notes:
                    report_lines.append(f"    Notes: {notes}")
            report_lines.append("")

        # Best Entry Timeframe
        best_entry = mtf.get("best_entry_timeframe", "unknown")
        best_entry_reason = mtf.get("best_entry_reasoning", "N/A")
        report_lines.extend([
            "BEST ENTRY TIMEFRAME:",
            f"  {best_entry}",
            f"  Reasoning: {best_entry_reason}",
            ""
        ])

        # Pattern Confirmation
        pattern_conf = mtf.get("pattern_confirmation", {})
        if pattern_conf:
            confirmed = pattern_conf.get("confirmed", False)
            details = pattern_conf.get("details", "N/A")
            strength = pattern_conf.get("pattern_strength", "unknown")

            report_lines.extend([
                "PATTERN CONFIRMATION:",
                f"  Confirmed: {'YES' if confirmed else 'NO'}",
                f"  Strength: {strength.upper()}",
                f"  Details: {details}",
                ""
            ])

        # Divergences
        divergences = mtf.get("divergences", [])
        if divergences:
            report_lines.extend([
                "DIVERGENCES & CONFLICTS:",
            ])
            for div in divergences:
                report_lines.append(f"  [WARN] {div}")
            report_lines.append("")

        # Recommended Alerts
        alerts = mtf.get("recommended_alerts", [])
        if alerts:
            report_lines.extend([
                "RECOMMENDED ALERTS (Multi-Timeframe Context):",
            ])
            for i, alert in enumerate(alerts, 1):
                price = alert.get("price", 0)
                alert_type = alert.get("type", "unknown")
                priority = alert.get("priority", "medium")
                reason = alert.get("reason", "N/A")
                supporting_tfs = alert.get("timeframes_supporting", [])

                report_lines.append(
                    f"  {i}. ${price:.2f} - {alert_type.upper()} "
                    f"({priority.upper()} priority)"
                )
                report_lines.append(f"     Reason: {reason}")
                if supporting_tfs:
                    report_lines.append(f"     Supporting Timeframes: {', '.join(supporting_tfs)}")
            report_lines.append("")

        # Multi-Timeframe Risk
        risk = mtf.get("multi_timeframe_risk", {})
        if risk:
            risk_level = risk.get("level", "unknown")
            risk_factors = risk.get("factors", [])
            confidence = risk.get("confidence", "unknown")

            report_lines.extend([
                f"MULTI-TIMEFRAME RISK: {risk_level.upper()}",
                f"  Confidence: {confidence.upper()}",
            ])
            if risk_factors:
                report_lines.append("  Risk Factors:")
                for factor in risk_factors:
                    report_lines.append(f"    - {factor}")
            report_lines.append("")

        # Trading Strategy
        strategy = mtf.get("trading_strategy", {})
        if strategy:
            approach = strategy.get("approach", "unknown")
            entry_strat = strategy.get("entry_strategy", "N/A")
            exit_strat = strategy.get("exit_strategy", "N/A")
            position_size = strategy.get("position_sizing", "N/A")

            report_lines.extend([
                "TRADING STRATEGY:",
                f"  Approach: {approach.upper()}",
                f"  Entry: {entry_strat}",
                f"  Exit: {exit_strat}",
                f"  Position Sizing: {position_size}",
                ""
            ])

        # Summary
        summary = mtf.get("summary", "")
        if summary:
            report_lines.extend([
                "SUMMARY:",
                f"  {summary}",
                ""
            ])

        report_lines.append("=" * 70)

        return "\n".join(report_lines)

    def save_analysis_to_file(self, ticker: str, output_dir: str = "analysis_results", multi_timeframe: bool = False) -> dict:
        """
        Save analysis results to both JSON and TXT files

        Args:
            ticker: Stock symbol
            output_dir: Directory to save output files
            multi_timeframe: Whether this is a multi-timeframe analysis

        Returns:
            dict: Paths to saved files
        """
        import json
        from pathlib import Path
        from datetime import datetime

        # Check for the appropriate cache key
        cache_key = ticker
        if not multi_timeframe and ticker not in self.analysis_cache:
            # Try checking for multi-timeframe version
            cache_key_mtf = f"{ticker}_multi_timeframe"
            if cache_key_mtf in self.analysis_cache:
                multi_timeframe = True
                cache_key = cache_key_mtf
            else:
                logger.error(f"No analysis available for {ticker}")
                return {"error": "No analysis available"}
        elif multi_timeframe:
            cache_key = f"{ticker}_multi_timeframe"
            if cache_key not in self.analysis_cache:
                logger.error(f"No multi-timeframe analysis available for {ticker}")
                return {"error": "No multi-timeframe analysis available"}

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # File paths
        analysis_type = "_mtf" if multi_timeframe else ""
        json_filename = f"{ticker}_analysis{analysis_type}_{timestamp}.json"
        txt_filename = f"{ticker}_report{analysis_type}_{timestamp}.txt"
        json_path = output_path / json_filename
        txt_path = output_path / txt_filename

        analysis = self.analysis_cache[cache_key]

        # Save JSON (complete data)
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved JSON analysis to: {json_path}")
        except Exception as e:
            logger.error(f"Failed to save JSON: {e}")

        # Save TXT report (human-readable)
        try:
            report = self.generate_report(ticker, multi_timeframe=multi_timeframe)

            # Add detailed AI analysis if available
            pattern_analysis = analysis.get("pattern_analysis", {})
            if "raw_analysis" in pattern_analysis:
                report += "\n\n" + "=" * 60
                report += "\nDETAILED AI ANALYSIS:\n"
                report += "=" * 60 + "\n"
                report += pattern_analysis.get("raw_analysis", "")

            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Saved text report to: {txt_path}")
        except Exception as e:
            logger.error(f"Failed to save text report: {e}")

        return {
            "json_path": str(json_path),
            "txt_path": str(txt_path),
            "ticker": ticker,
            "timestamp": timestamp
        }
