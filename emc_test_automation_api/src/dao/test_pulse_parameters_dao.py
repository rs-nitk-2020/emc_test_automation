from dao.base_dao import BaseDAO
from models.test_pulse_parameters import TestPulseParameters

class TestPulseParametersDAO(BaseDAO):
    def __init__(self, session):
        super().__init__(session, TestPulseParameters)
