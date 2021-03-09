from tkinter import *
import threading
import cv2
import time
import numpy as np
import tkinter
import PIL
from PIL import Image, ImageTk
from utils import *


class StoppableThread(threading.Thread):
    """Thread class that implemented stop function"""

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class EmoTrackerThread(StoppableThread):
    def __init__(self, video_processor, db, dashboard, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.dashboard = dashboard
        self.video_capture = cv2.VideoCapture(0)
        self.video_processor = video_processor
        self.db = db
        self.emotion_counter = [0 for i in range(
            len(self.video_processor.EMOTION_CLASSES))]

        self.minute_emotion_counter = [0 for i in range(
            len(self.video_processor.EMOTION_CLASSES))]

    def run(self, *args):
        """Record camera, detect face and track emotion within a thread"""
        time_mark = -1  # mark timer to calculate fps
        fps = 0
        onscreen_time = 0
        while not self.stopped():
            _, _frame = self.video_capture.read()
            _frame = cv2.resize(_frame, self.video_processor.window_size)
            faces = self.video_processor.detector.detect_faces(_frame)

            if len(faces) > 0:
                emotion, detect_face_MTCNN = self.video_processor.find_face_MTCNN(
                    _frame, faces)
                if emotion is not None:
                    self.emotion_counter[emotion] += 1
                else:
                    detect_face_MTCNN = _frame
                    self.emotion_counter[-1] += 1  # add to no face detected
            else:
                detect_face_MTCNN = _frame
                self.emotion_counter[-1] += 1  # add to no face detected

            if self.stopped():
                break

            _time_current = int(time.time())
            _minute_counter = _time_current % 60
            if (_time_current != time_mark):
                for i in range(len(self.emotion_counter)):
                    fraction = self.emotion_counter[i]/(fps + 1)
                    self.minute_emotion_counter[i] += fraction
                    self.emotion_counter[i] = 0

                if _time_current % 60 == 0:  # End of minute
                    # Add data to db
                    self.db.insert_row(
                        _time_current, self.minute_emotion_counter)

                    active_time = 60 - self.minute_emotion_counter[-1]
                    if is_low_activity_value_thresh(active_time, thresh=0.1):
                        onscreen_time = 0
                    else:
                        onscreen_time += 1

                    if onscreen_time > self.dashboard.break_time_value:
                        self.dashboard.break_time_warning()

                    for i in range(len(self.minute_emotion_counter)):
                        self.minute_emotion_counter[i] = 0
                fps = 0
                time_mark = _time_current
            else:
                fps += 1

            cv2.imshow('EmoTracker Webcam', detect_face_MTCNN)
            cv2.waitKey(1)
