import streamlit as st
import requests
import uuid

API_URL = "https://ghost-message-wjr1.onrender.com"

# --- Sticky ID Logic ---
if "my_ghost_id" not in st.session_state:
    # This only runs the VERY first time they open the page
    st.session_state.my_ghost_id = f"Ghost-{str(uuid.uuid4())[:8]}"

my_id = st.session_state.my_ghost_id

st.title("👻 GhostBox")
st.info(f"Your Permanent ID for this session: **{my_id}**")


# --- Updated Message Input ---
with st.form("message_form", clear_on_submit=True):
    user_text = st.text_area("Write a message...")
    submitted = st.form_submit_button("Send")
    
    if submitted and user_text:
        # We now send the 'my_id' along with the text
        response = requests.post(
            f"{API_URL}/send", 
            params={"text": user_text, "sender_id": my_id}
        )
        if response.status_code == 200:
            st.rerun() # Refresh the feed immediately

# --- Message Feed ---
st.divider()
st.subheader("The Feed")

try:
    messages = requests.get(f"{API_URL}/messages").json()
    # Show newest messages first
    for msg in reversed(messages):
        with st.chat_message("user", avatar="👤"):
            st.write(f"**{msg['sender_id']}**")
            st.write(msg['text'])
            st.caption(f"Posted on: {msg['created_at'][:16]}")
except:

    st.info("No messages yet. Be the first!")
