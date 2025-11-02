"""
Basic tests for POC components
Run with: pytest tests/test_poc.py -v
"""
import pytest
import asyncio
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.browser.stockcharts_controller import StockChartsController
from src.ai.chart_analyzer import ChartAnalyzer


class TestConfiguration:
    """Test configuration and setup"""
    
    def test_config_files_exist(self):
        """Verify required config files exist"""
        base_path = Path(__file__).parent.parent
        
        assert (base_path / "config" / "settings.yaml").exists()
        assert (base_path / "config" / ".env.example").exists()
        assert (base_path / "requirements.txt").exists()
    
    def test_screenshot_directory(self):
        """Verify screenshot directory can be created"""
        screenshots_dir = Path(__file__).parent.parent / "screenshots"
        screenshots_dir.mkdir(exist_ok=True)
        assert screenshots_dir.exists()


class TestBrowserController:
    """Test browser automation components"""
    
    @pytest.mark.asyncio
    async def test_controller_initialization(self):
        """Test that browser controller can be initialized"""
        controller = StockChartsController(
            username="test_user",
            password="test_pass",
            headless=True,
            screenshot_dir="screenshots"
        )
        
        # Should not raise an exception
        assert controller.username == "test_user"
        assert controller.headless == True
        assert controller.is_logged_in == False
    
    @pytest.mark.asyncio
    async def test_browser_lifecycle(self):
        """Test browser can be started and stopped"""
        controller = StockChartsController(
            username="test_user",
            password="test_pass",
            headless=True
        )
        
        # Initialize
        await controller.initialize()
        assert controller.browser is not None
        assert controller.page is not None
        
        # Close
        await controller.close()


class TestAIAnalyzer:
    """Test AI components (without making actual API calls)"""
    
    def test_analyzer_initialization(self):
        """Test that AI analyzer can be initialized"""
        analyzer = ChartAnalyzer(
            api_key="test_key_1234567890",
            model="claude-sonnet-4-5-20250929"
        )
        
        assert analyzer.model == "claude-sonnet-4-5-20250929"
        assert analyzer.max_tokens == 4096
    
    def test_image_encoding(self, tmp_path):
        """Test image encoding functionality"""
        # Create a dummy image file
        dummy_image = tmp_path / "test_chart.png"
        dummy_image.write_bytes(b"fake image data")
        
        analyzer = ChartAnalyzer(api_key="test_key")
        
        # Should not raise an exception
        encoded = analyzer._encode_image(dummy_image)
        assert isinstance(encoded, str)
        assert len(encoded) > 0
    
    def test_media_type_detection(self):
        """Test media type detection from file extension"""
        analyzer = ChartAnalyzer(api_key="test_key")
        
        assert analyzer._get_media_type(Path("test.png")) == "image/png"
        assert analyzer._get_media_type(Path("test.jpg")) == "image/jpeg"
        assert analyzer._get_media_type(Path("test.jpeg")) == "image/jpeg"
    
    def test_pattern_extraction(self):
        """Test pattern extraction from text"""
        analyzer = ChartAnalyzer(api_key="test_key")
        
        text = "I see an ascending triangle pattern and a possible head and shoulders formation"
        patterns = analyzer._extract_patterns(text)
        
        assert "triangle" in patterns
        assert "head and shoulders" in patterns
    
    def test_trend_extraction(self):
        """Test trend extraction from text"""
        analyzer = ChartAnalyzer(api_key="test_key")
        
        text = "The chart shows a strong uptrend with bullish momentum"
        trend = analyzer._extract_trend(text)
        
        assert trend["direction"] == "uptrend"
        assert trend["strength"] > 5
    
    def test_risk_level_extraction(self):
        """Test risk level extraction"""
        analyzer = ChartAnalyzer(api_key="test_key")
        
        text1 = "This is a high risk setup"
        assert analyzer._extract_risk_level(text1) == "high"
        
        text2 = "Low risk entry point"
        assert analyzer._extract_risk_level(text2) == "low"
        
        text3 = "Moderate conditions"
        assert analyzer._extract_risk_level(text3) == "medium"


class TestIntegration:
    """Integration tests (require actual credentials)"""
    
    @pytest.mark.skip(reason="Requires valid credentials")
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test complete workflow end-to-end"""
        # This would test the full workflow but requires:
        # - Valid StockCharts credentials
        # - Valid Anthropic API key
        # - Network access
        pass


def test_imports():
    """Test that all required packages can be imported"""
    try:
        from playwright.async_api import async_playwright
        import anthropic
        import yaml
        from dotenv import load_dotenv
        import logging
        
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import required package: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
