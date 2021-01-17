from flask import Flask, render_template
import requests
import json
from datetime import datetime
import pymongo

# Set up database connection
client = pymongo.MongoClient('localhost', 27017)
tfl_db = client['tfl_database']
bus_col = tfl_db['bus_data']

# Instantiating Flask class
app = Flask(__name__)

# Variables
error_message = "No information available."
url = r"https://api.tfl.gov.uk/StopPoint/490009333W/arrivals"
db_exists = False

# Default home page data table data
headings = ("Station Name", "Bus Arrival Time", "Destination")
empty_data = (
    ("-", "-", "-"),
    ("-", "-", "-"),
    ("-", "-", "-")
)

# Set up dictionary for data on home page
bus_info_dict = {"Station Name": [],
                 "Bus Arrival Time": [],
                 "Destination": []}


@app.route('/')
def home():
    """Renders home page of web application"""
    rows = get_bus_info()
    # if 'rows' returns data then this is passed to the html table, else the default empty data is passed
    if rows:
        save_to_database()
        return render_template('home_page.html', data_info=rows, headings=headings)
    else:
        return render_template('home_page.html', data_info=empty_data, headings=headings, info=error_message)


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
            result = bus_col.insert_one(bus_info_dict)
            print(result)

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
        for i in range(len(parsed)):
            rows.append((parsed[i]["stationName"], parsed[i]["expectedArrival"][11:16], parsed[i]["destinationName"]))

        # Orders results in order of earliest arrival time
        if len(rows) >= 1:
            time = rows[0][1]
            datemask = "%H:%M"
            earliest_time = datetime.strptime(time, datemask)
            for row in range(len(rows)):
                new_time = datetime.strptime(rows[row][1], datemask)
                if new_time < earliest_time:
                    earliest_time = new_time
                    rows.insert(0, rows[row])
                    del rows[row + 1]
                else:
                    continue

            # update dictionary
            bus_info_dict["Station Name"] = [rows[0][0]]
            bus_info_dict["Bus Arrival Time"] = [rows[0][1]]
            bus_info_dict["Destination"] = [rows[0][2]]
            return rows

        else:
            return None

    ### PAGE 2 ###


def query_data(data_headings):
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
        for i in range(len(all_data[0])):
            for a in range(len(data_headings)):
                complete_row.append(all_data[a][i])
            ordered_data.append(complete_row)
            complete_row = []

        ordered_data.reverse()
        return ordered_data

    except:
        print("Error getting data from database")
        return None


def filter_morning(all_data):
    if all_data:
        datemask = "%H:%M"
        morning_start = datetime.strptime("05:00", datemask)
        morning_end = datetime.strptime("11:59", datemask)
        morning_rows = [row for row in all_data if morning_start <= datetime.strptime(row[1], datemask) <= morning_end]
        return morning_rows
    else:
        return None


def filter_afternoon(all_data):
    if all_data:
        datemask = "%H:%M"
        after_start = datetime.strptime("12:00", datemask)
        after_end = datetime.strptime("16:59", datemask)
        after_rows = [row for row in all_data if after_start <= datetime.strptime(row[1], datemask) <= after_end]
        return after_rows
    else:
        return None


def filter_evening(all_data):
    if all_data:
        datemask = "%H:%M"
        eve_start = datetime.strptime("17:00", datemask)
        eve_end = datetime.strptime("23:59", datemask)
        eve_rows = [row for row in all_data if eve_start <= datetime.strptime(row[1], datemask) <= eve_end]
        return eve_rows
    else:
        return None


@app.route('/data/')
def data_page():
    data_headings = ["Date Searched", "Time Searched", "Station Start", "Arrival Time", "Destination"]
    ordered_data = query_data(data_headings)
    empty_list = [['-', '-', '-', '-', '-']]
    error = "There was an issue connecting with the database."
    if ordered_data:
        return render_template('data.html', all_data=ordered_data, headings=data_headings, error="")
    else:
        return render_template('data.html', all_data=empty_list, headings=data_headings, error=error)


@app.route('/morning/')
def morning_page():
    data_headings = ["Date Searched", "Time Searched", "Station Start", "Arrival Time", "Destination"]
    ordered_data = query_data(data_headings)
    empty_list = [['-', '-', '-', '-', '-']]
    error = "There was an issue connecting with the database."
    morning_rows = filter_morning(ordered_data)
    if morning_rows:
        return render_template('data.html', all_data=morning_rows, headings=data_headings, error="")
    else:
        return render_template('data.html', all_data=empty_list, headings=data_headings, error=error)


@app.route('/afternoon/')
def afternoon_page():
    data_headings = ["Date Searched", "Time Searched", "Station Start", "Arrival Time", "Destination"]
    ordered_data = query_data(data_headings)
    empty_list = [['-', '-', '-', '-', '-']]
    error = "There was an issue connecting with the database."
    after_rows = filter_afternoon(ordered_data)
    if after_rows:
        return render_template('data.html', all_data=after_rows, headings=data_headings, error="")
    else:
        return render_template('data.html', all_data=empty_list, headings=data_headings, error=error)


@app.route('/evening/')
def evening_page():
    data_headings = ["Date Searched", "Time Searched", "Station Start", "Arrival Time", "Destination"]
    ordered_data = query_data(data_headings)
    empty_list = [['-', '-', '-', '-', '-']]
    error = "There was an issue connecting with the database."
    eve_rows = filter_evening(ordered_data)
    if eve_rows:
        return render_template('data.html', all_data=eve_rows, headings=data_headings, error="")
    else:
        return render_template('data.html', all_data=empty_list, headings=data_headings, error=error)


if __name__ == '__main__':
    app.run()
