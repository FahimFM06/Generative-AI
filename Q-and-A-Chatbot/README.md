# 💬 Groq-Powered Q&A Chatbot  
### A Multi-Page Streamlit Chat Application Using LangChain and Groq API  

🔗 **Live Application:**  
https://chatbot-cdb8appvfzeedfhbbwgxw2v.streamlit.app/

---

## 📌 Project Overview

This project is a modern multi-page Q&A chatbot built using:

- **Streamlit** (for the web interface)
- **LangChain** (for model interaction handling)
- **Groq API** (for fast LLM inference)
- **GitHub + Streamlit Community Cloud** (for free deployment)

The chatbot allows users to:

- Select different Groq models
- Adjust temperature and max tokens
- Chat in a clean and modern interface
- Navigate between landing, setup, and chat pages
- Run fully online without installing anything locally

This project is suitable for:

- Educational demonstrations  
- Portfolio projects  
- Research experiments with LLM APIs  
- Beginners learning Streamlit deployment  

---


### Folder Explanation

- **app.py** → Main Streamlit application  
- **requirements.txt** → Python dependencies  
- **assets/** → Background images used in the UI  
- **README.md** → Project documentation  

---

## ⚙️ Technologies Used

| Technology | Purpose |
|------------|----------|
| Streamlit | Frontend web application |
| LangChain | LLM integration |
| Groq API | Model inference |
| Python | Backend logic |
| GitHub | Version control |
| Streamlit Cloud | Free hosting |

---

## 🚀 How the Application Works

The application contains three main sections:

### 1️⃣ Landing Page
- Displays project introduction
- Shows features and project information
- Provides navigation buttons

### 2️⃣ Setup Page
- User selects:
  - Model
  - Temperature
  - Max Tokens
- Settings are stored using Streamlit session state

### 3️⃣ Chat Page
- User submits a message
- Message is sent to Groq model via LangChain
- Response is displayed
- Chat history remains during the session

---

## 🧠 Supported Groq Models

Currently supported models in this project:

- `llama-3.1-8b-instant`
- `llama-3.3-70b-versatile`
- `groq/compound-mini`
- `groq/compound`

> Note: Some older models (such as `gemma2-9b-it`) were deprecated by Groq and are no longer supported.

---

## 🔐 API Key Setup

This project requires a Groq API key.

### Step 1: Generate API Key

1. Visit: https://console.groq.com/
2. Create or log into your account
3. Navigate to **API Keys**
4. Generate a new key

---

### Step 2: Add API Key to Streamlit Cloud

In Streamlit Cloud:

1. Open your deployed app
2. Click **Settings → Secrets**
3. Add the following:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
