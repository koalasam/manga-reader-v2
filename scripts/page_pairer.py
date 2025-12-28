import os
import re
import cv2
import numpy as np

class MangaPagePairer:
    def __init__(self, image_dir):
        self.image_dir = image_dir
        self.image_files = self._load_images()

    # -------------------------------------------------
    # Load & sort numeric filenames
    # -------------------------------------------------
    def _load_images(self):
        files = []
        for f in os.listdir(self.image_dir):
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                m = re.match(r"(\d+)", f)
                if m:
                    files.append(f)
        return sorted(files, key=lambda x: int(re.match(r"(\d+)", x).group(1)))

    # -------------------------------------------------
    # Full paths
    # -------------------------------------------------
    def _get_image_paths(self):
        return [os.path.join(self.image_dir, f) for f in self.image_files]

    # -------------------------------------------------
    # Double spread detection
    # -------------------------------------------------
    def _is_double_spread(self, image_path, ratio=1.35):
        img = cv2.imread(image_path)
        if img is None:
            return False
        h, w = img.shape[:2]
        return (w / h) >= ratio

    # -------------------------------------------------
    # Black page detection
    # -------------------------------------------------
    def _is_black_page(self, image_path, threshold=40, min_ratio=0.65):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return False
        dark = np.sum(img < threshold)
        return (dark / img.size) >= min_ratio

    # -------------------------------------------------
    # Solid-color page detection (artsy edge cases)
    # -------------------------------------------------
    def _is_solid_color_page(self, image_path, std_threshold=4.0):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return False
        return np.std(img) <= std_threshold

    # -------------------------------------------------
    # Detect page side using white-density analysis
    # -------------------------------------------------
    def _detect_page_side_with_confidence(
        self,
        image_path,
        region_fraction=0.33,
        white_threshold=230
    ):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return "left", 0.0
        h, w = img.shape
        region_w = int(w * region_fraction)
        left_region = img[:, :region_w]
        right_region = img[:, -region_w:]
        
        left_white = np.sum(left_region >= white_threshold)
        right_white = np.sum(right_region >= white_threshold)
        
        total = left_white + right_white
        if total == 0:
            return "left", 0.0
        
        diff = abs(left_white - right_white)
        confidence = min(diff / total, 1.0)
        side = "left" if left_white > right_white else "right"
        return side, confidence

    # -------------------------------------------------
    # Determine first page side using MOST confident page
    # -------------------------------------------------
    def _determine_first_page_side(self, image_paths):
        # --- PRIORITY CHECK: Double Spread Parity ---
        # If we find a double spread at index N, we can mathematically determine
        # if the first page (Index 0) should stand alone to ensure N lands correctly.
        for idx, path in enumerate(image_paths):
            if self._is_double_spread(path):
                # If index is Even (0, 2, 4...), the pages before it (even count)
                # can pair up perfectly [0,1], [2,3]. So P0 is NOT alone. (Return False)
                # If index is Odd (1, 3...), we need P0 to stand alone [0], [1,2] 
                # to push the double spread to a new slot. (Return True)
                return (idx % 2) != 0

        # --- FALLBACK: Confidence Analysis ---
        best = {
            "confidence": 0.0,
            "index": None,
            "side": None
        }
        
        for idx, path in enumerate(image_paths):
            # Skip unusable pages for density check
            if self._is_black_page(path) or self._is_solid_color_page(path):
                continue
                
            side, conf = self._detect_page_side_with_confidence(path)
            
            if conf > best["confidence"]:
                best.update({
                    "confidence": conf,
                    "index": idx,
                    "side": side
                })

        if best["index"] is None:
            return True  # safe fallback if no clear signal found

        idx = best["index"]
        side = best["side"]
        
        # Work backwards using parity
        if side == "left":
            return (idx % 2) == 1
        else:
            return (idx % 2) == 0

    # -------------------------------------------------
    # Pair pages
    # -------------------------------------------------
    def pair_pages(self):
        image_paths = self._get_image_paths()
        paired = []
        if not image_paths:
            return paired

        # Determine if we need to offset the first page
        start_left = self._determine_first_page_side(image_paths)
        
        i = 0
        if start_left:
            paired.append([self.image_files[0]])
            i = 1

        while i < len(image_paths):
            current = image_paths[i]
            
            # 1. Handle actual double spread
            if self._is_double_spread(current):
                paired.append([self.image_files[i]])
                i += 1
                continue

            # 2. Handle filler/black pages
            if self._is_black_page(current) or self._is_solid_color_page(current):
                paired.append([self.image_files[i]])
                i += 1
                continue

            # 3. Handle Pairing
            if i + 1 < len(image_paths):
                next_page = image_paths[i + 1]
                
                # Check if the NEXT page prevents pairing (is double/black/solid)
                if (
                    not self._is_double_spread(next_page)
                    and not self._is_black_page(next_page)
                    and not self._is_solid_color_page(next_page)
                ):
                    paired.append([self.image_files[i], self.image_files[i + 1]])
                    i += 2
                    continue

            # 4. Fallback: Add as single
            paired.append([self.image_files[i]])
            i += 1
            
        return paired