import streamlit as st
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("BACKEND_URL")

st.set_page_config(
    page_title="Cold Case Detective",
    page_icon="🕵️",
    layout="wide"
)

st.markdown("""
<style>
body {
    background-color: #0b0f14;
}
.chat-container {
    max-width: 780px;
    margin: auto;
}
.user-bubble {
    background: #2563eb;
    color: white;
    padding: 12px 16px;
    border-radius: 14px;
    margin: 10px 0;
    text-align: right;
    animation: fade 0.3s;
}
.bot-bubble {
    background: #1e293b;
    color: white;
    padding: 12px 16px;
    border-radius: 14px;
    margin: 10px 0;
    text-align: left;
    animation: fade 0.3s;
}
.source-box {
    font-size: 13px;
    opacity: 0.7;
    margin-top: 6px;
}
@keyframes fade {
    from {opacity: 0;}
    to {opacity: 1;}
}
hr {
    border: 0;
    height: 1px;
    background: #222;
}
</style>
""", unsafe_allow_html=True)


# Session State

if "token" not in st.session_state:
    st.session_state.token = None

if "username" not in st.session_state:
    st.session_state.username = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "loaded_history" not in st.session_state:
    st.session_state.loaded_history = False



# Sidebar Auth

st.sidebar.title("Account")

if not st.session_state.token:

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Register"):
        res = requests.post(
            f"{API_URL}/register",
            json={"username": username, "password": password}
        )

        if res.status_code == 200:
            st.sidebar.success("Registered successfully!")
        else:
            st.sidebar.error("Registration failed")
            st.sidebar.code(res.text)

    if st.sidebar.button("Login"):
        res = requests.post(
            f"{API_URL}/login",
            json={"username": username, "password": password}
        )

        if res.status_code == 200:
            st.session_state.token = res.json()["access_token"]
            st.session_state.username = username
            st.sidebar.success("Logged in!")
            st.rerun()
        else:
            st.sidebar.error("Invalid username or password")

else:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    st.sidebar.success(f"Logged in as **{st.session_state.username}**")

    # Quota Display
    q = requests.get(f"{API_URL}/quota", headers=headers).json()
    st.sidebar.write(f"🛡️ Remaining Today: **{q['remaining']} / 15**")

    with st.spinner("Waking up detective..."):
        try:
            requests.get(f"{API_URL}/docs", timeout=5)
        except:
            st.sidebar.warning("Server is starting, please wait...")

    # New Converstion Button
    if st.sidebar.button("New Conversation"):
        requests.delete(f"{API_URL}/history", headers=headers)
        st.session_state.messages = []
        st.session_state.loaded_history = True
        st.rerun()


    # Logout Button
    if st.sidebar.button("🚪 Logout"):
        st.session_state.token = None
        st.session_state.username = None
        st.session_state.messages = []
        st.session_state.loaded_history = False
        st.sidebar.info("Logged out!")
        st.rerun()



# Response Style Toggle

st.sidebar.divider()
st.sidebar.title("Response Mode")

strict_mode = st.sidebar.toggle(
    "Strict citations (Detective Mode)",
    value=True
)


# Upload Evidence

st.sidebar.divider()
st.sidebar.title("📂 Upload Evidence")

uploaded = st.sidebar.file_uploader(
    "Upload TXT or PDF files",
    type=["txt", "pdf"],
    accept_multiple_files=True
)

if uploaded and st.session_state.token:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    for file in uploaded:
        res = requests.post(
            f"{API_URL}/upload",
            files={"file": (file.name, file.getvalue())},
            headers=headers
        )

    st.sidebar.success("Evidence uploaded successfully!")



# Load Chat History Once

if st.session_state.token and not st.session_state.loaded_history:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    res = requests.get(f"{API_URL}/history", headers=headers)

    if res.status_code == 200:
        history = res.json()

        for chat in history:
            st.session_state.messages.append(
                {"role": "user", "content": chat["question"]}
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": chat["answer"]}
            )

    st.session_state.loaded_history = True



# Main Header

st.markdown(
    "<h1 style='text-align:center;'>🕵️ Detective</h1>",
    unsafe_allow_html=True
)

st.write(
    "<p style='text-align:center; opacity:0.7;'>Ask questions only from uploaded evidence files.</p>",
    unsafe_allow_html=True
)

st.markdown("<hr>", unsafe_allow_html=True)



# Chat Window

st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f"<div class='user-bubble'>{msg['content']}</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='bot-bubble'>{msg['content']}</div>",
            unsafe_allow_html=True
        )

st.markdown("</div>", unsafe_allow_html=True)



# Chat Input

question = st.chat_input("Ask the detective...")

if question:

    if not st.session_state.token:
        st.error("Please login first.")
        st.stop()

    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    res = requests.post(
        f"{API_URL}/ask",
        json={"question": question, "strict": strict_mode},
        headers=headers
    )

    if res.status_code != 200:
        st.error("Backend error:")
        st.code(res.text)
        st.stop()

    data = res.json()

    answer = data["answer"]
    citations = ", ".join(data["citations"])

    bot_msg = f"""
{answer}

<div class='source-box'>Sources: {citations}</div>
"""

    st.session_state.messages.append(
        {"role": "assistant", "content": bot_msg}
    )

    time.sleep(0.15)
    st.rerun()
