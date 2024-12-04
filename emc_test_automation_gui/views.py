import base64
import json
import os
from django.shortcuts import render
from emc_test_automation_api import app_dashboard
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import FileSystemStorage

from emc_test_automation_dashboard import settings

# Create your views here.
def home(request):
    basic_gui_data = None
    log_dashboard = app_dashboard.EMCTestAutomationApi()
    basic_gui_data = log_dashboard.load_gui_basic_data()
    return render(request, 'home.html', basic_gui_data)

def validation_rules(request):
    log_dashboard = app_dashboard.EMCTestAutomationApi()
    basic_gui_data = log_dashboard.load_gui_basic_data()
    return JsonResponse(basic_gui_data)


def process_log_warnings(request):
    response_data = JsonResponse({})
    files_data = None
    log_dashboard = app_dashboard.EMCTestAutomationApi()

    if request.method == 'POST':
        warning_type = request.POST.get('warning_type')
        if warning_type in ['Compiler_Warnings', 'MISRA_Warnings']:
            files_data = request.FILES

            if warning_type == 'Compiler_Warnings':
                report_name, report_data, report_status, report_message = log_dashboard.process_compiler_warnings(files_data)
            else:  # 'MISRA_Warnings'
                report_name, report_data, report_status, report_message = log_dashboard.process_misra_warnings(files_data)

            response_data = {
                'report_name': report_name,
                'report_data': report_data,
                'report_status': report_status,
                'report_message': report_message
            }

    return JsonResponse(response_data, content_type='application/json', charset='utf-8')


def display_report(request):
    return render(request, 'report.html')

def download_report(request):
    # Decode the bytes object from the request body into a string and parse it as JSON
    request_data = json.loads(request.body.decode('utf-8'))

    # Assuming the request_data contains 'report_name' key
    report_name = request_data.get('report_name')
    log_dashboard = app_dashboard.EMCTestAutomationApi()
    report_path = log_dashboard.download_report(report_name)
    try:
        if os.path.exists(report_path):
            with open(report_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = f'attachment; filename={report_name}'
                return response
        else:
            return HttpResponse("File not found", status=404)
    except Exception as e:
        return HttpResponse(f"Error occurred while handling the file: {e}", status=500)

def generate_schematic_image(request):
    log_dashboard = app_dashboard.EMCTestAutomationApi()
    if request.method == 'POST' and request.FILES['file1']:
        asc_file = request.FILES['file1']

        # Define where to save the file, e.g., a subfolder under media
        custom_path = os.path.join(settings.BASE_DIR, 'emc_test_automation_api/data/Schematics/testx')  # Adjust the folder name or path as needed
        os.makedirs(custom_path, exist_ok=True)  # Ensure the directory exists

        # Define the full path to save the file, including its name
        file_path = os.path.join(custom_path, asc_file.name)

        # Write the file manually
        with open(file_path, 'wb+') as destination:
            for chunk in asc_file.chunks():
                destination.write(chunk)

        # Process the .asc file and generate PNG
        # (you should implement the logic to convert the .asc file to a PNG file)
        
        png_file_path = log_dashboard.generate_schematic_images([file_path])

        # Ensure the PNG file is accessible via a URL (e.g., in your 'media' folder)
        if png_file_path:
            file_data = png_file_path[0]['image']
            # Convert the binary data to a Base64 string
            base64_data = base64.b64encode(file_data).decode('utf-8')
            return JsonResponse({
                'status': 'success',
                'image': f'{base64_data}'
            })
        else:
            return JsonResponse({'error': 'Failed to generate PNG'}, status=400)
    return JsonResponse({'error': 'No file uploaded'}, status=400)




def test_config_gui(request):
    return render(request, 'test_standards_config.html')