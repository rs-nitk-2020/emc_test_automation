# Project Structure for log_analysis_dashboard

This project is a single system that provides log analysis and generates an excel report using a Graphical User Interface (GUI) and whose parent project directory is the name of the github repository and this can be customized.

There are three modules in this project which are in the form three top-level directories or folders. They are

1. ***log_analysis_gui*** : This is the module which contains the UI files with 
    - **templates/log_analysis_gui** : contains html files.
    - **static/css** : contains css files.
    - **static/js** : contains js files.
    - **static/assets** : contains any image and media files.

2. ***log_analysis_api*** : This is the module which contains the core python logic to access environment based logs, analyze and process them and generate reports. 

    The description of the directories is as follows:
    - **src/services** : for the core process logic of file analysis with a group of functionalities contained in their own file. For example compiler_analysis_service.py has all functions related to compiler log analysis.
    - **src/utils** : has common reusable code such as file_utils.py (for file manipulation functionalities), log_utils for log creation and so on.
    - **tests/services**: has pyunit test cases for the respective service present in src/services
    - **tests/utils** : has pyunit test cases for the respective util functionality.
    - **src/config/properties.yaml** : contains the configurable properties for the applicaton.
    - **tests/config/properties.yaml** : contains the configurable properties for the applicaton test cases.
    - **src/data/Warnings/Misra Warnings** : has the log files for Misra warnings.
    - **src/data/Warnings/Compiler Warnings** : has the log files for Compiler warnings.
    - **tests/data/Warnings/Misra Warnings** : has the log files for Misra warnings for tests.
    - **tests/data/Warnings/Compiler Warnings** : has the log files for Compiler warnings for tests.
    - **logs** : has the application's log files.

3. ***log_analysis_dashboard*** : This module has the core Django configuration for rendering the frontend application defined in log_analysis_gui as a web application.

The application launches as a regular Django web application from the parent driectory using **python manage.py runserver** or can be launched as a ***windows desktop application using launch.bat***
