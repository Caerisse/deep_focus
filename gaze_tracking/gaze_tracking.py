from __future__ import division
import os
import cv2
import dlib
import typing

import numpy
from imutils import face_utils
from .eye import Eye
from .calibration import Calibration


class GazeTracking(object):
    """
    This class tracks the user's gaze.
    It provides useful information like the position of the eyes
    and pupils and allows to know if the eyes are open or closed
    """

    def __init__(self):
        self.frame:       typing.Optional[numpy.ndarray]              = None
        self.faces:       typing.Optional[typing.List[numpy.ndarray]] = None
        self.landmarks:   typing.Optional[dlib.full_object_detection] = None
        self.calibration: Calibration                                 = Calibration()
        self.eye_left:    typing.Optional[Eye]                        = Eye(self.frame, self.landmarks, 0, self.calibration)
        self.eye_right:   typing.Optional[Eye]                        = Eye(self.frame, self.landmarks, 1, self.calibration)
        self.nose:        typing.Optional[typing.Tuple]               = None

        # _face_detector is used to detect faces
        self._face_detector = dlib.get_frontal_face_detector()

        # _predictor is used to get facial landmarks of a given face
        cwd = os.path.abspath(os.path.dirname(__file__))
        model_path = os.path.abspath(os.path.join(cwd, "trained_models/shape_predictor_68_face_landmarks.dat"))
        self._predictor = dlib.shape_predictor(model_path)

    def _analyze(self):
        """Detects the face and initialize Eye objects"""
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        self.faces = self._face_detector(frame)
        self.landmarks = self._predictor(frame, self.face) if self.faces else None
        self.eye_left = Eye(frame, self.landmarks, 0, self.calibration)
        self.eye_right = Eye(frame, self.landmarks, 1, self.calibration)
        self.nose = (self.landmarks.part(30).x, self.landmarks.part(30).y) if self.landmarks else None

    def refresh(self, frame: numpy.ndarray):
        """Refreshes the frame and analyzes it.

        Arguments:
            frame (numpy.ndarray): The frame to analyze
        """
        self.frame = frame
        self._analyze()

    def run(self, webcam):
        """
        Gets frame form webcam and calls refresh
        :param webcam:
        :return:
        """
        while True:
            _, frame = webcam.read()
            self.refresh(frame)

    @property
    def face(self):
        # TODO: if multiple faces get one nearer the center
        if self.faces:
            return self.faces[0]
        else:
            return None

    @property
    def pupils_located(self):
        if self.eye_left and self.eye_right:
            return self.eye_left.pupil_located and self.eye_right.pupil_located

    def is_right(self):
        """Returns true if the user is looking to the right"""
        if self.pupils_located:
            return (self.eye_left.horizontal_ratio() + self.eye_right.horizontal_ratio()) / 2 <= 0.4

    def is_left(self):
        """Returns true if the user is looking to the left"""
        if self.pupils_located:
            return (self.eye_left.horizontal_ratio() + self.eye_right.horizontal_ratio()) / 2 >= 0.6

    def is_center(self):
        """Returns true if the user is looking to the center"""
        if self.pupils_located:
            return self.is_right() is not True and self.is_left() is not True

    def is_blinking(self):
        """Returns true if the user closes his eyes"""
        if self.pupils_located:
            blinking_ratio = (self.eye_left.blinking + self.eye_right.blinking) / 2
            return blinking_ratio > 3.8


    def annotated_frame(self):
        """Returns the main frame with pupils highlighted"""
        frame = self.frame.copy()

        red = (0, 0, 255)
        green = (0, 255, 0)
        blue = (255, 0, 0)

        if self.face:
            # All landmarks points
            shape = face_utils.shape_to_np(self.landmarks)
            for (x, y) in shape:
                cv2.circle(frame, (x, y), 2, blue, -1)

            # Face boundaries
            # left = self.face.left()
            # top = self.face.top()
            # bottom = self.face.bottom()
            # right = self.face.right()
            # cv2.line(frame, (left, top), (right, top), red)
            # cv2.line(frame, (right, top), (right, bottom), red)
            # cv2.line(frame, (right, bottom), (left, bottom), red)
            # cv2.line(frame, (left, bottom), (left, top), red)

            # Eyes Circle
            if self.eye_left.radius:
                left_center = self.eye_left.eye_center
                cv2.circle(frame, left_center, int(self.eye_left.radius), green)
            if self.eye_right.radius:
                right_center = self.eye_right.eye_center
                cv2.circle(frame, right_center, int(self.eye_right.radius), green)

            # Cross in eyes
            if self.eye_left.pupil_located:
                x_left, y_left = self.eye_left.pupil_center
                cv2.line(frame, (x_left - 5, y_left), (x_left + 5, y_left), green)
                cv2.line(frame, (x_left, y_left - 5), (x_left, y_left + 5), green)
            if self.eye_right.pupil_located:
                x_right, y_right = self.eye_right.pupil_center
                cv2.line(frame, (x_right - 5, y_right), (x_right + 5, y_right), green)
                cv2.line(frame, (x_right, y_right - 5), (x_right, y_right + 5), green)

        return frame
