#!/usr/bin/env python3
"""
Volunteer Copilot - Final Version
"""

import streamlit as st
from dotenv import load_dotenv
import os
import pdfplumber
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq
from datetime import datetime

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

COLLECTION_NAME = "volunteer_handbook"
CHROMA_PATH = "./chroma_db"

# ==================== SESSION STATE ====================
if "current_role" not in st.session_state:
    st.session_state.current_role = None
if "selected_event" not in st.session_state:
    st.session_state.selected_event = None
if "onboarding_step" not in st.session_state:
    st.session_state.onboarding_step = 0
if "question_log" not in st.session_state:
    st.session_state.question_log = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "Overview"
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# ==================== SAMPLE EVENTS ====================
SAMPLE_EVENTS = [
    {"id": 1, "name": "Community Food Drive", "date": "Saturday, July 20, 2026",
     "time": "9:00 AM - 3:00 PM", "location": "Brooklyn Community Center",
     "volunteers_needed": 53, "image": "https://images.unsplash.com/photo-1593113598332-cd288d649433?w=600"},
    {"id": 2, "name": "Park Cleanup Day", "date": "Sunday, July 27, 2026",
     "time": "8:30 AM - 12:00 PM", "location": "Central Park",
     "volunteers_needed": 35, "image": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600"},
    {"id": 3, "name": "Youth Mentorship Orientation", "date": "Friday, August 1, 2026",
     "time": "6:00 PM - 8:30 PM", "location": "Harlem Youth Center",
     "volunteers_needed": 22, "image": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=600"}
]

# ==================== HELPER FUNCTIONS ====================
def get_embedding_model():
    return SentenceTransformer("BAAI/bge-small-zh-v1.5", device="cpu")

def get_chroma_client():
    os.makedirs(CHROMA_PATH, exist_ok=True)
    return chromadb.PersistentClient(path=CHROMA_PATH)

def get_groq_client():
    if not GROQ_API_KEY:
        st.error("GROQ_API_KEY not found. Please check your .env file.")
        st.stop()
    return Groq(api_key=GROQ_API_KEY)

def process_handbook(uploaded_file):
    chroma_client = get_chroma_client()
    embed_model = get_embedding_model()

    if uploaded_file.name.lower().endswith(".pdf"):
        text = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    else:
        text = uploaded_file.getvalue().decode("utf-8")

    if len(text.strip()) < 50:
        return False

    chunks = [text[i:i+700] for i in range(0, len(text), 600)]

    try:
        chroma_client.delete_collection(COLLECTION_NAME)
    except:
        pass

    collection = chroma_client.create_collection(COLLECTION_NAME)
    embeddings = embed_model.encode(chunks).tolist()
    collection.add(documents=chunks, embeddings=embeddings, ids=[f"chunk_{i}" for i in range(len(chunks))])
    return True

def get_rag_answer(question):
    try:
        chroma_client = get_chroma_client()
        collection = chroma_client.get_collection(COLLECTION_NAME)
        embed_model = get_embedding_model()
        groq_client = get_groq_client()

        query_embedding = embed_model.encode([question]).tolist()[0]
        results = collection.query(query_embeddings=[query_embedding], n_results=5, include=["documents"])

        context = "\n\n".join(results["documents"][0]) if results.get("documents") else ""
        if not context:
            return None

        prompt = f"""You are a helpful volunteer assistant.
Answer using ONLY the handbook below. If not found, say so.

Handbook Content:
{context}

Question: {question}
Answer:"""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=700
        )
        return response.choices[0].message.content.strip()
    except:
        return None

# ==================== MAIN APP ====================
def main():
    st.set_page_config(page_title="Volunteer Copilot", layout="wide")
    st.title("Volunteer Copilot")

    # ==================== LANDING PAGE (已优化) ====================
    if st.session_state.current_role is None:
        # Hero Section
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1a73e8 0%, #34a853 100%);
            padding: 70px 50px;
            border-radius: 20px;
            color: white;
            text-align: center;
            margin-bottom: 40px;
        ">
            <h1 style="font-size: 40px; font-weight: 700; margin-bottom: 16px;">
                Volunteer Copilot
            </h1>
            <p style="font-size: 22px; max-width: 720px; margin: 0 auto 16px; line-height: 1.4;">
                Helping nonprofits spend less time managing volunteers<br>
                and more time creating impact.
            </p>
            <p style="font-size: 17px; max-width: 650px; margin: 0 auto; opacity: 0.95;">
                Volunteer Copilot streamlines volunteer communication, event coordination, 
                and knowledge sharing — so your team can focus on serving communities 
                instead of answering repetitive questions.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # 两个按钮
        col1, col2 = st.columns(2)

        with col1:
            if st.button(" Continue as Volunteer", use_container_width=True, type="primary"):
                st.session_state.current_role = "Volunteer"
                st.rerun()

        with col2:
            if st.button(" Continue as Coordinator", use_container_width=True):
                st.session_state.current_role = "Coordinator"
                st.rerun()

        return

    # ==================== VOLUNTEER SIDE ====================
    if st.session_state.current_role == "Volunteer":

        if st.session_state.selected_event is None:
            st.header("Upcoming Volunteer Opportunities")
            for event in SAMPLE_EVENTS:
                with st.container(border=True):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(event["image"], use_container_width=True)
                    with col2:
                        st.subheader(event["name"])
                        st.write(f"**Date:** {event['date']}")
                        st.write(f"**Time:** {event['time']}")
                        st.write(f"**Location:** {event['location']}")
                        if st.button("Enter Workspace", key=f"enter_{event['id']}"):
                            st.session_state.selected_event = event
                            st.rerun()
            return

        event = st.session_state.selected_event

        with st.sidebar:
            st.header("Navigation")
            if st.button("Event Overview"):
                st.session_state.current_page = "Overview"
            if st.button("FAQ"):
                st.session_state.current_page = "FAQ"
            if st.button("Talk to AI Assistant"):
                st.session_state.current_page = "Chat"
            st.divider()
            if st.button("← Back to Role Selection"):
                st.session_state.current_role = None
                st.session_state.selected_event = None
                st.session_state.onboarding_step = 0
                st.rerun()

        # ==================== PAGE CONTENT ====================
        if st.session_state.current_page == "Overview":
            st.header(event["name"])
            st.write(f"**Date:** {event['date']}")
            st.write(f"**Time:** {event['time']}")
            st.write(f"**Location:** {event['location']}")

            st.divider()
            st.subheader("Onboarding Steps: Please complete the required steps before the event.")

            step = st.session_state.onboarding_step

            if step == 0:
                st.write("**Step 1: Commitment & Qualifications**")
                st.checkbox("I am available on the event date and time.")
                st.checkbox("I meet the basic requirements for this volunteer role.")
                if st.button("Next"):
                    st.session_state.onboarding_step = 1
                    st.rerun()

            elif step == 1:
                st.write("**Step 2: Health & Flexibility**")
                st.checkbox("I am in good health and able to perform volunteer duties.")
                st.checkbox("I can be flexible with minor last-minute changes.")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Back"):
                        st.session_state.onboarding_step = 0
                        st.rerun()
                with col2:
                    if st.button("Next"):
                        st.session_state.onboarding_step = 2
                        st.rerun()

            elif step == 2:
                st.write("**Step 3: Personal Information**")
                st.write("Please provide your contact details. This information will be used for event updates.")
                name = st.text_input("Full Name")
                email = st.text_input("Email Address")
                dietary = st.text_input("Dietary Restrictions (optional)")
                accessibility = st.text_area("Accessibility Needs (optional)")

                if st.button("Next") and name and email:
                    st.session_state.user_name = name
                    st.session_state.user_email = email
                    st.session_state.user_dietary = dietary
                    st.session_state.user_accessibility = accessibility
                    st.session_state.onboarding_step = 3
                    st.rerun()

            elif step == 3:
                st.write("**Step 4: Consent & Agreement**")
                c1 = st.checkbox("I have read and agree to follow the Volunteer Handbook.")
                c2 = st.checkbox("I consent to photos and videos being taken during the event.")
                c3 = st.checkbox("I understand my questions may be logged to improve future events.")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Back"):
                        st.session_state.onboarding_step = 2
                        st.rerun()
                with col2:
                    if st.button("Complete Onboarding", disabled=not (c1 and c2 and c3)):
                        st.session_state.onboarding_step = 4
                        st.rerun()

            elif step == 4:
                st.balloons()
                st.success("Onboarding Completed! Thank you for joining us.")
                st.write(f"**Name:** {st.session_state.user_name}")
                st.write(f"**Email:** {st.session_state.user_email}")

                st.divider()
                st.write("**Ask any questions you have related to this event and participation.**")

                if st.button("Talk to the AI Assistant", type="primary"):
                    st.session_state.current_page = "Chat"
                    st.rerun()

        elif st.session_state.current_page == "FAQ":
            st.header("Frequently Asked Questions")

            faqs = [
                "Will I be compensated for this volunteer event?",
                "Am I able to receive a certificate of hours for my future reference?",
                "If I need to cancel at the last minute, what should I do?"
            ]

            for q in faqs:
                if st.button(q):
                    answer = get_rag_answer(q)
                    if answer:
                        st.info(answer)
                    else:
                        st.warning("I couldn't find this information in the handbook.")

            st.divider()
            st.subheader("Still have questions?")
            with st.form("send_to_coordinator_faq"):
                message = st.text_area("Write your question for the coordinator")
                submitted = st.form_submit_button("Send to Coordinator")
                if submitted and message:
                    st.success("Thank you! Your message has been sent to the coordinator. They will get back to you within 24 hours.")

        elif st.session_state.current_page == "Chat":
            st.header("Talk to the AI Assistant")

            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            if prompt := st.chat_input("Ask your question here..."):
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    answer = get_rag_answer(prompt)
                    if answer:
                        st.markdown(answer)
                    else:
                        st.markdown("I'm sorry, I couldn't find the answer in the handbook.")
                st.session_state.chat_history.append({"role": "assistant", "content": answer or "I'm sorry, I couldn't find the answer."})

            st.divider()
            st.subheader("Not clear enough? Send to coordinator")
            with st.form("send_to_coordinator_chat"):
                message = st.text_area("Write your question here")
                submitted = st.form_submit_button("Send to Coordinator")
                if submitted and message:
                    st.success("Thank you! Your message has been sent to the coordinator. They will get back to you within 24 hours.")

    # ==================== COORDINATOR SIDE ====================
    elif st.session_state.current_role == "Coordinator":

        with st.sidebar:
            st.header("Coordinator Dashboard")
            if st.button("← Back to Role Selection"):
                st.session_state.current_role = None
                st.rerun()

        st.header("Coordinator Dashboard")
        st.write("Upload the volunteer handbook so volunteers can get accurate answers.")

        uploaded_file = st.file_uploader("Upload Handbook (PDF or TXT)", type=["pdf", "txt"])
        if uploaded_file:
            if st.button("Process Handbook"):
                if process_handbook(uploaded_file):
                    st.success("Submission has been completed")
                    st.markdown(
                        "<span style='color:green; font-weight:bold; font-size:16px;'>✓ Handbook has been successfully processed. Volunteers can now ask questions based on this handbook.</span>",
                        unsafe_allow_html=True
                    )
                else:
                    st.error("Failed to process the handbook. Please try again.")

if __name__ == "__main__":
    main()