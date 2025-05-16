# -*- coding: utf-8 -*-

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, or_
from db.models.models import CloudComparison
from typing import List, Optional
from fastapi import HTTPException
from config.config import Config
from utils.location_mapping import expand_common_locations

# Setup database engine and session
DATABASE_URL = Config.POSTGRES_CONNECTION
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
class CloudComparisonService:
    def get_filtered_cloud_comparisons(
        self,
        location: Optional[List[str]] = None,
        vcpus_min: Optional[int]       = None,
        vcpus_max: Optional[int]       = None,
        ram_gib_min: Optional[float]   = None,
        ram_gib_max: Optional[float]   = None,
    ) -> List[CloudComparison]:
        """
        Query by:
          - location: list of substrings (ILIKE '%loc%')
          - vcpus_min / vcpus_max
          - ram_gib_min / ram_gib_max
        """
        session = SessionLocal()
        try:
            query = session.query(CloudComparison)

            # 1) multiple-location filter via ILIKE
            if location:
                expanded = expand_common_locations(location, clouds=None)
                ilike_clauses = [
                    CloudComparison.location.ilike(f"%{loc}%")
                    for loc in expanded
                ]
                if ilike_clauses:
                    query = query.filter(or_(*ilike_clauses))

            # 2) vCPU range
            if vcpus_min is not None:
                query = query.filter(CloudComparison.vcpus >= vcpus_min)
            if vcpus_max is not None:
                query = query.filter(CloudComparison.vcpus <= vcpus_max)

            # 3) RAM range
            if ram_gib_min is not None:
                query = query.filter(CloudComparison.ram_gib >= ram_gib_min)
            if ram_gib_max is not None:
                query = query.filter(CloudComparison.ram_gib <= ram_gib_max)

            results = query.all()

            if not results:
                raise HTTPException(
                    status_code=404,
                    detail="No matching cloud instances found."
                )

            return results

        except HTTPException:
            # re-raise 404
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error filtering cloud comparisons: {e}"
            )
        finally:
            session.close()
