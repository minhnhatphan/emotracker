from datetime import datetime, timedelta


def get_hours_minutes(td):
    return td.seconds//3600, (td.seconds//60) % 60
