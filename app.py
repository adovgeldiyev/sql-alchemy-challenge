import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

#Database setup
engine_path="../Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{engine_path}")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine,reflect=True)
# Save reference to the table
Base.classes.keys()
Measurement = Base.classes.measurement
Station = Base.classes.station
#session=Session(engine)
session=Session(engine)
#Flask setup
app=Flask(__name__)

#Flask routes
@app.route("/")
def welcome():
    '''All available routes'''
    return (
        f"Avaliable routes:<br/>"
        f'<br/>'
        f"/api/v1.0/precipitation<br/>"
        f'<br/>'
        f'Rain total<br/>'
        f'<br/>'
        f'/api/v1.0/stations<br/>'
        f'<br/>'
        f'Station numbers<br/>'
        f'<br/>'
        f'/api/v1.0/tobs<br/>'
        f'<br/>'
        f'Temperature observations start point<br/>'
        f'<br/>'
        f'When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date<br/>'
        f'<br/>'
        f'/api/v1.0/start<br/>'
        f'<br/>'
        f'Temperature observations end point<br/>'
        f'<br/>'
        f'/api/v1.0/start/end<br/>'
        f'<br/>'
        f'When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive<br/>'

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = dt.date(2017,8,23)-dt.timedelta(days=365)
    scores = session.query(Measurement.date,Measurement.prcp).\
        filter(Measurement.date>year_ago).\
            order_by(Measurement.date).all()
    rain_list = []
    for r in scores:
        d={}
        d['date']=scores[0]
        d['prcp']=scores[1]
        rain_list.append(d)

    return jsonify(rain_list)

@app.route("/api/v1.0/stations")
def stations():
    stations_query = session.query(Station.name, Station.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    return jsonify(stations.to_dict())

@app.route("/api/v1.0/tobs")
def tobs():
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = dt.date(2017,8,23)-dt.timedelta(days=365)
    temp = session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.date>year_ago).\
            order_by(Measurement.date).all()
    temp_list = []
    for t in temp:
        t_d={}
        d['date'] = temp[0]
        d['tobs'] = temp[1]
        temp_list.append(t_d)
    
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
def begin(start):
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end =  dt.date(2017, 8, 23)
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

@app.route("/api/v1.0/<start>/<end>")
def finish(start,end):
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end = end_date-last_year
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)


if __name__ == '__main__':
    app.run(debug=True)
