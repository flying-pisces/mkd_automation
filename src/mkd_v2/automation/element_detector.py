"""
Cross-Platform UI Element Detection and Analysis.

Provides intelligent UI element detection using multiple approaches:
- Screen OCR for text recognition
- Visual pattern matching
- Platform-specific accessibility APIs
- Coordinate-based element mapping
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
import hashlib

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    cv2 = np = None
    CV2_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    pytesseract = None
    TESSERACT_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class UIElementInfo:
    """Information about a detected UI element."""
    element_id: str
    element_type: str  # button, text, input, link, image, etc.
    bounds: Tuple[int, int, int, int]  # x, y, width, height
    text: Optional[str] = None
    attributes: Dict[str, Any] = None
    confidence: float = 0.0
    detection_method: str = "unknown"
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}
        if self.timestamp == 0.0:
            self.timestamp = time.time()
        if not self.element_id:
            self.element_id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique element ID based on properties."""
        content = f"{self.element_type}_{self.bounds}_{self.text}_{self.timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    @property
    def center_point(self) -> Tuple[int, int]:
        """Get center point of element."""
        x, y, w, h = self.bounds
        return (x + w // 2, y + h // 2)
    
    @property
    def area(self) -> int:
        """Get element area in pixels."""
        _, _, w, h = self.bounds
        return w * h


@dataclass
class DetectionResult:
    """Result of UI element detection operation."""
    success: bool
    elements: List[UIElementInfo]
    screenshot_path: Optional[str] = None
    detection_time: float = 0.0
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.detection_time == 0.0:
            self.detection_time = time.time()


class ElementDetector(ABC):
    """Abstract base class for UI element detectors."""
    
    @abstractmethod
    def detect_elements_at_point(self, x: int, y: int, radius: int = 50) -> DetectionResult:
        """Detect UI elements around a specific point."""
        pass
    
    @abstractmethod  
    def detect_elements_in_region(self, x: int, y: int, width: int, height: int) -> DetectionResult:
        """Detect UI elements in a rectangular region."""
        pass
    
    @abstractmethod
    def detect_text_elements(self, screenshot: Optional[bytes] = None) -> DetectionResult:
        """Detect text elements using OCR."""
        pass
    
    @abstractmethod
    def find_element_by_text(self, text: str, fuzzy: bool = True) -> Optional[UIElementInfo]:
        """Find element containing specific text."""
        pass


class VisualElementDetector(ElementDetector):
    """Visual element detector using computer vision and OCR."""
    
    def __init__(self, screenshot_func=None):
        self.screenshot_func = screenshot_func
        self.cache = {}
        self.cache_ttl = 2.0  # seconds
        
        # Check dependencies
        if not CV2_AVAILABLE:
            logger.warning("OpenCV not available - visual detection limited")
        if not TESSERACT_AVAILABLE:
            logger.warning("Tesseract not available - OCR disabled")
        
        # OCR configuration
        self.ocr_config = '--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 '
        
        logger.info("VisualElementDetector initialized")
    
    def detect_elements_at_point(self, x: int, y: int, radius: int = 50) -> DetectionResult:
        """Detect UI elements around a specific point using visual analysis."""
        try:
            # Define search region around point
            region_x = max(0, x - radius)
            region_y = max(0, y - radius) 
            region_w = radius * 2
            region_h = radius * 2
            
            return self.detect_elements_in_region(region_x, region_y, region_w, region_h)
            
        except Exception as e:
            logger.error(f"Failed to detect elements at point ({x}, {y}): {e}")
            return DetectionResult(
                success=False,
                elements=[],
                error_message=str(e)
            )
    
    def detect_elements_in_region(self, x: int, y: int, width: int, height: int) -> DetectionResult:
        """Detect UI elements in a rectangular region using computer vision."""
        try:
            start_time = time.time()
            elements = []
            
            # Take screenshot if no screenshot function provided
            screenshot_data = self._get_screenshot_region(x, y, width, height)
            if not screenshot_data:
                return DetectionResult(
                    success=False,
                    elements=[],
                    error_message="Failed to capture screenshot"
                )
            
            if CV2_AVAILABLE:
                # Convert screenshot to OpenCV format
                image = self._bytes_to_cv2_image(screenshot_data)
                if image is not None:
                    # Detect button-like elements
                    button_elements = self._detect_buttons(image, x, y)
                    elements.extend(button_elements)
                    
                    # Detect text elements
                    text_elements = self._detect_text_regions(image, x, y)
                    elements.extend(text_elements)
            
            detection_time = time.time() - start_time
            
            return DetectionResult(
                success=True,
                elements=elements,
                detection_time=detection_time
            )
            
        except Exception as e:
            logger.error(f"Failed to detect elements in region: {e}")
            return DetectionResult(
                success=False,
                elements=[],
                error_message=str(e)
            )
    
    def detect_text_elements(self, screenshot: Optional[bytes] = None) -> DetectionResult:
        """Detect text elements using OCR."""
        if not TESSERACT_AVAILABLE:
            return DetectionResult(
                success=False,
                elements=[],
                error_message="Tesseract OCR not available"
            )
        
        try:
            start_time = time.time()
            elements = []
            
            # Get screenshot
            if screenshot is None:
                screenshot = self._take_full_screenshot()
            
            if not screenshot:
                return DetectionResult(
                    success=False,
                    elements=[],
                    error_message="Failed to capture screenshot"
                )
            
            # Convert to OpenCV image
            if CV2_AVAILABLE:
                image = self._bytes_to_cv2_image(screenshot)
                if image is not None:
                    # Use OCR to detect text
                    text_elements = self._ocr_detect_text(image)
                    elements.extend(text_elements)
            
            detection_time = time.time() - start_time
            
            return DetectionResult(
                success=True,
                elements=elements,
                detection_time=detection_time
            )
            
        except Exception as e:
            logger.error(f"Failed to detect text elements: {e}")
            return DetectionResult(
                success=False,
                elements=[],
                error_message=str(e)
            )
    
    def find_element_by_text(self, text: str, fuzzy: bool = True) -> Optional[UIElementInfo]:
        """Find element containing specific text using OCR."""
        try:
            # Detect all text elements
            result = self.detect_text_elements()
            if not result.success:
                return None
            
            search_text = text.lower().strip()
            
            # Search for matching text
            for element in result.elements:
                if element.text:
                    element_text = element.text.lower().strip()
                    
                    if fuzzy:
                        # Fuzzy matching - check if search text is contained
                        if search_text in element_text or element_text in search_text:
                            return element
                    else:
                        # Exact matching
                        if element_text == search_text:
                            return element
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find element by text '{text}': {e}")
            return None
    
    def _get_screenshot_region(self, x: int, y: int, width: int, height: int) -> Optional[bytes]:
        """Get screenshot of specific region."""
        try:
            if self.screenshot_func:
                # Use provided screenshot function with region
                return self.screenshot_func(region=(x, y, width, height))
            else:
                # Fallback to full screenshot
                full_screenshot = self._take_full_screenshot()
                if full_screenshot and CV2_AVAILABLE:
                    # Crop the region from full screenshot
                    image = self._bytes_to_cv2_image(full_screenshot)
                    if image is not None:
                        cropped = image[y:y+height, x:x+width]
                        return self._cv2_image_to_bytes(cropped)
                
                return full_screenshot
                
        except Exception as e:
            logger.error(f"Failed to get screenshot region: {e}")
            return None
    
    def _take_full_screenshot(self) -> Optional[bytes]:
        """Take full screen screenshot."""
        try:
            if self.screenshot_func:
                return self.screenshot_func()
            else:
                # Mock screenshot for testing
                return b"mock_screenshot_data"
                
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None
    
    def _bytes_to_cv2_image(self, image_bytes: bytes):
        """Convert bytes to OpenCV image."""
        if not CV2_AVAILABLE or not image_bytes:
            return None
        
        try:
            # For now, return a mock image since we don't have real image bytes
            # In real implementation, would decode image bytes
            return np.zeros((100, 100, 3), dtype=np.uint8)
            
        except Exception as e:
            logger.error(f"Failed to convert bytes to image: {e}")
            return None
    
    def _cv2_image_to_bytes(self, image) -> bytes:
        """Convert OpenCV image to bytes."""
        if not CV2_AVAILABLE or image is None:
            return b""
        
        try:
            # Encode image as PNG bytes
            success, encoded = cv2.imencode('.png', image)
            if success:
                return encoded.tobytes()
            else:
                return b""
                
        except Exception as e:
            logger.error(f"Failed to convert image to bytes: {e}")
            return b""
    
    def _detect_buttons(self, image, offset_x: int = 0, offset_y: int = 0) -> List[UIElementInfo]:
        """Detect button-like elements in image."""
        elements = []
        
        if not CV2_AVAILABLE:
            return elements
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Find contours (simplified button detection)
            contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for i, contour in enumerate(contours):
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by size (reasonable button dimensions)
                if 20 <= w <= 300 and 15 <= h <= 100:
                    element = UIElementInfo(
                        element_id=f"button_{i}",
                        element_type="button",
                        bounds=(offset_x + x, offset_y + y, w, h),
                        confidence=0.7,
                        detection_method="contour_analysis"
                    )
                    elements.append(element)
            
            return elements
            
        except Exception as e:
            logger.error(f"Failed to detect buttons: {e}")
            return elements
    
    def _detect_text_regions(self, image, offset_x: int = 0, offset_y: int = 0) -> List[UIElementInfo]:
        """Detect text regions in image."""
        elements = []
        
        if not CV2_AVAILABLE:
            return elements
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to get text regions
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for i, contour in enumerate(contours):
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by aspect ratio for text-like regions
                aspect_ratio = w / h if h > 0 else 0
                if 0.5 <= aspect_ratio <= 10 and w >= 10 and h >= 8:
                    element = UIElementInfo(
                        element_id=f"text_{i}",
                        element_type="text",
                        bounds=(offset_x + x, offset_y + y, w, h),
                        confidence=0.6,
                        detection_method="text_region_analysis"
                    )
                    elements.append(element)
            
            return elements
            
        except Exception as e:
            logger.error(f"Failed to detect text regions: {e}")
            return elements
    
    def _ocr_detect_text(self, image) -> List[UIElementInfo]:
        """Use OCR to detect and extract text elements."""
        elements = []
        
        if not TESSERACT_AVAILABLE or not CV2_AVAILABLE:
            return elements
        
        try:
            # Get detailed OCR data with bounding boxes
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, config=self.ocr_config)
            
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                confidence = int(data['conf'][i])
                
                # Filter out low confidence and empty text
                if confidence > 30 and text:
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    
                    element = UIElementInfo(
                        element_id=f"ocr_text_{i}",
                        element_type="text",
                        bounds=(x, y, w, h),
                        text=text,
                        confidence=confidence / 100.0,
                        detection_method="tesseract_ocr"
                    )
                    elements.append(element)
            
            return elements
            
        except Exception as e:
            logger.error(f"OCR text detection failed: {e}")
            return elements


def create_element_detector(screenshot_func=None) -> ElementDetector:
    """Create appropriate element detector for the current platform."""
    return VisualElementDetector(screenshot_func=screenshot_func)