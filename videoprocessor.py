import cv2
from mtcnn import MTCNN
import time
from tensorflow.keras.models import load_model
import tensorflow as tf
import numpy as np
import os
# os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

class VideoProcessor:
    def __init__(self, 
            emotion_dir, window_size, 
            face_detector_dir=None, 
            min_face_size=80, scale_factor=0.7, res=360):
        self.EMOTION_CLASSES = ["Angry", "Disgust", "Fear", "Happy", "Sad", 
                                "Surprise", "Neutral", "None"]
        self.window_size = window_size
        self.emotion_model = load_model(emotion_dir)
        self.detector = MTCNN(
            weights_file=face_detector_dir, 
            min_face_size=min_face_size, 
            scale_factor=scale_factor)

    def detect_emotion(self, img):
        img = cv2.resize(img, (150,150))
        img = img/255.0
        img = np.expand_dims(img, 0)
        # pred = self.emotion_model.predict_step(img)
        pred = self.emotion_model(img, training = False)
        resultEmotion = np.argmax(pred[0])
        return resultEmotion, self.EMOTION_CLASSES[resultEmotion]

    def find_face_MTCNN(self, frame, result_list):
        result_list.sort(
            key = lambda x: (x['box'][2] - x['box'][0])*(x['box'][3] - x['box'][1]))
        result = result_list[0]        
        x, y, w, h = result['box']
        roi = frame[y:y+h, x:x+w]
        resultEmotion, emotion = self.detect_emotion(roi)
        # draw rectangle
        cv2.rectangle(
            img=frame, pt1=(x, y), pt2=(x+w, y+h),
            color=(0, 155, 255), thickness=1)
        cv2.putText(
            img=frame, text=emotion, org=(x, y-10), 
            fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
            fontScale=0.9, color=(0, 155, 255), thickness=2)

        return resultEmotion, frame
    

