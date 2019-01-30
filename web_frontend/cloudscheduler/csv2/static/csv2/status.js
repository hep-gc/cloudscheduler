var date = new Date();
date.setMilliseconds(0);
var x = date.getHours();
date.setHours(x+8);



/* Add click events to table elements*/
function addEventListeners(className) {
	var inputList = document.getElementsByClassName(className);
		var i;
		for (i = 0; i < inputList.length; i++){
			inputList[i].addEventListener('click', function(){
		    		togglePlot(this);
			});
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
			/* Remove trace if it is already plotted*/
			if(TSPlot.traces.length == 1) {
				TSPlot.hide();
			}else{
				Plotly.deleteTraces('plotly-TS', index);
			}
		}else{
			/* Add trace to plot*/
			getTraceData(trace, true);
		}
	}else{
		document.getElementById("loader").style.display = 'inline-block';		
		/* Create plot*/
		TSPlot.show();
		getTraceData(trace, false);
		//TSPlot.initialize(newtrace);
	}
	
}

/* Fetch trace data from db and add to plot*/
function getTraceData(trace, showing){
	var line = trace.dataset.path.split(" ");
	var group = line[0];
	var measurement;
	var query;
	if(line.length == 3){
		var cloud = line[1];
		measurement = line[2];
		query = `SELECT * FROM "${measurement}" WHERE "cloud"='${cloud}' AND "group"='${group}'`;
	}else{
		measurement = line[1];
		query = `SELECT * FROM "${measurement}" WHERE "group"='${group}'`;
	}
	console.log(query);
	var csrftoken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
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
		console.log(data);
		var responsedata = data.results[0].series[0].values;
		console.log(responsedata);
		const unpackData = (arr, index) => {
			var newarr = arr.map(x => x[index]);
			return newarr
		}
	    	const aTrace = {
			type: 'scatter',
			mode: 'lines+markers',
			name: trace.dataset.path,
			x: unpackData(responsedata, 0),
			y: unpackData(responsedata, responsedata[0].length-1)
		}
		if(showing == true) return Plotly.addTraces('plotly-TS', aTrace);
		else return TSPlot.initialize(aTrace);
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
			precision: 'seconds'
		},
		margin: {
			l: 50,
			r: 50,
			t: 50,
			b: 50
		}
	},

	showing: false,
	traces: [],

	/* Create new plot with trace in div*/
	initialize: function(trace) {
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

	














