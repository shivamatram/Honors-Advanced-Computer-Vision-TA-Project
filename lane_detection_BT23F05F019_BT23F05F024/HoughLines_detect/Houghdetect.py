import cv2
import numpy as np

prev_left_fit_average = None
prev_right_fit_average = None

def canny(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    canny = cv2.Canny(blur, 50, 150)
    return canny

def region_of_interest(image):
    height = image.shape[0]
    width = image.shape[1]

    polygons = np.array([[
        (int(0.1 * width), height),
        (int(0.9 * width), height),
        (int(0.5 * width), int(0.4 * height))
    ]])

    mask = np.zeros_like(image)
    cv2.fillPoly(mask, polygons, 255)
    masked_image = cv2.bitwise_and(image, mask)
    return masked_image

def make_coordinates(image, line_parameters):
    slope, intercept = line_parameters

    if slope == 0:
        slope = 0.1  

    y1 = image.shape[0]
    y2 = int(y1 * (3/5))

    x1 = int((y1 - intercept) / slope)
    x2 = int((y2 - intercept) / slope)

    return np.array([x1, y1, x2, y2])

def average_slope_intercept(image, lines):
    global prev_left_fit_average, prev_right_fit_average

    left_fit = []
    right_fit = []

    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)

        parameters = np.polyfit((x1, x2), (y1, y2), 1)
        slope = parameters[0]
        intercept = parameters[1]

        if slope < 0:
            left_fit.append((slope, intercept))
        else:
            right_fit.append((slope, intercept))

    left_line, right_line = None, None

    # LEFT lane
    if len(left_fit) > 0:
        left_fit_average = np.average(left_fit, axis=0)
        prev_left_fit_average = left_fit_average
    else:
        left_fit_average = prev_left_fit_average

    # RIGHT lane
    if len(right_fit) > 0:
        right_fit_average = np.average(right_fit, axis=0)
        prev_right_fit_average = right_fit_average
    else:
        right_fit_average = prev_right_fit_average

    
    if left_fit_average is not None:
        left_line = make_coordinates(image, left_fit_average)

    if right_fit_average is not None:
        right_line = make_coordinates(image, right_fit_average)

    lines_output = []
    if left_line is not None:
        lines_output.append(left_line)
    if right_line is not None:
        lines_output.append(right_line)

    return np.array(lines_output)

def display_lines(image, lines):
    line_image = np.zeros_like(image)

    if lines is not None:
        for x1, y1, x2, y2 in lines:
            cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 100), 12)

    return line_image

def to_bgr(image):
    if len(image.shape) == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return image

def label_image(image, text):
    labeled = image.copy()
    cv2.rectangle(labeled, (0, 0), (labeled.shape[1], 32), (0, 0, 0), -1)
    cv2.putText(labeled, text, (10, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return labeled

def build_output_grid(combo_image, frame, canny_image, cropped_image):
    tile_h = frame.shape[0] // 2
    tile_w = frame.shape[1] // 2

    combo_tile = label_image(cv2.resize(to_bgr(combo_image), (tile_w, tile_h)), "Result")
    canny_tile = label_image(cv2.resize(to_bgr(canny_image), (tile_w, tile_h)), "Canny")
    roi_tile = label_image(cv2.resize(to_bgr(cropped_image), (tile_w, tile_h)), "ROI")
    frame_tile = label_image(cv2.resize(to_bgr(frame), (tile_w, tile_h)), "Original")

    top = cv2.hconcat([combo_tile, canny_tile])
    bottom = cv2.hconcat([roi_tile, frame_tile])

    grid = cv2.vconcat([top, bottom])
    return grid

cap = cv2.VideoCapture("HoughLines_detect/test2.mp4")

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("End of video or cannot read frame.")
        break

    canny_image = canny(frame)
    cropped_image = region_of_interest(canny_image)

    lines = cv2.HoughLinesP(
        cropped_image,
        2,
        np.pi / 180,
        100,
        np.array([]),
        minLineLength=40,
        maxLineGap=5
    )

    if lines is not None:
        averaged_lines = average_slope_intercept(frame, lines)
        line_image = display_lines(frame, averaged_lines)
    else:
        line_image = np.zeros_like(frame)

    combo_image = cv2.addWeighted(frame, 0.9, line_image, 1, 1)

    grid = build_output_grid(combo_image, frame, canny_image, cropped_image)
    cv2.imshow('Output', grid)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC key
        break

cap.release()
cv2.destroyAllWindows()