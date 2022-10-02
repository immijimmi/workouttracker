from managedstate import State

from os import chdir
from datetime import date, datetime, timedelta
from json import loads

"""
Provides a summary of the total time logged using the workout tracker's timer per week, for previous weeks
"""

NUMBER_OF_WEEKS = 52


def get_week_start(start_value: date) -> date:
    # Coalesce datetime to date to retrieve weekday
    start_value = date(year=start_value.year, month=start_value.month, day=start_value.day)

    return start_value - timedelta(days=start_value.weekday())


filename = "data.json"

chdir("..")
with open(filename, "r") as file:
    tracker_state = State(loads(file.read()))

    stopwatch_entries = tracker_state.get()["stopwatch"]["saved"]

current_week_start = get_week_start(datetime.now())
week_starts = []
for week_index in range(NUMBER_OF_WEEKS):
    week_starts.append(current_week_start)
    current_week_start -= timedelta(days=7)

total_times = [timedelta(0) for week_start in week_starts]
for entry in stopwatch_entries:
    entry_inserted_datetime = datetime.strptime(entry["inserted_at"][0:10], "%Y-%m-%d").date()
    for week_start_index, week_start in enumerate(week_starts):
        if entry_inserted_datetime >= week_start:
            entry_duration_timedelta = timedelta(seconds=entry["duration_s"])
            total_times[week_start_index] += entry_duration_timedelta
            break

week_starts.reverse()
total_times.reverse()
for week_start_index, week_start in enumerate(week_starts):
    total_time = total_times[week_start_index]

    print(f"WC {week_start}: {total_time}")

input("\nEnter to quit: ")
