const resultsResponseData = JSON.parse(localStorage.getItem('jsonData'));

function loadReport(){
  var keys = Object.keys(resultsResponseData.report_data);
  var reportData = resultsResponseData.report_data;
  var reportMessage = resultsResponseData.report_message;

  function populateResultsTable(key, reportData) {
    var tableContainer = document.getElementById('resultsTable');
    while (tableContainer.firstChild) {
      tableContainer.removeChild(tableContainer.firstChild);
    }
    var table = document.createElement('table');
    table.id = 'tblResults';
    var thead = document.createElement('thead');
    var tbody = document.createElement('tbody');

    var headerRow = thead.insertRow(0);
    var headers = Object.keys(reportData[key]);
    headers.forEach(function (headerText) {
      var th = document.createElement('th');
      th.textContent = headerText;
      th.setAttribute('scope', 'col'); // Set the scope attribute
      headerRow.appendChild(th);
    });

    var dataValues = Object.values(reportData[key]);

    // Assuming all rows have the same number of columns
    for (var i = 0; i < dataValues[0].length; i++) {
      var dataRow = tbody.insertRow();
      dataValues.forEach(function (rowData) {
        var cell = dataRow.insertCell();
        cell.textContent = rowData[i];
      });
    }

    // Append the table parts to the table
    table.appendChild(thead);
    table.appendChild(tbody);
    table.classList.add("table");



    document.getElementById('resultsTable').appendChild(table);
  }

  var primaryDisplayKey = "";

  // Create buttons for each key in the parsed JSON
  keys.forEach(function (key, index) {
    var button = document.createElement('button');
    button.id = key;
    button.innerHTML = key;
    button.classList.add("custom-group-btn");
    button.addEventListener('click', function (event) {
      if (event.target.tagName === 'BUTTON') {
        var buttonId = event.target.id;
        populateResultsTable(key, reportData);
      }
    });
    document.getElementById('reportMenu').appendChild(button); // Append the button to the body or any desired container

    //  Create a table for the first key
    if (index === 0) {
      primaryDisplayKey = key;
    }
  });

  document.getElementById("lblMessage").innerHTML = reportMessage
  populateResultsTable(primaryDisplayKey, reportData);

}

// Get the CSRF token from the cookie (if using cookies for CSRF protection)
function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        .split('=')[1];

    return cookieValue;
}

// Download the report
function downloadReport(resultsResponseData) {
    // Make a POST request to send files to the backend
    fetch('/download_report/', {
          method: 'POST',
          headers: {
              'X-CSRFToken': getCSRFToken()
          },
          body: JSON.stringify({'report_name': resultsResponseData.report_name})
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.blob();
      })
      .then(blob => {
        console.log("Test "+ blob)
        // Create a URL for the blob object
        const url = window.URL.createObjectURL(blob);
        // Create an anchor element
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', resultsResponseData.report_name); // Set filename
        link.style.display = 'none';
  
        // Append the anchor element to the body
        document.body.appendChild(link);
  
        // Trigger a click on the anchor element
        link.click();
  
        // Clean up
        document.body.removeChild(link);
      })
      .catch(error => { 
          // Handle any errors that occurred during the fetch
          document.getElementById('lblMessage').innerHTML = 'Error uploading files:' + error;
          document.getElementById('submitBtn').disabled = false;
          document.getElementById('submitBtn').innerHTML = 'ANALYSE';
      })
  }