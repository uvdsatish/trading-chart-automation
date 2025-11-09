# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## **CRITICAL CODING RULES**

### ❌ NO UNICODE CHARACTERS IN CODE
**NEVER use Unicode characters in Python code, log messages, or console output.**

Windows PowerShell/Command Prompt uses cp1252 encoding which cannot display Unicode characters, causing `UnicodeEncodeError` crashes.

**Forbidden characters:**
- ✓ ✗ ⚠ 📸 (checkmarks, warnings, emojis)
- Any non-ASCII characters in logging output

**Use instead:**
- `[SUCCESS]`, `[OK]`, `[PASS]` instead of ✓
- `[ERROR]`, `[FAIL]` instead of ✗
- `[WARN]`, `[WARNING]` instead of ⚠
- `[SCREENSHOT]`, `[IMAGE]` instead of 📸

**Example:**
```python
# BAD - Will crash on Windows
logger.info("✓ Login successful!")

# GOOD - Works everywhere
logger.info("[SUCCESS] Login successful!")
```

This applies to:
- All `.py` files
- Log messages
- Console output
- Error messages
- Status indicators

Markdown files (`.md`) and shell scripts (`.sh`) can use Unicode for documentation purposes only.

---

## Project Overview

This is a **hybrid browser automation POC** that combines traditional Playwright automation with AI-powered chart analysis using Claude Vision. The system automates StockCharts.com navigation while leveraging AI to intelligently analyze chart patterns, technical indicators, and recommend alert levels.

**Key Philosophy**: Use the right tool for each job - browser automation for navigation/interaction (fast, reliable), AI for pattern recognition and decision-making (intelligent, contextual).

## Development Commands

### Environment Activation
```bash
# IMPORTANT: This project uses a conda environment named 'browser_automation'
# Always activate this environment before running any commands:
conda activate browser_automation

# The environment is located at: C:\Users\uvdsa\.conda\envs\browser_automation
# This environment has all necessary dependencies including Playwright
```

## **CRITICAL: WINDOWS COMMAND EXECUTION RULES**

### ❌ NEVER DO THIS - Common Mistakes to Avoid

1. **NEVER use conda activate in Bash tool** - It doesn't work in subprocess
   ```bash
   # WRONG - Will fail with "Run 'conda init' before 'conda activate'"
   conda activate browser_automation && python script.py
   ```

2. **NEVER use unquoted Windows paths** - Backslashes break without quotes
   ```bash
   # WRONG - Bash interprets backslashes as escape characters
   C:\Users\uvdsa\anaconda3\envs\browser_automation\python.exe script.py
   ```

3. **NEVER try to read Excel files with Read tool** - Excel files are binary
   ```python
   # WRONG - Read tool cannot handle binary files
   Read("config/file.xlsx")  # Will fail with binary file error
   ```

### ✅ ALWAYS DO THIS - Correct Approaches

1. **Use full Python path with quotes**
   ```bash
   # CORRECT - Use quotes around Windows paths
   "C:\Users\uvdsa\anaconda3\envs\browser_automation\python.exe" script.py
   ```

2. **For Excel files, create a Python script to read them**
   ```python
   # CORRECT - Use pandas to read Excel
   import pandas as pd
   df = pd.read_excel('config/file.xlsx')
   ```

3. **Remember these key paths**
   - Conda env Python: `"C:\Users\uvdsa\.conda\envs\browser_automation\python.exe"`
   - Base Python: `"C:\ProgramData\Anaconda3\python.exe"` (doesn't have project dependencies)
   - Project root: `C:\Users\uvdsa\PycharmProjects\poc_browser_automation`

4. **For running the main application**
   ```bash
   # CORRECT: Use PowerShell with the actual conda env path
   powershell -Command "& 'C:\Users\uvdsa\.conda\envs\browser_automation\python.exe' main.py --mode chartlist-batch --config config/chartlist_config_S1.xlsx"

   # Or create a batch file for easier execution
   ```

### ADMIN ACCESS REQUIRED FOR FULLSCREEN
**CRITICAL**: Browser fullscreen (--kiosk mode) requires administrator privileges on Windows.

#### Quick Launch Options:
1. **Desktop Shortcut**: Use "VS Code Admin - Browser Automation" shortcut on desktop
2. **Batch File**: Double-click `launch_vscode_admin.bat` in project folder
3. **Complete Launcher**: Use `launch_all_admin.bat` for menu-driven options

#### Manual Admin Launch:
- Right-click VS Code → "Run as administrator"
- Right-click terminal → "Run as administrator"
- Look for "[Administrator]" in VS Code title bar to confirm admin mode

#### Why Admin is Needed:
- `--kiosk` mode requires elevated permissions to hide Windows taskbar
- Without admin, browser won't achieve true fullscreen
- ChartStyle box clicking may fail without proper fullscreen

### Setup (if needed)
```bash
# If using a new environment, install dependencies:
pip install -r requirements.txt

# Install Playwright browsers (only needed once)
playwright install chromium

# Setup environment variables
cp config/.env.example config/.env
# Then edit config/.env with your credentials
```

### Running the Application
```bash
# Single ticker analysis
python main.py --mode single --ticker AAPL

# Batch analysis of multiple tickers
python main.py --mode batch --tickers AAPL MSFT GOOGL

# Compare tickers
python main.py --mode compare --tickers SPY QQQ DIA

# Interactive mode
python main.py --mode interactive

# Debug mode with verbose logging
python main.py --mode single --ticker AAPL --log-level DEBUG
```

### Testing
```bash
# Run tests
pytest tests/

# Run specific test
pytest tests/test_poc.py::test_function_name
```

## Architecture

### Three-Layer Architecture

1. **Browser Layer** (`src/browser/stockcharts_controller.py`)
   - Handles Playwright automation
   - Manages authentication and session state
   - Performs navigation and DOM interaction
   - Captures screenshots
   - **Key methods**: `initialize()`, `login()`, `navigate_to_chart()`, `capture_chart_screenshot()`

2. **AI Layer** (`src/ai/chart_analyzer.py`)
   - Interfaces with Anthropic Claude API
   - Performs vision-based chart analysis
   - Extracts patterns, trends, and technical indicators
   - Generates alert recommendations
   - **Key methods**: `analyze_chart_patterns()`, `analyze_technical_indicators()`, `get_alert_recommendations()`

3. **Service Layer** (`src/services/hybrid_chart_service.py`)
   - Orchestrates browser automation + AI analysis
   - Manages workflow between browser and AI components
   - Caches analysis results
   - Generates reports
   - **Key methods**: `analyze_ticker_with_alerts()`, `batch_analyze_tickers()`, `compare_tickers()`

### Typical Workflow
```
User Request → HybridChartService
  ├─ 1. Browser navigates to chart (Playwright)
  ├─ 2. Browser captures screenshot (Playwright)
  ├─ 3. AI analyzes patterns (Claude Vision)
  ├─ 4. AI analyzes indicators (Claude Vision)
  ├─ 5. AI recommends alerts (Claude Vision)
  └─ 6. Service generates report (Orchestration)
```

## Configuration

### Environment Variables (config/.env)
- `STOCKCHARTS_USERNAME`, `STOCKCHARTS_PASSWORD`: StockCharts.com credentials
- `ANTHROPIC_API_KEY`: Required for AI analysis
- `HEADLESS`: Set to `true` to run browser in background
- `AI_MODEL`: Default is `claude-sonnet-4-5-20250929`
- `LOG_LEVEL`: Controls logging verbosity (DEBUG, INFO, WARNING, ERROR)

### Settings File (config/settings.yaml)
- **StockCharts selectors**: If StockCharts.com UI changes, update CSS selectors here
- **Timeouts**: Navigation, login, and chart load timeouts
- **AI prompts**: Customize analysis prompts for different AI tasks
- **Browser configuration**: Viewport size, user agent

## Key Implementation Details

### Browser Automation
- Uses Playwright with stealth mode to avoid detection
- Implements multiple selector fallbacks for robustness (login fields, buttons)
- Saves debug screenshots at each step for troubleshooting
- Maintains session state with `is_logged_in` flag
- Browser context uses realistic viewport (1920x1080) and user agent

### AI Analysis
- Encodes screenshots as base64 for Claude Vision API
- Structured prompts request JSON responses for easy parsing
- Fallback text parsing if JSON extraction fails
- Three separate AI calls per ticker:
  1. Pattern analysis (patterns, trends, support/resistance)
  2. Technical indicator analysis (RSI, MACD, volume)
  3. Alert recommendations (specific price levels with reasoning)

### Error Handling
- Browser operations include extensive try/except with fallback selectors
- AI errors return default structures with error flags
- Debug screenshots saved automatically on failures
- Logs saved to `poc_automation.log` for post-mortem analysis

### Async Architecture
- All I/O operations are async (browser, API calls)
- Batch operations can run sequentially (safe) or concurrently (advanced)
- Uses `asyncio.sleep()` for delays between operations
- Browser controller supports async context manager pattern

## Production Use Cases (Implemented)

### Production Use Case #1: Multi-Timeframe Viewer ✅ COMPLETE

**Purpose**: Open 3 browser tabs showing the same ticker in different timeframes (Daily, 60min, 5min) for manual multi-timeframe analysis.

**Status**: ✅ Fully implemented and tested (Nov 2, 2025)

**Usage:**
```bash
python main.py --mode multi-timeframe --ticker AAPL
```

**How it works:**
1. Logs in to StockCharts.com (once, shared session)
2. Enters ticker in search box ("Enter Symbol or Name" at top)
3. Loads Tab 1: Default Daily chart
4. Duplicates tab → Tab 2: Clicks ChartStyle box #7 (60Mins_Default)
5. Duplicates tab → Tab 3: Clicks ChartStyle box #10 (5mins_Default)
6. Browser stays open for manual inspection
7. User presses Enter when done to close browser

**Key Implementation Details:**
- **Search box selector**: `input[placeholder*='Enter Symbol' i]`
- **ChartStyle button selector**: `.chart-style-buttons .chart-style-button-container:nth-child(N) button.chart-style-button`
  - Box numbers are 1-indexed
  - First button (nth-child 1) is "Manage StyleButtons" gear icon
  - Actual style buttons start at nth-child(2)
  - Box #7 = nth-child(8) = 60Mins_Default
  - Box #10 = nth-child(11) = 5mins_Default
- **Method**: `StockChartsController.open_multi_timeframe_tabs(ticker, chartstyle_box_numbers)`
- **Method**: `StockChartsController.enter_ticker_in_search_box(ticker)`

**ChartStyle Box Numbers (Your Configuration):**
- Box #1: Just_Price_Volume (Daily-ish)
- Box #2: Just_Price_Volume_60Mins
- Box #3: Monthly_Default
- Box #4: Weekly_Default
- Box #5: Daily_Default
- Box #6: Daily_Zoom_Default
- **Box #7: 60Mins_Default** ← Used for 60-minute charts
- Box #8: 30Mins_Default
- Box #9: 15Mins_Default
- **Box #10: 5mins_Default** ← Used for 5-minute charts
- Box #11: 2Minutes_Default
- Box #12: 1min_Default

**Note**: These box numbers/configurations are user-specific (saved to your StockCharts account). Adjust `chartstyle_box_numbers = [1, 7, 10]` in main.py if your setup is different.

**Files Modified:**
- `src/browser/stockcharts_controller.py`: Added `enter_ticker_in_search_box()`, `open_multi_timeframe_tabs()`
- `main.py`: Added `demo_multi_timeframe_viewer()` and `--mode multi-timeframe`

**Output:**
- 3 browser tabs with different timeframes
- Screenshots saved: `screenshots/{TICKER}_tab{N}_box{BOX}_{TIMEFRAME}.png`
- All tabs remain open until user presses Enter

---

### Production Use Case #2: TBD

(To be implemented)

---

### Production Use Case #2: ChartList Batch Viewer ✅ COMPLETE

**Purpose**: Open multiple charts from different ChartLists in separate browser tabs based on an Excel configuration file. Each chart opens in a specific order for manual review.

**Status**: ✅ Fully implemented and tested (Nov 7, 2024)

**Usage:**
```bash
# Create Excel template first
python create_excel_template.py

# Run with your Excel config
python main.py --mode chartlist-batch --config config/chartlist_config_sample.xlsx
```

**Excel Configuration Structure:**

| ChartList | Ticker | TabOrder | TimeframeBox | Notes |
|-----------|--------|----------|--------------|-------|
| My Watchlist | AAPL | 1 | | Check resistance |
| My Watchlist | MSFT | 2 | | Earnings next week |
| Tech Stocks | NVDA | 3 | 7 | 60min chart |
| Energy Sector | XLE | 4 | | Oil sector ETF |
| Small Caps | AEIS | 5 | 10 | 5min day trade |

**How it works:**
1. Reads Excel file with chart configurations
2. Logs in to StockCharts.com (once, shared session)
3. For each row in Excel (sorted by TabOrder):
   - Navigates to the ticker's chart
   - Opens in new browser tab
   - Optionally applies ChartStyle box for timeframe
   - Captures screenshot for verification
4. Browser stays open for manual inspection
5. User presses Enter when done to close browser

**Key Implementation Details:**
- **Excel Reader**: `src/utils/excel_reader.py` - ChartListConfigReader class
- **Method**: `StockChartsController.open_charts_from_excel(excel_path)`
- **Main Function**: `chartlist_batch_viewer()` in main.py
- **Command**: `--mode chartlist-batch --config <excel_path>`

**Files Added/Modified:**
- `src/utils/excel_reader.py`: NEW - Excel configuration reader
- `src/browser/stockcharts_controller.py`: Added `open_charts_from_excel()` method
- `main.py`: Added `chartlist_batch_viewer()` function and `--mode chartlist-batch`
- `requirements.txt`: Added `openpyxl==3.1.2`
- `create_excel_template.py`: NEW - Creates template Excel file

**Output:**
- N browser tabs (one per chart in Excel)
- Screenshots saved: `screenshots/tab{ORDER}_{CHARTLIST}_{TICKER}.png`
- All tabs remain open until user presses Enter

---

### Production Use Case #3: TBD

(To be implemented)

---

## Screenshots and Logging

### Screenshots
- Saved to `screenshots/` directory (configurable via `SCREENSHOT_DIR`)
- Naming convention: `{ticker}_{timestamp}.png` for production screenshots
- Debug screenshots: `debug_{step_name}.png` for troubleshooting
- Debug screenshots are saved at critical points:
  - `01_login_page.png`, `02_credentials_filled.png`, `03_after_login_attempt.png`
  - `error_*.png` for various error conditions

### Logging
- All logs saved to `poc_automation.log`
- Console output uses structured logging with timestamps
- Component-specific loggers (`browser`, `ai`, `service`)
- Use `--log-level DEBUG` for detailed execution traces

## Common Development Patterns

### Adding a New Analysis Type
1. Add prompt to `config/settings.yaml` under `ai_analysis.prompts`
2. Create method in `ChartAnalyzer` class (e.g., `analyze_volume()`)
3. Call from `HybridChartService.analyze_ticker_with_alerts()`
4. Update report generation in `generate_report()`

### Modifying StockCharts Navigation
- Update selectors in `config/settings.yaml` first (prefer configuration over code)
- If code changes needed, modify `StockChartsController.navigate_to_chart()`
- Always test with `HEADLESS=false` to visually verify behavior
- Use debug screenshots to capture state at each step

### Adding New Demo Modes
- Create async function in `main.py` (e.g., `demo_new_feature()`)
- Add mode to argparse choices in `main()`
- Follow pattern: initialize → login → perform analysis → cleanup

## Performance Considerations

- Each ticker analysis takes ~30-50 seconds (includes 3 AI API calls)
- Batch mode uses sequential processing by default (safer, respects rate limits)
- AI API calls dominate execution time (8-15s each)
- Browser navigation is fast (3-5s per chart)
- Add delays between batch operations to avoid overwhelming the site (`delay_between` parameter)

## Security Notes

- Never commit `config/.env` file (included in `.gitignore`)
- StockCharts credentials stored in environment variables only
- Anthropic API key required - treat as sensitive credential
- Browser automation may violate StockCharts.com ToS - use responsibly

## Troubleshooting Quick Reference

### Login Failures
- Check credentials in `config/.env`
- Run with `HEADLESS=false` to observe browser behavior
- Check `screenshots/debug_*.png` for visual debugging
- Update selectors in `config/settings.yaml` if StockCharts changed their UI

### AI Analysis Errors
- Verify `ANTHROPIC_API_KEY` is valid
- Check API quota/rate limits
- Ensure screenshot file exists and is readable
- Review AI prompt in `config/settings.yaml` for clarity

### Screenshot Issues
- Increase wait times in `navigate_to_chart()` (after line 279 in stockcharts_controller.py)
- Verify chart element is visible before capture
- Check viewport size in browser config

---

## Next Phase: Multi-Platform Extension

This section outlines the planned evolution from a single-platform POC to a robust multi-platform automation system.

### Vision: Universal Chart Analysis Platform

**Goal**: Support multiple trading platforms (web + desktop) with a unified architecture while maintaining the hybrid automation + AI approach.

**Supported Platforms (Planned)**:
- **Web**: StockCharts.com (✅ current), TradingView, MarketSurge, FinViz
- **Desktop**: TradeStation, ThinkOrSwim, Interactive Brokers TWS
- **API**: Direct data integration where available (preferred method)

### Proposed Architecture Evolution

#### Current Architecture (Phase 1 - POC)
```
src/
├── browser/
│   └── stockcharts_controller.py    # StockCharts-specific
├── ai/
│   └── chart_analyzer.py            # Platform-agnostic ✅
└── services/
    └── hybrid_chart_service.py      # Tightly coupled to StockCharts
```

#### Target Architecture (Phase 2 - Multi-Platform)
```
src/
├── controllers/
│   ├── base_controller.py                    # Abstract interface
│   │
│   ├── web/                                   # Web platforms
│   │   ├── base_web_controller.py            # Playwright base
│   │   ├── stockcharts_controller.py         # Migrated from src/browser/
│   │   ├── tradingview_controller.py         # NEW
│   │   └── marketsurge_controller.py         # NEW
│   │
│   ├── desktop/                               # Desktop apps
│   │   ├── base_desktop_controller.py        # pywinauto/pyautogui base
│   │   ├── tradestation_controller.py        # NEW
│   │   └── thinkorswim_controller.py         # NEW
│   │
│   └── api/                                   # Direct API integrations
│       ├── base_api_controller.py            # REST/WebSocket base
│       └── tradingview_api_controller.py     # NEW (if API available)
│
├── locators/                                  # Element finding strategies
│   ├── web_locator.py                        # CSS/XPath selectors
│   ├── uia_locator.py                        # Windows UI Automation
│   └── image_locator.py                      # Template matching
│
├── services/
│   ├── window_manager.py                     # NEW - Multi-monitor management
│   └── hybrid_chart_service.py               # Refactored - accepts any controller
│
├── platforms/
│   └── platform_factory.py                   # NEW - Controller instantiation
│
└── ai/
    └── chart_analyzer.py                     # UNCHANGED - already perfect!
```

### Controller Abstraction Layer

All platform controllers will implement a common interface:

```python
# src/controllers/base_controller.py
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

class BaseController(ABC):
    """Abstract base class for all platform controllers"""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the controller (browser/app/API client)"""
        pass

    @abstractmethod
    async def login(self) -> bool:
        """Authenticate with the platform"""
        pass

    @abstractmethod
    async def navigate_to_chart(self, ticker: str) -> bool:
        """Navigate to/load chart for specified ticker"""
        pass

    @abstractmethod
    async def capture_chart_screenshot(self, ticker: str) -> Path:
        """Capture chart screenshot and return path"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Cleanup resources"""
        pass

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Return platform identifier (e.g., 'stockcharts', 'tradingview')"""
        pass
```

**Benefits**:
- Service layer works with any controller
- Easy to add new platforms
- Testable with mock controllers
- Type-safe with protocol/ABC

### Platform-Specific Implementation Strategies

#### Web Platforms (Playwright-based)

**StockCharts** (current):
- Login: Form-based (username/password)
- Navigation: URL with ticker parameter
- Difficulty: Low ✅

**TradingView**:
- Login: Email/password or OAuth
- Navigation: URL with symbol parameter
- Challenges: Heavy JavaScript, anti-bot measures, Canvas charts
- Difficulty: Medium ⚠️

**MarketSurge**:
- Login: Email-based (IBD account)
- Navigation: Modern SPA architecture
- Challenges: May require specific subscription tier
- Difficulty: Medium ⚠️

#### Desktop Applications (UI Automation)

**Strategy Decision Tree**:
```
Does platform offer API?
├─ YES → Use API Controller (fastest, most reliable)
└─ NO → Does app expose UI Automation?
    ├─ YES → Use pywinauto (Windows UIA)
    └─ NO → Use image-based automation (pyautogui)
```

**TradeStation**:
- Check API: TradeStation offers API (✅ preferred approach!)
- Fallback: UI automation with pywinauto
- Difficulty: Low (API) / High (UI automation)

**ThinkOrSwim**:
- Check API: TD Ameritrade API available
- Fallback: UI automation (very complex app)
- Difficulty: Low (API) / Very High (UI automation)

**Interactive Brokers TWS**:
- API: IB API available (Python wrapper: ib_insync)
- Should NOT use UI automation
- Difficulty: Low (API)

### Window Management for Headed Multi-Platform Mode

**Challenge**: Running 3-5 visible browser/desktop windows while user works on same computer.

**Solution**: Intelligent window placement on multi-monitor setup:

```python
# src/services/window_manager.py
from typing import Dict, Tuple
import pygetwindow as gw
from screeninfo import get_monitors

class WindowManager:
    """Manages window placement for multi-platform headed mode"""

    def __init__(self, automation_monitor: int = 2):
        """
        Args:
            automation_monitor: Which monitor for automation (1-indexed)
                               User's primary work stays on monitor 1
        """
        self.monitors = get_monitors()
        self.automation_monitor = automation_monitor
        self.window_registry: Dict[str, gw.Win32Window] = {}

    def assign_platform_position(self, platform: str, window_title: str) -> Tuple[int, int, int, int]:
        """
        Assign window position based on platform

        Returns: (x, y, width, height) for window placement
        """
        monitor = self.monitors[self.automation_monitor - 1]

        # Grid layout on automation monitor
        positions = {
            'stockcharts': (0, 0, 0.5, 0.5),      # Top-left
            'tradingview': (0.5, 0, 0.5, 0.5),    # Top-right
            'marketsurge': (0, 0.5, 0.5, 0.5),    # Bottom-left
            'tradestation': (0.5, 0.5, 0.5, 0.5), # Bottom-right
        }

        rel_x, rel_y, rel_w, rel_h = positions.get(platform, (0, 0, 1, 1))

        return (
            monitor.x + int(monitor.width * rel_x),
            monitor.y + int(monitor.height * rel_y),
            int(monitor.width * rel_w),
            int(monitor.height * rel_h)
        )

    async def position_browser(self, controller, platform: str):
        """Position Playwright browser window"""
        # Use Playwright's browser window positioning
        # This requires CDP (Chrome DevTools Protocol) access
        pass

    async def position_desktop_app(self, window_title: str, platform: str):
        """Position desktop application window"""
        window = gw.getWindowsWithTitle(window_title)[0]
        x, y, w, h = self.assign_platform_position(platform, window_title)
        window.moveTo(x, y)
        window.resizeTo(w, h)
```

**Multi-Monitor Configuration**:

```yaml
# config/settings.yaml
window_management:
  enabled: true
  automation_monitor: 2          # Dedicate monitor 2 for automation
  restore_on_crash: true         # Restore window positions

  grid_layout:                   # How to arrange windows on monitor
    stockcharts: {row: 0, col: 0}
    tradingview: {row: 0, col: 1}
    marketsurge: {row: 1, col: 0}
    tradestation: {row: 1, col: 1}
```

**Alternative: Virtual Desktop (Windows 10/11)**:
```python
# Use Windows Virtual Desktops API
# Run all automation on Virtual Desktop 2
# User works on Virtual Desktop 1
# Zero visual interference!

# Note: Requires Windows-specific COM API access
```

### Configuration Extensions

#### Multi-Platform Settings Structure

```yaml
# config/settings.yaml (extended)

platforms:
  stockcharts:
    type: web
    base_url: "https://stockcharts.com"
    login_url: "https://stockcharts.com/h-sc/ui"
    chart_url_template: "{base_url}/h-sc/ui?s={ticker}"
    timeouts:
      navigation: 30000
      login: 10000
      chart_load: 15000
    selectors:
      username_field: "input[name='username']"
      password_field: "input[type='password']"
      login_button: "button[type='submit']"
    credentials_env:
      username: STOCKCHARTS_USERNAME
      password: STOCKCHARTS_PASSWORD

  tradingview:
    type: web
    base_url: "https://www.tradingview.com"
    login_url: "https://www.tradingview.com/accounts/signin/"
    chart_url_template: "{base_url}/chart/?symbol={ticker}"
    requires_cookies: true
    anti_bot_protection: true
    timeouts:
      navigation: 45000  # Slower due to JS-heavy app
      login: 15000
      chart_load: 20000
    selectors:
      email_field: "input[name='username']"
      password_field: "input[name='password']"
      login_button: "button[type='submit']"
    credentials_env:
      username: TRADINGVIEW_EMAIL
      password: TRADINGVIEW_PASSWORD

  tradestation:
    type: desktop
    executable_path: "C:\\Program Files\\TradeStation\\tsclient.exe"
    window_title_pattern: ".*TradeStation.*"
    automation_method: api  # Options: api, uia, image
    api_config:
      base_url: "https://api.tradestation.com/v3"
      auth_type: oauth2
      credentials_env:
        client_id: TRADESTATION_CLIENT_ID
        client_secret: TRADESTATION_CLIENT_SECRET
    # Fallback if API not used:
    uia_config:
      chart_area_id: "ChartControl"
      ticker_input_id: "SymbolInput"
```

#### Environment Variables (.env)

```bash
# StockCharts
STOCKCHARTS_USERNAME=your_username
STOCKCHARTS_PASSWORD=your_password

# TradingView
TRADINGVIEW_EMAIL=your_email
TRADINGVIEW_PASSWORD=your_password

# TradeStation (API approach)
TRADESTATION_CLIENT_ID=your_client_id
TRADESTATION_CLIENT_SECRET=your_client_secret

# TradeStation (UI automation fallback)
TRADESTATION_USERNAME=your_username
TRADESTATION_PASSWORD=your_password

# Anthropic (unchanged)
ANTHROPIC_API_KEY=your_api_key

# Window Management
HEADLESS=false
AUTOMATION_MONITOR=2  # Which monitor for automation windows
```

### Additional Dependencies

#### Web Platforms (already have)
```
playwright==1.40.0
playwright-stealth==1.0.0
```

#### Desktop Automation (NEW)
```
# requirements-desktop.txt

# Windows UI Automation (primary method)
pywinauto==0.6.8              # Native Windows automation
pygetwindow==0.0.9            # Window detection/control
pynput==1.7.6                 # Keyboard/mouse input (cross-platform)

# Screen capture (non-Playwright)
mss==9.0.1                    # Fast multi-monitor screenshots
screeninfo==0.8.1             # Monitor detection

# Image-based automation (fallback)
opencv-python==4.8.1          # Template matching
pyautogui==0.9.54             # Simple automation API

# Optional: OCR for reading values
easyocr==1.7.0                # If needed for text extraction
```

#### API Integrations (NEW)
```
# requirements-api.txt

# TradeStation API
requests==2.31.0              # HTTP client (already have from anthropic)
aiohttp==3.9.1                # Async HTTP

# TD Ameritrade (ThinkOrSwim)
# tda-api==1.3.0              # Official wrapper (if needed)

# OAuth handling
authlib==1.2.1                # OAuth 2.0 client
```

### Migration Path (Implementation Phases)

#### Phase 1: Refactor for Abstraction (2-3 days)
**Goal**: Introduce controller abstraction without breaking current functionality

1. Create `src/controllers/base_controller.py` with abstract interface
2. Create `src/controllers/web/base_web_controller.py` (Playwright wrapper)
3. Move `src/browser/stockcharts_controller.py` → `src/controllers/web/stockcharts_controller.py`
4. Inherit from `BaseWebController`, ensure interface compliance
5. Update `HybridChartService` to accept `BaseController` type instead of `StockChartsController`
6. Run existing tests to verify nothing broke

**Success Criteria**: All existing functionality works with new structure

#### Phase 2: Add Second Web Platform (3-4 days)
**Goal**: Prove architecture works for multiple platforms

1. Implement `src/controllers/web/tradingview_controller.py`
2. Add TradingView config to `settings.yaml`
3. Create `src/platforms/platform_factory.py`
4. Update `main.py` to accept `--platform tradingview`
5. Test full workflow: login → navigate → screenshot → AI analysis
6. Compare results between StockCharts and TradingView

**Success Criteria**: Can analyze same ticker on both platforms

#### Phase 3: Window Management (2-3 days)
**Goal**: Enable multi-platform headed mode without disrupting workflow

1. Install `pygetwindow` and `screeninfo`
2. Implement `src/services/window_manager.py`
3. Add monitor detection and grid layout logic
4. Integrate with Playwright browser positioning
5. Test with 2-3 platforms running simultaneously
6. Add configuration for monitor assignment

**Success Criteria**: Multiple platforms visible on dedicated monitor, user can work on primary monitor

#### Phase 4: Desktop Foundation (4-5 days)
**Goal**: Prepare for desktop application automation

1. Research TradeStation API availability (API is preferred!)
2. If API exists:
   - Implement `src/controllers/api/tradestation_api_controller.py`
   - Skip UI automation complexity
3. If no API:
   - Install `pywinauto`
   - Implement `src/controllers/desktop/base_desktop_controller.py`
   - Create stub `src/controllers/desktop/tradestation_controller.py`
   - Focus on window detection and screenshot capture first
4. Test screenshot → AI analysis pipeline

**Success Criteria**: Can capture TradeStation chart and analyze with Claude

#### Phase 5: Multi-Platform Orchestration (2-3 days)
**Goal**: Enable concurrent analysis across all platforms

1. Update `HybridChartService.batch_analyze_tickers()` to accept platform list
2. Implement platform-specific routing in service layer
3. Add cross-platform comparison features
4. Optimize concurrent execution with proper resource limits
5. Add error handling for platform-specific failures

**Success Criteria**: Analyze same ticker on 3+ platforms simultaneously

#### Phase 6: Production Hardening (3-4 days)
**Goal**: Reliability, monitoring, and documentation

1. Add retry logic with exponential backoff
2. Implement health checks for each platform
3. Add performance monitoring (timing, success rates)
4. Create comprehensive error recovery
5. Update all documentation (README, CLAUDE.md)
6. Create platform-specific troubleshooting guides

**Success Criteria**: System runs reliably for 24+ hours unattended

### Technical Challenges & Mitigation

#### Challenge 1: Browser Anti-Bot Detection
**Platforms Affected**: TradingView, others with Cloudflare/DataDome

**Mitigation**:
- Use `playwright-stealth` (already have)
- Realistic viewport and user agent
- Human-like delays between actions
- Session cookie persistence
- Consider residential proxy rotation (advanced)

#### Challenge 2: Desktop App Element Location
**Platforms Affected**: TradeStation, ThinkOrSwim (if using UI automation)

**Mitigation**:
- Prefer API integration over UI automation
- If UI automation required:
  - Use Windows UIA (pywinauto) for reliability
  - Maintain image templates for fallback
  - Use coordinate ranges instead of exact pixels
  - Test across app versions

#### Challenge 3: Window Focus Stealing
**Impact**: Disrupts user workflow during headed automation

**Mitigation**:
- Dedicated monitor for automation (recommended)
- Virtual Desktop isolation (Windows 10/11)
- Minimize unnecessary window activation
- Batch operations to reduce focus changes

#### Challenge 4: Rate Limiting / ToS Violations
**Platforms Affected**: All

**Mitigation**:
- Add configurable delays between requests
- Respect platform rate limits (per-platform config)
- Run during off-peak hours for scheduled tasks
- Use official APIs where available
- Review each platform's ToS and automation policies

#### Challenge 5: Screenshot Reliability
**Impact**: AI analysis quality depends on screenshot quality

**Mitigation**:
- Ensure window is focused before screenshot
- Wait for chart to fully render (custom wait logic per platform)
- Verify screenshot file size > threshold (detect blank screenshots)
- Retry mechanism for failed captures
- Platform-specific chart area cropping

#### Challenge 6: Cross-Platform Chart Variations
**Impact**: Different platforms show different chart styles

**Mitigation**:
- Claude AI handles this naturally! (Vision model adapts)
- Standardize screenshot dimensions where possible
- Platform-specific AI prompts (if needed)
- Include platform context in AI analysis prompt

### Performance Optimization

#### Headed vs Headless Trade-offs

**Current POC** (1 platform, headed):
- Browser launch: 3-5s
- Memory: ~200MB
- CPU: 10-15% (rendering)

**Multi-Platform** (5 platforms, headed):
- Browser launch: 15-25s total
- Memory: ~1.5GB (5 browsers + 2 desktop apps)
- CPU: 30-50% (multiple rendering)
- **Recommendation**: Use headless for production, headed for development

**Optimization Strategies**:
1. **Browser Pooling**: Keep browsers open, reuse for multiple tickers
2. **Lazy Initialization**: Only launch platforms as needed
3. **Parallel Screenshot**: Capture from multiple platforms concurrently
4. **AI Batching**: Group AI requests where possible
5. **Caching**: Cache analysis results to avoid re-analysis

### Development Guidelines

#### Adding a New Web Platform

1. **Research Phase**:
   - Inspect login flow (username vs email, OAuth, 2FA?)
   - Identify chart URL structure
   - Test selectors in browser dev tools
   - Check for anti-bot measures

2. **Implementation**:
   ```python
   # src/controllers/web/newplatform_controller.py
   from .base_web_controller import BaseWebController

   class NewPlatformController(BaseWebController):
       platform_name = "newplatform"

       async def login(self) -> bool:
           # Platform-specific login logic
           pass

       async def navigate_to_chart(self, ticker: str) -> bool:
           # Platform-specific navigation
           pass
   ```

3. **Configuration**:
   - Add platform section to `settings.yaml`
   - Add credentials to `.env.example`
   - Document any special requirements

4. **Testing**:
   - Test login flow with valid/invalid credentials
   - Test navigation with various tickers
   - Verify screenshot quality
   - Run full AI analysis pipeline

#### Adding a New Desktop Platform

1. **API Check First**:
   - Search for official API documentation
   - If API exists, implement `api/*_controller.py` instead
   - APIs are always preferred over UI automation

2. **UI Automation (if no API)**:
   - Use Spy++ or Accessibility Insights to inspect UI tree
   - Identify reliable element locators (AutomationId, Name, ClassName)
   - Test with `pywinauto` interactively first
   - Have image-based fallback for complex elements

3. **Window Management**:
   - Implement window detection by title pattern
   - Handle window states (minimized, background, etc.)
   - Test focus behavior doesn't disrupt user

### Decision Matrix: Which Automation Method?

For each platform, choose the best approach:

| Criteria | API | Web (Playwright) | Desktop (UIA) | Image-Based |
|----------|-----|------------------|---------------|-------------|
| **Reliability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Speed** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Maintenance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ |
| **Setup Complexity** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Cross-Platform** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ (Windows) | ⭐⭐⭐⭐ |
| **Cost** | 💰 (may require paid tier) | Free | Free | Free |

**Recommendation Priority**:
1. ✅ **API** (if available) - Most reliable, fastest
2. ✅ **Web/Playwright** (for web platforms) - Current POC approach
3. ⚠️ **Desktop UIA** (for desktop apps without API) - Complex but reliable
4. ❌ **Image-Based** (last resort only) - Fragile, avoid if possible

### Expected Outcomes

After implementing Phase 2 architecture:

**Capabilities**:
- ✅ Analyze charts from 5+ different platforms
- ✅ Run multiple platforms simultaneously (multi-monitor)
- ✅ Easy to add new platforms (just implement controller)
- ✅ Unified AI analysis across all platforms
- ✅ Cross-platform comparison and ranking
- ✅ Configurable headed/headless per platform

**Limitations**:
- ⚠️ Desktop apps more fragile than web
- ⚠️ Requires multi-monitor for optimal headed experience
- ⚠️ Each platform needs individual maintenance
- ⚠️ API access may require paid subscriptions

**Performance** (5 platforms, 1 ticker each):
- Sequential: ~3-4 minutes total
- Concurrent: ~1-1.5 minutes total
- AI analysis: Still dominates (same as current)

### Resources & References

**Desktop Automation**:
- pywinauto docs: https://pywinauto.readthedocs.io/
- Windows UIA guide: https://docs.microsoft.com/en-us/windows/win32/winauto/entry-uiauto-win32

**Trading Platform APIs**:
- TradeStation API: https://www.tradestation.com/platforms-and-tools/api/
- TD Ameritrade API: https://developer.tdameritrade.com/
- Interactive Brokers API: https://www.interactivebrokers.com/en/index.php?f=5041

**Window Management**:
- pygetwindow: https://github.com/asweigart/PyGetWindow
- screeninfo: https://github.com/rr-/screeninfo

**Best Practices**:
- Always check for official APIs before UI automation
- Prefer configuration over code for platform differences
- Test on target platform frequently (UI changes break automation)
- Implement graceful degradation (if one platform fails, others continue)
- Respect platform ToS and rate limits
