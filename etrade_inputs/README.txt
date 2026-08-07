E*TRADE INPUT FILES
===================

Place the following E*TRADE export files here:

REQUIRED:
- ByStatus_expanded.xlsx  (Current holdings)
- ClientStatements_*.pdf  (Account statement for closing balance)

REQUIRED IF YOU SOLD SHARES:
- G&L_Expanded.xlsx       (Gains & Losses - sold shares)
  ⚠️ Without this file, Table A3 will be incomplete!

OPTIONAL:
- Transaction_History.csv (Dividend transactions)

How to export from E*TRADE:
1. Log in to E*TRADE
2. Go to Stock Plan > My Account > Holdings
3. Export as Excel (expanded view)
4. Save as ByStatus_expanded.xlsx

For G&L report:
1. Go to Stock Plan > My Account > Gains & Losses
2. Export as Excel (expanded view)
3. Save as G&L_Expanded.xlsx

For ClientStatements:
1. Log in to E*TRADE
2. Go to Documents > Documents & Statements
3. In the filter select Statements
4. Select timeframe to target year (calendar year) > Apply
5. Download the Dec 31 statement

NEVER COMMIT THESE FILES TO GIT - They contain personal financial data!
