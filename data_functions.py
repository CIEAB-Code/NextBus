import requests
import json
from datetime import datetime
from nextbus import tfl_db, bus_col

# Variables
url = r"https://api.tfl.gov.uk/StopPoint/490009333W/arrivals"
db_exists = False

# Default home page data table data
headings = ("Station Name", "Bus Arrival Time", "Destination")
empty_data = (
    ("-", "-", "-"),
    ("-", "-", "-"),
    ("-", "-", "-")
)

# Default data page table data.
data_headings = ["Date\nSearched", "Time\nSearched", "Station\nStart", "Arrival\nTime", "Destination"]
empty_list = [['-', '-', '-', '-', '-']]

# Set up dictionary for data on home page
bus_info_dict = {"Station Name": [],
                 "Bus Arrival Time": [],
                 "Destination": []}


def save_to_database():
    """Saves bus route information from API call to a local mongodb database."""
    # Get the current time
    date = datetime.now()
    date_name = date.strftime("%d/%m/%Y")
    date_time = date.strftime("%H:%M")

    # Check if database collection already exists
    global db_exists
    if not db_exists:
        col_name = 'bus_data'
        if col_name in tfl_db.list_collection_names():
            db_exists = True
        else:
            # creates new database collection if it doesn't already exist.
            bus_info_dict['date_searched'] = [date_name]
            bus_info_dict['time_searched'] = [date_time]
            bus_col.insert_one(bus_info_dict)

    # Add data to database collection
    if db_exists:
        found = tfl_db.bus_data.find()

        bus_time = bus_info_dict['Bus Arrival Time']
        station_name = bus_info_dict['Station Name']
        destination = bus_info_dict['Destination']

        tfl_db.bus_data.update({u'_id': found[0]['_id']},
                               {'$push': {'Station Name': station_name[0]}})
        tfl_db.bus_data.update({u'_id': found[0]['_id']},
                               {'$push': {'Bus Arrival Time': bus_time[0]}})
        tfl_db.bus_data.update({u'_id': found[0]['_id']},
                               {'$push': {'Destination': destination[0]}})
        tfl_db.bus_data.update({u'_id': found[0]['_id']},
                               {'$push': {'date_searched': date_name}})
        tfl_db.bus_data.update({u'_id': found[0]['_id']},
                               {'$push': {'time_searched': date_time}})


def get_bus_info():
    """Function that calls TFL API and loads data into dictionary"""
    response = requests.get(url)
    # Checks for a good response from request
    if response.status_code == 200:
        data = response.text
        parsed = json.loads(data)
        rows = []

        # Update rows.
        for i, result in enumerate(parsed):
            rows.append((parsed[i]["stationName"], parsed[i]["expectedArrival"][11:16], parsed[i]["destinationName"]))

        # Orders results in order of earliest arrival time
        if len(rows) >= 1:
            time = rows[0][1]
            datemask = "%H:%M"
            earliest_time = datetime.strptime(time, datemask)
            for i, row in enumerate(rows):
                new_time = datetime.strptime(row[1], datemask)
                if new_time < earliest_time:
                    earliest_time = new_time
                    rows.insert(0, rows[i])
                    del rows[i + 1]
                else:
                    continue

            # update dictionary
            bus_info_dict["Station Name"] = [rows[0][0]]
            bus_info_dict["Bus Arrival Time"] = [rows[0][1]]
            bus_info_dict["Destination"] = [rows[0][2]]
            return rows

        else:
            return None


def query_data():
    """Retrieves data from mongodb database and saves to a list."""

    all_data = []

    # TO DO: Make except block specific.
    try:
        # Retrieve data from database.
        col_headings = ['date_searched', 'time_searched', 'Station Name', 'Bus Arrival Time', 'Destination']
        for title in col_headings:
            for date in bus_col.find({}, {'_id': 0, title: 1}):
                all_data.append(date[title])

        # Format retrieved data
        ordered_data = []
        complete_row = []
        for i, result in enumerate(all_data[0]):
            for a, heading in enumerate(data_headings):
                complete_row.append(all_data[a][i])
            ordered_data.append(complete_row)
            complete_row = []

        ordered_data.reverse()
        return ordered_data

    except:
        print("Error getting data from database")
        return None


def filter_morning(all_data):
    """ Filters results from database and returns data collected between 05:00 and 11:59am"""
    if all_data:
        datemask = "%H:%M"
        morning_start = datetime.strptime("05:00", datemask)
        morning_end = datetime.strptime("11:59", datemask)
        morning_rows = [row for row in all_data if morning_start <= datetime.strptime(row[1], datemask) <= morning_end]
        return morning_rows
    else:
        return None


def filter_afternoon(all_data):
    """ Filters results from database and returns data collected between 12:00 and 16:59am"""
    if all_data:
        datemask = "%H:%M"
        after_start = datetime.strptime("12:00", datemask)
        after_end = datetime.strptime("16:59", datemask)
        after_rows = [row for row in all_data if after_start <= datetime.strptime(row[1], datemask) <= after_end]
        return after_rows
    else:
        return None


def filter_evening(all_data):
    """ Filters results from database and returns data collected between 17:00 and 23:59am"""
    if all_data:
        datemask = "%H:%M"
        eve_start = datetime.strptime("17:00", datemask)
        eve_end = datetime.strptime("23:59", datemask)
        eve_rows = [row for row in all_data if eve_start <= datetime.strptime(row[1], datemask) <= eve_end]
        return eve_rows
    else:
        return None
