import logging
import streamlit as st
import time
import base64
from docusign_esign import Document, ApiClient, EnvelopeDefinition, EnvelopesApi, Signer, Tabs, SignHere, Recipients
import requests
from streamlit_oauth import OAuth2Component
from streamlit_theme import st_theme
from ds_config import DS_CONFIG as ds_config
from ollama import chat
from ollama import ChatResponse

#%% ollama chatbot

def response_generator(prompt, state):
    try:
        if len(state.messages) > 0:
            full_context = state.messages + [{'role': 'user', 'content': prompt}]
            response: ChatResponse = chat(model="mistral",messages= full_context)
        else:
            response: ChatResponse = chat(model="mistral" , messages=[
            {
                'role': 'user',
                'content': f"{prompt}",
            },
            ])
        return response.message.content
    except Exception as e:
        logging.error(f"Error during streaming: {str(e)}")
        raise e


def display_response(response):
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

with st.expander("Ollama Chatbot"):
    st.subheader('Ollama Chatbot')
    #display model
    #st.write(ModelDetails("llama-13b"))
    st.write("Ask questions about the rental agreement and get answers based on the extracted terms.")

    # initialize chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

# Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Hello Ollama, what's up?"):
        # Add user message to chat history
        st.chat_message("user").write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Generate assistant response
        with st.spinner("Thinking..."):
            response = response_generator(prompt, st.session_state)

        # display assistant response
        st.chat_message("assistant").write(response)
            
        # add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # clear chat history
    if st.button("Clear Chat"):
        del st.session_state["messages"]
        st.toast('Chat cleared successfully!')
        st.rerun()