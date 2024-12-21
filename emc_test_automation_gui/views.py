import base64
import json
import os
from django.shortcuts import render
from emc_test_automation_api import app_dashboard
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import FileSystemStorage

from emc_test_automation_dashboard import settings

from django.views.decorators.csrf import csrf_exempt

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
        print(f"Test check {request}")
        asc_file = request.FILES['file1']
        request_id = request.POST.get('requestId')
        circuit_type = request.POST.get('circuitType')

        # Define where to save the file, e.g., a subfolder under media
        custom_path = os.path.join(settings.BASE_DIR, f'emc_test_automation_api/data/Schematics/{request_id}/{circuit_type}')  # Adjust the folder name or path as needed
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
    return render(request, 'test_stnadard_page.html')

def prediction_gui(request):
    return render(request, 'prediction.html')

def get_Prediction(request):
    log_dashboard = app_dashboard.EMCTestAutomationApi()
    
    if request.method == 'POST':
        inputs = [request.POST.get('Component Position'), request.POST.get('Component Value'), request.POST.get('Input Voltage'), request.POST.get('Input Current')]
        results =  log_dashboard.getPrediction(inputs)
        return JsonResponse({'status': results['status'], 'predictions': results['predictions']})

def get_test_standards_data(request):
    if request.method == 'GET':
        try:
            json_file_path = 'emc_test_automation_gui/test_data.json'
            with open(json_file_path, 'r') as f:
                data = json.load(f)
            return JsonResponse(data)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt  #TODO: Remove this decorator in production
def set_test_standards_data(request):
    if request.method == 'POST':
        print(request.POST.get('data'))
        try:
            json_file_path = 'emc_test_automation_gui/test_data.json'
            data = json.loads(request.POST.get('data'))
            with open(json_file_path, 'w') as f:
                json.dump(data, f, indent=4)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=500)


from PyLTSpice import SimRunner, SpiceEditor, LTspice, RawRead, SimCommander
def generate_netlist(asc_file):
    # if request.method == 'POST' and request.FILES['file1']:
    # asc_file = request.FILES['file1']
    sim = SimCommander(asc_file)
    sim.add_instruction('.tran 100u 100m 0 100u')
    sim.run()
    netlist = asc_file.replace(".asc", ".net")
    search_path='.'
    for root, dirs, files in os.walk(search_path):
        if netlist in files:
            return os.path.join(root, netlist)

    print(f"Netlist file not found {netlist}") 
    return None

def get_node_list(request):
    if request.method == 'POST' and request.FILES['file1']:
        asc_file = request.FILES['file1']

        request_id = request.POST.get('requestId')
        circuit_type = request.POST.get('circuitType')

        custom_path = os.path.join(settings.BASE_DIR, f'emc_test_automation_api/data/Schematics/{request_id}/{circuit_type}')  # Adjust the folder name or path as needed
        os.makedirs(custom_path, exist_ok=True)  # Ensure the directory exists

        # Define the full path to save the file, including its name
        file_path = os.path.join(custom_path, asc_file.name)

        net_list = generate_netlist(file_path)
        print(net_list)
        # Set to store unique nodes
        nodes = set()

        # Read the netlist file
        with open(net_list, 'r') as file:
            for line in file:
                # Skip empty lines or comments
                line = line.strip()
                if not line or line.startswith('*'):
                    continue

                # Split the line into words (assuming netlist format)
                words = line.split()
                
                # Extract nodes (ignore the first word, which is usually the component name)
                for word in words[1:len(words)-1]:
                    if word.upper() not in {"GND", "0"}:  # Exclude GND and 0
                        nodes.add(word)
        
        return JsonResponse({'status': 'success','nodes': list(nodes)})