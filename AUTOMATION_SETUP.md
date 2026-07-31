# GitHub Actions Automation Setup

This document explains how to set up automatic daily fetching of SBI TTBR rates using GitHub Actions.

## Overview

The automation runs **daily at 9:00 PM IST** and:
1. Fetches latest USD/INR rate from SBI official PDF
2. Merges with historical rates from GitHub backup
3. Saves to `data/sbi_ttbr_rates.csv`
4. Commits and pushes changes automatically

## Setup Steps

### 1. Push to GitHub

First, push this repository to GitHub:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit with SBI TTBR automation"

# Add remote (replace with your GitHub repo URL)
git remote add origin https://github.com/YOUR_USERNAME/ITR_FA_GENERATOR.git

# Push
git push -u origin main
```

### 2. Enable GitHub Actions

GitHub Actions should be enabled by default. The workflow file is already in place:
- `.github/workflows/fetch_sbi_ttbr.yml`

No additional configuration needed! 🎉

### 3. Verify Workflow

1. Go to your GitHub repository
2. Click on **Actions** tab
3. You should see **"Fetch SBI TTBR Rates Daily"** workflow
4. The workflow will run automatically at 9:00 PM IST every day

### 4. Manual Trigger (Optional)

To test the workflow immediately:

1. Go to: **Actions** → **Fetch SBI TTBR Rates Daily**
2. Click **Run workflow** button
3. Select branch (usually `main`)
4. Click green **Run workflow** button
5. Refresh the page to see the workflow running

## How It Works

### Schedule
- **Cron**: `30 15 * * *` (3:30 PM UTC = 9:00 PM IST)
- **Runs**: Daily, automatically
- **Also**: Can be triggered manually via GitHub UI

### Workflow Steps

1. **Checkout repository** - Gets latest code
2. **Set up Python** - Installs Python 3.11
3. **Install dependencies** - Installs: pandas, requests, PyPDF2, python-dateutil
4. **Run SBI TTBR Fetcher** - Executes `sbi_ttbr_fetcher.py`
5. **Commit and push** - Commits updated CSV if data changed
6. **Upload artifact** - Saves CSV as downloadable artifact (kept 7 days)

### What Gets Committed

The bot will commit:
- `data/sbi_ttbr_rates.csv` (updated with latest rates)

Commit message format:
```
Auto-update: SBI TTBR rates for YYYY-MM-DD

Updated by GitHub Actions bot
Auto-fetched from SBI official PDF + historical GitHub data
```

### Bot Identity

The commits will show:
- **Author**: GitHub Actions Bot
- **Email**: github-actions[bot]@users.noreply.github.com

## Data Location

After automation runs:
- **Local**: `data/sbi_ttbr_rates.csv` (committed to git)
- **GitHub**: Same file, updated daily
- **Artifact**: Available in Actions tab for 7 days (for debugging)

## Monitoring

### Check if it's working

1. **GitHub Actions page**: See green checkmarks for successful runs
2. **Latest commit**: Should show daily commits from "GitHub Actions Bot"
3. **Data file**: Check `data/SBI_FOREX_CARD_RATES_USD.csv` has recent dates

### If it fails

1. Go to **Actions** tab
2. Click on the failed workflow run
3. Expand the failed step to see error logs
4. Common issues:
   - SBI website down: Falls back to GitHub CSV
   - GitHub CSV unavailable: Workflow will fail (needs manual intervention)
   - Network timeout: Will retry next day
   - SBI PDF has stale date: Skips SBI data, uses only GitHub (no commit since no new data)

## Testing Locally

Before relying on GitHub Actions, test locally:

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Run the fetcher
python sbi_forex_fetcher.py

# Check output
type SBI_FOREX_CARD_RATES_USD.csv  # Windows
cat SBI_FOREX_CARD_RATES_USD.csv   # Linux/Mac
```

## Integration with ITR FA Generator

The main script (`itr_fa_engine.py`) automatically uses the CSV if available:

1. **First choice**: Read `data/SBI_FOREX_CARD_RATES_USD.csv` (if exists and has data for target year)
2. **Second choice**: Fetch on-demand using `sbi_forex_fetcher.py`
3. **Third choice**: Use fallback interpolated rates (if all else fails)

This means once you push to GitHub and the automation runs, your local ITR FA Generator will automatically use the pre-fetched data! 🚀

## Cost

GitHub Actions is **FREE** for public repositories and has generous limits for private repos:
- **Public repos**: Unlimited free
- **Private repos**: 2000 minutes/month free (this workflow uses ~2 minutes/day)

## Security Notes

- No API keys or secrets required
- All data sources are public
- Bot only has write access to your repository
- SSL verification disabled for GitHub CSV fallback (mirrors reference implementation)

## Troubleshooting

### Workflow doesn't run
- Check if Actions are enabled in repository settings
- Verify cron syntax in `.github/workflows/fetch_sbi_ttbr.yml`
- Check workflow is on `main` branch

### No commits from bot
- Check workflow logs for errors
- Verify data actually changed (bot only commits if CSV differs)
- Check if you have branch protection rules blocking bot

### Data is stale
- Manually trigger workflow to update immediately
- Check if SBI website changed PDF location (update URL in `sbi_ttbr_fetcher.py`)
- Verify GitHub CSV source is still active

## Reference

This automation is inspired by:
- https://github.com/sahilgupta/sbi-fx-ratekeeper

But with improvements:
- ✅ Fetches from SBI official PDF (more reliable)
- ✅ Falls back to GitHub CSV (historical data)
- ✅ Simplified format (just Date + TTBR)
- ✅ Integrated with ITR FA Generator
