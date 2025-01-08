import streamlit as st
import time

st.title('Rental Agreement Agent')

st.write("This is a simple web app that assists you in understanding the terms of a rental agreement. It uses a pre-trained model to extract the key terms from the agreement and provides a summary of the agreement. You can also ask questions about the agreement and get answers based on the extracted terms.")

st.divider()

st.subheader('Streamlit File Uploader')

uploaded_file = st.file_uploader("Upload a rental agreement", type=["pdf"])

if uploaded_file is not None:
    st.toast('Uploading file...')
    time.sleep(.5)
    st.toast('File uploaded successfully!')

    st.write("Filename:", uploaded_file.name)
    st.write("File type:", uploaded_file.type)

st.divider()

st.subheader('Docusign Navigator API')