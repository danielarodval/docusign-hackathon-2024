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

# load environment variables
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(level=logging.INFO)

# prints time on reruns
print("home - ",time.time())

#%% create functions
# Determine user, account_id, base_url by calling OAuth::getUserInfo
# See https://developers.docusign.com/esign-rest-api/guides/authentication/user-info-endpoints
def get_user(access_token):
    url = "https://account-d.docusign.com/oauth/userinfo"
    auth = {"Authorization": "Bearer " + access_token}
    response = requests.get(url, headers=auth).json()
    return response

#%% streamlit app
st.set_page_config(
    page_title="Rental Agreement Agent",
    page_icon="app\ds_brand\Docusign_Logo.png",
    initial_sidebar_state="collapsed",
    menu_items={"About": "https://github.com/danielarodval/docusign-hackathon-2024"}
    #layout="wide"
)

theme = st_theme()

if theme['base'] == 'light':
    st.logo("app\ds_brand\Docusign Horizontal Color Black\Docusign Horizontal_Black.svg")
else:
    st.logo("app\ds_brand\Docusign Horizontal Color White\Docusign Horizontal_White.svg")

st.title('Rental Agreement Agent')
st.write("This is a simple web app that assists you in understanding the terms of a rental agreement. It uses a pre-trained model to extract the key terms from the agreement and provides a summary of the agreement. You can also ask questions about the agreement and get answers based on the extracted terms.")
st.divider()

#%% docusign authentication
AUTHORIZATION_URL = f"{ds_config['authorization_server']}/oauth/auth"
TOKEN_URL = f"{ds_config['authorization_server']}/oauth/token"
REDIRECT_URI = ds_config["app_url_lcl"]
CLIENT_ID = ds_config['ds_client_id']
CLIENT_SECRET = ds_config['ds_client_secret']
SCOPES = "signature adm_store_unified_repo_read"

oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZATION_URL, TOKEN_URL)

# check access token and user
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

encoded_icon = base64.b64encode(open("app\ds_brand\Docusign_Logo.png", "rb").read()).decode()
st_btn_ds_icon = f"data:image/png+xml;base64,{encoded_icon}"

# check if token is in session state
if 'token' not in st.session_state:

    result = oauth2.authorize_button("Continue with Docusign", REDIRECT_URI, SCOPES, icon=st_btn_ds_icon)
    with st.spinner("Waiting for authorization..."):
        # check if result is not None
        if result:
            # store token in session state
            st.session_state.token = result.get("token")
            # get user info
            user = get_user(st.session_state.get("token").get("access_token"))
            # store user in session state
            st.session_state.user = user
            st.rerun()
else:
    st.write("You are logged in as: ", st.session_state.get("user").get("name"))

# get access token and account id
if st.session_state.get("token") and st.session_state.get("user"):
    access_token = st.session_state.get("token").get("access_token")
    account_id = st.session_state.get("user").get("accounts")[0].get("account_id")
    base_path = "https://demo.docusign.net/restapi"

    api_client = ApiClient()
    api_client.host = base_path
    api_client.set_default_header("Authorization", f"Bearer {access_token}")
else:
    st.warning("Please log in to continue.")
    access_token = None

#%% streamlit file uploader
# UPDATE: find a way to delete the uploaded file when delete uploaded document selected
# UPDATE: add preview file option
with st.expander("Upload Rental Agreement"):
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
with st.expander("Docusign File Upload API"):
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

#%% docusign navigator api

# set headers
headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

with st.expander("Docusign Navigator API: Get List of Agreements"):
    st.subheader('Docusign Navigator API')

    if 'navapi_list' not in st.session_state:
        if st.button("Get List of Agreements"):
            # get list of agreements
            response_list = requests.get(f"https://api-d.docusign.com/v1/accounts/{account_id}/agreements", headers=headers)
            # check if response is successful
            if response_list.status_code > 399:
                # display error message
                st.error(f"Error: {response_list.status_code}")
                st.write(response_list.text)
            else:
                # display response
                try:
                    # convert response to json
                    response_list_json = response_list.json()
                    
                    # Store response list in session state
                    st.session_state.navapi_list = response_list_json
                    #st.write(response_list_json)
                    st.success("Agreements fetched successfully!")
                    st.rerun()
                except requests.exceptions.JSONDecodeError:
                    # display error message
                    st.error("Error: Response is not in JSON format")
                    st.write(response_list.text)
    else:
        # display agreements json items by names
        st.markdown("<b>Agreements</b>", unsafe_allow_html=True)
        for item in st.session_state.navapi_list.get("data"):
            st.write(item.get("file_name"))
        # button to clear agreements
        if st.button("Clear Agreements"):
            del st.session_state["navapi_list"]
            st.toast('Agreements cleared successfully!')
            st.rerun()

with st.expander("Docusign Navigator API: Get Agreement"):
    st.subheader('Docusign Navigator API')

    # if navapi_list is not in session state
    if 'navapi_list' not in st.session_state:
        st.warning("Please get list of agreements first.")
    else:
        # agreement id selection
        agreements = [{"file_name": item.get("file_name"), "id": item.get("id")} for item in st.session_state.navapi_list.get("data")]
        selected_agreement = st.selectbox("Select Agreement", agreements, format_func=lambda x: x["file_name"])

        if selected_agreement is None:
            st.warning("Please select an agreement.")
        else:
            agreement_id = selected_agreement["id"]

            # get agreement
            if st.button("Get Agreement"):
                response = requests.get(f"https://api-d.docusign.com/v1/accounts/{account_id}/agreements/{agreement_id}", headers=headers)
                if response.status_code > 399:
                    st.error(f"Error: {response.status_code}")
                    st.write(response.text)
                else:
                    try:
                        response_json = response.json()
                        st.write(response_json)
                        st.success("Agreement fetched successfully!")
                    except requests.exceptions.JSONDecodeError:
                        st.error("Error: Response is not in JSON format")
                        st.write(response.text)

