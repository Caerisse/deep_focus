# import sys
# from PyQt5.QtGui import QPainter, QPen
# from PyQt5.QtWidgets import QMainWindow, QApplication
# from PyQt5.QtCore import Qt
import sys
from threading import Thread

import cv2
import pyautogui
from PyQt5.QtWidgets import QApplication

from gaze_tracking import GazeTracking
from .calibration import Calibration
from .annotated_frame import  AnnotatedFrame
from .mouse_control import MouseControl

def main():
    # Initialize webcam
    webcam = cv2.VideoCapture(0)

    # Start GazeTracking
    gaze = GazeTracking()
    thread_gaze = Thread(target=gaze.run, args=(webcam,))
    thread_gaze.name = "ThreadGaze"
    #thread_gaze.daemon = True
    thread_gaze.start()

    # Calibrate
    size = pyautogui.size()
    # changed manually to test only in my primary monitor
    size = (1920, 1080)
    calibration = Calibration(gaze, size)

    # Show annotated camera
    annotated_frame = AnnotatedFrame(gaze)
    thread_annotated = Thread(target=annotated_frame.show)
    thread_annotated.name = "ThreadAnnotated"
    #thread_annotated.daemon = True
    thread_annotated.start()

    # Initialize mouse control
    mouse_control = MouseControl(gaze, calibration)
    mouse_control.run()




if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass



    # Start Screen Overlay
    # app = QApplication(sys.argv)
    # overlay = Overlay()
    # overlay.show()
    # app.exec_()

