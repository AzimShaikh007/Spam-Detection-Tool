# Context-Aware Spam Detection System

An offline, context-aware NLP system that uses Deep Learning word embeddings to classify text messages as **Spam** or **Ham**. Unlike simple keyword-blockers, this project actually understands the semantic meaning of sentences using **SpaCy** GloVe vectors!

It features a fast API backend, a clean web interface, and an integrated Telegram Bot.

## ✨ Features
- **100% Offline AI**: Uses locally hosted SpaCy NLP vectors (no expensive API keys or rate limits).
- **Web Dashboard**: A lightweight frontend to instantly test messages and view analytics.
- **Telegram Bot Integration**: Forward messages to your Telegram bot and it will automatically classify them.
- **Analytics Database**: Automatically logs all classifications into a local SQLite database for statistical tracking.

## 🚀 How to Run Locally

### 1. Install Dependencies
Make sure you have Python installed, then run:
```powershell
pip install -r requirements.txt
```

### 2. Download the AI Language Brain (Important!)
Because the AI understands complex context, it needs a pre-trained dictionary of word vectors. Download it by running:
```powershell
python -m spacy download en_core_web_md
```

### 3. Start the Server
Boot up the FastAPI backend:
```powershell
uvicorn main:app --reload
```

Open your browser and navigate to `http://localhost:8000` to start using the app!

---

## 📁 File Structure
* `main.py` - The FastAPI backend, database manager, and AI execution script.
* `spam_model.pkl` - The trained Logistic Regression model.
* `index.html` - The frontend web interface.
* `telegram_bot.py` - The background worker for Telegram integration.
* `requirements.txt` - Python dependencies.

## 🤖 Optional: Setup Telegram Bot
If you want the Telegram bot to work, simply create a file called `.env` in this folder and add your bot token like this:
```
TELEGRAM_TOKEN=your_bot_token_here
```
When you start the server, the bot will automatically start listening in the background!
