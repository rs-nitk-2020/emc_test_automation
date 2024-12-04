import sys
import os
# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from models.test_standards import Base, TestStandards
from models.test_pulse_parameters import TestPulseParameters
from models.simulation_parameters import SimulationParameters

class DatabaseOps:
    def __init__(self, db_path="emc_test_automation_api/db/emc_test_automation_dashboard.db") -> None:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        # Create Engine
        self.engine = create_engine(f"sqlite:///{db_path}", echo=True)

        # Create Tables
        Base.metadata.create_all(self.engine)

        # Create a Session Factory
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        """Provides a new database session."""
        return self.Session()

    def show_table_details(self):
        """Inspect and print details of all tables."""
        inspector = inspect(self.engine)
        tables = inspector.get_table_names()
        print("\n--- Tables in the Database ---")
        for table_name in tables:
            print(f"Table: {table_name}")
            columns = inspector.get_columns(table_name)
            print(f"  Columns:")
            for column in columns:
                print(f"    - {column['name']} ({column['type']})")


    def create_and_modify_test_standard_details(self, test_standard_details):
        """Create or modify test standards and their pulse parameters."""
        session = self.get_session()

        for standard_name, standard_info in test_standard_details.items():
            # Check if the TestStandard already exists
            existing_standard = session.query(TestStandards).filter_by(NAME=standard_name).first()

            if not existing_standard:
                # Create new Test Standard if it doesn't exist
                new_standard = TestStandards(
                    NAME=standard_name,
                    DESCRIPTION=standard_info['description'],
                    TYPE='standard'  # Set type as standard
                )
                session.add(new_standard)
                session.commit()  # Commit after adding the new standard
                print(f"Created new Test Standard: {standard_name}")
                existing_standard = new_standard

            # For each test in the standard, create or update test pulse parameters
            for test_name, test_info in standard_info['tests'].items():
                for param in test_info['parameters']:
                    param_name = param['name']
                    # Check if the parameter exists for this standard
                    existing_param = session.query(TestPulseParameters).filter_by(
                        TEST_ID=existing_standard.TEST_ID,
                        PARAMETER=param_name
                    ).first()

                    if not existing_param:
                        # Add a new pulse parameter if it doesn't exist
                        new_param = TestPulseParameters(
                            TEST_ID=existing_standard.TEST_ID,
                            PARAMETER=param_name,
                            DESCRIPTION=param['description'],
                            VALUE=param['value'],
                            UNITS=param['units'],
                            IS_DEFAULT=False  # You can set this as needed
                        )
                        session.add(new_param)
                        print(f"Created new parameter: {param_name}")
                    else:
                        # If exists, update the value and other fields if needed
                        existing_param.VALUE = param['value']
                        existing_param.DESCRIPTION = param['description']
                        existing_param.UNITS = param['units']
                        print(f"Updated parameter: {param_name}")

            session.commit()  # Commit after processing all parameters for this test standard

        session.close()


    def get_test_standards_details(self):
        """Fetch and return all test standards and their details."""
        session = self.get_session()
        test_standard_details = dict()

        # Query all test standards
        standards = session.query(TestStandards).all()
        for standard in standards:
            standard_info = {
                "description": standard.DESCRIPTION,
                "tests": {}
            }

            # Get all tests and their parameters
            tests = session.query(TestPulseParameters).filter_by(TEST_ID=standard.TEST_ID).all()
            for test in tests:
                test_info = {
                    "description": test.DESCRIPTION,
                    "parameters": []
                }
                test_info['parameters'].append({
                    "name": test.PARAMETER,
                    "description": test.DESCRIPTION,
                    "value": test.VALUE,
                    "units": test.UNITS
                })
                standard_info['tests'][test.PARAMETER] = test_info

            test_standard_details[standard.NAME] = standard_info

        session.close()
        return test_standard_details
  

db_ops = DatabaseOps()
# db_ops.show_table_details()
print(db_ops.get_test_standards_details())
# Example input data
test_standard_data = {
    "Transient Immunity Standard": {
        "description": "description of Transient immunity (optional) - None",
        "tests": {
            "Pulse 1": {
                "description": "Pulse 1 default parameters",
                "parameters": [
                    {
                        "name": "Us",
                        "description": "optional",
                        "value": "13.5+/-2",
                        "units": "V"
                    },
                    {
                        "name": "Ri",
                        "description": "Internal Resistance",
                        "value": "10",
                        "units": "Ohms"
                    }
                ]
            }
        }
    },
    "Other Standard": {
        "description": "",
        "tests": {}
    }
}

# Create/Modify test standard details
# db_ops.create_and_modify_test_standard_details(test_standard_data)

# Fetch test standard details
# standard_details = db_ops.get_test_standards_details()
# print(standard_details)
