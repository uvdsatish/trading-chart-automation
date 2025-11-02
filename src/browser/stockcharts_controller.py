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

logger = logging.getLogger(__name__)


class StockChartsController:
    """Manages browser automation for StockCharts.com"""
    
    def __init__(
        self,
        username: str,
        password: str,
        headless: bool = False,
        screenshot_dir: str = "screenshots",
        config: Optional[Dict] = None
    ):
        self.username = username
        self.password = password
        self.headless = headless
        self.screenshot_dir = Path(screenshot_dir)
        self.config = config or {}
        
        # Browser instances
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # State tracking
        self.is_logged_in = False
        self.current_ticker: Optional[str] = None
        
        # Ensure screenshot directory exists
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Start browser and create context"""
        logger.info("Initializing browser...")
        
        self.playwright = await async_playwright().start()
        
        # Launch browser with options
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        # Create context with viewport and user agent
        viewport = self.config.get('browser', {}).get('viewport', {})
        user_agent = self.config.get('browser', {}).get('user_agent')
        
        self.context = await self.browser.new_context(
            viewport=viewport or {'width': 1920, 'height': 1080},
            user_agent=user_agent
        )
        
        # Create page
        self.page = await self.context.new_page()
        
        # Set default timeout
        timeout = self.config.get('stockcharts', {}).get('timeouts', {}).get('navigation', 30000)
        self.page.set_default_timeout(timeout)
        
        logger.info("Browser initialized successfully")
    
    async def login(self) -> bool:
        """
        Authenticate with StockCharts.com
        
        Returns:
            bool: True if login successful, False otherwise
        """
        if self.is_logged_in:
            logger.info("Already logged in")
            return True
        
        try:
            logger.info("Attempting login to StockCharts.com...")
            
            # Navigate to login page
            login_url = self.config.get('stockcharts', {}).get('login_url', 
                                                               'https://stockcharts.com/h-sc/ui')
            await self.page.goto(login_url, wait_until='networkidle')
            
            # Wait a moment for page to stabilize
            await asyncio.sleep(2)
            
            # Take screenshot of login page for debugging
            await self._save_screenshot("01_login_page")
            
            # Find and fill username field (try multiple selectors)
            username_selectors = [
                "input[name='username']",
                "input[type='email']",
                "#username",
                "input[placeholder*='email' i]",
                "input[placeholder*='username' i]"
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
            
            # Find and click login button
            login_button_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:has-text('Log in')",
                "button:has-text('Sign in')",
                "a:has-text('Log in')"
            ]
            
            login_clicked = False
            for selector in login_button_selectors:
                try:
                    if await self.page.locator(selector).count() > 0:
                        await self.page.click(selector)
                        login_clicked = True
                        logger.info(f"Clicked login button using selector: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            if not login_clicked:
                # Try pressing Enter as fallback
                logger.info("Trying Enter key as fallback")
                await self.page.keyboard.press('Enter')
            
            # Wait for navigation or error message
            await asyncio.sleep(3)
            await self.page.wait_for_load_state('networkidle', timeout=10000)
            
            await self._save_screenshot("03_after_login_attempt")
            
            # Check if login was successful
            # Look for common indicators of successful login
            success_indicators = [
                "text=My Account",
                "text=Logout",
                "text=Sign Out",
                "text=Gallery",
                "[href*='logout']",
                "[href*='signout']"
            ]
            
            for indicator in success_indicators:
                try:
                    if await self.page.locator(indicator).count() > 0:
                        self.is_logged_in = True
                        logger.info("✓ Login successful!")
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
            
            await self.page.goto(chart_url, wait_until='networkidle')
            await asyncio.sleep(2)  # Give chart time to render
            
            self.current_ticker = ticker
            
            if save_screenshot:
                await self._save_screenshot(f"chart_{ticker}")
            
            logger.info(f"Successfully loaded {ticker} chart")
            return True
            
        except Exception as e:
            logger.error(f"Failed to navigate to chart: {e}")
            await self._save_screenshot(f"error_navigate_{ticker}")
            return False
    
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
