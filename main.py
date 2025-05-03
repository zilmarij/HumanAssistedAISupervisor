from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import boto3
import uuid
from datetime import datetime
from agent import handle_call, handle_supervisor_response
from db import resolve_help_request, add_to_knowledge_base, get_help_requests_by_status, get_knowledge_base_entries

app = FastAPI()
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
help_requests_table = dynamodb.Table('help_requests')
knowledge_base_table = dynamodb.Table('knowledge_base')
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup_event():
    print("Application running at http://127.0.0.1/5000")
    
@app.get("/")
async def root():
    return {"message": "Frontdesk AI Supervisor System"}

@app.post("/call")
async def receive_call(question: str = Form(...), caller_id: str = Form(...)):
    """
    Simulate receiving a call with a question from a caller.
    """
    result = handle_call(question, caller_id, knowledge_base_table, help_requests_table)
    return JSONResponse(content={"answer": result["answer"]})

@app.get("/supervisor", response_class=HTMLResponse)
async def supervisor_dashboard(request: Request):
    """
    Render the supervisor UI dashboard.
    """
    pending_requests = get_help_requests_by_status("Pending")
    resolved_requests = get_help_requests_by_status("Resolved")
    unresolved_requests = get_help_requests_by_status("Unresolved")
    knowledge_base = get_knowledge_base_entries()
    return templates.TemplateResponse("supervisor.html", {
        "request": request,
        "pending_requests": pending_requests,
        "resolved_requests": resolved_requests,
        "unresolved_requests": unresolved_requests,
        "knowledge_base": knowledge_base
    })

@app.post("/supervisor/respond")
async def submit_response(request_id: str = Form(...), answer: str = Form(...)):
    """
    Handle supervisor response to a help request.
    Update the request status, simulate caller follow-up, and update knowledge base.
    """
    try:
        # Fetch the request to get caller_id and question
        request_data = help_requests_table.get_item(Key={'id': request_id}).get('Item')
        if not request_data:
            raise HTTPException(status_code=404, detail="Request not found")
        if request_data['status'] != 'Pending':
            raise HTTPException(status_code=400, detail="Request already processed")

        caller_id = request_data['caller_id']
        question = request_data['question']

        # Update help request as resolved
        resolve_help_request(request_id, answer)

        # Simulate texting back to caller
        handle_supervisor_response(request_id, question, answer, caller_id)

        # Update knowledge base with new answer
        add_to_knowledge_base(question, answer)

        return JSONResponse(content={"message": "Response submitted successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing response: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)