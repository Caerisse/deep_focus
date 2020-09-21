"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.
"""

import cv2
from gaze_tracking import GazeTracking

class AnnotatedFrame:
    def __init__(self, gaze: GazeTracking):
        self.gaze = gaze

    def show(self):
        while True:
            try:
                frame = self.gaze.annotated_frame()
            except AttributeError:
                continue

            text = ""

            if self.gaze.is_blinking():
                text = "Blinking"
            elif self.gaze.is_right():
                text = "Looking right"
            elif self.gaze.is_left():
                text = "Looking left"
            elif self.gaze.is_center():
                text = "Looking center"

            cv2.putText(frame, text, (10, 50), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

            left_pupil = self.gaze.eye_left.pupil_center
            right_pupil = self.gaze.eye_right.pupil_center
            cv2.putText(frame, "Left pupil:  " + str(left_pupil), (10, 80), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
            cv2.putText(frame, "Right pupil: " + str(right_pupil), (10, 115), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

            cv2.imshow("Annotated", frame)

            if cv2.waitKey(1) == 27:
                break