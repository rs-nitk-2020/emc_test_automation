import os
import re
from typing import OrderedDict
import unittest
from yaml import YAMLError
from emc_test_automation_api.src.services.compiler_warning_ops import CompilerWarningReport
from emc_test_automation_api.src.utils.property_utils import PropertyLoader, DictToObject
import pandas as pd


class TestCompilerWarningReport(unittest.TestCase):
    def setUp(self):
        self.compiler_warning_report = CompilerWarningReport()
        self.test_driver = "MCU"
        self.test_log_file = f"{self.test_driver}-TC3XX_00_00_MM_03_MADE_LOG.txt"
        self.test_driver_note_coverage = "MPG"
        self.test_log_file_note_coverage = (
            f"{self.test_driver_note_coverage}-TC3XX_00_00_XX_00_made.log"
        )

    def test_process_compiler_report_note_coverage(self):
        yaml_file_path = "tests/config/properties.yaml"
        test_data_folder = "20231210_131415"
        property_loader = PropertyLoader()
        properties = property_loader.load_properties_from_yaml(file_path=yaml_file_path)
        props = DictToObject(properties)
        # Sample data for testing
        parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        log_directory = f"data/Warnings/Compiler Warnings/{test_data_folder}"
        report_name = f"{test_data_folder}_Compiler_Warnings_Report.xlsx"
        reference_report_name = (
            f"{test_data_folder}_Compiler_Warnings_Report_Reference.xlsx"
        )

        log_directory = os.path.join(parent_dir, log_directory)
        report_path = os.path.join(log_directory, report_name)
        reference_report_path = os.path.join(log_directory, reference_report_name)
        result = self.compiler_warning_report.process_compiler_report(
            log_directory, report_path, props
        )

        reference_data = pd.read_excel(reference_report_path, sheet_name=None)
        # Convert DataFrames to list of dictionaries with header as keys and row values as values
        reference_dict_data = {}
        for sheet_name, df in reference_data.items():
            # handle any nan values read
            df = df.fillna("")
            header_value_pairs = OrderedDict()
            for col in df.columns:
                header_value_pairs[col] = df[col].tolist()
            reference_dict_data[sheet_name] = header_value_pairs

        # Call the method under test
        result = self.compiler_warning_report.process_compiler_report(
            log_directory, report_path, props
        )

        # Assertions based on expected behavior
        self.assertIsInstance(result, dict)
        self.assertDictEqual(
            {k: None for k in result},
            {k: None for k in reference_dict_data},
            "Dictionaries have different keys.",
        )

        test_driver_filter_pattern = re.compile(
            self.compiler_warning_report.driver_filter_pattern_prefix
            + self.test_driver_note_coverage
            + self.compiler_warning_report.driver_filter_pattern_suffix
        )

        cfgstat_result_dict = self.compiler_warning_report.process_log_file(
            is_driver=False,
            cfgstat_filter_pattern=self.compiler_warning_report.cfgstat_filter_pattern,
            driver=self.test_driver_note_coverage,
            driver_filter_pattern=test_driver_filter_pattern,
            log_file=self.test_log_file_note_coverage,
        )
        cfg_df = cfgstat_result_dict.get("HAL_CFGSTAT")[0]
        self.assertFalse(cfg_df.empty, "DataFrame is empty")

    def test_process_compiler_report(self):
        yaml_file_path = "tests/config/properties.yaml"
        test_data_folder = "20231210_094651"
        property_loader = PropertyLoader()
        properties = property_loader.load_properties_from_yaml(file_path=yaml_file_path)
        props = DictToObject(properties)
        # Sample data for testing
        parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        log_directory = f"data/Warnings/Compiler Warnings/{test_data_folder}"
        report_name = f"{test_data_folder}_Compiler_Warnings_Report.xlsx"
        reference_report_name = (
            f"{test_data_folder}_Compiler_Warnings_Report_Reference.xlsx"
        )

        log_directory = os.path.join(parent_dir, log_directory)
        report_path = os.path.join(log_directory, report_name)
        reference_report_path = os.path.join(log_directory, reference_report_name)
        result = self.compiler_warning_report.process_compiler_report(
            log_directory, report_path, props
        )

        reference_data = pd.read_excel(reference_report_path, sheet_name=None)
        # Convert DataFrames to list of dictionaries with header as keys and row values as values
        reference_dict_data = {}
        for sheet_name, df in reference_data.items():
            # handle any nan values read
            df = df.fillna("")
            header_value_pairs = OrderedDict()
            for col in df.columns:
                header_value_pairs[col] = df[col].tolist()
            reference_dict_data[sheet_name] = header_value_pairs

        # Call the method under test
        result = self.compiler_warning_report.process_compiler_report(
            log_directory, report_path, props
        )

        # Assertions based on expected behavior
        self.assertIsInstance(result, dict)
        self.assertDictEqual(
            {k: None for k in result},
            {k: None for k in reference_dict_data},
            "Dictionaries have different keys.",
        )

        # assert process log file data
        test_driver_filter_pattern = re.compile(
            self.compiler_warning_report.driver_filter_pattern_prefix
            + self.test_driver
            + self.compiler_warning_report.driver_filter_pattern_suffix
        )

        driver_result_dict = self.compiler_warning_report.process_log_file(
            is_driver=True,
            cfgstat_filter_pattern=self.compiler_warning_report.cfgstat_filter_pattern,
            driver=self.test_driver,
            driver_filter_pattern=test_driver_filter_pattern,
            log_file=self.test_log_file,
        )

        cfgstat_result_dict = self.compiler_warning_report.process_log_file(
            is_driver=False,
            cfgstat_filter_pattern=self.compiler_warning_report.cfgstat_filter_pattern,
            driver=self.test_driver,
            driver_filter_pattern=test_driver_filter_pattern,
            log_file=self.test_log_file,
        )
        empty_df = driver_result_dict.get("MCU")[0]
        self.assertTrue(empty_df.empty, "DataFrame is not empty")

        cfg_df = cfgstat_result_dict.get("HAL_CFGSTAT")[0]
        self.assertFalse(cfg_df.empty, "DataFrame is empty")

    def test_process_compiler_report_yaml(self):
        with self.assertRaises(YAMLError):
            yaml_file_path = "tests/config/incorrect_properties.yaml"
            property_loader = PropertyLoader()
            _ = property_loader.load_properties_from_yaml(file_path=yaml_file_path)
        with self.assertRaises(ValueError):
            yaml_file_path = None
            property_loader = PropertyLoader()
            _ = property_loader.load_properties_from_yaml(file_path=yaml_file_path)
        with self.assertRaises(FileNotFoundError):
            yaml_file_path = "tests/config/nonexistant_properties.yaml"
            property_loader = PropertyLoader()
            _ = property_loader.load_properties_from_yaml(file_path=yaml_file_path)

    def test_process_compiler_report_properties_check(self):
        yaml_file_path = "tests/config/snapshot_properties.yaml"
        ref_dict = {
            "applog_suffix": "log_dashboard.log",
            "applog_prefix": "%Y_%m_%d",
            "applog_message_format": "[%(asctime)s GMT] %(levelname)s::%(funcName)s() %(message)s",
            "log_analysis_options": {
                "MISRA_Warnings": "MISRA Warnings",
                "Compiler_Warnings": "Compiler Warnings",
            },
        }
        property_loader = PropertyLoader()
        properties = property_loader.load_properties_from_yaml(file_path=yaml_file_path)
        props_dict = DictToObject(properties).to_dict()
        self.assertDictEqual(ref_dict, props_dict)


if __name__ == "__main__":
    unittest.main()  # pragma: no cover - excluded since this line launches tests
