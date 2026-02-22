import cv2
import numpy as np
import pytesseract
from PIL import Image
import re
from typing import Dict, List, Tuple, Optional
import json

class PokemonCardIdentifier:
    """
    Identifies Pokemon cards from images using computer vision and OCR
    """
    
    def __init__(self):
        self.confidence_threshold = 0.7
        self.card_aspect_ratio = 2.5 / 3.5  # Standard Pokemon card ratio
        
    def detect_card_boundaries(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Detect card boundaries and return corrected/cropped card image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150, apertureSize=3)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find the largest rectangular contour (likely the card)
        for contour in sorted(contours, key=cv2.contourArea, reverse=True):
            # Approximate contour to polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # If we found a 4-sided polygon, check if it's card-like
            if len(approx) == 4:
                # Check aspect ratio
                rect = cv2.boundingRect(approx)
                aspect_ratio = rect[2] / rect[3]  # width/height
                
                if 0.5 < aspect_ratio < 0.8:  # Reasonable card ratio range
                    # Perspective correction
                    return self._correct_perspective(image, approx)
        
        # If no card detected, return original image
        return image
    
    def _correct_perspective(self, image: np.ndarray, corners: np.ndarray) -> np.ndarray:
        """
        Apply perspective correction to straighten the card
        """
        # Order corners: top-left, top-right, bottom-right, bottom-left
        corners = corners.reshape(4, 2)
        
        # Calculate target dimensions
        width = 350  # Standard card width in pixels
        height = int(width / self.card_aspect_ratio)
        
        # Define target corners
        target_corners = np.array([
            [0, 0],
            [width, 0],
            [width, height],
            [0, height]
        ], dtype=np.float32)
        
        # Calculate perspective transform
        matrix = cv2.getPerspectiveTransform(corners.astype(np.float32), target_corners)
        
        # Apply transformation
        corrected = cv2.warpPerspective(image, matrix, (width, height))
        
        return corrected
    
    def extract_text_regions(self, image: np.ndarray) -> Dict[str, str]:
        """
        Extract text from different regions of the card
        """
        height, width = image.shape[:2]
        
        # Define regions of interest for different card elements
        regions = {
            'name': image[int(height * 0.05):int(height * 0.15), :],  # Top area
            'hp': image[int(height * 0.05):int(height * 0.15), int(width * 0.7):],  # Top-right
            'type': image[int(height * 0.15):int(height * 0.3), :],  # Below name
            'set_info': image[int(height * 0.85):, :],  # Bottom area
            'full_card': image  # Entire card for fallback
        }
        
        extracted_text = {}
        
        for region_name, region_image in regions.items():
            try:
                # Use pytesseract for OCR
                text = pytesseract.image_to_string(
                    region_image,
                    config='--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,/()-'
                )
                extracted_text[region_name] = text.strip()
            except Exception as e:
                print(f"OCR failed for region {region_name}: {e}")
                extracted_text[region_name] = ""
        
        return extracted_text
    
    def parse_card_info(self, text_regions: Dict[str, str]) -> Dict[str, any]:
        """
        Parse extracted text to identify card information
        """
        card_info = {
            'name': '',
            'hp': None,
            'type': '',
            'set_number': '',
            'set_name': '',
            'rarity': '',
            'confidence': 0.0
        }
        
        # Extract Pokemon name (usually first line in name region)
        name_text = text_regions.get('name', '').split('\n')[0].strip()
        if name_text:
            card_info['name'] = name_text
        
        # Extract HP (look for number followed by HP)
        hp_match = re.search(r'(\d+)\s*HP', text_regions.get('hp', ''), re.IGNORECASE)
        if hp_match:
            card_info['hp'] = int(hp_match.group(1))
        
        # Extract set information from bottom of card
        set_text = text_regions.get('set_info', '')
        set_match = re.search(r'(\d+)/(\d+)', set_text)
        if set_match:
            card_info['set_number'] = f"{set_match.group(1)}/{set_match.group(2)}"
        
        # Calculate confidence based on how much info we extracted
        confidence_factors = []
        if card_info['name']: confidence_factors.append(0.4)
        if card_info['hp']: confidence_factors.append(0.3)
        if card_info['set_number']: confidence_factors.append(0.3)
        
        card_info['confidence'] = sum(confidence_factors)
        
        return card_info
    
    def identify_card(self, image_path: str) -> Dict[str, any]:
        """
        Main method to identify a Pokemon card from an image file
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return {'error': 'Could not load image'}
            
            # Step 1: Detect and correct card boundaries
            card_image = self.detect_card_boundaries(image)
            
            # Step 2: Extract text from different regions
            text_regions = self.extract_text_regions(card_image)
            
            # Step 3: Parse card information
            card_info = self.parse_card_info(text_regions)
            
            # Add debug info
            card_info['extracted_text'] = text_regions
            card_info['image_path'] = image_path
            
            return card_info
            
        except Exception as e:
            return {'error': f'Identification failed: {str(e)}'}

def main():
    """Test the card identifier with a sample image"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python card_identifier.py <image_path>")
        sys.exit(1)
    
    identifier = PokemonCardIdentifier()
    result = identifier.identify_card(sys.argv[1])
    
    print("Card Identification Result:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()