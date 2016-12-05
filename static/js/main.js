queue()
	.defer(d3.json, "/citibike/trip")
	.defer(d3.json, "/static/geojson/nyc-zip-code.json")
	.await(makeGraphs);

function makeGraphs(error, tripJson, nycJson) {

	var tripData = tripJson;
	var dateFormat = d3.time.format("%m/%d/%y");
	
	tripData.forEach(function(d) {
		d["date"] = dateFormat.parse(d["date"]);
		d["tripduration"] = +d["tripduration"];
		d["birthdate"] = +d["birthdate"];
		d["start"] = +d["start"];
		d["gender"] = +d["gender"];
		d["precipitation"] = +d["precipitation"];
		d["snowdepth"] = +d["snowdepth"];
		d["avgtemp"] = +d["avgtemp"];
		d["avgwind"] = +d["avgwind"];
	});
	
	var ndx = crossfilter(tripData);

	//Demension
	var dateDim = ndx.dimension(function(d) { return d["date"]; });
	var rainDim = ndx.dimension(function(d) {
		if (d.precipitation > 0.3) return "Heavy";
		else if (d.precipitation >= 0.1 && d.precipitation <= 0.3) return "Moderate";
		else if (d.precipitation > 0 && d.precipitation < 0.1) return "Light";
		else return "None";
	});
	var snowDim = ndx.dimension(function(d) {
		if (d.snowdepth > 1.6) return "Heavy";
		else if (d.snowdepth > 0.2 && d.snowdepth <= 1.6) return "Moderate";
		else if (d.snowdepth > 0 && d.snowdepth <= 0.2) return "Light";
		else return "None";
	});
	var genderDim = ndx.dimension(function(d) {
		if (d.gender == 1) { return "Male"; }
		else { return "Female"; }
	});
	var birthDim = ndx.dimension(function(d) {
		if (d.birthdate >= 1987) return "14-25";
		else if (d.birthdate >= 1981 && d.birthdate <= 1986) return "26-31";
		else if (d.birthdate >= 1964 && d.birthdate <= 1980) return "32-48";
		else return "49-67 and Above";
	});
	var nycDim = ndx.dimension(function(d) { return d["start"]; });
	
	var projection = d3.geo.conicConformal()
      .parallels([40 + 40 / 60, 41 + 2 / 60])
      .scale(240000)
      .rotate([74, -40 - 45 / 60]);

	//Group
	var dateGroup = dateDim.group();
	var rainGroup = rainDim.group();
	var snowGroup = snowDim.group();
	var tempGroup = ndx.groupAll().reduce(
		function (p, v) { ++p.n; p.tot += v.avgtemp; return p; },
		function (p, v) { --p.n; p.tot -= v.avgtemp; return p; },
		function () { return {n:0,tot:0}; }
	);
	var windGroup = ndx.groupAll().reduce(
		function (p, v) { ++p.n; p.tot += v.avgwind; return p; },
		function (p, v) { --p.n; p.tot -= v.avgwind; return p; },
		function () { return {n:0,tot:0}; }
	);
	var average = function(d) { return d.n ? d.tot / d.n : 0; };
	var genderGroup = genderDim.group().reduceSum(function(d){ return 100; });
	var birthGroup = birthDim.group().reduceSum(function(d){ return 100; });
	var nycGroup = nycDim.group().reduceSum(function(d){ return d["tripduration"]; });

	var minDate = dateDim.bottom(1)[0]["date"];
	var maxDate = dateDim.top(1)[0]["date"];

	var timeChart = dc.barChart("#time-chart");
	var rainChart = dc.pieChart("#rain-chart");
	var snowChart = dc.pieChart("#snow-chart");
	var tempChart = dc.numberDisplay("#temp-chart");
	var windChart = dc.numberDisplay("#wind-chart");
	var genderChart = dc.rowChart("#gender-chart");
	var birthChart = dc.rowChart("#birthdate-chart");
	var nycChart = dc.geoChoroplethChart("#nyc-chart");

	timeChart
		.width(1200)
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

	tempChart
		.valueAccessor(average)
		.html({
        temp:"<span>%number</span> F"
      })
		.group(tempGroup);

	windChart
		.formatNumber(d3.format(".2f"))
		.valueAccessor(average)
		.html({
        wind:"<span>%number</span> mph"
      })
		.group(windGroup);

	genderChart
		.width(480)
		.dimension(genderDim)
		.group(genderGroup)
		.xAxis().ticks(4);

	birthChart
		.width(480)
		.dimension(birthDim)
		.group(birthGroup)
		.xAxis().ticks(4);

	nycChart
		.width(380)
		.height(837)
		.dimension(nycDim)
		.group(nycGroup)
		.overlayGeoJson(nycJson["features"], "station", function(d) { return d.properties["ZIP"]; })
		.projection(projection.translate([-140,430]))
		.title(function (p) {
			return "Zipcode: " + p["key"]
					+ "\n"
					+ "Total Trip Duration: " + Math.round(p["value"]);
		});

	dc.renderAll();
	// nycChart.render();
};