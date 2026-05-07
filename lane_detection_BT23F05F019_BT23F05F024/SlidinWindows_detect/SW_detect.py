import cv2
import numpy as np

vidcap = cv2.VideoCapture("SlidinWindows_detect\\ip.mp4")
success, image = vidcap.read()

def nothing(x):
    pass

cv2.namedWindow("Trackbars")

cv2.createTrackbar("L - H", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("L - S", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("L - V", "Trackbars", 200, 255, nothing)
cv2.createTrackbar("U - H", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("U - S", "Trackbars", 50, 255, nothing)
cv2.createTrackbar("U - V", "Trackbars", 255, 255, nothing)

def to_bgr(image):
    if len(image.shape) == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return image

def label_image(image, text):
    labeled = image.copy()
    cv2.rectangle(labeled, (0, 0), (labeled.shape[1], 32), (0, 0, 0), -1)
    cv2.putText(labeled, text, (10, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return labeled

def build_output_grid(images_with_labels, target_size=(640, 480)):
    grid_w, grid_h = target_size
    tile_w = grid_w // 3
    tile_h = grid_h // 2

    tiles = []
    for image, label in images_with_labels:
        tile = cv2.resize(to_bgr(image), (tile_w, tile_h))
        tile = label_image(tile, label)
        tiles.append(tile)

    while len(tiles) < 6:
        tiles.append(np.zeros((tile_h, tile_w, 3), dtype=np.uint8))

    top = cv2.hconcat(tiles[:3])
    bottom = cv2.hconcat(tiles[3:6])
    return cv2.vconcat([top, bottom])

while success:
    success, image = vidcap.read()
    if not success:
        break
    frame = cv2.resize(image, (640, 480))

    ## Choosing points for perspective transformation
    tl = (222, 387)
    bl = (70, 472)
    tr = (400, 380)
    br = (538, 472)

    ## Applying perspective transformation
    pts1 = np.float32([tl, bl, tr, br]) 
    pts2 = np.float32([[0, 0], [0, 480], [640, 0], [640, 480]]) 
    
    matrix = cv2.getPerspectiveTransform(pts1, pts2) 
    transformed_frame = cv2.warpPerspective(frame, matrix, (640, 480))

    ### Object Detection
    hsv_transformed_frame = cv2.cvtColor(transformed_frame, cv2.COLOR_BGR2HSV)
    
    l_h = cv2.getTrackbarPos("L - H", "Trackbars")
    l_s = cv2.getTrackbarPos("L - S", "Trackbars")
    l_v = cv2.getTrackbarPos("L - V", "Trackbars")
    u_h = cv2.getTrackbarPos("U - H", "Trackbars")
    u_s = cv2.getTrackbarPos("U - S", "Trackbars")
    u_v = cv2.getTrackbarPos("U - V", "Trackbars")
    
    lower = np.array([l_h, l_s, l_v])
    upper = np.array([u_h, u_s, u_v])
    mask = cv2.inRange(hsv_transformed_frame, lower, upper)

    # Histogram
    histogram = np.sum(mask[mask.shape[0]//2:, :], axis=0)
    midpoint = int(histogram.shape[0]/2)
    left_base = np.argmax(histogram[:midpoint])
    right_base = np.argmax(histogram[midpoint:]) + midpoint

    # Sliding Window
    y = 472
    lx = []
    rx = []
    msk = mask.copy()
    original_perpective_lane_image = np.zeros_like(frame)
    overlay = transformed_frame.copy()
    result = frame.copy()

    while y > 0:
        ## Left threshold
        img = mask[y-40:y, left_base-50:left_base+50]
        contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"]/M["m00"])
                lx.append(left_base - 50 + cx)
                left_base = left_base - 50 + cx
        
        ## Right threshold
        img = mask[y-40:y, right_base-50:right_base+50]
        contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"]/M["m00"])
                rx.append(right_base - 50 + cx)
                right_base = right_base - 50 + cx
        
        cv2.rectangle(msk, (left_base-50, y), (left_base+50, y-40), (255, 255, 255), 2)
        cv2.rectangle(msk, (right_base-50, y), (right_base+50, y-40), (255, 255, 255), 2)
        y -= 40

    # --- FINAL PARTS FROM VIDEO (Lines 119 - 147) ---
    if len(lx) > 0 and len(rx) > 0:
        # Define the quadrilateral points
        top_left = [lx[-1], 0]
        bottom_left = [lx[0], 472]
        bottom_right = [rx[0], 472]
        top_right = [rx[-1], 0]

        quad_points = np.array([top_left, bottom_left, bottom_right, top_right], dtype=np.int32)
        
        # Reshape quad_points to the required shape for fillPoly
        quad_points = quad_points.reshape((-1, 1, 2))

        # Create a copy of the transformed frame for the overlay
        overlay = transformed_frame.copy()

        # Draw the filled polygon on the transformed frame
        cv2.fillPoly(overlay, [quad_points], (0, 255, 0))

        alpha = 0.2  # Opacity factor
        cv2.addWeighted(overlay, alpha, transformed_frame, 1 - alpha, 0, transformed_frame)

        # Inverse perspective transformation to map the lanes back to the original image
        inv_matrix = cv2.getPerspectiveTransform(pts2, pts1)
        original_perpective_lane_image = cv2.warpPerspective(transformed_frame, inv_matrix, (640, 480))

        # Combine the original frame with the lane image
        result = cv2.addWeighted(frame, 1, original_perpective_lane_image, 1, 0)

    grid = build_output_grid([
        (frame, "Original"),
        (transformed_frame, "Bird's Eye View"),
        (mask, "Lane Threshold"),
        (msk, "Sliding Windows"),
        (overlay, "Highlighted Lane"),
        (result, "Final Result")
    ])

    cv2.imshow("Output", grid)

    if cv2.waitKey(10) == 27: # Esc key to exit
        break

vidcap.release()
cv2.destroyAllWindows()