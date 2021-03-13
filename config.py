EMOTION_CLASSES = ["Angry", "Disgust", "Fear", "Happy",
                   "Sad", "Surprise", "Neutral", "None"]

TIME_RANGE = ["Today", "1 week", "1 month",
              "3 months", "6 months", "Customize"]

ROLLING_MEAN_TIME = [("1 min", 1), ("5 mins", 5), ("15 mins", 15), ("30 mins", 30),
                     ("1 hour", 60), ("2 hours", 120), ("6 hours", 360),
                     ("12 hours", 720)]

stress_percent = list(range(10, 101, 10))
STRESS_LEVEL = list(zip([f"{i}%" for i in stress_percent], stress_percent))

X_PADDING = 15

Y_PADDING = 3
