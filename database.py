import sqlite3
import pandas as pd


class Database:
    def __init__(self, db_dir="../databases/emotracker.db"):
        self.db_dir = db_dir
        self.tableName = "records"
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        with sqlite3.connect(self.db_dir) as conn:
            c = conn.cursor()
            sql = '''
                CREATE TABLE IF NOT EXISTS {} (
                    TimeStamp INTEGER PRIMARY KEY,
                    Angry REAL NOT NULL,
                    Disgust REAL NOT NULL,
                    Fear REAL NOT NULL,
                    Happy REAL NOT NULL,
                    Sad REAL NOT NULL,
                    Surprise REAL NOT NULL,
                    Neutral REAL NOT NULL,
                    None REAL NOT NULL
                )
            '''.format(self.tableName)
            c.execute(sql)
            conn.commit()

    def insert_row(self, timestamp, counter):
        for i in range(len(counter)):
            counter[i] = round(counter[i], 2)

        with sqlite3.connect(self.db_dir) as conn:
            c = conn.cursor()
            sql = '''
                INSERT INTO {} 
                VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {})
            '''.format(self.tableName, timestamp, *counter)
            c.execute(sql)
            conn.commit()

    def get_all_record(self):
        rows = []
        with sqlite3.connect(self.db_dir) as conn:
            c = conn.cursor()
            sql = '''
                SELECT * FROM {}
            '''.format(self.tableName)
            c.execute(sql)
            rows = c.fetchall()
        return pd.DataFrame(rows, columns=["TimeStamp", "Angry", "Disgust",
                                           "Fear", "Happy", "Sad", "Surprise",
                                           "Neutral", "None"])

    def get_record_range(self, unix_start, unix_end):
        rows = []
        with sqlite3.connect(self.db_dir) as conn:
            c = conn.cursor()
            sql = '''
                SELECT * FROM {}
                WHERE TimeStamp BETWEEN {} AND {}
            '''.format(self.tableName, unix_start, unix_end)

            c.execute(sql)
            rows = c.fetchall()
        return pd.DataFrame(rows, columns=["TimeStamp", "Angry", "Disgust",
                                           "Fear", "Happy", "Sad", "Surprise",
                                           "Neutral", "None"])


if __name__ == "__main__":
    db = Database()
    from datetime import datetime, timedelta
    import time
    import matplotlib.pyplot as plt
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    time_end = today
    time_start = today - timedelta(days=7)
    unix_start = time.mktime(time_start.timetuple())
    unix_end = time.mktime(time_end.timetuple())

    df = db.get_record_range(unix_start, unix_end)
    emo_df = pd.DataFrame(
        data=list(df.columns)[1:-1],
        columns=["Emotion"])
    emo_df["Sum"] = emo_df.apply(lambda row: df[row["Emotion"]].mean(), axis=1)

    ax = emo_df.plot.bar(
        x="Emotion",
        y="Sum",
        title="Weekly mean",
        figsize=(10, 5),
        legend=False,
        fontsize=8)
    ax.set_xlabel("Emotion", fontsize=12)
    ax.set_ylabel("Average Time/Min", fontsize=12)
    plt.show()
    print(emo_df)
