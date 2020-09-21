import math

import dlib
import numpy
import numpy as np
import cv2
import typing

from .calibration import Calibration
from .pupil import Pupil


class Eye(object):
    """
    This class creates a new frame to isolate the eye and
    initiates the pupil detection.
    """

    LEFT_EYE_POINTS = [36, 37, 38, 39, 40, 41]
    RIGHT_EYE_POINTS = [42, 43, 44, 45, 46, 47]

    def __init__(
            self,
            original_frame: typing.Optional[numpy.ndarray],
            landmarks: typing.Optional[dlib.full_object_detection],
            side: typing.Optional[int],
            calibration: typing.Optional[Calibration]):
        """

        :param original_frame:
        :param landmarks: Facial landmarks for the face region
        :param side: Indicates whether it's the left eye (0) or the right eye (1)
        :param calibration:
        """
        self.landmarks = landmarks
        self.side = side
        self.frame = None
        self.origin = None
        self.center = None
        self.radius = None
        self.pupil = None

        if not self.landmarks: return

        self._analyze(original_frame, calibration)

    def _analyze(self, original_frame, calibration):
        """Detects and isolates the eye in a new frame, sends data to the calibration
        and initializes Pupil object.

        Arguments:
            original_frame (numpy.ndarray): Frame passed by the user
            calibration (calibration.Calibration): Manages the binarization threshold value
        """
        if self.side == 0:
            points = self.LEFT_EYE_POINTS
        elif self.side == 1:
            points = self.RIGHT_EYE_POINTS
        else:
            return

        self.blinking = self._blinking_ratio(points)
        self._isolate(original_frame, points)

        if not calibration.is_complete():
            calibration.evaluate(self.frame, self.side)

        threshold = calibration.threshold(self.side)
        self.pupil = Pupil(self.frame, threshold)

    @staticmethod
    def _middle_point(p1: dlib.point, p2: dlib.point):
        """Returns the middle point (x,y) between two points

        Arguments:
            p1 (dlib.point): First point
            p2 (dlib.point): Second point
        """
        x = int((p1.x + p2.x) / 2)
        y = int((p1.y + p2.y) / 2)
        return x, y

    def _isolate(self, frame, points):
        """Isolate an eye, to have a frame without other part of the face.

        Arguments:
            frame (numpy.ndarray): Frame containing the face
            points (list): Points of an eye (from the 68 Multi-PIE landmarks)
        """
        region = np.array([(self.landmarks.part(point).x, self.landmarks.part(point).y) for point in points])
        region = region.astype(np.int32)

        # Applying a mask to get only the eye
        height, width = frame.shape[:2]
        black_frame = np.zeros((height, width), np.uint8)
        mask = np.full((height, width), 255, np.uint8)
        cv2.fillPoly(mask, [region], (0, 0, 0))
        eye = cv2.bitwise_not(black_frame, frame.copy(), mask=mask)

        # Cropping on the eye
        margin = 5
        min_x = np.min(region[:, 0]) - margin
        max_x = np.max(region[:, 0]) + margin
        min_y = np.min(region[:, 1]) - margin
        max_y = np.max(region[:, 1]) + margin

        self.frame = eye[min_y:max_y, min_x:max_x]
        self.origin = (min_x, min_y)

        height, width = self.frame.shape[:2]
        height = 2 if height <= 1 else height
        width = 2 if width <= 1 else width
        self.radius = int((height + width) / 4)
        self.center = (width / 2, height / 2)

    def _blinking_ratio(self, points):
        """Calculates a ratio that can indicate whether an eye is closed or not.
        It's the division of the width of the eye, by its height.

        Arguments:
            points (list): Points of an eye (from the 68 Multi-PIE landmarks)

        Returns:
            The computed ratio
        """
        left = (self.landmarks.part(points[0]).x, self.landmarks.part(points[0]).y)
        right = (self.landmarks.part(points[3]).x, self.landmarks.part(points[3]).y)
        top = self._middle_point(self.landmarks.part(points[1]), self.landmarks.part(points[2]))
        bottom = self._middle_point(self.landmarks.part(points[5]), self.landmarks.part(points[4]))

        eye_width = math.hypot((left[0] - right[0]), (left[1] - right[1]))
        eye_height = math.hypot((top[0] - bottom[0]), (top[1] - bottom[1]))

        try:
            ratio = eye_width / eye_height
        except ZeroDivisionError:
            ratio = None

        return ratio

    @property
    def eye_center(self):
        """Returns the coordinates of the center of the eye"""
        if self.center and self.origin:
            x = int(self.origin[0] + self.center[0])
            y = int(self.origin[1] + self.center[1])
            return x, y

    @property
    def pupil_located(self):
        """Check that the pupils have been located"""
        try:
            int(self.pupil.x)
            int(self.pupil.y)
            return True
        except (TypeError, AttributeError) as _:
            return False

    @property
    def pupil_center(self):
        """Returns the coordinates of the center of the pupil"""
        if self.pupil_located:
            x = self.origin[0] + self.pupil.x
            y = self.origin[1] + self.pupil.y
            return x, y
        else:
            return None

    def horizontal_ratio(self):
        """Returns a number between 0.0 and 1.0 that indicates the
        horizontal direction of the gaze. The extreme right is 0.0,
        the center is 0.5 and the extreme left is 1.0
        """
        if self.pupil_located:
            # pupil_pos = self.pupil.x / (self.center[0] * 2 - 10)
            # return pupil_pos
            if self.side == 0:
                points = self.LEFT_EYE_POINTS
            elif self.side == 1:
                points = self.RIGHT_EYE_POINTS
            else:
                return

            left = (self.landmarks.part(points[0]).x, self.landmarks.part(points[0]).y)
            right = (self.landmarks.part(points[3]).x, self.landmarks.part(points[3]).y)
            eye_width = math.hypot((left[0] - right[0]), (left[1] - right[1]))
            pupil_to_left = math.hypot((left[0] - self.pupil_center[0]), (left[1] - self.pupil_center[1]))
            pupil_to_right = math.hypot((self.pupil_center[0] - right[0]), (self.pupil_center[1]- right[1]))
            semi_perimeter = (eye_width + pupil_to_left + pupil_to_right) / 2
            area = math.sqrt(semi_perimeter*(semi_perimeter-eye_width)*(semi_perimeter-pupil_to_left)*(semi_perimeter-pupil_to_right))
            height = area / eye_width
            return math.hypot(pupil_to_left, height) / eye_width


    def vertical_ratio(self):
        """Returns a number between 0.0 and 1.0 that indicates the
        vertical direction of the gaze. The extreme top is 0.0,
        the center is 0.5 and the extreme bottom is 1.0
        """
        if self.pupil_located:
            # pupil_pos = self.pupil.y / (self.center[1] * 2 - 10)
            # return pupil_pos

            if self.side == 0:
                points = self.LEFT_EYE_POINTS
            elif self.side == 1:
                points = self.RIGHT_EYE_POINTS
            else:
                return

            top = self._middle_point(self.landmarks.part(points[1]), self.landmarks.part(points[2]))
            bottom = self._middle_point(self.landmarks.part(points[5]), self.landmarks.part(points[4]))
            eye_height = math.hypot((top[0] - bottom[0]), (top[1] - bottom[1]))
            pupil_to_left = math.hypot((top[0] - self.pupil_center[0]), (top[1] - self.pupil_center[1]))
            pupil_to_right = math.hypot((self.pupil_center[0] - bottom[0]), (self.pupil_center[1]- bottom[1]))
            semi_perimeter = (eye_height + pupil_to_left + pupil_to_right) / 2
            area = math.sqrt(semi_perimeter*(semi_perimeter-eye_height)*(semi_perimeter-pupil_to_left)*(semi_perimeter-pupil_to_right))
            height = area / eye_height
            return math.hypot(pupil_to_left, height) / eye_height