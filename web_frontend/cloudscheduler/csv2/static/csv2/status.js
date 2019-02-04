var date = Date.now();

/* Add click events to table elements and range selection*/
function addEventListeners(className) {
	var inputList = document.getElementsByClassName(className);
		var i;
		for (i = 0; i < inputList.length; i++){
			inputList[i].addEventListener('click', function(){
				if(className == 'plottable'){
					this.classList.toggle("plotted");
					togglePlot(this);
				}else selectRange(this);
			});
		}
}

function dropDown(){
	document.getElementById("range-select").classList.toggle("selected");
	document.getElementById("myDropdown").classList.toggle("show");
}

/* Change time range for plot*/
function selectRange(range){
	const curr_range = document.getElementsByClassName("range-value");
	curr_range[0].innerHTML = range.innerHTML;
	const dropdowns = document.getElementsByClassName("range");
	for (var i = 0; i < dropdowns.length; i++) {
		if (dropdowns[i].classList.contains('selected')) {
			dropdowns[i].classList.remove('selected');
      		}
	}
	range.classList.toggle("selected");
	const curr = Date.now();
	var to = new Date();
	var from = new Date();
	var multiple = 60000;
	if(range.parentElement.classList.contains("days")) multiple = 86400000;
	to.setTime(curr-(range.dataset.to*multiple))
	to = to.getTime();
	from.setTime(curr-(range.dataset.from*multiple));
	from = from.getTime();
	TSPlot.layout.xaxis.range = [from, to];
	Plotly.relayout('plotly-TS', TSPlot.layout);
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
			document.getElementById("range-select").classList.toggle("selected");
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
			}
		}else{
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
function createQuery(trace,time){
	const line = trace.split(" ");
	const group = line[0];
	var query = `SELECT time,value FROM `
	if(line.length == 3){
		var cloud = line[1];
		var measurement = line[2];
		query += `"${measurement}" WHERE "cloud"='${cloud}' AND "group"='${group}'`;
	}else{
		var measurement = line[1];
		query += `"${measurement}" WHERE "group"='${group}'`;
	}if (time == true){
		query += `AND time > ${date}ms`;
	}
	return query;
}

/* Fetch trace data from db and add to plot*/
function getTraceData(trace, showing){
	query = createQuery(trace.dataset.path, false);
	const csrftoken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
	fetch('cloud/status/plot',{
		method: 'POST',
		headers: {'Accept': 'application/json', 'X-CSRFToken': csrftoken},
		credentials: 'same-origin',
		body: query,
		}
	)
	.then(function(response){
		return response.json();
	})
	.then(function(data){
		const responsedata = data.results[0].series[0].values;
		const unpackData = (arr, index) => {
			var newarr = arr.map(x => x[index]);
			return newarr
		}
	    	const newtrace = {
			type: 'scatter',
			name: trace.dataset.path,
			x: unpackData(responsedata, 0),
			y: unpackData(responsedata, 1)
		}
		if(showing == true) return Plotly.addTraces('plotly-TS', newtrace);
		else return TSPlot.initialize(newtrace);
	})
	.catch(error => console.log('Error:', error));
	
}

/* Refresh plot every 30 seconds with new data from db if looking at last hour >
var plot_timer;
function refresh_plot() {
	plot_timer = setTimeout(function() {
		console.log("to "+TSPlot.layout.xaxis.range[1]);
		console.log("from "+TSPlot.layout.xaxis.range[0]);
		console.log(TSPlot.layout.xaxis.range[1] - TSPlot.layout.xaxis.range[0]);
		if((TSPlot.layout.xaxis.range[1] - TSPlot.layout.xaxis.range[0]) <= 3600000 && TSPlot.layout.xaxis.range[1] == date){
			console.log("yes");
			var traces = TSPlot.traces;
			var newdata = {
				y: [],
				x: []
			};
			var index = [];
			for (var i = 0; i < traces.length; i++){
				index.push(i);
				var query = createQuery(traces[i].name,true)
				const csrftoken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
				fetch('cloud/status/plot',{
					method: 'POST',
					headers: {'Accept': 'application/json', 'X-CSRFToken': csrftoken},
					credentials: 'same-origin',
					body: query,
					}
				)
				.then(function(response){
					return response.json();
				})
				.then(function(data){
					const responsedata = data.results[0].series[0].values;
					const unpackData = (arr, index) => {
						var newarr = arr.map(x => x[index]);
						return newarr
					}
					var updatetrace = {
						x: unpackData(responsedata, 0),
						y: unpackData(responsedata, 1)
					}
					/* Update trace
					newdata.y.push(unpackData(responsedata, 1));
					newdata.x.push(unpackData(responsedata, 0));*/
					/* Update plot range*/
					//var ready = false;
					//if(i == traces.length -1) ready = true;
				/*	return updateTraces(newdata, index);
				})
				.catch(error => console.log('Error:', error));
			}
		}		
		refresh_plot();
	},30000);
}*/

/* Update plot traces with new data*/
function updateTraces(newdata, index){
	console.log(index);
	if (newdata.y.length == index.length){
		Plotly.extendTraces('plotly-TS', newdata, index);
		if(TSPlot.layout.xaxis.range[1] == date){
			date = Date.now();
			TSPlot.layout.xaxis.range[1] = date; 
			Plotly.relayout('plotly-TS', TSPlot.layout);
		}
	}
}


/* Plot Object*/
var TSPlot = {
	layout: {
		yaxis: {
			rangemode: "tozero"
		},
		xaxis: {
			type: 'date',
		},
		margin: {
			l: 50,
			r: 50,
			t: 40,
			b: 40
		}
	},

	showing: false,
	traces: [],

	/* Create new plot with trace in div*/
	initialize: function(trace) {
		var to = date;
		var from = new Date();
		from = from.setTime(to-3600000);
		TSPlot.layout.xaxis.range = [from, to];
		TSPlot.traces = [trace];		
		Plotly.newPlot('plotly-TS', TSPlot.traces, TSPlot.layout, {responsive: true, displayModeBar: false});	
	},

	/* Hide plot and start timer*/
	hide: function() {
		TSPlot.showing = false;
		TSPlot.traces = [];
		Plotly.purge('plotly-TS');
		document.getElementById("plot").style.display = 'none';
		const curr_range = document.getElementsByClassName("range-value");
		curr_range[0].innerHTML = 'Last 1 hour';
		set_refresh(1000*document.getElementById("CDTimer").innerHTML);
		//clearTimeout(plot_timer);
	},

	/* Show plot and pause timer*/
	show: function(){
		TSPlot.showing = true;
		document.getElementById("plot").style.display = 'block';
		clearTimeout(timer_id);
		stop_refresh();
		//refresh_plot();
	}

}//TSPlot

	

