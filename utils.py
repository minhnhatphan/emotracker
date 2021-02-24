from datetime import datetime, timedelta
import pandas as pd


def get_hours_minutes(td):
    return td.seconds//3600, (td.seconds//60) % 60


def round_time(dt=None, roundTo=60):
    """Round a datetime object to any time lapse in seconds
    dt : datetime.datetime object, default now.
    roundTo : Closest number of seconds to round to, default 1 minute.
    Author: Thierry Husson 2012 - Use it as you want but don't blame me.
    """
    if dt == None:
        dt = datetime.now()
    seconds = (dt.replace(tzinfo=None) - dt.min).seconds
    rounding = (seconds+roundTo/2) // roundTo * roundTo
    return dt + timedelta(0, rounding-seconds, -dt.microsecond)


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


def add_emotion_states(df):
    df["Negative"] = df.apply(get_emotion, axis=1,
                              emotions=["Angry", "Disgust", "Fear", "Sad"])
    df["Positive"] = df.apply(
        get_emotion, axis=1, emotions=["Happy"])
    df["Neutral"] = df.apply(
        get_emotion, axis=1, emotions=["Neutral", "Surprise"])

    return df


def get_emotion_percent(row, emotion):
    if row["Total"] != 0:
        return (row[emotion]/row["Total"])*100

    return 0 if emotion == "Neutral" else 0


def add_emotion_states_percent(df):
    df["Negative_percent"] = df.apply(
        get_emotion_percent, axis=1, emotion="Negative")
    df["Positive_percent"] = df.apply(
        get_emotion_percent, axis=1, emotion="Positive")
    df["Neutral_percent"] = df.apply(
        get_emotion_percent, axis=1, emotion="Neutral")

    return df
