import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# last_year ='>=2016-08-23'

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
    #    f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp_start<br/>"
        f"/api/v1.0/temp_start/end"

    )


@app.route("/api/v1.0/precipitation")
def precipitation():
     """Return the JSON representation of your dictionary."""
    # Query all precipitation
     results = session.query(Measurement.date, Measurement.prcp).\
                order_by(Measurement.date).all()

    # Convert the query results to a Dictionary using date as the key and prcp as the value.
     all_precipitation=[]
     for precip in results:
        precip_dict = {}
        precip_dict["date"] = precip.date
        precip_dict["prcp"] = precip.prcp
        all_precipitation.append(precip_dict)
        
     return jsonify(all_precipitation)



# /api/v1.0/stations
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Measurement.station, func.count(Measurement.station)).\
                group_by(Measurement.station).\
                order_by(func.count(Measurement.station).desc()).all()

    # Convert the query results to a list of stations inside Dicitonary
    all_stations=[]
    for row in results:
        station_dict = {}
        station_dict["station"] = row[0]
        station_dict["count"] = row[1]
        all_stations.append(station_dict)

    return jsonify(all_stations)


# /api/v1.0/tobs
# Return a JSON list of Temperature Observations (tobs) for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    last_date=session.query(Measurement.date).\
        order_by(Measurement.date.desc()).first()
    for date in last_date:
        split_last_date=date.split('-')
    
    last_year=int(split_last_date[0])
    last_month=int(split_last_date[1])
    last_day=int(split_last_date[2])
    
    query_date = dt.date(last_year, last_month, last_day) - dt.timedelta(days=365)
    
    results = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date>=query_date).\
                order_by(Measurement.date).all()

    # Convert the query results to a Dictionary using date as the key and tobs as the value.
    last_12months_tobs=[]
    for row in results:
        tobs_dict = {}
        tobs_dict["date"] = row.date
        tobs_dict["station"] = row.tobs
        last_12months_tobs.append(tobs_dict)

    return jsonify(last_12months_tobs)

@app.route("/api/v1.0/<start_date>")
def calc_temps_start(start_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
    Returns:
        TMIN, TAVE, and TMAX"""
    
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    # Convert the query results to a Dictionary using date as the key and tobs as the value.
    calc_tobs=[]
    for row in results:
        calc_tobs_dict = {}
        calc_tobs_dict["TMIN"] = row[0]
        calc_tobs_dict["TAVG"] = row[1]
        calc_tobs_dict["TMAX"] = row[2]
        calc_tobs.append(calc_tobs_dict)

    return jsonify(calc_tobs)

@app.route("/api/v1.0/<start_date>/<end_date>")
def calc_temps_start_end(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()
    
    # Convert the query results to a Dictionary using date as the key and tobs as the value.
    calc_tobs=[]
    for row in results:
        calc_tobs_dict = {}
        calc_tobs_dict["TMIN"] = row[0]
        calc_tobs_dict["TAVG"] = row[1]
        calc_tobs_dict["TMAX"] = row[2]
        calc_tobs.append(calc_tobs_dict)

    return jsonify(calc_tobs)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)