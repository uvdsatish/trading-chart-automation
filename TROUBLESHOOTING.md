# Troubleshooting Guide - Hybrid Browser Automation POC

## Quick Diagnostic Checklist

Before diving into specific issues, run this quick diagnostic:

```bash
# 1. Check Python version
python --version  # Should be 3.8+

# 2. Check virtual environment is activated
which python  # Should point to venv/bin/python

# 3. Check dependencies
pip list | grep -E "playwright|anthropic|pyyaml"

# 4. Check config files
ls -la config/
# Should see: .env, .env.example, settings.yaml

# 5. Test imports
python -c "from playwright.async_api import async_playwright; import anthropic; print('✓ OK')"

# 6. Check logs
tail -50 poc_automation.log
```

---

## Common Issues & Solutions

### 1. Installation Issues

#### Issue: "playwright: command not found"
**Symptoms**:
```
playwright install
-bash: playwright: command not found
```

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install playwright properly
pip install playwright
playwright install chromium
```

#### Issue: "No module named 'playwright'"
**Symptoms**:
```python
ModuleNotFoundError: No module named 'playwright'
```

**Solution**:
```bash
# Check if you're in the right environment
which python  # Should show venv path

# Reinstall
pip install -r requirements.txt
```

#### Issue: Browser download fails
**Symptoms**:
```
Downloading Chromium... Failed
```

**Solutions**:
```bash
# Option 1: Try direct browser download
playwright install --with-deps chromium

# Option 2: Use system browser (not recommended)
# Set env var: PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

# Option 3: Check network/firewall
curl -I https://playwright.azureedge.net/
```

---

### 2. Authentication Issues

#### Issue: Login fails silently
**Symptoms**:
- Script says "Login successful" but you're not logged in
- Or "Login failed" with no clear reason

**Debug Steps**:
```bash
# 1. Run with browser visible
# Edit config/.env:
HEADLESS=false

# 2. Run with debug logging
python main.py --mode single --ticker AAPL --log-level DEBUG

# 3. Check debug screenshots
ls -lt screenshots/debug_*.png
# Open most recent ones

# 4. Verify credentials manually
# Try logging in manually in the browser to confirm they work
```

**Common Causes**:

1. **Wrong Credentials**
   - Check `.env` file has correct username/password
   - No extra spaces or quotes in .env values
   - Try logging in manually on StockCharts.com first

2. **UI Selectors Changed**
   - StockCharts.com updated their UI
   - Update selectors in `config/settings.yaml`:
   ```yaml
   stockcharts:
     selectors:
       username_field: "NEW_SELECTOR_HERE"
       password_field: "NEW_SELECTOR_HERE"
       login_button: "NEW_SELECTOR_HERE"
   ```
   
   To find new selectors:
   - Open browser with HEADLESS=false
   - Right-click on field → Inspect
   - Note the selector (id, name, class)

3. **CAPTCHA or 2FA**
   - StockCharts might be requiring additional verification
   - Try logging in manually first
   - May need to whitelist your IP
   - Consider using session cookies (advanced)

4. **Rate Limiting**
   - Too many login attempts
   - Wait 15-30 minutes before retrying
   - Use longer delays between attempts

#### Issue: "Element not found" during login
**Symptoms**:
```
TimeoutError: Timeout 30000ms exceeded waiting for selector...
```

**Solutions**:

```python
# Option 1: Increase timeout in settings.yaml
stockcharts:
  timeouts:
    login: 30000  # Change to 60000

# Option 2: Add explicit waits in code
# Edit src/browser/stockcharts_controller.py:
await asyncio.sleep(5)  # After page load

# Option 3: Try alternative selectors
# Check debug screenshots to identify actual element
```

---

### 3. Navigation & Screenshot Issues

#### Issue: Charts don't load or appear blank
**Symptoms**:
- Screenshot is completely black or white
- Chart elements not visible
- Page loads but no chart appears

**Solutions**:

```python
# 1. Increase wait time after navigation
# Edit src/browser/stockcharts_controller.py:

async def navigate_to_chart(self, ticker: str):
    await self.page.goto(chart_url, wait_until='networkidle')
    await asyncio.sleep(5)  # Add or increase this
    
    # Wait for specific element
    await self.page.wait_for_selector('.chart-image', timeout=15000)

# 2. Try different chart URL format
# StockCharts has multiple URL patterns:
# Pattern A: https://stockcharts.com/h-sc/ui?s=AAPL
# Pattern B: https://stockcharts.com/c-sc/sc?s=AAPL
# Pattern C: https://stockcharts.com/freecharts/gallery.html?AAPL

# 3. Verify chart loads manually
# Open browser with HEADLESS=false and watch what happens
```

#### Issue: Screenshot captured but AI can't analyze
**Symptoms**:
- Screenshot file exists and looks correct
- AI returns empty or error response

**Debug**:
```bash
# 1. Check screenshot file size
ls -lh screenshots/AAPL_*.png
# Should be >100KB for a good chart

# 2. Verify image is valid
file screenshots/AAPL_*.png
# Should say: PNG image data

# 3. Try viewing the image
# On Mac: open screenshots/AAPL_*.png
# On Linux: xdg-open screenshots/AAPL_*.png

# 4. Test AI with known good image
python -c "
import asyncio
from pathlib import Path
from src.ai.chart_analyzer import ChartAnalyzer

async def test():
    analyzer = ChartAnalyzer('YOUR_API_KEY')
    result = await analyzer.analyze_chart_patterns(
        Path('screenshots/AAPL_20241101_120000.png'),
        'AAPL'
    )
    print(result)

asyncio.run(test())
"
```

---

### 4. AI Analysis Issues

#### Issue: AI returns empty or poor analysis
**Symptoms**:
- Analysis dict is mostly empty
- No patterns identified
- Generic or unhelpful recommendations

**Solutions**:

1. **Check Image Quality**:
   ```bash
   # Screenshot should clearly show:
   # - Price chart
   # - Time axis
   # - Price axis
   # - Any indicators (RSI, MACD, etc.)
   
   # If image is too small or unclear, adjust capture:
   await self.page.screenshot(
       path=filepath,
       full_page=True  # Try this
   )
   ```

2. **Improve Prompts**:
   ```yaml
   # Edit config/settings.yaml
   ai_analysis:
     prompts:
       chart_pattern_detection: |
         You are an expert technical analyst. Analyze this stock chart carefully.
         
         [Add more specific instructions]
         [Add examples of good analysis]
         [Request specific format]
   ```

3. **Increase Token Limit**:
   ```bash
   # Edit config/.env
   MAX_TOKENS=8192  # Increase from 4096
   ```

4. **Check API Response**:
   ```python
   # Add debug logging to chart_analyzer.py
   logger.debug(f"API Response: {message.content}")
   ```

#### Issue: API rate limiting or quota exceeded
**Symptoms**:
```
anthropic.RateLimitError: rate_limit_error: ...
```

**Solutions**:
```bash
# 1. Check your API usage
# Log into Anthropic Console: https://console.anthropic.com/

# 2. Add rate limiting to code
# Edit src/services/hybrid_chart_service.py:

async def batch_analyze_tickers(self, tickers: List[str], delay_between: float = 5.0):
    # Increase delay_between from 2.0 to 5.0 or higher

# 3. Reduce concurrent requests
# Use sequential processing only (already default)

# 4. Cache results
# Don't re-analyze same ticker multiple times
```

#### Issue: AI cost too high
**Symptoms**:
- API costs more than expected

**Cost Reduction Strategies**:
```python
# 1. Reduce image size before sending
# Add to chart_analyzer.py:
from PIL import Image

def _optimize_image(self, image_path: Path) -> Path:
    img = Image.open(image_path)
    # Resize to max 1920x1080
    img.thumbnail((1920, 1080))
    optimized_path = image_path.with_stem(f"{image_path.stem}_optimized")
    img.save(optimized_path, optimize=True, quality=85)
    return optimized_path

# 2. Cache analyses
# Don't re-analyze same ticker same day

# 3. Batch similar questions
# Instead of 3 API calls, combine into 1 comprehensive call

# 4. Use smaller model for simple tasks
# claude-haiku-3 for quick checks
# claude-sonnet for detailed analysis
```

---

### 5. Performance Issues

#### Issue: Processing too slow
**Symptoms**:
- Takes >2 minutes per ticker
- Batch processing extremely slow

**Optimization**:

```python
# 1. Reduce wait times
# Edit stockcharts_controller.py:
await asyncio.sleep(2)  # Instead of 5

# 2. Parallel processing (advanced)
# Edit hybrid_chart_service.py:
async def batch_analyze_tickers(self, tickers: List[str], concurrent: bool = True):
    # Set concurrent=True and implement semaphore:
    semaphore = asyncio.Semaphore(3)  # Max 3 concurrent
    
    async def analyze_with_limit(ticker):
        async with semaphore:
            return await self.analyze_ticker_with_alerts(ticker)
    
    tasks = [analyze_with_limit(t) for t in tickers]
    results = await asyncio.gather(*tasks)

# 3. Skip redundant AI calls
# If you only need patterns, don't call indicator analysis

# 4. Use headless mode
# Edit .env:
HEADLESS=true  # Faster than visible browser
```

#### Issue: Browser crashes or hangs
**Symptoms**:
- Browser stops responding
- Python script hangs
- Memory usage very high

**Solutions**:

```python
# 1. Add timeout protection
# Edit stockcharts_controller.py:

async def navigate_to_chart(self, ticker: str):
    try:
        await asyncio.wait_for(
            self.page.goto(chart_url, wait_until='networkidle'),
            timeout=30  # Force timeout after 30s
        )
    except asyncio.TimeoutError:
        logger.error(f"Navigation timeout for {ticker}")
        return False

# 2. Restart browser periodically
# For batch processing:
async def batch_analyze_tickers(self, tickers: List[str]):
    for i, ticker in enumerate(tickers):
        result = await self.analyze_ticker_with_alerts(ticker)
        
        # Restart browser every 10 tickers
        if (i + 1) % 10 == 0:
            await self.browser.close()
            await self.browser.initialize()
            await self.browser.login()

# 3. Monitor memory
import psutil
print(f"Memory: {psutil.Process().memory_info().rss / 1024 / 1024:.1f} MB")
```

---

### 6. Configuration Issues

#### Issue: ".env file not found"
**Solution**:
```bash
# Create from template
cp config/.env.example config/.env

# Edit with your credentials
nano config/.env  # or vim, or any editor
```

#### Issue: "Settings file not found" or YAML errors
**Symptoms**:
```
FileNotFoundError: config/settings.yaml
# or
yaml.scanner.ScannerError: while scanning...
```

**Solutions**:
```bash
# 1. Verify file exists
ls -la config/settings.yaml

# 2. Check YAML syntax
python -c "import yaml; yaml.safe_load(open('config/settings.yaml'))"

# 3. Common YAML errors:
# - Incorrect indentation (use spaces, not tabs)
# - Missing colons
# - Unquoted special characters

# 4. Validate YAML online
# Copy content to: http://www.yamllint.com/
```

---

### 7. Testing Issues

#### Issue: Tests fail
**Symptoms**:
```bash
pytest tests/test_poc.py
# Multiple failures
```

**Solutions**:

```bash
# 1. Run tests with verbose output
pytest tests/test_poc.py -v -s

# 2. Run specific test
pytest tests/test_poc.py::TestBrowserController::test_controller_initialization -v

# 3. Skip tests requiring credentials
pytest tests/test_poc.py -v -m "not slow"

# 4. Update test fixtures
# Some tests may need actual credentials to pass
# Mark them as @pytest.mark.skip for POC testing
```

---

## Debugging Tools & Techniques

### 1. Enable Debug Logging

```python
# Add to top of main.py or any script:
import logging
logging.basicConfig(level=logging.DEBUG)

# Or use command line:
python main.py --log-level DEBUG
```

### 2. Interactive Debugging

```python
# Add breakpoints in code:
import pdb; pdb.set_trace()

# Or use iPython:
from IPython import embed; embed()

# Then run normally
python main.py --mode single --ticker AAPL
```

### 3. Screenshot Everything

```python
# Add to stockcharts_controller.py:

async def _debug_screenshot(self, name: str):
    """Take screenshot for debugging"""
    path = self.screenshot_dir / f"debug_{name}_{int(time.time())}.png"
    await self.page.screenshot(path=str(path))
    print(f"Debug screenshot: {path}")

# Use liberally:
await self._debug_screenshot("before_login")
await self._debug_screenshot("after_login")
await self._debug_screenshot("chart_loaded")
```

### 4. Log API Requests

```python
# Add to chart_analyzer.py:

import json

def _log_api_call(self, prompt: str, response: str):
    """Log API interactions for debugging"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt[:200],  # First 200 chars
        "response": response[:500]
    }
    
    with open("api_calls.log", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
```

### 5. Browser DevTools

```python
# Open browser DevTools programmatically:
await self.context.tracing.start(screenshots=True, snapshots=True)
# ... do stuff ...
await self.context.tracing.stop(path="trace.zip")

# View trace at: https://trace.playwright.dev/
```

---

## Getting Help

### Before Asking for Help

Collect this information:

```bash
# 1. System info
python --version
pip list | grep -E "playwright|anthropic"
cat config/settings.yaml

# 2. Error messages
tail -100 poc_automation.log > error_log.txt

# 3. Screenshots
ls -lh screenshots/debug_*.png

# 4. Test results
pytest tests/test_poc.py -v > test_results.txt 2>&1
```

### Where to Get Help

1. **Check logs first**: `poc_automation.log`
2. **Review debug screenshots**: `screenshots/debug_*.png`
3. **Search issues**: Similar problems likely solved
4. **Documentation**: Playwright, Anthropic, StockCharts
5. **Community forums**: Stack Overflow, GitHub Issues

### Creating a Good Bug Report

Include:
- Python version
- OS (Windows/Mac/Linux)
- Full error message
- Steps to reproduce
- Expected vs actual behavior
- Relevant log excerpts
- Screenshots if applicable

---

## Prevention Tips

### Before You Start
- ✅ Verify all credentials work manually first
- ✅ Test StockCharts.com access in regular browser
- ✅ Confirm Anthropic API key has sufficient credits
- ✅ Start with HEADLESS=false to see what's happening

### During Development
- ✅ Test changes incrementally
- ✅ Keep debug logging enabled
- ✅ Save debug screenshots frequently
- ✅ Commit working code before major changes

### For Production Use
- ✅ Add comprehensive error handling
- ✅ Implement retry logic
- ✅ Monitor API costs
- ✅ Set up alerts for failures
- ✅ Keep screenshots for debugging

---

## Emergency Procedures

### If Everything Breaks

```bash
# Nuclear option: Start fresh
rm -rf venv
rm -rf screenshots/*
rm poc_automation.log

# Recreate from scratch
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Verify credentials
cat config/.env

# Test basic functionality
python main.py --mode single --ticker AAPL --log-level DEBUG
```

### If You're Stuck

1. **Take a break** - Fresh eyes help
2. **Simplify** - Test one component at a time
3. **Document** - Write down what you tried
4. **Ask for help** - With good info collected
5. **Consider alternatives** - Maybe different approach needed

---

## Success Indicators

✅ Browser launches and logs in consistently
✅ Screenshots clearly show charts
✅ AI provides useful analysis
✅ Reports are generated correctly
✅ No mysterious errors in logs
✅ Performance is acceptable
✅ Costs are within budget

If you can check all these boxes, your POC is working! 🎉

---

*Last updated: November 2024*
