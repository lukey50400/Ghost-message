import streamlit as st
import requests
import uuid

API_URL = "https://ghost-message-wjr1.onrender.com" 

st.set_page_config(page_title="GhostBox", page_icon="👻")

# --- STICKY ID (Outside the Fragment) ---
# This stays the same as long as you don't close the tab
if "my_ghost_id" not in st.session_state:
    st.session_state.my_ghost_id = f"Ghost-{str(uuid.uuid4())[:8]}"

my_id = st.session_state.my_ghost_id

st.title("👻 GhostBox")
st.caption(f"Logged in as: **{my_id}**")

# --- SEND MESSAGE SECTION ---
with st.form("message_form", clear_on_submit=True):
    user_text = st.text_area("Write something...")
    submitted = st.form_submit_button("Send")
    
    if submitted and user_text:
        requests.post(f"{API_URL}/send", params={"text": user_text, "sender_id": my_id})
        

st.divider()

# --- THE MESSAGE FEED (The Only Part That Refreshes) ---
@st.fragment(run_every=10)
def message_feed():
    st.subheader("Live Feed")
    try:
        response = requests.get(f"{API_URL}/messages")
        if response.status_code == 200:
            messages = response.json()
            for msg in reversed(messages):
                with st.chat_message("user"):
                    st.write(f"**{msg['sender_id']}**")
                    st.write(msg['text'])
                    st.caption(f"{msg['created_at']}")
    except:
        st.error("Connecting to the Ghost Brain...")

message_feed()
