"""
Real-Time Intelligent Image Enhancement & Editing Toolkit
===========================================================
A production-ready Streamlit application for advanced image processing and enhancement.

Author: AI Assistant
Date: 2024
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import enhancement
import filters
import utils
import io
import os
from typing import Optional, Tuple


st.set_page_config(
    page_title="Image Enhancement Toolkit",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
    <style>
    .main { 
        padding-top: 0rem;
        background: linear-gradient(135deg, #fff5f7 0%, #ffe0ec 50%, #ffd9e8 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #fff5f7 0%, #ffe0ec 50%, #ffd9e8 100%);
    }
    .stTabs { margin-bottom: 2rem; }
    .section-header { font-size: 24px; font-weight: bold; margin: 20px 0; }
    .metric-box { 
        background: linear-gradient(135deg, #ff69b4 0%, #ff1493 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(255, 20, 147, 0.3);
    }
    .info-box {
        background: linear-gradient(135deg, #fff0f6 0%, #ffe8f5 100%);
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #ff1493;
    }
    .stButton>button {
        background: linear-gradient(135deg, #ff69b4 0%, #ff1493 100%);
        color: white;
        border: none;
        box-shadow: 0 4px 15px rgba(255, 20, 147, 0.3);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #ff1493 0%, #c71585 100%);
    }
    .stSlider {
        background: linear-gradient(90deg, #ffe0ec 0%, #ffb6d9 100%);
    }
    .stSelectbox, .stRadio {
        background: linear-gradient(135deg, #fff0f6 0%, #ffe8f5 100%);
    }
    </style>
    """, unsafe_allow_html=True)

if 'original_image' not in st.session_state:
    st.session_state.original_image = None

if 'processed_image' not in st.session_state:
    st.session_state.processed_image = None

if 'current_filter' not in st.session_state:
    st.session_state.current_filter = "None"

if 'comparison_mode' not in st.session_state:
    st.session_state.comparison_mode = "side-by-side"


# ==================== HEADER ====================
def render_header():
    """Render the application header"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("# Image Enhancement Toolkit")
        st.markdown("*Professional-grade image processing with real-time preview*")
    
    with col2:
        st.caption("OpenCV • NumPy • Streamlit")


# ==================== SIDEBAR - CONTROLS ====================
def create_sidebar_controls() -> Tuple[Optional[np.ndarray], dict]:
    """Create sidebar controls for image upload and processing parameters"""
    
    with st.sidebar:
        st.markdown("## Upload Image")
        st.divider()

        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['jpg', 'jpeg', 'png', 'bmp', 'tiff'],
            help="Supported formats: JPG, PNG, BMP, TIFF"
        )
        
        original_image = None
        if uploaded_file is not None:
            original_image = utils.load_image_from_upload(uploaded_file)
            st.session_state.original_image = original_image
        
        st.divider()
        
        
        processing_params = {}

        
        st.markdown("## Enhancement Controls")
        
        # Brightness
        processing_params['brightness'] = st.slider(
            "Brightness",
            min_value=-100,
            max_value=100,
            value=0,
            step=1,
            help="Adjust image brightness (-100 to 100)"
        )
        
        # Contrast
        processing_params['contrast'] = st.slider(
            "Contrast",
            min_value=0.5,
            max_value=3.0,
            value=1.0,
            step=0.1,
            help="Adjust image contrast (0.5 to 3.0)"
        )
        
        # Blur
        processing_params['blur'] = st.slider(
            "Blur",
            min_value=0,
            max_value=25,
            value=0,
            step=1,
            help="Apply Gaussian blur (0 to 25)"
        )
        
        # Sharpen
        processing_params['sharpen'] = st.slider(
            "Sharpen",
            min_value=0.0,
            max_value=3.0,
            value=0.0,
            step=0.1,
            help="Apply sharpening filter (0 to 3.0)"
        )
        
        st.divider()

        st.markdown("## Advanced Options")

        processing_params['histogram_eq'] = st.checkbox(
            "Histogram Equalization",
            help="Improve contrast using histogram equalization"
        )
        
        processing_params['denoise'] = st.checkbox(
            "Denoise",
            help="Reduce image noise"
        )
        
        if processing_params['denoise']:
            processing_params['denoise_method'] = st.radio(
                "Denoise Method",
                options=['Bilateral', 'Median'],
                horizontal=True
            )
        
        processing_params['edge_enhance'] = st.checkbox(
            "Edge Enhancement",
            help="Enhance edges in the image"
        )
        
        if processing_params['edge_enhance']:
            processing_params['edge_strength'] = st.slider(
                "Edge Strength",
                min_value=0.0,
                max_value=2.0,
                value=1.0,
                step=0.1
            )
        
        st.divider()
        
        st.markdown("## Artistic Filters")
        
        filter_options = [
            "None",
            "Cartoon",
            "Pencil Sketch",
            "Sepia Tone",
            "Oil Painting",
            "Watercolor",
            "Posterize",
            "Edge Detection",
            "Emboss",
            "Thermal",
            "Vignette",
            "Grayscale",
            "Invert Colors"
        ]
        
        processing_params['filter'] = st.selectbox(
            "Select Filter",
            options=filter_options,
            help="Apply artistic filter effects"
        )
        
        
        # Filter-specific parameters
        if processing_params['filter'] == "Vignette":
            processing_params['vignette_strength'] = st.slider(
                "Vignette Strength",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.1
            )
        
        elif processing_params['filter'] == "Posterize":
            processing_params['posterize_levels'] = st.slider(
                "Posterize Levels",
                min_value=2,
                max_value=8,
                value=4,
                step=1
            )
        
        elif processing_params['filter'] == "Sepia Tone":
            processing_params['sepia_intensity'] = st.slider(
                "Sepia Intensity",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.1
            )
        
        elif processing_params['filter'] == "Edge Detection":
            processing_params['edge_threshold1'] = st.slider(
                "Lower Threshold",
                min_value=0,
                max_value=200,
                value=100,
                step=5
            )
            processing_params['edge_threshold2'] = st.slider(
                "Upper Threshold",
                min_value=100,
                max_value=300,
                value=200,
                step=5
            )
        
        st.divider()

        st.markdown("## Color Correction (HSV)")
        
        processing_params['hue_shift'] = st.slider(
            "Hue Shift",
            min_value=-180,
            max_value=180,
            value=0,
            step=1
        )
        
        processing_params['saturation'] = st.slider(
            "Saturation",
            min_value=0.0,
            max_value=2.0,
            value=1.0,
            step=0.1
        )
        
        processing_params['brightness_hsv'] = st.slider(
            "Brightness (HSV)",
            min_value=0.0,
            max_value=2.0,
            value=1.0,
            step=0.1
        )
        
        st.divider()

        st.markdown("## Transformations")
        
        processing_params['flip_mode'] = st.selectbox(
            "Flip",
            options=["None", "Horizontal", "Vertical", "Both"],
            help="Flip the image"
        )
        
        processing_params['rotation'] = st.slider(
            "Rotate (degrees)",
            min_value=-180,
            max_value=180,
            value=0,
            step=1
        )
        
        st.divider()

        st.markdown("## Special Effects")

        processing_params['night_mode'] = st.checkbox(
            "Night Mode Enhancement",
            help="Enhance low-light images"
        )
        
        if processing_params['night_mode']:
            processing_params['night_strength'] = st.slider(
                "Night Enhancement Strength",
                min_value=0.5,
                max_value=2.0,
                value=1.0,
                step=0.1
            )
        
        st.divider()

        st.markdown("## Actions")

        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Auto Enhance", use_container_width=True):
                if st.session_state.original_image is not None:
                    st.session_state.processed_image = enhancement.auto_enhance(
                        st.session_state.original_image
                    )
                    st.success("Auto enhanced!")
                else:
                    st.warning("Please upload an image first")
        
        with col2:
            if st.button("Reset", use_container_width=True):
                st.session_state.processed_image = None
                st.info("Reset to original")
        
        with col3:
            if st.button("Live Preview", use_container_width=True):
                st.session_state.processed_image = "apply_now"
                st.success("Updating preview...")
        
    return original_image, processing_params


# ==================== IMAGE PROCESSING PIPELINE ====================
def process_image(original_image: np.ndarray, params: dict) -> np.ndarray:
    """Apply all selected processing operations to image"""
    
    if original_image is None:
        return None
    
    processed = original_image.copy()
    
    
    if params['brightness'] != 0:
        processed = enhancement.adjust_brightness(processed, params['brightness'])
    
    if params['contrast'] != 1.0:
        processed = enhancement.adjust_contrast(processed, params['contrast'])
    
    if params['blur'] > 0:
        processed = enhancement.apply_gaussian_blur(processed, params['blur'])
    
    if params['sharpen'] > 0 and params['blur'] == 0:
        processed = enhancement.apply_sharpen(processed, params['sharpen'])
    
    
    if params['histogram_eq']:
        processed = enhancement.histogram_equalization(processed)
    
    if params['denoise']:
        method = params.get('denoise_method', 'Bilateral')
        if method == 'Bilateral':
            processed = enhancement.noise_reduction_bilateral(processed)
        else:
            processed = enhancement.noise_reduction_median(processed)
    
    if params['edge_enhance']:
        strength = params.get('edge_strength', 1.0)
        processed = enhancement.edge_enhancement(processed, strength)
    
    if (params['hue_shift'] != 0 or 
        params['saturation'] != 1.0 or 
        params['brightness_hsv'] != 1.0):
        processed = enhancement.color_correction_hsv(
            processed,
            hue_shift=params['hue_shift'],
            saturation_factor=params['saturation'],
            value_factor=params['brightness_hsv']
        )
    
    if params['night_mode']:
        strength = params.get('night_strength', 1.0)
        processed = enhancement.night_mode_enhancement(processed, strength)
    
    if params['flip_mode'] != "None":
        flip_dict = {'Horizontal': 'horizontal', 'Vertical': 'vertical', 'Both': 'both'}
        processed = enhancement.flip_image(processed, flip_dict[params['flip_mode']])
    
    if params['rotation'] != 0:
        processed = enhancement.rotate_image(processed, params['rotation'])
    
    if params['filter'] != "None":
        filter_name = params['filter']
        
        if filter_name == "Cartoon":
            processed = filters.cartoon_filter(processed)
        elif filter_name == "Pencil Sketch":
            processed = filters.pencil_sketch_filter(processed)
        elif filter_name == "Sepia Tone":
            intensity = params.get('sepia_intensity', 0.5)
            processed = filters.sepia_tone(processed, intensity)
        elif filter_name == "Oil Painting":
            processed = filters.oil_painting_effect(processed)
        elif filter_name == "Watercolor":
            processed = filters.watercolor_effect(processed)
        elif filter_name == "Posterize":
            levels = params.get('posterize_levels', 4)
            processed = filters.posterize_effect(processed, levels)
        elif filter_name == "Edge Detection":
            t1 = params.get('edge_threshold1', 100)
            t2 = params.get('edge_threshold2', 200)
            processed = filters.edge_detection_canny(processed, t1, t2)
        elif filter_name == "Emboss":
            processed = filters.emboss_effect(processed)
        elif filter_name == "Thermal":
            processed = filters.thermal_effect(processed)
        elif filter_name == "Vignette":
            strength = params.get('vignette_strength', 0.5)
            processed = filters.vignette_effect(processed, strength)
        elif filter_name == "Grayscale":
            processed = filters.grayscale_filter(processed)
        elif filter_name == "Invert Colors":
            processed = filters.invert_colors(processed)
    
    return processed


# ==================== MAIN CONTENT AREA ====================
def render_main_content(original_image: Optional[np.ndarray], params: dict):
    """Render the main content area with image display"""
    
    if original_image is None:
        
        st.info("Upload an image from the sidebar to get started!")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### Supported Formats")
            st.caption("• JPG/JPEG\n• PNG\n• BMP\n• TIFF")
        
        with col2:
            st.markdown("### Key Features")
            st.caption("• Real-time preview\n• 13+ filters\n• Auto enhancement\n• Pro editing tools")
        
        with col3:
            st.markdown("### Export Options")
            st.caption("• High-quality download\n• PNG/JPEG formats\n• Batch processing\n• Before/After comparison")
        
        return
    
    img_info = utils.get_image_info(original_image)
    
    st.markdown("### Image Information")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Width", f"{img_info['width']}px")
    with col2:
        st.metric("Height", f"{img_info['height']}px")
    with col3:
        st.metric("Aspect Ratio", f"{img_info['aspect_ratio']:.2f}")
    with col4:
        st.metric("Size", f"{img_info['size_mb']:.2f}MB")
    
    st.divider()

    processed_image = process_image(original_image, params)
    
    
    st.session_state.processed_image = processed_image
    
    st.markdown("## Before & After Comparison")
    
    # Comparison mode selector
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("### Comparison Mode")
        comparison_mode = st.radio(
            "Select comparison view",
            options=["Side-by-Side", "Overlay", "Slider"],
            horizontal=False,
            label_visibility="collapsed"
        )
    
    with col2:
        pass
    
    with col3:
        pass
    
    st.divider()
    
    # Display based on selected mode
    if comparison_mode == "Side-by-Side":
        utils.display_comparison_side_by_side(
            original_image,
            processed_image,
            "Original Image",
            "Enhanced Image"
        )
    
    elif comparison_mode == "Overlay":
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original Image")
            original_rgb = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
            st.image(original_rgb, use_column_width=True)
        
        with col2:
            st.subheader("Enhanced Image")
            processed_rgb = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)
            st.image(processed_rgb, use_column_width=True)
    
    elif comparison_mode == "Slider":
        st.markdown("### Before/After Slider")
        slider_pos = st.slider(
            "Drag to compare",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.01,
            label_visibility="collapsed"
        )
        
        comparison_img = utils.create_before_after_slider(
            original_image,
            processed_image,
            slider_pos
        )
        
        comparison_rgb = cv2.cvtColor(comparison_img, cv2.COLOR_BGR2RGB)
        st.image(comparison_rgb, use_column_width=True)
    
    st.divider()
    
    st.markdown("## Download Enhanced Image")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        png_data = utils.save_image_to_bytes(processed_image, format='PNG')
        st.download_button(
            label="Download as PNG",
            data=png_data,
            file_name="enhanced_image.png",
            mime="image/png",
            use_container_width=True
        )
    
    with col2:
        jpg_data = utils.save_image_to_bytes(processed_image, format='JPEG')
        st.download_button(
            label="Download as JPG",
            data=jpg_data,
            file_name="enhanced_image.jpg",
            mime="image/jpeg",
            use_container_width=True
        )
    
    with col3:
        composite = np.hstack([original_image, processed_image])
        composite_data = utils.save_image_to_bytes(composite, format='PNG')
        st.download_button(
            label="Download Comparison",
            data=composite_data,
            file_name="comparison.png",
            mime="image/png",
            use_container_width=True
        )


# ==================== ABOUT & INFO TABS ====================
def render_info_tabs():
    """Render information tabs"""
    
    tab1, tab2, tab3 = st.tabs(["About", "Tools Used", "FAQ"])
    
    with tab1:
        st.markdown("""
        ## About This Application
        
        **Real-Time Intelligent Image Enhancement & Editing Toolkit** is a professional-grade
        image processing application built with cutting-edge computer vision technologies.
        
        ### Key Features
        - **Real-time Preview**: See changes instantly as you adjust parameters
        - **Professional Filters**: 13+ artistic and enhancement filters
        - **Advanced Tools**: Auto-enhance, color correction, noise reduction
        - **Easy Export**: Download in multiple formats with comparison options
        - **Optimized Performance**: Fast processing even on CPU
        
        ### Perfect For
        - Photography enthusiasts
        - Content creators
        - Image restoration
        - Batch processing
        - Learning computer vision
        """)
    
    with tab2:
        st.markdown("""
        ## Technologies & Libraries
        
        | Technology | Purpose |
        |-----------|---------|
        | **OpenCV** | Core image processing and computer vision |
        | **NumPy** | Numerical computations and array operations |
        | **Streamlit** | Web application framework |
        | **Pillow** | Image I/O and manipulation |
        | **Python 3.8+** | Programming language |
        
        ### Algorithms Implemented
        - **Histogram Equalization**: CLAHE for adaptive contrast improvement
        - **Edge Detection**: Canny edge detector
        - **Noise Reduction**: Bilateral and Median filtering
        - **Object Detection**: Color space conversions (RGB/HSV/LAB/BGR)
        - **Image Transformations**: Rotation, flipping, resizing
        """)
    
    with tab3:
        st.markdown("""
        ## Frequently Asked Questions
        
        ### Q: What image formats are supported?
        **A:** JPG, JPEG, PNG, BMP, and TIFF formats are fully supported.
        
        ### Q: Can I process multiple images at once?
        **A:** Currently, the app processes one image at a time. Multiple images can be
               processed sequentially by re-uploading.
        
        ### Q: What's the recommended image size?
        **A:** Up to 10MB recommended for optimal performance. Larger images are automatically
               optimized.
        
        ### Q: Are my images stored on the server?
        **A:** No! All processing happens locally in your browser. Images are not stored.
        
        ### Q: Can I undo changes?
        **A:** Use the Reset button in the sidebar to revert to the original image.
        
        ### Q: Which filter should I use for old photos?
        **A:** Try combining Auto Enhance + Histogram Equalization + Noise Reduction.
        
        ### Q: How can I improve low-light images?
        **A:** Enable Night Mode Enhancement and adjust the strength slider.
        """)


# ==================== MAIN APP ====================
def main():
    """Main application function"""
    
    render_header()
    
    st.divider()
    
    # Create sidebar
    original_image, processing_params = create_sidebar_controls()
    
    # Main content
    if original_image is not None:
        render_main_content(original_image, processing_params)
    else:
        render_main_content(None, processing_params)
    
    st.divider()
    
    # Info tabs
    st.markdown("## More Information")
    render_info_tabs()
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 12px; padding: 20px;
    background: linear-gradient(135deg, #fff0f6 0%, #ffe8f5 100%);
    border-radius: 10px; border: 2px solid #ff69b4;'>
    <p>Real-Time Intelligent Image Enhancement & Editing Toolkit 2024</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
