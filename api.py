from fastapi import FastAPI, File, UploadFile, Form, Header, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import shutil
import os
import json

from agent_orchestrator import AgentOrchestrator

app = FastAPI(title="Multi-Agent Classifier API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "internship123"

orchestrator = AgentOrchestrator()

def verify_api_key(x_api_key: Optional[str]):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )

@app.post("/process/pdf")
async def process_pdf(
    file: UploadFile = File(None),
    text: Optional[str] = Form(None),
    sender: Optional[str] = Form(None),
    conversation_id: Optional[str] = Form(None),
    x_api_key: Optional[str] = Header(None),
):
    verify_api_key(x_api_key)
    
    if not file and not text:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Either file or text must be provided"}
        )
    
    try:
        if file:
            # Handle file upload
            temp_path = f"temp_{file.filename}"
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            result = orchestrator.route_input(temp_path, sender=sender, 
                                           conversation_id=conversation_id, 
                                           input_format="PDF")
            os.remove(temp_path)
        else:
            # Handle direct text content
            result = orchestrator.route_input(text, sender=sender,
                                           conversation_id=conversation_id,
                                           input_format="PDF")

        return JSONResponse(content={"success": True, "result": result})

    except Exception as e:
        return JSONResponse(
            status_code=500, 
            content={"success": False, "error": str(e)}
        )

@app.post("/process/pdf/text")
async def process_pdf_text(
    text: str = Form(...),
    sender: Optional[str] = Form(None),
    conversation_id: Optional[str] = Form(None),
    x_api_key: Optional[str] = Header(None),
):
    """Process PDF content directly from text input."""
    verify_api_key(x_api_key)
    try:
        result = orchestrator.route_input(text, sender=sender,
                                       conversation_id=conversation_id,
                                       input_format="PDF")
        return JSONResponse(content={"success": True, "result": result})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.post("/process/text")
async def process_text(
    text: str = Form(...),
    sender: Optional[str] = Form(None),
    conversation_id: Optional[str] = Form(None),
    x_api_key: Optional[str] = Header(None),
):
    verify_api_key(x_api_key)
    try:
        result = orchestrator.route_input(text, sender=sender, conversation_id=conversation_id, input_format="Text")
        return JSONResponse(content={"success": True, "result": result})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.post("/process/email")
async def process_email(
    email_text: str = Form(...),
    sender: Optional[str] = Form(None),
    conversation_id: Optional[str] = Form(None),
    x_api_key: Optional[str] = Header(None),
):
    verify_api_key(x_api_key)
    try:
        result = orchestrator.route_input(email_text, sender=sender, conversation_id=conversation_id, input_format="Email")
        return JSONResponse(content={"success": True, "result": result})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.post("/process/json")
async def process_json(
    json_data: str = Form(...),
    sender: Optional[str] = Form(None),
    conversation_id: Optional[str] = Form(None),
    x_api_key: Optional[str] = Header(None),
):
    verify_api_key(x_api_key)
    try:
        data = json.loads(json_data)
        result = orchestrator.route_input(data, sender=sender, conversation_id=conversation_id, input_format="JSON")
        return JSONResponse(content={"success": True, "result": result})
    except json.JSONDecodeError:
        return JSONResponse(status_code=400, content={"success": False, "error": "Invalid JSON data"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.get("/")
async def root():
    return {"message": "Multi-Agent Classifier API is running"}
