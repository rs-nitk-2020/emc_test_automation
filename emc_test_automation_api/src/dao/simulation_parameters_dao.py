from dao.base_dao import BaseDAO
from models.simulation_parameters import SimulationParameters

class SimulationParametersDAO(BaseDAO):
    def __init__(self, session):
        super().__init__(session, SimulationParameters)
