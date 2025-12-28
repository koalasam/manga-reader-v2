"""
Chapter Reader - Handles chapter reading functionality
Returns page lists and navigation info
Includes dual-page mode support
"""

from pathlib import Path
import re
import sys
import os

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from page_pairer import MangaPagePairer

class ChapterReader:
    def __init__(self, manga_root):
        self.manga_root = Path(manga_root)
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        
    def get_chapter_pages(self, series_name, chapter_num):
        """Get all pages for a specific chapter"""
        chapter_path = self.manga_root / series_name / f"chapter-{chapter_num}"
        
        # Try exact match first
        if not chapter_path.exists():
            # Try to find chapter with similar name
            series_path = self.manga_root / series_name
            if series_path.exists():
                for chapter_dir in series_path.iterdir():
                    if chapter_dir.is_dir() and chapter_num in chapter_dir.name:
                        chapter_path = chapter_dir
                        break
        
        if not chapter_path.exists() or not chapter_path.is_dir():
            return None
        
        pages = []
        for file in sorted(chapter_path.iterdir(), key=self._natural_sort_key):
            if file.is_file() and file.suffix.lower() in self.image_extensions:
                # Create relative path from manga root
                rel_path = str(Path(series_name) / chapter_path.name / file.name)
                pages.append(rel_path)
        
        if not pages:
            return None
        
        # Get page pairs for dual mode
        page_pairs = []
        try:
            pairer = MangaPagePairer(str(chapter_path))
            pairs = pairer.pair_pages()
            # Convert pairs to use relative paths
            for pair in pairs:
                pair_paths = [str(Path(series_name) / chapter_path.name / p) for p in pair]
                page_pairs.append(pair_paths)
        except Exception as e:
            print(f"Warning: Could not generate page pairs: {e}")
            # Fallback: simple sequential pairing
            page_pairs = []
            for i in range(0, len(pages), 2):
                if i + 1 < len(pages):
                    page_pairs.append([pages[i], pages[i + 1]])
                else:
                    page_pairs.append([pages[i]])
        
        # Get navigation info
        nav_info = self._get_navigation_info(series_name, chapter_path.name)
        
        return {
            'series_name': series_name,
            'chapter': chapter_path.name,
            'chapter_display': self.format_chapter_name(chapter_path.name),
            'pages': pages,
            'page_pairs': page_pairs,
            'page_count': len(pages),
            'pair_count': len(page_pairs),
            'navigation': nav_info
        }
    
    def format_chapter_name(self, chapter_name):
        """Format chapter name for display"""
        # Extract chapter number
        match = re.search(r'(\d+(?:\.\d+)?)', chapter_name)
        if match:
            num = match.group(1)
            # Remove leading zeros but keep decimal part
            if '.' in num:
                whole, decimal = num.split('.')
                num = f"{int(whole)}.{decimal}"
            else:
                num = str(int(num))
            return f"Chapter {num}"
        
        # Fallback: format the name nicely
        return chapter_name.replace('-', ' ').replace('_', ' ').title()
    
    def _get_navigation_info(self, series_name, current_chapter):
        """Get previous/next chapter info"""
        series_path = self.manga_root / series_name
        
        if not series_path.exists():
            return {}
        
        # Get all chapters
        chapters = []
        for chapter_dir in series_path.iterdir():
            if chapter_dir.is_dir() and self._has_images(chapter_dir):
                chapters.append(chapter_dir.name)
        
        # Sort chapters
        chapters = sorted(chapters, key=self._extract_chapter_number)
        
        # Find current chapter index
        try:
            current_idx = chapters.index(current_chapter)
        except ValueError:
            return {}
        
        nav = {}
        
        # Previous chapter
        if current_idx > 0:
            prev_chapter = chapters[current_idx - 1]
            nav['prev_chapter'] = prev_chapter
            nav['prev_chapter_num'] = self._extract_chapter_number(prev_chapter)
            nav['prev_chapter_display'] = self.format_chapter_name(prev_chapter)
        
        # Next chapter
        if current_idx < len(chapters) - 1:
            next_chapter = chapters[current_idx + 1]
            nav['next_chapter'] = next_chapter
            nav['next_chapter_num'] = self._extract_chapter_number(next_chapter)
            nav['next_chapter_display'] = self.format_chapter_name(next_chapter)
        
        nav['total_chapters'] = len(chapters)
        nav['current_index'] = current_idx + 1
        
        return nav
    
    def _has_images(self, directory):
        """Check if directory contains image files"""
        for file in directory.iterdir():
            if file.is_file() and file.suffix.lower() in self.image_extensions:
                return True
        return False
    
    def _extract_chapter_number(self, chapter_name):
        """Extract chapter number for sorting"""
        match = re.search(r'(\d+(?:\.\d+)?)', chapter_name)
        if match:
            return float(match.group(1))
        return 0
    
    def _natural_sort_key(self, path):
        """Natural sorting key for paths"""
        filename = path.name
        return [int(text) if text.isdigit() else text.lower() 
                for text in re.split(r'(\d+)', filename)]