# log_analysis_gui/urls.py
from django.urls import path
from .views import home, validation_rules, process_log_warnings, display_report, download_report, generate_schematic_image, test_config_gui, get_test_standards_data, get_node_list

urlpatterns = [
    path('', home, name='home'),
    path('validation_rules/', validation_rules, name='validation_rules'),
    path('process_log_warnings/', process_log_warnings, name='process_log_warnings'),
    path('display_report/', display_report, name='display_report'),
    path('download_report/', download_report, name='download_report'),
    path('generate_schematic_image/', generate_schematic_image, name='generate_schematic_image'),
    path('get_test_data/', test_config_gui, name='test_config_gui'),
    path('get_test_standards_data/', get_test_standards_data, name='get_test_standards_data'),
    path('get_node_list/', get_node_list, name='get_node_list')

]
