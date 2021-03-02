from gui_emotracker import GUI_EmoTracker

emotion_dir = "C:/Users/Minh Phan/EmoTracker/weights/Xception_Feb_11_2021/model_Xception_Feb_11_2021.h5"
gui = GUI_EmoTracker(emotion_dir=emotion_dir)
gui.main()
