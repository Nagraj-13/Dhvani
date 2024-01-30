
import cv2
import dlib
from scipy.spatial import distance as dist
import winsound
import threading
import json
import time
import pandas as pd
from data_management import load_data
from speech_recognition_response import talkback

user_driving_patterns = []

sleepy_status = False
sleepiness_timer = 0
sleepiness_threshold = 0.2  
sleepiness_duration = 10



sleep_patterns_excel_file = 'sleep_patterns.xlsx'

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(r"C:\Users\nagaraj\Desktop\shape_predictor_68_face_landmarks.dat")

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

cap = cv2.VideoCapture(0)

def face_recognition():
    global sleepy_status, sleepiness_timer, user_driving_patterns

    while True:
        ret, frame = cap.read()

       
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

      
        faces = detector(gray)

        for face in faces:
      
            shape = predictor(gray, face)
            landmarks = [(shape.part(i).x, shape.part(i).y) for i in range(68)]

            left_eye = landmarks[36:42]
            right_eye = landmarks[42:48]

            ear_left = eye_aspect_ratio(left_eye)
            ear_right = eye_aspect_ratio(right_eye)

    
            ear_avg = (ear_left + ear_right) / 2.0

            if ear_avg < sleepiness_threshold:
                sleepiness_timer += 1

                if sleepiness_timer >= sleepiness_duration:
                    print("User is feeling sleepy for more than 5 seconds.")
                    winsound.Beep(1000, 500) 
                    sleepy_status = True
                    sleepiness_timer = 0

                    sleep_pattern = {"timestamp": time.time(), "status": "sleepy"}
                    user_driving_patterns.append(sleep_pattern)
                    df_sleep_patterns = pd.DataFrame(user_driving_patterns)
                    df_sleep_patterns.to_excel(sleep_patterns_excel_file, index=False)
            else:
                sleepiness_timer = 0
                sleepy_status = False

        cv2.imshow('Frame', frame)

        # Break the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()