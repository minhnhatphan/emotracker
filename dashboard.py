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

EMOTION_CLASSES = ["Angry", "Disgust", "Fear", "Happy",
                   "Sad", "Surprise", "Neutral", "None"]
TIME_RANGE = ["Today", "1 week", "1 month",
              "3 months", "6 months", "Customize"]


class Dashboard():
    def __init__(self, db, master):
        self.db = db
        self.master = master
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
        _option_frame.grid(row=0, column=0)
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
        self.start_cal.grid(row=2, column=1,
                            padx=x_padding, pady=y_padding)
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
            padx=x_padding, pady=y_padding)
        # Submit button
        self.submitButton = Button(
            _option_frame,
            text='Update',
            command=lambda: self.update_fig())
        self.submitButton.grid(
            row=4, column=1,
            padx=x_padding, pady=y_padding)

        self.update_fig()

    def update_fig(self):
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
        s = pd.to_numeric(s).groupby(
            pd.Grouper(freq='15Min')).aggregate(np.mean)
        # self.ax.plot(df_cur[col].interpolate('time'), color='black')
        self.ax.plot(s, color='black')
        self.ax.set_title(col, fontsize='medium')
        self.ax.set_ylim(bottom=0)

        # Rotate x ticks vertically
        for tick in self.ax.get_xticklabels():
            tick.set_rotation(90)
        # Consise Date Formatter
        locator = mdates.AutoDateLocator(minticks=5, maxticks=10)
        formatter = mdates.ConciseDateFormatter(locator)
        self.ax.xaxis.set_major_locator(locator)
        self.ax.xaxis.set_major_formatter(formatter)
        self.canvas.draw()

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