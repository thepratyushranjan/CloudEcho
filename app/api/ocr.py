# -*- coding: utf-8 -*-

from fastapi import APIRouter, HTTPException
from models.ocr import OcrRequest
from services.ocr_service import OcrService

router = APIRouter()

@router.post("/invoice")
async def invoice_ocr(request: OcrRequest):
    
    invoice_service = OcrService(ocr_type="invoice")
    
    try:
        final_response = invoice_service.process_ocr(request.base64_string)
        
        if not final_response:
            raise HTTPException(status_code=404, detail="No relevant documents found.")
        
        return {"response": final_response}
    
    except Exception as e:
        print(e,flush=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/passbook")
async def passbook_ocr(request: OcrRequest):

    invoice_service = OcrService(ocr_type="passbook")
    
    try:
        final_response = invoice_service.process_ocr(request.base64_string)
        
        if not final_response:
            raise HTTPException(status_code=404, detail="No relevant documents found.")
        
        return {"response": final_response}
    
    except Exception as e:
        print(e,flush=True)
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/electricity-bill")
async def electricity_bill_ocr(request: OcrRequest):

    invoice_service = OcrService(ocr_type="electricity_bill")
    
    try:
        final_response = invoice_service.process_ocr(request.base64_string)
        
        if not final_response:
            raise HTTPException(status_code=404, detail="No relevant documents found.")
        
        return {"response": final_response}
    
    except Exception as e:
        print(e,flush=True)
        raise HTTPException(status_code=400, detail=str(e))
