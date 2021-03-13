from database import Database
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *
from tkcalendar import DateEntry
from slider import Slider

EMOTION_CLASSES = ["Angry", "Disgust", "Fear", "Happy",
                   "Sad", "Surprise", "Neutral", "None"]
TIME_RANGE = ["Today", "1 week", "1 month",
              "3 months", "6 months", "Customize"]

ROLLING_MEAN_TIME = [("1 min", 1), ("5 mins", 5), ("15 mins", 15), ("30 mins", 30),
                     ("1 hour", 60), ("2 hours", 120), ("6 hours", 360),
                     ("12 hours", 720)]

stress_percent = list(range(0, 101, 10))
STRESS_LEVEL = list(zip([f"{i}%" for i in stress_percent], stress_percent))


class Dashboard():
    def __init__(self, db, master):
        self.db = db
        self.master = master
        self.break_time_len = 60
        self.stress_time_len = 5
        self.create_widget()

    def create_widget(self, x_padding=10, y_padding=3):
        # Statistic Canvas
        self.fig = plt.figure()
        self.ax = self.fig.add_axes([0.1, 0.2, 0.8, 0.7])
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().grid(row=0, column=1)

        # Frame for options bars
        _option_frame = LabelFrame(
            self.master, text="Settings",
            padx=10, pady=10)
        _option_frame.grid(row=0, column=0, sticky="N")

        # Emotion menu dropdown bar
        Label(_option_frame, text="Emotion: ").grid(row=0, column=0, pady=10)
        self.emotion_variable = StringVar(_option_frame)
        self.emotion_variable.set(EMOTION_CLASSES[-1])  # default value
        _emotion_menu = OptionMenu(
            _option_frame,
            self.emotion_variable,
            *EMOTION_CLASSES)
        _emotion_menu.configure(width=10)
        _emotion_menu.grid(
            row=0, column=1,
            padx=x_padding, pady=y_padding,
            sticky="ew")

        # Time range
        Label(_option_frame, text="Time Range: ").grid(
            row=1, column=0,
            padx=x_padding, pady=y_padding)
        self.time_range_variable = StringVar(_option_frame)
        self.time_range_variable.set(TIME_RANGE[0])  # default value
        OptionMenu(_option_frame,
                   self.time_range_variable,
                   *TIME_RANGE).grid(row=1,
                                     column=1, padx=x_padding,
                                     pady=y_padding, sticky="ew")

        # Date time picker
        _today = datetime.today()

        # Start Date picker
        Label(_option_frame, text="Start date: ").grid(
            row=2, column=0,
            padx=x_padding, pady=y_padding)
        self.start_cal = DateEntry(
            _option_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2)
        self.start_cal.set_date(_today)
        self.start_cal.grid(
            row=2, column=1,
            padx=x_padding, pady=y_padding,
            sticky="ew")

        # End date picker
        Label(_option_frame, text="End date: ").grid(row=3, column=0)
        self.end_cal = DateEntry(
            _option_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2)
        self.end_cal.set_date(_today)
        self.end_cal.grid(
            row=3, column=1,
            padx=x_padding, pady=y_padding,
            sticky="ew")

        # Slider
        Label(_option_frame, text="Rolling mean: ").grid(row=4, column=0)
        self.rolling_mean_slider = Slider(
            time_value=ROLLING_MEAN_TIME, parent=_option_frame, init_value_index=2)
        self.rolling_mean_slider.grid(
            row=4, column=1, padx=x_padding, pady=y_padding, sticky="ew")

        # Break time picker
        Label(_option_frame, text="Break time (in minutes): ").grid(
            row=5, column=0)
        self.break_time_entry = Entry(_option_frame)
        self.break_time_entry.insert(END, self.break_time_len)
        self.break_time_entry.grid(row=5, column=1, padx=x_padding,
                                   pady=y_padding, sticky="ew")

        Label(_option_frame, text="Stress time (in minutes): ").grid(
            row=6, column=0)
        self.stress_time_entry = Entry(_option_frame)
        self.stress_time_entry.insert(END, self.stress_time_len)
        self.stress_time_entry.grid(row=6, column=1, padx=x_padding,
                                    pady=y_padding, sticky="ew")

        Label(_option_frame, text="Stress Threshold: ").grid(row=7, column=0)
        self.stress_slider = Slider(
            time_value=STRESS_LEVEL, parent=_option_frame, init_value_index=5)
        self.stress_slider.grid(
            row=7, column=1, padx=x_padding, pady=y_padding, sticky="ew")

        # Submit button
        self.submitButton = Button(
            _option_frame,
            text='Update',
            command=lambda: self.update_fig())
        self.submitButton.grid(
            row=8, column=1,
            padx=x_padding, pady=y_padding)

        self.update_fig()

    def update_break_time(self):
        try:
            value = int(self.break_time_entry.get())
            if value < 1:
                raise ValueError()
            self.break_time_len = value
        except ValueError:
            self.break_time_entry.delete(0, END)
            self.break_time_entry.insert(0, self.break_time_len)
            messagebox.showerror(
                title="Error",
                message="Time fields must be positive. Please try again.")

    def update_stress_time(self):
        try:
            value = int(self.stress_time_entry.get())
            if value < 1:
                raise ValueError()
            self.stress_time_len = value
        except ValueError:
            self.stress_time_entry.delete(0, END)
            self.stress_time_entry.insert(0, self.stress_time_len)
            messagebox.showerror(
                title="Error",
                message="Time fields must be positive. Please try again.")

    def update_fig(self):
        self.update_break_time()
        self.update_stress_time()

        self.ax.clear()
        col = self.emotion_variable.get()
        if self.time_range_variable.get() == "Customize":
            time_start = self.start_cal.get_date()
            time_end = self.end_cal.get_date() + timedelta(days=1)
        else:
            time_start, time_end = self.get_time_range()

        _unix_start = time.mktime(time_start.timetuple())
        _unix_end = time.mktime(time_end.timetuple())

        if _unix_end < _unix_start:
            messagebox.showerror(
                title="Error",
                message="End date is smaller than start date. Please try again.")
            return

        df = self.db.get_record_range(_unix_start, _unix_end)
        df.index = df.apply(lambda row: datetime.fromtimestamp(
            int(row.TimeStamp)), axis=1)  # Local Time
        df_cur = df.loc[time_start:time_end]

        idx = pd.date_range(time_start, time_end, freq='min')
        s = df_cur[col].interpolate('time')
        s.index = pd.DatetimeIndex(s.index)
        s = s.reindex(idx, fill_value=0.0)
        s = pd.to_numeric(s).rolling(
            self.rolling_mean_slider.get_value()).mean()
        self.ax.plot(s, color='black')
        self.ax.set_title(col, fontsize='medium')
        self.ax.set_ylim(bottom=0)

        for tick in self.ax.get_xticklabels():
            tick.set_rotation(90)
        # Consise Date Formatter
        locator = mdates.AutoDateLocator(minticks=5, maxticks=10)
        formatter = mdates.ConciseDateFormatter(locator)
        self.ax.xaxis.set_major_locator(locator)
        self.ax.xaxis.set_major_formatter(formatter)
        self.canvas.draw()

    def break_time_warning(self):
        messagebox.showwarning(title="Break time warning",
                               message=f"You have been on screen for {self.break_time_len} minutes. It's time for a break.")

    def stress_time_warning(self):
        messagebox.showwarning(title="Stress time warning",
                               message=f"You have been under negative emotions for {self.stress_time_len} minutes. It's time for a break.")

    def get_time_range(self):
        time_type = self.time_range_variable.get()
        _today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        time_end = _today + timedelta(days=1)

        if time_type == "1 week":
            time_start = _today - timedelta(days=7)
        elif time_type == "1 month":
            time_start = _today - timedelta(days=30)
        elif time_type == "3 months":
            time_start = _today - timedelta(days=90)
        elif time_type == "6 months":
            time_start = _today - timedelta(days=180)
        else:
            time_start = _today
        return time_start, time_end
