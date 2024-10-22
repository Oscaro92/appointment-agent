import time
import streamlit as st
from agent import AgentRDV

st.title("🤖 Appointment LSP")
agent = AgentRDV()

def stream_data(response):
    for word in response.split(" "):
        yield word + " "
        time.sleep(0.05)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# React to user input
if prompt := st.chat_input("Que puis-je faire pour toi ? "):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("Loading response..."):
            print(prompt)
            response = agent.chat(st.session_state.messages)
        st.write_stream(stream_data(response))

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
