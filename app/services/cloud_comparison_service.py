# cloud
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db.models.models import CloudComparison  # Assuming your model is in this file
from typing import List, Optional
from fastapi import HTTPException
from config.config import Config

# Setup database engine and session
DATABASE_URL = Config.POSTGRES_CONNECTION  # Adjust your database URI
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class CloudComparisonService:
    def get_filtered_cloud_comparisons(self, region: Optional[str], vcpus: Optional[int], ram_gib: Optional[float]) -> List[CloudComparison]:
        session = SessionLocal()
        try:
            query = session.query(CloudComparison)
            
            if region:
                query = query.filter(CloudComparison.region == region)
            if vcpus:
                query = query.filter(CloudComparison.vcpus == vcpus)
            if ram_gib:
                query = query.filter(CloudComparison.ram_gib == ram_gib)

            filtered_results = query.all()
            
            if not filtered_results:
                raise HTTPException(status_code=404, detail="No matching cloud instances found.")
            
            return filtered_results

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in filtering cloud comparisons: {e}")
        finally:
            session.close()
