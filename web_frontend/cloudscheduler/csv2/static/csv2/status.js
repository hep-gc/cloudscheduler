set_state();

/* Get custom refresh interval, default = 30 seconds*/
var refresh_interval = parseInt(document.getElementsByName('refresh_interval')[0].value);
if (!(typeof(refresh_interval) !== 'undefined')) refresh_interval = 30;
if (refresh_interval == null || refresh_interval == NaN) refresh_interval = 30;
else if (refresh_interval < 1) stop_refresh;



/* Timestamp of last refresh*/
var date = Date.now();

/* Close the range dropdown menu when user clicks outside of it*/
window.onclick = function(event) {
    try{
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
    /* Catch for if user clicks outside of 'window'. Otherwise event.target.matches is undefined*/
    catch{
        return;
    }
}

var statusTables = document.getElementsByClassName("status-table");
var navbar = document.getElementsByClassName("top-nav")[0];

// table one
var tableOneHeaders = document.getElementsByClassName("header-row")[0];
var tableOne = statusTables[0].getElementsByTagName("table")[0];
var tableOneData = tableOne.getElementsByTagName("td");

// table one initial dimensions
var offsetOne = document.getElementsByClassName("main-div super-main-div")[0].offsetTop;
var tableOneHeight = tableOne.clientHeight;
var headerWidthOne = [];
var dataWidthOne = [];
computeDimensions(headerWidthOne, dataWidthOne, tableOneHeaders, tableOneData, 15)

// table two
var tableTwoHeaders = document.getElementsByClassName("header-row")[1];
var tableTwo = statusTables[1].getElementsByTagName("table")[0];
var tableTwoData = tableTwo.getElementsByTagName("td");

// table two initial dimensions
var offsetTwo = tableTwo.parentElement.offsetTop;
var tableTwoHeight = tableTwo.clientHeight;
var headerWidthTwo = [];
var dataWidthTwo = [];
computeDimensions(headerWidthTwo, dataWidthTwo, tableTwoHeaders, tableTwoData, 29);
computeStartEnd();


window.onresize = function () {
    // remove the sticky header to ensure correct inital dimensions
    tableOneHeaders.classList.remove("sticky-top");
    tableTwoHeaders.classList.remove("sticky-top");

    tableOneHeight = tableOne.clientHeight;
    tableTwoHeight = tableTwo.clientHeight;

    offsetOne = document.getElementsByClassName("main-div super-main-div")[0].offsetTop;
    offsetTwo = tableTwo.parentElement.offsetTop;

    // reset the dimensions and compute the current header location
    computeDimensions(headerWidthOne = [], dataWidthOne = [], tableOneHeaders, tableOneData, 15);
    computeDimensions(headerWidthTwo = [], dataWidthTwo = [], tableTwoHeaders, tableTwoData, 29);
    computeStartEnd();
}

window.onscroll = function () {
    computeStartEnd();
}

function computeStartEnd() {
    // start when table hits nav bar, end when it hits the bottom
    var startOne = offsetOne - navbar.clientHeight;
    var endOne = tableOneHeight + startOne - navbar.clientHeight;

    var startTwo = offsetTwo + startOne;
    var endTwo = offsetTwo + tableTwoHeight;
    
    stickyHeader(tableOneHeaders, tableOneData, startOne, endOne, headerWidthOne, dataWidthOne);
    stickyHeader(tableTwoHeaders, tableTwoData, startTwo, endTwo, headerWidthTwo, dataWidthTwo);
}

/** computes the initial width of each column */
function computeDimensions(headerWidth, dataWidth, headers, data, numColumns) {
    for (var header of headers.getElementsByTagName("th")) {
        headerWidth.push(window.getComputedStyle(header).getPropertyValue("width"));
    }
    
    for (var i = 0; i < numColumns; i++) {
        if (data[i]) {
            dataWidth.push(window.getComputedStyle(data[i]).getPropertyValue("width"));
        }
    }
}

/** keeps the header on the screen while scrolling through the table */
function stickyHeader(headers, data, tableStart, tableEnd, headerWidth, dataWidth) {
    if (window.pageYOffset >= tableStart && window.pageYOffset <= tableEnd) {
        // in the table, stick the table header
        headers.classList.add("sticky-top");
        headers.style.top = navbar.clientHeight;

        var header = headers.getElementsByTagName("th");
        var subHeaders = 0;

        // set the width of each column
        for (var i = 0; i < header.length; i++) {
            if (header[i].colSpan > 1) {
                subHeaders++;
            } else {
                data[i-subHeaders].style.minWidth = dataWidth[i-subHeaders];
            }
            header[i].style.minWidth = headerWidth[i];
            header[i].style.maxWidth = headerWidth[i];
        }

        return;
    }
    // not in table anymore, stop sticking the top
    headers.classList.remove("sticky-top");
}


/* Refresh status table and system services display*/
var TimerSwitch = 1;
var timer_id;
function set_refresh(time) {
    TimerSwitch = 1;
    timer_id = setTimeout(function() {

        refresh_plot();

        fetch(location.href,{   
            method: 'GET',
            headers: {'Accept': 'application/json', 'Content-Type':'application/json'},
        })  
        .then(function(response){
            /* Check response status code*/
            if(response.ok){
                return response.text();
            }throw new Error('Could not update status table :( HTTP response not was not OK -> '+response.status);
        })
        .then((html) => {
            var parser = new DOMParser();
            var doc = parser.parseFromString(html, "text/html");
            document.getElementById("status").innerHTML = doc.getElementById("status").innerHTML;
            document.getElementById("system-services").innerHTML = doc.getElementById("system-services").innerHTML;
            TimerVal = refresh_interval;
            set_refresh(refresh_interval*1000);
            set_state();
            checkForExpandedRow();
            checkForPlottedTraces();
            initialize();
        })
        .catch((error) => {
            console.warn(error);
            TimerVal = refresh_interval;
            set_refresh(refresh_interval*1000);
        });
    },time);
    document.getElementById('vms-iframe').src='';
}

function stop_refresh() {
    TimerSwitch = 0;
    clearTimeout(timer_id);
    window.stop();
}

function native_list(url) {
    stop_refresh();
    document.getElementById('vms-iframe').src='/vm/list/'+url;
    window.location.href = "#vms-overlay";
}

function foreign_list(url) {
    stop_refresh();
    document.getElementById('vms-iframe').src='/vm/foreign/'+url;
    window.location.href = "#vms-overlay";
}

function toggle_id(name){

    if(document.getElementById(name).style.display == "table-row"){
        document.getElementById('sym-'+name).innerHTML = "&#x25BE;"
        document.getElementById(name).style.display = "none"
        sessionStorage.setItem(name, 0);
    }
    else{
        document.getElementById('sym-'+name).innerHTML = "&#x25B4;"
        document.getElementById(name).style.display = "table-row"
        sessionStorage.setItem(name, 1);
    }
}

function toggle_group(name){

    var n;

    if(document.getElementsByClassName(name)[0].style.display == "table-row"){
        document.getElementById('sym-'+name).innerHTML = "&#x25BE;"

        for(n=0; n<document.getElementsByClassName(name).length; n++){
            document.getElementsByClassName(name)[n].style.display = "none"
            sessionStorage.setItem(document.getElementsByClassName(name)[n].id, 0);
        }
    }
    else{
        for(n=0; n<document.getElementsByClassName(name).length; n++){
            document.getElementById('sym-'+name).innerHTML = "&#x25B4;"

            document.getElementsByClassName(name)[n].style.display = "table-row"
            sessionStorage.setItem(document.getElementsByClassName(name)[n].id, 1);
        }
    }
}


/* Set state of expand row in session storage*/
function set_state(){
    var n;
    var clouds = document.querySelectorAll('[id^="expand-"]');

    for(n=0;n<clouds.length;n++){
        if(sessionStorage.getItem(clouds[n].id)==1){
            console.log(clouds[n].id)
            document.getElementById(clouds[n].id).style.display = "table-row"
            document.getElementById('sym-'+clouds[n].id).innerHTML = "&#x25B4;"
        }
    }
}



/* Add event listeners*/
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
                var list = document.querySelectorAll(`td[data-path="${this.dataset.path}"]`);
                for (k = 0; k < list.length; k++){
                    list[k].classList.toggle('plotted');
                }
                if(!list) this.classList.toggle("plotted");
                togglePlot(this);
            } 
            else if (className == 'filter') {
                document.getElementById("filter-form").addEventListener('submit', function (event) {
                    // prevent the page from refreshing on form submission
                    event.preventDefault();
                });
                selectRangeFilter();
            }
            else selectRange(this);
        });
    }
}


/* Range selection dropdown*/
function dropDown(){
    if(!document.getElementById("myDropdown").classList.contains("show"))
        document.getElementById("range-select").classList.add("selected");
    else document.getElementById("range-select").classList.remove("selected");
    document.getElementById("myDropdown").classList.toggle("show");
    
    // close custom filter dropdown if open
    if (document.getElementById("myFilterDropdown").classList.contains("show")) {
        document.getElementById("myFilterDropdown").classList.toggle("show");
        document.getElementById("filter-select").classList.remove("selected");
    }
}

/* custom date filter dropdown */
function dropDownFilter() {
    if (!document.getElementById("myFilterDropdown").classList.contains("show"))
        document.getElementById("filter-select").classList.add("selected");
    else
        document.getElementById("filter-select").classList.remove("selected");
    document.getElementById("myFilterDropdown").classList.toggle("show");
}

/* preprocess selected dates from custom filter */
function selectRangeFilter() {
    const start = document.getElementById("start-date");
    const end = document.getElementById("end-date");

    // missing a date value
    if (!start.value || !end.value)
        return;


    var to = Date.parse(end.value);
    var from = Date.parse(start.value);

    // error with date input
    if (checkDates(to, from))
        return;
    
    // close the dropdown
    document.getElementById("filter-select").classList.remove("selected");
    document.getElementById("myFilterDropdown").classList.toggle("show");

    createPlot(to, from);
}

/* preprocess selected time range  */
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
    createPlot(to, from)    
}

/* Change time range for plot based on user selection*/
function createPlot(to, from) {
    /* Update traces with data from new range*/
    if((date-from) > 3600000 && !(TSPlot.traces[0].x[0] < from)){
        var traces = TSPlot.traces;
        var newdata = {
            y: [],
            x: []
        };
        var index = [];
        var query = createQuery(traces[0].name, from, TSPlot.traces[0].x[0], true);
        /* Create string of queries for db*/
        for (var i = 1; i < traces.length; i++){
            query += ';';
            query += createQuery(traces[i].name, from, TSPlot.traces[0].x[0], true);
        };
        var current_url = window.location.href;
        const regex = /(.*\/\/[^\/]*)(\/.*)/;
        var root_url = current_url.split(regex)[1];
        var newpath = root_url + ":8086/query";
        newpath += "?q=" + query + "&db=csv2_timeseries&epoch=ms&u=csv2_read&p=csv2_public";
        newpath = encodeURI(newpath)
        newpath = newpath.replace(';', '%3B')
        fetch(newpath,{
            method: 'GET',
            headers: {'Accept': 'application/json', 'Content-Type':'application/json'},
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
            var no_new_points = 0;
            for(var i = 0; i < traces.length; i++){
                /* Skip trace if no new data exists*/
                if(!(typeof data.results[i].series !== 'undefined')){
                    no_new_points ++;
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
            if(no_new_points == index.length) return data;
            else{
                Plotly.prependTraces('plotly-TS', newdata, index);
                return updateTraces(newdata, index, []);
            }
        })
        .then(function(response){
            /* Update plot range*/
            TSPlot.layout.xaxis.range = [from, to];
            Plotly.relayout('plotly-TS', TSPlot.layout);
        })
        .catch(error => console.warn(error));
    }
    /* If no new data is needed*/
    else{
        /* Only update plot range*/
        TSPlot.layout.xaxis.range = [from, to];
        TSPlot.layout.yaxis.range = [];
        Plotly.relayout('plotly-TS', TSPlot.layout);
    }
}

/* preprocess dates for error handling */
function validate() {
    const start = document.getElementById("start-date");
    const end = document.getElementById("end-date");

    from = start.value ? Date.parse(start.value) : null;
    to = end.value ? Date.parse(end.value) : null;

    checkDates(to, from)
}

/* error messages for filtered dates */
function checkDates(to, from) {
    const dateError = document.getElementById("date-error");
    
    if (from && from > date + 60000)
        dateError.textContent = "Start date must be less than or equal to current date";
    else if (to && to > date + 60000)
        dateError.textContent = "End date must be less than or equal to current date";
    else if (to && from && from > to)
        dateError.textContent = "Start date must be less than or equal to end date"
    else
        dateError.textContent = null;
    
    return dateError.textContent;
}

/* Toggle plotted traces and initialize/show plot if not yet created*/
function togglePlot(trace){
    if (trace.dataset.path.startsWith("  ")){
        trace.dataset.path = trace.dataset.path.replace("  "," groups_total ");
    }
    else{
        trace.dataset.path = trace.dataset.path.replace("  "," "); 
    }
    trace.dataset.path = trace.dataset.path.trim();

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
        /* If trace is already plotted*/
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
    }
    /* If plot is not created*/
    else{
        document.getElementById("loader").style.display = 'inline-block';		
        /* Create plot*/
        TSPlot.show();
        getTraceData(trace, false);
    }
}


/* Construct query in Line Protocol for db*/
function createQuery(trace, from, to, showing){
    const line = trace.split(" ");
    var query = '';
    var services = false;
    var global_total = false;
    var group = line[0];
    /* If trace is for global group total*/
    if (group == 'groups_total'){
        global_total = true
        var groups = [];
        var l = document.getElementsByName(group);
        var len = l.length
        for (var k = 0; k < len; k++){
            groups.push(l[k].value);
        }
        var measurement = line[1];
        query += `SELECT time,SUM("value") FROM "${measurement}" WHERE `;
        for (var g = 0; g < groups.length; g++){
            query += `"group"='${groups[g]}'`;
            if(g != groups.length-1){
                query += ` OR `;
            }
        }
    }
    else{
        query += `SELECT time,value FROM `;
    }
    /* If trace is for service status*/
    if(line.length == 1){
        services = true;
        var measurement = line[0];
        query += `"${measurement}"`;
    }
    /* If trace is regular*/
    else if(line.length == 3 && !global_total){
        var cloud = line[1];
        var measurement = line[2];
        query += `"${measurement}" WHERE "cloud"='${cloud}' AND "group"='${group}'`;
    }else if(!services && !global_total){
        var measurement = line[1];
        query += `"${measurement}" WHERE "group"='${group}'`;
    }
    /* If requesting newest 30s of data*/
    if (to == 0){
        if(!services) query += ` AND time >= ${from}ms`;
        else query += ` WHERE time >= ${from}ms`;
    /* Default request is last 1 hour*/
    }else if (showing == false || (date-from) <= 3600000){
        if(!services) query += ` AND time >= ${date-3600000}ms`;
        else query += ` WHERE time >= ${date-3600000}ms`;
    /* If plot is showing*/
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
        if(index == -1) to = date;
        if(!services){
            if(from > TSPlot.layout.xaxis.range[0])	query += ` AND time >= ${TSPlot.layout.xaxis.range[0]}ms AND time < ${to}ms`;
            else query += ` AND time >= ${from}ms AND time < ${to}ms`;
        }else{
            if(from > TSPlot.layout.xaxis.range[0])	query += ` WHERE time >= ${TSPlot.layout.xaxis.range[0]}ms AND time < ${to}ms`;
            else query += ` WHERE time >= ${from}ms AND time < ${to}ms`;
        }
    }
    /* Get db to sum over 30s periods*/
    if(global_total) query += ` GROUP BY time(30s)`;
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
                /* If gap between two timestamps is > 60s*/
                if((Math.abs(arr[ind+1][index] - arr[ind][index])) > 60000){
                    addtime.push(arr[ind][index] + 1000);
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

/* Function to convert characters in query to browser url format */
function convertQueryToURL(query){
    var newquery = "";
    for (let i=0; i<query.length; i++){
        switch(query[i]){
            default:
                newquery += query[i];
                break;
            case " ":
                newquery += "%20";
                break;
            case '"':
                newquery += "%22";
                break;
            case "-":
                newquery += "%2D";
                break;
            case "'":
                newquery += "%27";
                break;
            case "<":
                newquery += "%3C";
                break;
            case "=":
                newquery += "%3D";
                break;
            case ">":
                newquery += "%3E";
                break;
        }
    }
    return newquery;
}

/* Fetch trace data from db and add to plot*/
function getTraceData(trace, showing){
    trace.dataset.path = trace.dataset.path.replace("  ","groups_total ")
    var current_url = window.location.href;
    const regex = /(.*\/\/[^\/]*)(\/.*)/;
    var root_url = current_url.split(regex)[1];
    var newpath = root_url + ":8086/query";
    var nullvalues = [];
    if(showing == true) query = createQuery(trace.dataset.path, TSPlot.traces[0].x[0], date, showing);
    else query = createQuery(trace.dataset.path, date-3600000, date, showing);
    var newquery = encodeURI(query)
    newpath += "?q=" + query + "&db=csv2_timeseries&epoch=ms&u=csv2_read&p=csv2_public"
    newpath = newpath.replace(';', '%3B')
    fetch(newpath,{
        method: 'GET',
        headers: {'Accept': 'application/json', 'Content-Type':'application/json'},
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
        if(!(typeof (data.results[0]) !== 'undefined') || !(typeof (data.results[0].series) !== 'undefined')){
            throw `Oops! That trace: '${trace.dataset.path}' does not exist`;
        }
        const newarrays = parseData(data.results[0].series[0].values);
        var newtrace = {
            mode: 'lines',
            name: trace.dataset.path,
            x: newarrays[0],
            y: newarrays[1],
        }
        /* Pop trailing nulls that were produced by db through summing in a query*/
        if (newtrace.name.split(" ", 1) == 'groups_total'){
            if(newtrace.y[newtrace.y.length -1] == null){
                newtrace.y.pop();
                newtrace.x.pop();
            }
        }

        /* If plot is showing, add trace to plot*/
        if(showing == true){
            var newlayout = {
                yaxis: {
                    rangemode : "tozero"
                },
                xaxis: {
                    type : "date",
                    range: TSPlot.layout.xaxis.range
                }
            };
            Plotly.relayout('plotly-TS', newlayout);
            return Plotly.addTraces('plotly-TS', newtrace);
        }
        /* Create plot with trace*/
        else return TSPlot.initialize(newtrace);
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
    
    .catch(function(error){
        if(showing == false) document.getElementById("plot").style.display = 'none';
        console.warn(error);	
    });
}


/* On refresh, check for plotted traces to update colour in status tables*/
function checkForPlottedTraces(){
    if (typeof (Storage) !== "undefined"){
        var plotted_traces = JSON.parse(sessionStorage.getItem("traces"));
        if (plotted_traces != null){
            for(var x = 0; x < plotted_traces.length; x++){

                if(plotted_traces[x].split(" ", 1) == 'groups_total'){
                    plotted_traces[x] = plotted_traces[x].replace("groups_total ","  ")
                }

                var stat = document.querySelectorAll('td[data-path="'+plotted_traces[x]+'"]');
                for(var k = 0; k < stat.length; k++){
                    stat[k].classList.toggle("plotted");
                }
            }
        }
    }
}


/* On refresh, check if expanded row was showing*/
function checkForExpandedRow() {
    if (typeof (Storage) !== "undefined"){
        var expanded_row = JSON.parse(sessionStorage.getItem("extra-row"));
        if(expanded_row != null && expanded_row == true){
                document.getElementById('toggle-row').click();
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
        /* Keep track of order of traces that are global totals. This info is used in updateTraces() below*/
        var global_total = [];
        if (traces[0].name.split(" ", 1) == 'groups_total') global_total.push(true);
        else global_total.push(false);
        index.push(0);
        /* Create string of queries for db*/
        for (var i = 1; i < traces.length; i++){
            if (traces[i].name.split(" ", 1) == 'groups_total') global_total.push(true);
            else global_total.push(false);

            index.push(i);
            query += ';'
            query += createQuery(traces[i].name, traces[i].x[traces[i].x.length-1], 0, true);
        }
        var current_url = window.location.href;
        const regex = /(.*\/\/[^\/]*)(\/.*)/;
        var root_url = current_url.split(regex)[1];
        var newpath = root_url + ":8086/query"; 
        newpath += "?q=" + query + "&db=csv2_timeseries&epoch=ms&u=csv2_read&p=csv2_public";
        newpath = encodeURI(newpath)
        newpath = newpath.replace(';', '%3B')
        fetch(newpath,{
            method: 'GET',
            headers: {'Accept': 'application/json', 'Content-Type':'application/json'},
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
            if(new_points == true) return updateTraces(newdata, index, global_total);
            else return;
        })
        .catch(error => console.warn(error));					
    }
}


/* Update plot traces with most recent data points and new range*/
function updateTraces(newdata, index, global_total_list){
    /* If global view totals, check for null values in last < 30s period and remove*/
    if(global_total_list && global_total_list.length){
        for(var x = 0; x < global_total_list.length; x++){
            if(global_total_list[x]){
                /* Pop trailing nulls that were produced by db through summing in a query*/
                if(newdata.y[x][newdata.y[x].length-1] == null){
                    newdata.y[x].pop();
                    newdata.x[x].pop();
                }
            }
        }
    }
    /* If last plotted data point was 55s or more ago, insert null to show break in plot*/
    for(var k = 0; k < index.length; k++){
        var len = TSPlot.traces[k].x.length -1;
        if(typeof(TSPlot.traces[k]) !== 'undefined'){
            if(TSPlot.traces[k].x[len] < ((newdata.x[k][0])-60000)){
                newdata.x[k].unshift(newdata.x[k][0] - 1000);
                newdata.y[k].unshift(null);
            }
        }
    }
    Plotly.extendTraces('plotly-TS', newdata, index);
    /* Only update range if if looking at last 12 hours or less*/
    if(TSPlot.layout.xaxis.range[1] >= date && (date - TSPlot.layout.xaxis.range[0]) <= 43200000){
        date = Date.now();
        var diff = date - TSPlot.layout.xaxis.range[1];
        TSPlot.layout.xaxis.range[1] = date; 
        TSPlot.layout.xaxis.range[0] += diff;
    }
    var newlayout = {
        yaxis: {
            rangemode : "tozero"
        },
        xaxis: {
            type : "date",
            range: TSPlot.layout.xaxis.range
        }
    };
    Plotly.relayout('plotly-TS', newlayout);
}


function downloadPlot(){
    Plotly.downloadImage('plotly-TS', {format: 'png', width: 1200, height: 600, filename: 'newplot'});
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
        showlegend: true,
        hoverlabel: {
            namelength:30
        }
    },

    showing: false,
    traces: [],

    /* Create new plot with trace in div*/
    initialize: function(trace) {
        TSPlot.layout.xaxis.range = [date-3600000, date];
        TSPlot.traces.push(trace);		
        Plotly.newPlot('plotly-TS', TSPlot.traces, TSPlot.layout, {responsive: true, displayModeBar: false});
        var traces = [];
        traces.push(trace.name);
        sessionStorage.setItem("traces", JSON.stringify(traces));
    },

    /* Hide plot*/
    hide: function() {		
        var newlayout = {
            yaxis: {
                rangemode : "tozero"
            },
            xaxis: {
                type : "date"
            }
        };
        Plotly.relayout('plotly-TS', newlayout);
        TSPlot.traces = [];
        TSPlot.showing = false;
        /* Hide plot div*/
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
        sessionStorage.removeItem("traces");
        const dropdowns = document.getElementsByClassName("selected");
        var l = dropdowns.length;
        for (var i = 0; i < l; i++) {
            dropdowns[0].classList.remove('selected');
        }
        document.querySelectorAll('a[data-from="60"]')[0].classList.add('selected');
        /* Pause before purging to avoid TypeError, seems to be a Plotly bug
            https://community.plot.ly/t/typeerror-e-is-undefined-when-using-plotly-relayout-followed-by-plotly-purge/20442 */
        setTimeout(function(){
            Plotly.purge('plotly-TS');
        }, 10);
    },

    /* Show plot*/
    show: function(){
        TSPlot.showing = true;
        document.getElementById("plot").style.display = 'block';
    }

}//TSPlot
