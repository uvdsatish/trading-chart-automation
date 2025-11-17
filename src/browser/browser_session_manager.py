"""
Browser Session Manager for Multiple Instance Support
Manages multiple independent browser instances for parallel execution
"""
import asyncio
import logging
from typing import Dict, Optional, List
from pathlib import Path
import json

from .stockcharts_controller import StockChartsController

logger = logging.getLogger(__name__)


class BrowserSessionManager:
    """Manages multiple browser instances for parallel execution"""

    def __init__(self):
        """Initialize the session manager"""
        self.sessions: Dict[str, StockChartsController] = {}
        self.session_data_dir = Path("browser_sessions")
        self.session_data_dir.mkdir(parents=True, exist_ok=True)

    async def create_session(
        self,
        session_id: str,
        username: str,
        password: str,
        headless: bool = False,
        screenshot_dir: Optional[str] = None,
        config: Optional[Dict] = None,
        window_position: Optional[Dict] = None
    ) -> StockChartsController:
        """
        Create a new browser session with unique ID

        Args:
            session_id: Unique identifier for this session
            username: StockCharts username
            password: StockCharts password
            headless: Whether to run in headless mode
            screenshot_dir: Directory for screenshots (defaults to screenshots/session_id)
            config: Configuration dictionary
            window_position: Optional window positioning for headed mode
                           Example: {"x": 0, "y": 0, "width": 960, "height": 1080}

        Returns:
            StockChartsController instance
        """
        if session_id in self.sessions:
            logger.warning(f"Session {session_id} already exists, returning existing session")
            return self.sessions[session_id]

        # Create unique screenshot directory for this session
        if screenshot_dir is None:
            screenshot_dir = f"screenshots/{session_id}"

        # Create controller with session-specific settings
        controller = StockChartsController(
            username=username,
            password=password,
            headless=headless,
            screenshot_dir=screenshot_dir,
            config=config
        )

        # Store the window position if provided
        if window_position and not headless:
            controller.window_position = window_position

        # Store session
        self.sessions[session_id] = controller

        logger.info(f"[SESSION] Created new session: {session_id}")
        return controller

    async def initialize_session(
        self,
        session_id: str,
        auto_login: bool = True
    ) -> bool:
        """
        Initialize a browser session

        Args:
            session_id: Session identifier
            auto_login: Whether to automatically log in after initialization

        Returns:
            True if successful, False otherwise
        """
        if session_id not in self.sessions:
            logger.error(f"Session {session_id} not found")
            return False

        controller = self.sessions[session_id]

        try:
            # Initialize browser
            await controller.initialize()

            # Apply window positioning if specified
            if hasattr(controller, 'window_position') and controller.page:
                pos = controller.window_position
                # Use CDP to position window (Chrome DevTools Protocol)
                try:
                    client = await controller.page.context.new_cdp_session(controller.page)
                    bounds = {
                        "left": pos.get("x", 0),
                        "top": pos.get("y", 0),
                        "width": pos.get("width", 960),
                        "height": pos.get("height", 1080),
                        "windowState": "normal"
                    }
                    await client.send("Browser.setWindowBounds", {
                        "windowId": 1,
                        "bounds": bounds
                    })
                    logger.info(f"[SESSION {session_id}] Positioned window at {bounds}")
                except Exception as e:
                    logger.warning(f"[SESSION {session_id}] Could not position window: {e}")

            # Auto login if requested
            if auto_login:
                login_success = await controller.login()
                if not login_success:
                    logger.error(f"[SESSION {session_id}] Login failed")
                    return False

            logger.info(f"[SESSION {session_id}] Initialized successfully")
            return True

        except Exception as e:
            logger.error(f"[SESSION {session_id}] Initialization failed: {e}")
            return False

    async def close_session(self, session_id: str):
        """Close a specific browser session"""
        if session_id in self.sessions:
            controller = self.sessions[session_id]
            await controller.close()
            del self.sessions[session_id]
            logger.info(f"[SESSION] Closed session: {session_id}")

    async def close_all_sessions(self):
        """Close all browser sessions"""
        logger.info(f"Closing {len(self.sessions)} browser sessions...")

        close_tasks = []
        for session_id, controller in self.sessions.items():
            close_tasks.append(controller.close())

        if close_tasks:
            await asyncio.gather(*close_tasks, return_exceptions=True)

        self.sessions.clear()
        logger.info("All browser sessions closed")

    def get_session(self, session_id: str) -> Optional[StockChartsController]:
        """Get a specific session by ID"""
        return self.sessions.get(session_id)

    def list_sessions(self) -> List[str]:
        """List all active session IDs"""
        return list(self.sessions.keys())

    async def run_parallel_tasks(
        self,
        tasks: List[Dict]
    ) -> Dict[str, any]:
        """
        Run tasks in parallel across different sessions

        Args:
            tasks: List of task dictionaries, each containing:
                   - session_id: Which session to use
                   - task_type: Type of task (e.g., "chartlist-batch", "chartlist-viewer")
                   - params: Task-specific parameters

        Returns:
            Dictionary of results keyed by session_id
        """
        results = {}

        async def run_task(task):
            session_id = task["session_id"]
            task_type = task["task_type"]
            params = task.get("params", {})

            controller = self.get_session(session_id)
            if not controller:
                logger.error(f"Session {session_id} not found for task")
                return session_id, {"error": "Session not found"}

            try:
                if task_type == "chartlist-batch":
                    # Run chartlist batch viewer
                    excel_path = params.get("excel_path")
                    result = await controller.open_charts_from_excel(excel_path)
                    return session_id, {"success": True, "charts_opened": result}

                elif task_type == "chartlist-viewer":
                    # Run chartlist viewer
                    excel_path = params.get("excel_path")
                    result = await controller.open_chartlists_as_tabs(excel_path)
                    return session_id, {"success": True, "chartlists_opened": result}

                elif task_type == "multi-timeframe":
                    # Run multi-timeframe viewer
                    ticker = params.get("ticker")
                    box_numbers = params.get("box_numbers", [1, 7, 10])
                    result = await controller.open_multi_timeframe_tabs(ticker, box_numbers)
                    return session_id, {"success": True, "tabs_opened": len(result)}

                else:
                    return session_id, {"error": f"Unknown task type: {task_type}"}

            except Exception as e:
                logger.error(f"[SESSION {session_id}] Task failed: {e}")
                return session_id, {"error": str(e)}

        # Run all tasks in parallel
        task_results = await asyncio.gather(
            *[run_task(task) for task in tasks],
            return_exceptions=True
        )

        # Process results
        for result in task_results:
            if isinstance(result, Exception):
                logger.error(f"Task exception: {result}")
            else:
                session_id, task_result = result
                results[session_id] = task_result

        return results


class WindowPositioner:
    """Helper class to calculate window positions for multiple browser instances"""

    @staticmethod
    def get_split_screen_positions(
        num_windows: int,
        monitor_width: int = 1920,
        monitor_height: int = 1080,
        monitor_x: int = 0,
        monitor_y: int = 0
    ) -> List[Dict]:
        """
        Calculate window positions for split-screen layout

        Args:
            num_windows: Number of windows to position
            monitor_width: Width of the monitor
            monitor_height: Height of the monitor
            monitor_x: X offset of the monitor (for multi-monitor setups)
            monitor_y: Y offset of the monitor

        Returns:
            List of position dictionaries
        """
        positions = []

        if num_windows == 1:
            # Full screen
            positions.append({
                "x": monitor_x,
                "y": monitor_y,
                "width": monitor_width,
                "height": monitor_height
            })
        elif num_windows == 2:
            # Side by side
            half_width = monitor_width // 2
            positions.append({
                "x": monitor_x,
                "y": monitor_y,
                "width": half_width,
                "height": monitor_height
            })
            positions.append({
                "x": monitor_x + half_width,
                "y": monitor_y,
                "width": half_width,
                "height": monitor_height
            })
        elif num_windows <= 4:
            # 2x2 grid
            half_width = monitor_width // 2
            half_height = monitor_height // 2

            positions = [
                {"x": monitor_x, "y": monitor_y, "width": half_width, "height": half_height},
                {"x": monitor_x + half_width, "y": monitor_y, "width": half_width, "height": half_height},
                {"x": monitor_x, "y": monitor_y + half_height, "width": half_width, "height": half_height},
                {"x": monitor_x + half_width, "y": monitor_y + half_height, "width": half_width, "height": half_height}
            ][:num_windows]
        else:
            # Default positioning (overlapping windows with offset)
            offset = 50
            for i in range(num_windows):
                positions.append({
                    "x": monitor_x + (i * offset),
                    "y": monitor_y + (i * offset),
                    "width": min(monitor_width - (i * offset), 1200),
                    "height": min(monitor_height - (i * offset), 800)
                })

        return positions

    @staticmethod
    def get_multi_monitor_positions(
        sessions: List[str],
        primary_monitor: Dict = None,
        secondary_monitor: Dict = None
    ) -> Dict[str, Dict]:
        """
        Calculate positions for multiple monitors

        Args:
            sessions: List of session IDs
            primary_monitor: Primary monitor specs {"x": 0, "y": 0, "width": 1920, "height": 1080}
            secondary_monitor: Secondary monitor specs

        Returns:
            Dictionary mapping session_id to position
        """
        if primary_monitor is None:
            primary_monitor = {"x": 0, "y": 0, "width": 1920, "height": 1080}

        if secondary_monitor is None:
            secondary_monitor = {"x": 1920, "y": 0, "width": 1920, "height": 1080}

        positions = {}

        if len(sessions) <= 2:
            # One window per monitor
            if len(sessions) >= 1:
                positions[sessions[0]] = {
                    "x": primary_monitor["x"],
                    "y": primary_monitor["y"],
                    "width": primary_monitor["width"],
                    "height": primary_monitor["height"]
                }
            if len(sessions) >= 2:
                positions[sessions[1]] = {
                    "x": secondary_monitor["x"],
                    "y": secondary_monitor["y"],
                    "width": secondary_monitor["width"],
                    "height": secondary_monitor["height"]
                }
        else:
            # Split windows across monitors
            half = len(sessions) // 2

            # First half on primary monitor
            primary_positions = WindowPositioner.get_split_screen_positions(
                half,
                primary_monitor["width"],
                primary_monitor["height"],
                primary_monitor["x"],
                primary_monitor["y"]
            )

            # Second half on secondary monitor
            secondary_positions = WindowPositioner.get_split_screen_positions(
                len(sessions) - half,
                secondary_monitor["width"],
                secondary_monitor["height"],
                secondary_monitor["x"],
                secondary_monitor["y"]
            )

            for i, session_id in enumerate(sessions):
                if i < half:
                    positions[session_id] = primary_positions[i]
                else:
                    positions[session_id] = secondary_positions[i - half]

        return positions