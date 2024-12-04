$(document).ready(function() {
    // Disable submit button on page load
    $('#submitBtn').prop('disabled', true);

    // Enable submit button when form fields are not empty
    $('#warningForm input').on('input', function() {
        var allFieldsFilled = true;

        // Check if any input field is empty
        $('#warningForm input').each(function() {
            if ($(this).val().trim() === '') {
                allFieldsFilled = false;
                return false;  // Break the loop if any field is empty
            }
        });

        // Enable or disable the submit button based on field values
        $('#submitBtn').prop('disabled', !allFieldsFilled);
    });
});

var validationData = {};
var discardedFiles = [];
var selectedFiles = [];
var selectedWarningType = "";
$(document).ready(function() {
  $.ajax({
      url: '/validation_rules/',  // Replace with your Django view endpoint
      method: 'GET',
      success: function(response) {
          // Validation rules/data received from the backend
          // Use this data for client-side validation
          validationData = response;
          
      },
      error: function(error) {
          console.log('Error fetching validation rules:', error);
      }
  });
});
function displaySelected(){
  validateInput();
}

// Get the CSRF token from the cookie (if using cookies for CSRF protection)
function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        .split('=')[1];

    return cookieValue;
}

function validateInput(){
  event.preventDefault();
  discardedFiles = [];
  selectedFiles = [];
  // Retrieve the selected folder
  var selectedFolder = document.getElementById('ipFileUpload');

  // Display the selected folder path (customize this part)
  // Get the selected files
  selectedFiles = selectedFolder.files;
  var selectedOptionFilePatterns = [];
  
  // Display information about selected files
  if (selectedFiles.length > 0) {
    document.getElementById('lblMessage').innerHTML = ""
    var fileList = '<br>';
    var discardedFilesList = '<br>';
    let selectedFilesCtr = 0;
    let discardedFilesCtr = 0;
    var filepathDisplayCharsLimit = 10;
    var selectElement = document.getElementById('ddnLogAnalysisOptions');
    var selectedOption = selectElement.options[selectElement.selectedIndex];
    var selectedOptionValue = selectedOption.value;
    selectedWarningType = selectedOption.id;
    
    selectedOptionFilePatterns = validationData.emc_test_automation_valid_file_patterns[selectedOption.id].slice();
    
    // Selects options provided from backend, shows display values instead of option selected
    selectElement.addEventListener('change', function() {
      selectedOption = selectElement.options[selectElement.selectedIndex];
      selectedOptionValue = selectedOption.value;
      selectedOptionFilePatterns = validationData.emc_test_automation_valid_file_patterns[selectedOption.id].slice();
      selectedWarningType = selectedOption.id;
    });
             
              
    for (var i = 0; i < selectedFiles.length; i++) {
      file_path = selectedFiles[i].webkitRelativePath;
      if (file_path > filepathDisplayCharsLimit) {
        // Truncate the path to 50 characters and append '...'
        file_path = file_path.slice(0, filepathDisplayCharsLimit) + '...';
      }
      if (includesAnyString(selectedFiles[i].webkitRelativePath, selectedOptionFilePatterns)){
        fileList += file_path+'<br>';
        selectedFilesCtr += 1;
      }else{
        discardedFilesList += file_path+'<br>';
        discardedFiles.push(selectedFiles[i].webkitRelativePath.split('/').pop());
        discardedFilesCtr += 1;
      }
    }
    if (fileList.length>4){
      document.getElementById('lblMessage').innerHTML = 'Selected Files for Analysis: ' + selectedFilesCtr + fileList;
    }
    if (discardedFilesList.length>4){
      document.getElementById('lblMessage').innerHTML += '<br>Files discarded from Analysis due to invalid format: ' +  discardedFilesCtr +discardedFilesList;
    }
    if (fileList.length == 0 && discardedFilesList.length == 0) {
      document.getElementById('lblMessage').innerHTML = 'No files present in selected folder.';
    }
    
  
  }
}

function includesAnyString(path, stringsList) {
  const filename = path.split('/').pop(); // Extract filename from path
  const prefix = filename.split('-')[0]; // Extract the prefix before the first hyphen
  const underscoreCount = (prefix.match(/_/g) || []).length; // Count underscores in the prefix
  // Check conditions
  if ((underscoreCount <= 1) && (stringsList.some(str => path.includes(str)))) {
      return true; 
  } else {
      return false;
  }
}

function submitForm() {
  validateInput();

  document.getElementById('submitBtn').disabled = true;
  document.getElementById('submitBtn').innerHTML = 'ANALYSING...';

  // Get the selected files from the input element
  var filteredFiles = removeFilesByFilename(discardedFiles);

  // Create a FormData object to store files
  var formData = new FormData();

  // Append each selected file to the FormData object
  for (var i = 0; i < filteredFiles.length; i++) {
      formData.append('files[]', filteredFiles[i]);
  }

  formData.append('warning_type', selectedWarningType);
  document.getElementById('lblMessage').innerHTML = filteredFiles.length +' files uploaded successfully. Processing logs for '+ selectedWarningType + '....';

  // Make a POST request to send files to the backend
  fetch('/process_log_warnings/', {
      method: 'POST',
      headers: {
          'X-CSRFToken': getCSRFToken()
      },
      body: formData
  })
  .then(response => {
      // Handle the response from the backend
      return response.json();
  })
  .then(data => {
    // Redirect to a new page using window.location.href
    localStorage.setItem('jsonData', JSON.stringify(data));
    window.location.href = 'display_report/';
    
  })
  .catch(error => { 
      // Handle any errors that occurred during the fetch
      document.getElementById('lblMessage').innerHTML = 'Error uploading files:' + error;
      document.getElementById('submitBtn').disabled = false;
      document.getElementById('submitBtn').innerHTML = 'ANALYSE';
  });
}

// Function to remove specific files by filename
function removeFilesByFilename(discardedFiles) {
  return Array.from(selectedFiles).filter(file => !discardedFiles.includes(file.name));
}

function initialize() {
  // Set up event listener for when the user navigates away from the page
  window.addEventListener('unload', resetFields);
}

function resetFields() {
  document.getElementById('warningForm').reset(); // Reset the form
}
