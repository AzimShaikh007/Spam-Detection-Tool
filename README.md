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

## 📧 Gmail API & Chrome Extension Setup

This project now includes a Gmail API integration with a Chrome Extension to highlight spam directly in your inbox.

### 1. Google Cloud Setup
- Create a Google Cloud project.
- Enable the **Gmail API** and **Cloud Pub/Sub API**.
- Create an OAuth 2.0 Client ID (Desktop App) and download the credentials. Save it as `credentials.json` in the root directory.

### 2. Pub/Sub Setup
- Create a Pub/Sub topic in your Google Cloud Console.
- Create a **push subscription** for this topic pointing to your backend endpoint (e.g., `https://your-ngrok-url.com/pubsub/push`).

### 3. Required Environment Variables
Create a `.env` file in the root directory:
```
PUBSUB_TOPIC=projects/your-project-id/topics/your-topic-name
TELEGRAM_TOKEN=your_bot_token_here
```

### 4. Running the Backend
Boot up the FastAPI backend (with auto-reload):
```powershell
uvicorn main:app --reload
```
Note: You may need to use a tool like `ngrok` to expose your local port 8000 to the internet so Google Pub/Sub can reach the webhook.

### 5. Loading the Chrome Extension
1. Open Google Chrome and go to `chrome://extensions/`.
2. Enable **Developer mode** in the top right corner.
3. Click **Load unpacked** and select the `extension` folder in this project directory.
4. Refresh your Gmail inbox to see the extension in action!
