# ==========================================================
# SHAPE DETECTION USING CONTOURS + approxPolyDP
# Detects:
# Triangle, Square, Rectangle,
# Pentagon, Hexagon, Circle, Oval
# ==========================================================

import cv2
import numpy as np
import math

# ----------------------------------------------------------
# LOAD IMAGE
# ----------------------------------------------------------
image = cv2.imread("input_images/square.png")

if image is None:
    print("Image not found")
    exit()

output = image.copy()

# ----------------------------------------------------------
# PREPROCESSING
# ----------------------------------------------------------
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

blur = cv2.GaussianBlur(gray, (5, 5), 0)

# Canny edge detection
edges = cv2.Canny(blur, 50, 150)

# Morphology close gaps
kernel = np.ones((3, 3), np.uint8)
edges = cv2.dilate(edges, kernel, iterations=1)
edges = cv2.erode(edges, kernel, iterations=1)

# ----------------------------------------------------------
# FIND CONTOURS
# ----------------------------------------------------------
contours, _ = cv2.findContours(
    edges,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)

# ----------------------------------------------------------
# DETECTION LOOP
# ----------------------------------------------------------
for cnt in contours:

    area = cv2.contourArea(cnt)

    if area < 1200:
        continue

    perimeter = cv2.arcLength(cnt, True)

    # Douglas-Peucker polygon approximation
    approx = cv2.approxPolyDP(cnt, 0.02 * perimeter, True)

    vertices = len(approx)

    x, y, w, h = cv2.boundingRect(approx)

    shape = "Unknown"

    # ------------------------------------------------------
    # TRIANGLE
    # ------------------------------------------------------
    if vertices == 3:
        shape = "Triangle"

    # ------------------------------------------------------
    # QUADRILATERAL
    # ------------------------------------------------------
    elif vertices == 4:

        ratio = w / float(h)

        if 0.95 <= ratio <= 1.05:
            shape = "Square"
        else:
            shape = "Rectangle"

    # ------------------------------------------------------
    # PENTAGON
    # ------------------------------------------------------
    elif vertices == 5:
        shape = "Pentagon"

    # ------------------------------------------------------
    # HEXAGON
    # ------------------------------------------------------
    elif vertices == 6:
        shape = "Hexagon"

    # ------------------------------------------------------
    # CIRCLE / OVAL
    # ------------------------------------------------------
    else:

        circularity = (4 * math.pi * area) / (perimeter * perimeter)

        ratio = w / float(h)

        if circularity > 0.82 and 0.90 <= ratio <= 1.10:
            shape = "Circle"
        else:
            shape = "Oval"

    # ------------------------------------------------------
    # DRAW CONTOUR
    # ------------------------------------------------------
    cv2.drawContours(output, [approx], -1, (0, 255, 0), 3)

    # ------------------------------------------------------
    # LABEL
    # ------------------------------------------------------
    # ------------------------------------------------------
# LABEL
# ------------------------------------------------------
font = cv2.FONT_HERSHEY_SIMPLEX
scale = 0.7
thickness = 2
gap = 8

(text_w, text_h), baseline = cv2.getTextSize(
    shape, font, scale, thickness
)

img_h, img_w = output.shape[:2]

# Center horizontally
tx = x + (w - text_w) // 2
tx = max(5, min(tx, img_w - text_w - 5))

# Try above shape first
ty = y - gap

# If top cut -> try below
if ty - text_h < 5:
    ty = y + h + text_h + gap

# If bottom cut -> place safely inside image
if ty + baseline > img_h - 5:
    ty = img_h - 10

cv2.putText(
    output,
    shape,
    (tx, ty),
    font,
    scale,
    (255, 0, 0),
    thickness
)

# ----------------------------------------------------------
# DISPLAY
# ----------------------------------------------------------
cv2.imshow("Edges", edges)
cv2.imshow("Detected Shapes", output)

cv2.waitKey(0)
cv2.destroyAllWindows()