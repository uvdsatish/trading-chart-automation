"""
StockCharts.com Browser Controller
Handles authentication, navigation, and chart interaction
"""
import asyncio
import logging
from typing import Optional, Dict, List
from pathlib import Path
from datetime import datetime

from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from playwright.async_api import TimeoutError as PlaywrightTimeout
from .fullscreen_manager import FullscreenManager
from ..utils.excel_reader import ChartListConfigReader

logger = logging.getLogger(__name__)


class StockChartsController:
    """Manages browser automation for StockCharts.com"""
    
    def __init__(
        self,
        username: str,
        password: str,
        headless: bool = False,
        screenshot_dir: str = "screenshots",
        config: Optional[Dict] = None,
        session_id: Optional[str] = None
    ):
        self.username = username
        self.password = password
        self.headless = headless
        self.screenshot_dir = Path(screenshot_dir)
        self.config = config or {}
        self.session_id = session_id or "default"

        # Browser instances
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        # State tracking
        self.is_logged_in = False
        self.current_ticker: Optional[str] = None
        self.current_chartlist: Optional[str] = None  # Cache current ChartList to avoid re-selection

        # Session file path (unique per instance)
        self.session_file = Path(f"browser_session_{self.session_id}.json")

        # Ensure screenshot directory exists
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Start browser and create context"""
        logger.info("Initializing browser...")
        
        self.playwright = await async_playwright().start()
        
        # Launch browser with options
        if not self.headless:
            # Use FullscreenManager for aggressive fullscreen in headed mode
            browser_args = FullscreenManager.get_browser_args()
        else:
            # Minimal args for headless mode
            browser_args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-infobars',
                '--no-default-browser-check',
                '--no-first-run'
            ]

        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=browser_args
        )
        
        # Create context with viewport and user agent
        viewport = self.config.get('browser', {}).get('viewport', {})
        user_agent = self.config.get('browser', {}).get('user_agent')

        # Check for saved session state
        storage_state = None

        if self.session_file.exists():
            try:
                logger.info(f"Found saved browser session for {self.session_id}, attempting to restore...")
                storage_state = self.session_file.as_posix()
            except Exception as e:
                logger.warning(f"Could not load session file: {e}")

        # In headed mode (not headless), don't constrain viewport to allow full screen
        if not self.headless:
            # Use no_viewport=True for true fullscreen (Python-specific syntax)
            self.context = await self.browser.new_context(
                no_viewport=True,  # Proper Python syntax for no viewport constraint
                user_agent=user_agent,
                storage_state=storage_state  # Load saved session if available
            )
            width, height = FullscreenManager.get_monitor_dimensions()
            logger.info(f"Browser launched for {width}x{height} monitor with AGGRESSIVE FULLSCREEN")
        else:
            # Headless mode: use fixed viewport
            self.context = await self.browser.new_context(
                viewport=viewport or {'width': 1920, 'height': 1080},
                user_agent=user_agent,
                storage_state=storage_state  # Load saved session if available
            )
            logger.info(f"Browser launched with viewport: {viewport or {'width': 1920, 'height': 1080}}")

        # Create page
        self.page = await self.context.new_page()

        # Apply multiple fullscreen strategies for non-headless mode
        if not self.headless:
            # Navigate to blank page first
            await self.page.goto('about:blank')
            await asyncio.sleep(0.5)

            # Apply all fullscreen methods from FullscreenManager
            await FullscreenManager.apply_page_fullscreen(self.page)

            # Verify fullscreen was achieved
            is_fullscreen = await FullscreenManager.verify_fullscreen(self.page)
            if not is_fullscreen:
                logger.warning("[FULLSCREEN] Initial fullscreen verification failed, will retry after navigation")

        # Set default timeout
        timeout = self.config.get('stockcharts', {}).get('timeouts', {}).get('navigation', 30000)
        self.page.set_default_timeout(timeout)

        # Check if session was restored successfully
        if storage_state and self.session_file.exists():
            # Try navigating to a protected page to verify session is valid
            try:
                logger.info("Verifying restored session...")
                await self.page.goto("https://stockcharts.com/panels/", wait_until='domcontentloaded')

                # Check for logout link (indicates we're logged in)
                try:
                    await self.page.wait_for_selector("a:has-text('Log Out')", timeout=3000)
                    self.is_logged_in = True
                    logger.info("[SUCCESS] Session restored successfully - skipping login!")
                except:
                    logger.warning("Session expired or invalid, will need to login normally")
            except Exception as e:
                logger.warning(f"Could not verify session: {e}")

        logger.info("Browser initialized successfully")

    async def investigate_chartlist_navigation(self) -> Dict:
        """
        Investigation mode: Explore ChartList navigation on StockCharts.com
        Discovers how to navigate to ChartLists and open charts from them

        Returns:
            Dict with findings including URLs, selectors, and navigation strategy
        """
        findings = {
            "urls_discovered": [],
            "chartlist_selectors": [],
            "chart_selectors": [],
            "navigation_strategy": "",
            "screenshots": [],
            "errors": []
        }

        try:
            logger.info("=" * 70)
            logger.info("INVESTIGATION MODE: Exploring ChartList Navigation")
            logger.info("=" * 70)

            # First, ensure we're logged in
            if not self.is_logged_in:
                logger.info("Not logged in, attempting login first...")
                login_success = await self.login()
                if not login_success:
                    findings["errors"].append("Login failed - cannot investigate ChartLists")
                    return findings

            # Try different ChartList URLs
            chartlist_urls = [
                "https://stockcharts.com/freecharts/gallery.html",
                "https://stockcharts.com/def/servlet/Favorites.CServlet",
                "https://stockcharts.com/def/servlet/SC.web",
                "https://stockcharts.com/public/",
                "https://stockcharts.com/h-hc/ui"
            ]

            for url in chartlist_urls:
                logger.info(f"Trying ChartList URL: {url}")
                try:
                    await self.page.goto(url, wait_until='domcontentloaded', timeout=10000)
                    await asyncio.sleep(2)

                    # Capture screenshot
                    screenshot_path = await self._save_screenshot(f"chartlist_investigate_{url.split('/')[-1]}")
                    findings["screenshots"].append(str(screenshot_path))

                    # Look for ChartList indicators
                    chartlist_indicators = [
                        "text=Public ChartLists",
                        "text=My ChartLists",
                        "text=Your ChartLists",
                        "text=ChartList",
                        ".chartlist",
                        "[class*='chartlist']",
                        "[id*='chartlist']",
                        "a[href*='chartlist']"
                    ]

                    for selector in chartlist_indicators:
                        try:
                            count = await self.page.locator(selector).count()
                            if count > 0:
                                logger.info(f"[SUCCESS] Found ChartList element with selector: {selector} (count: {count})")
                                findings["chartlist_selectors"].append(selector)
                                findings["urls_discovered"].append(url)

                                # Try to find actual ChartList links
                                links = await self.page.locator("a").all()
                                for link in links[:20]:  # Check first 20 links
                                    text = await link.inner_text()
                                    href = await link.get_attribute("href") or ""
                                    if "chartlist" in text.lower() or "list" in text.lower():
                                        logger.info(f"Found potential ChartList link: {text} -> {href}")

                        except Exception as e:
                            logger.debug(f"Selector {selector} failed: {e}")

                except Exception as e:
                    logger.debug(f"URL {url} failed: {e}")
                    findings["errors"].append(f"Failed to load {url}: {str(e)}")

            # If we found ChartList pages, try to click into one
            if findings["chartlist_selectors"]:
                logger.info("Attempting to open a ChartList...")
                # This would click on the first ChartList found
                # We'll implement the actual clicking logic after we understand the structure

            findings["navigation_strategy"] = self._determine_navigation_strategy(findings)

        except Exception as e:
            logger.error(f"Investigation failed: {e}")
            findings["errors"].append(str(e))

        return findings

    def _determine_navigation_strategy(self, findings: Dict) -> str:
        """Determine the best navigation strategy based on findings"""
        if "https://stockcharts.com/freecharts/gallery.html" in findings["urls_discovered"]:
            return "Use gallery.html page to access ChartLists"
        elif findings["chartlist_selectors"]:
            return "ChartList elements found, can navigate via selectors"
        else:
            return "No clear ChartList navigation found - may need manual investigation"

    async def investigate_login_flow(self) -> Dict:
        """
        Investigation mode: Explore StockCharts.com login flow
        Captures detailed information about how to properly login

        Returns:
            Dict with findings including selectors, screenshots, and flow details
        """
        findings = {
            "urls_tried": [],
            "login_button_selectors_found": [],
            "form_selectors_found": [],
            "screenshots": [],
            "errors": []
        }

        try:
            logger.info("=" * 70)
            logger.info("INVESTIGATION MODE: Exploring StockCharts.com login flow")
            logger.info("=" * 70)

            # Try homepage first
            homepage_url = "https://stockcharts.com"
            logger.info(f"Step 1: Navigating to homepage: {homepage_url}")
            await self.page.goto(homepage_url, wait_until='networkidle')
            await asyncio.sleep(2)

            screenshot_path = await self._save_screenshot("investigate_01_homepage")
            findings["urls_tried"].append(homepage_url)
            findings["screenshots"].append(str(screenshot_path))
            logger.info(f"Screenshot saved: {screenshot_path}")

            # Look for "Log In" button in header/nav with multiple strategies
            login_button_selectors = [
                "a:has-text('Log In')",
                "button:has-text('Log In')",
                "a:has-text('LOGIN')",
                "a:has-text('Sign In')",
                "[href*='login']",
                "[class*='login']",
                "nav a:has-text('Log In')",
                "header a:has-text('Log In')",
                ".login-link",
                "#login-button"
            ]

            logger.info(f"Step 2: Searching for 'Log In' button with {len(login_button_selectors)} strategies...")

            login_button_found = None
            for selector in login_button_selectors:
                try:
                    count = await self.page.locator(selector).count()
                    if count > 0:
                        logger.info(f"[OK] Found login button with selector: {selector} (count: {count})")
                        findings["login_button_selectors_found"].append(selector)
                        if not login_button_found:
                            login_button_found = selector
                except Exception as e:
                    logger.debug(f"Selector '{selector}' failed: {e}")

            if not login_button_found:
                logger.warning("Could not find 'Log In' button with any selector")
                findings["errors"].append("No login button found on homepage")

                # Take screenshot showing what's visible
                await self._save_screenshot("investigate_02_no_login_button")

                # Try the old URL to see what's there
                old_url = "https://stockcharts.com/h-sc/ui"
                logger.info(f"Step 3: Trying old URL: {old_url}")
                await self.page.goto(old_url, wait_until='networkidle')
                await asyncio.sleep(2)
                screenshot_path = await self._save_screenshot("investigate_03_old_url")
                findings["urls_tried"].append(old_url)
                findings["screenshots"].append(str(screenshot_path))

                return findings

            # Click the login button
            logger.info(f"Step 3: Clicking login button with selector: {login_button_found}")
            await self.page.locator(login_button_found).first.click()
            await asyncio.sleep(2)

            screenshot_path = await self._save_screenshot("investigate_02_after_login_click")
            findings["screenshots"].append(str(screenshot_path))
            logger.info(f"Screenshot saved: {screenshot_path}")

            # Look for login form fields
            logger.info("Step 4: Searching for login form fields...")

            form_field_selectors = {
                "username": [
                    "input[name='username']",
                    "input[type='email']",
                    "input[name='email']",
                    "input[placeholder*='email' i]",
                    "input[placeholder*='username' i]",
                    "#username",
                    "#email"
                ],
                "password": [
                    "input[type='password']",
                    "input[name='password']",
                    "#password"
                ],
                "submit": [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button:has-text('Log In')",
                    "button:has-text('Sign In')",
                    "button:has-text('Submit')"
                ]
            }

            for field_type, selectors in form_field_selectors.items():
                logger.info(f"  Searching for {field_type} field...")
                for selector in selectors:
                    try:
                        count = await self.page.locator(selector).count()
                        if count > 0:
                            logger.info(f"  [OK] Found {field_type} with selector: {selector} (count: {count})")
                            findings["form_selectors_found"].append({
                                "field": field_type,
                                "selector": selector,
                                "count": count
                            })
                    except Exception as e:
                        logger.debug(f"  Selector '{selector}' failed: {e}")

            # Check current URL (might have redirected)
            current_url = self.page.url
            logger.info(f"Step 5: Current URL after login button click: {current_url}")
            findings["urls_tried"].append(current_url)

            # Final screenshot
            screenshot_path = await self._save_screenshot("investigate_03_final_state")
            findings["screenshots"].append(str(screenshot_path))

            logger.info("=" * 70)
            logger.info("INVESTIGATION COMPLETE")
            logger.info("=" * 70)
            logger.info(f"Login button selectors found: {len(findings['login_button_selectors_found'])}")
            logger.info(f"Form fields found: {len(findings['form_selectors_found'])}")
            logger.info(f"Screenshots saved: {len(findings['screenshots'])}")

            return findings

        except Exception as e:
            logger.error(f"Investigation failed: {e}")
            findings["errors"].append(str(e))
            await self._save_screenshot("investigate_error")
            return findings

    async def investigate_ui_elements(self, ticker: str = "AAPL") -> Dict:
        """
        Investigation mode: Find selectors for search box and ChartStyle presets

        Returns:
            Dict with findings about UI elements
        """
        findings = {
            "search_box_selectors": [],
            "chartstyle_presets": [],
            "screenshots": [],
            "errors": []
        }

        try:
            logger.info("=" * 70)
            logger.info("UI ELEMENT INVESTIGATION: Search Box & ChartStyle Presets")
            logger.info("=" * 70)

            # STEP 1: Find search box
            logger.info("\nStep 1: Searching for 'Enter Symbol or Name' search box...")

            search_box_selectors = [
                "input[placeholder*='Enter Symbol' i]",
                "input[placeholder*='Symbol or Name' i]",
                "input[name='s']",
                "input[name='symbol']",
                ".symbol-search",
                "#symbol",
                "input[type='text']"
            ]

            for selector in search_box_selectors:
                try:
                    count = await self.page.locator(selector).count()
                    if count > 0:
                        # Get placeholder text
                        try:
                            placeholder = await self.page.locator(selector).first.get_attribute("placeholder")
                            logger.info(f"  [FOUND] {selector} - placeholder: '{placeholder}'")
                            findings["search_box_selectors"].append({
                                "selector": selector,
                                "placeholder": placeholder,
                                "count": count
                            })
                        except:
                            logger.info(f"  [FOUND] {selector} (count: {count})")
                            findings["search_box_selectors"].append({
                                "selector": selector,
                                "count": count
                            })
                except Exception as e:
                    logger.debug(f"  Selector failed: {selector} - {e}")

            # Take screenshot of current page
            screenshot_path = await self._save_screenshot("investigate_ui_search_box")
            findings["screenshots"].append(str(screenshot_path))
            logger.info(f"\n  Screenshot saved: {screenshot_path}")

            # STEP 2: Find ChartStyle presets (vertical boxes on left)
            logger.info("\nStep 2: Searching for ChartStyle preset boxes...")
            logger.info("  Looking for: '60 mins default', '5 mins default', etc.")

            # Try to find all links with "default" or "mins" text
            chartstyle_patterns = [
                "a:has-text('default')",
                "a:has-text('mins')",
                "a:has-text('60')",
                "a:has-text('5')",
                "div:has-text('default')",
                ".chartstyle",
                ".preset",
                "[data-chartstyle]"
            ]

            for pattern in chartstyle_patterns:
                try:
                    elements = await self.page.locator(pattern).all()
                    if len(elements) > 0:
                        logger.info(f"  [FOUND] {len(elements)} elements matching: {pattern}")

                        # Get text of first few elements
                        for i, elem in enumerate(elements[:5]):  # Show first 5
                            try:
                                text = await elem.text_content()
                                if text and text.strip():
                                    logger.info(f"    Element {i+1}: '{text.strip()}'")
                                    findings["chartstyle_presets"].append({
                                        "selector": pattern,
                                        "text": text.strip(),
                                        "index": i
                                    })
                            except:
                                pass
                except Exception as e:
                    logger.debug(f"  Pattern failed: {pattern} - {e}")

            # STEP 3: Look for any element containing "60 mins default" or "5 mins default" explicitly
            logger.info("\nStep 3: Searching for exact preset names...")

            exact_presets = ["60 mins default", "5 mins default", "60Mins_Default", "5mins_Default"]
            for preset_name in exact_presets:
                try:
                    selector = f":has-text('{preset_name}')"
                    count = await self.page.locator(selector).count()
                    if count > 0:
                        logger.info(f"  [FOUND] '{preset_name}' appears {count} times on page")
                        findings["chartstyle_presets"].append({
                            "preset_name": preset_name,
                            "count": count
                        })
                except Exception as e:
                    logger.debug(f"  Preset search failed: {preset_name} - {e}")

            screenshot_path = await self._save_screenshot("investigate_ui_chartstyles")
            findings["screenshots"].append(str(screenshot_path))

            # STEP 4: Navigate to a chart to see ChartStyle boxes on the chart page
            logger.info(f"\nStep 4: Navigating to {ticker} chart to find ChartStyle boxes...")

            base_url = self.config.get('stockcharts', {}).get('base_url', 'https://stockcharts.com')
            chart_url = f"{base_url}/h-sc/ui?s={ticker}"
            await self.page.goto(chart_url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(3)

            screenshot_path = await self._save_screenshot(f"investigate_ui_chart_{ticker}")
            findings["screenshots"].append(str(screenshot_path))
            logger.info(f"  Chart screenshot: {screenshot_path}")

            # Now look for ChartStyle boxes on the CHART page (far left edge)
            logger.info("\n  Searching for ChartStyle numbered boxes on chart (far left edge)...")

            # These are numbered boxes (1, 2, 3, etc.) stacked vertically on the left edge of chart
            # They likely have tooltips/titles showing the preset names
            chartstyle_box_selectors = [
                "a.chartStyle",
                "a[class*='chartStyle']",
                "a[class*='chart-style']",
                "div.chartStyle",
                "div[class*='chartStyle']",
                "button.chartStyle",
                "a[title]",  # Links with title attribute (tooltip)
                ".chart-settings a",
                ".chart-presets a",
                "a[onclick*='chartStyle']",
                "a[onclick*='chart']"
            ]

            for selector in chartstyle_box_selectors:
                try:
                    count = await self.page.locator(selector).count()
                    if count > 0:
                        logger.info(f"  [FOUND] {selector} (count: {count})")
                        # Get first few elements and their titles/text
                        elements = await self.page.locator(selector).all()
                        for i, elem in enumerate(elements[:10]):
                            try:
                                # Get title attribute (tooltip)
                                title = await elem.get_attribute("title")
                                text = await elem.text_content()

                                info = f"    Box {i+1}: "
                                if text and text.strip():
                                    info += f"text='{text.strip()}'"
                                if title:
                                    info += f" title='{title}'"

                                if info != f"    Box {i+1}: ":
                                    logger.info(info)
                                    findings["chartstyle_presets"].append({
                                        "selector": selector,
                                        "text": text.strip() if text else "",
                                        "title": title,
                                        "index": i,
                                        "location": "chart_left_edge"
                                    })
                            except:
                                pass
                except Exception as e:
                    logger.debug(f"  Selector failed: {selector}")

            # Also try to find elements by looking for common ChartStyle names
            logger.info("\n  Searching for specific preset boxes by title attribute...")
            specific_presets = ["60Mins_Default", "5mins_Default", "60 mins default", "5 mins default"]
            for preset in specific_presets:
                try:
                    # Search by title attribute
                    selector = f"a[title='{preset}']"
                    count = await self.page.locator(selector).count()
                    if count > 0:
                        logger.info(f"  [FOUND] Preset '{preset}' in title attribute (count: {count})")
                        findings["chartstyle_presets"].append({
                            "preset_name": preset,
                            "selector": selector,
                            "count": count,
                            "location": "chart_left_edge"
                        })
                except:
                    pass

            logger.info("\n" + "=" * 70)
            logger.info("INVESTIGATION COMPLETE")
            logger.info("=" * 70)
            logger.info(f"Search box selectors found: {len(findings['search_box_selectors'])}")
            logger.info(f"ChartStyle elements found: {len(findings['chartstyle_presets'])}")

            return findings

        except Exception as e:
            logger.error(f"Investigation failed: {e}")
            findings["errors"].append(str(e))
            return findings

    async def investigate_timeframe_urls(self, ticker: str) -> Dict:
        """
        Investigation mode: Test different URL parameters to discover how to control timeframes

        Args:
            ticker: Stock symbol to test with

        Returns:
            Dict with findings about which URL patterns work for each timeframe
        """
        findings = {
            "ticker": ticker,
            "patterns_tested": [],
            "screenshots": [],
            "working_patterns": {},
            "errors": []
        }

        try:
            logger.info("=" * 70)
            logger.info(f"TIMEFRAME URL INVESTIGATION: {ticker}")
            logger.info("=" * 70)

            base_url = self.config.get('stockcharts', {}).get('base_url', 'https://stockcharts.com')

            # Define URL patterns to test
            test_patterns = {
                "baseline": {
                    "params": f"s={ticker}",
                    "expected": "Default (probably daily)"
                },
                "daily_p_D": {
                    "params": f"s={ticker}&p=D",
                    "expected": "Daily"
                },
                "daily_period_daily": {
                    "params": f"s={ticker}&period=daily",
                    "expected": "Daily"
                },
                "daily_p_1D": {
                    "params": f"s={ticker}&p=1D",
                    "expected": "Daily"
                },
                "60min_p_I_i_60": {
                    "params": f"s={ticker}&p=I&i=60",
                    "expected": "60-minute"
                },
                "60min_period_intraday_60": {
                    "params": f"s={ticker}&period=intraday&interval=60",
                    "expected": "60-minute"
                },
                "60min_p_60min": {
                    "params": f"s={ticker}&p=60min",
                    "expected": "60-minute"
                },
                "5min_p_I_i_5": {
                    "params": f"s={ticker}&p=I&i=5",
                    "expected": "5-minute"
                },
                "5min_period_intraday_5": {
                    "params": f"s={ticker}&period=intraday&interval=5",
                    "expected": "5-minute"
                },
                "5min_p_5min": {
                    "params": f"s={ticker}&p=5min",
                    "expected": "5-minute"
                },
                "weekly_p_W": {
                    "params": f"s={ticker}&p=W",
                    "expected": "Weekly"
                },
                "monthly_p_M": {
                    "params": f"s={ticker}&p=M",
                    "expected": "Monthly"
                }
            }

            for pattern_name, pattern_info in test_patterns.items():
                try:
                    url = f"{base_url}/h-sc/ui?{pattern_info['params']}"
                    logger.info(f"\nTesting pattern: {pattern_name}")
                    logger.info(f"  URL: {url}")
                    logger.info(f"  Expected: {pattern_info['expected']}")

                    # Navigate to URL
                    await self.page.goto(url, wait_until='networkidle', timeout=15000)
                    await asyncio.sleep(3)  # Wait for chart to render

                    # Check final URL (might redirect)
                    final_url = self.page.url
                    logger.info(f"  Final URL: {final_url}")

                    # Try to get page title
                    try:
                        title = await self.page.title()
                        logger.info(f"  Page title: {title}")
                    except:
                        title = "Unknown"

                    # Capture screenshot
                    screenshot_name = f"investigate_tf_{pattern_name}_{ticker}"
                    screenshot_path = await self._save_screenshot(screenshot_name)
                    logger.info(f"  Screenshot: {screenshot_path}")

                    # Record findings
                    findings["patterns_tested"].append({
                        "pattern_name": pattern_name,
                        "url": url,
                        "final_url": final_url,
                        "expected": pattern_info['expected'],
                        "title": title,
                        "screenshot": str(screenshot_path)
                    })

                    findings["screenshots"].append(str(screenshot_path))

                    logger.info(f"  [OK] Test completed")

                except Exception as e:
                    logger.error(f"  [ERROR] Pattern test failed: {e}")
                    findings["errors"].append({
                        "pattern": pattern_name,
                        "error": str(e)
                    })

                # Small delay between tests
                await asyncio.sleep(1)

            logger.info("\n" + "=" * 70)
            logger.info("INVESTIGATION COMPLETE")
            logger.info("=" * 70)
            logger.info(f"Patterns tested: {len(findings['patterns_tested'])}")
            logger.info(f"Screenshots captured: {len(findings['screenshots'])}")
            logger.info(f"Errors encountered: {len(findings['errors'])}")

            return findings

        except Exception as e:
            logger.error(f"Investigation failed: {e}")
            findings["errors"].append({"general": str(e)})
            return findings

    async def login(self) -> bool:
        """
        Authenticate with StockCharts.com

        NEW FLOW (based on investigation):
        1. Navigate to homepage
        2. Click "Log In" button in header (redirects to login page)
        3. Fill credentials on login page
        4. Submit and verify

        Returns:
            bool: True if login successful, False otherwise
        """
        if self.is_logged_in:
            logger.info("Already logged in")
            return True

        try:
            logger.info("Attempting login to StockCharts.com...")

            # STEP 1: Navigate directly to login page (skip homepage for speed)
            login_url = "https://stockcharts.com/login/index.php"
            logger.info(f"Step 1: Navigating directly to login page: {login_url}")
            await self.page.goto(login_url, wait_until='domcontentloaded')

            # Wait for login form to be visible
            try:
                await self.page.wait_for_selector("input[type='email']", state='visible', timeout=3000)
            except:
                await asyncio.sleep(0.5)  # Short fallback

            await self._save_screenshot("01_login_page")

            # STEP 2: Fill in login form (we're already on the login page)
            logger.info("Step 2: Filling login credentials...")

            # Find and fill username field (USER ID / EMAIL)
            username_selectors = [
                "input[type='email']",
                "input[name='email']",
                "input[name='username']",
                "input[placeholder*='email' i]",
                "input[placeholder*='user' i]",
                "#username",
                "#email"
            ]
            
            username_filled = False
            for selector in username_selectors:
                try:
                    if await self.page.locator(selector).count() > 0:
                        await self.page.fill(selector, self.username)
                        username_filled = True
                        logger.info(f"Filled username using selector: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            if not username_filled:
                logger.error("Could not find username field")
                await self._save_screenshot("error_no_username_field")
                return False
            
            # Find and fill password field
            password_selectors = [
                "input[name='password']",
                "input[type='password']",
                "#password"
            ]
            
            password_filled = False
            for selector in password_selectors:
                try:
                    if await self.page.locator(selector).count() > 0:
                        await self.page.fill(selector, self.password)
                        password_filled = True
                        logger.info(f"Filled password using selector: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            if not password_filled:
                logger.error("Could not find password field")
                await self._save_screenshot("error_no_password_field")
                return False
            
            await self._save_screenshot("02_credentials_filled")

            # STEP 3: Click the submit button
            logger.info("Step 3: Submitting login form...")
            submit_button_selectors = [
                "button:has-text('Log In')",
                "button[type='submit']",
                "input[type='submit']",
                "button:has-text('Sign In')",
                "button:has-text('Submit')"
            ]
            
            submit_clicked = False
            for selector in submit_button_selectors:
                try:
                    if await self.page.locator(selector).count() > 0:
                        logger.info(f"Found submit button with selector: {selector}")
                        await self.page.locator(selector).first.click()
                        submit_clicked = True
                        logger.info("Clicked submit button")
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue

            if not submit_clicked:
                # Try pressing Enter as fallback
                logger.warning("Could not find submit button, trying Enter key as fallback")
                await self.page.keyboard.press('Enter')

            # Wait for navigation after login (OPTIMIZED)
            logger.info("Waiting for login to complete...")

            # Wait for either logout link (success) or URL change (navigation)
            try:
                await self.page.wait_for_selector("a:has-text('Log Out')", timeout=5000)
                logger.info("Login successful - found logout link")
            except:
                # Fallback: wait for URL to change from login page
                try:
                    await self.page.wait_for_url(lambda url: 'login' not in url.lower(), timeout=5000)
                    logger.info("Login successful - navigated away from login page")
                except:
                    # Last fallback: brief wait
                    await asyncio.sleep(2)
                    logger.warning("Could not detect login completion, continuing...")

            await self._save_screenshot("03_after_login_attempt")

            # STEP 4: Verify login success
            logger.info("Step 4: Verifying login success...")

            # Check current URL (should not be login page anymore)
            final_url = self.page.url
            logger.info(f"Final URL after login: {final_url}")

            # Look for indicators of successful login
            success_indicators = [
                "text=Your Dashboard",
                "text=My Account",
                "text=Log Out",
                "text=Logout",
                "a:has-text('Log Out')",
                "[href*='logout']",
                "[href*='signout']"
            ]
            
            for indicator in success_indicators:
                try:
                    if await self.page.locator(indicator).count() > 0:
                        self.is_logged_in = True
                        logger.info("[SUCCESS] Login successful!")

                        # Save session state for future runs
                        try:
                            await self.context.storage_state(path=self.session_file.as_posix())
                            logger.info(f"Session saved to {self.session_file} for future use")
                        except Exception as e:
                            logger.warning(f"Could not save session: {e}")

                        return True
                except:
                    continue
            
            # Check for error messages
            error_indicators = [
                "text=Invalid",
                "text=incorrect",
                "text=error",
                ".error",
                ".alert-danger"
            ]
            
            for indicator in error_indicators:
                try:
                    if await self.page.locator(indicator).count() > 0:
                        error_text = await self.page.locator(indicator).text_content()
                        logger.error(f"Login failed: {error_text}")
                        return False
                except:
                    continue
            
            # If we're still on a login-looking page, assume failure
            current_url = self.page.url
            if 'login' in current_url.lower() or 'signin' in current_url.lower():
                logger.warning("Still on login page - login may have failed")
                return False
            
            # If no error but no success indicator, cautiously assume success
            logger.info("No explicit success indicator, but navigated away from login page")
            self.is_logged_in = True
            return True
            
        except PlaywrightTimeout as e:
            logger.error(f"Login timeout: {e}")
            await self._save_screenshot("error_login_timeout")
            return False
        except Exception as e:
            logger.error(f"Login error: {e}")
            await self._save_screenshot("error_login_exception")
            return False
    
    async def enter_ticker_in_search_box(self, ticker: str) -> bool:
        """
        Enter ticker in the "Enter Symbol or Name" search box and navigate to chart

        Args:
            ticker: Stock symbol to search for

        Returns:
            bool: True if successful
        """
        try:
            logger.info(f"Entering ticker '{ticker}' in search box...")

            # Find the search box (from investigation: input[placeholder*='Enter Symbol' i])
            search_box_selector = "input[placeholder*='Enter Symbol' i]"

            # Wait for search box to be visible
            await self.page.wait_for_selector(search_box_selector, timeout=10000)

            # Clear any existing text and type ticker
            await self.page.fill(search_box_selector, ticker)
            logger.info(f"Typed '{ticker}' into search box")

            await asyncio.sleep(1)

            # Press Enter or click Go button
            go_button_selectors = [
                "button:has-text('Go')",
                "input[value='Go']",
                "button[type='submit']"
            ]

            button_clicked = False
            for selector in go_button_selectors:
                try:
                    if await self.page.locator(selector).count() > 0:
                        await self.page.locator(selector).first.click()
                        logger.info(f"Clicked Go button")
                        button_clicked = True
                        break
                except:
                    continue

            if not button_clicked:
                # Fallback: press Enter
                logger.info("Go button not found, pressing Enter...")
                await self.page.press(search_box_selector, "Enter")

            # Wait for chart to load (OPTIMIZED)
            logger.info("Waiting for chart to load...")

            # Wait for chart image to be visible instead of fixed sleep
            try:
                await self.page.wait_for_selector('.chart-image, img[src*="chart"], #chartImg',
                                                 state='visible', timeout=5000)
                logger.info("Chart image loaded")
            except:
                # Fallback: wait for URL to contain ticker
                try:
                    await self.page.wait_for_url(lambda url: ticker in url or 's=' in url.lower(),
                                                timeout=3000)
                except:
                    await asyncio.sleep(2)  # Brief fallback
                    logger.warning("Could not verify chart load, continuing...")

            # Verify we're on a chart page
            current_url = self.page.url
            logger.info(f"Navigated to: {current_url}")

            if ticker.lower() in current_url.lower() or 's=' in current_url.lower():
                logger.info(f"[SUCCESS] Successfully navigated to {ticker} chart")
                self.current_ticker = ticker

                # Maximize chart area for better viewing in fullscreen
                await self.maximize_chart_area()

                return True
            else:
                logger.warning(f"URL doesn't contain ticker, but continuing...")
                self.current_ticker = ticker
                return True

        except Exception as e:
            logger.error(f"Failed to enter ticker in search box: {e}")
            await self._save_screenshot(f"error_search_box_{ticker}")
            return False


    async def navigate_via_chartlist_dropdown(
        self,
        chartlist_name: str,
        chart_name: str
    ) -> bool:
        """
        Navigate to a specific chart within a ChartList using dropdown navigation
        OPTIMIZED: Caches current ChartList to avoid redundant selections

        Args:
            chartlist_name: Name of the ChartList (e.g., "My Watchlist", "S2_SetUps")
            chart_name: Name of the chart within that ChartList

        Returns:
            bool: True if successful
        """
        try:
            import time
            start_time = time.time()

            # Check if we need to switch ChartList (OPTIMIZATION)
            need_chartlist_switch = (self.current_chartlist != chartlist_name)

            if need_chartlist_switch:
                logger.info(f"[CACHE MISS] Navigating to new ChartList: {chartlist_name} > {chart_name}")
                logger.info(f"Previous ChartList was: {self.current_chartlist}")

                # Step 1: Click ChartList dropdown button
                chartlist_button_selector = "#chart-list-dropdown-menu-toggle-button"
                chartlist_button = await self.page.query_selector(chartlist_button_selector)

                if not chartlist_button:
                    logger.warning(f"ChartList dropdown button not found with selector: {chartlist_button_selector}")
                    # Fallback to direct navigation
                    logger.info("Falling back to direct URL navigation")
                    return await self.navigate_to_chart(chart_name)

                # Click to open ChartList dropdown
                logger.info("Clicking ChartList dropdown button...")
                await chartlist_button.click()

                # Smart wait for dropdown to appear
                try:
                    await self.page.wait_for_selector('.chartlist-dropdown-menu', state='visible', timeout=3000)
                except:
                    await asyncio.sleep(1)  # Fallback to fixed wait

                # Look for the ChartList option in the dropdown menu
                try:
                    # Try to find and click the ChartList item
                    chartlist_item = await self.page.query_selector(f"text={chartlist_name}")
                    if chartlist_item:
                        logger.info(f"Clicking ChartList: {chartlist_name}")
                        await chartlist_item.click()
                        # Update cache AFTER successful selection
                        self.current_chartlist = chartlist_name
                        await asyncio.sleep(2)  # Wait for charts to load
                    else:
                        # Try with partial match
                        chartlist_item = await self.page.query_selector(f"*:has-text('{chartlist_name}')")
                        if chartlist_item:
                            await chartlist_item.click()
                            self.current_chartlist = chartlist_name  # Update cache
                            await asyncio.sleep(2)
                        else:
                            logger.warning(f"ChartList '{chartlist_name}' not found in dropdown")
                            return await self.navigate_to_chart(chart_name)

                except Exception as e:
                    logger.warning(f"Could not select ChartList: {e}")
                    return await self.navigate_to_chart(chart_name)
            else:
                logger.info(f"[CACHE HIT] Already in ChartList '{chartlist_name}', skipping ChartList selection")
                logger.info(f"Navigating directly to chart: {chart_name}")

            # Step 2: Click Chart dropdown button (now should show charts from selected list)
            chart_button_selector = "#charts-dropdown-menu-toggle-button"
            chart_button = await self.page.query_selector(chart_button_selector)

            if not chart_button:
                logger.warning(f"Chart dropdown button not found with selector: {chart_button_selector}")
                return await self.navigate_to_chart(chart_name)

            # Click to open Chart dropdown
            logger.info("Clicking Chart dropdown button...")
            await chart_button.click()
            await asyncio.sleep(1)  # Wait for dropdown to appear

            # Select the specific chart
            try:
                # Try to find and click the chart item
                chart_item = await self.page.query_selector(f"text={chart_name}")
                if chart_item:
                    logger.info(f"Clicking Chart: {chart_name}")
                    await chart_item.click()
                else:
                    # Try with partial match
                    chart_item = await self.page.query_selector(f"*:has-text('{chart_name}')")
                    if chart_item:
                        await chart_item.click()
                    else:
                        logger.warning(f"Chart '{chart_name}' not found in dropdown")
                        return await self.navigate_to_chart(chart_name)

            except Exception as e:
                logger.warning(f"Could not select chart: {e}")
                return await self.navigate_to_chart(chart_name)

            # Wait for chart to load (OPTIMIZED: replaced networkidle with domcontentloaded)
            try:
                await self.page.wait_for_load_state('domcontentloaded', timeout=5000)
                # Wait for chart image to be visible
                await self.page.wait_for_selector('.chart-image', state='visible', timeout=5000)
            except:
                # Fallback to fixed wait if selectors not found
                await asyncio.sleep(2)
                logger.warning("Could not wait for chart image, continuing...")

            elapsed = time.time() - start_time
            cache_status = "CACHE HIT" if not need_chartlist_switch else "CACHE MISS"
            logger.info(f"[SUCCESS] Navigated to {chartlist_name} > {chart_name} in {elapsed:.2f}s ({cache_status})")
            return True

        except Exception as e:
            logger.error(f"Error navigating via dropdown: {e}")
            # Fallback to direct navigation
            logger.info("Falling back to direct URL navigation due to error")
            return await self.navigate_to_chart(chart_name)

    async def navigate_to_chart(
        self,
        ticker: str,
        chart_type: str = "daily",
        save_screenshot: bool = True
    ) -> bool:
        """
        Navigate to specific ticker chart
        
        Args:
            ticker: Stock symbol (e.g., "AAPL")
            chart_type: Type of chart (daily, weekly, intraday)
            save_screenshot: Whether to save screenshot after loading
            
        Returns:
            bool: True if navigation successful
        """
        if not self.is_logged_in:
            logger.warning("Not logged in, attempting login first...")
            if not await self.login():
                return False
        
        try:
            logger.info(f"Navigating to {ticker} chart...")
            
            # Construct chart URL (adjust based on StockCharts URL structure)
            # Example: https://stockcharts.com/h-sc/ui?s=AAPL
            base_url = self.config.get('stockcharts', {}).get('base_url', 
                                                              'https://stockcharts.com')
            chart_url = f"{base_url}/h-sc/ui?s={ticker}"
            
            # OPTIMIZED: Use domcontentloaded instead of networkidle
            await self.page.goto(chart_url, wait_until='domcontentloaded')

            # Wait for chart to be visible instead of fixed sleep
            try:
                await self.page.wait_for_selector('.chart-image, img[src*="chart"], #chartImg',
                                                 state='visible', timeout=3000)
            except:
                await asyncio.sleep(1)  # Brief fallback if chart not found
            
            self.current_ticker = ticker
            
            if save_screenshot:
                await self._save_screenshot(f"chart_{ticker}")
            
            logger.info(f"Successfully loaded {ticker} chart")
            return True
            
        except Exception as e:
            logger.error(f"Failed to navigate to chart: {e}")
            await self._save_screenshot(f"error_navigate_{ticker}")
            return False

    async def maximize_chart_area(self):
        """
        Inject CSS to maximize chart viewing area by hiding unnecessary elements
        and expanding the chart to use full viewport
        """
        try:
            logger.info("Injecting CSS to maximize chart area...")

            # Inject CSS to maximize chart viewing area
            await self.page.add_style_tag(content="""
                /* Remove body margins and padding */
                body {
                    margin: 0 !important;
                    padding: 0 !important;
                    overflow: hidden !important;
                }

                /* Hide ads, banners, and unnecessary UI elements */
                .sidebar-ad, .top-banner, .footer-links, .advertisement {
                    display: none !important;
                }

                /* Hide header elements if they're not essential */
                .site-header, .nav-secondary {
                    display: none !important;
                }

                /* Maximize the main chart container */
                #chart-container, .chart-wrapper, .chart-content, #chartImg {
                    width: 100vw !important;
                    height: 100vh !important;
                    max-width: none !important;
                    max-height: none !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }

                /* Expand the chart image itself */
                .chart-image, img[src*='chart'] {
                    width: 100% !important;
                    height: auto !important;
                    max-width: none !important;
                }

                /* Hide or minimize the ChartStyle buttons sidebar if not needed */
                .chart-style-buttons {
                    opacity: 0.3;  /* Make semi-transparent instead of hiding */
                    transition: opacity 0.3s;
                }

                .chart-style-buttons:hover {
                    opacity: 1;  /* Show on hover */
                }

                /* Remove any fixed width constraints */
                .container, .content-wrapper {
                    max-width: none !important;
                    width: 100% !important;
                }
            """)

            logger.info("CSS injection successful - chart area maximized")

        except Exception as e:
            logger.warning(f"Could not inject CSS to maximize chart area: {e}")

    async def capture_chart_screenshot(
        self,
        ticker: Optional[str] = None,
        full_page: bool = False
    ) -> Path:
        """
        Capture screenshot of current chart
        
        Args:
            ticker: Stock symbol (for filename), uses current_ticker if None
            full_page: Whether to capture full page or just viewport
            
        Returns:
            Path: Path to saved screenshot
        """
        ticker = ticker or self.current_ticker or "unknown"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{ticker}_{timestamp}.png"
        filepath = self.screenshot_dir / filename
        
        await self.page.screenshot(path=str(filepath), full_page=full_page)
        logger.info(f"Screenshot saved: {filepath}")
        
        return filepath

    async def select_timeframe_from_dropdown(self, timeframe: str) -> bool:
        """
        Select timeframe using the Period dropdown

        Args:
            timeframe: One of: "Daily", "Weekly", "Monthly", "Intraday 60 min", "Intraday 5 min", etc.

        Returns:
            bool: True if successful
        """
        try:
            logger.info(f"Selecting timeframe: {timeframe}")

            # Common selectors for the Period dropdown
            period_dropdown_selectors = [
                "select#period",
                "select[name='period']",
                "select.period-select",
                "#Period",
                "//select[contains(@id, 'period') or contains(@id, 'Period')]"
            ]

            dropdown_found = False
            for selector in period_dropdown_selectors:
                try:
                    count = await self.page.locator(selector).count()
                    if count > 0:
                        logger.info(f"Found Period dropdown with selector: {selector}")

                        # Select the option by visible text
                        await self.page.select_option(selector, label=timeframe)
                        logger.info(f"Selected '{timeframe}' from dropdown")

                        dropdown_found = True

                        # Wait for chart to reload
                        await asyncio.sleep(3)

                        return True
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue

            if not dropdown_found:
                logger.error("Could not find Period dropdown")
                await self._save_screenshot("error_no_period_dropdown")
                return False

        except Exception as e:
            logger.error(f"Failed to select timeframe: {e}")
            await self._save_screenshot(f"error_select_timeframe_{timeframe}")
            return False

    async def get_chart_element(self) -> Optional[str]:
        """
        Get the main chart image element
        
        Returns:
            Optional[str]: Selector for chart element if found
        """
        chart_selectors = [
            ".chart-image",
            "#chartImg",
            "img[alt*='chart' i]",
            "img[src*='chart' i]",
            "canvas",
            "svg.chart"
        ]
        
        for selector in chart_selectors:
            try:
                if await self.page.locator(selector).count() > 0:
                    logger.info(f"Found chart element: {selector}")
                    return selector
            except:
                continue
        
        logger.warning("Could not find chart element")
        return None
    
    async def modify_chart_settings(
        self,
        timeframe: Optional[str] = None,
        indicators: Optional[List[str]] = None
    ):
        """
        Modify chart settings (timeframe, indicators, etc.)
        
        Args:
            timeframe: Chart timeframe (e.g., "Daily", "Weekly")
            indicators: List of indicators to add
        """
        # This is highly site-specific and would need to be adjusted
        # based on StockCharts.com's actual UI
        logger.info("Modifying chart settings...")
        
        if timeframe:
            # Example: Look for timeframe dropdown
            try:
                await self.page.click("select[name='timeframe']")
                await self.page.select_option("select[name='timeframe']", timeframe)
                logger.info(f"Set timeframe to {timeframe}")
            except Exception as e:
                logger.warning(f"Could not set timeframe: {e}")
        
        if indicators:
            # Example: Add indicators
            for indicator in indicators:
                try:
                    # This would need actual StockCharts.com UI logic
                    logger.info(f"Adding indicator: {indicator}")
                    # await self.page.click(f"button:has-text('{indicator}')")
                except Exception as e:
                    logger.warning(f"Could not add indicator {indicator}: {e}")
    
    async def _save_screenshot(self, name: str):
        """Internal helper to save debug screenshots"""
        try:
            filepath = self.screenshot_dir / f"debug_{name}.png"
            await self.page.screenshot(path=str(filepath))
            logger.debug(f"Debug screenshot saved: {filepath}")
        except Exception as e:
            logger.debug(f"Could not save debug screenshot: {e}")

    async def open_multi_timeframe_tabs(
        self,
        ticker: str,
        chartstyle_box_numbers: List[int] = [1, 4, 7, 10]
    ) -> Dict[str, Dict]:
        """
        Open multiple tabs with different timeframes for the same ticker

        NEW WORKFLOW:
        1. Use main page to enter ticker in search box -> loads Daily chart (Tab 1)
        2. Duplicate tab -> click ChartStyle box #4 for Weekly (Tab 2)
        3. Duplicate tab -> click ChartStyle box #7 for 60min (Tab 3)
        4. Duplicate tab -> click ChartStyle box #10 for 5min (Tab 4)

        Args:
            ticker: Stock symbol
            chartstyle_box_numbers: List of ChartStyle box numbers (1-indexed, e.g., [1, 4, 7, 10])
                                   These are the vertical grey boxes on the far left edge

        Returns:
            Dict[str, Dict]: Dictionary mapping timeframe names to info dicts containing:
                            {"page": Page, "screenshot_path": str, "box_number": int}
        """
        logger.info(f"Opening {len(chartstyle_box_numbers)} timeframe tabs for {ticker}...")
        logger.info(f"ChartStyle box numbers: {chartstyle_box_numbers}")

        pages = {}
        # Enhanced mapping with Weekly timeframe
        timeframe_names = {
            1: "Daily",
            4: "Weekly",  # Added Weekly
            7: "60min",
            10: "5min"
        }  # Map box numbers to timeframe names

        try:
            # TAB 1: Use main page to enter ticker in search box
            logger.info(f"[Tab 1/{len(chartstyle_box_numbers)}] Entering {ticker} in search box...")

            success = await self.enter_ticker_in_search_box(ticker)
            if not success:
                logger.error("Failed to navigate to chart via search box")
                return pages

            # Optimized: Reduced wait time from 3s to 2s
            await asyncio.sleep(2)

            # Apply StockCharts-specific fullscreen maximization
            if not self.headless:
                await FullscreenManager.maximize_stockcharts_chart(self.page)
                logger.info("[FULLSCREEN] Applied StockCharts chart maximization")

            # Store the main page as first tab
            first_box = chartstyle_box_numbers[0]
            timeframe_name = timeframe_names.get(first_box, f"Box{first_box}")
            logger.info(f"[Tab 1] Chart loaded (ChartStyle box #{first_box} = {timeframe_name})")

            # Capture screenshot of Tab 1
            screenshot_path = self.screenshot_dir / f"{ticker}_tab1_box{first_box}_{timeframe_name}.png"
            await self.page.screenshot(path=str(screenshot_path))
            logger.info(f"[Tab 1] Screenshot saved: {screenshot_path}")

            # Store page info with screenshot path
            pages[timeframe_name] = {
                "page": self.page,
                "screenshot_path": str(screenshot_path),
                "box_number": first_box
            }

            # Get current URL to duplicate for other tabs
            base_chart_url = self.page.url
            logger.info(f"  Base chart URL: {base_chart_url}")

            # Pre-create all tabs at once for faster operations
            new_pages = []
            for i, box_number in enumerate(chartstyle_box_numbers[1:], 2):
                logger.info(f"[Tab {i}] Pre-creating browser tab...")
                new_page = await self.context.new_page()
                new_pages.append((i, box_number, new_page))

            # TAB 2 and beyond: Navigate pre-created tabs and click numbered ChartStyle box
            for i, box_number, page in new_pages:
                try:
                    timeframe_name = timeframe_names.get(box_number, f"Box{box_number}")
                    logger.info(f"[Tab {i}/{len(chartstyle_box_numbers)}] Loading chart for box #{box_number} ({timeframe_name})...")

                    # Navigate the pre-created tab to the chart URL
                    await page.goto(base_chart_url, wait_until='domcontentloaded', timeout=20000)
                    # Optimized: Reduced wait from 3s to 1.5s, using domcontentloaded instead of networkidle
                    await asyncio.sleep(1.5)

                    # Click the numbered ChartStyle box on far left edge
                    logger.info(f"[Tab {i}] Clicking ChartStyle box #{box_number}...")

                    # Based on actual HTML inspection:
                    # Boxes are: <button class="chart-style-button" id="chart-style-button-XXXXX">
                    # Inside: .chart-style-buttons container
                    # Box #1 is first button, Box #7 is 7th button, etc.

                    # Strategy: Select the nth button in the .chart-style-buttons container
                    # Note: First button is the "Manage StyleButtons" gear icon, so we need nth-child(box_number + 1)
                    chartstyle_box_selectors = [
                        f".chart-style-buttons .chart-style-button-container:nth-child({box_number + 1}) button.chart-style-button",
                        f".chart-style-buttons button.chart-style-button:nth-of-type({box_number})",
                        f"button.chart-style-button[id*='chart-style-button']:nth-of-type({box_number})"
                    ]

                    chartstyle_clicked = False
                    for selector in chartstyle_box_selectors:
                        try:
                            count = await page.locator(selector).count()
                            if count > 0:
                                logger.info(f"[Tab {i}] Found ChartStyle box with selector: {selector}")
                                await page.locator(selector).click()
                                logger.info(f"[Tab {i}] Clicked ChartStyle box #{box_number}!")
                                chartstyle_clicked = True
                                break
                        except Exception as e:
                            logger.debug(f"[Tab {i}] Selector {selector} failed: {e}")
                            continue

                    if not chartstyle_clicked:
                        logger.warning(f"[Tab {i}] Could not find/click ChartStyle box #{box_number}, keeping default")
                        await page.screenshot(path=str(self.screenshot_dir / f"debug_box_fail_{box_number}.png"))

                    # Optimized: Reduced wait from 4s to 2.5s after ChartStyle click
                    await asyncio.sleep(2.5)

                    # Apply StockCharts-specific fullscreen maximization to each tab
                    if not self.headless and chartstyle_clicked:
                        await FullscreenManager.maximize_stockcharts_chart(page)
                        logger.info(f"[Tab {i}] Applied StockCharts chart maximization")

                    # Capture screenshot of this tab
                    screenshot_path = self.screenshot_dir / f"{ticker}_tab{i}_box{box_number}_{timeframe_name}.png"
                    await page.screenshot(path=str(screenshot_path))
                    logger.info(f"[Tab {i}] Screenshot saved: {screenshot_path}")

                    # Store page info with screenshot path
                    pages[timeframe_name] = {
                        "page": page,
                        "screenshot_path": str(screenshot_path),
                        "box_number": box_number
                    }

                    logger.info(f"[Tab {i}] Tab created for box #{box_number} ({timeframe_name})")

                except Exception as e:
                    logger.error(f"[Tab {i}] Failed to create tab for box #{box_number}: {e}")

            logger.info(f"Successfully opened {len(pages)}/{len(chartstyle_box_numbers)} tabs")
            return pages

        except Exception as e:
            logger.error(f"Failed to open multi-timeframe tabs: {e}")
            return pages

    async def open_charts_from_excel(self, excel_path: Path) -> Dict[int, Dict]:
        """
        Production Use Case #2: ChartList Batch Viewer
        Opens multiple charts from different ChartLists based on Excel configuration

        Args:
            excel_path: Path to Excel configuration file

        Returns:
            Dict mapping tab_order -> {page, chartlist, ticker, screenshot_path}
        """
        logger.info("=" * 70)
        logger.info("CHARTLIST BATCH VIEWER")
        logger.info("=" * 70)

        opened_tabs = {}

        try:
            # Load Excel configuration
            logger.info(f"Loading configuration from {excel_path}")
            reader = ChartListConfigReader(excel_path)
            chart_configs = reader.load_chart_configs()

            logger.info(f"Loaded {len(chart_configs)} charts to open")

            # Reset ChartList cache at the start of batch operation
            self.current_chartlist = None
            logger.info("ChartList cache reset for new batch operation")

            # Navigate to main charts page after login
            logger.info("Navigating to main charts page with AMZN...")
            await self.enter_ticker_in_search_box("AMZN")

            # OPTIMIZED: Wait for ChartList dropdown to be available instead of fixed sleep
            try:
                await self.page.wait_for_selector('#chart-list-dropdown-menu-toggle-button',
                                                 state='visible', timeout=3000)
                logger.info("ChartList dropdowns available")
            except:
                await asyncio.sleep(1)  # Brief fallback
                logger.warning("ChartList dropdown not found, continuing...")

            logger.info("Main charts page loaded - ChartList dropdowns should be available\n")

            # Track total performance
            import time
            batch_start_time = time.time()
            cache_hits = 0
            cache_misses = 0

            # Process each chart in order
            for idx, config in enumerate(chart_configs, 1):
                chart_start_time = time.time()
                chartlist_name = config['chartlist']
                chart_name = config['chart_name']
                tab_order = config['tab_order']
                timeframe_box = config.get('timeframe_box')
                notes = config.get('notes', '')

                logger.info(f"[Tab {tab_order}/{len(chart_configs)}] Opening '{chart_name}' from '{chartlist_name}'...")
                if notes:
                    logger.info(f"  Notes: {notes}")

                try:
                    # Track cache performance
                    was_cached = (self.current_chartlist == chartlist_name)
                    if was_cached:
                        cache_hits += 1
                    else:
                        cache_misses += 1

                    # Navigate using ChartList dropdown
                    success = await self.navigate_via_chartlist_dropdown(chartlist_name, chart_name)

                    if not success:
                        logger.error(f"[Tab {tab_order}] Failed to navigate to {chart_name}")
                        continue

                    # Create new tab (if not first chart)
                    if idx > 1:
                        page = await self.context.new_page()
                        await page.goto(self.page.url, wait_until='domcontentloaded', timeout=15000)
                        # Smart wait for chart to load
                        try:
                            await page.wait_for_selector('.chart-image', state='visible', timeout=3000)
                        except:
                            await asyncio.sleep(1)
                    else:
                        page = self.page

                    # Apply timeframe box if specified
                    if timeframe_box:
                        logger.info(f"[Tab {tab_order}] Applying ChartStyle box #{timeframe_box}")
                        await self._click_chartstyle_box(page, timeframe_box)

                    # Apply fullscreen maximization
                    if not self.headless:
                        await FullscreenManager.maximize_stockcharts_chart(page)

                    # Capture screenshot
                    screenshot_filename = f"tab{tab_order}_{chartlist_name.replace(' ', '_')}_{chart_name.replace(' ', '_')}"
                    if timeframe_box:
                        screenshot_filename += f"_box{timeframe_box}"
                    screenshot_filename += ".png"

                    screenshot_path = self.screenshot_dir / screenshot_filename
                    await page.screenshot(path=str(screenshot_path))
                    logger.info(f"[Tab {tab_order}] Screenshot saved: {screenshot_path}")

                    # Store tab info
                    opened_tabs[tab_order] = {
                        "page": page,
                        "chartlist": chartlist_name,
                        "chart_name": chart_name,
                        "screenshot_path": str(screenshot_path),
                        "timeframe_box": timeframe_box,
                        "notes": notes
                    }

                    chart_elapsed = time.time() - chart_start_time
                    logger.info(f"[Tab {tab_order}] [SUCCESS] Opened {chart_name} in {chart_elapsed:.2f}s")

                except Exception as e:
                    logger.error(f"[Tab {tab_order}] Error opening {chart_name}: {e}")
                    continue

            # Performance Summary
            total_elapsed = time.time() - batch_start_time
            logger.info("\n" + "=" * 70)
            logger.info(f"ALL TABS OPENED - {len(opened_tabs)}/{len(chart_configs)} successful")
            logger.info("=" * 70)
            logger.info(f"[PERFORMANCE SUMMARY]")
            logger.info(f"  Total time: {total_elapsed:.2f} seconds")
            logger.info(f"  Average per chart: {total_elapsed/len(chart_configs):.2f} seconds")
            logger.info(f"  Cache hits: {cache_hits} ({cache_hits/(cache_hits+cache_misses)*100:.1f}%)")
            logger.info(f"  Cache misses: {cache_misses} ({cache_misses/(cache_hits+cache_misses)*100:.1f}%)")
            logger.info(f"  Time saved from caching: ~{cache_hits * 3:.1f} seconds")
            logger.info("=" * 70)

            if opened_tabs:
                unique_chartlists = set(tab['chartlist'] for tab in opened_tabs.values())
                logger.info(f"ChartLists accessed: {', '.join(unique_chartlists)}")
                logger.info("\nTabs open (in order):")
                for tab_order in sorted(opened_tabs.keys()):
                    tab_info = opened_tabs[tab_order]
                    msg = f"  {tab_order}. {tab_info['chartlist']} > {tab_info['chart_name']}"
                    if tab_info.get('timeframe_box'):
                        msg += f" (Box #{tab_info['timeframe_box']})"
                    logger.info(msg)

            return opened_tabs

        except Exception as e:
            logger.error(f"Failed to open charts from Excel: {e}")
            return opened_tabs

    async def _click_chartstyle_box(self, page: Page, box_number: int) -> bool:
        """
        Helper method to click a ChartStyle box

        Args:
            page: Page to click on
            box_number: ChartStyle box number (1-indexed)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Try multiple selector strategies
            selectors = [
                f".chart-style-buttons .chart-style-button-container:nth-child({box_number + 1}) button.chart-style-button",
                f".chart-style-buttons button.chart-style-button:nth-of-type({box_number})",
                f"button.chart-style-button[id*='chart-style-button']:nth-of-type({box_number})"
            ]

            for selector in selectors:
                try:
                    count = await page.locator(selector).count()
                    if count > 0:
                        await page.locator(selector).click()
                        await asyncio.sleep(2)
                        return True
                except:
                    continue

            logger.warning(f"Could not find/click ChartStyle box #{box_number}")
            return False

        except Exception as e:
            logger.error(f"Error clicking ChartStyle box: {e}")
            return False

    async def open_chartlists_as_tabs(self, excel_path: Path) -> Dict[int, Dict]:
        """
        Production Use Case #3: ChartList Viewer
        Opens first chart from each ChartList in separate tabs

        Args:
            excel_path: Path to Excel file with ChartList names (single column)

        Returns:
            Dict mapping tab_number -> {page, chartlist_name, chart_name, screenshot_path}
        """
        logger.info("=" * 70)
        logger.info("CHARTLIST VIEWER")
        logger.info("=" * 70)

        opened_tabs = {}

        try:
            # Load ChartList names from Excel
            logger.info(f"Loading ChartList names from {excel_path}")
            from src.utils.excel_reader import ChartListConfigReader
            reader = ChartListConfigReader(excel_path)
            chartlist_names = reader.load_chartlist_names_only()

            logger.info(f"Loaded {len(chartlist_names)} ChartLists to open")
            logger.info(f"ChartLists: {', '.join(chartlist_names)}")

            # Reset ChartList cache
            self.current_chartlist = None

            # Navigate to AMZN to get to a chart page (so dropdowns are available)
            logger.info("\nNavigating to AMZN to access ChartList dropdowns...")
            await self.enter_ticker_in_search_box("AMZN")

            # Wait for ChartList dropdown to be available
            try:
                await self.page.wait_for_selector('#chart-list-dropdown-menu-toggle-button',
                                                 state='visible', timeout=3000)
                logger.info("ChartList dropdowns available\n")
            except:
                await asyncio.sleep(1)
                logger.warning("ChartList dropdown not found, continuing...")

            # Keep the initial AMZN page as is - this becomes Tab 1
            base_url = self.page.url

            # Process each ChartList
            for idx, chartlist_name in enumerate(chartlist_names, 1):
                logger.info(f"[Tab {idx+1}/{len(chartlist_names)+1}] Opening ChartList: {chartlist_name}")

                try:
                    # ALWAYS create a new tab for EVERY ChartList
                    page = await self.context.new_page()
                    await page.goto(base_url, wait_until='domcontentloaded', timeout=15000)

                    # Wait for page to be ready
                    try:
                        await page.wait_for_selector('#chart-list-dropdown-menu-toggle-button', state='visible', timeout=3000)
                    except:
                        await asyncio.sleep(1)

                    # Click ChartList dropdown
                    chartlist_button_selector = "#chart-list-dropdown-menu-toggle-button"
                    chartlist_button = await page.query_selector(chartlist_button_selector)

                    if not chartlist_button:
                        logger.error(f"[Tab {idx+1}] ChartList dropdown not found")
                        continue

                    # Open ChartList dropdown
                    await chartlist_button.click()

                    # Smart wait for dropdown to appear
                    try:
                        await page.wait_for_selector('.chartlist-dropdown-menu', state='visible', timeout=3000)
                    except:
                        await asyncio.sleep(1)  # Fallback to fixed wait

                    # Select the ChartList
                    chartlist_item = await page.query_selector(f"text={chartlist_name}")
                    if not chartlist_item:
                        # Try partial match
                        chartlist_item = await page.query_selector(f"*:has-text('{chartlist_name}')")

                    if not chartlist_item:
                        logger.error(f"[Tab {idx+1}] ChartList '{chartlist_name}' not found in dropdown")
                        await page.keyboard.press("Escape")  # Close dropdown
                        continue

                    logger.info(f"[Tab {idx+1}] Selecting ChartList: {chartlist_name}")
                    await chartlist_item.click()

                    # Wait for ChartList to load (it will automatically load its first chart)
                    logger.info(f"[Tab {idx+1}] Waiting for ChartList '{chartlist_name}' to load...")
                    await asyncio.sleep(3)

                    # Extract the chart that was loaded
                    current_url = page.url
                    first_chart_name = "Unknown"

                    if '?s=' in current_url:
                        ticker = current_url.split('?s=')[1].split('&')[0]
                        if ticker and ticker != 'AMZN':
                            first_chart_name = ticker
                            logger.info(f"[Tab {idx+1}] ChartList '{chartlist_name}' loaded chart: {first_chart_name}")
                        else:
                            first_chart_name = "Default Chart"

                    # Check if we have a chart image
                    try:
                        chart_image = await page.query_selector('.chart-image')
                        if not chart_image:
                            logger.warning(f"[Tab {idx+1}] No chart image found for '{chartlist_name}'")
                    except:
                        pass

                    # Apply fullscreen maximization
                    if not self.headless:
                        await FullscreenManager.maximize_stockcharts_chart(page)

                    # Capture screenshot
                    screenshot_filename = f"tab{idx+1}_{chartlist_name.replace(' ', '_')}_{first_chart_name.replace(' ', '_')}.png"
                    screenshot_path = self.screenshot_dir / screenshot_filename
                    await page.screenshot(path=str(screenshot_path))
                    logger.info(f"[Tab {idx+1}] Screenshot saved: {screenshot_path}")

                    # Store tab info (using idx+1 since tab 1 is the initial AMZN page)
                    opened_tabs[idx+1] = {
                        "page": page,
                        "chartlist_name": chartlist_name,
                        "chart_name": first_chart_name,
                        "screenshot_path": str(screenshot_path)
                    }

                    logger.info(f"[Tab {idx+1}] [SUCCESS] Opened {chartlist_name} > {first_chart_name}")

                except Exception as e:
                    logger.error(f"[Tab {idx+1}] Error opening ChartList '{chartlist_name}': {e}")
                    continue

            # Summary (remember tab 1 is the initial AMZN page)
            logger.info("\n" + "=" * 70)
            logger.info(f"ALL TABS OPENED - {len(opened_tabs)}/{len(chartlist_names)} successful")
            logger.info("=" * 70)
            logger.info("Tab 1: AMZN (initial navigation page)")

            if opened_tabs:
                logger.info("Tabs open (in order):")
                for tab_num in sorted(opened_tabs.keys()):
                    tab_info = opened_tabs[tab_num]
                    logger.info(f"  Tab {tab_num}: {tab_info['chartlist_name']} > {tab_info['chart_name']}")

            return opened_tabs

        except Exception as e:
            logger.error(f"Failed to open ChartLists from Excel: {e}")
            return opened_tabs

    async def close(self):
        """Cleanup resources"""
        logger.info("Closing browser...")
        
        if self.context:
            await self.context.close()
        
        if self.browser:
            await self.browser.close()
        
        if self.playwright:
            await self.playwright.stop()
        
        logger.info("Browser closed")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
