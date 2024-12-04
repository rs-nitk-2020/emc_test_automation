from sqlalchemy import Column, Integer, String, Text
from models.base import Base

class TestStandards(Base):
    __tablename__ = "TEST_STANDARDS"

    TEST_ID = Column(Integer, primary_key=True, autoincrement=True)
    TYPE = Column(String, nullable=False)
    NAME = Column(String, unique=True, nullable=False)
    DESCRIPTION = Column(Text, nullable=True)
