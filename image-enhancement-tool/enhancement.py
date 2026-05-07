"""
Core Image Enhancement Functions
==================================
This module contains fundamental image processing operations using OpenCV.
All functions take a numpy array (OpenCV format) and return enhanced images.
"""

import cv2
import numpy as np
from typing import Tuple, Optional


def adjust_brightness(image: np.ndarray, value: float) -> np.ndarray:
    """
    Adjust image brightness.
    
    Args:
        image: Input image (BGR format)
        value: Brightness adjustment (-100 to 100)
               Negative values darken, positive values brighten
    
    Returns:
        Brightness-adjusted image
    """
    brightness_value = int((value / 100) * 50)
    if brightness_value >= 0:
        image_bright = cv2.convertScaleAbs(image, alpha=1, beta=brightness_value)
    else:
        image_bright = cv2.convertScaleAbs(image, alpha=1, beta=brightness_value)
    
    return np.clip(image_bright, 0, 255).astype(np.uint8)


def adjust_contrast(image: np.ndarray, factor: float) -> np.ndarray:
    """
    Adjust image contrast.
    
    Args:
        image: Input image (BGR format)
        factor: Contrast factor (0.5 to 3.0)
                1.0 = original, < 1.0 = decrease contrast, > 1.0 = increase contrast
    
    Returns:
        Contrast-adjusted image
    """
    image_float = image.astype(np.float32) / 255.0
    image_contrast = (image_float - 0.5) * factor + 0.5
    image_contrast = np.clip(image_contrast, 0, 1) * 255
    
    return image_contrast.astype(np.uint8)


def apply_gaussian_blur(image: np.ndarray, kernel_size: int) -> np.ndarray:
    """
    Apply Gaussian blur to the image.
    
    Args:
        image: Input image (BGR format)
        kernel_size: Blur kernel size (must be odd number, 1 to 51)
    
    Returns:
        Blurred image
    """
    kernel_size = int(kernel_size * 2) + 1
    kernel_size = min(kernel_size, 51)  # Maximum reasonable kernel size
    
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)


def apply_sharpen(image: np.ndarray, intensity: float = 1.0) -> np.ndarray:
    """
    Apply unsharp masking for sharpness enhancement.
    
    Args:
        image: Input image (BGR format)
        intensity: Sharpening intensity (0.0 to 3.0)
    
    Returns:
        Sharpened image
    """
    blurred = cv2.GaussianBlur(image, (0, 0), 1.0)
    image_float = image.astype(np.float32)
    blurred_float = blurred.astype(np.float32)
    
    sharpened = image_float + (image_float - blurred_float) * intensity
    sharpened = np.clip(sharpened, 0, 255)
    
    return sharpened.astype(np.uint8)


def histogram_equalization(image: np.ndarray) -> np.ndarray:
    """
    Apply histogram equalization to improve contrast.
    Uses CLAHE (Contrast Limited Adaptive Histogram Equalization) for better results.
    
    Args:
        image: Input image (BGR format)
    
    Returns:
        Histogram-equalized image
    """
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge([l, a, b])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def noise_reduction_bilateral(image: np.ndarray, diameter: int = 9, 
                               sigma_color: float = 75.0, sigma_space: float = 75.0) -> np.ndarray:
    """
    Reduce noise using bilateral filtering (preserves edges).
    
    Args:
        image: Input image (BGR format)
        diameter: Diameter of pixel neighborhood
        sigma_color: Filter sigma in the color space
        sigma_space: Filter sigma in the coordinate space
    
    Returns:
        Denoised image
    """
    return cv2.bilateralFilter(image, diameter, sigma_color, sigma_space)


def noise_reduction_median(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """
    Reduce noise using median filtering (very effective for salt-and-pepper noise).
    
    Args:
        image: Input image (BGR format)
        kernel_size: Size of the kernel (must be odd)
    
    Returns:
        Denoised image
    """
    kernel_size = int(kernel_size) if kernel_size % 2 == 1 else int(kernel_size) + 1
    
    return cv2.medianBlur(image, kernel_size)


def edge_enhancement(image: np.ndarray, strength: float = 1.0) -> np.ndarray:
    """
    Enhance edges in the image using Laplacian filter.
    
    Args:
        image: Input image (BGR format)
        strength: Edge enhancement strength (0.0 to 2.0)
    
    Returns:
        Edge-enhanced image
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Laplacian filter
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    
    # Normalize laplacian
    laplacian = np.uint8(np.absolute(laplacian))
    
    # Convert back to 3 channels
    laplacian_3ch = cv2.cvtColor(laplacian, cv2.COLOR_GRAY2BGR)
    
    # Blend with original image
    image_float = image.astype(np.float32)
    laplacian_float = laplacian_3ch.astype(np.float32)
    
    result = image_float + laplacian_float * strength * 0.5
    result = np.clip(result, 0, 255)
    
    return result.astype(np.uint8)


def auto_enhance(image: np.ndarray) -> np.ndarray:
    """
    Automatically enhance image with optimized brightness, contrast, and sharpness.
    One-click enhancement for improved image quality.
    
    Args:
        image: Input image (BGR format)
    
    Returns:
        Auto-enhanced image
    """
    enhanced = histogram_equalization(image)
    
    # Step 2: Slight sharpening
    enhanced = apply_sharpen(enhanced, intensity=0.8)
    
    # Step 3: Auto-adjust brightness if needed
    # Calculate average brightness
    gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
    avg_brightness = np.mean(gray)
    
    # Adjust brightness based on calculated average
    if avg_brightness < 80:
        enhanced = adjust_brightness(enhanced, 30)
    elif avg_brightness > 200:
        enhanced = adjust_brightness(enhanced, -20)
    
    return enhanced


def color_correction_hsv(image: np.ndarray, hue_shift: int = 0, 
                         saturation_factor: float = 1.0, 
                         value_factor: float = 1.0) -> np.ndarray:
    """
    Perform color correction using HSV color space adjustments.
    
    Args:
        image: Input image (BGR format)
        hue_shift: Hue shift value (-180 to 180)
        saturation_factor: Saturation multiplier (0.0 to 2.0)
        value_factor: Value/brightness multiplier (0.0 to 2.0)
    
    Returns:
        Color-corrected image
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
    
    # Extract channels
    h, s, v = cv2.split(hsv)
    
    # Apply adjustments
    h = (h + hue_shift) % 180  # Hue range is 0-180 in OpenCV
    s = np.clip(s * saturation_factor, 0, 255)
    v = np.clip(v * value_factor, 0, 255)
    
    # Merge channels
    hsv = cv2.merge([h, s, v]).astype(np.uint8)
    
    # Convert back to BGR
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def night_mode_enhancement(image: np.ndarray, strength: float = 1.0) -> np.ndarray:
    """
    Enhance low-light/night mode images.
    Uses contrast stretching and adaptive histogram equalization.
    
    Args:
        image: Input image (BGR format)
        strength: Enhancement strength (0.5 to 2.0)
    
    Returns:
        Night-mode enhanced image
    """
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # More aggressive CLAHE for night mode
    clahe = cv2.createCLAHE(clipLimit=4.0 * strength, tileGridSize=(8, 8))
    l = clahe.apply(l)
    
    lab = cv2.merge([l, a, b])
    result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    # Slight contrast boost
    result = adjust_contrast(result, 1.2 * strength)
    
    return result


def flip_image(image: np.ndarray, direction: str = 'horizontal') -> np.ndarray:
    """
    Flip image horizontally or vertically.
    
    Args:
        image: Input image (BGR format)
        direction: 'horizontal', 'vertical', or 'both'
    
    Returns:
        Flipped image
    """
    if direction.lower() == 'horizontal':
        return cv2.flip(image, 1)
    elif direction.lower() == 'vertical':
        return cv2.flip(image, 0)
    elif direction.lower() == 'both':
        return cv2.flip(image, -1)
    else:
        return image


def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    """
    Rotate image by specified angle (in degrees).
    
    Args:
        image: Input image (BGR format)
        angle: Rotation angle in degrees (positive = counter-clockwise)
    
    Returns:
        Rotated image
    """
    height, width = image.shape[:2]
    center = (width / 2, height / 2)
    
    # Get rotation matrix
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # Apply rotation
    rotated = cv2.warpAffine(image, rotation_matrix, (width, height),
                             borderMode=cv2.BORDER_REFLECT)
    
    return rotated


def get_image_statistics(image: np.ndarray) -> dict:
    """
    Calculate and return image statistics.
    
    Args:
        image: Input image (BGR format)
    
    Returns:
        Dictionary containing image statistics
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    return {
        'mean_brightness': np.mean(gray),
        'std_deviation': np.std(gray),
        'min_value': np.min(gray),
        'max_value': np.max(gray),
    }
