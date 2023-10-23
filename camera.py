import cv2

exposure_time = 10000 #in ms

camera = cv2.VideoCapture(1)
print(camera.isOpened())
camera.set(cv2.CAP_PROP_EXPOSURE, exposure_time)
print(camera.get(cv2.CAP_PROP_EXPOSURE))
stat, image = camera.read()
if stat == True:
    cv2.imshow("image",image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
