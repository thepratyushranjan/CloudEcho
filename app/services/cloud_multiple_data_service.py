# -*- coding: utf-8 -*-

import math
import traceback
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

from config.config import Config
from utils.location_mapping import expand_common_locations
from db.models.models import CloudComparison
from orm.cloud_response import CloudResponse

engine = create_engine(Config().POSTGRES_CONNECTION, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class CloudMultipleDataService:
    def get_filtered_cloud_comparisons_multiple(
        self,
        location: Optional[List[str]]         = None,
        clouds:   Optional[List[str]]         = None,
        instance_families: Optional[List[str]] = None,
        regions: Optional[List[str]] = None,
        instance_type: Optional[List[str]] = None
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

            if regions:
                query = query.filter(CloudComparison.region.in_(regions))

            if instance_type:
                query = query.filter(CloudComparison.instance_type.in_(instance_type))

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
