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
COLLECTION_TRIP = 'trip'
FIELDS_TRIP = {'date': True, 'tripduration': True, 'startlong': True,
 'startlat': True, 'endlong': True, 'endlat': True, 'birthdate': True,
  'gender': True, 'precipitation': True, 'snowdepth': True, 'avgtemp': True,
   'avgwind': True, '_id': False}

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/citibike/trip")
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

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5000, debug=True)