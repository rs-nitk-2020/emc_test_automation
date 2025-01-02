import numpy as np
import pandas as pd
import os
import time
import glob
from scipy.fft import fft, fftfreq
from PyLTSpice import SimRunner, SpiceEditor, LTspice, RawRead, SimCommander

class Circuit_Simulator:
    def __init__(self):
        pass

    @staticmethod
    def iso_fields_selector(iso_type):
        if iso_type=="ISO1 12V":
            return [
                { "name": "Ua", "value": "13.5" },
                { "name": "Us", "value": "-150" },
                { "name": "Ri", "value": "10" },
                { "name": "td", "value": "2m" },
                { "name": "tr", "value": "1u" },
                { "name": "t1", "value": "0.5" },
                { "name": "t2", "value": "200m" },
                { "name": "t3", "value": "50u" },
                { "name": "t", "value": "1m" },
                { "name": "Ext_res", "value": "10" } ]
        elif(iso_type=="ISO1 24V"):
            return [
                { "name": "Ua", "value": "27" },
                { "name": "Us", "value": "-600" },
                { "name": "Ri", "value": "50" },
                { "name": "td", "value": "1m" },
                { "name": "tr", "value": "3u" },
                { "name": "t1", "value": "0.5" },
                { "name": "t2", "value": "200m" },
                { "name": "t3", "value": "50u" },
                { "name": "t", "value": "1m" } ]
        elif(iso_type=="ISO2a 12V"):
            return [
                { "name": "Ua", "value": "13.5" },
                { "name": "Us", "value": "112" },
                { "name": "Ri", "value": "2" },
                { "name": "td", "value": "0.05m" },
                { "name": "tr", "value": "1u" },
                { "name": "t1", "value": "0.2" },
                { "name": "t", "value": "1m" } 
            ]
        elif(iso_type=="ISO2a 24V"):
            return  [
                { "name": "Ua", "value": "27" },
                { "name": "Us", "value": "112" },
                { "name": "Ri", "value": "2" },
                { "name": "td", "value": "0.05m" },
                { "name": "tr", "value": "1u" },
                { "name": "t1", "value": "0.2" },
                { "name": "t", "value": "1m" }
            ]
        elif(iso_type=="ISO2b 12V"):
            return [
                { "name": "Ua", "value": "13.5" },
                { "name": "Us", "value": "10" },
                { "name": "Ri", "value": "0.05" },
                { "name": "td", "value": "0.2" },
                { "name": "t12", "value": "1m" },
                { "name": "tr", "value": "1m" },
                { "name": "t6", "value": "1m" },
                { "name": "trep", "value": "5" },
                { "name": "ton", "value": "1" },
                { "name": "t0", "value": "1m" }   #check this once (if t and t0 mean the same thing)
            ]
        elif(iso_type=="ISO2b 24V"):
            return  [
                { "name": "Ua", "value": "27" },
                { "name": "Us", "value": "20" },
                { "name": "Ri", "value": "0.05" },
                { "name": "td", "value": "0.2" },
                { "name": "t12", "value": "1m" },
                { "name": "tr", "value": "1m" },
                { "name": "t6", "value": "1m" },
                { "name": "trep", "value": "5" },
                { "name": "ton", "value": "1" },
                { "name": "t0", "value":"1m" }
            ]
        elif(iso_type=="ISO3a 12V"):
            return [
                { "name": "Ua", "value": "13.5" },
                { "name": "Us", "value": "-300" },
                { "name": "Ri", "value": "50" },
                { "name": "td", "value": "150n" },
                { "name": "tr", "value": "5n" },
                { "name": "t1", "value": "100u" },
                { "name": "t0", "value": "1m" },
                { "name": "t4", "value": "10m" },
                { "name": "t5", "value": "90m" }
            ]
        elif(iso_type== "ISO3a 24V"):
            return [
                { "name": "Ua", "value": "27" },
                { "name": "Us", "value": "-220" },
                { "name": "Ri", "value": "50" },
                { "name": "td", "value": "150n" },
                { "name": "tr", "value": "5n" },
                { "name": "t1", "value": "100u" },
                { "name": "t0", "value": "1m" },
                { "name": "t4", "value": "10m" },
                { "name": "t5", "value": "90m" }
            ]
        elif(iso_type=="ISO3b 12V"):
            return  [
                { "name": "Ua", "value": "13.5" },
                { "name": "Us", "value": "150" },
                { "name": "Ri", "value": "50" },
                { "name": "td", "value": "150n" },
                { "name": "tr", "value": "5n" },
                { "name": "t1", "value": "100u" },
                { "name": "t0", "value": "1m" },
                { "name": "t4", "value": "10m" },
                { "name": "t5", "value": "90m" }
            ]
        elif(iso_type== "ISO3b 24V"):
            return [
                { "name": "Ua", "value": "27" },
                { "name": "Us", "value": "300" },
                { "name": "Ri", "value": "50" },
                { "name": "td", "value": "150n" },
                { "name": "tr", "value": "5n" },
                { "name": "t1", "value": "100u" },
                { "name": "t0", "value": "1m" },
                { "name": "t4", "value": "10m" },
                { "name": "t5", "value": "90m" }
            ]
        elif(iso_type=="ISO5 12V"):
            return [
                { "name": "Ua", "value": "14" },
                { "name": "Us", "value": "101" },
                { "name": "UsClamp", "value": "35" },
                { "name": "Ri", "value": "0.5" },
                { "name": "td", "value": "40m" },
                { "name": "tr", "value": "5m" },
                { "name": "t0", "value": "1" }
            ]
        elif(iso_type=="ISO5 24V"):
            return [
                { "name": "Ua", "value": "28" },
                { "name": "Us", "value": "202" },
                { "name": "UsClamp", "value": "58" },
                { "name": "Ri", "value": "1" },
                { "name": "td", "value": "100m" },
                { "name": "tr", "value": "5m" },
                { "name": "t0", "value": "1" }
            ]
        else: 
            print("Invalid iso type - no iso fields available, empty array returned")
            return []


    @staticmethod
    def get_latest_raw_file(base_name, directory="."):
        """
        Get the latest `.raw` file matching the base name within a directory.

        :param base_name: Base name of the .asc file (e.g., 'res_divider').
        :param directory: Directory to search for raw files.
        :return: Path to the latest .raw file or None if not found.
        """
        pattern = os.path.join(directory, f"{base_name}*.raw")
        matching_files = glob.glob(pattern)
        if not matching_files:
            return None
        # Sort files by modification time and return the latest
        latest_file = max(matching_files, key=os.path.getmtime)
        return latest_file

    @staticmethod
    def wait_for_latest_raw_file(asc_file, timeout=30, check_interval=1):
        """
        Wait for the latest `.raw` file associated with a given `.asc` file.

        :param asc_file: Name of the .asc file.
        :param timeout: Maximum wait time in seconds.
        :param check_interval: Interval to check for the file in seconds.
        :return: Path to the latest .raw file or None if not found.
        """
        base_name = os.path.splitext(asc_file)[0]  # Remove .asc extension
        start_time = time.time()
        print(base_name)
        while True:
            latest_raw_file = Circuit_Simulator.get_latest_raw_file(base_name)
            if latest_raw_file:
                print(f"Latest .raw file found: {latest_raw_file}")
                return latest_raw_file
            if timeout and time.time() - start_time > timeout:
                print(f"Timeout reached. No .raw file found for {asc_file}.")
                return None
            time.sleep(check_interval)

# pulse = 'Pulse1_12V'
# node = 'Vin'
# Ri = 1
# sim.add_instruction(f'XU1 node1 0 {pulse} Ri=1u')
# sim.add_instruction(f'Ri node1 {node} {Ri}')
# sim.add_instruction('.tran 0.1u 1 0 0.1u')
# sim.add_instruction('.lib ISO7637-2.lib')
# sim.run()

# asc_file = "res_divider.asc"
# output_csv = "res_divider.csv"
    @staticmethod
    def run_simulation_func(asc_file_path,csv_file_path,iso_type,port1,port2,port3,default_iso_fields,stop_time_value,stop_time_unit,save_time_value,save_time_unit,max_time_value,max_time_unit,measurements):
        asc_file = asc_file_path
        output_csv = csv_file_path
        if not os.path.exists(asc_file):
            print("ASC file not found at given path")
        elif not os.path.exists(output_csv):
            print("CSV file does not exist at given path")
        if os.path.exists(asc_file):
            print(f"Processing {asc_file}...")
            try:
                # Create simulation object and run
                sim = SimCommander(asc_file)
                pulse_name_dictionary = {
                    "ISO1 12V": "Pulse1_12V",   
                    "ISO1 24V": "Pulse1_24V",
                    "ISO2a 12V": "Pulse2a_12V",
                    "ISO2a 24V": "Pulse2a_24V",
                    "ISO2b 12V": "Pulse2b_12V",
                    "ISO2b 24V": "Pulse2b_24V",
                    "ISO3a 12V": "Pulse3a_12V",
                    "ISO3a 24V": "Pulse3a_24V",
                    "ISO3b 12V": "Pulse3b_12V",
                    "ISO3b 24V": "Pulse3b_24V",
                    "ISO5 12V": "Pulse5_12V",
                    "ISO5 24V": "Pulse5_24V"

                }
                pulse = pulse_name_dictionary[iso_type] #'Pulse1_12V' ......iso type
                node = 'Vin' #port1, create 3 for 3 ports

                #creating instructions from default_iso_fields
                str1 = f'XU1 {port1} {port3} {pulse} Ri=1u'
                for field in default_iso_fields:
                    str1=str1 + ' ' + f'{field["name"]}' + '=' + f'{field["value"]}'
                Ri=""
                for item in default_iso_fields:
                    if(item["name"]=="Ri"):
                        Ri = item["value"]

                sim.add_instructions(str1)
                #sim.add_instructions(f'XU1 {port1} {port3} {pulse} Ua={Ua} Us={Us} Ri=1u td={td} tr={tr} t1={t1} t2={t2} t3={t3} t={t}')
                sim.add_instructions(f'Ri {port1} {port2} {Ri}')
                sim.add_instruction(f'.tran 100u {stop_time_value}{stop_time_unit} {save_time_value}{save_time_unit} {max_time_value}{max_time_unit}')  #100m-stop time    0-time to start saving data    2nd-100u-maximum time stamp   firsty one-100u pass tehse values from the user like above
                # sim.add_instruction('.op')
                sim.add_instruction('.lib ISO7637-2.lib')
                sim.run()
                # Wait for the .raw file
                raw_file = Circuit_Simulator.wait_for_latest_raw_file(asc_file, timeout=30)
                if not raw_file:
                    print(f"No .raw file generated for {asc_file}. Skipping...")

                raw_data = RawRead(raw_file)
                print(output_csv)
                # csv_file = raw_data.to_csv(output_csv)
                time_data = raw_data.get_trace('time')  # Extract the time axis data
                data_dict = {"time": time_data.get_wave(0)}  # Initialize the dictionary with time

                # Extract all other signals
                for trace_name in raw_data.get_trace_names():
                    if trace_name != 'time':  # Skip time since it's already included
                        trace = raw_data.get_trace(trace_name)
                        data_dict[trace_name] = trace.get_wave(0)  # Extract waveform data

                # Convert the data to a pandas DataFrame
                df = pd.DataFrame(data_dict)

                # Save the DataFrame to a CSV file
                df.to_csv(output_csv, index=False)
                print(f"CSV file successfully saved to {output_csv}")

                # Load the saved CSV for further processing
                data = pd.read_csv(output_csv)
                # data = pd.read_csv(csv_file)
                columns = data.columns
                node_voltages = []
                component_currents = []
                peak_voltages = []
                peak_currents = []
                avg_voltages = []
                avg_currents = []

                for col in columns:
                    if col.startswith('V('):
                        node_voltages.append(col)
                    elif col.startswith('I('):
                        component_currents.append(col)

                print("Node Names:")
                print(node_voltages)

                print("Component Names:")
                print(component_currents)

                rms_voltages = {node: np.sqrt(np.mean(data[node] ** 2)) for node in node_voltages}
                print("RMS voltages:", rms_voltages)

                rms_currents = {component: np.sqrt(np.mean(data[component] ** 2)) for component in component_currents}
                print("RMS currents:", rms_currents)

                peak_voltages = {node: data[node][data[node].abs().idxmax()] for node in node_voltages}
                print("Peak voltages:", peak_voltages)

                peak_currents = {component: data[component][data[component].abs().idxmax()] for component in component_currents}
                print("Peak currents:", peak_currents)

                avg_voltages = {node: np.mean(data[node]) for node in node_voltages}
                print("Average voltages:", avg_voltages)

                avg_currents = {component: np.mean(data[component]) for component in component_currents}
                print("Average currents:", avg_currents) # rise time, fall time and propagation delay

                # Save the raw transient data to CSV
                # data.to_csv("res_divider_1.csv", index=False)

                # Prepare additional parameters to append
                summary_data = {
                    "Parameter": [],
                    "Node/Component": [],
                    "Value": []
                }

                # Append peak voltages
                for node, value in peak_voltages.items():
                    summary_data["Parameter"].append("Peak Voltage")
                    summary_data["Node/Component"].append(node)
                    summary_data["Value"].append(value)

                # Append peak currents
                for component, value in peak_currents.items():
                    summary_data["Parameter"].append("Peak Current")
                    summary_data["Node/Component"].append(component)
                    summary_data["Value"].append(value)

                # Append average voltages
                for node, value in avg_voltages.items():
                    summary_data["Parameter"].append("Average Voltage")
                    summary_data["Node/Component"].append(node)
                    summary_data["Value"].append(value)

                # Append RMS voltages
                for node, value in rms_voltages.items():
                    summary_data["Parameter"].append("RMS Voltage")
                    summary_data["Node/Component"].append(node)
                    summary_data["Value"].append(value)

                # Append average currents
                for component, value in avg_currents.items():
                    summary_data["Parameter"].append("Average Current")
                    summary_data["Node/Component"].append(component)
                    summary_data["Value"].append(value)

                # Append RMS currents
                for component, value in rms_currents.items():
                    summary_data["Parameter"].append("RMS Current")
                    summary_data["Node/Component"].append(component)
                    summary_data["Value"].append(value)

                summary_df = pd.DataFrame(summary_data)

                # Append summary to the existing CSV file
                with open(output_csv, 'a') as f:
                    f.write("\n\nSummary Data:\n")
                summary_df.to_csv(output_csv, index=False, mode='a')

            except Exception as e:
                print(f"Error processing {asc_file}: {e}")
        else:
            print(f"File not found: {asc_file}")