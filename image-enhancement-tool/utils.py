"""
Utility Functions
=================
This module contains helper functions for image I/O, conversion, and UI support.
"""

import io
import cv2
import numpy as np
from PIL import Image
from typing import Optional, Tuple
import streamlit as st


def _ensure_bgr(image: np.ndarray) -> np.ndarray:
    """Convert an image array to 3-channel BGR for OpenCV processing."""
    if image is None:
        return None

    if len(image.shape) == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    if image.shape[2] == 4:
        return cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)

    if image.shape[2] == 3:
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    return image


def load_image_from_upload(uploaded_file) -> Optional[np.ndarray]:
    """
    Load image from Streamlit file uploader.
    
    Args:
        uploaded_file: Image file from st.file_uploader
    
    Returns:
        Image as numpy array (BGR format) or None if error
    """
    try:
        # Read image file
        image = Image.open(uploaded_file)
        
        # Convert to numpy array
        image_np = np.array(image)

        # Normalize to 3-channel BGR so downstream OpenCV functions work reliably
        return _ensure_bgr(image_np)
    except Exception as e:
        st.error(f"Error loading image: {str(e)}")
        return None


def save_image_to_bytes(image: np.ndarray, format: str = 'PNG') -> bytes:
    """
    Convert numpy array to bytes for download.
    
    Args:
        image: Image as numpy array (BGR format)
        format: Output format ('PNG', 'JPEG', etc.)
    
    Returns:
        Image as bytes
    """
    # Convert to a PIL-friendly format
    if len(image.shape) == 2:
        image_rgb = image
    elif image.shape[2] == 4:
        # OpenCV images are typically BGRA; PIL expects RGBA
        if format.upper() == 'JPEG':
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
        else:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
    else:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Convert to PIL Image
    pil_image = Image.fromarray(image_rgb)
    
    # Save to bytes
    buffer = io.BytesIO()
    pil_image.save(buffer, format=format)
    buffer.seek(0)
    
    return buffer.getvalue()


def display_comparison_side_by_side(original: np.ndarray, 
                                     processed: np.ndarray,
                                     title1: str = "Original",
                                     title2: str = "Processed") -> None:
    """
    Display two images side by side using Streamlit columns.
    
    Args:
        original: Original image (BGR format)
        processed: Processed image (BGR format)
        title1: Title for original image
        title2: Title for processed image
    """
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(title1)
        # Convert BGR to RGB for display
        original_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
        st.image(original_rgb, use_column_width=True)
    
    with col2:
        st.subheader(title2)
        # Convert BGR to RGB for display
        processed_rgb = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
        st.image(processed_rgb, use_column_width=True)


def resize_image_for_display(image: np.ndarray, max_height: int = 600) -> np.ndarray:
    """
    Resize image for display purposes (avoid loading large images).
    
    Args:
        image: Input image (any format)
        max_height: Maximum height in pixels
    
    Returns:
        Resized image
    """
    height, width = image.shape[:2]
    
    if height > max_height:
        scale = max_height / height
        width = int(width * scale)
        height = max_height
        image = cv2.resize(image, (width, height))
    
    return image


def get_image_info(image: np.ndarray) -> dict:
    """
    Get basic information about the image.
    
    Args:
        image: Input image (any format)
    
    Returns:
        Dictionary with image information
    """
    height, width = image.shape[:2]
    channels = 1 if len(image.shape) == 2 else image.shape[2]
    
    info = {
        'width': width,
        'height': height,
        'channels': channels,
        'size_mb': (image.nbytes / (1024 * 1024)),
        'aspect_ratio': width / height if height > 0 else 0
    }
    
    return info


def create_histogram(image: np.ndarray, channel: str = 'gray') -> np.ndarray:
    """
    Create histogram visualization.
    
    Args:
        image: Input image (BGR format)
        channel: 'gray', 'blue', 'green', 'red', or 'all'
    
    Returns:
        Histogram image
    """
    # Create histogram image
    hist_image = np.zeros((256, 256, 3), dtype=np.uint8)
    
    if channel == 'gray':
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    else:
        colors = {'blue': (255, 0, 0), 'green': (0, 255, 0), 'red': (0, 0, 255)}
        if channel not in colors:
            channel = 'all'
    
    if channel in ['all', 'blue', 'green', 'red']:
        channels = [2, 1, 0]  # BGR
        colors_list = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]
        
        for i, col in enumerate(channels):
            hist = cv2.calcHist([image], [col], None, [256], [0, 256])
            hist = cv2.normalize(hist, hist).flatten() * 256
            
            for x in range(256):
                cv2.line(hist_image, (x, 256), 
                        (x, 256 - int(hist[x])), colors_list[i], 1)
    else:
        hist_colors = colors.get(channel, (128, 128, 128))
        if channel == 'gray':
            cv2.line(hist_image, (0, 256), (0, 256), (128, 128, 128), 1)
    
    return hist_image


def apply_quality_metrics(original: np.ndarray, processed: np.ndarray) -> dict:
    """
    Calculate quality metrics between original and processed images.
    
    Args:
        original: Original image
        processed: Processed image
    
    Returns:
        Dictionary with quality metrics
    """
    # Ensure same shape
    if original.shape != processed.shape:
        min_height = min(original.shape[0], processed.shape[0])
        min_width = min(original.shape[1], processed.shape[1])
        original = original[:min_height, :min_width]
        processed = processed[:min_height, :min_width]
    
    # Calculate metrics
    mse = np.mean((original.astype(np.float32) - processed.astype(np.float32)) ** 2)
    
    # PSNR calculation
    if mse > 0:
        psnr = 20 * np.log10(255.0 / np.sqrt(mse))
    else:
        psnr = float('inf')
    
    # Structural Similarity (simplified)
    original_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    processed_gray = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
    
    ssim = cv2.matchTemplate(original_gray, processed_gray, cv2.TM_CCOEFF)
    
    return {
        'mse': mse,
        'psnr': psnr,
        'similarity': min(1.0, max(0.0, ssim[0][0] / 255)),
    }


@st.cache_data
def load_sample_image(filename: str = "sample.jpg") -> Optional[np.ndarray]:
    """
    Load a sample image from the sample_images folder.
    
    Args:
        filename: Name of the sample image file
    
    Returns:
        Image as numpy array or None
    """
    try:
        import os
        sample_path = os.path.join('sample_images', filename)
        if os.path.exists(sample_path):
            image = cv2.imread(sample_path)
            return image
        return None
    except Exception as e:
        print(f"Error loading sample image: {str(e)}")
        return None


def create_before_after_slider(original: np.ndarray, processed: np.ndarray,
                                slider_value: float = 0.5) -> np.ndarray:
    """
    Create a before/after comparison image with slider effect.
    
    Args:
        original: Original image (BGR format)
        processed: Processed image (BGR format)
        slider_value: Position of slider (0.0 to 1.0)
    
    Returns:
        Composite image
    """
    # Ensure same dimensions
    height, width = original.shape[:2]
    if processed.shape[:2] != (height, width):
        processed = cv2.resize(processed, (width, height))
    
    # Calculate split position
    split_x = int(width * slider_value)
    
    # Create composite
    composite = original.copy()
    composite[:, split_x:] = processed[:, split_x:]
    
    # Add a line to show the split
    cv2.line(composite, (split_x, 0), (split_x, height), (0, 255, 0), 3)
    
    return composite


def get_dominant_colors(image: np.ndarray, k: int = 5) -> list:
    """
    Extract dominant colors from image using K-means clustering.
    
    Args:
        image: Input image (BGR format)
        k: Number of dominant colors to extract
    
    Returns:
        List of dominant colors in BGR format
    """
    # Reshape image to list of pixels
    data = image.reshape((-1, 3))
    data = np.float32(data)
    
    # K-means clustering
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, _, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    
    centers = np.uint8(centers)
    
    return centers.tolist()


def apply_gradient_map(image: np.ndarray, gradient_type: str = 'cool') -> np.ndarray:
    """
    Apply gradient/colourmap effect to image.
    
    Args:
        image: Input image (BGR format)
        gradient_type: Type of gradient ('cool', 'warm', 'jet', 'hsv')
    
    Returns:
        Gradient-mapped image
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply colormap
    colormap_dict = {
        'cool': cv2.COLORMAP_COOL,
        'warm': cv2.COLORMAP_AUTUMN,
        'jet': cv2.COLORMAP_JET,
        'hsv': cv2.COLORMAP_HSV,
        'hot': cv2.COLORMAP_HOT,
        'viridis': cv2.COLORMAP_VIRIDIS,
    }
    
    colormap = colormap_dict.get(gradient_type, cv2.COLORMAP_COOL)
    result = cv2.applyColorMap(gray, colormap)
    
    return result


def optimize_image_for_web(image: np.ndarray, max_width: int = 1920,
                           max_height: int = 1080, quality: int = 85) -> np.ndarray:
    """
    Optimize image for web display (resize and compress).
    
    Args:
        image: Input image (BGR format)
        max_width: Maximum width
        max_height: Maximum height
        quality: JPEG quality (1-100)
    
    Returns:
        Optimized image
    """
    height, width = image.shape[:2]
    
    # Calculate scaling factor
    scale = min(1.0, min(max_width / width, max_height / height))
    
    if scale < 1.0:
        new_width = int(width * scale)
        new_height = int(height * scale)
        image = cv2.resize(image, (new_width, new_height))
    
    return image
