"""
Module: app_dashboard
Description: This module contains functions that
receive requests from the front end, process and
sends reponses back.

Author: Richard Saldanha
Date: December 9, 2023
"""

from typing import Any, OrderedDict
import os
import time
from django.http import HttpResponse
from emc_test_automation_api.src.utils.property_utils import PropertyLoader, DictToObject
from emc_test_automation_api.src.utils.log_utils import LoggingUtils
from emc_test_automation_api.src.services.compiler_warning_ops import (
    CompilerWarningReport as cwr,
)
from emc_test_automation_api.src.services.misra_warning_ops import (
    MisraWarningReport as mwr,
)
from emc_test_automation_api.src.utils.date_time_utils import DateTimeOps
from emc_test_automation_api.src.utils.file_utils import FileOps
from emc_test_automation_api.src.services.image_ops import (
    ImageOps as iops,
)

class EMCTestAutomationApi:
    """
    Contains methods to load gui data, and process data
    """

    def __init__(self, properties_config_file: str = "src/config/properties.yaml"):
        """
        Initialses the back end evironment, logs and properties when invoked from the front end GUI

        Args:
            env (str, optional): _description_. Defaults to 'dev'.
            properties_config_file (str, optional): _description_. Defaults
            to 'src/config/properties.yaml'.
        """
        property_loader = PropertyLoader()
        logging_utils = LoggingUtils()
        yaml_file_path = properties_config_file
        properties = property_loader.load_properties_from_yaml(yaml_file_path)
        self.props = DictToObject(properties)
        self.log = logging_utils.time_rotated_log(
            props=self.props, log_dir_path="emc_test_automation_api/logs/"
        )

    def load_gui_basic_data(self) -> OrderedDict:
        """
        Invoked from the GUI to load options and validations for log analysis

        Returns:
            OrderedDict: Dictionary of GUI options to load and populate the form entry page options.
        """
        basic_data = OrderedDict()
        basic_data[
            "emc_test_automation_options"
        ] = (
            self.props.emc_test_automation_options.to_dict()  # pylint: disable=E1101 # dynamically populated
        )
        basic_data[
            "emc_test_automation_valid_file_patterns"
        ] = (
            self.props.emc_test_automation_valid_file_patterns.to_dict()  # pylint: disable=E1101 # dynamically populated
        )
        return basic_data
    
    def generate_schematic_images(self, files:Any):
        processed_images = []
        for file in files:
            processed_images.append(iops.generate_schematic_image(schematic_file=file))
        return processed_images

    def process_compiler_warnings(self, files: Any):
        """
        Accepts file objects from the front end GUI, processes them and sends the generated report
        and report name back to the GUI

        Args:
            files (Any): File objects passed from the front end

        Returns:
            OrderedDict, str: report data and report name
        """
        start_time = time.time()
        report_data = ""
        report_name = ""
        report_status = "Success"
        report_status_message = ""
        average_file_size = 0
        try:
            date_time_ops = DateTimeOps(log=self.log)
            file_ops = FileOps()
            request_id = date_time_ops.get_current_timestamp_utc(
                self.props.compiler_warning_report_props.report_prefix  # pylint: disable=E1101 # dynamically populated
            )
            files_list = files.getlist("files[]")
            self.log.info(
                f"{request_id} : Start of compiler warning analysis process "
                f"for {len(files_list)} files."
            )
            log_and_report_dir_path = os.path.join(
                "emc_test_automation_api/src/data/Warnings/Compiler Warnings",
                request_id,
            )
            if not os.path.exists(log_and_report_dir_path):
                file_ops.create_dir(log_and_report_dir_path)
            for file in files_list:
                file_name = file.name
                file_content = file.read()
                file_destination = os.path.join(log_and_report_dir_path, file_name)
                with open(file_destination, "wb") as destination:
                    destination.write(file_content)

            report_name = "_".join(
                [
                    request_id,
                    self.props.compiler_warning_report_props.report_suffix,  # pylint: disable=E1101 # dynamically populated
                ]
            )
            report_path = os.path.join(log_and_report_dir_path, report_name)
            average_file_size = file_ops.get_average_file_size(log_and_report_dir_path)
            report_data = cwr().process_compiler_report(
                log_directory=log_and_report_dir_path,
                report_path=report_path,
                props=self.props,
            )
            end_time = time.time()
            hours, minutes, seconds, milliseconds = date_time_ops.get_processing_time(
                start_time=start_time, end_time=end_time
            )
            report_status_message = (
                f"Request Id: {request_id} : "
                f"Files {len(files_list)} with avg size {average_file_size} MB "
                f"Processing Status \"{report_status}\" : Processing time: "
                f"{hours:02d} hours, {minutes:02d} minutes, "
                f"{seconds:02d}.{milliseconds:03d} seconds"
            )
            self.log.info(report_status_message)
            return report_name, report_data, report_status, report_status_message
        except (ValueError, TypeError) as ex:
            report_status = "Failure"
            self.log.error(f"{request_id} Exception: {ex}")

            # Calculate processing time
            end_time = time.time()
            hours, minutes, seconds, milliseconds = date_time_ops.get_processing_time(
                start_time=start_time, end_time=end_time
            )
            report_status_message = (
                f"Request Id: {request_id} : "
                f"Files {len(files_list)} with avg size {average_file_size} MB "
                f"Processing Status \"{report_status}\" : {ex} \nProcessing time: "
                f"{hours:02d} hours, {minutes:02d} minutes, "
                f"{seconds:02d}.{milliseconds:03d} seconds"
            )
            self.log.info(report_status_message)
            return report_name, report_data, report_status, report_status_message
        except (
            Exception # pylint: disable=W0718 # Need this to handle unexpected exceptions
        ) as ex:
            report_status = "Failure"
            self.log.error(f"{request_id} Exception: {ex}")

            # Calculate processing time
            end_time = time.time()
            hours, minutes, seconds, milliseconds = date_time_ops.get_processing_time(
                start_time=start_time, end_time=end_time
            )
            report_status_message = f"Request Id: {request_id} : "
            report_status_message = (
                f"Request Id: {request_id} : "
                f"Files {len(files_list)} with avg size {average_file_size} MB "
                f"Processing Status \"{report_status}\" : {ex} \nProcessing time: "
                f"{hours:02d} hours, {minutes:02d} minutes, "
                f"{seconds:02d}.{milliseconds:03d} seconds"
            )
            self.log.info(report_status_message)
            return report_name, report_data, report_status, report_status_message

    def process_misra_warnings(self, files: Any):
        """
        Accepts file objects from the front end GUI, processes them and sends the generated report
        and report name back to the GUI

        Args:
            files (Any): File objects passed from the front end

        Returns:
            OrderedDict, str: report data and report name
        """
        start_time = time.time()
        date_time_ops = DateTimeOps(log=self.log)
        file_ops = FileOps()
        report_data = ""
        report_name = ""
        report_status = "Success"
        report_status_message = ""
        average_file_size = 0
        try:
            request_id = date_time_ops.get_current_timestamp_utc(
                self.props.misra_warning_report_props.report_prefix  # pylint: disable=E1101 # dynamically populated
            )
            files_list = files.getlist("files[]")
            self.log.info(
                f"{request_id} : Start of MISRA warning analysis process "
                f"for {len(files_list)} files."
            )
            log_and_report_dir_path = os.path.join(
                "emc_test_automation_api/src/data/Warnings/Misra Warnings", request_id
            )
            report_name = "_".join(
                [
                    request_id,
                    self.props.misra_warning_report_props.report_suffix,  # pylint: disable=E1101 # dynamically populated
                ]
            )
            report_path = os.path.join(log_and_report_dir_path, report_name)
            file_ops.create_dir(log_and_report_dir_path)
            for file in files.getlist("files[]"):
                file_name = file.name
                file_content = file.read()
                file_destination = os.path.join(log_and_report_dir_path, file_name)
                with open(file_destination, "wb") as destination:
                    destination.write(file_content)
            report_data = mwr(props=self.props).process_misra_report(
                log_directory_path=log_and_report_dir_path,
                report_path=report_path,
            )
            end_time = time.time()
            hours, minutes, seconds, milliseconds = date_time_ops.get_processing_time(
                start_time=start_time, end_time=end_time
            )
            average_file_size = file_ops.get_average_file_size(log_and_report_dir_path)
            report_status_message = (
                f"Request Id: {request_id} : "
                f"Files {len(files_list)} with avg size {average_file_size} MB "
                f"Processing Status \"{report_status}\" : Processing time: "
                f"{hours:02d} hours, {minutes:02d} minutes, "
                f"{seconds:02d}.{milliseconds:03d} seconds"
            )
            self.log.info(report_status_message)
            return report_name, report_data, report_status, report_status_message
        except (ValueError, TypeError) as ex:
            report_status = "Failure"
            self.log.error(f"{request_id} Exception: {ex}")

            # Calculate processing time
            end_time = time.time()
            hours, minutes, seconds, milliseconds = date_time_ops.get_processing_time(
                start_time=start_time, end_time=end_time
            )
            report_status_message = (
                f"Request Id: {request_id} : "
                f"Files {len(files_list)} with avg size {average_file_size} MB "
                f"Processing Status \"{report_status}\" : {ex} \nProcessing time: "
                f"{hours:02d} hours, {minutes:02d} minutes, "
                f"{seconds:02d}.{milliseconds:03d} seconds"
            )
            self.log.info(report_status_message)
            return report_name, report_data, report_status, report_status_message
        except (
            Exception # pylint: disable=W0718 # Need this to handle unexpected exceptions
        ) as ex:
            report_status = "Failure"
            self.log.error(f"{request_id} Exception: {ex}")

            # Calculate processing time
            end_time = time.time()
            hours, minutes, seconds, milliseconds = date_time_ops.get_processing_time(
                start_time=start_time, end_time=end_time
            )
            report_status_message = (
                f"Request Id: {request_id} : "
                f"Files {len(files_list)} with avg size {average_file_size} MB "
                f"Processing Status \"{report_status}\" : {ex} \nProcessing time: "
                f"{hours:02d} hours, {minutes:02d} minutes, "
                f"{seconds:02d}.{milliseconds:03d} seconds"
            )
            self.log.info(report_status_message)
            return report_name, report_data, report_status, report_status_message

    def download_report(self, report_name: str):
        """
        Accepts file name and sends back a report file object on success

        Args:
            report_name (str): report name

        Returns:
            report_path (Any): report file object
        """
        base_dir = os.path.dirname(
            __file__
        )  # Get the base directory of the current file
        report_parts = report_name.split("_")
        # This logic is specific to report format YYYYMMDD_HHMMSS_Type_Warnings_Report.xlsx
        # If the pattern changes then logic needs to be changed , here type is Compiler or MISRA
        request_id = "_".join(report_parts[:2])
        if "compiler" in report_name.casefold():
            report_path = os.path.join(
                base_dir,
                "src/data/Warnings/Compiler Warnings",
                request_id,
                report_name,
            )
        elif "misra" in report_name.casefold():
            report_path = os.path.join(
                base_dir,
                "src/data/Warnings/Misra Warnings",
                request_id,
                report_name,
            )
        else:
            return HttpResponse("Invalid File")

        return report_path
