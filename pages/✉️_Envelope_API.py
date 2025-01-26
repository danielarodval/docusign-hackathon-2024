import streamlit as st
import time
import base64
from docusign_esign import Document, ApiClient, EnvelopeDefinition, EnvelopesApi, Signer, Tabs, SignHere, Recipients
import requests
from streamlit_oauth import OAuth2Component

# load environment variables
from dotenv import load_dotenv
load_dotenv()

# prints time on reruns
print("envelope_api - ",time.time())

#%% streamlit app
st.title('Docusign Envelope API')
st.write("This is a simple web app that allows you to upload a rental agreement and send it to a signer using the Docusign Envelope API.")
st.divider()

with st.sidebar:
    #st.write("Access Token: ", st.session_state.get("token"))
    #st.write("User: ", st.session_state.get("user"))
    try:
        st.write("Access Token: ", 'access_token' in st.session_state.get("token"))
    except:
        st.write("Access Token: ", False)

    try:
        st.write("User: ", 'name' in st.session_state.get("user"))
    except:
        st.write("User: ", False)
    try:
        st.write("Name: ", st.session_state.get("user").get("name"))
    except:
        st.write("Account ID: ", False)
    # display top level items in session state
    st.write("Session State: ", st.session_state)

#%% streamlit file uploader
# UPDATE: find a way to delete the uploaded file when delete uploaded document selected
# UPDATE: add preview file option
st.subheader('Streamlit File Uploader')
# file uploader
uploaded_file = st.file_uploader("Upload a rental agreement", type=["pdf"])
if uploaded_file is not None:
    # display success message
    st.toast('Uploading file...')
    time.sleep(.5)
    st.toast('File uploaded successfully!')

    # read file and encode to base64
    file_content = uploaded_file.read()
    base64_file_content = base64.b64encode(file_content).decode("utf-8")

    # add document to session_state
    st.session_state.document = {"name": uploaded_file.name, "content": base64_file_content}
    uploaded_file = None
    del file_content, base64_file_content

#%% docusign send agreement
# UPDATE: change to st.form for better layout
st.subheader('Docusign File Upload API')
results = None
if 'document' in st.session_state:

    #display currently uploaded document
    st.write("Uploaded Document: ", st.session_state.document.get("name"))
    if st.button("Delete Uploaded Document"):
        del st.session_state["document"]
        st.toast('Document deleted successfully!')
        st.rerun()

    st.divider()

    # get signer email and name
    st_email_input = st.text_input('Signer Email')
    st_name_input = st.text_input('Signer Name')

    # create document object
    document = Document(
        document_base64=st.session_state.document.get("content"),
        name=str(st.session_state.document.get("name")),
        file_extension="pdf",
        document_id="1"
    )
    # create signer object
    signer = Signer(
        email = st_email_input,
        name = st_name_input,
        recipient_id="1",
        routing_order="1"
    )

    # create signer object
    signer = Signer(
        email = st_email_input,
        name = st_name_input,
        recipient_id="1",
        routing_order="1"
    )

    # create the sign_here tab
    sign_here = SignHere(
        anchor_string="/sn1/",
        anchor_units="pixels",
        anchor_y_offset="10",
        anchor_x_offset="20"
    )

    # add the tab to the signer
    signer.tabs = Tabs(sign_here_tabs=[sign_here])

    # create receipients object
    receipients = Recipients(signers=[signer])

    envelope_definition = EnvelopeDefinition(
        email_subject="Please sign this document",
        documents=[document],
        recipients=receipients,
        status="sent"
    )

    if st.button("Send Agreement"):
        envelopes_api = EnvelopesApi(api_client)
        results = envelopes_api.create_envelope(account_id, envelope_definition=envelope_definition)
        st.success(f"Envelope created! Envelope ID: {results.envelope_id}")
else:
    st.warning("Please upload a document first.")