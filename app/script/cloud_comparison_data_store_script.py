import pandas as pd
# from config.config import Config
from sqlalchemy import create_engine, Column, Integer, String, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.exc import SQLAlchemyError

# Define the SQLAlchemy Base
Base = declarative_base()

# Define the CloudComparison model
class CloudComparison(Base):
    __tablename__ = "cloud_comparison"

    id = Column(Integer, primary_key=True, autoincrement=True)
    region = Column(String, nullable=False)
    location = Column(String, nullable=False)
    instance_type = Column(String, nullable=False)
    instance_family = Column(String, nullable=False)
    vcpus = Column(Integer, nullable=False)
    ram_gib = Column(Float, nullable=False)
    memory_mib = Column(Integer, nullable=False)
    cost_per_hour = Column(Float, nullable=True)
    cloud = Column(
        SqlEnum('AWS', 'Azure', 'GCP', name='cloud_enum'),
        nullable=False
    )

POSTGRES_CONNECTION = "postgresql+psycopg://postgres:postgres@localhost:5432/app"
engine = create_engine(POSTGRES_CONNECTION)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Load the data from the CSV
    df = pd.read_csv('script/cloud_comparison.csv')
    
    # Process the data and insert into the database
    for index, row in df.iterrows():
        # Log each row to verify
        print(f"Inserting row {index + 1}...")
        
        cloud_comparison = CloudComparison(
            region=row['Region'],
            location=row['Location'],
            instance_type=row['Instance Type'],
            instance_family=row['Instance Family'],
            vcpus=int(row['CPU']),
            ram_gib=float(row['RAM (GiB)']),
            memory_mib=int(row['Memory MiB']),
            cost_per_hour=float(row['Cost Per Hour']),
            cloud=row['Cloud']
        )
        session.add(cloud_comparison)
    
    # Commit the session to save all changes to the database
    session.commit()
    print("Data successfully inserted into the database.")

except SQLAlchemyError as e:
    print(f"Error: {e}")
    session.rollback()

finally:
    session.close()
