from tkinter import *
import os
from datetime import datetime, timedelta
from tkcalendar import DateEntry
import time
import pandas as pd
import matplotlib.pyplot as plt

EMOTION_CLASSES = ["Angry", "Disgust", "Fear", "Happy",
                   "Sad", "Surprise", "Neutral", "None"]


class Report:
    def __init__(self, master, db):
        self.master = master
        self.db = db
        self.date_range = IntVar()
        self.date_range.set(7)
        self.report_directory = os.getcwd()

        self.period_frame = Frame(self.master)
        self.period_frame.grid(row=1, column=1)

        self.create_widget()

    def get_directory(self):
        self.report_directory = filedialog.askdirectory()
        self.directory_label.configure(
            text="Save report at: {}".format(self.report_directory))

    def create_widget(self):
        Label(self.master, text="Save report at: ").grid(row=0, column=0)
        self.directory_label = Label(self.master, text=self.report_directory)
        self.directory_label.grid(row=0, column=1)
        Button(self.master, text="Change",
               command=self.get_directory).grid(row=0, column=2)

        Label(self.master, text="Period: ").grid(row=1, column=0)
        Radiobutton(self.period_frame, text="Weekly (7 days)",
                    variable=self.date_range, value=7).grid(row=0, column=0)
        Radiobutton(self.period_frame, text="Monthly (30 days)",
                    variable=self.date_range, value=30).grid(row=0, column=1)

        Label(self.master, text="End date: ").grid(row=2, column=0)
        self.end_date = DateEntry(self.master, width=12, background='darkblue',
                                  foreground='white', borderwidth=2)
        self.end_date.grid(row=2, column=1)

        Button(self.master, text="Generate Report",
               command=self.generate_report).grid(row=3, column=1)

    def generate_report(self):
        end_date = self.end_date.get_date() + timedelta(days=1)  # Until end of day
        start_date = end_date - timedelta(days=self.date_range.get())
        _unix_start = time.mktime(start_date.timetuple())
        _unix_end = time.mktime(end_date.timetuple())

        self.df = self.db.get_record_range(_unix_start, _unix_end)
        self.df["DateTime"] = self.df.apply(
            lambda row: datetime.fromtimestamp(row["TimeStamp"]), axis=1)
        self.df["TimeOfDay"] = self.df.apply(
            lambda row: row["DateTime"].hour, axis=1)
        self.prepare_activity_df()

        _date_range_str = "weekly" if self.date_range.get() == 7 else "monthly"

        self.generate_emotion_mean_plot(_date_range_str)
        self.generate_activity_plot()
        self.generate_pos_neg_plot()
        self.generate_emotion_pie_plot()

        self.generate_pdf()

    def prepare_activity_df(self):
        self.activity_df = self.df.groupby("TimeOfDay").mean().drop(
            ["TimeStamp"], axis=1)
        self.activity_df["Total"] = self.activity_df.sum(axis=1)

        def get_activity(row, mood):
            if row["Total"] == 0:
                return 0
            if mood == "None":
                return ((row["Total"]-row[mood])/row["Total"])*100
            return (row[mood]/row["Total"])*100

        def get_emotion(row, emotions):
            res = 0
            for emotion in emotions:
                res += row[emotion]
            return res

        self.activity_df["Activity"] = self.activity_df.apply(
            get_activity, axis=1, mood="None")
        self.activity_df["Negative"] = self.activity_df.apply(get_emotion, axis=1,
                                                              emotions=["Angry", "Disgust", "Fear", "Sad"])
        self.activity_df["Positive"] = self.activity_df.apply(
            get_emotion, axis=1, emotions=["Happy"])
        self.activity_df["Neutral"] = self.activity_df.apply(
            get_emotion, axis=1, emotions=["Neutral", "Surprise"])

        self.activity_df = self.activity_df.reindex(
            pd.RangeIndex(24)).fillna(0)

    def generate_emotion_mean_plot(self, date_range_str):
        self.EMOTION_MEAN_PLOT = f"{date_range_str}_mean.png"

        emo_df = pd.DataFrame(
            data=list(self.df.columns)[1:-3],
            columns=["Emotion"])
        emo_df["Sum"] = emo_df.apply(
            lambda row: self.df[row["Emotion"]].mean(), axis=1)
        ax = emo_df.plot.bar(
            x="Emotion",
            y="Sum",
            title=f"{date_range_str} mean",
            figsize=(10, 5),
            legend=False,
            fontsize=8)
        ax.set_xlabel("Emotion", fontsize=12)
        ax.set_ylabel("Average Time/Min", fontsize=12)

        plt.savefig(os.path.join(self.report_directory, EMOTION_MEAN_PLOT))

    def generate_activity_plot(self):
        self.ACTIVITY_PLOT = "daily_activity_plot.png"
        self.activity_df.plot.bar(
            y="Activity",
            title="Activity Time in Day",
            xlabel="Time",
            ylabel="Percentage",
            legend=False
        )

        plt.savefig(os.path.join(self.report_directory, ACTIVITY_PLOT))

    def generate_pos_neg_plot(self):
        self.POS_NEG_PLOT = "positive_vs_negative.png"
        self.activity_df.plot(
            y=["Positive", "Negative"],
            kind="bar",
            title="Positive vs Negative",
            xlabel="Time",
            ylabel="s/min"
        )
        plt.savefig(os.path.join(self.report_directory, POS_NEG_PLOT))

    def generate_emotion_pie_plot(self):
        self.EMOTION_PIE_PLOT = "emotion_pie.png"
        self.activity_df[["Positive", "Negative", "Neutral"]].sum().plot(
            kind="pie",
            title="Emotion Proportions",
            ylabel="",
            labeldistance=1.1,
            autopct=lambda p: '{:.2f}%'.format(p)
        )
        plt.savefig(os.path.join(self.report_directory, EMOTION_PIE_PLOT))

    def generate_pdf(self):
        pass
