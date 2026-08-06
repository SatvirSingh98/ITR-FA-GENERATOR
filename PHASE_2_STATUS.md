# Phase 2 Status Update

## Completed Modules (2/3)

### ✅ 1. YahooFinanceScraper (yahoo_scraper.py) - 420 lines
**Status:** Complete and ready for integration
**Responsibility:** Scrape company profiles and stock prices from Yahoo Finance
**Key Methods:**
- `scrape_company_profile(symbol)` - Extract company name, address, zip, country code
- `scrape_stock_prices(symbol)` - Scrape historical stock prices for calendar year
- `detect_country(address)` - Map address to ITR country codes
- `get_price_on_date(df_prices, date)` - Get price with backward search for weekends

### ✅ 2. ScheduleOSFSIGenerator (schedule_os_fsi_generator.py) - 230 lines
**Status:** Complete and ready for integration
**Responsibility:** Generate Schedule OS and FSI
**Key Methods:**
- `calculate_schedule_os(df_dividends)` - Apply Rule 115(1)(e) for dividend income
- `calculate_schedule_fsi(df_dividends, df_capital_gains)` - Aggregate foreign source income
- Quarterly breakup per Section 234C

## Pending Module (1/3)

### ⏳ 3. ScheduleFAGenerator (schedule_fa_generator.py)
**Status:** Not yet created - highly complex
**Reason for delay:** The Table A2/A3 generation logic in the legacy code is extremely intricate:

**Complexity factors:**
1. **Peak Value Calculation:** Daily matrix of (stock price × TTBR) across entire year for EACH holding
2. **Partial Sale Handling:** Splits holdings into separate rows (holding vs sold portions)
3. **Dividend Allocation:** Per-lot dividend distribution based on holdings on dividend dates
4. **Pre-FY TTBR Loading:** Backward search for acquisition dates before calendar year
5. **Multiple Holding Windows:** Different calculation windows for sold vs unsold shares
6. **Matrix Merging:** Complex joins between stock prices, TTBR rates, and holding periods

**Lines of code in legacy:** ~800 lines just for Table A2/A3 logic (lines 1199-2050 in itr_fa_etrade.py)

## Recommended Approach

Given the extreme complexity of ScheduleFAGenerator, I recommend **Phase 2A/2B split:**

### Phase 2A (Current) - Integration with Legacy Delegation
- ✅ Create YahooFinanceScraper (done)
- ✅ Create ScheduleOSFSIGenerator (done)
- ⏳ Create a lightweight ScheduleFAGenerator wrapper that delegates Table A2/A3 to legacy code
- Integrate all three into main.py
- Test end-to-end with legacy fallback
- Commit as "Phase 2A: Partial modularization with legacy delegation"

### Phase 2B (Future) - Full Table A2/A3 Refactoring
- Extract peak calculation logic into separate PeakCalculator class
- Extract dividend allocation into DividendAllocator class
- Extract tranche processing into TrancheProcessor class
- Break 800-line monolith into 4-5 focused classes
- Full test coverage
- Commit as "Phase 2B: Complete Table A2/A3 modularization"

## Current Status: Phase 2A in progress

**What's working:**
- YahooFinanceScraper ready
- ScheduleOSFSIGenerator ready
- Capital Gains (Phase 1) working

**What's pending:**
- ScheduleFAGenerator wrapper (delegates to legacy)
- Integration into main.py
- End-to-end testing

**Why this is pragmatic:**
- Delivers working solution faster
- Reduces risk of breaking complex logic
- Allows incremental refactoring in Phase 2B
- Matches Phase 1 philosophy: modularize what's tractable, delegate what's complex
