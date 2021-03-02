from tkinter import *
from emotrackerthread import EmoTrackerThread
from videoprocessor import VideoProcessor
from database import Database
from dashboard import Dashboard
from report import Report

from tkinter import ttk


class GUI_EmoTracker():
    def __init__(self, emotion_dir, face_detector_dir=None, window_size=(480, 360)):
        self.root = Tk()
        self.tab_parent = ttk.Notebook(self.root)

        self.tab_tracker = ttk.Frame(self.tab_parent)
        self.tab_dashboard_day = ttk.Frame(self.tab_parent)
        self.tab_report = ttk.Frame(self.tab_parent)

        # self.tab_parent.add(self.tab_tracker, text="This Session")
        self.tab_parent.add(self.tab_dashboard_day, text="Statistics")
        self.tab_parent.add(self.tab_report, text="Generate Report")
        self.tab_parent.pack(expand=1, fill="both")

        self.video_processor = VideoProcessor(
            emotion_dir=emotion_dir,
            face_detector_dir=face_detector_dir,
            window_size=window_size)
        self.setup_root()
        self.db = Database()
        self.dashboard = Dashboard(self.db, self.tab_dashboard_day)
        self.report = Report(self.tab_report, self.db)

    def setup_root(self):
        self.root.title("EmoTracker Dashboard")
        # self.root.geometry("400x400")
        self.root.resizable(0, 0)

    def main(self):
        self.worker_frame = EmoTrackerThread(
            self.video_processor, self.tab_tracker, self.db)
        self.worker_frame.start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        print("Stopping")
        self.worker_frame.stop()
        print("Thread Stopped")
        self.worker_frame.join()
        print("Thread joined")
        self.root.destroy()
        self.root.quit()
        print("Finished")
