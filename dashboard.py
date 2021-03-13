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
from utils import *
from config import *


class Dashboard():
    def __init__(self, db, master):
        self.db = db
        self.master = master
        self.break_time_len = 60
        self.stress_time_len = 5
        self.create_widgets()

    def create_widgets(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_axes([0.1, 0.2, 0.8, 0.7])
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().grid(row=0, column=1, rowspan=2)

        session_frame = LabelFrame(
            self.master, text="Session",
            padx=10, pady=10)
        session_frame = configure_column(session_frame, [1, 1])
        session_frame = configure_row(session_frame, [1, 1, 1, 1])
        session_frame.grid(row=0, column=0, sticky="nsew")

        stats_option_frame = LabelFrame(
            self.master, text="Settings",
            padx=10, pady=10)
        stats_option_frame = configure_column(stats_option_frame, [1, 1])
        stats_option_frame = configure_row(
            stats_option_frame, [1, 1, 1, 1, 1, 2])
        stats_option_frame.grid(row=1, column=0, sticky="nsew")

        self.create_session_widgets(session_frame)
        self.create_stats_option_widgets(stats_option_frame)

        self.update_fig()

    def create_session_widgets(self, session_frame):
        Label(session_frame, text="Time to break (in minutes): ").grid(
            row=0, column=0, padx=X_PADDING, pady=Y_PADDING, sticky="w")
        self.break_time_entry = Entry(session_frame)
        self.break_time_entry.insert(END, self.break_time_len)
        self.break_time_entry.grid(row=0, column=1, padx=X_PADDING,
                                   pady=Y_PADDING, sticky="ew")

        Label(session_frame, text="Stress length (in minutes): ").grid(
            row=1, column=0, padx=X_PADDING, pady=Y_PADDING, sticky="w")
        self.stress_time_entry = Entry(session_frame)
        self.stress_time_entry.insert(END, self.stress_time_len)
        self.stress_time_entry.grid(
            row=1, column=1, padx=X_PADDING, pady=Y_PADDING, sticky="ew")

        Label(session_frame, text="Stress Threshold: ").grid(
            row=2, column=0, padx=X_PADDING, pady=Y_PADDING, sticky="w")
        self.stress_slider = Slider(
            time_value=STRESS_LEVEL, parent=session_frame, init_value_index=4, length=130)
        self.stress_slider.grid(
            row=2, column=1, padx=X_PADDING, pady=Y_PADDING, sticky="ew")

        update_session_button = Button(
            session_frame,
            text='Update',
            command=lambda: self.update_session(), padx=50)
        update_session_button.grid(
            row=3, column=0, columnspan=2, sticky='n')

    def create_stats_option_widgets(self, stats_option_frame):
        # Emotion menu dropdown bar
        Label(stats_option_frame, text="Emotion: ").grid(
            row=0, column=0, padx=X_PADDING, pady=Y_PADDING, sticky="w")
        self.emotion_variable = StringVar(stats_option_frame)
        self.emotion_variable.set(EMOTION_CLASSES[-1])  # default value
        OptionMenu(
            stats_option_frame, self.emotion_variable, *EMOTION_CLASSES
        ).grid(row=0, column=1, padx=X_PADDING, pady=Y_PADDING, sticky="ew")

        # Time range
        self.time_range_variable = StringVar(stats_option_frame)
        self.time_range_variable.set(TIME_RANGE[0])
        Label(
            stats_option_frame, text="Time Range: "
        ).grid(row=1, column=0, padx=X_PADDING, pady=Y_PADDING, sticky="w")
        OptionMenu(
            stats_option_frame, self.time_range_variable, *TIME_RANGE
        ).grid(row=1, column=1, padx=X_PADDING, pady=Y_PADDING, sticky="ew")

        # Start Date picker
        _today = datetime.today()
        Label(stats_option_frame, text="Start date: ").grid(
            row=2, column=0, padx=X_PADDING, pady=Y_PADDING, sticky="w")
        self.start_cal = DateEntry(
            stats_option_frame, width=12,
            background='darkblue', foreground='white', borderwidth=2)
        self.start_cal.set_date(_today)
        self.start_cal.grid(
            row=2, column=1, padx=X_PADDING, pady=Y_PADDING, sticky="ew")

        # End date picker
        Label(stats_option_frame, text="End date: ").grid(
            row=3, column=0, padx=X_PADDING, pady=Y_PADDING, sticky="w")
        self.end_cal = DateEntry(
            stats_option_frame, width=12,
            background='darkblue', foreground='white', borderwidth=2)
        self.end_cal.set_date(_today)
        self.end_cal.grid(
            row=3, column=1, padx=X_PADDING, pady=Y_PADDING, sticky="ew")

        # Slider
        Label(stats_option_frame, text="Rolling mean: ").grid(
            row=4, column=0, padx=X_PADDING, pady=Y_PADDING, sticky="w")
        self.rolling_mean_slider = Slider(
            time_value=ROLLING_MEAN_TIME, parent=stats_option_frame,
            init_value_index=2, length=180)
        self.rolling_mean_slider.grid(
            row=4, column=1, padx=X_PADDING, pady=Y_PADDING, sticky="ew")

        # Submit button
        update_fig_button = Button(
            stats_option_frame, text='Update',
            command=lambda: self.update_fig(), padx=50)
        update_fig_button.grid(row=5, column=0, columnspan=2, sticky='n')

    def update_session(self):
        self.update_break_time()
        self.update_stress_time()

    def update_fig(self):
        self.ax.clear()
        self.ax.plot(self.get_emotion_in_range(), color='black')
        self.ax.set_title(self.emotion_variable.get(), fontsize='medium')
        self.ax.set_ylim(bottom=0)

        for tick in self.ax.get_xticklabels():
            tick.set_rotation(90)
        # Consise Date Formatter
        locator = mdates.AutoDateLocator(minticks=5, maxticks=10)
        formatter = mdates.ConciseDateFormatter(locator)
        self.ax.xaxis.set_major_locator(locator)
        self.ax.xaxis.set_major_formatter(formatter)
        self.canvas.draw()

    def get_emotion_in_range(self):
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
        s = df_cur[self.emotion_variable.get()].interpolate('time')
        s.index = pd.DatetimeIndex(s.index)
        s = s.reindex(idx, fill_value=0.0)
        s = pd.to_numeric(s).rolling(
            self.rolling_mean_slider.get_value()).mean()
        return s

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
