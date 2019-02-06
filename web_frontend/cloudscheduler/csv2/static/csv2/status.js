var date = Date.now();

function initialize(){
	/*Add event listeners once page loads*/
	addEventListeners("plottable");
	addEventListeners("range");
}

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

/* Range selection dropdown*/
function dropDown(){
	document.getElementById("range-select").classList.toggle("selected");
	document.getElementById("myDropdown").classList.toggle("show");
}

/* Change time range for plot*/
function selectRange(range){
	const curr_range = document.getElementsByClassName("range-btn");
	curr_range[0].innerHTML = range.innerHTML+'<span class="space"></span><span class="caret"></span>';
	const dropdowns = document.getElementsByClassName("range");
	for (var i = 0; i < dropdowns.length; i++) {
		if (dropdowns[i].classList.contains('selected')) {
			dropdowns[i].classList.remove('selected');
      		}
	}
	range.classList.toggle("selected");
	var to = new Date();
	var from = new Date();
	var multiple = 60000;
	if(range.parentElement.classList.contains("days")) multiple = 86400000;
	to.setTime(date-(range.dataset.to*multiple))
	to = to.getTime();
	from.setTime(date-(range.dataset.from*multiple));
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
				var trace_array = [];
				for(var y = 0; y < TSPlot.traces.length; y++){
					trace_array.push(TSPlot.traces[y].name)
				}
				sessionStorage.setItem("traces", JSON.stringify(trace_array));
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
		query += `AND time > ${TSPlot.layout.xaxis.range[1]}ms`;
	}
	return query;
}

/* Fetch trace data from db and add to plot*/
function getTraceData(trace, showing){
	if(window.location.pathname == "/cloud/status/") var newpath = "plot";
	else var newpath = "/cloud/status/plot";
	query = createQuery(trace.dataset.path, false);
	const csrftoken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
	fetch(newpath,{
		method: 'POST',
		headers: {'Accept': 'application/json', 'X-CSRFToken': csrftoken},
		credentials: 'same-origin',
		body: query,
		}
	)
	.then(function(response){
		if(response.ok){
			return response.json();
		}
		throw new Error('HTTP response not was not OK. '+response.status);
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
	}).then(function(data){
		if(showing == true){
			var trace_array = [];
			for(var y = 0; y < TSPlot.traces.length; y++){
				trace_array.push(TSPlot.traces[y].name)
			}
			sessionStorage.setItem("traces", JSON.stringify(trace_array));
		}
	})
	.catch(error => console.log('Error:', error));
	
}

/* Refresh status table every 30s*/
/*var TimerSwitch = 1;
function set_refresh(time) {
	TimerSwitch = 1;
	setTimeout(function() {
		refresh_plot();
		fetch(location.href,{	
			method: 'GET',
			headers: {'Accept': 'text/html'},
		})	
		.then((response) => response.text())
		.then((html) => {
			var parser = new DOMParser();
			var doc = parser.parseFromString(html, "text/html");
			document.getElementById("status").innerHTML = doc.getElementById("status").innerHTML;
			checkForPlottedTraces();
			TimerVal = 30;
			set_refresh(30000);
		})
		.catch((error) => {
			console.warn(error);
		});
	
	},time);
	document.getElementById('vms-iframe').src='';
}

function stop_refresh() {
	TimerSwitch = 0;
	window.stop();
}

function pass_url(url) {
	stop_refresh();
	document.getElementById('vms-iframe').src='/vm/list/'+url;
}*/

function checkForPlottedTraces(){
	if (typeof(Storage) !== "undefined"){
		if(sessionStorage.length != 0){
			var plotted_traces = JSON.parse(sessionStorage.getItem("traces"));
			for(var x = 0; x < plotted_traces.length; x++){
				var stat = document.querySelectorAll('td[data-path="'+plotted_traces[x]+'"]');
				stat[0].classList.toggle("plotted");
			}
		}
	}else console.log("Sorry! No Web Storage support..");
	
	
}


/* Refresh plot every 30 seconds with new data from db*/
var plot_timer;
function refresh_plot() {

	if(TSPlot.showing == true){
		/* Only refresh if plot is showing and current range is Last hour or less*/
		if((TSPlot.layout.xaxis.range[1] - TSPlot.layout.xaxis.range[0]) <= 3600000 && TSPlot.layout.xaxis.range[1] == date){
			date = Date.now();
			var traces = TSPlot.traces;
			var newdata = {
				y: [],
				x: []
			};
			var index = [];
			var query = createQuery(traces[0].name,true)
			index.push(0);
			for (var i = 1; i < traces.length; i++){
				index.push(i);
				query += ';'
				query += createQuery(traces[i].name,true)
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
				for(var k = 0; k < traces.length; k++){
					const responsedata = data.results[k].series[0].values;
					const unpackData = (arr, index) => {
						var newarr = arr.map(x => x[index]);
						return newarr
					}
					var updatetrace = {
						x: unpackData(responsedata, 0),
						y: unpackData(responsedata, 1)
					}
				
					/* Update trace*/
					newdata.y.push(unpackData(responsedata, 1));
					newdata.x.push(unpackData(responsedata, 0));
				}
				/* Update plot range*/
				return updateTraces(newdata, index);
			})
			.catch(error => console.log('Error:', error));
		}					
		
	}
}

/* Update plot traces with most recent data points*/
function updateTraces(newdata, index){
	Plotly.extendTraces('plotly-TS', newdata, index);
	TSPlot.layout.xaxis.range[1] = date; 
	Plotly.relayout('plotly-TS', TSPlot.layout);
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
		//refresh_plot();
		sessionStorage.setItem("traces", JSON.stringify(trace.name));
	},

	/* Hide plot*/
	hide: function() {
		TSPlot.showing = false;
		TSPlot.traces = [];
		Plotly.purge('plotly-TS');
		document.getElementById("plot").style.display = 'none';
		const curr_range = document.getElementsByClassName("range-btn");
		curr_range[0].innerHTML = 'Last 1 hour<span class="space"></span><span class="caret"></span>';
		var list = document.getElementsByClassName('plotted');
		var init_length = list.length;
		for (var i = 0; i < init_length; i++) {
			var value = list[0];
			value.classList.remove('plotted');
		}
		sessionStorage.clear();
	},

	/* Show plot*/
	show: function(){
		TSPlot.showing = true;
		document.getElementById("plot").style.display = 'block';
	}

}//TSPlot

	

