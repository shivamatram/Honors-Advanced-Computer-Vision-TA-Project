"""
Artistic Image Filters
======================
This module contains advanced artistic filter effects using OpenCV.
Includes cartoon, sketch, and other creative effects.
"""

import cv2
import numpy as np
from typing import Tuple


def cartoon_filter(image: np.ndarray, down_sampling: int = 2, 
                  bilateral_iterations: int = 7) -> np.ndarray:
    """
    Apply a cartoon effect to the image.
    Creates a simplified, poster-like version of the image.
    
    Args:
        image: Input image (BGR format)
        down_sampling: Downsampling factor for faster processing
        bilateral_iterations: Number of bilateral filter iterations
    
    Returns:
        Cartoonified image
    """
    # Downsample for faster processing
    height, width = image.shape[:2]
    small_image = cv2.resize(image, (width // down_sampling, height // down_sampling))
    
    # Apply bilateral filter multiple times for edge-preserving smoothing
    cartoon_image = small_image
    for _ in range(bilateral_iterations):
        cartoon_image = cv2.bilateralFilter(cartoon_image, 9, 75, 75)
    
    # Upsample back to original size
    cartoon_image = cv2.resize(cartoon_image, (width, height))
    
    # Detect edges
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                   cv2.THRESH_BINARY, 9, 10)
    
    # Convert edges to 3 channels
    edges_3ch = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    # Invert edges for combining
    edges_inv = 255 - edges_3ch
    
    # Combine cartoon image with edge lines
    result = cv2.bitwise_and(cartoon_image, edges_inv)
    
    return result


def pencil_sketch_filter(image: np.ndarray, sigma_s: float = 60.0, 
                        sigma_r: float = 0.4, shade_factor: float = 0.02) -> np.ndarray:
    """
    Apply a pencil sketch effect to the image.
    Creates a grayscale sketchy appearance.
    
    Args:
        image: Input image (BGR format)
        sigma_s: Spatial extent of the kernel
        sigma_r: Range of the kernel (color/intensity)
        shade_factor: Factor for shade (color sketch)
    
    Returns:
        Pencil sketch image
    """
    # Apply domain transform filter for edge-preserving smoothing
    smoothed = cv2.ximgproc.dtFilter(image, image, sigma_s, sigma_r)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Create inverted grayscale
    gray_inv = 255 - gray
    
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray_inv, (21, 21), 0)
    
    # Create sketch using color dodge blend mode formula
    sketch = cv2.divide(gray, 255 - blurred + 1, scale=256)
    
    return sketch


def pencil_sketch_colored(image: np.ndarray, sigma_s: float = 60.0,
                         sigma_r: float = 0.4) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate both grayscale and colored pencil sketches.
    
    Args:
        image: Input image (BGR format)
        sigma_s: Spatial extent of the kernel
        sigma_r: Range of the kernel
    
    Returns:
        Tuple of (grayscale_sketch, colored_sketch)
    """
    # Grayscale sketch
    gray_sketch = pencil_sketch_filter(image, sigma_s, sigma_r)
    
    # Colored sketch using edge-preserving filter
    kernel_size = 15
    sigma = 0
    
    # Apply stylization filter for colored sketch effect
    colored_sketch = cv2.stylization(image, sigma_s=int(sigma_s), sigma_r=sigma_r)
    
    return gray_sketch, colored_sketch


def sepia_tone(image: np.ndarray, intensity: float = 1.0) -> np.ndarray:
    """
    Apply a sepia tone effect (vintage brown color).
    
    Args:
        image: Input image (BGR format)
        intensity: Intensity of sepia effect (0.0 to 1.0)
    
    Returns:
        Sepia-toned image
    """
    # Sepia matrix in BGR format
    sepia_matrix = np.array([[0.272, 0.534, 0.131],
                             [0.349, 0.686, 0.168],
                             [0.393, 0.769, 0.189]])
    
    # Apply sepia
    sepia_image = cv2.transform(image, sepia_matrix)
    sepia_image = np.clip(sepia_image, 0, 255).astype(np.uint8)
    
    # Blend with original based on intensity
    result = cv2.addWeighted(image, 1 - intensity, sepia_image, intensity, 0)
    
    return result


def oil_painting_effect(image: np.ndarray, size: int = 7, 
                        dynRatio: int = 1) -> np.ndarray:
    """
    Apply an oil painting effect using xphoto module.
    
    Args:
        image: Input image (BGR format)
        size: Size for averaging neighborhood
        dynRatio: Dynamic ratio for color quantization
    
    Returns:
        Oil painting style image
    """
    # Use bilateral filter as alternative if xphoto is not available
    # This gives a similar painterly effect
    result = image.copy()
    
    # Multiple bilateral filter applications for oil painting effect
    for _ in range(2):
        result = cv2.bilateralFilter(result, size, 50, 50)
    
    return result


def watercolor_effect(image: np.ndarray) -> np.ndarray:
    """
    Apply a watercolor painting effect.
    
    Args:
        image: Input image (BGR format)
    
    Returns:
        Watercolor style image
    """
    # Reduce colors
    data = image.reshape((-1, 3))
    data = np.float32(data)
    
    # K-means clustering for posterization
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(data, 8, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    
    centers = np.uint8(centers)
    result = centers[labels.flatten()]
    result = result.reshape(image.shape)
    
    # Apply slight blur for watercolor effect
    result = cv2.medianBlur(result, 5)
    
    return result


def posterize_effect(image: np.ndarray, levels: int = 4) -> np.ndarray:
    """
    Apply a posterization effect by reducing color levels.
    
    Args:
        image: Input image (BGR format)
        levels: Number of color levels (2 to 8)
    
    Returns:
        Posterized image
    """
    # Ensure levels is within valid range
    levels = max(2, min(levels, 8))
    
    # Calculate bins
    bins = 256 // levels
    
    # Apply posterization
    result = (image // bins) * bins + bins // 2
    result = np.clip(result, 0, 255).astype(np.uint8)
    
    return result


def edge_detection_canny(image: np.ndarray, threshold1: float = 100, 
                        threshold2: float = 200) -> np.ndarray:
    """
    Apply Canny edge detection.
    
    Args:
        image: Input image (BGR format)
        threshold1: Lower threshold
        threshold2: Upper threshold
    
    Returns:
        Edge-detected image (grayscale)
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, int(threshold1), int(threshold2))
    
    # Convert to 3 channels for consistency
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)


def emboss_effect(image: np.ndarray, strength: float = 1.0) -> np.ndarray:
    """
    Apply an emboss/relief effect.
    
    Args:
        image: Input image (BGR format)
        strength: Emboss strength (0.5 to 2.0)
    
    Returns:
        Embossed image
    """
    # Emboss kernel
    kernel = np.array([[-2, -1, 0],
                       [-1,  1, 1],
                       [ 0,  1, 2]]) / 4
    
    # Apply filter
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    embossed = cv2.filter2D(gray, -1, kernel)
    
    # Normalize and add offset
    embossed = embossed + 128
    embossed = np.clip(embossed * strength, 0, 255).astype(np.uint8)
    
    # Convert to 3 channels
    return cv2.cvtColor(embossed, cv2.COLOR_GRAY2BGR)


def thermal_effect(image: np.ndarray) -> np.ndarray:
    """
    Apply a thermal imaging-like effect.
    
    Args:
        image: Input image (BGR format)
    
    Returns:
        Thermal-style image
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply thermal colormap
    thermal = cv2.applyColorMap(gray, cv2.COLORMAP_HOT)
    
    return thermal


def vignette_effect(image: np.ndarray, strength: float = 0.5) -> np.ndarray:
    """
    Apply a vignette effect (darkened edges).
    
    Args:
        image: Input image (BGR format)
        strength: Vignette strength (0.0 to 1.0)
    
    Returns:
        Vignette-applied image
    """
    height, width = image.shape[:2]
    
    # Create Gaussian kernel for vignette
    kernel_x = cv2.getGaussianKernel(width, width / 2)
    kernel_y = cv2.getGaussianKernel(height, height / 2)
    kernel = kernel_y * kernel_x.T
    
    # Normalize kernel
    mask = kernel / kernel.max()
    
    # Blend strength
    mask = np.power(mask, strength)
    
    # Apply vignette to each channel
    vignette = image.copy().astype(np.float32)
    for i in range(3):
        vignette[:, :, i] = vignette[:, :, i] * mask
    
    return np.clip(vignette, 0, 255).astype(np.uint8)


def color_pop_effect(image: np.ndarray, hue_range: Tuple[int, int] = (90, 130)) -> np.ndarray:
    """
    Apply a color pop effect (desaturate all colors except specified range).
    
    Args:
        image: Input image (BGR format)
        hue_range: Range of hues to preserve (0-180)
    
    Returns:
        Color-popped image
    """
    # Convert to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    # Create mask for the hue range to preserve
    lower_hue, upper_hue = hue_range
    
    if lower_hue < upper_hue:
        mask = cv2.inRange(h, lower_hue, upper_hue)
    else:
        # Wrap around case
        mask1 = cv2.inRange(h, lower_hue, 180)
        mask2 = cv2.inRange(h, 0, upper_hue)
        mask = cv2.bitwise_or(mask1, mask2)
    
    # Desaturate masked areas
    s[mask == 0] = s[mask == 0] * 0.3
    
    # Merge and convert back
    hsv = cv2.merge([h, s, v])
    result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    return result


def grayscale_filter(image: np.ndarray) -> np.ndarray:
    """
    Convert image to grayscale.
    
    Args:
        image: Input image (BGR format)
    
    Returns:
        Grayscale image (3 channels for consistency)
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def invert_colors(image: np.ndarray) -> np.ndarray:
    """
    Invert image colors (negative effect).
    
    Args:
        image: Input image (BGR format)
    
    Returns:
        Color-inverted image
    """
    return 255 - image
