import math
import time

import pyautogui

from gaze_tracking import GazeTracking

from .gaze import Gaze
from .calibration import Calibration


class MouseControl:
    def __init__(self, gaze: GazeTracking, calibration: Calibration):
        self.gaze_tracking = gaze
        self.last_gaze = Gaze(self.gaze_tracking)
        self.current_gaze = Gaze(self.gaze_tracking)
        self.calibration = calibration
        self.old_pos = [int(self.calibration.size[0]/2), int(self.calibration.size[1]/2)]
        self.new_pos = self.old_pos

    def run(self, sleep = 0.05, sensibility_x = 30, sensibility_y = 50, threshold = 50):
        self.reset_position()
        self.last_gaze = Gaze(self.gaze_tracking)
        no_gaze_count = 0
        blinking_count = 0
        while True:
            time.sleep(sleep)
            # print("old_pos: {}".format(old_pos))
            self.current_gaze = Gaze(self.gaze_tracking)
            current_pos = pyautogui.position()
            # print("current_pos: {}".format(current_pos))
            try:
                # Sleep if moved moved by user
                if current_pos.x != self.old_pos[0] or current_pos.y != self.old_pos[1]:
                    print("Mouse moved dy user, sleeping 3 second")
                    time.sleep(3)
                    self.new_pos = [current_pos.x, current_pos.y]
                    continue

                # Skip if gaze not detected
                if not self.current_gaze or not self.last_gaze:
                    no_gaze_count += 1
                    if no_gaze_count >= 5:
                        no_gaze_count = 0
                        self.reset_position()
                    continue
                no_gaze_count = 0

                # Check if user is blinking
                if self.gaze_tracking.is_blinking():
                    blinking_count += 1
                    if blinking_count >= 5:
                        blinking_count = 0
                        self.reset_position()
                    continue
                else:
                    blinking_count = 0

                # Calculate movement
                change_x, change_y = self.calculate_movement(-sensibility_x, sensibility_y)

                # Check if above or bellow screen boundaries
                self.new_pos = [current_pos.x + change_x, current_pos.y + change_y]
                self.new_pos[0] = self.new_pos[0] if self.new_pos[0] < self.calibration.size[0] - 5 \
                    else self.calibration.size[0] - 5
                self.new_pos[1] = self.new_pos[1] if self.new_pos[1] < self.calibration.size[1] - 5 \
                    else self.calibration.size[1] - 5
                self.new_pos[0] = self.new_pos[0] if self.new_pos[0] > 5 else 5
                self.new_pos[1] = self.new_pos[1] if self.new_pos[1] > 5 else 5

                # Skip if distance if less that threshold
                distance = math.hypot((self.new_pos[0] - self.old_pos[0]), (self.new_pos[1]- self.old_pos[1]))
                if distance <= threshold:
                    self.new_pos = self.old_pos

                # Move cursor
                pyautogui.moveTo(self.new_pos[0], self.new_pos[1])
                # print("new_pos: {}".format(new_pos))
            finally:
                # Save last mouse position and gaze
                self.old_pos = self.new_pos
                self.last_gaze = self.current_gaze

    def calculate_movement(self, sensibility_x, sensibility_y):
        eyes_movement_x = (
            (self.current_gaze.eye_left_x - self.last_gaze.eye_left_x) +
            (self.current_gaze.eye_right_x - self.last_gaze.eye_right_x)
        ) / 2
        eyes_movement_y = (
            (self.current_gaze.eye_left_y - self.last_gaze.eye_left_y) +
            (self.current_gaze.eye_right_y - self.last_gaze.eye_right_y)
        ) / 2

        pupils_movement_x = (
            (self.current_gaze.pupil_left_x - self.last_gaze.pupil_left_x) +
            (self.current_gaze.pupil_right_x - self.last_gaze.pupil_right_x)
        ) / 2
        pupils_movement_y = (
            (self.current_gaze.pupil_left_y - self.last_gaze.pupil_left_y) +
            (self.current_gaze.pupil_right_y - self.last_gaze.pupil_right_y)
        ) / 2

        nose_movement_x = self.current_gaze.nose_x - self.last_gaze.nose_x
        nose_movement_y = self.current_gaze.nose_y - self.last_gaze.nose_y

        head_movement_x = (eyes_movement_x + pupils_movement_x + nose_movement_x) / 3
        head_movement_y = (eyes_movement_y + pupils_movement_y + nose_movement_y) / 3

        head_rotation_x = nose_movement_x/(eyes_movement_x*2 if eyes_movement_x != 0 else 1)
        head_rotation_y = nose_movement_y/(eyes_movement_y*2 if eyes_movement_y != 0 else 1)
        # print("head_rotation x: {}, y: {}".format(head_rotation_x, head_rotation_y))

        h_ratio = (self.current_gaze.h_ratio_left + self.current_gaze.h_ratio_right - 1)
        v_ratio = (self.current_gaze.v_ratio_left + self.current_gaze.v_ratio_right - 1)
        # print("ratio h: {}, v: {}".format(h_ratio, v_ratio))

        h_distance = 0
        v_distance = 0

        return (
            int(sensibility_x * (head_movement_x * head_rotation_x + h_distance * h_ratio)),
            int(sensibility_y * (head_movement_y * head_rotation_y + v_distance * v_ratio))
        )

    def reset_position(self):
        self.old_pos = [int(self.calibration.size[0]/2), int(self.calibration.size[1]/2)]
        self.new_pos = self.old_pos
        pyautogui.moveTo(self.new_pos[0], self.new_pos[1])












