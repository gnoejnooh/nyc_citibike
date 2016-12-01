from flask import Flask
from flask import render_template
from pymongo import MongoClient
import json
from bson import json_util
from bson.json_util import dumps

app = Flask(__name__)

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'citibike'
COLLECTION_TRIP = 'trips'
COLLECTION_WTR = 'weather'
FIELDS_TRIP = {'tripduration': True, 'starttime': True, 'stoptime': True,
 'usertype': True, 'birth year': True, 'gender': True, '_id': False}
FIELDS_WTR = {'DATE': True, 'PRCP': True, 'SNWD': True, 'SNOW': True,
 'TMAX': True, 'TMIN': True, 'AWND': True, '_id': False}

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/citibike/trips")
def citibike_trips():
	connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
	collection = connection[DBS_NAME][COLLECTION_TRIP]
	trips = collection.find(projection=FIELDS_TRIP)
	json_trips = []
	for trip in trips:
		json_trips.append(trip)
	json_trips = json.dumps(json_trips, default=json_util.default)
	connection.close()
	return json_trips

@app.route("/citibike/weather")
def citibike_weather():
	connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
	collection = connection[DBS_NAME][COLLECTION_WTR]
	wtrs = collection.find(projection=FIELDS_WTR)
	json_wtrs = []
	for wtr in wtrs:
		json_wtrs.append(wtr)
	json_wtrs = json.dumps(json_wtrs, default=json_util.default)
	connection.close()
	return json_wtrs

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5000, debug=True)