# -*- coding: utf-8 -*-

import math
import traceback
from config.config import Config
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from utils.location_mapping import expand_common_locations
from db.models.models import CloudComparison
from orm.cloud_response import CloudResponse

# Setup database engine and session

engine = create_engine(Config().POSTGRES_CONNECTION, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# CloudComparisonService provides methods to filter cloud comparisons based on various criteria.
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


# CloudMultipleDataService provides methods to filter cloud comparisons based on multiple criteria.
class CloudMultipleDataService:
    def get_filtered_cloud_comparisons_multiple(
        self,
        location: Optional[List[str]]         = None,
        clouds:   Optional[List[str]]         = None,
        instance_families: Optional[List[str]] = None
    ) -> List[dict]:
        session = SessionLocal()
        try:
            query = session.query(CloudComparison)

            if clouds:
                query = query.filter(CloudComparison.cloud.in_(clouds))

            if location:
                expanded = expand_common_locations(location, clouds)
                loc_conds = [
                    CloudComparison.location.ilike(f"%{loc}%")
                    for loc in expanded
                ]
                if loc_conds:
                    query = query.filter(or_(*loc_conds))

            if instance_families:
                query = query.filter(
                    CloudComparison.instance_family.in_(instance_families)
                )

            rows = query.all()
            response_dicts: List[dict] = []

            for row in rows:
                # 1) turn ORM object into a clean dict
                d = row.__dict__.copy()
                d.pop("_sa_instance_state", None)

                # 2) guard against NaN cost_per_hour
                cp = d.get("cost_per_hour")
                if isinstance(cp, float) and math.isnan(cp):
                    d["cost_per_hour"] = None

                # 3) validate & coerce via Pydantic
                cr = CloudResponse.model_validate(d)

                # 4) dump back to plain dict
                response_dicts.append(cr.model_dump())

            return response_dicts

        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            session.close()
