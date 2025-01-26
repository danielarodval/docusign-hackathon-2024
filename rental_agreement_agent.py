import streamlit as st
import time
import base64
from docusign_esign import Document, ApiClient, EnvelopeDefinition, EnvelopesApi, Signer, Tabs, SignHere, Recipients
import requests
from streamlit_oauth import OAuth2Component
from ds_config import DS_CONFIG as ds_config

# load environment variables
from dotenv import load_dotenv
load_dotenv()

print(time.time())

#%% create functions
# Determine user, account_id, base_url by calling OAuth::getUserInfo
# See https://developers.docusign.com/esign-rest-api/guides/authentication/user-info-endpoints
def get_user(access_token):
    url = "https://account-d.docusign.com/oauth/userinfo"
    auth = {"Authorization": "Bearer " + access_token}
    response = requests.get(url, headers=auth).json()
    return response

#%% streamlit app
st.title('Rental Agreement Agent')
st.write("This is a simple web app that assists you in understanding the terms of a rental agreement. It uses a pre-trained model to extract the key terms from the agreement and provides a summary of the agreement. You can also ask questions about the agreement and get answers based on the extracted terms.")
st.divider()

#%% configuration
AUTHORIZATION_URL = f"{ds_config['authorization_server']}/oauth/auth"
TOKEN_URL = f"{ds_config['authorization_server']}/oauth/token"
REDIRECT_URI = ds_config['app_url_lcl']
CLIENT_ID = ds_config['ds_client_id']
CLIENT_SECRET = ds_config['ds_client_secret']
REDIRECT_URI = ds_config['app_url_lcl']
#BTN_URL = f"https://account-d.docusign.com/oauth/auth?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=signature&state=d8LjbTmbZVlirw77oqw3OReWk5v9jC&code_challenge=RMK30ueseHEu6V7FImJA0KFJI1JCVzjc-Pgbo_adPUA&code_challenge_method=S256&approval_prompt=auto"
SCOPES = "signature adm_store_unified_repo_read"

oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZATION_URL, TOKEN_URL)

with st.sidebar: # check access token and user
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

if 'access_token' not in st.session_state:
    result = oauth2.authorize_button("Continue with Docusign", REDIRECT_URI, SCOPES)
    with st.spinner("Waiting for authorization..."):
        if result:
            st.session_state.token = result.get("token")
            user = get_user(st.session_state.get("token").get("access_token"))
            st.session_state.user = user
            st.rerun()

if st.session_state.get("token") and st.session_state.get("user"):
    access_token = st.session_state.get("token").get("access_token")
    account_id = st.session_state.get("user").get("accounts")[0].get("account_id")
    base_path = "https://demo.docusign.net/restapi"

    api_client = ApiClient()
    api_client.host = base_path
    api_client.set_default_header("Authorization", f"Bearer {access_token}")

else:
    st.write("Please log in to continue.")
    access_token = None

#%% streamlit file uploader
with st.expander("Upload Rental Agreement"):
    st.subheader('Streamlit File Uploader')
    uploaded_file = st.file_uploader("Upload a rental agreement", type=["pdf"])
    if uploaded_file is not None:
        st.toast('Uploading file...')
        time.sleep(.5)
        st.toast('File uploaded successfully!')

        # display file details
        st.write("Filename:", uploaded_file.name)
        st.write("File type:", uploaded_file.type)

        # read file and encode to base64
        file_content = uploaded_file.read()
        base64_file_content = base64.b64encode(file_content).decode("utf-8")
    st.divider()

#%% docusign send agreement

with st.expander("Docusign File Upload API"):
    st.subheader('Docusign File Upload API')
    results = None
    if uploaded_file is not None:
        st_email_input = st.text_input('Signer Email')
        st_name_input = st.text_input('Signer Name')

        # create document object
        document = Document(
            document_base64=base64_file_content,
            name=uploaded_file.name,
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
        exit

#%% docusign navigator api
headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
with st.expander("Docusign Navigator API: Get List of Agreements"):
    st.subheader('Docusign Navigator API')
    if st.button("Get List of Agreements"):
        response_list = requests.get(f"https://api-d.docusign.com/v1/accounts/{account_id}/agreements", headers=headers)
        if response_list.status_code > 399:
            st.error(f"Error: {response_list.status_code}")
            st.write(response_list.text)
        else:
            try:
                response_list_json = response_list.json()
                st.write(response_list_json)
                st.success("Agreements fetched successfully!")
            except requests.exceptions.JSONDecodeError:
                st.error("Error: Response is not in JSON format")
                st.write(response_list.text)

with st.expander("Docusign Navigator API: Get Agreement"):
    st.subheader('Docusign Navigator API')
    if uploaded_file is not None:
        if results is None:

            agreement_id = "2d2812ba-974c-4068-9e99-9f42ebd2bf9a"
            
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
        exit