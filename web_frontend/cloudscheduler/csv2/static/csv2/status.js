/* Timestamp of last refresh*/
var date = Date.now();

/* Add event listeners once page loads*/
function initialize(){
	addEventListeners("plottable");
}


/* Add click events to table elements and range selection*/
function addEventListeners(className) {
	var inputList = document.getElementsByClassName(className);
		var i;
		var list_length = inputList.length;
		for (i = 0; i < list_length; i++){
			inputList[i].addEventListener('click', function(){
				if(className == 'plottable'){
					this.classList.toggle("plotted");
					togglePlot(this);
				}else selectRange(this);
			});
		}
}


/* Range selection dropdown*/
function dropDown(){
	if(!document.getElementById("myDropdown").classList.contains("show"))
		document.getElementById("range-select").classList.add("selected");
	else document.getElementById("range-select").classList.remove("selected");
	document.getElementById("myDropdown").classList.toggle("show");
}


/* Change time range for plot*/
function selectRange(range){
	const curr_range = document.getElementsByClassName("range-btn");
	curr_range[0].innerHTML = range.innerHTML+'<span class="space"></span><span class="caret"></span>';
	const dropdowns = document.getElementsByClassName("selected");
	var l = dropdowns.length;
	for (var i = 0; i < l; i++) {
		dropdowns[0].classList.remove('selected');
	}
	range.classList.toggle("selected");
	/* Calculate new range*/
	var to = new Date();
	var from = new Date();
	var multiple = 60000;
	if(range.parentElement.classList.contains("days")) multiple = 86400000;
	to.setTime(date-(range.dataset.to*multiple))
	to = to.getTime();
	from.setTime(date-(range.dataset.from*multiple));
	from = from.getTime();
	/* Update traces with new range*/
	if((date-from) > 604800000 && !(TSPlot.traces[0].x[0] < from)){
		var traces = TSPlot.traces;
		var newdata = {
			y: [],
			x: []
		};
		var index = [];
		var query = createQuery(traces[0].name, from, TSPlot.traces[0].x[0], true);
		
		/* Create string of queries for db*/
		for (var i = 1; i < traces.length; i++){
			query += ';'
			query += createQuery(traces[i].name, from, TSPlot.traces[0].x[0], true)
		}
		if(window.location.pathname == "/cloud/status/") var newpath = "plot";
		else var newpath = "/cloud/status/plot";
		const csrftoken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
		fetch(newpath,{
			method: 'POST',
			headers: {'Accept': 'application/json', 'X-CSRFToken': csrftoken},
			credentials: 'same-origin',
			body: query,
			}
		)
		.then(function(response){
			/* Check response status code*/
			if(response.ok){
				return response.json();
			}throw new Error('Could not update range :( HTTP response not was not OK -> '+response.status)
		})
		.then(function(data){
			/* Parse response into trace object. Add null values between points where no data
		   	   exists for more than 70s to show gaps in plot*/
			var nonewpoints = 0;
			for(var i = 0; i < traces.length; i++){
				/* Skip trace if no new data exists*/
				if(!(typeof data.results[i].series !== 'undefined')){
					nonewpoints ++;
					break;
				}
				index.push(i);
				var responsedata = data.results[i].series;
				if((typeof (data.results[i].series) !== 'undefined')){
					responsedata = data.results[i].series[0].values;
				}
				var arrays = parseData(responsedata);
				var newarrayx = arrays[0];
				var newarrayy = arrays[1];
				/* Add nulls to beginning and end of new data*/
				newarrayx.unshift(newarrayx[0]-15000);
				newarrayy.unshift(null);
				newarrayx.push(newarrayx[newarrayx.length-1]+15000);
				newarrayy.push(null);
				newdata.y.push(newarrayy);
				newdata.x.push(newarrayx);
			}
			/* If there were no new points for all traces*/
			if(nonewpoints == index.length) return data;
			else{
				Plotly.prependTraces('plotly-TS', newdata, index);
				return updateTraces(newdata, index);
			}
		})
		.then(function(response){
			/* Update plot range*/
			TSPlot.layout.xaxis.range = [from, to];
			Plotly.relayout('plotly-TS', TSPlot.layout);
		})
		.catch(error => console.warn(error));
	}
	else{
		/* Only update plot range*/
		TSPlot.layout.xaxis.range = [from, to];
		Plotly.relayout('plotly-TS', TSPlot.layout);
	}
}


/* Close the range dropdown menu*/
window.onclick = function(event) {
	if (!event.target.matches('.range-btn') && document.getElementsByClassName("dropdown-content")[0].classList.contains('show')) {
		var dropdowns = document.getElementsByClassName("dropdown-content");
		var k = false;
		var i;
		for (i = 0; i < dropdowns.length; i++) {
			var openDropdown = dropdowns[i];
			if (openDropdown.classList.contains('show')) {
				openDropdown.classList.remove('show');
				k = true;
	      		}
    		}
		if(k == true){
			document.getElementsByClassName("range-btn")[0].classList.remove("selected");
		}
	}
}


/* Toggle traces, show plot*/
function togglePlot(trace){
	if(TSPlot.showing == true){
		/* Check if trace is already plotted*/
		var x;
		var index = -1;
		for(x = 0; x < TSPlot.traces.length; x++){
			if (TSPlot.traces[x].name == trace.dataset.path){
				index = x;
				break;
			}
		}
		if(index != -1){
			if(TSPlot.traces.length == 1) {
				TSPlot.hide();
			}else{
				Plotly.deleteTraces('plotly-TS', index);
				/* Store plotted traces for refresh*/
				var trace_array = [];
				for(var y = 0; y < TSPlot.traces.length; y++){
					trace_array.push(TSPlot.traces[y].name)
				}
				sessionStorage.setItem("traces", JSON.stringify(trace_array));
			}
		}else{
			/* Plot new trace*/
			getTraceData(trace, true);
		}
	}else{
		document.getElementById("loader").style.display = 'inline-block';		
		/* Create plot*/
		TSPlot.show();
		getTraceData(trace, false);
	}
}


/* Construct query for db*/
function createQuery(trace, from, to, showing){
	const line = trace.split(" ");
	var query = `SELECT time,value FROM `;
	var services = false;
	/* If trace is for service status*/
	if(line.length == 1){
		services = true;
		var measurement = line[0];
		query += `"${measurement}"`;
	}
	const group = line[0];
	if(line.length == 3){
		var cloud = line[1];
		var measurement = line[2];
		query += `"${measurement}" WHERE "cloud"='${cloud}' AND "group"='${group}'`;
	}else if(!services){
		var measurement = line[1];
		query += `"${measurement}" WHERE "group"='${group}'`;
	}
	/* If requesting newest 30s of data*/
	if (to == 0){
		if(!services) query += ` AND time >= ${from}ms`;
		else query += ` WHERE time >= ${from}ms`;
	/* Default request is last 7 days*/
	}else if (showing == false || (date-from) <= 604800000){
		if(!services) query += ` AND time >= ${date-604800000}ms`;
		else query += ` WHERE time >= ${date-604800000}ms`;
	}else{
		/* Check if trace is already plotted*/
		var index = -1;
		for(var x = 0; x < TSPlot.traces.length; x++){
			if (TSPlot.traces[x].name == trace){
				index = x;
				break;
			}
		}
		/* If trace is already plotted*/
		if(index != -1){
			if(!services){
				if(from > TSPlot.layout.xaxis.range[0])	query += ` AND time >= ${TSPlot.layout.xaxis.range[0]}ms AND time < ${to}ms`;
				else query += ` AND time >= ${from}ms AND time < ${to}ms`;
			}else{
				if(from > TSPlot.layout.xaxis.range[0])	query += ` WHERE time >= ${TSPlot.layout.xaxis.range[0]}ms AND time < ${to}ms`;
				else query += ` WHERE time >= ${from}ms AND time < ${to}ms`;
			}
		}else{
			if(!services){
				if(from > TSPlot.layout.xaxis.range[0])	query += ` AND time >= ${TSPlot.layout.xaxis.range[0]}ms AND time < ${date}ms`;
				else query += ` AND time >= ${from}ms AND time < ${date}ms`;
			}else{
				if(from > TSPlot.layout.xaxis.range[0])	query += ` WHERE time >= ${TSPlot.layout.xaxis.range[0]}ms AND time < ${date}ms`;
				else query += ` WHERE time >= ${from}ms AND time < ${date}ms`;
			}
		}
	}
	return query;
}


/* Parse data and add null values between points where no data exists for more than 70s to show gaps in plot.
   Returns new x and y arrays to be added to a trace*/
function parseData(responsedata){
	/* Variables to keep track of where to insert nulls*/
	var addindex = [];
	var addtime = [];
	const unpackData = (arr, index) => {
		var newarr = arr.map((x, ind) => {
			if(index == 0 && ind < arr.length-1){
				/* If gap between two timestamps is > 45s*/
				if((Math.abs(arr[ind+1][index] - arr[ind][index])) > 45000){
					addtime.push(arr[ind][index] + 15000);
					addindex.push(ind+1);
				}
			}
			return x[index];
		});
		return newarr
	}
	/* Add null timestamps and values to x and y arrays*/
	var newarrayx = unpackData(responsedata, 0);
	for(var f = 0; f<addindex.length; f++){
		newarrayx.splice(addindex[f]+f,0,addtime[f]);
	}
	var newarrayy = unpackData(responsedata, 1);
	for(var f = 0; f<addindex.length; f++){
		newarrayy.splice(addindex[f]+f,0,null);
	}
	return [newarrayx, newarrayy];
}


/* Fetch trace data from db and add to plot*/
function getTraceData(trace, showing){
	if(window.location.pathname == "/cloud/status/") var newpath = "plot";
	else var newpath = "/cloud/status/plot";
	var nullvalues = [];
	if(showing == true) query = createQuery(trace.dataset.path, TSPlot.traces[0].x[0], date, showing);
	else query = createQuery(trace.dataset.path, 3600, date, showing);
	const csrftoken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
	fetch(newpath,{
		method: 'POST',
		headers: {'Accept': 'application/json', 'X-CSRFToken': csrftoken},
		credentials: 'same-origin',
		body: query,
		}
	)
	.then(function(response){
		/* Check response status code*/
		if(response.ok){
			return response.json();
		}throw new Error('Could not get trace :( HTTP response not was not OK -> '+response.status);
	})
	.then(function(data){
		/* Parse response into trace object.*/
		const newarrays = parseData(data.results[0].series[0].values);
	    	const newtrace = {
			mode: 'lines',
			name: trace.dataset.path,
			x: newarrays[0],
			y: newarrays[1]
		}
		/* If plot is showing, add trace to plot, otherwise create plot with trace*/
		if(showing == true){
			Plotly.relayout('plotly-TS', TSPlot.layout);
			return Plotly.addTraces('plotly-TS', newtrace);
		}else return TSPlot.initialize(newtrace);
	}).then(function(data){
		if(showing == true){
			/* Store plotted traces for refresh*/
			var trace_array = [];
			for(var y = 0; y < TSPlot.traces.length; y++){
				trace_array.push(TSPlot.traces[y].name)
			}
			sessionStorage.setItem("traces", JSON.stringify(trace_array));
		}
	})
	.catch(error => {
		console.warn(error);
		if(showing == false) TSPlot.hide();		
	});
}


/* On refresh, check for plotted traces to update colour in status tables*/
function checkForPlottedTraces(){
	if (typeof (Storage) !== "undefined"){
		if(sessionStorage.length != 0){
			var plotted_traces = JSON.parse(sessionStorage.getItem("traces"));
			for(var x = 0; x < plotted_traces.length; x++){
				var stat = document.querySelectorAll('td[data-path="'+plotted_traces[x]+'"]');
				stat[0].classList.toggle("plotted");
			}
		}
	}
}


/* Refresh plot every 30 seconds with new data from db*/
function refresh_plot() {
	/* Only refresh if plot is showing*/
	if(TSPlot.showing == true){
		var traces = TSPlot.traces;
		var newdata = {
			y: [],
			x: []
		};
		var index = [];
		var query = createQuery(traces[0].name, traces[0].x[traces[0].x.length-1], 0, true)
		index.push(0);
		/* Create string of queries for db*/
		for (var i = 1; i < traces.length; i++){
			index.push(i);
			query += ';'
			query += createQuery(traces[i].name, traces[i].x[traces[i].x.length-1], 0, true);
		}
		if(window.location.pathname == "/cloud/status/") var newpath = "plot";
		else var newpath = "/cloud/status/plot";
		const csrftoken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
		fetch(newpath,{
			method: 'POST',
			headers: {'Accept': 'application/json', 'X-CSRFToken': csrftoken},
			credentials: 'same-origin',
			body: query,
			}
		)
		.then(function(response){
			/* Check response status code*/
			if(response.ok){
				return response.json();
			}throw new Error('Could not update trace(s) :( HTTP response not was not OK -> '+response.status)
		})
		.then(function(data){
			/* Parse response into arrays of new points*/
			var new_points = true;
			for(var k = 0; k < traces.length; k++){
				if(!(typeof (data.results[k]) !== 'undefined') || !(typeof (data.results[k].series) !== 'undefined')){
					console.log("new_points == false");
					new_points = false;
					break;
				}
				const responsedata = data.results[k].series[0].values;
				const unpackData = (arr, index) => {
					var newarr = arr.map(x => x[index]);
					return newarr
				}
				var updatetrace = {
					x: unpackData(responsedata, 0),
					y: unpackData(responsedata, 1)
				}
			
				/* Update new data for traces*/
				newdata.y.push(unpackData(responsedata, 1));
				newdata.x.push(unpackData(responsedata, 0));
			}
			/* Update plot with new data*/
			if(new_points == true) return updateTraces(newdata, index);
			else return;
		})
		.catch(error => console.warn(error));					
	}
}


/* Update plot traces with most recent data points and new range*/
function updateTraces(newdata, index){
	/* If last plotted data point was 55s or more ago, insert null to show break in plot*/
	for(var k = 0; k < index.length; k++){
		var len = TSPlot.traces[k].x.length -1;
		if(TSPlot.traces[k].x[len] < (newdata.x[k][0]-55000)){
			console.log(newdata);
			newdata.x[k].unshift(newdata.x[k][0] - 1000);
			newdata.y[k].unshift(null);
			console.log(newdata);
		}
	}
	Plotly.extendTraces('plotly-TS', newdata, index);
	/* Only update range if if looking at last 12 hours or less*/
	if(TSPlot.layout.xaxis.range[1] >= date && (date - TSPlot.layout.xaxis.range[0]) <= 43200000){
		date = Date.now();
		var diff = date - TSPlot.layout.xaxis.range[1];
		TSPlot.layout.xaxis.range[1] = date; 
		TSPlot.layout.xaxis.range[0] += diff;
		Plotly.relayout('plotly-TS', TSPlot.layout);
	}
}


/* Plot Object*/
var TSPlot = {
	layout: {
		yaxis: {
			rangemode: "tozero",
		},
		xaxis: {
			type: 'date',
		},
		margin: {
			l: 50,
			r: 50,
			t: 40,
			b: 40
		},
	},

	showing: false,
	traces: [],

	/* Create new plot with trace in div*/
	initialize: function(trace) {
		TSPlot.layout.xaxis.range = [date-3600000, date];
		TSPlot.traces = [trace];		
		Plotly.newPlot('plotly-TS', TSPlot.traces, TSPlot.layout, {responsive: true, displayModeBar: false});
		var traces = [];
		traces.push(trace.name);
		sessionStorage.setItem("traces", JSON.stringify(traces));
	},

	/* Hide plot*/
	hide: function() {
		TSPlot.showing = false;
		TSPlot.traces = [];
		Plotly.purge('plotly-TS');
		document.getElementById("plot").style.display = 'none';
		const curr_range = document.getElementsByClassName("range-btn");
		curr_range[0].innerHTML = 'Last 1 hour<span class="space"></span><span class="caret"></span>';
		/* Remove indication of plotted traces*/
		var list = document.getElementsByClassName('plotted');
		var init_length = list.length;
		for (var i = 0; i < init_length; i++) {
			var value = list[0];
			value.classList.remove('plotted');
		}
		sessionStorage.clear();
		const dropdowns = document.getElementsByClassName("selected");
		var l = dropdowns.length;
		for (var i = 0; i < l; i++) {
			dropdowns[0].classList.remove('selected');
		}
		document.querySelectorAll('a[data-from="60"]')[0].classList.add('selected');
	},

	/* Show plot*/
	show: function(){
		TSPlot.showing = true;
		document.getElementById("plot").style.display = 'block';
	}

}//TSPlot
