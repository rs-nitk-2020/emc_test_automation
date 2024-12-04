from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, PrimaryKeyConstraint
import os
import sys
# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.base import Base

class TestPulseParameters(Base):
    __tablename__ = "TEST_PULSE_PARAMETERS"

    TEST_ID = Column(Integer, ForeignKey("TEST_STANDARDS.TEST_ID", ondelete="CASCADE"), nullable=False)
    PARAMETER = Column(String, nullable=False)
    DESCRIPTION = Column(Text, nullable=True)
    VALUE = Column(String, nullable=False)
    UNITS = Column(String, nullable=True)
    IS_DEFAULT = Column(Boolean, nullable=False, default=False)
    SIMULATION_ID = Column(Integer, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint("TEST_ID", "PARAMETER"),
    )
