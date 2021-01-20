from data_functions import *
from flask import Flask, render_template
import pymongo

# Set up database connection
client = pymongo.MongoClient('localhost', 27017)
tfl_db = client['tfl_database']
bus_col = tfl_db['bus_data']

# Instantiating Flask class
app = Flask(__name__)

# Error messages
data_error = "No information available at this time."
error_message = "No information available."


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


@app.route('/data/')
def data_page():
    ordered_data = query_data()
    if ordered_data:
        return render_template('data.html', all_data=ordered_data, headings=data_headings, error="")
    else:
        return render_template('data.html', all_data=empty_list, headings=data_headings, error=data_error)


@app.route('/morning/')
def morning_page():
    ordered_data = query_data()
    morning_rows = filter_morning(ordered_data)
    if morning_rows and len(morning_rows) > 0:
        print(len(morning_rows))
        return render_template('data.html', all_data=morning_rows, headings=data_headings, error="")
    else:
        return render_template('data.html', all_data=empty_list, headings=data_headings, error=data_error)


@app.route('/afternoon/')
def afternoon_page():
    ordered_data = query_data()
    after_rows = filter_afternoon(ordered_data)
    if after_rows:
        return render_template('data.html', all_data=after_rows, headings=data_headings, error="")
    else:
        return render_template('data.html', all_data=empty_list, headings=data_headings, error=data_error)


@app.route('/evening/')
def evening_page():
    ordered_data = query_data()
    eve_rows = filter_evening(ordered_data)
    if eve_rows:
        return render_template('data.html', all_data=eve_rows, headings=data_headings, error="")
    else:
        return render_template('data.html', all_data=empty_list, headings=data_headings, error=data_error)


if __name__ == '__main__':
    app.run()
