"""
Module: date_time_utils
Description: This module contains functions for date time formatting.

Author: Richard Saldanha
Date: December 9, 2023
"""

import datetime
from logging import Logger


class DateTimeOps:
    """
    This class has methods for Date Time Operations.
    """

    def __init__(self, log: Logger) -> None:
        self.log = log

    def get_current_timestamp_utc(self, date_time_format: str) -> str:
        """
        Converts the date time by taking the required date time format and
        returns the UTC timestamp as a string in requested format.

        Args:
            date_time_format (str): a date time format as a string

        Returns:
            str: the UTC date time in specifiec format
        """
        try:
            current_datetime = datetime.datetime.utcnow()
            timestamp = current_datetime.strftime(date_time_format)
            if not timestamp:
                err_msg = f"Invalid timestamp format : '{date_time_format}'. No timestamp generated"
                raise ValueError(err_msg)
            return timestamp
        except ValueError as dtu_ve:
            self.log.error(dtu_ve)
            raise dtu_ve
        except TypeError as dtu_te:
            self.log.error(dtu_te)
            raise dtu_te
        except Exception as dtu_e:
            self.log.error(dtu_e)
            raise dtu_e

    def get_processing_time(self, start_time: float, end_time: float) -> (int, int, int, int):
        """
        Takes start and end time for a process and returns time elaspsed
        in hours, minutes and seconds

        Args:
            start_time (float): start time of a process
            end_time (float): end time of a process

        Returns:
            (int, int, int, int): time elapsed in hours, minutes, seconds and milliseconds
        """
        # Calculate the time difference
        # Ensures non-negative execution time
        execution_time_seconds = max(0, end_time - start_time)
        # Calculate hours, minutes, and seconds
        hours, remainder = divmod(execution_time_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = int((execution_time_seconds - int(execution_time_seconds)) * 1000)
        # Adjust milliseconds calculation
        milliseconds += int(seconds - int(seconds)) * 1000
        hours = int(hours)
        minutes = int(minutes)
        seconds = int(seconds)
        return (hours, minutes, seconds, milliseconds)
