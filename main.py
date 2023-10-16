####Importing everything we need

import fitparse
import cv2
import numpy as np
from skimage.feature import blob_log

####Edit these ones

threshold1 = 150 #150
threshold2 = 100 #100
minlinelength = 150 #150
maxlinegap = 5  #5
threshold3 = 0.1 #0.1

####Creating arrays early and opening the image file

coords = []
lines_list = []
x_coords = np.array([])
y_coords = np.array([])
FIT_image = fitparse.FitFile("C:/Users/thegr/Desktop/WORK/year 3/python data/SATELLITES/2023-01-13-1830_7-CapObj_0026.FIT")
for name in fit_file.get_messages("record"):
    for data in name:
        if data.name == "timestamp":
            time.append(data.value)
        elif data.name == "":
        elif data.name == "":
print(FIT_image)
image = np.array(data)

#image = cv2.imread('C:/Users/thegr/Desktop/WORK/year 3/python data/SATELLITE/2023-01-13-1835_4-CapObj_0048.FIT')

print(type(image))
cv2.imshow("image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

####Processing the image to make it grayscale and only caring about the boundaries of the shapes

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
threshold, im_bw = cv2.threshold(gray, threshold1, 255, cv2.THRESH_TOZERO)
edges = cv2.Canny(im_bw,50,150, apertureSize = 3)
new_image = im_bw
cv2.imshow("gray",gray)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imshow("edges",edges)
cv2.waitKey(0)
cv2.destroyAllWindows()

####Finding any lines within the image and storing the start and end coordinates of each

lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=threshold2, minLineLength=minlinelength, maxLineGap=maxlinegap)
line_image = cv2.cvtColor(new_image, cv2.COLOR_GRAY2RGB)
for points in lines:
    x1, y1, x2, y2 = points[0]
    line_image = cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
    new_image = cv2.line(im_bw, (x1, y1), (x2, y2), (0, 0, 0), 2)
    lines_list.append([(x1, y1), (x2, y2)])
cv2.imshow("new image",line_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

####Finding the coordinates of all the stars in the image and adding them to a list and grouping any coordinates or lines that are likely to be the same object

blobs = blob_log(new_image, max_sigma=30, threshold=threshold3)
color_image = cv2.cvtColor(new_image, cv2.COLOR_GRAY2RGB)
for blob in blobs:
    y, x, size = blob
    coords.append([x,y])
    center = (int(x), int(y))
    radius = int(size / 2)
    cv2.circle(color_image, center, radius, (150, 150, 255), 5)
cv2.imshow("stars",color_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

########### This is old code I am keeping while I bugfix the code above
#for rows in range(new_image.shape[0]):
#    for columns in range(new_image.shape[1]):
#        if new_image[rows][columns] != 0:
#            x_coords = np.concatenate((x_coords, np.array([columns])))
#            y_coords = np.concatenate((y_coords, np.array([rows])))
#x_coords = x_coords.reshape(-1, 1)
#y_coords = y_coords.reshape(-1, 1)
#coords = np.hstack((y_coords, x_coords))

####Comparing the star map to the image in question and finding the transformation

#https://gea.esac.esa.int/archive/
#https://cdsarc.cds.unistra.fr/viz-bin/cat/J/A+A/650/A201#/article

####Getting the corrected equation for the line

####Converting to orbital characteristics using time

####Pulling any other characteristics from the image

####Naming the object and pushing it to the external database

####The final output of the program

print("list of lines ", lines_list)
print("list of star coordinates ", coords)
cv2.waitKey(0)
cv2.destroyAllWindows()