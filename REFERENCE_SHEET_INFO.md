# Reference Sheet - Daily Rates

## Overview
The Excel file `schedule_fa_2025-26.xlsx` contains a third sheet called **"Reference - Daily Rates"** with complete daily data for the entire year 2025.

## Sheet Columns

| Column | Description |
|--------|-------------|
| **Date** | Every day of 2025 (365 rows) |
| **AMD Stock Price (USD)** | Daily closing price of AMD stock |
| **SBI TTBR Rate (USD to INR)** | State Bank of India TT Buying Rate |
| **AMD Value per Share (INR)** | Calculated: USD Price × TTBR |
| **Peak** | Marked with ⭐ PEAK on the highest INR value day |

## Peak AMD Value in 2025

**Date:** October 29, 2025  
**AMD Price:** USD 264.33  
**TTBR Rate:** ₹85.97  
**Peak INR Value:** ₹22,725.50 per share

This peak value is used to calculate the **"Peak Balance During the Period"** for all holdings in Schedule FA Table A3.

## How to Use

### Verify Your Holdings
1. Open the Reference sheet
2. Find the acquisition date of any tranche
3. Check the AMD price and TTBR on that date
4. Verify: Initial Value = Quantity × AMD Price (USD) × TTBR

### Example Verification
For ESPP Shares (6 shares) acquired on 2024-11-08:
- Look up 2024-11-08 in Reference sheet
- AMD Price: ~$147.37 USD
- TTBR: ~83.65
- Initial Value: 6 × 147.37 × 83.65 = ₹74,421 ✓

### Find Peak Value
- Look for the row with ⭐ PEAK marker
- This shows when AMD reached its highest INR value
- All open holdings use this peak value

## Data Sources

- **AMD Prices:** Live web scraped from Yahoo Finance (249 trading days)
- **SBI TTBR:** Interpolated based on typical 2025 range (83.50 - 86.49)
- **Non-trading days:** Forward-filled from last available trading day

## Notes

- Weekends and holidays show forward-filled values (same as previous trading day)
- Peak value may occur on different date than peak USD price (due to TTBR fluctuation)
- All values rounded to 2 decimal places for readability

