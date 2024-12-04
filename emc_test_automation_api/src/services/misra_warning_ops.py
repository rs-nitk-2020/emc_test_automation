"""
Module: misra_warning_ops
Description: This module contains functions for generating misra warnings report.

Author: Arif Kalluru
Date: December 14, 2023
"""
import os
import re
import pandas as pd
from emc_test_automation_api.src.utils.report_utils import ReportOps


class MisraWarningReport:
    """
    A class for processing MISRA log files, generating DataFrames, and creating Excel reports.

    Attributes:
        df_data_dict (dict): A dictionary to store the generated DataFrames.
        driver_names (set): A set to store unique driver names.
        driver_wise_file_names (dict): A dictionary to store driver-wise file names.
        file_wise_counts (dict): A dictionary to store file-wise MISRA level counts.
        driver_wise_counts (dict): A dictionary to store driver-wise MISRA level counts.
        props (object): An object containing properties for configuring the report.
        log_sheet_header (list): A list of headers for the log sheet.

    Methods:
        parse_line(line, driver_name): Parse a line of the log file and extract relevant information.
        get_driver_name(filename): Extract and return the driver name from the filename.
        prepare_file_wise_counts_df(): Prepare a DataFrame for file-wise calculation and store it in df_data_dict.
        file_wise_counting(driver_name, driver_file_name, misra_level): Update file-wise counts based on provided parameters.
        prepare_driver_wise_counts_df(): Prepare a DataFrame for driver-wise calculation and store it in df_data_dict.
        driver_wise_counting(): Perform driver-wise counting and update driver_wise_counts.
        log_parsing(log_directory): Parse log files and collect data for HAL, MCAL, and individual drivers.
        create_df(sheet_name, header, data): Create a DataFrame from provided data and store it in df_data_dict.
        reorder_dict(): Reorder a dictionary by placing specific keys at the beginning.
        process_misra_report(log_directory_path, report_path): Process MISRA log files, generate DataFrames, and create an Excel report.
    """

    def __init__(self, props):
        """
        Initialize the MisraWarningReport instance.

        Args:
            props (object): An object containing properties for configuring the report.
        """
        self.df_data_dict = {}
        self.driver_names = set()
        self.driver_wise_file_names = {}
        self.file_wise_counts = {}
        self.driver_wise_counts = {}
        self.props = props
        self.log_sheet_header = props.misra_warning_report_props.log_sheet_header

    def parse_line(self, line, driver_name):
        """
        Parse a line of the log file and extract relevant information.

        Args:
            line (str): A line from the log file.
            driver_name (str): The name of the driver.

        Returns:
            list or None: Parsed data as a list if valid, None otherwise.
        """
        parts = line.split()
        if len(parts) < 4:
            return None

        file_path = parts[0]
        pattern_hal = re.compile(f"hal/{re.escape(driver_name)}")
        pattern_mcal = re.compile(f"hal/mcal/{re.escape(driver_name)}")


        if pattern_hal.search(file_path):
            sheet_name = "HAL_Log"
        elif pattern_mcal.search(file_path):
            sheet_name = "MCAL_Log"
        else:
            return None  # Neither pattern is found in file path

        line_number = parts[1]
        error_no = parts[3].rstrip(":")

        driver_file_name = file_path.split("/")[-1].strip()

        error_message = " ".join(parts[4:])
        error_message_part = error_message.split('[MM', maxsplit=1)[0].strip()

        if " " in error_message_part:
            error_message_part = f'"{error_message_part}"'

        misra_level_match = re.search(r"\bMM-PWT (\d+)", error_message)
        misra_level = misra_level_match.group(0) if misra_level_match else "N/A"

        misra_rule_match = re.search(r"MISRA\s(.*?)(\d+\.\d+)", error_message)
        misra_rule_no = (
            f"MISRA {misra_rule_match.group(1)} {misra_rule_match.group(2)}"
            if misra_rule_match
            else "N/A"
        )

        return [
            line_number,
            file_path,
            error_no,
            error_message_part,
            misra_level,
            misra_rule_no,
            driver_file_name,
            sheet_name,
        ]

    def get_driver_name(self, filename):
        """
        Extract and return the driver name from the filename.

        Args:
            filename (str): The name of the log file.

        Returns:
            str: The extracted driver name.
        """
        driver_name = filename.split("-")[0].lower()
        self.driver_names.add(driver_name)
        self.driver_wise_file_names.setdefault(driver_name, [])
        return driver_name

    def prepare_file_wise_counts_df(self):
        """
        Prepare a DataFrame for file-wise calculation and store it in df_data_dict.

        Returns:
            None
        """
        file_data = {
            "File Name": [],
            "Driver": [],
            "Count MM-PWT 0": [],
            "Count MM-PWT 1": [],
            "Count MM-PWT 2": [],
            "Count MM-PWT 3": [],
            "Count MM-PWT 4": [],
            "Count MM-PWT 5": [],
            "Count MM-PWT 6": [],
            "Count MM-PWT 7": [],
            "File Wise Sum": [],
        }

        for driver_name in sorted(self.driver_names):
            for file_name in sorted(self.driver_wise_file_names[driver_name]):
                file_counts = self.file_wise_counts.get(file_name, {})
                counts = [file_counts.get(f"MM-PWT {i}", 0) for i in range(8)]
                sum_counts = sum(counts)
                row_data = [file_name, driver_name] + counts + [sum_counts]
                for col, value in zip(file_data.keys(), row_data):
                    file_data[col].append(value)

        file_wise_counts_df = pd.DataFrame(file_data)
        self.df_data_dict["File_wise_calculation"] = [file_wise_counts_df]

    def file_wise_counting(self, driver_name, driver_file_name, misra_level):
        """
        Update file-wise counts based on the provided parameters.

        Args:
            driver_name (str): The name of the driver.
            driver_file_name (str): The name of the driver file.
            misra_level (str): The MISRA level.

        Returns:
            None
        """
        if (
            driver_name in self.driver_names
            and driver_file_name
            not in self.driver_wise_file_names.setdefault(driver_name, [])
        ):
            self.driver_wise_file_names[driver_name].append(driver_file_name)

        if driver_file_name not in self.file_wise_counts:
            self.file_wise_counts[driver_file_name] = {}

        self.file_wise_counts[driver_file_name][misra_level] = (
            self.file_wise_counts[driver_file_name].get(misra_level, 0) + 1
        )

    def prepare_driver_wise_counts_df(self):
        """
        Prepare a DataFrame for driver-wise calculation and store it in df_data_dict.

        Returns:
            None
        """
        driver_data = {
            "Driver Name": [],
            "Driver Wise Sum": [],
            "Count MM-PWT 0": [],
            "Count MM-PWT 1": [],
            "Count MM-PWT 2": [],
            "Count MM-PWT 3": [],
            "Count MM-PWT 4": [],
            "Count MM-PWT 5": [],
            "Count MM-PWT 6": [],
            "Count MM-PWT 7": [],
        }

        for driver_name in sorted(self.driver_names):
            driver_counts = self.driver_wise_counts.get(driver_name, {})
            counts = [driver_counts.get(f"MM-PWT {i}", 0) for i in range(8)]
            sum_counts = sum(counts)
            row_data = [driver_name, sum_counts] + counts
            for col, value in zip(driver_data.keys(), row_data):
                driver_data[col].append(value)

        driver_wise_counts_df = pd.DataFrame(driver_data)
        self.df_data_dict["Final_output"] = [driver_wise_counts_df]

    def driver_wise_counting(self):
        """
        Perform driver-wise counting and update driver_wise_counts.
        """
        for driver_name in self.driver_names:
            driver_counts = {}
            for file_name in self.driver_wise_file_names.get(driver_name, []):
                file_counts = self.file_wise_counts.get(file_name, {})
                for i in range(8):
                    misra_key = f"MM-PWT {i}"
                    driver_counts[misra_key] = driver_counts.get(
                        misra_key, 0
                    ) + file_counts.get(misra_key, 0)
            self.driver_wise_counts[driver_name] = driver_counts

    def log_parsing(self, log_directory):
        """
        Parse log files in the specified directory and collect data for HAL, MCAL, and individual drivers.
        Create DataFrames from the collected data and store them in df_data_dict.

        Args:
            log_directory (str): The path to the directory containing log files.

        Returns:
            None
        """
        hal_data, mcal_data = [], []

        for root, _, files in os.walk(log_directory):
            for file in files:
                if not file.endswith("_LIN_LOG.txt"):
                    continue
                driver_name = self.get_driver_name(file)
                file_path = os.path.join(root, file)

                driver_data = []

                with open(file_path, "r", encoding="utf-8") as log_file:
                    for line in log_file:
                        data = self.parse_line(line, driver_name)
                        if data is None:
                            continue

                        # [line_number, file_path, error_no, error_message_part, misra_level, misra_rule_no, driver_file_name, sheet_name]
                        _, _, _, _, misra_level, _, driver_file_name, sheet_name = data
                        self.file_wise_counting(
                            driver_name, driver_file_name, misra_level
                        )

                        data = data[:-2]
                        # write to driver_name sheet
                        driver_data.append(data)

                        if sheet_name == "HAL_Log":
                            # write to HAL_Log sheet
                            hal_data.append(data)
                        elif sheet_name == "MCAL_Log":
                            # write to MCAL_Log sheet
                            mcal_data.append(data)

                # Create DataFrames from the collected driver data
                self.create_df(driver_name, self.log_sheet_header, driver_data)

        # Create DataFrames from the collected HAL & MCAL data
        self.create_df("HAL_Log", self.log_sheet_header, hal_data)
        self.create_df("MCAL_Log", self.log_sheet_header, mcal_data)

    def create_df(self, sheet_name, header, data):
        """
        Create a DataFrame from the provided data and store it in df_data_dict.

        Args:
            sheet_name (str): The name of the sheet.
            header (list): The column headers.
            data (list): The data to be stored in the DataFrame.

        Returns:
            None
        """
        df = pd.DataFrame(data, columns=header)
        self.df_data_dict[sheet_name] = [df]

    def reorder_dict(self):
        """
        Reorder a dictionary by placing specific keys at the beginning.

        Returns:
            dict: The reordered dictionary with specified keys at the beginning.
        """
        # Define the desired order
        desired_order = ["HAL_Log", "MCAL_Log"]

        # Create a new dictionary with keys from desired_order followed by the remaining keys
        ordered_df_data_dict = {
            key: self.df_data_dict[key]
            for key in desired_order
            if key in self.df_data_dict
        }
        ordered_df_data_dict.update(
            {
                key: self.df_data_dict[key]
                for key in self.df_data_dict
                if key not in desired_order
            }
        )

        return ordered_df_data_dict

    def process_misra_report(self, log_directory_path, report_path):
        """
        Process MISRA log files, generate DataFrames, and create an Excel report.

        Args:
            log_directory_path (str): The path to the directory containing log files.
            report_path (str): The path to save the generated Excel report.

        Returns:
            dict: Data for the generated Excel report.
        """
        self.log_parsing(log_directory_path)
        self.prepare_file_wise_counts_df()
        self.driver_wise_counting()
        self.prepare_driver_wise_counts_df()
        ordered_df_data_dict = self.reorder_dict()

        reports = ReportOps()
        report_data = reports.generate_excel_report_data(
            report_path=report_path, df_data_dict=ordered_df_data_dict, props=self.props
        )

        return report_data
