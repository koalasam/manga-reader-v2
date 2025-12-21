"""
Library Scanner - Scans manga directory structure
Handles: series-name/chapter-# format
"""

from pathlib import Path
import re
import os

class LibraryScanner:
    def __init__(self, manga_root):
        self.manga_root = Path(manga_root)
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        
    def scan_library(self):
        """Scan the entire manga library and return series list"""
        series_list = []
        
        if not self.manga_root.exists():
            print(f"Warning: Manga root directory not found: {self.manga_root}")
            return series_list
            
        for series_dir in sorted(self.manga_root.iterdir()):
            if series_dir.is_dir():
                series_info = self._get_series_basic_info(series_dir)
                if series_info:
                    series_list.append(series_info)
                    
        return series_list
    
    def _get_series_basic_info(self, series_path):
        """Get basic info about a series"""
        series_name = series_path.name
        chapters = self._get_chapters(series_path)
        
        if not chapters:
            return None
            
        # Get cover image (first page of first chapter)
        cover_path = None
        if chapters:
            first_chapter_path = series_path / chapters[0]
            pages = self._get_chapter_pages(first_chapter_path)
            if pages:
                cover_path = str(Path(series_name) / chapters[0] / pages[0])
        
        return {
            'name': series_name,
            'chapter_count': len(chapters),
            'chapters': chapters,
            'cover': cover_path
        }
    
    def get_series_info(self, series_name):
        """Get detailed info for a specific series"""
        series_path = self.manga_root / series_name
        
        if not series_path.exists() or not series_path.is_dir():
            return None
            
        return self._get_series_basic_info(series_path)
    
    def _get_chapters(self, series_path):
        """Get list of chapters for a series"""
        chapters = []
        
        for chapter_dir in series_path.iterdir():
            if chapter_dir.is_dir():
                # Check if directory has images
                if self._has_images(chapter_dir):
                    chapters.append(chapter_dir.name)
        
        # Sort chapters numerically
        return sorted(chapters, key=self._extract_chapter_number)
    
    def _has_images(self, directory):
        """Check if directory contains image files"""
        for file in directory.iterdir():
            if file.is_file() and file.suffix.lower() in self.image_extensions:
                return True
        return False
    
    def _get_chapter_pages(self, chapter_path):
        """Get sorted list of page filenames in a chapter"""
        pages = []
        
        for file in chapter_path.iterdir():
            if file.is_file() and file.suffix.lower() in self.image_extensions:
                pages.append(file.name)
        
        # Sort pages naturally (page1, page2, ..., page10)
        return sorted(pages, key=self._natural_sort_key)
    
    def _extract_chapter_number(self, chapter_name):
        """Extract chapter number for sorting"""
        match = re.search(r'(\d+(?:\.\d+)?)', chapter_name)
        if match:
            return float(match.group(1))
        return 0
    
    def _natural_sort_key(self, filename):
        """Natural sorting key for filenames"""
        return [int(text) if text.isdigit() else text.lower() 
                for text in re.split(r'(\d+)', filename)]