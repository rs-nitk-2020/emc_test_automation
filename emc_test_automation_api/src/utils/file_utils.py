"""
Module: file_utils
Description: This module contains functions for file and directory operations.

Author: Richard Saldanha
Date: December 9, 2023
"""

import os

class FileOps: # pylint: disable=R0903 # remove if more than 1 method is added
    """
    This class has methods for file and directory operations.
    """

    def create_dir(self, dir_path: str)->None:
        """
        Creates a directory at specified path if it doesnt exist

        Args:
            dir_path (str): path of the directory to be created.
        """
        try:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        except ValueError as fu_ve:
            raise fu_ve
        except TypeError as fu_te:
            raise fu_te
        except Exception as fu_e:
            raise fu_e

    def get_average_file_size(self, directory):
        total_size = 0
        file_count = 0

        # Traverse through the directory
        for root, dirs, files in os.walk(directory):
            for file in files:
                # Get the path of each file
                file_path = os.path.join(root, file)

                # Calculate the size of the file in bytes
                file_size = os.path.getsize(file_path)

                # Add the file size to the total and increment the file count
                total_size += file_size
                file_count += 1

        # Calculate the average file size in megabytes
        if file_count > 0:
            average_bytes = total_size / file_count
            average_mb = average_bytes / (1024 * 1024)  # Convert bytes to megabytes
            return round(average_mb, 2)
        else:
            return 0  # Return 0 if there are no files in the directory