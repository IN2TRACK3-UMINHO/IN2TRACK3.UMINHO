// The markov_prediction variable is passed from Flask
console.log(markov_prediction);
const indicators = Object.keys(markov_prediction);

// Call the function to create chart when the page loads
for (let i = 0; i < indicators.length; i++) {
    if (i===0) {
        createChart('predictionChart', markov_prediction[indicators[i]]['prediction']['Time'], markov_prediction[indicators[i]]['prediction']['IC'], 'Year', 'IC', indicators[i]);
    }
    else {
        let color = 'rgb(225,106,2)'
        if (i > 1){
            color = "#" + Math.floor(Math.random()*16777215).toString(16)
        }
        addPlotToChart('predictionChart', markov_prediction[indicators[i]]['prediction'], indicators[i], color)
    }
}

function createChart(canvas_name, data_x, data_y, x_label, y_label, data_title) {
    console.log(`DEBUGGING - createChart - ${data_title}`);
    
	// Create a Chart.js chart
	let predictionChart = Chart.getChart(canvas_name);
	if (predictionChart) {
		// If the chart already exists, update it with new data
		predictionChart.data.labels = data_x;
		predictionChart.data.datasets[0].data = data_y;
		predictionChart.data.datasets[0].label = data_title;
		predictionChart.options.scales.y.title.text = y_label;
		predictionChart.update();
	} else {
		// If the chart doesn't exist, create a new one
		const ctx = document.getElementById(canvas_name).getContext('2d');
		const predictionChart = new Chart(ctx, {
			type: 'line',
			data: {
			  labels: data_x,
			  datasets: [{
				label: data_title,
				data: data_y,
				backgroundColor: 'rgb(161, 26, 27)',
				borderColor: 'rgb(161, 26, 27)',
				borderWidth: 1
			  }]
			},
			options: {
			  responsive: true,
			  scales: {
				x: {
				  title: {
					display: true,
					text: x_label,
				  }
				},
				y: {
				  title: {
					display: true,
					text: y_label,
				  }
				},
			  },
			  //maintainAspectRatio: false
			}
		}
	)};
}

function addPlotToChart(canvas_name, markov_prediction, data_title, color){
	new_chart = Chart.getChart(canvas_name);
	
	// Get the chart data
	const chartData = new_chart.data;
	
	// Convert to data array
    var data = [];
    for (let i = 0; i < markov_prediction['Time'].length; i++) {
      data.push({ x: markov_prediction['Time'][i], y: markov_prediction['IC'][i] });
    }
	
	// Add a new dataset
		const result = {
		  label: data_title,
		  data: data,
		  backgroundColor: color,
		  borderColor: color,
		  borderWidth: 1
		};
	
	chartData.datasets.push(result);
    
	// Update the chart
	new_chart.update();
};


const maintenanceDiv = document.getElementById('maintenance-div');
addActionFields(maintenanceDiv);

function creatNumMaintenanceSelect(div){
    // Create and append the "Select the number of maintenance actions" dropdown
    const numMaintenanceSelect = document.createElement('select');
    numMaintenanceSelect.id = 'numMaintenanceSelect';

    const option_1 = document.createElement("option");
    option_1.value = 'numMaintenance';
    option_1.text = 'Select the number of maintenance actions:';
    numMaintenanceSelect.appendChild(option_1);
    
    for (let i = 1; i <= 5; i++) {
        const option1 = document.createElement("option");
        option1.value = i;
        option1.text = i;
        numMaintenanceSelect.appendChild(option1);
    };
    
    div.appendChild(numMaintenanceSelect);
    
    return numMaintenanceSelect
    
};

function addActionFields(div) {
    const numMaintenanceSelect = creatNumMaintenanceSelect(div);
    
    // Create and append an event listener to generate the form on selection change
    numMaintenanceSelect.addEventListener('change', createMaintenanceForm);
    
    // Create a container div for the form
    const formContainer = document.createElement('div');
    formContainer.id = 'formContainer';
    
    // Function to create the maintenance form based on the selected number of actions
    function createMaintenanceForm() {
        const numActions = parseInt(numMaintenanceSelect.value);
        const time_horizon = 50;
        
        // Clear any previous form elements
        formContainer.innerHTML = '';
        
        for (let i = 0; i < numActions; i++) {
            const formGroup = document.createElement('div');
            
            // Create a time selection dropdown
            const timeSelect = document.createElement('select');
            timeSelect.id = "time-maintenance-" + (i+1);
            for (let j = 0; j < time_horizon; j++) {
                const timeOption = document.createElement("option");
                if (j == 0) {
                    timeOption.value = "";
                    timeOption.text = "Select time:";
                } else {
                    timeOption.value = j;
                    timeOption.text = j;
                }
                
                timeSelect.add(timeOption);
            }

            // Create an action selection dropdown
            const actionSelect = document.createElement('select');
            actionSelect.id = "maintenance-action-" + (i+1);
            const actionOption_ = document.createElement('option');
            actionOption_.value = "";
            actionOption_.textContent = "Select action:";
            actionSelect.appendChild(actionOption_);
            
            for (const option of maintenanceActions) {
                const actionOption = document.createElement('option');
                actionOption.value = option.name;
                actionOption.textContent = option.name;
                actionSelect.appendChild(actionOption);
            }
            
            formGroup.appendChild(timeSelect);
            //formGroup.appendChild(document.createElement('br'));
            formGroup.appendChild(actionSelect);
            formContainer.appendChild(formGroup);
            
        }
    }
    
    // Append elements to the infoDiv
    div.appendChild(formContainer);
    
    // Create and append a button to submit the form data
    const submitButton = document.createElement('button');
    submitButton.textContent = 'Submit Form';
    submitButton.addEventListener('click', postMaintenanceToServer);
    
    // Append the submit button to the infoDiv
    div.appendChild(submitButton);
}

// Function to send data to the server via a POST request
async function postMaintenanceToServer() {
    const numActions = parseInt(numMaintenanceSelect.value);

    // // Create an array to store the form data
    let maintenanceData = {};
    
    for (let i = 0; i < numActions; i++) {
        
        const timeSelect = document.getElementById("time-maintenance-" + (i+1));
        const actionSelect = document.getElementById("maintenance-action-" + (i+1));

        // Get the selected time and action values
        const timeValue = timeSelect.value;
        const actionValue = actionSelect.value;

        // Push the data for each action to the maintenanceData
        maintenanceData[timeValue] = actionValue;
    }

    // Send the formData to the server via a POST request
    // Fetch request for prediction based on road properties
    
    const formData = new FormData();
    formData.append('maintenanceScenario', JSON.stringify(maintenanceData));

    const response = await fetch('/maintenance', {method: 'POST',
                                                  body: formData});
    const prediction = await response.json();
    
    // setChartMaintenanceMode(roadSelected, prediction);
    
    const chart = Chart.getChart('maintenanceChart');
    
    if (chart){
        chart.data.datasets.pop();
    };
    
    const indicators = Object.keys(prediction);
    
    for (let i = 0; i < indicators.length; i++) {
        if (i===0) {
            createChart('maintenanceChart', prediction[indicators[i]]['Time'], prediction[indicators[i]]['IC'], 'Year', 'IC', indicators[i]);
        }
        else {
            let color = 'rgb(225,106,2)'
            if (i > 1){
                color = "#" + Math.floor(Math.random()*16777215).toString(16)
            }
            addPlotToChart('maintenanceChart', prediction[indicators[i]], indicators[i], color)
        }
    }
};