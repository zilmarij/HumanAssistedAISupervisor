import boto3
from datetime import datetime
import uuid

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
help_requests_table = dynamodb.Table('help_requests')
knowledge_base_table = dynamodb.Table('knowledge_base')

def add_help_request(caller_id: str, question: str):
    """Create a new help request with status Pending."""
    request_id = str(uuid.uuid4())
    item = {
        'id': request_id,
        'caller_id': caller_id,
        'question': question,
        'status': 'Pending',
        'created_at': datetime.utcnow().isoformat(),
        'resolved_at': None,
        'supervisor_response': None
    }
    help_requests_table.put_item(Item=item)
    return request_id

def resolve_help_request(request_id: str, answer: str):
    """Update help request with supervisor's response and mark as Resolved."""
    resolved_time = datetime.utcnow().isoformat()
    help_requests_table.update_item(
        Key={'id': request_id},
        UpdateExpression="SET #status = :status, supervisor_response = :answer, resolved_at = :resolved_at",
        ExpressionAttributeNames={"#status": "status"},
        ExpressionAttributeValues={
            ':status': 'Resolved',
            ':answer': answer,
            ':resolved_at': resolved_time
        }
    )
    return resolved_time

def add_to_knowledge_base(question: str, answer: str):
    """Add a new Q&A pair to the knowledge base."""
    item = {
        'id': str(uuid.uuid4()),
        'question': question,
        'answer': answer,
        'added_at': datetime.utcnow().isoformat()
    }
    knowledge_base_table.put_item(Item=item)

def get_help_requests_by_status(status: str = None):
    """Fetch help requests, optionally filtered by status."""
    if status:
        response = help_requests_table.scan(
            FilterExpression='#status = :status',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':status': status}
        )
    else:
        response = help_requests_table.scan()
    return response.get('Items', [])

def get_knowledge_base_entries():
    """Fetch all entries in the knowledge base."""
    response = knowledge_base_table.scan()
    return response.get('Items', [])