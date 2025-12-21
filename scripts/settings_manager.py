"""
Settings Manager - Handles user preferences
Stores: reader mode, reading direction, and other settings
"""

import json
from pathlib import Path

class SettingsManager:
    def __init__(self, settings_file='data/settings.json'):
        self.settings_file = Path(settings_file)
        self.default_settings = {
            'reader_mode': 'scroll',  # 'scroll' or 'single'
            'reading_direction': 'ltr',  # 'ltr' (left-to-right) or 'rtl' (right-to-left)
            'single_page_click_navigation': True,
            'fit_mode': 'width',  # 'width', 'height', 'original'
            'background_color': '#0a0a0a'
        }
        self.settings = self._load_settings()
        
    def _load_settings(self):
        """Load settings from JSON file"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**self.default_settings, **loaded}
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self.default_settings.copy()
        else:
            # Create data directory if it doesn't exist
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            self._save_settings()
            return self.default_settings.copy()
    
    def _save_settings(self):
        """Save settings to JSON file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get_all_settings(self):
        """Get all settings"""
        return self.settings.copy()
    
    def get_setting(self, key):
        """Get a specific setting"""
        return self.settings.get(key, self.default_settings.get(key))
    
    def update_setting(self, key, value):
        """Update a single setting"""
        if key in self.default_settings:
            self.settings[key] = value
            self._save_settings()
            return True
        return False
    
    def update_settings(self, settings_dict):
        """Update multiple settings"""
        for key, value in settings_dict.items():
            if key in self.default_settings:
                self.settings[key] = value
        self._save_settings()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = self.default_settings.copy()
        self._save_settings()