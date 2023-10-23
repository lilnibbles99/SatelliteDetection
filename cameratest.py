import zwoasi as asi
#import time

cameras_found = asi.list_cameras()
camera = asi.Camera()
camera = asi._init_camera()
camera.get_camera_property()
camera.set_image_type(asi.ASI_IMG_RAW16)
camera.set_control_value(asi.ASI_EXPOSURE, 30)
camera.capture(filename="imagetest")
#save_control_values(filename="values", camera.get_control_values())
#camera.start_exposure()
#time.sleep(3)
#camera.stop_exposure()
