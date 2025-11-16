TICKER EXAMPLE FILES
====================

This directory contains example ticker lists for testing and demonstration.

FILE FORMATS:
- Columnar files (*.txt): One ticker per line
- Comma files (*_comma.txt): Comma-separated tickers

EXAMPLE FILES:

Watchlists:
- watchlist_tech.txt        : Technology sector stocks (columnar)
- watchlist_energy.txt      : Energy sector stocks (columnar)
- watchlist_financials.txt  : Financial sector stocks (columnar)

Portfolio:
- portfolio_current.txt     : Current portfolio holdings (columnar)
- portfolio_target.txt      : Target portfolio allocation (columnar)

Market Events:
- earnings_this_week.txt    : Stocks with earnings (comma-separated)
- high_volume_today.txt     : High volume stocks (comma-separated)

ChartLists:
- chartlist_daily.txt       : Daily chart analysis list (columnar)
- chartlist_60min.txt       : 60-minute chart analysis list (columnar)

Strategy Lists:
- breakout_candidates.txt   : Technical breakout patterns (columnar)
- momentum_stocks.txt       : High momentum stocks (columnar)
- value_picks.txt          : Value investment picks (columnar)

COMMON OPERATIONS:

1. Find new additions to watchlist:
   python ../../bin/set_operations.py -a watchlist_tech.txt -b portfolio_current.txt --operation "A-B"

2. Combine all watchlists:
   python ../../bin/set_operations.py -a watchlist_tech.txt -b watchlist_energy.txt -c watchlist_financials.txt --operation "A+B+C"

3. Portfolio rebalancing (what to buy):
   python ../../bin/set_operations.py -a portfolio_target.txt -b portfolio_current.txt --operation "A-B"

4. Multi-strategy intersection:
   python ../../bin/set_operations.py -a breakout_candidates.txt -b momentum_stocks.txt --operation "A&B"

5. Exclude earnings week:
   python ../../bin/set_operations.py -a chartlist_daily.txt -b earnings_this_week.txt --operation "A-B"