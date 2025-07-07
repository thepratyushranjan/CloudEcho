# -*- coding: utf-8 -*-

import json
import traceback
from fastapi import APIRouter, HTTPException, Depends
from httpx import AsyncClient

from app.utils.details_data_cleanup import (
    transform_data,
    structure_metrics,
    structured_data,
    extract_basic_info,
    get_cloud_comparison,
    get_cloud_comparison_filter,
    structured_data_with_cloud_migration,
)
from services.cloud_comparison_service import CloudComparisonService, CloudMultipleDataService, CloudComparisonFilterService
from services.cloudtuner_services import CloudTunerServiceRecommendations, CloudTunerServiceResource
from services.chat_agent_query_service import QueryService, SimpleQueryService
from services.document_service import DocumentService


from models.pydentic_model import (
    ChecklistAnalysisRequest,
    CloudComparisonQueryRequest,
    CloudComparisonQueryMultipleRequest,
    CloudMultipleDataResponse,
    CloudComparisonFilterRequest,
    DetailsAnalysisRequest,
    DocumentRequest,
    RecommendationRequest,
    ResourceRequest,
    SimpleQueryRequest,
    QueryRequest,
)
from utils.checklist_llm import ChecklistLlmGenerator
from utils.details_llm import DetailsLlmGenerator
from utils.http_client import get_async_client

router = APIRouter()

# Document API Endpoints
@router.post("/document")
async def scrape_and_store_document(request: DocumentRequest):
    """
    Scrapes the webpage from the given URL, generates embeddings for the text chunks,
    and stores them in the database under the specified collection.
    """
    document_service = DocumentService()
    
    try:
        # Pass both the URL and the collection_name to the service
        result = document_service.scrape_and_store(request.url, request.collection_name, request.source_identifier)
        return {
            "url": request.url,
            "collection_name": request.collection_name,
            "message": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Simple Query API Endpoints
@router.post("/simple-query")
async def query_docs(request: SimpleQueryRequest):
    print(f"RAG Chat-Bot Query Excuted with request: {request}")
    """
    Queries the documentation database using vector search.
    The endpoint receives a query (and optionally a collection_name),
    generates its embedding, performs a vector search, and returns the final answer.
    """
    simple_query_service = SimpleQueryService()
    
    try:
        final_response = simple_query_service.simple_query_document(
            query=request.query, 
            collection_name=request.collection_name, 
            )
        if not final_response:
            raise HTTPException(status_code=404, detail="No relevant documents found.")
        
        return {"response": final_response}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# Query API Endpoints
@router.post("/query")
async def query_docs(request: QueryRequest):
    """
    Queries the documentation database using vector search.
    The endpoint receives a query (and optionally a collection_name),
    generates its embedding, performs a vector search, and returns the final answer.
    """
    query_service = QueryService()
    
    try:
        final_response = query_service.query_document(
            query=request.query, 
            collection_name=request.collection_name, 
            filter_dict=request.filter_dict
            )
        
        if not final_response:
            raise HTTPException(status_code=404, detail="No relevant documents found.")
        
        return {"response": final_response}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# AI Checklist API Endpoints
@router.post("/checklist-analysis")
async def checklist_analysis(payload: ChecklistAnalysisRequest):
    try:
        content = payload.request
        query = payload.query

        # Clean up and transform the raw content
        transform_content = transform_data(content)
        data = {
            "content": transform_content,
            "question": query,
        }
        final_data = json.dumps(data, indent=2)

        # Invoke the checklist-specific LLM generator
        checklist_llm_generator = ChecklistLlmGenerator()
        response = checklist_llm_generator.llm_query(final_data)
        return {"response": response}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {str(e)}"
        )

# AI Recommndations API Endpoints
@router.post("/details-analysis")
async def details_analysis(payload: DetailsAnalysisRequest):
    try:
        sources = payload.request
        query = payload.query
        monitoring = payload.monitoring
        transform_monitoring = structure_metrics(monitoring)
        transform_sources = transform_data(sources)
        content = structured_data(transform_sources, transform_monitoring)
        basic_info = extract_basic_info(sources)
        comparison = get_cloud_comparison(basic_info)
        filtered = get_cloud_comparison_filter(comparison, basic_info)
        migration_content = structured_data_with_cloud_migration(transform_sources, transform_monitoring, filtered)
        details_llm_generator = DetailsLlmGenerator()
        if query == "Cross‑Cloud Migration":
            migration_data = {
                "content": migration_content,
                "question": query,
            }
            final_migration_data = json.dumps(migration_data, indent=2)
            response = details_llm_generator.migration_query(final_migration_data)
            return {"response": response}
            

        data = {
            "content": content,
            "question": query,
        }
        final_data = json.dumps(data, indent=2)
        response = details_llm_generator.llm_query(final_data)
        return {"response": response}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {str(e)}"
        )

# AI Cloud Comparison API Endpoints
@router.post("/cloud-comparison")
async def cloud_comparison(request: CloudComparisonQueryRequest):
    """
    This API endpoint queries cloud instances based on location, vCPUs, and RAM.
    It returns cloud instances that match the given criteria.
    """
    cloud_comparison_service = CloudComparisonService()
    
    try:
        filtered_results = cloud_comparison_service.get_filtered_cloud_comparisons(
            location   = request.location,
            vcpus_min   = request.vcpus_min,
            vcpus_max   = request.vcpus_max,
            memory_gb_min = request.memory_gb_min,
            memory_gb_max = request.memory_gb_max,
        )
        
        return {"cloud_comparisons": filtered_results}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")
    

@router.post("/cloud-comparison/cloud-provider", response_model=CloudMultipleDataResponse)
async def cloud_comparison_multiple(request: CloudComparisonQueryMultipleRequest):
    """
    This API endpoint queries cloud instances based on multiple location, clouds, instance families.
    It returns cloud instances that match the given criteria.
    """
    cloud_comparison_service = CloudMultipleDataService()
    
    try:
        filtered_results = cloud_comparison_service.get_filtered_cloud_comparisons_multiple(
            location=request.location, 
            clouds=request.clouds, 
            instance_families=request.instance_families,
            regions=request.regions,
            instance_type=request.instance_type,
            os=request.os
        )
        
        return CloudMultipleDataResponse(cloud_multiple_data=filtered_results)
    
    except HTTPException as e:
        raise e
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Unexpected error in cloud_comparison_multiple: {error_details}")
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")

@router.post("/cloud-comparison/cloud-provider/filter", response_model=CloudMultipleDataResponse)
async def cloud_comparison_filter(request: CloudComparisonFilterRequest):
    cloud_comparison_filter_service = CloudComparisonFilterService()
    
    try:
        filtered_results = cloud_comparison_filter_service.get_filtered_by_specs(
            vcpus=request.vcpus,
            memory_gb=request.memory_gb,
            cost_per_hour=request.cost_per_hour,
            instance_families=request.instance_families,
            country=request.country,
            os =request.os,

        )
        
        return CloudMultipleDataResponse(cloud_multiple_data=filtered_results)
    
    except HTTPException as e:
        raise e
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Unexpected error in cloud_comparison_filter: {error_details}")
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")

        # AI Recommndations API Endpoints
@router.post("/recommendations", response_model=dict)
async def get_recommendations(
    req: RecommendationRequest,
    client: AsyncClient = Depends(get_async_client),
):
    svc = CloudTunerServiceRecommendations(
        client=client,
        org_id=req.org_id,
        api_token=req.api_token,
    )
    return await svc.fetch_recommendations(
        limit=req.limit, overview=req.overview
    )

# AI Resource Data API Endpoints
@router.post("/recommndations/resource", response_model=dict)
async def get_resource(
    req: ResourceRequest,
    client: AsyncClient = Depends(get_async_client),
):
    svc = CloudTunerServiceResource(
        client=client,
        api_token=req.api_token
    )
    try:
        return await svc.fetch_resources(
            resource_id=req.resource_id,
            details=req.details
        )
    except HTTPException as exc:
        raise exc