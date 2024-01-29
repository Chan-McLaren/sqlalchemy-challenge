# Import the dependencies.
from flask import Flask, jsonify
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn = engine.connect()
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
# home page route
@app.route("/")
def welcome():
    print("Server received request for 'Home' page...")
    return (
        f"Welcome to the Climate Analysis API!<br/>"
        f"Available Routes:<br/>"

        f"To view the past year of precipitation data to date"
        f"/api/v1.0/precipitation<br/>"
    
        f"To look up a station"
        f"/api/v1.0/stations<br/>"

        f"To see a record of daily temperature of the most active station"
        f"/api/v1.0/tobs<br/>"

        f"To see the min, max, and avg temp for a given start date enter in YYYY-MM-DD format"
        f"/api/v1.0/start<br/>"

        f"To see the min, max, and avg temp for a given start and end date enter in YYYY-MM-DD format"
        f"/api/v1.0/start/end"
    )
# precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'Precipitation' page...")
    
    # Calculate the date 1 year ago from the last data point in the database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= prev_year).all()
    
    # create a dictionary from the row data and append to a list of precipitation
    precipitation = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict[date] = prcp
        precipitation.append(precip_dict)

    # return the json list of precipitation
    return jsonify(precipitation)

# stations route
@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'Stations' page...")

    # Query all stations
    results = session.query(station.station,station.name).distinct().all()

    # Convert list of tuples into normal list
    stations = []
    for station, name in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        stations.append(station_dict)

    # Return the json list of stations
    return jsonify(stations)

# tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'Tobs' page...")

    # Calculate the date 1 year ago from the last data point in the database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the primary station for all tobs from the last year
    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
        filter(measurement.date >= prev_year).all().\
        group_by(measurement.date).all()

    # Convert list of tuples into normal list
    temperatures = []
    for date, tobs in results:
        temperature_dict = {}
        temperature_dict[date] = tobs
        temperatures.append(temperature_dict)

    # Return the json list of tobs
    return jsonify(tobs)

# start route
@app.route("/api/v1.0/<start>")
def start(start):
    print("Server received request for 'Start' page...")

    # Query the minimum, average, and maximum temperatures for a given start date
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).group_by(measurement.date).all()

    # Convert list of tuples into normal list
    start_temps = []
    for min, avg, max in results:
        start_temp_dict = {}
        start_temp_dict["min"] = min
        start_temp_dict["avg"] = avg
        start_temp_dict["max"] = max
        start_temps.append(start_temp_dict)

    # Return the json list of temps
    return jsonify(start_temps)

# start/end route
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    print("Server received request for 'Start/End' page...")
    
    # Query the minimum, average, and maximum temperatures for a given start and end date
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).group_by(measurement.date).all()

    # Convert list of tuples into normal list
    start_end_temps = []
    for min, avg, max in results:
        start_end_temp_dict = {}
        start_end_temp_dict["min"] = min
        start_end_temp_dict["avg"] = avg
        start_end_temp_dict["max"] = max
        start_end_temps.append(start_end_temp_dict)

    # Return the json list of temps
    return jsonify(start_end_temps)

if __name__ == '__main__':
    app.run(debug=True)