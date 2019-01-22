var date = new Date();
date.setMilliseconds(0);



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
	//console.log(trace);
	//console.log(trace.firstChild.data);
	//console.log(trace.dataset.path);

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
			var newtrace = getTraceData(trace);
			/* Add trace to plot*/
			Plotly.addTraces('plotly-TS', newtrace);
		}
	}else{
		document.getElementById("loader").style.display = 'inline-block';
		var newtrace = getTraceData(trace);
		/* Create plot*/
		TSPlot.show();
		TSPlot.initialize(newtrace);
	}
	//if(TSPlot.showing == true) stop_refresh();
	//else set_refresh(1000*document.getElementById("CDTimer").firstChild.data);
}

function getTraceData(trace){
	console.log(trace.dataset.path);
	var line = trace.dataset.path.split(" ");
	//console.log(line);
	var group = line[0];
	var cloud;
	var measurement;
	if(line.length == 3){
		cloud = line[1];
		measurement = line[2];
	}else{
		measurement = line[1];
	}
	//console.log(group);
	//console.log(cloud);
	//console.log(measurement);
	console.log(trace.firstChild.data);
	var newtrace = {
		type: "scatter",
		mode: 'lines+markers',
		name: trace.dataset.path,
		x: [date],
		y: [trace.firstChild.data]
	}
	return newtrace;
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
		console.log(document.getElementById("CDTimer").firstChild.data)
		var timer_status;
		if(TimerSwitch == 1) timer_status = "on";
		else timer_status = "off";
		//console.log("Timer was "+timer_status);
		//console.log(1000*document.getElementById("CDTimer").firstChild.data);
		set_refresh(1000*document.getElementById("CDTimer").firstChild.data);
		if(TimerSwitch == 1) timer_status = "on";
		else timer_status = "off";
		//console.log("Timer now is "+timer_status);
	},

	show: function(){
		TSPlot.showing = true;
		document.getElementById("plot").style.display = 'block';
		var timer_status;
		if(TimerSwitch == 1) timer_status = "on";
		else timer_status = "off";
		//console.log("Timer was "+timer_status);
		stop_refresh();
		//clearTimeout(timer_id);
		if(TimerSwitch == 1) timer_status = "on";
		else timer_status = "off";
		//console.log("Timer now is "+timer_status);
	}

}//TSPlot

	
	// example request
//postAjax('https://csv2-dev3.heprc.uvic.ca', function(data){ console.log(data); });
	
	// example request with data object
//postAjax('https://csv2-dev3.heprc.uvic.ca/cloud/status/', function(data){ console.log(data); });

/*
function refreshA() {

	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
	  if (this.readyState == 4 && this.status == 200) {
		//document.getElementById("demo").innerHTML = this.responseText;
		console.log(this);
	  }
	};
	xhttp.open("POST", "https://csv2-dev3.heprc.uvic.ca/cloud/status", true);
	xhttp.send(); 
}



*/












