from tkinter import *
import os
from datetime import datetime, timedelta
from tkcalendar import DateEntry


class Report:
    def __init__(self, master):
        self.master = master
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
        pass
