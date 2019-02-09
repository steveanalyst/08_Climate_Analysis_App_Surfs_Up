
# import dependences
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station= Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################




# Define what to do when a user hits the index route
@app.route("/")
def home():
    
    return """
    <html>
    <h1>Welcome to Hawaii Weather API</h1>
    <ol>
        <li>
        Return last year precipitations:
        <br>
        <a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a>
        </li>
    
        <li>
        Return a JSON list of stations from the dataset: 
        <br>
        <a href="/api/v1.0/stations">/api/v1.0/stations</a>
        </li>
    
        <li>
        Return a JSON list of Temperature Observations (tobs) for the previous year:
        <br>
        <a href="/api/v1.0/tobs">/api/v1.0/tobs</a>
        </li>
    
        <li>
        Return a JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided:
        <br>
        You can replace default "Date" to your query date in format: YYYY-mm-dd . 
        <br>
        Date range: 2010-01-01 to 2017-08-23
        <br>
        <a href="/api/v1.0/2017-08-23">/api/v1.0/2017-08-23</a>
        </li>
    
        <li>
        Return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive:
        <br>
        You can replace default "Date" to your query date in format: YYYY-mm-dd . 
        <br>
        Date range: 2010-01-01 to 2017-08-23
        <br>
        <a href="/api/v1.0/2010-01-01/2017-08-23">/api/v1.0/2010-01-01/2017-08-23</a>
        </li>
        <br>
    </ol>
    </html>
    """


@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Query to get the max or latest date
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    max_date = max_date[0]

    # Calculate the last 12 month beginning date
    year_ago_date = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=365)
    year_ago_date.strftime('%Y-%m-%d')

    # Perform a query to retrieve the data and precipitation scores
    prcp_12_month = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago_date).\
       group_by(Measurement.date).all()

    # Convert tuple list into dictionary
    precipitation_dict = dict(prcp_12_month)
    
    #Close session for next call
    session.close()
    return jsonify(precipitation_dict)




@app.route("/api/v1.0/stations")
def stations(): 
    
    # Query stations
    stations =  session.query(Measurement.station).group_by(Measurement.station).all()

    # Convert list of tuples into list
    #stationlist = [x[0] for x in stations]
    stationlist=list(stations)

    #Close session for next call
    session.close()

    return jsonify(stationlist)



@app.route("/api/v1.0/tobs")
def tobs(): 
    
    # Query to get the max or latest date
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    max_date = max_date[0]

    # Calculate the last 12 month beginning date
    year_ago_date = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=365)
    year_ago_date.strftime('%Y-%m-%d')

    # Perform a query to retrieve the data and precipitation scores
    prcp_12_month = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago_date).\
       group_by(Measurement.date).all()

    # Convert list of tuples into normal list
    tobs_list = list(prcp_12_month)

    #Close session for next call
    session.close()

    return jsonify(tobs_list)



@app.route("/api/v1.0/<start>")
def start(start=None):

    start_date = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), \
        func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    start_date_list=list(start_date)

    #Close session for next call
    session.close()

    return jsonify(start_date_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    calcs_temps = session.query(*sel).filter(func.strftime('%Y-%m-%d', Measurement.date).between(start, end)).one()

    #Close session for next call
    session.close()

    return (
		f"Temperature between {start} to {end} are:<br>"
		f"Min Temp: {round(calcs_temps[0],1)}<br>"
		f"Mean Temp: {round(calcs_temps[1],1)}<br>"
		f"Max Temp: {round(calcs_temps[2],1)}<br>"
	)



if __name__ == "__main__":
    app.run(debug=False)