from dao.base_dao import BaseDAO
from models.test_standards import TestStandards

class TestStandardsDAO(BaseDAO):
    def __init__(self, session):
        super().__init__(session, TestStandards)
