const sensorNames = [
    'Kitchen',
    'Livingrm',
    'Studio',
    'Bedrm',
    'Bathrm',
    'East',
    'West',
];
const nsensors = 7;

// Function to get current year and week number
function getCurrentYearAndWeek() {
    const now = new Date();
    const start = new Date(now.getFullYear(), 0, 0);
    const diff = (now - start) + ((start.getTimezoneOffset() - now.getTimezoneOffset()) * 60 * 1000);
    const oneDay = 1000 * 60 * 60 * 24;
    const dayOfYear = Math.floor(diff / oneDay);
    return {
        year: now.getFullYear(),
        week: Math.ceil(dayOfYear / 7)
    };
}


// Function to fetch CSV data for a specific year and week and update chart
async function fetchDataAndUpdateChart() {
    const { year, week } = getCurrentYearAndWeek();
    //console.info('Current year and week:', year, week);
    try {
        const filePath = `data/${year}/w${week}.csv`;
        //console.info('Fetching data from:', filePath)
        const response = await fetch(filePath);
        if (!response.ok) {
            throw new Error('CSV file not found or unable to fetch data.');
        }
        const csvData = await response.text();
        const rows = csvData.split('\n');
        //console.info(`Fetched data for year ${year}, week ${week}:`, rows.length, 'rows');
        //console.info('Sample data:', rows[3]);

        const timestamps = [];
        const sensorData = {};

        rows.forEach(row => {
            const columns = row.split(',');
            if (columns.length == 8) { // Ensure there are just the right number of columns
                //const timestamp = moment(columns[0], 'YYYY-MM-DD HH:mm:ss'); // Parse timestamp using Moment.js
                timestamps.push(columns[0]);

                for (let i = 0; i < nsensors; i++) {
                    const sensorId = `S${i + 1}`;
                    if (!sensorData[sensorId]) {
                        sensorData[sensorId] = { temperature: [], humidity: [] };
                    }
                    const sValues = columns[i + 1].split('|').map(sensorString => parseFloat(sensorString.trim()));
                    sensorData[sensorId].temperature.push(sValues[0]);
                    sensorData[sensorId].humidity.push(sValues[1]);
                }
            }
        });
        //console.info('Parsed data:', timestamps.length, ' timestamps')
        //console.info('Sample data:', timestamps[3], sensorData['T1'].temperature[3])

        updateChart(timestamps, sensorData);
    } catch (error) {
        console.error(`Error fetching data for year ${year}, week ${week}:`, error);
    }
}

function updateChart(timestamps, sensorData) {

    const colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'];

    var tracesTemperature = [];
    var tracesHumidity = [];
    sensorNames.forEach((sensorName, index) => {
        tracesTemperature.push({
            x: timestamps,
            y: sensorData[`S${index+1}`].temperature,
            mode: 'lines',
            name: sensorName,
            line: {color: colors[index % colors.length], width: 2}
        });
        tracesHumidity.push({
            x: timestamps,
            y: sensorData[`S${index+1}`].humidity,
            mode: 'lines',
            name: sensorName,
            line: {color: colors[index % colors.length], width: 2},
            showlegend: false,
            xaxis: 'x',
            yaxis: 'y2',
        });
    });
    
    var layout = {
        title: '',
        height: 800,
        width: 700,
        hovermode:'closest',
        grid: {
            rows: 2,
            columns: 1,
            subplots:[['xy'],['xy2']],
        },
        margin: {
            t: 50, //top margin
            l: 50, //left margin
            r: 50, //right margin
            b: 50, //bottom margin
            pad: 0 //padding
        },
        yaxis: {
            domain: [0.5, 1] // range of y-axis for first subplot
        },
        yaxis2: {
            domain: [0, 0.45] // range of y-axis for second subplot
        },
        annotations: [
            {
                xref: 'paper',
                yref: 'paper',
                x: 0.5,
                y: 1.0,
                xanchor: 'center',
                yanchor: 'bottom',
                text: 'Temperature',
                showarrow: false,
                font: {
                    size: 16
                }
            },
            {
                xref: 'paper',
                yref: 'paper',
                x: 0.5,
                y: 0.45,
                xanchor: 'center',
                yanchor: 'bottom',
                text: 'Humidity',
                showarrow: false,
                font: {
                    size: 16
                }
            },
        ],
        legend: {
            x: 1,
            y: 0.5,
            xanchor: 'left',
            yanchor: 'middle'
        }
    };

    var data = tracesTemperature.concat(tracesHumidity);
    var config = {responsive: true};

    Plotly.newPlot('tempHumChart', data, layout, config);

};

// // Function to update chart with new data
// function updateChart(timestamps, sensorData) {
//     let temperatureCtx = document.getElementById('temperatureChart').getContext('2d');
//     let humidityCtx = document.getElementById('humidityChart').getContext('2d');
// 
//     let scales = {
//         x: {
//             type: 'time',
//             time: {
//                 parser: 'YYYY-MM-DD HH:mm:ss', // Specify the timestamp format
//                 unit: 'hour' // Adjust as needed based on your data resolution
//             }
//         },
//         y: {
//             type: 'linear',
//             display: true,
//             position: 'left',
//         },
//     };
//     let zoomOptions = {
//         pan: {
//             enabled: true,
//             mode: 'xy',
//             modifierKey: 'shift',
//         },
//         zoom: {
//             mode: 'xy',
//             wheel: {
//                 enabled: true,
//             },
//             pinch: {
//                 enabled: true
//             },
//             drag: {
//                 enabled: true,
//                 borderColor: 'rgb(54, 162, 235)',
//                 borderWidth: 1,
//                 backgroundColor: 'rgba(54, 162, 235, 0.3)'
//             },
//         }
//     };
//     let plotOpts = {
//         scales: scales,
//         plugins: {
//             zoom: zoomOptions,
//         }
//     };
// 
//     // Temperature chart
//     let temperatureChart = new Chart(temperatureCtx, {
//         type: 'line',
//         data: {
//             labels: timestamps,
//             datasets: Object.keys(sensorData).map((sensorId, index) => ({
//                 label: `${sensorId} Temperature`,
//                 data: sensorData[sensorId].temperature,
//                 borderColor: `rgb(${Math.random() * 255}, ${Math.random() * 255}, ${Math.random() * 255})`,
//                 backgroundColor: 'rgba(0, 0, 0, 0)',
//                 tension: 0.1
//             }))
//         },
//         options: plotOpts,
//     });
//     temperatureChart.options.plugins.zoom.onZoomComplete = function({ chart }) {
//         let min = chart.scales.x.min;
//         let max = chart.scales.x.max;
//         humidityChart.options.scales.x.min = min;
//         humidityChart.options.scales.x.max = max;
//         humidityChart.update();
//     };
// 
//     // Humidity chart
//     let humidityChart = new Chart(humidityCtx, {
//         type: 'line',
//         data: {
//             labels: timestamps,
//             datasets: Object.keys(sensorData).map((sensorId, index) => ({
//                 label: `${sensorId} Humidity`,
//                 data: sensorData[sensorId].humidity,
//                 borderColor: `rgba(${Math.random() * 255}, ${Math.random() * 255}, ${Math.random() * 255}, 0.5)`,
//                 backgroundColor: 'rgba(0, 0, 0, 0)',
//                 tension: 0.1
//             }))
//         },
//         options: plotOpts,
//     });
//     humidityChart.options.plugins.zoom.onZoomComplete = function({ chart }) {
//         let min = chart.scales.x.min;
//         let max = chart.scales.x.max;
//         temperatureChart.options.scales.x.min = min;
//         temperatureChart.options.scales.x.max = max;
//         temperatureChart.update();
//     };
// 
//     // Add event listeners for the buttons
//     document.getElementById('toggleZoom').addEventListener('click', () => {
//         zoomOptions.zoom.drag.enabled = !zoomOptions.zoom.drag.enabled;
//         temperatureChart.update();
//         humidityChart.update();
//     });
//     document.getElementById('togglePan').addEventListener('click', () => {
//         zoomOptions.pan.enabled = !zoomOptions.pan.enabled;
//         temperatureChart.update();
//         humidityChart.update();
//     });
//     document.getElementById('resetZoom').addEventListener('click', () => {
//         // Reset zoom for temperature chart
//         temperatureChart.options.scales.x.min = Math.min(...timestamps);
//         temperatureChart.options.scales.x.max = Math.max(...timestamps);
//         temperatureChart.options.scales.y.min = Math.min(...sensorData.map(sensor => Math.min(...sensor.temperature)));
//         temperatureChart.options.scales.y.max = Math.max(...sensorData.map(sensor => Math.max(...sensor.temperature)));
//         temperatureChart.update();
//         // Reset zoom for humidity chart
//         humidityChart.options.scales.x.min = Math.min(...timestamps);
//         humidityChart.options.scales.x.max = Math.max(...timestamps);
//         humidityChart.options.scales.y.min = Math.min(...sensorData.map(sensor => Math.min(...sensor.humidity)));
//         humidityChart.options.scales.y.max = Math.max(...sensorData.map(sensor => Math.max(...sensor.humidity)));
//         humidityChart.update();
//     });
// }

// Call the fetchDataAndUpdateChart function for a specific year and week when the page is loaded
window.onload = function () {
    fetchDataAndUpdateChart();
};
