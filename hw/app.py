import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
M = Base.classes.measurement
S = Base.classes.station

session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# /api/v1.0/precipitation
# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    maxDate = dt.date(2017, 8 ,23)
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    precipitation = session.query(M.date, M.prcp).\
    filter(M.date > year_ago).\
    order_by(M.date).all()
    
    precip = {date: prcp for date, prcp in year_ago}
    
    return jsonify(precip)

# /api/v1.0/stations
# Return a JSON list of stations from the dataset.

@app.route('/api/v1.0/stations')
def stations():

    stations_all = session.query(S.station).all()

    return jsonify(stations_all)

# /api/v1.0/tobs
# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route('/api/v1.0/tobs') 
def tobs():  
    maxDate = dt.date(2017, 8 ,23)
    year_ago = maxDate - dt.timedelta(days=365)

    lastyear = (session.query(M.tobs)
                .filter(M.station == 'USC00519281')
                .filter(M.date <= maxDate)
                .filter(M.date >= year_ago)
                .order_by(M.tobs).all())
    
    return jsonify(lastyear)

# /api/v1.0/<start> and /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

@app.route('/api/v1.0/<start>') 
def start(start=None):

    #start = Measurement.date <= '2010-01-01'
    #end = Measurement.date >= '2017-08-23'

    highest_temp = (session.query(M.tobs).filter(M.date.between(start, '2017-08-23')).all())
    
    temp_df = pd.DataFrame(highest_temp)

    tavg = temp_df["tobs"].mean()
    tmax = temp_df["tobs"].max()
    tmin = temp_df["tobs"].min()
    
    return jsonify(tavg, tmax, tmin)

# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route('/api/v1.0/<start>/<end>') 
def startend(start=None, end=None):

    #start = Measurement.date <= '2010-01-01'
    #end = Measurement.date >= '2017-08-23'

    highest_temp = (session.query(M.tobs).filter(M.date.between(start, end)).all())
    
    temp_df = pd.DataFrame(highest_temp)

    tavg = temp_df["tobs"].mean()
    tmax = temp_df["tobs"].max()
    tmin = temp_df["tobs"].min()
    
    return jsonify(tavg, tmax, tmin)

if __name__ == '__main__':
    app.run(debug=True)

