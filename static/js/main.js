queue()
	// .defer(d3.json, "/citibike/trips")
	.defer(d3.json, "/citibike/count")
	// .defer(d3.json, "/citibike/weather")
	.await(makeGraphs);

function makeGraphs(error, countJson) {

	// var tripData = tripsJson;
	var countData = countJson;
	// var weatherData = weatherJson;
	var dateFormat = d3.time.format("%Y-%m-%dT%H:%M:%S");
	// tripData.forEach(function(d) {
	// 	d["tripduration"] = +d["tripduration"];
	// 	d["starttime"] = dateFormat.parse(d["starttime"]);
	// 	d["stoptime"] = dateFormat.parse(d["stoptime"]);
	// });
	countData.forEach(function(d) {
		d["tripdate"] = dateFormat.parse(d["tripdate"]);
		d["count"] = +d["count"];
	});
	// weatherData.forEach(function(d) {
	// 	d["DATE"] = dateFormat.parse(d["DATE"]);
	// 	d["PRCP"] = +d["PRCP"];
	// 	d["SNWD"] = +d["SNWD"]
	// 	d["SNOW"] = +d["SNOW"]
	// 	d["TMAX"] = +d["TMAX"]
	// 	d["TMIN"] = +d["TMIN"]
	// 	d["AWND"] = +d["AWND"]
	// });

	// var cf_trip = crossfilter(tripData);
	var cf_count = crossfilter(countData);
	// var cf_weather = crossfilter(weatherData);

	// var dateDim = cf_trip.dimension(function(d) { return d["starttime"]; });
	var dateDim = cf_count.dimension(function(d) { return d["tripdate"] });

	var userByDate = dateDim.group().reduceSum(function(d) { return d.count; });

	// var minDate = dateDim.bottom(1)[0]["tripdate"];
	// var maxDate = dateDim.top(1)[0]["tripdate"];
	var minDate = new Date(2013,5,1);
	var maxDate = new Date(2016,5,30);
	// var minDate = "2013-07-01T00:00:00";
	// var maxDate = "2016-06-30T23:59:59";

	var timeGraph = dc.barChart("#time-graph");

	timeGraph
		.width(400)
		.height(160)
		.margins({top: 10, right: 50, bottom: 30, left: 50})
		.dimension(dateDim)
		.group(userByDate)
		.transitionDuration(500)
		.x(d3.time.scale().domain([minDate, maxDate]))
		.elasticY(true)
		.xAxisLabel("Year")
		.yAxis().ticks(4);

	dc.renderAll();
};