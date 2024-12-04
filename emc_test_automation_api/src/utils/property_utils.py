"""
Module: property_utils
Description: This module contains functions to load
configuration properties from a yaml file.

Author: Richard Saldanha
Date: December 9, 2023
"""

import os
from typing import Any
from pathlib import Path
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class DictToObject: # pylint: disable=R0903 # remove if more than 1 method is added
    """
    Contains methods to dictionary-object operations
    """

    def __init__(self, dictionary):
        """
        Accepts a dictionary and converts it into a python Object with relevant attributes

        Args:
            dictionary (_type_): a dictionary that needs to be converted into a Python Object
            with attributes.
        """
        for key, value in dictionary.items():
            if isinstance(value, dict):
                # Recursively convert nested dictionaries to objects
                setattr(self, key, DictToObject(value))
            else:
                setattr(self, key, value)

    def to_dict(self) -> dict:
        """
        Converts the object passed to a dictionary and returns the same.

        Returns:
            _type_: an instance of the dictionary object
        """
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, DictToObject):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result


class PropertyLoader: # pylint: disable=R0903 # remove if more than 1 method is added
    """
    Contains methods to load properties file located in config folder
    """

    def load_properties_from_yaml(self, file_path: str) -> Any:
        """
        Takes the path to the properties file and returns none 
        if no properties exist or a properties object if file exists
        these properties can be used for several configurable functions 
        like filenames, headers, etc and are obtained from the yaml 
        properties file path passed.

        Args:
            file_path (str): path to the yaml config file

        Returns:
            Any: formatted Properties dictionary object or None
        """
        try:
            if not file_path:
                raise ValueError(f'Invalid file : {file_path}')
            file_path = os.path.join(BASE_DIR, file_path)
            with open(file_path, "r", encoding='utf-8') as file:
                properties = yaml.safe_load(file)
                return properties
        except yaml.YAMLError as ye:
            print(f"Error loading YAML file: {ye}")
            raise ye
        except ValueError as pu_ve:
            raise pu_ve
        except FileNotFoundError as pu_fe:
            raise pu_fe
