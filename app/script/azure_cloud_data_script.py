import pandas as pd
from config.config import Config
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError

# Define the base for model classes
Base = declarative_base()

# Define the AzureCloud model
class AzureCloud(Base):
    __tablename__ = "azure_cloud"

    id = Column(Integer, primary_key=True, autoincrement=True)
    region = Column(String, nullable=False)
    location = Column(String, nullable=False)
    instance_type = Column(String, nullable=False)
    instance_family = Column(String, nullable=False)
    vcpus = Column(Integer, nullable=False)
    ram_gib = Column(Float, nullable=False)
    memory_mib = Column(Integer, nullable=False)
    cost_per_hour = Column(Float, nullable=True)
    storage_info = Column(String, nullable=True)
    network = Column(String, nullable=True)
    accelerators = Column(String, nullable=True)


engine = create_engine(Config.POSTGRES_CONNECTION)

# Create the table if not exists
Base.metadata.create_all(engine)

# Start a session
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Load the data from the CSV
    df = pd.read_csv('script/Pre_Final_Azure_Test_Data.csv')

    # Process the data and insert into the database
    for index, row in df.iterrows():
        # Log each row to verify
        print(f"Inserting row {index + 1}...")

        cloud_comparison = AzureCloud(
            region=row['Region'],
            location=row['Location'],
            instance_type=row['Instance Type'],
            instance_family=row['Instance Family'],
            vcpus=int(row['CPU']),
            ram_gib=float(row['RAM (GiB)']),
            memory_mib=int(row['Memory MiB']),
            cost_per_hour=float(row['Cost Per Hour']),
            storage_info=row['Storage Info'],
            network=row['Network Performance'],
            accelerators=row['Accelerators'],
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
