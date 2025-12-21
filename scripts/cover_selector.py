"""
Cover Selector - Intelligently selects cover images
Finds first non-black-and-white image from first chapter
"""

from pathlib import Path
from PIL import Image
import re

class CoverSelector:
    def __init__(self, manga_root):
        self.manga_root = Path(manga_root)
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        
    def get_best_cover(self, series_name):
        """Get the best cover image for a series"""
        series_path = self.manga_root / series_name
        
        if not series_path.exists():
            return None
        
        # Get first chapter
        chapters = self._get_sorted_chapters(series_path)
        if not chapters:
            return None
        
        first_chapter_path = series_path / chapters[0]
        
        # Get all images from first chapter
        images = self._get_sorted_images(first_chapter_path)
        
        # Find first color image
        for img_name in images:
            img_path = first_chapter_path / img_name
            if self._is_color_image(img_path):
                return str(Path(series_name) / chapters[0] / img_name)
        
        # Fallback to first image if all are B&W
        if images:
            return str(Path(series_name) / chapters[0] / images[0])
        
        return None
    
    def _get_sorted_chapters(self, series_path):
        """Get sorted list of chapter directories"""
        chapters = []
        for chapter_dir in series_path.iterdir():
            if chapter_dir.is_dir() and self._has_images(chapter_dir):
                chapters.append(chapter_dir.name)
        
        return sorted(chapters, key=self._extract_chapter_number)
    
    def _get_sorted_images(self, chapter_path):
        """Get sorted list of images in a chapter"""
        images = []
        for file in chapter_path.iterdir():
            if file.is_file() and file.suffix.lower() in self.image_extensions:
                images.append(file.name)
        
        return sorted(images, key=self._natural_sort_key)
    
    def _is_color_image(self, image_path):
        """
        Check if an image is in color (not grayscale/B&W)
        Returns True if image has significant color content
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if needed
                if img.mode not in ('RGB', 'RGBA'):
                    # If it's in grayscale mode, it's definitely B&W
                    if img.mode == 'L' or img.mode == '1':
                        return False
                    # Try converting other modes to RGB
                    try:
                        img = img.convert('RGB')
                    except:
                        return True  # Assume color if we can't convert
                
                # Resize to smaller size for faster processing
                # We only need to check a sample to determine if it's color
                img_small = img.resize((100, 100), Image.LANCZOS)
                
                # Get pixel data
                pixels = list(img_small.getdata())
                
                # Count pixels with significant color variation
                color_pixels = 0
                total_checked = 0
                
                # Sample up to 1000 pixels
                for pixel in pixels[:1000]:
                    total_checked += 1
                    
                    # Handle different pixel formats
                    if len(pixel) >= 3:
                        r, g, b = pixel[0], pixel[1], pixel[2]
                        
                        # Calculate color variance
                        # If R, G, B values differ significantly, it's a color pixel
                        diff_rg = abs(r - g)
                        diff_gb = abs(g - b)
                        diff_rb = abs(r - b)
                        max_diff = max(diff_rg, diff_gb, diff_rb)
                        
                        # Threshold: if any channel differs by more than 15, count as color
                        if max_diff > 15:
                            color_pixels += 1
                
                # Calculate percentage of color pixels
                if total_checked > 0:
                    color_percentage = (color_pixels / total_checked) * 100
                    
                    # If more than 5% of pixels have color, consider it a color image
                    # This helps skip intro pages that might be mostly B&W with slight color tints
                    return color_percentage > 5.0
                
                return True  # Default to True if we couldn't determine
                
        except Exception as e:
            # If we can't open/process the image, log warning and assume it's valid
            print(f"Warning: Could not analyze image {image_path}: {e}")
            return True
    
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
    
    def _natural_sort_key(self, filename):
        """Natural sorting key for filenames"""
        return [int(text) if text.isdigit() else text.lower() 
                for text in re.split(r'(\d+)', filename)]
    
    def get_chapter_preview(self, series_name, chapter_name, max_images=5):
        """
        Get preview images from a chapter
        Useful for displaying chapter thumbnails
        """
        chapter_path = self.manga_root / series_name / chapter_name
        
        if not chapter_path.exists():
            return []
        
        images = self._get_sorted_images(chapter_path)
        
        # Return first N images as preview
        preview_images = []
        for img_name in images[:max_images]:
            rel_path = str(Path(series_name) / chapter_name / img_name)
            preview_images.append(rel_path)
        
        return preview_images