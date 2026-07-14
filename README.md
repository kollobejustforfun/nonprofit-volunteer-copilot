# 🤝 Volunteer Copilot

**Helping nonprofits spend less time managing volunteers and more time creating impact.**

Volunteer Copilot is a practical AI-powered platform designed specifically for nonprofit organizations. It reduces repetitive administrative work by allowing coordinators to upload event information once, while volunteers can instantly access accurate answers through an intelligent assistant.

**Live Demo:** [Add your Streamlit Cloud URL here after deployment]  
**Tech Stack:** Streamlit • ChromaDB (RAG) • BAAI/bge-small-zh-v1.5 • Groq (Llama-3.3-70B)  
**Status:** Fully functional MVP • Ready for portfolio & real nonprofit use  
**Built for:** Cloud Code Scholarship Fellowship

---

## The Problem

Nonprofit coordinators often spend a large amount of time answering repetitive questions from volunteers, such as:

- What is the dress code?
- Where do I park?
- What time does the event start?
- What should I bring?

This tool solves that pain point by giving coordinators **one upload** and giving volunteers **instant, accurate answers** — while also providing coordinators with usage analytics to identify gaps in their materials.

---

## Key Features

### For Volunteers
- Browse multiple upcoming volunteer opportunities with clean event cards
- Enter an event workspace with clear navigation
- Complete a structured 4-step onboarding (commitment, health, personal information, consent)
- Ask questions through an AI assistant powered by the official handbook (RAG)
- View Frequently Asked Questions with real answers from the handbook
- Send questions directly to coordinators when the AI cannot answer

### For Coordinators
- Upload volunteer handbook (PDF or TXT) — automatic processing and indexing
- Clear success feedback after upload
- View usage analytics (most asked questions, potential handbook gaps)
- Reduce time spent on repetitive inquiries

---

## How It Works

### Volunteer Flow
1. Choose **"I am a Volunteer"**
2. Browse available events
3. Click **"Enter Workspace"** on an event
4. Complete the onboarding process (name, email, dietary needs, accessibility, consent)
5. Use the AI assistant or FAQ to get answers
6. Use "Send to Coordinator" when needed

### Coordinator Flow
1. Choose **"I am an Event Coordinator"**
2. Upload the volunteer handbook
3. Receive confirmation that the handbook has been processed
4. Volunteers can now ask questions based on the uploaded content

---

## Why This Project Stands Out

- Solves a **real operational pain point** for nonprofits
- Combines **structured onboarding + RAG chatbot + analytics** in one application
- Answers are strictly grounded in the uploaded handbook (minimizes hallucination)
- Includes a fallback mechanism ("Send to Coordinator") when the AI cannot answer
- Clean, modern interface with event cards and professional flow
- Fully deployable for free on Streamlit Community Cloud

---

## Tech Stack

| Component              | Technology                          | Purpose                              |
|------------------------|-------------------------------------|--------------------------------------|
| Frontend               | Streamlit                           | UI and multi-step experience         |
| Vector Database (RAG)  | ChromaDB + BAAI/bge-small-zh-v1.5   | Semantic search over handbook        |
| LLM                    | Groq (Llama-3.3-70B)                | Fast and high-quality responses      |
| PDF Processing         | pdfplumber                          | Extract text from uploaded handbooks |
| Deployment             | Streamlit Community Cloud           | Free public hosting                  |

---

## Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/volunteer-copilot.git
cd volunteer-copilot

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate          # Mac/Linux
venv\Scripts\Activate.ps1         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your Groq API key
echo "GROQ_API_KEY=your_groq_key_here" > .env

# 5. Run the app
streamlit run app.py