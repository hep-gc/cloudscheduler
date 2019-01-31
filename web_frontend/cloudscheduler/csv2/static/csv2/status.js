
/* Add click events to table elements and range selection*/
function addEventListeners(className) {
	var inputList = document.getElementsByClassName(className);
		var i;
		for (i = 0; i < inputList.length; i++){
			inputList[i].addEventListener('click', function(){
				if(className == 'plottable') togglePlot(this);
				else selectRange(this);
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
	curr_range[0].firstChild.data = range.firstChild.data;
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
	to.setTime(curr-(range.dataset.to*multiple));
	from.setTime(curr-(range.dataset.from*multiple));
	TSPlot.layout.xaxis.range = [from, to];
	Plotly.relayout('plotly-TS', TSPlot.layout);
}

// Close the dropdown menu if the user clicks outside of it
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
	console.log(trace.dataset.path);
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

/* Fetch trace data from db and add to plot*/
function getTraceData(trace, showing){
	const line = trace.dataset.path.split(" ");
	const group = line[0];
	if(line.length == 3){
		var cloud = line[1];
		var measurement = line[2];
		var query = `SELECT time,value FROM "${measurement}" WHERE "cloud"='${cloud}' AND "group"='${group}'`;
	}else{
		var cloud = 'total';
		var measurement = line[1];
		var query = `SELECT time,value FROM "${measurement}" WHERE "group"='${group}'`;
	}
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
			mode: 'lines',
			name: trace.dataset.path,
			x: unpackData(responsedata, 0),
			y: unpackData(responsedata, 1)
		}
		if(showing == true) return Plotly.addTraces('plotly-TS', newtrace);
		else return TSPlot.initialize(newtrace);
	})
	.catch(error => console.log('Error:', error));
	
	

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
		var to = Date.now();
		var from = new Date();
		from.setTime(to-43200000);
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
		var timer_status;
		if(TimerSwitch == 1) timer_status = "on";
		else timer_status = "off";
		set_refresh(1000*document.getElementById("CDTimer").firstChild.data);
		if(TimerSwitch == 1) timer_status = "on";
		else timer_status = "off";
	},

	/* Show plot and pause timer*/
	show: function(){
		TSPlot.showing = true;
		document.getElementById("plot").style.display = 'block';
		var timer_status;
		if(TimerSwitch == 1) timer_status = "on";
		else timer_status = "off";
		stop_refresh();
		if(TimerSwitch == 1) timer_status = "on";
		else timer_status = "off";
	}

}//TSPlot

	














