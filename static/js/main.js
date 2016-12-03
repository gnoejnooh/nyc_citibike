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
		if (d.precipitation > 0.3) return "Heavy Rain";
		else if (d.precipitation >= 0.1 && d.precipitation <= 0.3) return "Moderate Rain";
		else if (d.precipitation > 0 && d.precipitation < 0.1) return "Light Rain";
		else return "No Rain";
	});

	var dateGroup = dateDim.group();
	var rainGroup = rainDim.group();
	// var userByDate = dateDim.group().reduceSum(function(d) { return d.count; });

	var minDate = dateDim.bottom(1)[0]["date"];
	var maxDate = dateDim.top(1)[0]["date"];
	// var minDate = new Date(2013,5,1);
	// var maxDate = new Date(2016,5,30);
	// var minDate = "2013-07-01T00:00:00";
	// var maxDate = "2016-06-30T23:59:59";

	var timeChart = dc.barChart("#time-chart");
	var rainChart = dc.pieChart("#rain-chart");

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
		.height(240)
		.radius(100)
		.dimension(rainDim)
		.group(rainGroup)
		.title(function(d){return d.value;});


    // .on('pretransition', function(chart) {
    //     chart.selectAll('text.pie-slice').text(function(d) {
    //         return d.data.key + ' ' + dc.utils.printSingleValue((d.endAngle - d.startAngle) / (2*Math.PI) * 100) + '%';

	dc.renderAll();
};