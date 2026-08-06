"""
ITR-FA-GENERATOR - Schedule FA Generator for ITR2/ITR3
Copyright (c) 2024-2026 Satvinder Singh
Licensed under GNU General Public License

YahooFinanceScraper
Handles company profile and stock price scraping from Yahoo Finance
"""

import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class YahooFinanceScraper:
    """Scrape company information and stock prices from Yahoo Finance"""

    def __init__(self, calendar_year=2025):
        """
        Args:
            calendar_year (int): Year for stock price scraping
        """
        self.calendar_year = calendar_year
        self.start_date = f"{calendar_year}-01-01"
        self.end_date = f"{calendar_year}-12-31"

        # ITR Schedule FA Country Codes (common ones)
        self.country_mapping = {
            "UNITED STATES": {"name": "UNITED STATES OF AMERICA", "code": "2"},
            "USA": {"name": "UNITED STATES OF AMERICA", "code": "2"},
            "U.S.A": {"name": "UNITED STATES OF AMERICA", "code": "2"},
            "CANADA": {"name": "CANADA", "code": "3"},
            "UNITED KINGDOM": {"name": "UNITED KINGDOM", "code": "1"},
            "UK": {"name": "UNITED KINGDOM", "code": "1"},
            "GERMANY": {"name": "GERMANY", "code": "4"},
            "FRANCE": {"name": "FRANCE", "code": "5"},
            "JAPAN": {"name": "JAPAN", "code": "6"},
            "AUSTRALIA": {"name": "AUSTRALIA", "code": "7"},
            "SWITZERLAND": {"name": "SWITZERLAND", "code": "8"},
            "NETHERLANDS": {"name": "NETHERLANDS", "code": "9"},
            "SINGAPORE": {"name": "SINGAPORE", "code": "10"},
            "HONG KONG": {"name": "HONG KONG", "code": "11"},
            "CHINA": {"name": "CHINA", "code": "12"},
            "SOUTH KOREA": {"name": "SOUTH KOREA", "code": "13"},
            "KOREA": {"name": "SOUTH KOREA", "code": "13"},
            "TAIWAN": {"name": "TAIWAN", "code": "14"},
            "INDIA": {"name": "INDIA", "code": "15"},
            "BRAZIL": {"name": "BRAZIL", "code": "16"},
            "MEXICO": {"name": "MEXICO", "code": "17"},
            "ISRAEL": {"name": "ISRAEL", "code": "18"},
            "IRELAND": {"name": "IRELAND", "code": "19"},
            "SPAIN": {"name": "SPAIN", "code": "20"},
            "ITALY": {"name": "ITALY", "code": "21"},
        }

    def detect_country(self, address):
        """
        Detect country from address and return ITR-compliant country name and code.

        Args:
            address (str): Company address string

        Returns:
            tuple: (country_name, country_code)
        """
        address_upper = address.upper()

        # Try to detect country from address
        for country_key, country_data in self.country_mapping.items():
            if country_key in address_upper:
                return country_data["name"], country_data["code"]

        # Default to USA if not detected
        print(f"     [!] Could not detect country from address, defaulting to USA")
        return "UNITED STATES OF AMERICA", "2"

    def scrape_company_profile(self, symbol):
        """
        Scrapes company profile information from Yahoo Finance.

        Args:
            symbol (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT')

        Returns:
            dict: {
                'company_name': str,
                'company_address': str,
                'zip_code': str,
                'country_name': str,
                'country_code': str
            }
        """
        print(f"[*] Fetching company profile for {symbol}...")

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = None
        try:
            driver = webdriver.Chrome(options=chrome_options)

            # Go to Yahoo Finance profile page
            url = f"https://finance.yahoo.com/quote/{symbol}/profile"
            driver.get(url)
            time.sleep(3)  # Wait for page to load

            # Extract company info from asset-profile section
            company_name = f"{symbol} Inc."  # Default
            full_address = "United States"  # Default
            zip_code = "00000"  # Default
            country_name = "UNITED STATES OF AMERICA"  # Default
            country_code = "2"  # Default (USA)

            try:
                # Find the asset-profile section using data-testid
                profile_section = driver.find_element(By.CSS_SELECTOR, "[data-testid='asset-profile']")

                # Extract company name (h3 within asset-profile)
                try:
                    company_name = profile_section.find_element(By.CSS_SELECTOR, "h3").text.strip()
                except:
                    print(f"[!] Could not extract company name from h3")

                # Extract address from nested classes: .company-details > .company-info > .address
                # The .address class has 3 divs: [street, city+state+zip, country]
                # We only need first 2 divs (street + city/state/zip)
                try:
                    # All are class names, not tags
                    address_element = profile_section.find_element(By.CSS_SELECTOR, ".company-details .company-info .address")

                    # Get all div children (3 divs: street, city+state+zip, country)
                    address_divs = address_element.find_elements(By.TAG_NAME, "div")

                    # Extract country from third div (for country detection)
                    country_text = ""
                    if len(address_divs) >= 3:
                        country_text = address_divs[2].text.strip()

                    # Extract zip from the second div (city, state, zip)
                    # Zip is the last word (after last space) that's 5 digits
                    if len(address_divs) >= 2:
                        city_state_zip = address_divs[1].text.strip()
                        # Split by space and get last element as zip
                        parts = city_state_zip.split()
                        if parts and len(parts[-1]) == 5 and parts[-1].isdigit():
                            zip_code = parts[-1]
                            # Remove zip from city_state_zip for address
                            city_state_no_zip = " ".join(parts[:-1])
                        else:
                            city_state_no_zip = city_state_zip

                        # Build full address from first div (street) + second div without zip
                        street = address_divs[0].text.strip() if len(address_divs) >= 1 else ""
                        full_address = f"{street} {city_state_no_zip}".strip()

                        # Use country text for detection (more accurate than address)
                        if country_text:
                            country_name, country_code = self.detect_country(country_text)
                    else:
                        # Fallback if structure is different
                        address_parts = [address_divs[i].text.strip() for i in range(min(2, len(address_divs))) if address_divs[i].text.strip()]
                        full_address = " ".join(address_parts)

                except Exception as e:
                    print(f"[!] Could not extract address element: {e}")

            except Exception as e:
                print(f"[!] Could not find asset-profile section: {e}")

            # Detect country from address (only if not already detected from third div)
            try:
                if not country_name or country_name == "":
                    country_name, country_code = self.detect_country(full_address)
            except:
                country_name, country_code = self.detect_country(full_address)

            # If zip code wasn't extracted from div structure, try regex as fallback
            if not zip_code or zip_code == "":
                zip_match = re.search(r'\b(\d{5})\b', full_address)
                zip_code = zip_match.group(1) if zip_match else "00000"

            print(f"[OK] {company_name}")
            print(f"     Country: {country_name} (Code: {country_code})")
            print(f"     Address: {full_address}")
            print(f"     Zip: {zip_code}")

            driver.quit()

            return {
                "company_name": company_name,
                "company_address": full_address,
                "zip_code": zip_code,
                "country_name": country_name,
                "country_code": country_code
            }

        except Exception as e:
            print(f"[!] Error scraping profile for {symbol}: {e}")
            if driver:
                driver.quit()
            return {
                "company_name": f"{symbol} Inc.",
                "company_address": "United States",
                "zip_code": "00000",
                "country_name": "UNITED STATES OF AMERICA",
                "country_code": "2"
            }

    def scrape_stock_prices(self, symbol):
        """
        Scrapes stock price data from Yahoo Finance using Selenium.

        Args:
            symbol (str): Stock ticker symbol

        Returns:
            DataFrame: Columns: ['Date', 'Stock_Close_USD']
                      Sorted by date, filtered to calendar_year
        """
        print(f"[*] Scraping {symbol} stock prices from Yahoo Finance...")
        print(f"[*] This may take 30-60 seconds, please wait...")

        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in background
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.page_load_strategy = 'eager'  # Don't wait for all resources

        driver = None
        try:
            # Initialize driver - use system Chrome directly
            driver = webdriver.Chrome(options=chrome_options)

            # Navigate to history page
            url = f"https://finance.yahoo.com/quote/{symbol}/history/"
            print(f"[*] Opening {url}")
            driver.get(url)
            time.sleep(5)

            print("[*] Setting custom date range...")
            try:
                # Click on the date picker to open it
                date_picker = driver.find_element(By.CSS_SELECTOR, "div[data-testid='history-date-picker']")
                date_picker.click()
                time.sleep(3)

                # Find and fill the startDate field (format: mm/dd/yyyy)
                # Yahoo Finance might exclude boundaries, so request one day earlier
                print(f"[*] Setting start date to 12/31/{self.calendar_year - 1} (to ensure we get 01/01/{self.calendar_year})...")
                start_date_input = driver.find_element(By.CSS_SELECTOR, "input[name='startDate']")
                start_date_input.clear()
                time.sleep(0.5)
                start_date_input.send_keys(f"12/31/{self.calendar_year - 1}")
                time.sleep(1)

                # Find and fill the endDate field (format: mm/dd/yyyy)
                # Request one day later to ensure we get 12/31/year
                print(f"[*] Setting end date to 01/01/{self.calendar_year + 1} (to ensure we get 12/31/{self.calendar_year})...")
                end_date_input = driver.find_element(By.CSS_SELECTOR, "input[name='endDate']")
                end_date_input.clear()
                time.sleep(0.5)
                end_date_input.send_keys(f"01/01/{self.calendar_year + 1}")
                time.sleep(1)

                # Try multiple selectors for Done button
                print("[*] Looking for Done button...")
                done_clicked = False
                done_selectors = [
                    "//button[text()='Done']",
                    "//button[contains(text(), 'Done')]",
                    "//span[text()='Done']/parent::button",
                    "//button[@type='submit']",
                    "button[type='submit']"
                ]

                for selector in done_selectors:
                    try:
                        if selector.startswith('//'):
                            done_button = driver.find_element(By.XPATH, selector)
                        else:
                            done_button = driver.find_element(By.CSS_SELECTOR, selector)
                        done_button.click()
                        done_clicked = True
                        print(f"[OK] Set date range: 12/31/{self.calendar_year - 1} - 01/01/{self.calendar_year + 1} (will filter to {self.calendar_year}), clicked Done")
                        break
                    except:
                        continue

                if not done_clicked:
                    print("[!] Could not find Done button, pressing Enter on end date field...")
                    end_date_input.send_keys(Keys.RETURN)

                # Wait for table to reload with full year data
                print("[*] Waiting for table to reload with full year data...")
                time.sleep(10)

            except Exception as e:
                print(f"[!] Could not set date range: {str(e)[:80]}")
                print("[!] Using default view (last 12 months only)")

            # Scrape table data
            print("[*] Scraping price table...")
            rows = driver.find_elements(By.XPATH, "//table[@data-test='historical-prices']//tbody//tr")

            if not rows:
                # Try alternative selector
                rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

            if not rows:
                raise Exception("Could not find price table")

            print(f"[*] Found {len(rows)} rows in table, filtering for year {self.calendar_year}...")

            data = []
            for row in rows:
                try:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 6:
                        date_str = cols[0].text.strip()
                        # Use Adj Close (Column 5) instead of Close (Column 4)
                        # Adj Close accounts for splits, dividends, and other corporate actions
                        adj_close_price = cols[5].text.replace(',', '').strip()

                        # Parse date
                        date_obj = pd.to_datetime(date_str, errors='coerce')
                        if pd.isna(date_obj):
                            continue

                        date_formatted = date_obj.strftime('%Y-%m-%d')

                        # Filter for target year only
                        if self.start_date <= date_formatted <= self.end_date:
                            data.append({
                                'Date': date_formatted,
                                'Stock_Close_USD': float(adj_close_price)
                            })
                except:
                    continue

            if not data:
                raise Exception(f"No data found for {self.calendar_year}")

            df = pd.DataFrame(data)
            df = df.sort_values('Date')
            print(f"[OK] Scraped {len(df)} trading days for {symbol} in {self.calendar_year}")
            return df

        except Exception as e:
            print(f"[!] ERROR scraping Yahoo Finance: {str(e)}")
            print(f"[!] Falling back to yfinance API")

            # Fallback to yfinance API
            try:
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                df_stock = yf.download(symbol, start=self.start_date, end=self.end_date, progress=False)

                if not df_stock.empty:
                    if isinstance(df_stock.columns, pd.MultiIndex):
                        df_stock = df_stock['Close']
                    df_stock = df_stock.reset_index()
                    df_stock['Date'] = pd.to_datetime(df_stock['Date']).dt.strftime('%Y-%m-%d')
                    df_stock = df_stock.rename(columns={'Close': 'Stock_Close_USD'})
                    df_stock = df_stock[['Date', 'Stock_Close_USD']]
                    print(f"[OK] Fetched {len(df_stock)} days via yfinance API")
                    return df_stock
            except:
                pass

            return pd.DataFrame()

        finally:
            if driver:
                driver.quit()

    def get_price_on_date(self, df_prices, target_date):
        """
        Get stock price for a specific date (with backward search for weekends/holidays).

        Args:
            df_prices (DataFrame): Price data from scrape_stock_prices()
            target_date (str): Date in 'YYYY-MM-DD' format

        Returns:
            float: Stock price (or None if not found)
        """
        # Try exact match first
        exact_row = df_prices[df_prices['Date'] == target_date]
        if not exact_row.empty:
            return exact_row['Stock_Close_USD'].values[0]

        # Backward search for previous trading day
        df_before = df_prices[df_prices['Date'] < target_date]
        if not df_before.empty:
            closest_date = df_before['Date'].max()
            price = df_before[df_before['Date'] == closest_date]['Stock_Close_USD'].values[0]
            print(f"[i] {target_date} is weekend/holiday, using {closest_date} price: ${price:.2f}")
            return price

        return None
