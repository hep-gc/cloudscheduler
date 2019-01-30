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
			if(TSPlot.traces.length == 1) {
				TSPlot.hide();
			}else{
				Plotly.deleteTraces('plotly-TS', index);
			}
		}else{
			getTraceData(trace);
			/* Add trace to plot*/
		}
	}else{
		document.getElementById("loader").style.display = 'inline-block';
		//var newtrace = getTraceData(trace);
		var newtrace = {
			type: "scatter",
			mode: 'lines+markers',
			name: trace.dataset.path,
			x: [date],
			y: [trace.firstChild.data]
		}
		/* Create plot*/
		TSPlot.show();
		TSPlot.initialize(newtrace);
	}
	
}

function getTraceData(trace){
	var line = trace.dataset.path.split(" ");
	var group = line[0];
	var cloud;
	var measurement;
	var query;
	if(line.length == 3){
		cloud = line[1];
		measurement = line[2];
		query = `SELECT * FROM "${measurement}" WHERE "cloud"='${cloud}' AND "group"='${group}'`;
	}else{
		measurement = line[1];
		query = `SELECT * FROM "${measurement}" WHERE "group"='${group}'`;
	}
	/*var newtrace = {
		type: "scatter",
		mode: 'lines+markers',
		name: trace.dataset.path,
		x: [date],
		y: [trace.firstChild.data]
	}*/
	
	//fetch('https://csv2-dev3.uvic.ca:8086/query?db=dev3&epoch=s&q='+query,
	fetch('../../static/csv2/testjson.json',
		{method: 'GET',
		 headers: {'Accept': 'application/json'}
		}
	)
	.then(function(response) {
		return response.json();
	})
	.then(function(myJson) {
		var responsedata = myJson.results[0].series[0].values
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
		return Plotly.addTraces('plotly-TS', aTrace);
	});	

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

	














