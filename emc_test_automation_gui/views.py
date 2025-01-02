import base64
import json
import os
import csv
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

# from PyLTSpice import SimRunner, SpiceEditor, LTspice, RawRead, SimCommander
# def generate_netlist(asc_file):
#     sim = SimCommander(asc_file)
#     try:
#         sim.add_instruction('.tran 100u 100m 0 100u')
#         sim.run()
#     except Exception as e:
#         print(f"Error running simulation: {e}")
#         return None
    
#     netlist = asc_file.replace(".asc", ".net")
#     print("\n\n\n\n",netlist,"\n\n\n\n")
#     return str(netlist)


@csrf_exempt
def get_node_details(request):
    log_dashboard = app_dashboard.EMCTestAutomationApi()
    if request.method == 'POST' and request.FILES.get('file1'):
        asc_file = request.FILES['file1']
        request_id = request.POST.get('requestId')
        circuit_type = request.POST.get('circuitType')
        # Generate netlist path
        custom_path = os.path.join(settings.BASE_DIR, "emc_test_automation_api","data","Schematics",str(request_id),str(circuit_type))
        os.makedirs(custom_path, exist_ok=True)
        asc_file_path = os.path.join(custom_path,str(asc_file.name))
        print(f"ASC file path: {asc_file_path}")

        results = log_dashboard.get_node_details(asc_file_path)

        return JsonResponse({'status': 'success', 'nodes': results["nodes"], 'complete_node_data': results["complete_node_data"]})
    else:
        return JsonResponse({'status': 'error', 'message': 'No file uploaded'})
    
@csrf_exempt
def get_report_data(request):
    if request.method=='POST':
        body = json.loads(request.body)
        components = body.get('components',[])

        if not components:
            return JsonResponse({"error":"Invalid components list"},status=400)
        
        file_path = os.path.join(settings.BASE_DIR, "emc_test_automation_api","data","Schematics","12345","DUT","test_output.csv")

        if not os.path.exists(file_path):
            return JsonResponse({"error":"Invalid file path. CSV file not found at given path"},status=404)
        
        output_rows = []
        with open(file_path,'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if not row or len(row)!=3:  #check this logic once as the first two rows of the csv might have length 3 
                    continue
                elif any(component in  row[1] for component in components):
                    output_rows.append(row)
                    print(row,"\n")
        
        response_content = ""
        for row in output_rows:
            response_content+=",".join(map(str,row))+"\n"

        return JsonResponse({"csv_data":response_content})
    

@csrf_exempt
def get_table_data(request):
    if request.method=='POST':
        body = json.loads(request.body)
        node1 = body.get("node1")
        node2 = body.get("node2")
        section_id = body.get("SectionID")

        if section_id not in ["voltageSection", "currentSection", "powerSection", "frequencySection"]:
            return JsonResponse({"error": "Invalid SectionID"}, status=400)

        file_path = os.path.join(settings.BASE_DIR, "emc_test_automation_api","data","Schematics","12345","DUT","test_output.csv")

        if not os.path.exists(file_path):
            return JsonResponse({"error": "CSV file not found."}, status=404)

        summary_data = []
        with open(file_path, "r") as file:
            reader = csv.reader(file)
            # Skip to the "Summary Data" section
            for row in reader:
                if row and row[0].strip() == "Summary Data:":
                    break
            
            # Read the header for the "Summary Data"
            header = next(reader, [])
            # Create section maps. this can be used for the name section in the json response below 
            # section_map = {
            #     "voltageSection": ["Peak Voltage", "Average Voltage", "RMS Voltage"],
            #     "currentSection": ["Peak Current", "Average Current", "RMS Current"],
            #     "powerSection": [],  # power-related columns need to be added
            #     "frequencySection": []  # frequency related coluns need to be added
            # }

            print("Header:", header)
            print("Filtering rows for SectionID:", section_id)

            # Process the rows in the "Summary Data" section
            for row in reader:
                if not row or len(row) < 3:
                    continue
                
                parameter, node_or_component, value = row[0].strip(), row[1].strip(), row[2].strip()

                # Convert the value to a float if possible
                try:
                    value = float(value)
                except ValueError:
                    pass

                sections = {"currentSection":"current","voltageSection":"voltage","powerSection":"power","frequencySection":"frequency"}

                if sections[section_id] in parameter.lower() and (node_or_component==node1 or node_or_component==node2): # Make sure we match on the correct parameters for currentSection (case-insensitive) and also match the nodes which we are looking for
                    print(f"Matched: {parameter}")
                    summary_data.append({
                        "name": "Peak" if "peak" in parameter.lower() else "RMS" if "rms" in parameter.lower() else "Average", # might need to change this for frequency and power
                        "value": value,
                        "units": node_or_component.split("(")[0],  # Extract unit ("A" for current)
                        "totalDuration": 1.5,  # Assuming a fixed totalDuration for now. Need to check how to get this value
                        "units2": "us",       # Assuming a fixed units2 for now. Depends on the above.
                    })

                #ignore the following comments (its for debugging)
                # if section_id == "currentSection":
                # # Make sure we match on the correct parameters for currentSection (case-insensitive)
                #     if "current" in parameter.lower():
                #         print(f"Matched: {parameter}")
                #         summary_data.append({
                #             "name": "Peak" if "peak" in parameter.lower() else "RMS" if "rms" in parameter.lower() else "Average",
                #             "value": value,
                #             "units": node_or_component.split("(")[0],  # Extract unit ("A" for current)
                #             "totalDuration": 1.5,  # Assuming a fixed totalDuration for now
                #             "units2": "us",       # Assuming a fixed units2 for now
                #         })
                # elif section_id == "voltageSection":
                #     # Make sure we match on the correct parameters for voltageSection (case-insensitive)
                #     if "voltage" in parameter.lower():
                #         print(f"Matched: {parameter}")
                #         summary_data.append({
                #             "name": "Peak" if "peak" in parameter.lower() else "RMS" if "rms" in parameter.lower() else "Average",
                #             "value": value,
                #             "units": node_or_component.split("(")[0],  # Extract unit ("V" for voltage)
                #             "totalDuration": 1.5,  # Assuming a fixed totalDuration for now
                #             "units2": "us",       # Assuming a fixed units2 for now
                #         })
                # # need to add code for frequency and power sections
        
        if not summary_data:
            return JsonResponse({"error": "No data found for the given parameters."}, status=404)
        return JsonResponse(summary_data, safe=False)

@csrf_exempt
def get_graph_data(request):
    print("hello")

    
@csrf_exempt
def run_simulation(request):
    log_dashboard = app_dashboard.EMCTestAutomationApi()
    if request.method=='POST':
        data = json.loads(request.body)
        port1 = data.get('pulseParams').get('Port1')
        port2 = data.get('pulseParams').get('Port2')
        port3 = data.get('pulseParams').get('Port3')
        iso_type = data.get('isoType')
        default_iso_fields = log_dashboard.iso_fields_selector(iso_type)
        user_iso_fields = data.get("isoFields")
        for item in default_iso_fields:  #checks if the value sent by the user is different from the default, if so, then that value is changed
            key = item.get("name")
            if key in user_iso_fields:
                item["value"] = user_iso_fields[key]

        existing_keys = {item["name"] for item in default_iso_fields}  #if some parameter sent by the user is not present in the default list, then it is appended to the default list
        for key,val in user_iso_fields.items():
            if key not in existing_keys:
                default_iso_fields.append({"name": key, "value": val})

        # Ua = data.get('isoFields').get('Ua')
        # Us = data.get('isoFields').get('Us')
        # Ri = data.get('isoFields').get('Ri')
        # td = data.get('isoFields').get('td')
        # tr = data.get('isoFields').get('tr')
        # t1 = data.get('isoFields').get('t1')
        # t2 = data.get('isoFields').get('t2')
        # t3 = data.get('isoFields').get('t3')
        # t = data.get('isoFields').get('t')
        # Ext_res = data.get('isoFields').get('extRes') 
        stop_time_val = data.get('runParams').get('stopTime').get('value')
        stop_time_unit = data.get('runParams').get('stopTime').get('unit')
        save_time_val = data.get('runParams').get('timeToStartSavingData').get('value')
        save_time_unit = data.get('runParams').get('timeToStartSavingData').get('unit')
        max_time_val = data.get('runParams').get('maximumTimestep').get('value')
        max_time_unit = data.get('runParams').get('maximumTimestep').get('unit')
        measurements = ""
        asc_file_path = os.path.join(settings.BASE_DIR, "emc_test_automation_api","data","Schematics","12345","DUT","circuit.net")
        csv_file_path = os.path.join(settings.BASE_DIR, "emc_test_automation_api","data","Schematics","12345","DUT","test_output.csv")

        #debug - Ua,Us,Ri,td,tr,t1,t2,t3,t,Ext_res

        arr = [asc_file_path,csv_file_path,iso_type,port1,port2,port3,default_iso_fields,stop_time_val,stop_time_unit,save_time_val,save_time_unit,max_time_val,max_time_unit,measurements]
        for item in arr:
            print(item,"\n")

        log_dashboard.run_simulation(asc_file_path,csv_file_path,iso_type,port1,port2,port3,default_iso_fields,stop_time_val,stop_time_unit,save_time_val,save_time_unit,max_time_val,max_time_unit,measurements)

        return HttpResponse("Hello: success")