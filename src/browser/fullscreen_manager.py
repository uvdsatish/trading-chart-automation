"""
Fullscreen Manager for Browser Automation
Implements multiple aggressive fullscreen strategies to ensure browser takes entire monitor
"""

import asyncio
import logging
from typing import Optional, Tuple
import platform

logger = logging.getLogger(__name__)


class FullscreenManager:
    """Manages fullscreen strategies across different platforms and scenarios"""

    @staticmethod
    def get_monitor_dimensions() -> Tuple[int, int]:
        """
        Get the primary monitor dimensions using platform-specific methods

        Returns:
            Tuple of (width, height) in pixels
        """
        try:
            if platform.system() == "Windows":
                # Windows-specific approach
                import ctypes
                user32 = ctypes.windll.user32
                screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
                logger.info(f"[MONITOR] Detected Windows screen size: {screensize[0]}x{screensize[1]}")
                return screensize
            else:
                # Fallback for other platforms
                try:
                    from screeninfo import get_monitors
                    monitor = get_monitors()[0]
                    logger.info(f"[MONITOR] Detected screen size: {monitor.width}x{monitor.height}")
                    return monitor.width, monitor.height
                except:
                    # Ultimate fallback
                    logger.warning("[MONITOR] Could not detect screen size, using default 1920x1080")
                    return 1920, 1080
        except Exception as e:
            logger.error(f"[MONITOR] Error detecting screen size: {e}")
            return 1920, 1080

    @staticmethod
    def get_browser_args() -> list:
        """
        Get aggressive browser launch arguments for true fullscreen

        Returns:
            List of Chrome/Chromium launch arguments
        """
        width, height = FullscreenManager.get_monitor_dimensions()

        args = [
            # Primary fullscreen methods
            '--kiosk',  # Most aggressive - true fullscreen without any UI
            '--start-fullscreen',  # Backup fullscreen flag

            # Window positioning and sizing
            f'--window-size={width},{height}',
            '--window-position=0,0',

            # Disable all UI elements
            '--disable-infobars',
            '--disable-session-crashed-bubble',
            '--disable-translate',
            '--no-first-run',
            '--no-default-browser-check',

            # Hide scrollbars and maximize content area
            '--hide-scrollbars',

            # Automation flags
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',

            # Performance
            '--disable-gpu-sandbox',
            '--no-sandbox'
        ]

        logger.info(f"[FULLSCREEN] Browser args configured for {width}x{height} screen")
        return args

    @staticmethod
    async def apply_page_fullscreen(page) -> None:
        """
        Apply multiple JavaScript-based fullscreen methods to ensure full coverage

        Args:
            page: Playwright page object
        """
        try:
            width, height = FullscreenManager.get_monitor_dimensions()

            # Method 1: Standard Fullscreen API
            await page.evaluate("""
                () => {
                    // Try multiple elements for fullscreen
                    const elements = [
                        document.documentElement,
                        document.body,
                        document.querySelector('#app'),
                        document.querySelector('.main-container')
                    ];

                    for (const el of elements) {
                        if (el && el.requestFullscreen) {
                            el.requestFullscreen().catch(() => {});
                        }
                    }
                }
            """)
            logger.info("[FULLSCREEN] JavaScript Fullscreen API applied")

            # Method 2: Force window dimensions via JavaScript
            await page.evaluate(f"""
                () => {{
                    // Force window to specific size
                    window.moveTo(0, 0);
                    window.resizeTo({width}, {height});

                    // Remove any margins/padding
                    document.body.style.margin = '0';
                    document.body.style.padding = '0';
                    document.body.style.overflow = 'hidden';

                    // Maximize HTML element
                    document.documentElement.style.width = '100vw';
                    document.documentElement.style.height = '100vh';
                    document.documentElement.style.margin = '0';
                    document.documentElement.style.padding = '0';
                }}
            """)
            logger.info(f"[FULLSCREEN] Window forced to {width}x{height} via JavaScript")

            # Method 3: Hide all browser chrome via CSS
            await page.add_style_tag(content="""
                /* Hide all scrollbars */
                ::-webkit-scrollbar { display: none !important; }
                * { scrollbar-width: none !important; }

                /* Maximize body and html */
                html, body {
                    width: 100vw !important;
                    height: 100vh !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    overflow: hidden !important;
                    position: fixed !important;
                    top: 0 !important;
                    left: 0 !important;
                }

                /* Hide any overlays or modals that might appear */
                .modal, .popup, .overlay, .banner {
                    display: none !important;
                }
            """)
            logger.info("[FULLSCREEN] CSS maximization applied")

        except Exception as e:
            logger.error(f"[FULLSCREEN] Error applying page fullscreen: {e}")

    @staticmethod
    async def maximize_stockcharts_chart(page) -> None:
        """
        Specific optimizations for StockCharts.com to maximize chart area

        Args:
            page: Playwright page object
        """
        try:
            # Wait for chart to be present
            await page.wait_for_selector('.chart-container, #chartImg, canvas', timeout=5000)

            # Aggressive CSS to maximize StockCharts chart area
            await page.add_style_tag(content="""
                /* Hide all unnecessary StockCharts UI elements */
                .header, .navbar, .top-bar, .toolbar, .menu-bar {
                    display: none !important;
                }

                /* Hide ads and promotional content */
                .ad, .advertisement, .promo, iframe[src*="doubleclick"] {
                    display: none !important;
                }

                /* Maximize chart container */
                .chart-container, .chart-wrapper, #chartImg {
                    position: fixed !important;
                    top: 0 !important;
                    left: 0 !important;
                    width: 100vw !important;
                    height: 100vh !important;
                    max-width: 100vw !important;
                    max-height: 100vh !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    z-index: 9999 !important;
                }

                /* Handle canvas charts */
                canvas {
                    width: 100% !important;
                    height: 100% !important;
                    display: block !important;
                }

                /* Remove any padding from parent containers */
                .content, .main, .container {
                    padding: 0 !important;
                    margin: 0 !important;
                    max-width: 100% !important;
                }

                /* Force background to black for better contrast */
                body {
                    background: black !important;
                }
            """)
            logger.info("[STOCKCHARTS] Chart maximization CSS applied")

            # Try to click any "expand" or "fullscreen" buttons if they exist
            expand_selectors = [
                'button[title*="fullscreen" i]',
                'button[title*="expand" i]',
                'button[title*="maximize" i]',
                '.fullscreen-button',
                '.expand-button',
                '[class*="fullscreen"]',
                '[class*="expand"]'
            ]

            for selector in expand_selectors:
                try:
                    if await page.locator(selector).count() > 0:
                        await page.locator(selector).first.click()
                        logger.info(f"[STOCKCHARTS] Clicked expand button: {selector}")
                        break
                except:
                    continue

        except Exception as e:
            logger.error(f"[STOCKCHARTS] Error maximizing chart: {e}")

    @staticmethod
    async def verify_fullscreen(page) -> bool:
        """
        Verify that fullscreen was achieved

        Args:
            page: Playwright page object

        Returns:
            True if fullscreen appears successful
        """
        try:
            result = await page.evaluate("""
                () => {
                    return {
                        innerWidth: window.innerWidth,
                        innerHeight: window.innerHeight,
                        outerWidth: window.outerWidth,
                        outerHeight: window.outerHeight,
                        screenWidth: window.screen.width,
                        screenHeight: window.screen.height,
                        availWidth: window.screen.availWidth,
                        availHeight: window.screen.availHeight,
                        isFullscreen: document.fullscreenElement !== null
                    };
                }
            """)

            logger.info(f"[VERIFY] Window dimensions: {result}")

            # Check if window dimensions match screen dimensions
            width_match = abs(result['innerWidth'] - result['screenWidth']) < 50
            height_match = abs(result['innerHeight'] - result['screenHeight']) < 100

            if width_match and height_match:
                logger.info("[VERIFY] [SUCCESS] Fullscreen achieved!")
                return True
            else:
                logger.warning(f"[VERIFY] [WARNING] Not fully fullscreen - inner: {result['innerWidth']}x{result['innerHeight']}, screen: {result['screenWidth']}x{result['screenHeight']}")
                return False

        except Exception as e:
            logger.error(f"[VERIFY] Error verifying fullscreen: {e}")
            return False