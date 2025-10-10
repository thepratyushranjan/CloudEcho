from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .node_bridge import (
    NodeBridgeError,
    run_chat_helper,
    run_mcp_status_helper,
    stream_chat_helper,
)
from .schemas import ChatRequest, ChatResponse, MCPStatusResponse
from .pydentic_model import (
    ChecklistAnalysisRequest, 
    CloudComparisonQueryRequest, 
    CloudMultipleDataResponse, 
    CloudComparisonQueryMultipleRequest, 
    CloudComparisonFilterRequest,
    DetailsAnalysisRequest,
    SimpleQueryRequest
    )
from .details_data_cleanup import (
    transform_data, 
    structure_metrics, 
    structured_data, 
    extract_basic_info, 
    get_cloud_comparison, 
    get_cloud_comparison_filter, 
    structured_data_with_cloud_migration
)
from .utils.checklist_llm import ChecklistLlmGenerator
from .utils.details_llm import DetailsLlmGenerator
from .services.cloud_comparison_service import CloudComparisonService, CloudMultipleDataService, CloudComparisonFilterService
from .services.chat_agent_query_service import SimpleQueryService
import traceback
import json


def create_app() -> FastAPI:
    app = FastAPI(title="Agentic Chatbot Backend", version="0.1.0")

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify your frontend domain
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.post("/chatbot/chat", response_model=ChatResponse)
    async def chat_endpoint(
        request: ChatRequest, stream: bool | None = Query(default=None)
    ) -> ChatResponse | StreamingResponse:
        query_stream = bool(request.stream)
        if stream is not None:
            query_stream = query_stream or stream

        payload = {
            "query": request.query,
            "messages": [message.model_dump() for message in request.messages],
            "stream": query_stream,
            "context": request.context.model_dump() if request.context else None,
        }

        if query_stream:
            try:
                stream_gen = await stream_chat_helper(payload)
            except NodeBridgeError as exc:
                raise HTTPException(status_code=502, detail=str(exc)) from exc

            return StreamingResponse(
                stream_gen,
                media_type="application/x-ndjson; charset=utf-8",
                headers={
                    "Cache-Control": "no-cache, no-transform",
                    "Connection": "keep-alive",
                },
            )

        try:
            result = await run_chat_helper(payload)
        except NodeBridgeError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

        try:
            return ChatResponse(**result)
        except TypeError as exc:
            raise HTTPException(status_code=500, detail="Malformed response from agentic chatbot") from exc
    @app.get("/chatbot/mcp-status", response_model=MCPStatusResponse)
    async def mcp_status_endpoint() -> MCPStatusResponse:
        try:
            result = await run_mcp_status_helper({})
        except NodeBridgeError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

        return MCPStatusResponse(**result)
    
    @app.post("/chatbot/checklist-analysis")
    async def checklist_analysis(payload: ChecklistAnalysisRequest):
        try:
            content = payload.request
            query = payload.query
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
    
    @app.post("/chatbot/details-analysis")
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
    
    @app.post("/chatbot/cloud-comparison")
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
    
    @app.post("/chatbot/cloud-comparison/cloud-provider", response_model=CloudMultipleDataResponse)
    async def cloud_comparison_multiple(request: CloudComparisonQueryMultipleRequest):
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

    @app.post("/chatbot/cloud-comparison/cloud-provider/filter", response_model=CloudMultipleDataResponse)
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

    @app.post("/chatbot/simple-query")
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

    return app


app = create_app()
