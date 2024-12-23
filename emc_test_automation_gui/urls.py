# log_analysis_gui/urls.py
from django.urls import path
from .views import home, validation_rules, process_log_warnings, display_report, download_report, generate_schematic_image, test_config_gui, prediction_gui, get_Prediction, get_test_standards_data, set_test_standards_data, get_node_details

urlpatterns = [
    path('', home, name='home'),
    path('validation_rules/', validation_rules, name='validation_rules'),
    path('process_log_warnings/', process_log_warnings, name='process_log_warnings'),
    path('display_report/', display_report, name='display_report'),
    path('download_report/', download_report, name='download_report'),
    path('generate_schematic_image/', generate_schematic_image, name='generate_schematic_image'),
    path('get_test_data/', test_config_gui, name='test_config_gui'),
    path('prediction_gui/', prediction_gui, name='prediction_gui'),
    path('get_prediction_results/', get_Prediction, name='get_Prediction'),
    path('get_test_standards_data/', get_test_standards_data, name='get_test_standards_data'),
    path('set_test_standards_data/', set_test_standards_data, name='set_test_standards_data'),
    path('get_node_details/', get_node_details, name='get_node_details'),
    

]
