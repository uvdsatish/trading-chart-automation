"""
Excel configuration file reader for ChartList batch operations
Handles reading and validating Excel files for Production Use Case #2
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ChartListConfigReader:
    """
    Reads and validates Excel configuration for ChartList batch viewer

    Expected Excel columns:
    - ChartList: Name of the ChartList (required)
    - Ticker: Stock symbol (required)
    - TabOrder: Order to open tabs, 1-indexed (required)
    - TimeframeBox: Optional ChartStyle box number
    - Notes: Optional user notes
    """

    def __init__(self, excel_path: Path):
        """
        Initialize the Excel reader

        Args:
            excel_path: Path to Excel configuration file
        """
        self.excel_path = Path(excel_path)
        if not self.excel_path.exists():
            raise FileNotFoundError(f"Excel file not found: {self.excel_path}")

    def load_chart_configs(self) -> List[Dict]:
        """
        Load chart configurations from Excel file

        Returns:
            List of dicts with keys: chartlist, ticker, tab_order, timeframe_box, notes
            Sorted by tab_order

        Raises:
            ValueError: If required columns are missing or validation fails
        """
        logger.info(f"Loading configuration from {self.excel_path}")

        try:
            # Read Excel file
            df = pd.read_excel(self.excel_path)
            logger.info(f"Loaded {len(df)} rows from Excel")

            # Normalize column names (case-insensitive)
            df.columns = df.columns.str.strip()
            column_mapping = {}

            for col in df.columns:
                col_lower = col.lower()
                if 'chartlist' in col_lower or 'chart list' in col_lower:
                    column_mapping[col] = 'ChartList'
                elif 'chartname' in col_lower or 'chart name' in col_lower:
                    column_mapping[col] = 'ChartName'
                elif 'ticker' in col_lower or 'symbol' in col_lower:
                    # Backward compatibility - map Ticker to ChartName
                    column_mapping[col] = 'ChartName'
                elif 'tab' in col_lower and 'order' in col_lower:
                    column_mapping[col] = 'TabOrder'
                elif 'timeframe' in col_lower or 'box' in col_lower:
                    column_mapping[col] = 'TimeframeBox'
                elif 'note' in col_lower or 'comment' in col_lower:
                    column_mapping[col] = 'Notes'

            df = df.rename(columns=column_mapping)

            # Validate required columns
            required_cols = ['ChartList', 'ChartName', 'TabOrder']
            missing = set(required_cols) - set(df.columns)
            if missing:
                raise ValueError(f"Missing required columns: {missing}")

            # Remove empty rows
            df = df.dropna(subset=['ChartList', 'ChartName'])

            if df.empty:
                raise ValueError("No valid chart configurations found in Excel file")

            # Convert to list of dicts with normalized keys
            configs = []
            for _, row in df.iterrows():
                config = {
                    'chartlist': str(row['ChartList']).strip(),
                    'chart_name': str(row['ChartName']).strip(),  # Don't uppercase - could be descriptive name
                    'tab_order': int(row['TabOrder']) if pd.notna(row['TabOrder']) else 999,
                    'timeframe_box': int(row['TimeframeBox']) if 'TimeframeBox' in row and pd.notna(row.get('TimeframeBox')) else None,
                    'notes': str(row['Notes']) if 'Notes' in row and pd.notna(row.get('Notes')) else ''
                }
                configs.append(config)

            # Sort by TabOrder
            configs.sort(key=lambda x: x['tab_order'])

            # Validate no duplicate tab orders
            tab_orders = [c['tab_order'] for c in configs]
            if len(tab_orders) != len(set(tab_orders)):
                # Find duplicates
                duplicates = [x for x in tab_orders if tab_orders.count(x) > 1]
                logger.warning(f"Duplicate TabOrder values found: {set(duplicates)}")

            logger.info(f"Successfully loaded {len(configs)} chart configurations")
            return configs

        except Exception as e:
            logger.error(f"Error loading Excel file: {e}")
            raise

    def validate_config(self) -> Dict:
        """
        Validate configuration file and return detailed results

        Returns:
            Dict with validation results including:
            - is_valid: Boolean indicating if config is valid
            - errors: List of error messages
            - warnings: List of warning messages
            - summary: Summary statistics
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'summary': {}
        }

        try:
            configs = self.load_chart_configs()

            # Summary statistics
            result['summary']['total_charts'] = len(configs)
            result['summary']['unique_chartlists'] = len(set(c['chartlist'] for c in configs))
            result['summary']['unique_chart_names'] = len(set(c['chart_name'] for c in configs))

            # Check for reasonable number of tabs
            if len(configs) > 20:
                result['warnings'].append(f"Large number of tabs ({len(configs)}) may impact performance")

            # Check tab order sequence
            expected_order = list(range(1, len(configs) + 1))
            actual_order = [c['tab_order'] for c in configs]
            if actual_order != expected_order:
                result['warnings'].append(f"Tab orders are not sequential: {actual_order}")

            # Check for valid timeframe boxes
            valid_boxes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
            for config in configs:
                if config['timeframe_box'] and config['timeframe_box'] not in valid_boxes:
                    result['warnings'].append(
                        f"Invalid TimeframeBox {config['timeframe_box']} for {config['chart_name']}"
                    )

            logger.info(f"Validation complete: {result['summary']}")

        except Exception as e:
            result['is_valid'] = False
            result['errors'].append(str(e))
            logger.error(f"Validation failed: {e}")

        return result

    @staticmethod
    def create_template(output_path: Path) -> None:
        """
        Create a template Excel file with example data

        Args:
            output_path: Path where template should be saved
        """
        template_data = {
            'ChartList': [
                'My Watchlist',
                'My Watchlist',
                'Tech Stocks',
                'Energy Sector',
                'Small Caps'
            ],
            'ChartName': [
                'AAPL',
                'MSFT',
                'NVDA',
                'XLE',
                'AEIS'
            ],
            'TabOrder': [1, 2, 3, 4, 5],
            'TimeframeBox': [None, None, 7, None, 10],  # 7=60min, 10=5min
            'Notes': [
                'Check resistance at 180',
                'Earnings next week',
                '60min chart - watch volume',
                'Oil sector ETF',
                '5min chart - day trade setup'
            ]
        }

        df = pd.DataFrame(template_data)

        # Create Excel writer with formatting
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Charts', index=False)

            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Charts']

            # Add column widths
            column_widths = {'A': 15, 'B': 10, 'C': 10, 'D': 15, 'E': 30}
            for col, width in column_widths.items():
                worksheet.column_dimensions[col].width = width

            # Add header formatting (if openpyxl supports it)
            try:
                from openpyxl.styles import Font, PatternFill

                header_font = Font(bold=True)
                header_fill = PatternFill(start_color='CCE5FF', end_color='CCE5FF', fill_type='solid')

                for cell in worksheet[1]:
                    cell.font = header_font
                    cell.fill = header_fill
            except:
                pass  # Formatting is optional

        logger.info(f"Template created at: {output_path}")


def main():
    """Test the Excel reader with a sample file"""
    # Create a template for testing
    template_path = Path("config/chartlist_config_template.xlsx")
    template_path.parent.mkdir(exist_ok=True)

    ChartListConfigReader.create_template(template_path)
    print(f"Template created: {template_path}")

    # Test reading the template
    reader = ChartListConfigReader(template_path)
    configs = reader.load_chart_configs()

    print("\nLoaded configurations:")
    for config in configs:
        print(f"  Tab {config['tab_order']}: {config['chartlist']} > {config['chart_name']}")
        if config['timeframe_box']:
            print(f"    TimeframeBox: {config['timeframe_box']}")
        if config['notes']:
            print(f"    Notes: {config['notes']}")

    # Validate
    validation = reader.validate_config()
    print(f"\nValidation: {'PASS' if validation['is_valid'] else 'FAIL'}")
    if validation['warnings']:
        print(f"Warnings: {validation['warnings']}")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    main()