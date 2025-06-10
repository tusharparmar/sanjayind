import cv2
import numpy as np
import pytesseract
from PIL import Image
import base64
import io
import logging
from typing import Dict, List, Any, Optional

class ScreenAnalyzer:
    """Analyze screen content for context-aware AI assistance"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configure Tesseract (you may need to set the path)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
        # pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Linux
        
        self.logger.info("Screen analyzer initialized")
    
    def analyze_screenshot(self, image_data: str) -> Dict[str, Any]:
        """
        Analyze a screenshot and extract useful information
        
        Args:
            image_data (str): Base64 encoded image data
        
        Returns:
            Dict[str, Any]: Analysis results including text, elements, etc.
        """
        try:
            # Decode base64 image
            image = self._decode_base64_image(image_data)
            if image is None:
                return {"error": "Could not decode image"}
            
            # Extract text using OCR
            text_data = self._extract_text(image)
            
            # Detect UI elements
            ui_elements = self._detect_ui_elements(image)
            
            # Analyze layout
            layout_info = self._analyze_layout(image)
            
            # Detect forms
            form_elements = self._detect_forms(text_data, ui_elements)
            
            # Generate summary
            summary = self._generate_summary(text_data, ui_elements, layout_info)
            
            return {
                "text": text_data,
                "ui_elements": ui_elements,
                "layout": layout_info,
                "forms": form_elements,
                "summary": summary,
                "analysis_timestamp": None
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing screenshot: {e}")
            return {"error": str(e)}
    
    def _decode_base64_image(self, image_data: str) -> Optional[np.ndarray]:
        """Decode base64 image data to OpenCV format"""
        try:
            # Remove data URL prefix if present
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            
            # Convert to PIL Image
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to OpenCV format
            opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            return opencv_image
            
        except Exception as e:
            self.logger.error(f"Error decoding image: {e}")
            return None
    
    def _extract_text(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract text from image using OCR"""
        try:
            # Convert to PIL Image for Tesseract
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Extract text with detailed information
            text_data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
            
            # Filter out empty text
            filtered_text = []
            for i, text in enumerate(text_data['text']):
                if text.strip():
                    filtered_text.append({
                        'text': text.strip(),
                        'confidence': text_data['conf'][i],
                        'bbox': {
                            'x': text_data['left'][i],
                            'y': text_data['top'][i],
                            'width': text_data['width'][i],
                            'height': text_data['height'][i]
                        }
                    })
            
            # Extract full text
            full_text = pytesseract.image_to_string(pil_image)
            
            return {
                'full_text': full_text.strip(),
                'text_elements': filtered_text,
                'word_count': len(full_text.split()),
                'has_text': bool(full_text.strip())
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting text: {e}")
            return {
                'full_text': '',
                'text_elements': [],
                'word_count': 0,
                'has_text': False,
                'error': str(e)
            }
    
    def _detect_ui_elements(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect UI elements like buttons, input fields, etc."""
        try:
            elements = []
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect rectangles (potential buttons/input fields)
            rectangles = self._detect_rectangles(gray)
            elements.extend(rectangles)
            
            # Detect circles (potential buttons)
            circles = self._detect_circles(gray)
            elements.extend(circles)
            
            # Detect lines (potential separators)
            lines = self._detect_lines(gray)
            elements.extend(lines)
            
            return elements
            
        except Exception as e:
            self.logger.error(f"Error detecting UI elements: {e}")
            return []
    
    def _detect_rectangles(self, gray_image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect rectangular elements"""
        try:
            rectangles = []
            
            # Edge detection
            edges = cv2.Canny(gray_image, 50, 150, apertureSize=3)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Approximate contour to polygon
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Check if it's roughly rectangular
                if len(approx) >= 4:
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Filter by size (avoid tiny elements)
                    if w > 20 and h > 10:
                        aspect_ratio = w / h
                        area = cv2.contourArea(contour)
                        
                        # Classify based on dimensions
                        element_type = 'rectangle'
                        if aspect_ratio > 3 and h < 50:
                            element_type = 'input_field'
                        elif aspect_ratio < 3 and w < 200 and h < 100:
                            element_type = 'button'
                        
                        rectangles.append({
                            'type': element_type,
                            'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                            'area': area,
                            'aspect_ratio': aspect_ratio
                        })
            
            return rectangles[:20]  # Limit to top 20 elements
            
        except Exception as e:
            self.logger.error(f"Error detecting rectangles: {e}")
            return []
    
    def _detect_circles(self, gray_image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect circular elements (buttons, icons)"""
        try:
            circles = []
            
            # Use HoughCircles to detect circles
            detected_circles = cv2.HoughCircles(
                gray_image,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=30,
                param1=50,
                param2=30,
                minRadius=10,
                maxRadius=100
            )
            
            if detected_circles is not None:
                detected_circles = np.round(detected_circles[0, :]).astype("int")
                
                for (x, y, r) in detected_circles:
                    circles.append({
                        'type': 'circular_button',
                        'bbox': {
                            'x': x - r,
                            'y': y - r,
                            'width': 2 * r,
                            'height': 2 * r
                        },
                        'radius': r,
                        'center': {'x': x, 'y': y}
                    })
            
            return circles[:10]  # Limit to top 10 circles
            
        except Exception as e:
            self.logger.error(f"Error detecting circles: {e}")
            return []
    
    def _detect_lines(self, gray_image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect lines (separators, borders)"""
        try:
            lines = []
            
            # Edge detection
            edges = cv2.Canny(gray_image, 50, 150, apertureSize=3)
            
            # Detect lines using HoughLinesP
            detected_lines = cv2.HoughLinesP(
                edges,
                rho=1,
                theta=np.pi/180,
                threshold=100,
                minLineLength=50,
                maxLineGap=10
            )
            
            if detected_lines is not None:
                for line in detected_lines[:20]:  # Limit to 20 lines
                    x1, y1, x2, y2 = line[0]
                    length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                    
                    # Determine orientation
                    if abs(x2 - x1) > abs(y2 - y1):
                        orientation = 'horizontal'
                    else:
                        orientation = 'vertical'
                    
                    lines.append({
                        'type': 'line',
                        'start': {'x': x1, 'y': y1},
                        'end': {'x': x2, 'y': y2},
                        'length': length,
                        'orientation': orientation
                    })
            
            return lines
            
        except Exception as e:
            self.logger.error(f"Error detecting lines: {e}")
            return []
    
    def _analyze_layout(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze overall layout of the screen"""
        try:
            height, width = image.shape[:2]
            
            # Divide screen into regions
            regions = {
                'top': {'y': 0, 'height': height // 4},
                'middle': {'y': height // 4, 'height': height // 2},
                'bottom': {'y': 3 * height // 4, 'height': height // 4},
                'left': {'x': 0, 'width': width // 3},
                'center': {'x': width // 3, 'width': width // 3},
                'right': {'x': 2 * width // 3, 'width': width // 3}
            }
            
            # Analyze color distribution
            color_analysis = self._analyze_colors(image)
            
            return {
                'dimensions': {'width': width, 'height': height},
                'regions': regions,
                'colors': color_analysis,
                'aspect_ratio': width / height
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing layout: {e}")
            return {}
    
    def _analyze_colors(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze color distribution in the image"""
        try:
            # Convert to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Calculate mean colors
            mean_color = np.mean(rgb_image, axis=(0, 1))
            
            # Determine if image is mostly light or dark
            brightness = np.mean(mean_color)
            theme = 'light' if brightness > 127 else 'dark'
            
            return {
                'mean_rgb': mean_color.tolist(),
                'brightness': brightness,
                'theme': theme
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing colors: {e}")
            return {}
    
    def _detect_forms(self, text_data: Dict[str, Any], ui_elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect form elements and structure"""
        try:
            forms = []
            
            # Look for form-related text
            form_keywords = ['login', 'sign in', 'register', 'submit', 'email', 'password', 'name', 'phone']
            text_content = text_data.get('full_text', '').lower()
            
            has_form_text = any(keyword in text_content for keyword in form_keywords)
            
            # Count input-like elements
            input_elements = [elem for elem in ui_elements if elem.get('type') == 'input_field']
            button_elements = [elem for elem in ui_elements if elem.get('type') == 'button']
            
            if has_form_text or (len(input_elements) > 0 and len(button_elements) > 0):
                forms.append({
                    'type': 'detected_form',
                    'input_fields': len(input_elements),
                    'buttons': len(button_elements),
                    'form_keywords_found': [kw for kw in form_keywords if kw in text_content],
                    'confidence': 0.8 if has_form_text else 0.5
                })
            
            return forms
            
        except Exception as e:
            self.logger.error(f"Error detecting forms: {e}")
            return []
    
    def _generate_summary(self, text_data: Dict[str, Any], ui_elements: List[Dict[str, Any]], layout_info: Dict[str, Any]) -> str:
        """Generate a human-readable summary of the screen content"""
        try:
            summary_parts = []
            
            # Screen dimensions
            if layout_info.get('dimensions'):
                dims = layout_info['dimensions']
                summary_parts.append(f"Screen size: {dims['width']}x{dims['height']}")
            
            # Text content
            if text_data.get('has_text'):
                word_count = text_data.get('word_count', 0)
                summary_parts.append(f"Contains {word_count} words of text")
            
            # UI elements
            if ui_elements:
                element_counts = {}
                for elem in ui_elements:
                    elem_type = elem.get('type', 'unknown')
                    element_counts[elem_type] = element_counts.get(elem_type, 0) + 1
                
                element_summary = ', '.join([f"{count} {elem_type}" for elem_type, count in element_counts.items()])
                summary_parts.append(f"UI elements: {element_summary}")
            
            # Theme
            if layout_info.get('colors', {}).get('theme'):
                theme = layout_info['colors']['theme']
                summary_parts.append(f"Theme: {theme}")
            
            return '. '.join(summary_parts) if summary_parts else "No significant content detected"
            
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return "Error generating summary"
    
    def analyze_dom_content(self, dom_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze DOM content sent from the browser
        
        Args:
            dom_data (dict): DOM information from browser
        
        Returns:
            Dict[str, Any]: Analysis results
        """
        try:
            analysis = {
                'page_info': {
                    'url': dom_data.get('url', ''),
                    'title': dom_data.get('title', ''),
                    'domain': self._extract_domain(dom_data.get('url', ''))
                },
                'content_analysis': {},
                'form_analysis': {},
                'navigation_analysis': {},
                'recommendations': []
            }
            
            # Analyze text content
            if 'text' in dom_data:
                analysis['content_analysis'] = self._analyze_text_content(dom_data['text'])
            
            # Analyze forms
            if 'forms' in dom_data:
                analysis['form_analysis'] = self._analyze_dom_forms(dom_data['forms'])
            
            # Analyze buttons and navigation
            if 'buttons' in dom_data:
                analysis['navigation_analysis'] = self._analyze_navigation_elements(dom_data['buttons'])
            
            # Generate recommendations
            analysis['recommendations'] = self._generate_recommendations(analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing DOM content: {e}")
            return {'error': str(e)}
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return ''
    
    def _analyze_text_content(self, text: str) -> Dict[str, Any]:
        """Analyze text content from DOM"""
        words = text.split()
        return {
            'word_count': len(words),
            'character_count': len(text),
            'has_content': len(text.strip()) > 0,
            'language': 'en',  # Could be enhanced with language detection
            'readability': 'medium'  # Could be enhanced with readability analysis
        }
    
    def _analyze_dom_forms(self, forms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze form elements from DOM"""
        if not forms:
            return {'has_forms': False}
        
        total_fields = sum(len(form.get('elements', [])) for form in forms)
        form_types = []
        
        for form in forms:
            elements = form.get('elements', [])
            has_email = any('email' in elem.get('type', '') or 'email' in elem.get('name', '').lower() for elem in elements)
            has_password = any('password' in elem.get('type', '') for elem in elements)
            
            if has_email and has_password:
                form_types.append('login')
            elif has_email:
                form_types.append('contact')
            else:
                form_types.append('general')
        
        return {
            'has_forms': True,
            'form_count': len(forms),
            'total_fields': total_fields,
            'form_types': form_types
        }
    
    def _analyze_navigation_elements(self, buttons: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze navigation elements"""
        if not buttons:
            return {'has_navigation': False}
        
        nav_keywords = ['home', 'about', 'contact', 'menu', 'login', 'logout', 'sign up', 'register']
        nav_buttons = [btn for btn in buttons if any(keyword in btn.get('text', '').lower() for keyword in nav_keywords)]
        
        return {
            'has_navigation': True,
            'total_buttons': len(buttons),
            'navigation_buttons': len(nav_buttons),
            'button_types': [btn.get('text', '')[:20] for btn in buttons[:5]]  # First 5 button texts
        }
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Form recommendations
        if analysis.get('form_analysis', {}).get('has_forms'):
            recommendations.append("I can help you fill out forms on this page")
        
        # Navigation recommendations
        if analysis.get('navigation_analysis', {}).get('has_navigation'):
            recommendations.append("I can guide you through the navigation options")
        
        # Content recommendations
        content_analysis = analysis.get('content_analysis', {})
        if content_analysis.get('word_count', 0) > 100:
            recommendations.append("I can summarize the content on this page")
        
        return recommendations

