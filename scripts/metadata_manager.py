"""
Metadata Manager - Handles series metadata
Stores: cover art, description, alternate titles
"""

import json
from pathlib import Path

class MetadataManager:
    def __init__(self, metadata_file='data/metadata.json'):
        self.metadata_file = Path(metadata_file)
        self.metadata = self._load_metadata()
        
    def _load_metadata(self):
        """Load metadata from JSON file"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading metadata: {e}")
                return {}
        else:
            # Create data directory if it doesn't exist
            self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
            return {}
    
    def _save_metadata(self):
        """Save metadata to JSON file"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving metadata: {e}")
    
    def get_metadata(self, series_name):
        """Get metadata for a series"""
        return self.metadata.get(series_name)
    
    def set_metadata(self, series_name, metadata_dict):
        """
        Set metadata for a series
        metadata_dict can contain:
        - description: str
        - alternate_titles: list of str
        - custom_cover: str (path)
        - author: str
        - status: str (ongoing, completed, etc.)
        - genres: list of str
        """
        if series_name not in self.metadata:
            self.metadata[series_name] = {}
            
        self.metadata[series_name].update(metadata_dict)
        self._save_metadata()
        
    def update_field(self, series_name, field, value):
        """Update a single metadata field"""
        if series_name not in self.metadata:
            self.metadata[series_name] = {}
            
        self.metadata[series_name][field] = value
        self._save_metadata()
    
    def delete_metadata(self, series_name):
        """Delete metadata for a series"""
        if series_name in self.metadata:
            del self.metadata[series_name]
            self._save_metadata()
    
    def search_metadata(self, query):
        """Search for series by name or alternate titles"""
        query_lower = query.lower()
        results = []
        
        for series_name, meta in self.metadata.items():
            # Check series name
            if query_lower in series_name.lower():
                results.append(series_name)
                continue
                
            # Check alternate titles
            alt_titles = meta.get('alternate_titles', [])
            for alt_title in alt_titles:
                if query_lower in alt_title.lower():
                    results.append(series_name)
                    break
        
        return results