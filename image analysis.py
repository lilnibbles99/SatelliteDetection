import matplotlib as plt
import cv2
import numpy as np

image = cv2.imread('C:/Users/thegr/Desktop/WORK/year 3/python data/star.jpg')

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
(threshold, im_bw) = cv2.threshold(gray, 150, 255, cv2.THRESH_TOZERO)


#edges = cv2.Canny(im_bw,50,150)

maxgap = 20
minlength = 50
blank = np.copy(im_bw)

lines = cv2.HoughLinesP(im_bw,1,(np.pi/180),15,np.array([]),minlength,maxgap)
print(lines)
for line in lines:
    for x1,x2,y1,y2 in line:
        cv2.line(blank,(x1,y1),(x2,y2),(255,0,0),3)



print(lines)
cv2.imshow("lines",blank)
cv2.imshow("bw",im_bw)

cv2.waitKey(0)
