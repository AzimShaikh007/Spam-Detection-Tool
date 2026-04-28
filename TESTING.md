# Running & Testing the Gmail Spam Detector

This guide covers the end-to-end process of setting up, running, and testing the newly added Gmail API, Pub/Sub, and Chrome Extension features.

## 🛠️ Prerequisites & Setup

### 1. Google Cloud Configuration
To allow the app to read emails and apply labels, you need Google API credentials.
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Search for **Gmail API** and **Cloud Pub/Sub API** in the library and **Enable** both.
4. Go to **APIs & Services > Credentials**.
5. Click **Create Credentials** > **OAuth client ID**.
6. Set the Application type to **Desktop app**, name it, and create it.
7. Click **Download JSON** on the newly created credentials and save it exactly as `credentials.json` in the root folder of this project (`d:\Spam-Detection-Tool`).

### 2. Pub/Sub & Webhook Tunneling (Ngrok)
Google Pub/Sub requires a public HTTPS URL to push notifications to when you get a new email. 
1. Download and install [ngrok](https://ngrok.com/).
2. Start an ngrok tunnel pointing to your local port 8000:
   ```bash
   ngrok http 8000
   ```
3. Copy the **Forwarding URL** (e.g., `https://abcdef123.ngrok-free.app`).
4. In the Google Cloud Console, go to **Pub/Sub > Topics** and create a topic (e.g., `gmail-spam-watch`).
5. Click on the topic, go to **Subscriptions**, and create a **Push** subscription. 
6. Set the **Endpoint URL** to your ngrok URL + the route: `https://abcdef123.ngrok-free.app/pubsub/push`.

### 3. Environment Variables
Create a file named `.env` in your root folder and add the Pub/Sub topic string (found in your GCP console):
```env
PUBSUB_TOPIC=projects/your-project-id/topics/gmail-spam-watch
```

---

## 🚀 Running the Application

### 1. Start the Backend Server
Open your terminal in the project folder and run:
```powershell
uvicorn main:app --reload
```
* **First Time Setup:** The very first time you run this, a Google Login window will automatically open in your browser. Log in with the Gmail account you want to monitor and grant the requested permissions. A `token.json` file will be generated automatically so you don't have to do this again.

### 2. Load the Chrome Extension
1. Open Google Chrome and type `chrome://extensions/` in the URL bar.
2. Toggle **Developer mode** ON (top right corner).
3. Click the **Load unpacked** button (top left).
4. Select the `extension` folder located inside your `Spam-Detection-Tool` project.
5. The extension is now active and watching your Gmail tabs!

---

## 🧪 How to Test the Flow

Now that everything is running, let's trigger the entire lifecycle!

### Step 1: Send a "Spam" Email
From a different email address (or simply send it to yourself), send an email to the Gmail account you linked during setup. 
To trigger the AI and our mock reasons, include some of these red-flag keywords in the body of your email:
> "Urgent action required! You are the grand prize winner! Click here to claim your free money immediately. Confirm your login and password now."

### Step 2: Watch the Magic Happen (Backend)
1. Within seconds of the email arriving, Google will fire a push notification to your ngrok URL.
2. Check your backend terminal window. You should see incoming requests to `POST /pubsub/push`.
3. The backend will fetch the email, run the SpaCy text classification, and identify it as spam.
4. It will automatically apply a red `⚠ Spam-Detected` label directly inside your actual Gmail account.

### Step 3: View the Chrome Extension UI
1. Open Gmail in Chrome (`https://mail.google.com`).
2. Look at your Inbox. Next to the subject line of the email you just sent, you should instantly see a custom injected red **⚠ Spam** badge.
3. **Hover your mouse** over the badge. A sleek, dark tooltip will appear displaying the exact reasons the AI flagged the message (e.g., *"Urgency language detected"*, *"Prize or money bait"*).

### Step 4: False Positive Feedback Loop (Optional)
If you want to test the feedback loop:
1. Open the local dashboard (`http://localhost:8000`).
2. Simulate a feedback submission to the `/feedback` endpoint marking that specific message ID as `is_spam: false`.
3. The backend will reach back out to the Gmail API and automatically remove the `⚠ Spam-Detected` label from that email.
