from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import time
import os
import threading
import sqlite3
import pickle
import numpy as np
import re
from fastapi.middleware.cors import CORSMiddleware
import spacy
import telegram_bot

app = FastAPI(title="Spam Detection API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SpaCy Vector Embedding System
try:
    print("Loading SpaCy en_core_web_md model...")
    nlp = spacy.load('en_core_web_md')
    
    print("Loading offline classifier model...")
    with open('spam_model.pkl', 'rb') as f:
        model = pickle.load(f)
    print("✅ SpaCy Context-Aware Model loaded successfully")
except Exception as e:
    print(f"Error loading offline ML models: {e}")
    model = None
    nlp = None

def setup_db():
    conn = sqlite3.connect('analytics.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            is_spam BOOLEAN,
            confidence REAL,
            is_correct BOOLEAN DEFAULT 1,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.on_event("startup")
def startup_event():
    # Setup SQLite database
    setup_db()
    
    # Only start bot if token is configured
    token = os.environ.get("TELEGRAM_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
    if token != "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("Starting background Telegram Bot thread...")
        threading.Thread(target=telegram_bot.main, daemon=True).start()
    else:
        print("Telegram bot not started (no token configured).")

class MessageRequest(BaseModel):
    message: str

class MessageResponse(BaseModel):
    is_spam: bool
    confidence: float
    category: str
    processing_time_ms: float
    message_id: int

class FeedbackRequest(BaseModel):
    message_id: int

@app.get("/", response_class=HTMLResponse)
async def root():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return HTMLResponse(content=f"Error loading index.html: {e}", status_code=500)

@app.post("/classify", response_model=MessageResponse)
async def classify_message(request: MessageRequest):
    if model is None or nlp is None:
        raise HTTPException(status_code=500, detail="Offline ML Models not loaded.")
    
    start_time = time.time()
    
    try:
        # Step 1: Clean and Normalize Text
        clean_msg = str(request.message).lower()
        clean_msg = re.sub(r'[^\w\s]', '', clean_msg).strip()
        
        # Step 2: Generate Vector Embedding using SpaCy
        embedding = nlp(clean_msg).vector.reshape(1, -1)
        
        # Step 3: Use offline model to predict
        prediction = model.predict(embedding)[0]
        probabilities = model.predict_proba(embedding)[0]
        confidence = float(probabilities[prediction])
        is_spam_val = bool(prediction)
        
        # Save to DB
        conn = sqlite3.connect('analytics.db')
        c = conn.cursor()
        c.execute("INSERT INTO messages (message, is_spam, confidence) VALUES (?, ?, ?)", 
                  (request.message, is_spam_val, confidence))
        msg_id = c.lastrowid
        conn.commit()
        conn.close()
        
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return MessageResponse(
            is_spam=is_spam_val,
            confidence=confidence,
            category="Spam" if is_spam_val else "Ham",
            processing_time_ms=round(processing_time, 2),
            message_id=msg_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def process_feedback(req: FeedbackRequest):
    try:
        conn = sqlite3.connect('analytics.db')
        c = conn.cursor()
        c.execute("UPDATE messages SET is_correct = 0 WHERE id = ?", (req.message_id,))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Feedback recorded."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    try:
        conn = sqlite3.connect('analytics.db')
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM messages")
        total = c.fetchone()[0] or 0
        
        c.execute("SELECT COUNT(*) FROM messages WHERE is_spam = 1")
        total_spam = c.fetchone()[0] or 0
        
        c.execute("SELECT COUNT(*) FROM messages WHERE is_correct = 0")
        total_mistakes = c.fetchone()[0] or 0
        
        c.execute("SELECT AVG(confidence) FROM messages")
        avg_conf = c.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            "total_scanned": total,
            "total_spam": total_spam,
            "total_safe": total - total_spam,
            "mistakes_reported": total_mistakes,
            "accuracy_rate": 100.0 if total == 0 else round(((total - total_mistakes) / total) * 100, 2),
            "average_confidence": round(avg_conf * 100, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "offline_ai_active": model is not None
    }