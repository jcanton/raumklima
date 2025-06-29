const sensorNames = [
    'Kitchen',
    'Livingrm',
    'Studio',
    'Bedrm',
    'Bathrm',
    'Balcony',
    'Window',
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

    // Dynamically set width and height based on window size
    const chartWidth = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
    // Height is proportional to width, but not less than 400px
    const chartHeight = Math.max(Math.round(chartWidth * 1.1), 400);

    var layout = {
        title: '',
        height: chartHeight,
        width: chartWidth,
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

    // Optionally, update chart size on window resize
    window.onresize = function() {
        const newWidth = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
        const newHeight = Math.max(Math.round(newWidth * 1.1), 400);
        Plotly.relayout('tempHumChart', {width: newWidth, height: newHeight});
    };
};

// Call the fetchDataAndUpdateChart function for a specific year and week when the page is loaded
window.onload = function () {
    fetchDataAndUpdateChart();
};
