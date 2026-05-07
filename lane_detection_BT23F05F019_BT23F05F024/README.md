# 🚗 Lane Detection System using OpenCV (Python)

## 📌 Overview

This project implements a **real-time lane detection system** using classical computer vision techniques in Python with OpenCV. It demonstrates two different approaches:

* **Hough Transform-based Lane Detection** (for straight lanes)
* **Sliding Window-based Lane Detection** (for curved lanes)

Both methods process video input and overlay detected lanes onto the original frames.

---

## 🎯 Objectives

* Detect lane markings from road videos
* Compare two classical computer vision approaches
* Visualize lane detection results in real-time
* Understand perspective transformation and feature extraction

---

## 🧠 Methodologies

### 1️⃣ Hough Transform Lane Detection

This method is ideal for detecting **straight lane lines** using edge detection and line transformation.

#### 🔹 Steps:

1. Convert frame to grayscale
2. Apply Gaussian Blur
3. Perform Canny Edge Detection
4. Define Region of Interest (ROI)
5. Apply Hough Line Transform
6. Draw lane lines on original frame

#### 🔹 Input Video:

```bash
test2.mp4
```

---

### 2️⃣ Sliding Window Lane Detection

This method detects **curved lanes** using a top-down (bird’s-eye) transformation and polynomial fitting.

#### 🔹 Steps:

1. Apply Perspective Transform
2. Convert to HSV and apply thresholding
3. Compute histogram to find lane bases
4. Apply Sliding Window search
5. Extract lane pixels
6. Fit polynomial curves
7. Draw lane area
8. Warp back to original frame

#### 🔹 Input Video:

```bash
ip.mp4
```

---

## ⚙️ Technologies Used

* Python 3.x
* OpenCV (`cv2`)
* NumPy

---

## 📂 Project Structure

```bash
honors_acv/
│
├── HoughLines_detect/
│   ├── Houghdetect.py
│   └── test2.mp4
│
├── SlidinWindows_detect/
│   ├── SW_detect.py
│   └── ip.mp4
│
├── README.md
```

---

## ▶️ How to Run

### 🔹 Install Dependencies

```bash
python -m pip install opencv-python numpy
```

### 🔹 Run Hough Transform Detection

```bash
python HoughLines_detect/Houghdetect.py
```

### 🔹 Run Sliding Window Detection

```bash
python SlidinWindows_detect/SW_detect.py
```

### Notes

- Run the commands from the repository root (the folder that contains README.md).
- Press Esc to close the output window.

---

## 📊 Output

* Detected lane lines using Hough Transform
* Highlighted lane region using Sliding Window method
* Real-time video output windows

---

## 🔍 Comparison of Methods

| Feature               | Hough Transform | Sliding Window |
| --------------------- | --------------- | -------------- |
| Lane Type             | Straight        | Curved         |
| Accuracy              | Moderate        | High           |
| Complexity            | Low             | High           |
| Real-time Performance | Fast            | Moderate       |
| Robustness            | Lower           | Higher         |

---

## ⚠️ Limitations

* Sensitive to lighting conditions
* Performance decreases in shadows, rain, or night
* Requires manual tuning (HSV values, ROI points)
* No deep learning integration

---

## 🚀 Future Improvements

* Lane curvature and vehicle offset calculation
* Deep learning-based lane detection (CNNs)
* Improved robustness for real-world conditions
* Performance optimization for real-time systems

---

## 📸 Sample Results

<img width="1518" height="952" alt="image" src="https://github.com/user-attachments/assets/97edbd79-3cc2-4398-a607-5ecd67fe403d" />
<img width="1919" height="994" alt="Screenshot 2026-05-06 133859" src="https://github.com/user-attachments/assets/02cc6276-c3c2-4276-9f8f-972579af0987" />


---

## 👨‍💻 Authors

* Aditya Ghodki
* Ayan Farooque

---

## 📜 License

This project is for educational purposes only.
