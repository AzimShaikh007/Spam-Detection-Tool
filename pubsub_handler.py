from fastapi import APIRouter, Request
import base64
import json
import sqlite3
from gmail_service import get_message, apply_spam_label, get_gmail_service

router = APIRouter()

@router.post("/pubsub/push")
async def pubsub_push(request: Request):
    try:
        body = await request.json()
        message = body.get('message', {})
        data = message.get('data')
        
        if data:
            decoded_data = base64.b64decode(data).decode('utf-8')
            json_data = json.loads(decoded_data)
            
            history_id = json_data.get('historyId')
            
            service = get_gmail_service()
            if service:
                # We use messages.list to fetch recently added messages for simplicity
                # in a full implementation, history.list would be used with historyId
                results = service.users().messages().list(userId='me', maxResults=5).execute()
                messages = results.get('messages', [])
                
                from main import do_classification
                
                for msg in messages:
                    msg_id = msg['id']
                    
                    conn = sqlite3.connect('analytics.db')
                    c = conn.cursor()
                    c.execute("SELECT id FROM messages WHERE gmail_message_id = ?", (msg_id,))
                    exists = c.fetchone()
                    
                    if not exists:
                        email_data = get_message(msg_id)
                        if email_data and email_data.get('body'):
                            classification = do_classification(email_data['body'])
                            
                            reasons_json = json.dumps(classification['reasons'])
                            c.execute(
                                "INSERT INTO messages (gmail_message_id, message, is_spam, confidence, reasons) VALUES (?, ?, ?, ?, ?)",
                                (msg_id, email_data['body'], classification['is_spam'], classification['confidence'], reasons_json)
                            )
                            conn.commit()
                            
                            if classification['is_spam']:
                                apply_spam_label(msg_id)
                    conn.close()
                    
        return {"status": "ok"}
    except Exception as e:
        print(f"Error processing pubsub push: {e}")
        return {"status": "error", "detail": str(e)}
