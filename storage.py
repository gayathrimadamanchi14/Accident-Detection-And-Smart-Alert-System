import csv
import os

FILE_NAME = "history.csv"

def save_record(date_time, latitude, longitude,):

    file_exists = os.path.isfile(FILE_NAME)

    with open(FILE_NAME, "a", newline="") as file:

        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "Date & Time",
                "Latitude",
                "Longitude"
            ])

        writer.writerow([
            date_time,
            latitude,
            longitude
        ])