from tkinter import *
import os
from datetime import datetime, timedelta
from tkcalendar import DateEntry
import time
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from slider import Slider
from utils import *
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle

EMOTION_CLASSES = ["Angry", "Disgust", "Fear", "Happy",
                   "Sad", "Surprise", "Neutral", "None"]


class Report:
    def __init__(self, master, db):
        self.master = master
        self.db = db
        self.date_range = IntVar()
        self.date_range.set(7)
        self.report_directory = os.getcwd()
        self.create_widget()

    def get_directory(self):
        self.report_directory = filedialog.askdirectory()
        self.directory_label.configure(
            text=self.report_directory)

    def create_widget(self):
        directory_frame = Frame(self.master, padx=10, pady=10)
        directory_frame.grid(row=0, column=0, padx=300, pady=(20, 10))
        report_frame = LabelFrame(
            self.master, text="Weekly/monthly Report",
            padx=50, pady=10)
        report_frame.grid(row=3, column=0, padx=300)
        session_frame = LabelFrame(
            self.master, text="Session Report",
            padx=98, pady=10)
        session_frame.grid(row=4, column=0, padx=300)

        self.create_directory_frame(directory_frame)
        self.create_report_frame(report_frame)
        self.create_session_frame(session_frame)

    def create_directory_frame(self, directory_frame):
        Label(directory_frame, text="Save report at: ").grid(row=0, column=0)
        self.directory_label = Label(
            directory_frame, text=self.report_directory)
        self.directory_label.grid(row=0, column=1)
        Button(directory_frame, text="Change",
               command=self.get_directory).grid(row=0, column=2)

    def create_report_frame(self, report_frame):
        Label(report_frame, text="Period: ").grid(row=1, column=0)
        self.period_frame = Frame(report_frame)
        self.period_frame.grid(row=1, column=1)
        Radiobutton(self.period_frame, text="Weekly (7 days)",
                    variable=self.date_range, value=7).grid(row=0, column=0)
        Radiobutton(self.period_frame, text="Monthly (30 days)",
                    variable=self.date_range, value=30).grid(row=0, column=1)
        Label(report_frame, text="End date: ").grid(row=2, column=0)
        self.end_date = DateEntry(report_frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=10)
        self.end_date.grid(row=2, column=1)
        Button(report_frame, text="Generate Report",
               command=self.generate_report).grid(row=3, column=1)

    def create_session_frame(self, session_frame):
        Label(session_frame, text="Session length: ").grid(row=0, column=0)
        s_length = [(f"{i} hours", i) for i in range(1, 9)]
        self.session_slider = Slider(
            time_value=s_length, parent=session_frame)
        self.session_slider.grid(row=0, column=1)
        Button(session_frame, text="Generate Report",
               command=self.generate_session_report).grid(row=1, column=1)

    def generate_session_report(self):
        end_date = round_time(datetime.now())
        start_date = end_date - \
            timedelta(hours=self.session_slider.get_value())
        _unix_start = time.mktime(start_date.timetuple())
        _unix_end = time.mktime(end_date.timetuple())

        df = self.get_time_df(_unix_start, _unix_end)
        session_df = self.get_session_df(df, start_date, end_date)
        self.generate_session_area_plot(session_df)
        # print(session_df)

    def generate_report(self):
        end_date = self.end_date.get_date() + timedelta(days=1)  # Until end of day
        start_date = end_date - timedelta(days=self.date_range.get())
        _unix_start = time.mktime(start_date.timetuple())
        _unix_end = time.mktime(end_date.timetuple())

        df = self.get_time_df(_unix_start, _unix_end)
        activity_df = self.get_activity_df(df)
        _date_range_str = "weekly" if self.date_range.get() == 7 else "monthly"

        self.generate_emotion_mean_plot(df, _date_range_str)
        self.generate_activity_plot(activity_df)
        self.generate_pos_neg_plot(activity_df)
        self.generate_emotion_pie_plot(activity_df)

        self.generate_pdf(_date_range_str, start_date,
                          self.end_date.get_date(), activity_df)

        messagebox.showinfo("Emotracker", "Finished!")

    def get_emotion_time(self, activity_df, emotion):
        emotion_time = activity_df[emotion].sum()
        hours, mins = get_hours_minutes(timedelta(minutes=emotion_time))
        return "{0} hour{2} {1} minute{3}".format(hours, mins, "s" if hours > 1 else "", "s" if mins > 1 else "")

    def generate_emotion_time(self, activity_df):
        t = []
        for emotion in ["Positive", "Negative", "Neutral"]:
            t.append(self.get_emotion_time(activity_df, emotion))
        emotion_time_df = pd.DataFrame(
            data=t, index=["Positive", "Negative", "Neutral"], columns=["time_per_day"])
        return emotion_time_df

    def get_time_df(self, unix_start, unix_end):
        df = self.db.get_record_range(unix_start, unix_end)
        df["DateTime"] = df.apply(
            lambda row: datetime.fromtimestamp(row["TimeStamp"]), axis=1)
        df["TimeOfDay"] = df.apply(lambda row: row["DateTime"].hour, axis=1)
        return df

    def get_session_df(self, df, start_date, end_date):
        _date_range = pd.date_range(
            start_date, end_date, closed="right", freq="1min")
        session_df = pd.DataFrame(_date_range, columns=["DateTime"])
        session_df = session_df.merge(df, how="left", on="DateTime").fillna(0)
        session_df.drop(["TimeStamp", "TimeOfDay", "None"], axis=1)

        session_df = add_emotion_states(session_df)
        session_df["Total"] = session_df.apply(get_emotion, axis=1,
                                               emotions=["Positive", "Negative", "Neutral"])
        session_df = add_emotion_states_percent(session_df)
        return session_df

    def get_activity_df(self, df):
        activity_df = df.groupby("TimeOfDay").mean().drop(
            ["TimeStamp"], axis=1)
        activity_df["Total"] = activity_df.sum(axis=1)

        activity_df["Activity"] = activity_df.apply(
            get_activity, axis=1, mood="None")

        activity_df = add_emotion_states(activity_df)

        activity_df = activity_df.reindex(
            pd.RangeIndex(24)).fillna(0)
        return activity_df

    def generate_session_area_plot(self, df):
        self.session_area_plot_name = "session_area_plot.png"
        ax = df.plot.area(x="DateTime",
                          y=["Positive_percent", "Negative_percent",
                             "Neutral_percent"],
                          color=['green', 'red', '#04d8b2'])
        plt.ylim(0, 100)
        plt.legend(loc='upper left')

        plt.savefig(os.path.join(
            self.report_directory, self.session_area_plot_name))

    def generate_emotion_mean_plot(self, df, date_range_str):
        self.emotion_mean_plot_name = f"{date_range_str}_mean.png"

        emo_df = pd.DataFrame(
            data=list(df.columns)[1:-3],
            columns=["Emotion"])
        emo_df["Sum"] = emo_df.apply(
            lambda row: df[row["Emotion"]].mean(), axis=1)

        ax = emo_df.plot.bar(
            x="Emotion",
            y="Sum",
            title=f"{date_range_str} mean",
            figsize=(10, 5),
            legend=False,
            fontsize=8)
        ax.set_xlabel("Emotion", fontsize=12)
        ax.set_ylabel("Average Time/Min", fontsize=12)
        plt.savefig(os.path.join(
            self.report_directory, self.emotion_mean_plot_name))

    def generate_activity_plot(self, df):
        self.activity_plot_name = "daily_activity_plot.png"
        df.plot.bar(
            y="Activity",
            title="Activity Time in Day",
            xlabel="Time",
            ylabel="Percentage",
            legend=False
        )
        plt.savefig(os.path.join(
            self.report_directory, self.activity_plot_name))

    def generate_pos_neg_plot(self, df):
        self.pos_neg_plot_name = "positive_vs_negative.png"
        df.plot(
            y=["Positive", "Negative"],
            kind="bar",
            title="Positive vs Negative",
            xlabel="Time",
            ylabel="s/min"
        )
        plt.savefig(os.path.join(
            self.report_directory, self.pos_neg_plot_name))

    def generate_emotion_pie_plot(self, df):
        self.emotion_pie_plot_name = "emotion_pie.png"
        df[["Positive", "Negative", "Neutral"]].sum().plot(
            kind="pie",
            title="Emotion Proportions",
            ylabel="",
            labeldistance=1.1,
            autopct=lambda p: '{:.2f}%'.format(p)
        )
        plt.savefig(os.path.join(self.report_directory,
                                 self.emotion_pie_plot_name))

    def get_screen_time(self, activity_df):
        up_time = activity_df["Total"].sum(
        ) - activity_df["None"].sum()
        hours, mins = get_hours_minutes(timedelta(minutes=up_time))
        return "You are on screen on average {0} hour{2} {1} minute{3} per day.".format(hours, mins, "s" if hours > 1 else "", "s" if mins > 1 else "")

    def print_emotion_table(self, pdf, activity_df):
        emotion_time_df = self.generate_emotion_time(activity_df)

        pdf.set_font(family='arial', style='B', size=12)
        pdf.set_x(60)
        pdf.cell(40, 10, '', 1, 0, 'C')
        pdf.cell(40, 10, 'Time per day', 1, 1, 'C')
        for row in emotion_time_df.itertuples():
            pdf.set_x(60)
            pdf.set_font('arial', 'B', 12)
            pdf.cell(40, 10, '%s' % (row.Index), 1, 0, 'C')
            pdf.set_font('arial', '', 12)
            pdf.cell(40, 10, '%s' % (row.time_per_day), 1, 1, 'C')
        pdf.cell(w=0, h=10, ln=1)

    def generate_pdf(self, date_range_str, start_date, end_date, activity_df):
        start_date_str = start_date.strftime("%m/%d/%Y")
        end_date_str = end_date.strftime("%m/%d/%Y")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_xy(0, 0)
        pdf.set_font(family='arial', style='B', size=12)
        pdf.cell(60)
        pdf.cell(
            w=75, h=30, txt=f"Emotion {date_range_str} report {start_date_str} - {end_date_str}",
            border=0, ln=1, align='C')
        pdf.set_font(family='arial', size=12)
        pdf.set_x(20)
        pdf.cell(20, 20, self.get_screen_time(activity_df), 0, 1)
        pdf.image(os.path.join(self.report_directory, self.activity_plot_name),
                  x=30, y=None, w=140, h=0, type='', link='')
        pdf.image(os.path.join(self.report_directory, self.pos_neg_plot_name),
                  x=30, y=None, w=140, h=0, type='', link='')

        pdf.add_page()
        pdf.set_xy(0, 20)
        self.print_emotion_table(pdf, activity_df)
        pdf.image(os.path.join(self.report_directory, self.emotion_pie_plot_name),
                  x=30, y=None, w=140, h=0, type='', link='')
        pdf.image(os.path.join(self.report_directory, self.emotion_mean_plot_name),
                  x=20, y=None, w=160, h=0, type='', link='')
        pdf.output(
            f'{date_range_str}_report_{start_date.strftime("%m%d%Y")}_{end_date.strftime("%m%d%Y")}.pdf', 'F')

        os.remove(os.path.join(self.report_directory,
                               self.emotion_mean_plot_name))
        os.remove(os.path.join(self.report_directory, self.activity_plot_name))
        os.remove(os.path.join(self.report_directory, self.pos_neg_plot_name))
        os.remove(os.path.join(self.report_directory,
                               self.emotion_pie_plot_name))
