# Shape Detection Using OpenCV Contours + approxPolyDP

## Project Overview

This project detects and classifies basic geometric shapes from an input image using OpenCV and Python.

The system identifies the following shapes:

- Triangle
- Square
- Rectangle
- Pentagon
- Hexagon
- Circle
- Oval

It uses contour detection and polygon approximation to determine the number of sides and shape properties.

---

## Objective

To build a simple computer vision application that can detect shapes from images using image processing techniques.

---

## Technologies Used

- Python 3.12.0
- OpenCV
- NumPy
- Math Library

---

## Project Structure

```text
Shape-Detection-Project/
│── shape_detection.py
│── README.md
│── input_images/
│   ├── circle.png
│   ├── hexagon.png
│   ├── mix.png
│   ├── oval.png
│   ├── pentagon.png
│   ├── rectangle.png
│   └── square.png
│
│── output_images/
│   ├── circle_output.png
│   ├── hexagon_output.png
│   ├── mix_output_1.png
│   ├── mix_output_2.png
│   ├── oval_output.png
│   ├── pentagon_output.png
│   ├── rectangle_output.png
│   └── square_output.png
````

---

## Installation

Install required libraries:

```bash
pip install opencv-python numpy
```

---

## How to Run

1. Place your image inside the `input_images` folder.

2. Update image path inside code:

```python
image = cv2.imread("input_images/square.png")
```

3. Run the program:

```bash
python shape_detection.py
```

---

## Working Process

### 1. Load Image

Reads input image using OpenCV.

### 2. Preprocessing

* Convert to grayscale
* Apply Gaussian Blur
* Perform Canny Edge Detection
* Morphological operations

### 3. Contour Detection

Finds external contours from image.

### 4. Shape Classification

Based on contour vertices:

* 3 Vertices = Triangle
* 4 Vertices = Square / Rectangle
* 5 Vertices = Pentagon
* 6 Vertices = Hexagon
* More Vertices = Circle / Oval

### 5. Output

Contours are drawn and shape name is displayed.

---

## Sample Output

**Input Image:**
`input_images/square.png`

**Detected Output:**

* Shape boundary in Green
* Shape label in Blue

![Detected Output](output_images/square_output.png)

---

## Applications

* Object Recognition
* Industrial Shape Inspection
* Educational Projects
* Basic Computer Vision Tasks

---

## Future Improvements

* Real-time webcam detection
* Rotated rectangle detection
* Multiple object tracking
* Color + shape recognition

---

## Authors

* **BT23F05F028** – Vednarayan Hiralkar
* **BT23F05F060** – Aryan Shastri

Project developed for academic mini project submission.

---

## License

This project is submitted for teacher's assessment under the subject **Honors - Advanced Computer Vision**.

```