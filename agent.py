import uuid
from datetime import datetime
from livekit import rtc  # LiveKit SDK for Python (simulated usage)

def handle_call(question: str, caller_id: str, knowledge_base_table, help_requests_table):
    """
    Handle an incoming call (simulated or via LiveKit).
    Check knowledge base; if unknown, escalate to supervisor.
    """
    try:
        kb_response = knowledge_base_table.query(
            IndexName='question-index',
            KeyConditionExpression='question = :q',
            ExpressionAttributeValues={':q': question}
        )
        if kb_response.get('Items'):
            answer = kb_response['Items'][0]['answer']
            print(f"AI Response to {caller_id}: {answer}")
            return {"answer": answer}
    except Exception as e:
        print(f"Error querying knowledge base: {e}")

    # If no answer found, escalate to supervisor
    request_id = str(uuid.uuid4())
    try:
        help_requests_table.put_item(Item={
            'id': request_id,
            'caller_id': caller_id,
            'question': question,
            'status': 'Pending',
            'created_at': datetime.utcnow().isoformat(),
            'resolved_at': None,
            'supervisor_response': None
        })
        print(f"AI: Let me check with my supervisor and get back to you.")
        print(f"Simulated SMS to supervisor: Hey, I need help answering '{question}' (ID: {request_id})")
        return {"answer": "Let me check with my supervisor and get back to you."}
    except Exception as e:
        print(f"Error creating help request: {e}")
        return {"answer": "I'm having trouble processing your request. Please try again later."}

def handle_supervisor_response(request_id: str, question: str, answer: str, caller_id: str):
    """
    Simulate sending a response back to the caller after supervisor input.
    """
    print(f"AI: Texting back to {caller_id}: Regarding your question '{question}': {answer}")

def simulate_livekit_call(question: str, caller_id: str, knowledge_base_table, help_requests_table):
    """
    Simulate a LiveKit call event for demo purposes.
    """
    print(f"Simulating LiveKit call from {caller_id} with question: '{question}'")
    return handle_call(question, caller_id, knowledge_base_table, help_requests_table)