from PIL import Image, ImageDraw, ImageFont
import io
import base64
from typing import Optional, Tuple, List
from datetime import datetime

class ScreenshotAnnotator:
    """Annotate screenshots with visual markers for agent actions"""
    
    def __init__(self):
        # Try to load a monospace font, fallback to default
        try:
            self.font = ImageFont.truetype("consola.ttf", 16)
            self.font_large = ImageFont.truetype("consola.ttf", 24)
        except:
            self.font = ImageFont.load_default()
            self.font_large = ImageFont.load_default()
    
    def annotate_click(
        self, 
        image_b64: str, 
        x: int, 
        y: int, 
        label: Optional[str] = None
    ) -> str:
        """
        Draw a click marker (red circle with crosshair) at coordinates
        
        Args:
            image_b64: Base64 encoded image
            x, y: Click coordinates
            label: Optional label text
            
        Returns:
            Base64 encoded annotated image
        """
        img = self._decode_image(image_b64)
        draw = ImageDraw.Draw(img)
        
        # Draw red circle
        radius = 20
        draw.ellipse(
            [(x - radius, y - radius), (x + radius, y + radius)],
            outline='red',
            width=3
        )
        
        # Draw crosshair
        crosshair_len = 10
        draw.line([(x - crosshair_len, y), (x + crosshair_len, y)], fill='red', width=2)
        draw.line([(x, y - crosshair_len), (x, y + crosshair_len)], fill='red', width=2)
        
        # Add label if provided
        if label:
            # Draw background for text
            bbox = draw.textbbox((x + 25, y - 10), label, font=self.font)
            draw.rectangle(bbox, fill='red')
            draw.text((x + 25, y - 10), label, fill='white', font=self.font)
        
        return self._encode_image(img)
    
    def annotate_scroll(
        self,
        image_b64: str,
        direction: str,
        amount: int,
        label: Optional[str] = None
    ) -> str:
        """
        Draw scroll indicator (arrow showing direction)
        
        Args:
            image_b64: Base64 encoded image
            direction: 'up' or 'down'
            amount: Scroll distance in pixels
            label: Optional label text
            
        Returns:
            Base64 encoded annotated image
        """
        img = self._decode_image(image_b64)
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # Draw arrow on the right side
        x = width - 50
        y_start = height // 3
        y_end = height // 3 + (100 if direction == 'down' else -100)
        
        # Draw arrow line
        draw.line([(x, y_start), (x, y_end)], fill='blue', width=4)
        
        # Draw arrowhead
        if direction == 'down':
            draw.polygon([(x, y_end), (x - 10, y_end - 15), (x + 10, y_end - 15)], fill='blue')
        else:
            draw.polygon([(x, y_end), (x - 10, y_end + 15), (x + 10, y_end + 15)], fill='blue')
        
        # Add label
        scroll_label = label or f"SCROLL {direction.upper()}\n{amount}px"
        bbox = draw.textbbox((x - 60, y_start + 50), scroll_label, font=self.font)
        draw.rectangle(bbox, fill='blue')
        draw.text((x - 60, y_start + 50), scroll_label, fill='white', font=self.font)
        
        return self._encode_image(img)
    
    def annotate_type(
        self,
        image_b64: str,
        x: int,
        y: int,
        text: str,
        label: Optional[str] = None
    ) -> str:
        """
        Draw text overlay showing what was typed
        
        Args:
            image_b64: Base64 encoded image
            x, y: Input field coordinates
            text: Text that was typed
            label: Optional label
            
        Returns:
            Base64 encoded annotated image
        """
        img = self._decode_image(image_b64)
        draw = ImageDraw.Draw(img)
        
        # Truncate text if too long
        display_text = text[:50] + "..." if len(text) > 50 else text
        type_label = label or f'TYPE: "{display_text}"'
        
        # Draw yellow box with text
        bbox = draw.textbbox((x, y - 40), type_label, font=self.font)
        # Expand bbox for padding
        bbox = (bbox[0] - 5, bbox[1] - 5, bbox[2] + 5, bbox[3] + 5)
        draw.rectangle(bbox, fill='yellow', outline='orange', width=2)
        draw.text((x, y - 40), type_label, fill='black', font=self.font)
        
        # Draw pointer to input field
        draw.line([(x + 10, y - 35), (x + 10, y - 10)], fill='orange', width=2)
        
        return self._encode_image(img)
    
    def annotate_navigate(
        self,
        image_b64: str,
        url: str
    ) -> str:
        """
        Highlight URL bar for navigation actions
        
        Args:
            image_b64: Base64 encoded image
            url: URL navigated to
            
        Returns:
            Base64 encoded annotated image
        """
        img = self._decode_image(image_b64)
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # Draw highlight box at top (where URL bar typically is)
        draw.rectangle([(10, 10), (width - 10, 80)], outline='green', width=4)
        
        # Add label
        nav_label = f"NAVIGATE: {url[:60]}..."
        bbox = draw.textbbox((20, 90), nav_label, font=self.font)
        draw.rectangle(bbox, fill='green')
        draw.text((20, 90), nav_label, fill='white', font=self.font)
        
        return self._encode_image(img)
    
    def add_control_banner(
        self,
        image_b64: str,
        action_type: str,
        timestamp: Optional[str] = None
    ) -> str:
        """
        Add "AGENT CONTROLLED" banner to top of screenshot
        
        Args:
            image_b64: Base64 encoded image
            action_type: Type of action being performed
            timestamp: Optional timestamp
            
        Returns:
            Base64 encoded annotated image
        """
        img = self._decode_image(image_b64)
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # Draw semi-transparent banner (simulate with solid color)
        banner_height = 40
        draw.rectangle([(0, 0), (width, banner_height)], fill='black')
        
        # Add text
        banner_text = f"🤖 AGENT CONTROLLED - {action_type.upper()}"
        draw.text((10, 10), banner_text, fill='white', font=self.font_large)
        
        # Add timestamp if provided
        if timestamp:
            ts_text = timestamp
            ts_bbox = draw.textbbox((0, 0), ts_text, font=self.font)
            ts_width = ts_bbox[2] - ts_bbox[0]
            draw.text((width - ts_width - 10, 12), ts_text, fill='gray', font=self.font)
        
        return self._encode_image(img)
    
    def annotate_multi(
        self,
        image_b64: str,
        annotations: List[dict]
    ) -> str:
        """
        Apply multiple annotations to a single screenshot
        
        Args:
            image_b64: Base64 encoded image
            annotations: List of annotation dicts with keys:
                - type: 'click', 'scroll', 'type', 'navigate'
                - params: dict of parameters for that annotation type
                
        Returns:
            Base64 encoded annotated image
        """
        current_image = image_b64
        
        for annotation in annotations:
            ann_type = annotation['type']
            params = annotation['params']
            
            if ann_type == 'click':
                current_image = self.annotate_click(current_image, **params)
            elif ann_type == 'scroll':
                current_image = self.annotate_scroll(current_image, **params)
            elif ann_type == 'type':
                current_image = self.annotate_type(current_image, **params)
            elif ann_type == 'navigate':
                current_image = self.annotate_navigate(current_image, **params)
            elif ann_type == 'banner':
                current_image = self.add_control_banner(current_image, **params)
        
        return current_image
    
    def _decode_image(self, image_b64: str) -> Image.Image:
        """Decode base64 string to PIL Image"""
        image_data = base64.b64decode(image_b64)
        return Image.open(io.BytesIO(image_data))
    
    def _encode_image(self, img: Image.Image) -> str:
        """Encode PIL Image to base64 string"""
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=70)
        return base64.b64encode(buffer.getvalue()).decode()
