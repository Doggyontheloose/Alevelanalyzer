
import streamlit as st
import time

from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Use whichever model your assistant was created with
model = "gpt-4o-mini"

#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                        CUSTOMIZE YOUR APP COLOR AND FONT BELOW
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
st.markdown("""
<style>
.stApp {
   font-family: 'sans-serif' !important; 
   color: #FFA500 !important;  
   background-color: ##7DF9FF !important; 
}
.stApp * {
   font-family: inherit !important;
   color: inherit !important;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")

# Function to get assistant response
def get_assistant_response(assistant_id, input_text, thread_id):
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=input_text
    )

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )

    # Poll until the run is complete
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        if run_status.status == 'completed':
            break
        elif run_status.status in ['failed', 'cancelled', 'expired']:
            return "⚠️ Sorry, something went wrong.", []
        time.sleep(1)

    # Get the latest assistant message
    messages = cleint.beta.threads.messages.list(
        thread_id=thread_id,
        order="desc",
        limit=1
    )

    latest_message = messages.data[0]
    if latest_message.role != "assistant" or latest_message.run_id != run.id:
        return "⚠️ No valid response.", []

    return latest_message.content[0].text.value, []


#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                         APP SETUP
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

st.title("A-Level Analyzer")
st.subheader("For math and sciences")

# Replace with your existing assistant ID (already created via API with vector store & files)
ASSISTANT_ID = "asst_kALsd8EA7g4f88QHioNTA50y"

# Initialize session state
for key in ['thread_id', 'messages']:
    if key not in st.session_state:
        st.session_state[key] = None if key == 'thread_id' else []

# Create thread if not exists
if st.session_state.thread_id is None:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if user_input := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply, _ = get_assistant_response(
                ASSISTANT_ID,
                user_input,
                st.session_state.thread_id
            )
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

# Clear conversation
if st.session_state.messages:
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.session_state.thread_id = client.beta.threads.create().id
        st.rerun()
