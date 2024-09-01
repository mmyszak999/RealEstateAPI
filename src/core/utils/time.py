import datetime
import random


def get_current_time():
    return datetime.datetime.now()


def set_employment_date_for_factory():
    return get_current_time() - datetime.timedelta(weeks=random.randint(4, 55))


def generate_random_date(
    start_date: datetime.date, end_date: datetime.date
) -> datetime.date:

    delta_days = (end_date - start_date).days
    random_days = random.randint(0, delta_days)

    return start_date + datetime.timedelta(days=random_days)
