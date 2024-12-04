from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

def init_db(db_url="sqlite:///db/emc_test_automation_dashboard.db"):
    engine = create_engine(db_url, echo=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
