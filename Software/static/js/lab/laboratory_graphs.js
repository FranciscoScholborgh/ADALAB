const chartColors = {
	black: 'rgb(0, 0, 0)',
	blue: 'rgb(0, 47, 187)',
	brown: 'rgb(141, 73, 37)',
	green: 'rgb(0, 152, 70)',
	grey: 'rgb(201, 203, 207)',
	orange: 'rgb(239, 127, 26)',
	pink: 'rgb(247, 191, 190)',
	purple: 'rgb(153, 102, 255)',
	red: 'rgb(230, 0, 38)',
	yellow: 'rgb(255, 233, 0)'
};

var graphs = {}

function create_axes(x_axes, y_axes) {
    var x_factor = x_axes.split(",");
    var y_factor = y_axes.split(",");
    var xAxes = []
    var yAxes = []
    x_factor.forEach(function(x_label){
        var config = {
            display: true,
            scaleLabel: {
                display: true,
                labelString: x_label
            }
        }
        xAxes.push(config)
    });
    y_factor.forEach(function(y_label){
        var config = {
            display: true,
            id: y_label,
            scaleLabel: {
                display: true,
                labelString: y_label
            }
        }
        yAxes.push(config)
    });
    return [xAxes, yAxes]
}

function create_graph(canvas_id, g_title, g_type, g_datasets, g_xAxes, g_yAxes) {
    var xy_axes = create_axes(g_xAxes, g_yAxes)
    var config = {
        type: g_type,
        data: {
            labels: [],
            datasets: g_datasets
        },
        options: {
            responsive: true,
            bezierCurve: false,
            scaleShowValues: true,
                title: {
                display: true,
                text: g_title
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: xy_axes[0],
                yAxes: xy_axes[1]
            }
        }
    };

    var ctx = document.getElementById(canvas_id).getContext('2d');
    var chart= new Chart(ctx, config);
    graphs[canvas_id] = {'chart':chart, 'config':config}
}

function add_dataset(canvas_id, mesname, g_color) {
    var meseaures = mesname.split(',')
    var chart = graphs[canvas_id].chart;
    var config = graphs[canvas_id].config;
    var yAxes = config.options.scales["yAxes"]
    var yMes = []
    yAxes.forEach(function(yAxis){
        var measure = yAxis.scaleLabel["labelString"]
        yMes.push(measure)
    });
    meseaures.forEach(function(meseaure){
        var color = chartColors[g_color];
        
        if(color === undefined) {
            var colorNames = Object.keys(chartColors);
            var colorName = colorNames[config.data.datasets.length % colorNames.length];
            var color = chartColors[colorName];
        }
            
        var newDataset = {
            label: meseaure,
            backgroundColor: color,
            borderColor: color,
            data: [],
            yAxisID : yMes.shift(),
            fill: false
        };
        
        config.data.datasets.push(newDataset);
        
    });
    chart.update();
}

function add_data(canvas_id, data) {
    var chart = graphs[canvas_id].chart;
    var config = graphs[canvas_id].config;
    if (config.data.datasets.length > 0) {
        var sec = config.data.labels.length + 1;
        config.data.labels.push(`segundo ${sec}`);
        config.data.datasets.forEach(function(dataset) {
            var point = data[dataset.label];
            ////console.log(`label ${dataset.label}, data_keys: ${Object.keys(data)}, point: ${point}`)
            dataset.data.push(point);
            chart.update();
        });      
    }
}

function taskComplete(canvas_id) {
    var id = canvas_id.split('-P')[1];
    $(`#nextto-P${id}`).removeClass("hide_element");
    $(`#prev-P${id}`).removeClass("hide_element");
    $(`#btn-P${id}`).removeClass("hide_element");
    $(`#btn-P${id}`).html("Repetir medición");
}

function taskFail(canvas_id, title, message) {
    var id = canvas_id.split('-P')[1];
    $("#modal_title").text(title);
    $("#modal_content").text(message);
    $("#warn_modal").modal();
    $(`#btn-P${id}`).removeClass("hide_element");
}

function start_messurement(canvas_id, device, time) {
    var timeFrag = time.split(':');
    var timeSec = Number(timeFrag[2]) + Number(timeFrag[1])*60 + Number(timeFrag[0])*3600;
    var chart = graphs[canvas_id].chart;
    var config = graphs[canvas_id].config;
    var id = canvas_id.split('-P')[1];
    $(`#nextto-P${id}`).addClass("hide_element");
    $(`#prev-P${id}`).addClass("hide_element");
    $(`#btn-P${id}`).addClass("hide_element");
    config.data.labels = []
    if (config.data.datasets.length > 0) {
        config.data.datasets.forEach(function(dataset) {
            dataset.data = [];
        });
        chart.update();
    }
    webSocketSBC(canvas_id, device, timeSec, add_data, taskComplete, taskFail);
}

function generar_preinforme(id_lab, method) {
    var procs = {};
    var graph_keys = Object.keys(graphs);
    graph_keys.forEach(function(key){
        var config = graphs[key].config;
        var num_proc = key.split('-P')[1];
        datasets = []
        config.data.datasets.forEach(function(dataset) {
            datasets.push(dataset.data)
        });
        procs[`${num_proc}`] = datasets;
    });
    var pregid = 1;
    var pregs = {}
    while(true) {
        $(`#preg${pregid}`).length
        //console.log("pre: " + $(`#preg${pregid}`).length);
        //console.log("result: " + $(`#preg${pregid}`).length === 0);
        if ($(`#preg${pregid}`).length === 0){
            break;
        }
        pregs[`${pregid}`] = $(`#preg${pregid}`).val();
        pregid++;
    }
    //console.log(pregs)
    var csrftoken = getCookie('csrftoken');
    var preinfo = JSON.stringify({"procs":procs, "pregs":pregs, "id_lab":id_lab})
    var data = {"data": preinfo, "method": method, csrfmiddlewaretoken:csrftoken}
    post_request("https://adaslab.herokuapp.com/preinforme/", data);
}