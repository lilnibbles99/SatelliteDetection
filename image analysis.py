
import cv2
import numpy as np

image = cv2.imread('star.jpg')

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

threshold_value = 200
ret, binary_image = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)

contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

bright_spot_coordinates = []

for contour in contours:
    # Calculate the moments of the contour to find its centroid
    M = cv2.moments(contour)

    if M["m00"] != 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        bright_spot_coordinates.append((cX, cY))
        
for coord in bright_spot_coordinates:
    cv2.circle(image, coord, 5, (0, 0, 255), -1)  # Draw a red circle at the coordinates

cv2.imshow('Bright Spots', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
