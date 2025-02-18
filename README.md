<p><a target="_blank" href="https://app.eraser.io/workspace/eGLkzlZ9uwPCFrkGagdz" id="edit-in-eraser-github-link"><img alt="Edit in Eraser" src="https://firebasestorage.googleapis.com/v0/b/second-petal-295822.appspot.com/o/images%2Fgithub%2FOpen%20in%20Eraser.svg?alt=media&amp;token=968381c8-a7e7-472a-8ed6-4a6626da5501"></a></p>

# [﻿Rental Agreement Chat Agent](https://rpidev.floridaecrm.com/)﻿
## Overview
The Rental Agreement Chat Agent is an AI-powered tool designed to assist users in understanding rental agreements and calculating end costs. This project integrates with DocuSign’s APIs to provide seamless access to agreement data while offering an intuitive interface for user interaction. Developed as part of the DocuSign Hackathon, the solution leverages AI and DocuSign's ecosystem to enhance user experience and agreement management.

﻿[﻿DevPost Submission](https://devpost.com/software/rental-agreement-agent) 

---

## Objective
To build an intelligent and user-friendly chat agent that:

- Leverages DocuSign's environment through SDKs provided.
- Extract details from rental agreements and files uploaded by the end user.
- Explain and answer inquiries made by the end user with context from the files and conversation.
---

## Technical Approach
1. **User Interface**:
    - **Custom UI**:
        - Built using modern framework Streamlit
        - Allows for interactive chat functionality alongside agreement management.
        - Built around showcasing functionality to allow for replication in a variety of environments.
    - **DocuSign Integration**:
        - Download DocuSign's Python SDK to facilitate code structure and their integration policy to our app.
        - Utilize Navigator API for extracting key points of the user's rental agreement.
2. **Backend**:
    - Powered by Python to connect the custom-built AI chat agent with DocuSign APIs.
    - Integration with DocuSign’s **Navigator API** for extracting agreement data.
3. **Hosting:**
    - **Local Hosting:**
        - A Raspberry Pi to host the web application locally.
        - Ollama to run a local large language model (Mistral) for natural language processing.
        - Cloudflare and Cloudflare Tunnel for secure hosting and access.
    - **Cloud Hosting**:
        - Use Streamlit free tier option to host our app
        - Use ChatGPT gpt-4o-mini model to generate our chats. 
---

## **Key Features**
- **AI-Powered Assistance**:
    - Provides insights into agreement clauses, timelines, and costs.
- **DocuSign API Integration**:
    - Leverages Navigator API for agreement data extraction.
    - Embeds workflows using Extension Apps for streamlined user experiences.
- **Scalable Deployment**:
    - Local development infrastructure for rapid testing.
    - Cloud-hosted solutions or integration within DocuSign's platform for production.
---

## Implementation
### 1) OAuth2:
> Using a Streamlit third-party component `streamlit_oauth` 

```
﻿import streamlit as st
from streamlit_oauth import OAuth2Component
import base64

# docusign authentication
AUTHORIZATION_URL = f"{st.secrets['authorization_server']}/oauth/auth"
TOKEN_URL = f"{st.secrets['authorization_server']}/oauth/token"
REDIRECT_URI = st.secrets["app_url_lcl"]
CLIENT_ID = st.secrets['ds_client_id']
CLIENT_SECRET = st.secrets['ds_client_secret']
SCOPES = "signature adm_store_unified_repo_read"

oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZATION_URL, TOKEN_URL)
result = oauth2.authorize_button("Continue with Docusign", REDIRECT_URI, SCOPES, icon=st_btn_ds_icon)

# store token in session state
st.session_state.token = result.get("token")
# get user info
user = get_user(st.session_state.get("token").get("access_token"))
# store user in session state
st.session_state.user = user
```
### 2) Streamlit File Uploader:
> File uploader

```
import streamlit as st

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
```
### 3) Envelopes API:
> Using DocuSign's Envelope API 

```python
import streamlit as st
from docusign_esign import Document, ApiClient, EnvelopeDefinition, EnvelopesApi, Signer, Tabs, SignHere, Recipients
# get access token and account id
if st.session_state.get("token") and st.session_state.get("user"):
    access_token = st.session_state.get("token").get("access_token")
    account_id = st.session_state.get("user").get("accounts")[0].get("account_id")
    base_path = "https://demo.docusign.net/restapi"

    api_client = ApiClient()
    api_client.host = base_path
    api_client.set_default_header("Authorization", f"Bearer {access_token}")
    
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
```
### 4) Navigator API:
> Develop a custom frontend for user interactions.

```python
import streamlit as st
import requests
# agreement id selection
agreements = [{"file_name": item.get("file_name"), "id": item.get("id")} for item in st.session_state.navapi_list.get("data")]
selected_agreement = st.selectbox("Select Agreement", agreements, format_func=lambda x: x["file_name"])

if selected_agreement is None:
    st.warning("Please select an agreement.")
else:
    agreement_id = selected_agreement["id"]
    #st.write("test")

    col_get_1, col_get_2 = st.columns(2)

    with col_get_1:
        # get agreement
        if st.button("Get Agreement"):
            response = requests.get(f"https://api-d.docusign.com/v1/accounts/{account_id}/agreements/{agreement_id}", headers=headers)
            if response.status_code > 399:
                st.error(f"Error: {response.status_code}")
                st.write(response.text)
            else:
                try:
                    if "selected_agreement" not in st.session_state:
                        st.session_state.selected_agreement = ""
                    response_json = response.json()
                    
                    st.session_state.selected_agreement = response_json
                    st.rerun()
                except requests.exceptions.JSONDecodeError:
                    st.error("Error: Response is not in JSON format")
                    st.write(response.text)

    with col_get_2:
        # display agreement details
        if st.button("Clear Agreement") and "selected_agreement" in st.session_state:
            del st.session_state["selected_agreement"]
            st.toast('Agreement cleared successfully!')
            st.rerun()
    
    # display agreement status
    if "selected_agreement" in st.session_state:
        st.success("Agreement fetched successfully!")
```
### 5) LLM API:
> Use DocuSign’s sandbox to simulate agreement interactions and validate features.

#### Local Implementation
```python
from ollama import chat
from ollama import ChatResponse
import httpx

if hasattr(state, 'selected_agreement') and isinstance(state.selected_agreement, dict):
    url_ext = "/api/chat"
    # Convert agreement to JSON string for context
    agreement_context = json.dumps(state.selected_agreement, separators=(',', ':'))
    # Force-escape all existing double quotes
    #escaped_agreement_context = agreement_context.replace('"', r'\"')
    full_context = [
        {
            'role': 'system',
            'content': f"Agreement Context: {agreement_context}"
        },
        *state.messages,
        {
            'role': 'user',
            'content': prompt
        }
    ]
    DATA = {
        "model": "mistral",
        "messages": full_context
    }
    #print(json.dumps(DATA, indent=2))
    response = requests.post(URL+url_ext, json=DATA, headers={"Content-Type": "application/json"})
    # split the response by newlines and filter our empty lines
    response_lines = [line for line in response.text.strip().split("\n") if line]
    # parse each line as json
    response_dicts = [json.loads(line) for line in response_lines]
    # format as string
    response_text = ''.join(
        d['message']['content']
        for d in response_dicts
        if 'message' in d and 'content' in d['message']
```
#### Cloud Implementation
```python
﻿from openai import OpenAI
import json

# Check if selected_agreement exists and is a dictionary
client = OpenAI(
        api_key= st.secrets["openai_key"]
    )

if hasattr(state, 'selected_agreement') and isinstance(state.selected_agreement, dict):
    
    # Convert agreement to JSON string for context
    agreement_context = json.dumps(state.selected_agreement, separators=(',', ':'))
    # Force-escape all existing double quotes
    

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
            {"role": "system", "content": "You are an AI assistant that helps summarize and analyze agreements."},
            {"role": "user", "content": f"Here is the agreement context: {agreement_context}"},
            {"role": "user", "content": prompt}
        ]
    )

    # extract response content
    response_text = completion.choices[0].message.content
```
---

## **Potential Impact**
- Simplifies rental agreement navigation for users.
- Enhances DocuSign’s agreement ecosystem with AI-powered insights.
- Provides a scalable framework for extending AI solutions into other agreement types.
- With local hosting, allows users the freedom to integrate intricate LLMs




<!--- Eraser file: https://app.eraser.io/workspace/eGLkzlZ9uwPCFrkGagdz --->