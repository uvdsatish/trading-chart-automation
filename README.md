# POC: Hybrid Browser Automation for StockCharts.com

## Overview

This Proof of Concept demonstrates a **hybrid approach** to chart automation that combines:

1. **Traditional Browser Automation (Playwright)** - Fast, reliable navigation and interaction
2. **AI Analysis (Claude Vision)** - Intelligent pattern recognition and decision-making
3. **Orchestration Service** - Combines both for smart trading workflows

## Why Hybrid?

| Task | Traditional Automation | AI Agent |
|------|----------------------|----------|
| Navigate to chart | ✅ Fast & Reliable | ❌ Slow & Expensive |
| Capture screenshot | ✅ Perfect accuracy | ❌ Not needed |
| Identify chart patterns | ❌ Hard to code | ✅ Excellent |
| Read indicator values | ⚠️ Requires OCR | ✅ Natural |
| Place alerts | ✅ Precise control | ❌ Unreliable |
| Make recommendations | ❌ Rule-based only | ✅ Contextual |

**Result**: Use the right tool for each job!

## Project Structure

```
poc_browser_automation/
├── src/
│   ├── browser/
│   │   └── stockcharts_controller.py    # Playwright automation
│   ├── ai/
│   │   └── chart_analyzer.py            # Claude vision analysis
│   └── services/
│       └── hybrid_chart_service.py      # Orchestration
├── config/
│   ├── .env.example                     # Template for credentials
│   └── settings.yaml                    # Configuration
├── screenshots/                          # Auto-generated screenshots
├── main.py                              # Entry point with demos
├── requirements.txt                     # Dependencies
└── README.md                            # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- StockCharts.com account (with valid subscription)
- Anthropic API key (for Claude)

### 2. Installation

```bash
# Clone or navigate to project directory
cd poc_browser_automation

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 3. Configuration

```bash
# Copy environment template
cp config/.env.example config/.env

# Edit .env file with your credentials
nano config/.env  # or use your preferred editor
```

**Required in `.env`:**
```bash
STOCKCHARTS_USERNAME=your_username
STOCKCHARTS_PASSWORD=your_password
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Optional settings
HEADLESS=false           # Set to true to hide browser
SCREENSHOT_DIR=screenshots
AI_MODEL=claude-sonnet-4-5-20250929
MAX_TOKENS=4096
LOG_LEVEL=INFO
```

### 4. Test Configuration

```bash
# Test that everything is set up correctly
python main.py --mode single --ticker AAPL
```

## Usage Examples

### Single Ticker Analysis

Analyze one ticker with full AI insights:

```bash
python main.py --mode single --ticker AAPL
```

**What happens:**
1. Logs into StockCharts.com
2. Navigates to AAPL chart
3. Captures screenshot
4. AI analyzes patterns, trends, support/resistance
5. AI recommends alert levels
6. Generates comprehensive report

**Output:**
```
==============================================================
CHART ANALYSIS REPORT: AAPL
==============================================================

CHART PATTERNS:
  Identified: ascending triangle, bullish flag

TREND ANALYSIS:
  Direction: uptrend
  Strength: 8/10

KEY LEVELS:
  Support: $148.50, $145.00, $142.25
  Resistance: $155.00, $158.75, $162.00

RISK LEVEL: MEDIUM

TECHNICAL INDICATORS:
  Recommendation: BUY
  Confidence: HIGH

RECOMMENDED ALERTS:
  1. $155.00 - breakout (high priority)
     Reason: Major resistance level from previous highs
  2. $148.50 - breakdown (medium priority)
     Reason: Key support confluence with 50-day MA
```

### Batch Analysis

Analyze multiple tickers:

```bash
python main.py --mode batch --tickers AAPL MSFT GOOGL TSLA
```

**Use case:** Daily watchlist analysis

### Ticker Comparison

Compare tickers and rank them:

```bash
python main.py --mode compare --tickers SPY QQQ DIA IWM
```

**Output includes:**
- Ranked by trend strength
- Ranked by risk level
- Individual analysis for each

### Interactive Mode

Explore interactively:

```bash
python main.py --mode interactive
```

**Commands:**
```
>>> analyze AAPL
>>> batch MSFT GOOGL AMZN
>>> compare SPY QQQ DIA
>>> quit
```

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  HYBRID WORKFLOW                        │
└─────────────────────────────────────────────────────────┘

1. NAVIGATION (Playwright)
   ├─ Login to StockCharts.com
   ├─ Navigate to ticker chart
   └─ Wait for chart to load
         │
         v
2. CAPTURE (Playwright)
   ├─ Take full screenshot
   └─ Save to screenshots/AAPL_20241101_143022.png
         │
         v
3. AI ANALYSIS (Claude Vision)
   ├─ Identify chart patterns
   ├─ Analyze trend direction & strength
   ├─ Find support/resistance levels
   └─ Recommend alert levels
         │
         v
4. REPORTING (Service Layer)
   ├─ Generate structured report
   ├─ Cache analysis results
   └─ Display to user
         │
         v
5. OPTIONAL: SET ALERTS (Playwright)
   └─ Use AI recommendations to place actual alerts
```

## Configuration Options

### StockCharts Selectors

If StockCharts.com changes their UI, update selectors in `config/settings.yaml`:

```yaml
stockcharts:
  selectors:
    username_field: "input[name='username']"
    password_field: "input[name='password']"
    login_button: "button[type='submit']"
    chart_container: ".chart-image"
```

### AI Prompts

Customize AI analysis by editing prompts in `config/settings.yaml`:

```yaml
ai_analysis:
  prompts:
    chart_pattern_detection: |
      Analyze this chart and identify:
      1. Chart patterns
      2. Trend analysis
      ...
```

## Troubleshooting

### Login Issues

**Problem:** Login fails or doesn't detect success

**Solutions:**
1. Check credentials in `.env` file
2. Verify StockCharts.com account is active
3. Check `screenshots/debug_*.png` to see what the automation sees
4. Update selectors in `settings.yaml` if UI changed

### Screenshot Issues

**Problem:** Screenshots are black or incomplete

**Solutions:**
1. Increase wait time after navigation
2. Set `HEADLESS=false` to see what's happening
3. Check if chart requires interaction to load

### AI Analysis Issues

**Problem:** AI returns empty or poor analysis

**Solutions:**
1. Ensure screenshot clearly shows chart
2. Check API key is valid
3. Review AI prompt in settings.yaml
4. Increase MAX_TOKENS if analysis is cut off

## Development Guide

### Adding New Features

**Example: Add Volume Analysis**

1. **Update AI Prompt** (`config/settings.yaml`):
```yaml
ai_analysis:
  prompts:
    volume_analysis: |
      Analyze volume patterns in this chart:
      - Volume trend
      - Volume spikes
      - Volume divergences
```

2. **Add Analyzer Method** (`src/ai/chart_analyzer.py`):
```python
async def analyze_volume(self, image_path: Path, ticker: str) -> Dict:
    # Implementation
    pass
```

3. **Update Service** (`src/services/hybrid_chart_service.py`):
```python
async def analyze_ticker_with_alerts(self, ticker: str):
    # ... existing code ...
    
    # Add volume analysis
    volume_analysis = await self.ai.analyze_volume(screenshot_path, ticker)
    result["volume_analysis"] = volume_analysis
```

### Testing

Create test file `tests/test_poc.py`:

```python
import pytest
from src.browser.stockcharts_controller import StockChartsController

@pytest.mark.asyncio
async def test_login():
    controller = StockChartsController("test", "test", headless=True)
    await controller.initialize()
    # Test logic
    await controller.close()
```

Run tests:
```bash
pytest tests/
```

## Performance Metrics

Based on POC testing:

| Operation | Time (avg) | Notes |
|-----------|-----------|-------|
| Browser initialization | 3-5s | One-time per session |
| Login | 5-8s | One-time per session |
| Navigate to chart | 3-5s | Per ticker |
| Capture screenshot | 1-2s | Per ticker |
| AI pattern analysis | 8-15s | Per ticker |
| AI indicator analysis | 8-15s | Per ticker |
| AI alert recommendations | 8-15s | Per ticker |
| **Total per ticker** | **30-50s** | Including all AI analysis |

**Batch mode**: ~45s per ticker (sequential) with 2s delay between tickers

## Cost Estimation

### AI API Costs (Anthropic Claude)

Assuming Claude Sonnet 4.5 pricing:
- Input: ~$3 per million tokens
- Output: ~$15 per million tokens

**Per ticker analysis:**
- Input: ~2,000 tokens (image + prompt) = $0.006
- Output: ~500 tokens (analysis) = $0.0075
- **Total: ~$0.014 per ticker**

**Daily watchlist (20 tickers):** ~$0.28/day or ~$8.40/month

## Next Steps

### Phase 2 Features (Future POC Extensions)

1. **Actually Set Alerts**
   - Implement alert placement in StockCharts UI
   - Test alert triggers and notifications

2. **Real-time Monitoring**
   - Periodic chart refresh
   - Alert on pattern changes
   - Intraday tracking

3. **Multi-Platform Support**
   - TradingView integration
   - ThinkorSwim automation
   - Custom broker platforms

4. **Advanced AI Features**
   - Historical pattern matching
   - Multi-timeframe analysis
   - Sentiment integration

5. **Integration with Trading Platform**
   - Connect to your main trading system
   - Automatic strategy execution
   - Portfolio tracking

## Security Notes

- **Never commit `.env` file** to version control
- Store credentials securely (consider using password managers)
- Use environment variables in production
- API keys should have minimal required permissions
- Consider using OAuth where available

## Support

For issues or questions:
1. Check `poc_automation.log` for detailed logs
2. Review screenshots in `screenshots/` directory
3. Test with `--log-level DEBUG` for verbose output
4. Review Playwright and Anthropic documentation

## License

This is a POC for personal/educational use. Ensure compliance with:
- StockCharts.com Terms of Service
- Anthropic API Terms of Use
- Securities regulations in your jurisdiction

---

## Quick Start Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Playwright browsers installed (`playwright install chromium`)
- [ ] `.env` file configured with credentials
- [ ] StockCharts.com account verified
- [ ] Anthropic API key tested
- [ ] First test run successful (`python main.py --mode single --ticker AAPL`)

**Ready to trade smarter! 🚀📈**
