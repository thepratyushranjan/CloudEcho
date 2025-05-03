# -*- coding: utf-8 -*-

from fastapi import APIRouter, HTTPException
from models.ocr import OcrRequest
from services.ocr_service import OcrService

router = APIRouter()

@router.post("/invoice")
async def invoice_ocr(request: OcrRequest):
    """
    Queries the documentation database using vector search.
    The endpoint receives a query (and optionally a collection_name),
    generates its embedding, performs a vector search, and returns the final answer.
    """
    invoice_service = OcrService()
    
    try:
        # print(request.base64_string,flush=True)
        # print(type(request.base64_string),flush=True)
        final_response = invoice_service.process_ocr(request.base64_string, ocr_type="invoice")
        
        if not final_response:
            raise HTTPException(status_code=404, detail="No relevant documents found.")
        
        return {"response": final_response}
    
    except Exception as e:
        print(e,flush=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/passbook")
async def passbook_ocr(request: OcrRequest):
    """
    Queries the documentation database using vector search.
    The endpoint receives a query (and optionally a collection_name),
    generates its embedding, performs a vector search, and returns the final answer.
    """
    invoice_service = OcrService()
    
    try:
        # print(request.base64_string,flush=True)
        # print(type(request.base64_string),flush=True)
        final_response = invoice_service.process_ocr(request.base64_string, ocr_type="passbook")
        
        if not final_response:
            raise HTTPException(status_code=404, detail="No relevant documents found.")
        
        return {"response": final_response}
    
    except Exception as e:
        print(e,flush=True)
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/electricity-bill")
async def electricity_bill_ocr(request: OcrRequest):
    """
    Queries the documentation database using vector search.
    The endpoint receives a query (and optionally a collection_name),
    generates its embedding, performs a vector search, and returns the final answer.
    """
    invoice_service = OcrService()
    
    try:
        # print(request.base64_string,flush=True)
        # print(type(request.base64_string),flush=True)
        final_response = invoice_service.process_ocr(request.base64_string, ocr_type="electricity_bill")
        
        if not final_response:
            raise HTTPException(status_code=404, detail="No relevant documents found.")
        
        return {"response": final_response}
    
    except Exception as e:
        print(e,flush=True)
        raise HTTPException(status_code=400, detail=str(e))
