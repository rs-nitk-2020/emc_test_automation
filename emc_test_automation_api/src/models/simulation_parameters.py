from sqlalchemy import Column, Integer, String, Text, PrimaryKeyConstraint
from models.base import Base

class SimulationParameters(Base):
    __tablename__ = "SIMULATION_PARAMETERS"

    SIMULATION_ID = Column(Integer, nullable=False)
    PARAMETER_TYPE = Column(String, nullable=False)
    PARAMETER = Column(String, nullable=False)
    VALUE = Column(String, nullable=False)
    UNITS = Column(String, nullable=True)
    DESCRIPTION = Column(Text, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint("SIMULATION_ID", "PARAMETER_TYPE", "PARAMETER"),
    )
