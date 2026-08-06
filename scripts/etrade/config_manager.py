"""
ITR-FA-GENERATOR - Schedule FA Generator for ITR2/ITR3
Copyright (c) 2024-2026 Satvinder Singh
Licensed under GNU General Public License

Configuration Manager
Handles loading and saving config.json
"""

import json
import os


class ConfigManager:
    """Manages application configuration"""

    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load()

    def load(self):
        """Load configuration from JSON file"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(
                f"[ERROR] {self.config_file} not found! "
                f"Copy config.example.json to config.json and edit it."
            )

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"[OK] Loaded configuration from {self.config_file}")
            return config
        except json.JSONDecodeError as e:
            raise ValueError(f"[ERROR] Invalid JSON in {self.config_file}: {e}")

    def save(self):
        """Save configuration to JSON file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        print(f"[OK] Saved company info to {self.config_file} for next run")

    def get(self, key, default=None):
        """Get configuration value by key"""
        return self.config.get(key, default)

    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value

    def get_target_year(self):
        """
        Get target calendar year for ITR filing.

        Returns previous year if not specified in config.
        (ITR filing is for the previous calendar year)
        """
        from datetime import datetime

        target_year = self.config.get('target_year')

        # If target_year is specified in config, use it
        if target_year:
            return int(target_year)

        # Otherwise, auto-detect: previous year
        # (ITR filing in 2026 is for calendar year 2025)
        current_year = datetime.now().year
        return current_year - 1

    def get_account_info(self):
        """Get custodial account information"""
        return self.config.get('custodial_account', {})

    def get_company_config(self, symbol):
        """Get company-specific configuration"""
        companies = self.config.get('table_a3_companies', {})
        return companies.get(symbol)

    def set_company_config(self, symbol, company_data):
        """Save company configuration"""
        if 'table_a3_companies' not in self.config:
            self.config['table_a3_companies'] = {}
        self.config['table_a3_companies'][symbol] = company_data
        self.save()

    def should_disclose_unvested_rsu(self):
        """Check if unvested RSU should be disclosed"""
        return self.config.get('disclose_unvested_rsu', False)
