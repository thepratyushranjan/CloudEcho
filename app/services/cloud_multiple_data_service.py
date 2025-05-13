import traceback
from typing import List, Optional
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, or_
from db.models.models import CloudComparison
from fastapi import HTTPException
from orm.cloud_response import CloudResponse
from config.config import Config

# Setup database engine and session
DATABASE_URL = Config.POSTGRES_CONNECTION
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class CloudMultipleDataService:
    def get_filtered_cloud_comparisons_multiple(
        self, 
        location: Optional[List[str]], 
        clouds: Optional[List[str]], 
        instance_families: Optional[List[str]],
    ) -> List[CloudResponse]:
        session = SessionLocal()
        try:
            query = session.query(CloudComparison)
            
            if location:
                # Use 'ilike' for case-insensitive partial matching on location
                location_filters = [
                    CloudComparison.location.ilike(f"%{loc}%") for loc in location
                ]
                query = query.filter(or_(*location_filters))
                
            if clouds:
                query = query.filter(CloudComparison.cloud.in_(clouds))
            if instance_families:
                query = query.filter(CloudComparison.instance_family.in_(instance_families))

            filtered_results = query.all()
            
            if not filtered_results:
                raise HTTPException(status_code=404, detail="No matching cloud instances found.")
        
            response_list = []
            for result in filtered_results:
                try:
                    result_dict = result.__dict__.copy()
                    if '_sa_instance_state' in result_dict:
                        del result_dict['_sa_instance_state']

                    if 'cost_per_hour' in result_dict and (
                        isinstance(result_dict['cost_per_hour'], float) and 
                        result_dict['cost_per_hour'] != result_dict['cost_per_hour']
                    ):
                        result_dict['cost_per_hour'] = None
                        
                    response_list.append(CloudResponse.model_validate(result_dict))
                except Exception as model_error:
                    print(f"Error converting model: {str(model_error)}, Data: {result.__dict__}")
                    continue
            
            return response_list

        except Exception as e:
            error_details = traceback.format_exc()
            print(f"Error in filtering cloud comparisons: {error_details}")
            raise HTTPException(status_code=500, detail=f"Error in filtering cloud comparisons: {str(e)}")
        finally:
            session.close()
