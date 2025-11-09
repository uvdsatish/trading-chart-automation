# Production Use Case #2: ChartList Batch Viewer - Implementation Plan

## Overview
Create a system that reads an Excel file specifying charts from different ChartLists, then opens each chart in a separate browser tab in the specified order for manual review.

## User Requirements
- Open charts from different ChartLists in specific order
- Configuration via Excel file
- Each chart opens in its own tab
- Browser stays open for manual inspection

## Excel File Structure

### Schema Design

| Column | Description | Example | Required |
|--------|-------------|---------|----------|
| `ChartList` | Name of the ChartList containing the chart | "Tech Momentum" | Yes |
| `Ticker` | Stock symbol | "AAPL" | Yes |
| `TabOrder` | Order to open tabs (1, 2, 3...) | 1 | Yes |
| `TimeframeBox` | Optional ChartStyle box number | 7 | No |
| `Notes` | Optional user notes | "Check resistance at $180" | No |

### Example Configuration

| ChartList | Ticker | TabOrder | TimeframeBox | Notes |
|-----------|--------|----------|--------------|-------|
| Tech Momentum | AAPL | 1 | | Key resistance watch |
| Tech Momentum | NVDA | 2 | | Volume confirmation needed |
| Energy Plays | XLE | 3 | | Oil sector leader |
| Small Caps | AEIS | 4 | 7 | 60min chart - earnings next week |
| Tech Momentum | MSFT | 5 | | Consolidation pattern |

## Implementation Architecture

### New Components

#### 1. Excel Reader (`src/utils/excel_reader.py`)
```python
class ChartListConfigReader:
    def __init__(self, excel_path: Path)
    def load_chart_configs() -> List[Dict]
    def validate_config() -> Dict
```

#### 2. ChartList Navigator (extend `StockChartsController`)
New methods to add:
- `navigate_to_chartlist_gallery()`: Navigate to ChartList gallery page
- `get_available_chartlists()`: Get list of all user's ChartLists
- `open_chartlist(chartlist_name)`: Open a specific ChartList by name
- `navigate_to_chart_in_list(ticker)`: Navigate to specific chart within ChartList
- `open_charts_from_excel(excel_path)`: Main orchestration method

#### 3. Main Entry Point
Add new mode to `main.py`:
- `chartlist_batch_viewer(excel_path, config)`: Production Use Case #2 main function

## Implementation Phases

### Phase 1: Research ChartList Navigation (Day 1-2)
**Objective**: Understand how ChartLists work on StockCharts.com

**Tasks**:
1. Create investigation method similar to `investigate_login_flow()`
2. Navigate to ChartList gallery manually and inspect HTML
3. Identify selectors for:
   - ChartList gallery URL (likely `https://stockcharts.com/freecharts/gallery.html`)
   - ChartList links/buttons
   - Charts within a ChartList
   - Navigation to individual charts
4. Document URL patterns
5. Test with multiple ChartLists

**Deliverables**:
- Research findings document with selectors
- Navigation strategy (direct URL vs clicking through UI)

### Phase 2: Excel Reader Component (Day 3)
**Objective**: Create robust Excel configuration reader

**Tasks**:
1. Create `src/utils/excel_reader.py`
2. Implement `ChartListConfigReader` class
3. Add validation logic:
   - Required columns present
   - TabOrder is numeric and unique
   - ChartList and Ticker are non-empty
4. Create Excel template file
5. Unit tests for Excel parsing

**Deliverables**:
- Working Excel reader with validation
- Template Excel file for users

### Phase 3: ChartList Navigation Methods (Day 4-5)
**Objective**: Implement reliable ChartList navigation

**Tasks**:
1. Add ChartList methods to `StockChartsController`
2. Implement `navigate_to_chartlist_gallery()`
3. Implement `open_chartlist(chartlist_name)`
4. Implement `navigate_to_chart_in_list(ticker)`
5. Add error handling for missing lists/charts
6. Test with real ChartLists

**Deliverables**:
- Reliable ChartList navigation methods
- Error handling for edge cases

### Phase 4: Batch Tab Opener (Day 6-7)
**Objective**: Orchestrate opening multiple charts in tabs

**Tasks**:
1. Implement `open_charts_from_excel()` orchestration method
2. Handle tab creation and management
3. Apply fullscreen/maximization to each tab
4. Screenshot capture for each tab
5. Progress logging

**Deliverables**:
- Working batch tab opener
- Screenshots for verification

### Phase 5: Main Entry Point & Testing (Day 8)
**Objective**: Complete end-to-end workflow

**Tasks**:
1. Add `chartlist_batch_viewer()` to `main.py`
2. Add command-line arguments:
   - `--mode chartlist-batch`
   - `--config <excel_path>`
3. Implement user wait/exit logic
4. Add helpful terminal output
5. Test with various configurations

**Deliverables**:
- Complete working feature
- User documentation

## Detailed Workflow

```
1. Load Excel Configuration
   ├─ Read config/chartlist_config.xlsx
   ├─ Validate columns and data
   └─ Sort by TabOrder

2. Initialize Browser & Login
   ├─ Launch browser (kiosk mode with admin)
   └─ Login to StockCharts.com

3. For Each Chart in Excel (sorted by TabOrder):
   ├─ Navigate to ChartList gallery
   ├─ Open specific ChartList by name
   ├─ Find ticker within ChartList
   ├─ Click chart to navigate to full chart page
   ├─ Create new browser tab (if not first chart)
   ├─ Optional: Apply ChartStyle box if TimeframeBox specified
   ├─ Apply fullscreen maximization
   ├─ Capture screenshot
   └─ Store tab reference

4. Browser Stays Open
   ├─ All tabs visible in order specified by Excel
   ├─ User manually reviews each tab
   └─ User presses Enter or closes browser when done

5. Cleanup
   └─ Close browser and save session log
```

## Error Handling Strategy

| Error | Cause | Handling |
|-------|-------|----------|
| ChartList not found | Typo in Excel or list was deleted | Log warning, skip to next chart |
| Ticker not found in list | Typo or ticker removed from list | Log warning, skip to next chart |
| Excel file missing | User didn't create config file | Show helpful error with template location |
| Invalid TabOrder | Duplicates or non-numeric values | Fail fast with clear error message |
| Login failure | Credentials issue | Abort entire operation |
| TimeframeBox invalid | Box number doesn't exist | Use default timeframe, log warning |

## Command Line Usage

```bash
# Basic usage
python main.py --mode chartlist-batch --config config/my_charts.xlsx

# With custom screenshot directory
python main.py --mode chartlist-batch --config my_charts.xlsx --screenshot-dir batch_screenshots

# Debug mode
python main.py --mode chartlist-batch --config my_charts.xlsx --log-level DEBUG
```

## Expected Terminal Output

```
======================================================================
CHARTLIST BATCH VIEWER
======================================================================
Configuration: config/chartlist_config.xlsx
Charts to open: 5

Logging in to StockCharts.com...
[SUCCESS] Login successful!

Opening charts...

[Tab 1/5] Opening 'AAPL' from 'Tech Momentum'...
  [OK] Found ChartList 'Tech Momentum'
  [OK] Found ticker 'AAPL'
  [OK] Screenshot saved: screenshots/tab1_Tech_Momentum_AAPL.png
  [SUCCESS] Tab 1 opened

[Tab 2/5] Opening 'NVDA' from 'Tech Momentum'...
  [OK] Found ChartList 'Tech Momentum'
  [OK] Found ticker 'NVDA'
  [OK] Screenshot saved: screenshots/tab2_Tech_Momentum_NVDA.png
  [SUCCESS] Tab 2 opened

[Tab 3/5] Opening 'XLE' from 'Energy Plays'...
  [OK] Found ChartList 'Energy Plays'
  [OK] Found ticker 'XLE'
  [OK] Screenshot saved: screenshots/tab3_Energy_Plays_XLE.png
  [SUCCESS] Tab 3 opened

[Tab 4/5] Opening 'AEIS' from 'Small Caps'...
  [OK] Found ChartList 'Small Caps'
  [OK] Found ticker 'AEIS'
  [OK] Applying ChartStyle box #7 (60min)
  [OK] Screenshot saved: screenshots/tab4_Small_Caps_AEIS_60min.png
  [SUCCESS] Tab 4 opened

[Tab 5/5] Opening 'MSFT' from 'Tech Momentum'...
  [OK] Found ChartList 'Tech Momentum'
  [OK] Found ticker 'MSFT'
  [OK] Screenshot saved: screenshots/tab5_Tech_Momentum_MSFT.png
  [SUCCESS] Tab 5 opened

======================================================================
ALL TABS OPENED - 5/5 successful
======================================================================
ChartLists accessed: Tech Momentum, Energy Plays, Small Caps

Tabs open (in order):
  1. Tech Momentum > AAPL
  2. Tech Momentum > NVDA
  3. Energy Plays > XLE
  4. Small Caps > AEIS (60min)
  5. Tech Momentum > MSFT

======================================================================
BROWSER IS NOW OPEN IN KIOSK FULLSCREEN MODE
======================================================================
[KIOSK MODE] Browser using entire monitor (no taskbar/UI)
[NAVIGATION] Switch between tabs: Ctrl+Tab or click tabs
[EXIT] Use Alt+F4 to close browser (F11 disabled in kiosk)
[ALTERNATIVE] Press Enter in this terminal to close

Waiting for user to finish review...
```

## File Structure (New Files)

```
poc_browser_automation/
├── config/
│   ├── chartlist_config.xlsx             # NEW: User's chart configuration
│   └── chartlist_config_template.xlsx    # NEW: Empty template for users
│
├── docs/
│   └── use_case_2_plan.md               # NEW: This planning document
│
├── src/
│   ├── utils/                           # NEW: Utility modules directory
│   │   ├── __init__.py
│   │   └── excel_reader.py              # NEW: Excel parsing logic
│   │
│   └── browser/
│       └── stockcharts_controller.py    # MODIFIED: Add ChartList methods
│
├── main.py                               # MODIFIED: Add chartlist-batch mode
├── requirements.txt                      # MODIFIED: Add openpyxl
└── CLAUDE.md                            # MODIFIED: Document Use Case #2
```

## Dependencies to Add

```python
# Add to requirements.txt
openpyxl==3.1.2          # Required for reading .xlsx files with pandas
```

Note: `pandas==2.1.4` already exists in requirements.txt

## Technical Challenges & Mitigations

### Challenge 1: ChartList URL Structure Unknown
**Mitigation**: Investigation phase will discover actual URLs and navigation patterns. Have fallback to click-through navigation if direct URLs don't exist.

### Challenge 2: Chart Identification Within ChartList
**Mitigation**: Research phase will determine if charts are identified by ticker only or have custom names. Excel schema flexible enough to adapt.

### Challenge 3: Tab Ordering
**Mitigation**: Pre-sort by TabOrder in Excel reader. Verify tab order after creation.

### Challenge 4: Performance with Many Tabs
**Mitigation**: Add configurable delays between tab creations. Warn if more than 10 tabs requested.

## Future Enhancements (Post-MVP)

1. **ChartList Auto-Discovery**: Scan all ChartLists and generate Excel template
2. **AI Analysis Integration**: After opening tabs, run AI analysis on all charts
3. **Session Save/Restore**: Save which tabs were open for quick reload
4. **Conditional Opening**: Only open if ticker meets criteria (e.g., volume > threshold)
5. **Export Current Tabs**: Save currently open tabs back to Excel

## Success Criteria

- [ ] Can read Excel configuration file
- [ ] Can navigate to ChartList gallery
- [ ] Can open specific ChartList by name
- [ ] Can find and open chart within ChartList
- [ ] Opens charts in correct tab order
- [ ] All tabs stay open for manual review
- [ ] Clear error messages for missing lists/charts
- [ ] Works with admin privileges for fullscreen
- [ ] Screenshots captured for verification

## Notes for Next Session

1. Start with Phase 1 - Research ChartList navigation
2. Key unknowns to resolve:
   - Exact ChartList gallery URL
   - How charts are listed within a ChartList
   - Whether direct navigation URLs exist
3. May need to adjust Excel schema based on findings
4. Remember to test with admin privileges for fullscreen