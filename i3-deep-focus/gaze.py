class Gaze:
    def __init__(
            self,
            gaze_tracking = None,
            eye_left_x = None,
            eye_left_y = None,
            eye_right_x = None,
            eye_right_y = None,
            pupil_left_x = None,
            pupil_left_y = None,
            pupil_right_x = None,
            pupil_right_y = None,
            h_ratio_left = None,
            h_ratio_right = None,
            v_ratio_left = None,
            v_ratio_right = None,
            nose_x = None,
            nose_y = None,
    ):
        try:
            self.success = True
            self.eye_left_x = gaze_tracking.eye_left.eye_center[0]
            self.eye_left_y = gaze_tracking.eye_left.eye_center[1]
            self.eye_right_x = gaze_tracking.eye_right.eye_center[0]
            self.eye_right_y = gaze_tracking.eye_right.eye_center[1]
            self.pupil_left_x = gaze_tracking.eye_left.pupil_center[0]
            self.pupil_left_y = gaze_tracking.eye_left.pupil_center[1]
            self.pupil_right_x = gaze_tracking.eye_right.pupil_center[0]
            self.pupil_right_y = gaze_tracking.eye_right.pupil_center[1]
            self.h_ratio_left = gaze_tracking.eye_left.horizontal_ratio()
            self.h_ratio_right = gaze_tracking.eye_right.horizontal_ratio()
            self.v_ratio_left = gaze_tracking.eye_left.vertical_ratio()
            self.v_ratio_right = gaze_tracking.eye_right.vertical_ratio()
            self.nose_x = gaze_tracking.nose[0]
            self.nose_y = gaze_tracking.nose[1]
        except (TypeError, AttributeError):
            self.eye_left_x = eye_left_x
            self.eye_left_y = eye_left_y
            self.eye_right_x = eye_right_x
            self.eye_right_y = eye_right_y
            self.pupil_left_x = pupil_left_x
            self.pupil_left_y = pupil_left_y
            self.pupil_right_x = pupil_right_x
            self.pupil_right_y = pupil_right_y
            self.h_ratio_left = h_ratio_left
            self.h_ratio_right = h_ratio_right
            self.v_ratio_left = v_ratio_left
            self.v_ratio_right = v_ratio_right
            self.nose_x = nose_x
            self.nose_y = nose_y

    def __list__(self):
        return [
            self.eye_left_x,
            self.eye_left_y,
            self.eye_right_x,
            self.eye_right_y,
            self.pupil_left_x,
            self.pupil_left_y,
            self.pupil_right_x,
            self.pupil_right_y,
            self.h_ratio_left,
            self.h_ratio_right,
            self.v_ratio_left,
            self.v_ratio_right,
            self.nose_x,
            self.nose_y
        ]

    def __bool__(self):
        return all(self.__list__())

    def __str__(self):
        return str(self.__list__())

    def __add__(self, other):
        return Gaze(
                None,
                self.eye_left_x if self.eye_left_x else 0 + other.eye_left_x  if other.eye_left_x else 0,
                self.eye_left_y if self.eye_left_y else 0 + other.eye_left_y  if other.eye_left_y else 0,
                self.eye_right_x if self.eye_right_x else 0 + other.eye_right_x  if other.eye_right_x else 0,
                self.eye_right_y if self.eye_right_y else 0 + other.eye_right_y  if other.eye_right_y else 0,
                self.pupil_left_x if self.pupil_left_x else 0 + other.pupil_left_x  if other.pupil_left_x else 0,
                self.pupil_left_y if self.pupil_left_y else 0 + other.pupil_left_y  if other.pupil_left_y else 0,
                self.pupil_right_x if self.pupil_right_x else 0 + other.pupil_right_x  if other.pupil_right_x else 0,
                self.pupil_right_y if self.pupil_right_y else 0 + other.pupil_right_y  if other.pupil_right_y else 0,
                self.h_ratio_left if self.h_ratio_left else 0 + other.h_ratio_left  if other.h_ratio_left else 0,
                self.h_ratio_right if self.h_ratio_right else 0 + other.h_ratio_right  if other.h_ratio_right else 0,
                self.v_ratio_left if self.v_ratio_left else 0 + other.v_ratio_left  if other.v_ratio_left else 0,
                self.v_ratio_right if self.v_ratio_right else 0 + other.v_ratio_right  if other.v_ratio_right else 0,
                self.nose_x if self.nose_x else 0 + other.nose_x  if other.nose_x else 0,
                self.nose_y if self.nose_y else 0 + other.nose_y  if other.nose_y else 0
        )
