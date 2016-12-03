queue()
	.defer(d3.json, "/citibike/trip")
	.await(makeGraphs);

function makeGraphs(error, tripJson) {

	var tripData = tripJson;
	var dateFormat = d3.time.format("%m/%d/%y");
	
	tripData.forEach(function(d) {
		d["date"] = dateFormat.parse(d["date"]);
		d["tripduration"] = +d["tripduration"];
		d["startlong"] = +d["startlong"];
		d["startlat"] = +d["startlat"];
		d["endlong"] = +d["endlong"];
		d["endlat"] = +d["endlat"];
		d["birthdate"] = +d["birthdate"];
		d["gender"] = +d["gender"];
		d["precipitation"] = +d["precipitation"];
		d["snowdepth"] = +d["snowdepth"];
		d["avgtemp"] = +d["avgtemp"];
		d["avgwind"] = +d["avgwind"];
	});
	
	var cf_trip = crossfilter(tripData);

	//Demension
	var dateDim = cf_trip.dimension(function(d) { return d["date"]; });
	var rainDim = cf_trip.dimension(function(d) {
		if (d.precipitation > 0.3) return "Heavy";
		else if (d.precipitation >= 0.1 && d.precipitation <= 0.3) return "Moderate";
		else if (d.precipitation > 0 && d.precipitation < 0.1) return "Light";
		else return "None";
	});
	var snowDim = cf_trip.dimension(function(d) {
		if (d.snowdepth > 1.6) return "Heavy";
		else if (d.snowdepth > 0.2 && d.snowdepth <= 1.6) return "Moderate";
		else if (d.snowdepth > 0 && d.snowdepth <= 0.2) return "Light";
		else return "None";
	});

	//Group
	var dateGroup = dateDim.group();
	var rainGroup = rainDim.group();
	var snowGroup = snowDim.group();

	var minDate = dateDim.bottom(1)[0]["date"];
	var maxDate = dateDim.top(1)[0]["date"];

	var timeChart = dc.barChart("#time-chart");
	var rainChart = dc.pieChart("#rain-chart");
	var snowChart = dc.pieChart("#snow-chart");

	timeChart
		.width(860)
		.height(320)
		.margins({top: 10, right: 50, bottom: 30, left: 50})
		.dimension(dateDim)
		.group(dateGroup)
		.transitionDuration(500)
		.x(d3.time.scale().domain([minDate, maxDate]))
		.elasticY(true)
		.xAxisLabel("Year")
		.yAxisLabel('User (in thousands)')
		.yAxis().ticks(4);

	rainChart
		.ordinalColors(["#56B2EA","#E064CD","#F8B700","#78CC00","#7B71C5"])
		.width(220)
		.radius(100)
		.innerRadius(60)
		.dimension(rainDim)
		.group(rainGroup)
		.renderLabel(false)
		.legend(dc.legend().x(90).y(65).gap(5));

	snowChart
		.ordinalColors(["#56B2EA","#E064CD","#F8B700","#78CC00","#7B71C5"])
		.width(220)
		.radius(100)
		.innerRadius(60)
		.dimension(snowDim)
		.group(snowGroup)
		.renderLabel(false)
		.legend(dc.legend().x(90).y(75).gap(5));

	dc.renderAll();
};