"""
AI-Powered Chart Analyzer
Uses Claude's vision capabilities to analyze chart screenshots
"""
import base64
import json
import logging
from pathlib import Path
from typing import Dict, Optional, List
import anthropic

logger = logging.getLogger(__name__)


class ChartAnalyzer:
    """Uses Claude AI to analyze stock charts visually"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-5-20250929",
        max_tokens: int = 4096
    ):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
    
    def _encode_image(self, image_path: Path) -> str:
        """Encode image to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.standard_b64encode(image_file.read()).decode("utf-8")
    
    def _get_media_type(self, image_path: Path) -> str:
        """Determine media type from file extension"""
        extension = image_path.suffix.lower()
        media_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }
        return media_types.get(extension, "image/png")
    
    async def analyze_chart_patterns(
        self,
        image_path: Path,
        ticker: str,
        additional_context: Optional[str] = None
    ) -> Dict:
        """
        Analyze chart for technical patterns, support/resistance, and trends
        
        Args:
            image_path: Path to chart screenshot
            ticker: Stock symbol for context
            additional_context: Extra information to provide to AI
            
        Returns:
            Dict: Analysis results with patterns, levels, and recommendations
        """
        logger.info(f"Analyzing chart patterns for {ticker}...")
        
        try:
            # Encode image
            image_data = self._encode_image(image_path)
            media_type = self._get_media_type(image_path)
            
            # Construct prompt
            prompt = self._build_pattern_analysis_prompt(ticker, additional_context)
            
            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )
            
            # Parse response
            response_text = message.content[0].text
            logger.debug(f"Raw AI response: {response_text}")
            
            # Try to extract JSON if present
            analysis = self._parse_analysis_response(response_text)
            
            logger.info(f"Chart analysis completed for {ticker}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing chart: {e}")
            return {
                "error": str(e),
                "ticker": ticker,
                "patterns": [],
                "trend": {"direction": "unknown", "strength": 0},
                "support_levels": [],
                "resistance_levels": [],
                "recommended_alerts": [],
                "risk_level": "unknown"
            }
    
    async def analyze_technical_indicators(
        self,
        image_path: Path,
        ticker: str,
        indicators_present: Optional[List[str]] = None
    ) -> Dict:
        """
        Analyze technical indicators visible in chart
        
        Args:
            image_path: Path to chart screenshot
            ticker: Stock symbol
            indicators_present: List of indicators known to be in chart
            
        Returns:
            Dict: Analysis of technical indicators
        """
        logger.info(f"Analyzing technical indicators for {ticker}...")
        
        try:
            image_data = self._encode_image(image_path)
            media_type = self._get_media_type(image_path)
            
            prompt = self._build_indicator_analysis_prompt(ticker, indicators_present)
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )
            
            response_text = message.content[0].text
            
            analysis = {
                "ticker": ticker,
                "indicators": {},
                "recommendation": "hold",
                "confidence": "medium",
                "raw_analysis": response_text
            }
            
            # Parse indicator analysis
            if "RSI" in response_text.upper():
                analysis["indicators"]["rsi"] = self._extract_rsi_info(response_text)
            
            if "MACD" in response_text.upper():
                analysis["indicators"]["macd"] = self._extract_macd_info(response_text)
            
            # Extract recommendation
            if "buy" in response_text.lower():
                analysis["recommendation"] = "buy"
            elif "sell" in response_text.lower():
                analysis["recommendation"] = "sell"
            
            logger.info(f"Indicator analysis completed for {ticker}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing indicators: {e}")
            return {
                "error": str(e),
                "ticker": ticker,
                "indicators": {},
                "recommendation": "hold",
                "confidence": "low"
            }
    
    async def get_alert_recommendations(
        self,
        image_path: Path,
        ticker: str,
        current_price: Optional[float] = None
    ) -> List[Dict]:
        """
        Get AI-recommended alert levels based on chart analysis
        
        Args:
            image_path: Path to chart screenshot
            ticker: Stock symbol
            current_price: Current stock price if known
            
        Returns:
            List[Dict]: Recommended alerts with prices and reasons
        """
        logger.info(f"Getting alert recommendations for {ticker}...")
        
        try:
            image_data = self._encode_image(image_path)
            media_type = self._get_media_type(image_path)
            
            price_context = f"Current price: ${current_price}" if current_price else ""
            
            prompt = f"""
            Analyze this stock chart for {ticker} and recommend specific price alert levels.
            {price_context}
            
            For each recommended alert, provide:
            1. Price level (be specific)
            2. Alert type (breakout, breakdown, support test, resistance test)
            3. Reasoning (why this level is significant)
            4. Priority (high/medium/low)
            
            Recommend 3-5 most important alert levels.
            
            Format as JSON array:
            [
                {{
                    "price": 150.25,
                    "type": "resistance_breakout",
                    "reason": "Major resistance from previous highs",
                    "priority": "high"
                }},
                ...
            ]
            """
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )
            
            response_text = message.content[0].text
            
            # Try to parse JSON array
            alerts = self._parse_alerts_response(response_text)
            
            logger.info(f"Generated {len(alerts)} alert recommendations for {ticker}")
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting alert recommendations: {e}")
            return []
    
    def _build_pattern_analysis_prompt(
        self,
        ticker: str,
        additional_context: Optional[str] = None
    ) -> str:
        """Build prompt for pattern analysis"""
        base_prompt = f"""
        Analyze this stock chart for {ticker} and provide a comprehensive technical analysis.
        
        Please identify and analyze:
        
        1. **Chart Patterns**: Identify any technical patterns such as:
           - Triangles (ascending, descending, symmetrical)
           - Head and Shoulders (regular or inverse)
           - Double/Triple Tops or Bottoms
           - Flags and Pennants
           - Wedges
           - Channels
        
        2. **Trend Analysis**:
           - Current trend direction (uptrend, downtrend, sideways)
           - Trend strength (rate 1-10, where 10 is strongest)
           - Potential trend changes or exhaustion signs
        
        3. **Support and Resistance Levels**:
           - Identify 2-3 key support levels (with approximate prices)
           - Identify 2-3 key resistance levels (with approximate prices)
        
        4. **Alert Recommendations**:
           - Suggest 3-5 price levels for alerts
           - Explain why each level is significant
        
        5. **Risk Assessment**:
           - Overall risk level (low/medium/high)
           - Key risk factors
        
        {additional_context or ""}
        
        Please format your response as JSON with this structure:
        {{
            "patterns": ["pattern1", "pattern2"],
            "trend": {{
                "direction": "uptrend|downtrend|sideways",
                "strength": 7,
                "notes": "explanation"
            }},
            "support_levels": [150.25, 148.50, 145.00],
            "resistance_levels": [155.00, 158.75, 162.00],
            "recommended_alerts": [
                {{
                    "price": 155.00,
                    "type": "breakout",
                    "reason": "Major resistance level"
                }}
            ],
            "risk_level": "medium",
            "summary": "Overall market assessment"
        }}
        """
        return base_prompt
    
    def _build_indicator_analysis_prompt(
        self,
        ticker: str,
        indicators_present: Optional[List[str]] = None
    ) -> str:
        """Build prompt for indicator analysis"""
        indicators_text = ""
        if indicators_present:
            indicators_text = f"Focus on these indicators: {', '.join(indicators_present)}"
        
        prompt = f"""
        Analyze the technical indicators visible in this chart for {ticker}.
        {indicators_text}
        
        For each visible indicator, provide:
        1. Current reading/value
        2. Interpretation (bullish/bearish/neutral)
        3. Signal strength
        
        Common indicators to look for:
        - RSI (Relative Strength Index)
        - MACD (Moving Average Convergence Divergence)
        - Moving Averages (50-day, 200-day)
        - Volume
        - Bollinger Bands
        - Stochastic
        
        Provide:
        - Overall signal (buy/sell/hold)
        - Confidence level (high/medium/low)
        - Key observations
        - Conflicting signals if any
        
        Be specific about actual values you see in the chart.
        """
        return prompt
    
    def _parse_analysis_response(self, response_text: str) -> Dict:
        """Parse AI response and extract structured data"""
        # Try to find JSON in response
        try:
            # Look for JSON block
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning("Could not parse JSON from response")
        
        # Fallback: Create structure from text analysis
        return {
            "patterns": self._extract_patterns(response_text),
            "trend": self._extract_trend(response_text),
            "support_levels": self._extract_levels(response_text, "support"),
            "resistance_levels": self._extract_levels(response_text, "resistance"),
            "recommended_alerts": [],
            "risk_level": self._extract_risk_level(response_text),
            "raw_analysis": response_text
        }
    
    def _parse_alerts_response(self, response_text: str) -> List[Dict]:
        """Parse alert recommendations from response"""
        try:
            # Look for JSON array
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning("Could not parse alerts JSON")
        
        return []
    
    def _extract_patterns(self, text: str) -> List[str]:
        """Extract chart patterns from text"""
        patterns = []
        pattern_keywords = [
            "triangle", "head and shoulders", "double top", "double bottom",
            "flag", "pennant", "wedge", "channel"
        ]
        
        text_lower = text.lower()
        for keyword in pattern_keywords:
            if keyword in text_lower:
                patterns.append(keyword)
        
        return patterns
    
    def _extract_trend(self, text: str) -> Dict:
        """Extract trend information from text"""
        text_lower = text.lower()
        
        direction = "sideways"
        if "uptrend" in text_lower or "bullish" in text_lower:
            direction = "uptrend"
        elif "downtrend" in text_lower or "bearish" in text_lower:
            direction = "downtrend"
        
        # Try to extract strength
        strength = 5  # default medium
        if "strong" in text_lower:
            strength = 8
        elif "weak" in text_lower:
            strength = 3
        
        return {
            "direction": direction,
            "strength": strength,
            "notes": "Extracted from text analysis"
        }
    
    def _extract_levels(self, text: str, level_type: str) -> List[float]:
        """Extract support or resistance levels from text"""
        levels = []
        
        # Look for price patterns like $150.25 or 150.25
        import re
        price_pattern = r'\$?(\d{1,4}\.\d{2})'
        matches = re.findall(price_pattern, text)
        
        # Filter to reasonable stock prices (10-10000)
        for match in matches:
            try:
                price = float(match)
                if 10 <= price <= 10000:
                    levels.append(price)
            except ValueError:
                continue
        
        # Return unique values, limited to 3
        return sorted(list(set(levels)))[:3]
    
    def _extract_risk_level(self, text: str) -> str:
        """Extract risk assessment from text"""
        text_lower = text.lower()
        
        if "high risk" in text_lower:
            return "high"
        elif "low risk" in text_lower:
            return "low"
        else:
            return "medium"
    
    def _extract_rsi_info(self, text: str) -> Dict:
        """Extract RSI information from text"""
        import re
        
        # Look for RSI value
        rsi_pattern = r'RSI[:\s]+(\d{1,3})'
        match = re.search(rsi_pattern, text, re.IGNORECASE)
        
        rsi_value = None
        if match:
            rsi_value = int(match.group(1))
        
        interpretation = "neutral"
        if rsi_value:
            if rsi_value > 70:
                interpretation = "overbought"
            elif rsi_value < 30:
                interpretation = "oversold"
        
        return {
            "value": rsi_value,
            "interpretation": interpretation
        }
    
    def _extract_macd_info(self, text: str) -> Dict:
        """Extract MACD information from text"""
        text_lower = text.lower()
        
        signal = "neutral"
        if "bullish" in text_lower and "macd" in text_lower:
            signal = "bullish"
        elif "bearish" in text_lower and "macd" in text_lower:
            signal = "bearish"
        
        return {
            "signal": signal
        }
