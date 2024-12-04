"""
Module: log_utils
Description: This module contains functions for creating and 
formatting log instances.

Author: Richard Saldanha
Date: December 9, 2023
"""

import logging as lg
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
import time
from typing import Any
from genericpath import exists
from emc_test_automation_api.src.utils.file_utils import FileOps # pylint: disable=E0401 # for effective import

class LoggingUtils: # pylint: disable=R0903 # remove if more than 1 method is added
    """
    Contains methods for Log operations
    """
    def time_rotated_log(self, props: Any, log_dir_path: str) -> lg.Logger:
        """
        Takes properties and log directory path and returns an object for time rotated logging
        with specified format.

        Args:
            props (Any): Object with properties from yaml config
            log_dir_path (str): path of the application logs directory

        Returns:
            lg.Logger: Formatted instance of Logging Object
        """
        try:
            file_ops = FileOps()
            if not exists(log_dir_path):
                file_ops.create_dir(log_dir_path)
            log_data_file = log_dir_path+"_".join([
                datetime.utcnow().strftime(props.applog_prefix),
                props.applog_suffix])
            lg.getLogger()
            lg.Formatter.converter = time.gmtime
            time_handler=TimedRotatingFileHandler(
                log_data_file,utc=True,
                when='midnight',encoding='utf-8')
            stream_handler=lg.StreamHandler()

            lg.basicConfig(format=props.applog_message_format,
                        level=lg.INFO,
                        handlers=[time_handler, stream_handler])
            return lg
        except ValueError as lu_ve:
            raise lu_ve
        except TypeError as lu_te:
            raise lu_te
        except Exception as lu_e:
            raise lu_e
