# ds_config.py
#
# DocuSign configuration settings
from dotenv import load_dotenv
import os

dotenv_path = os.path.join('env', '.env')
load_dotenv(dotenv_path)
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
signer_email = os.getenv("SIGNER_EMAIL")
signer_name = os.getenv("SIGNER_NAME")
DS_CONFIG = {
    "ds_client_id": f'{client_id}',  # The app's DocuSign integration key
    "ds_client_secret": f'{client_secret}',  # The app's DocuSign integration key's secret
    "organization_id": "{ORGANIZATION_ID}", # A GUID value that identifies the organization
    "signer_email": f"{signer_email}",
    "signer_name": f"{signer_name}",
    "app_url": "http://localhost:3000",  # The URL of the application. Eg http://localhost:5000
    # NOTE: You must add a Redirect URI of appUrl/ds/callback to your Integration Key.
    #       Example: http://localhost:5000/ds/callback
    "authorization_server": "https://account-d.docusign.com",
    "click_api_client_host": "https://demo.docusign.net/clickapi",
    "rooms_api_client_host": "https://demo.rooms.docusign.com/restapi",
    "monitor_api_client_host": "https://lens-d.docusign.net",
    "admin_api_client_host": "https://api-d.docusign.net/management",
    "maestro_api_client_host": "https://apps-d.docusign.com/api/maestro",
    "webforms_api_client_host": "https://apps-d.docusign.com/api/webforms/v1.1",
    "allow_silent_authentication": True,  # a user can be silently authenticated if they have an
    # active login session on another tab of the same browser
    "target_account_id": None,  # Set if you want a specific DocuSign AccountId,
    # If None, the user's default account will be used.
    "demo_doc_path": "demo_documents",
    "doc_salary_docx": "World_Wide_Corp_salary.docx",
    "doc_docx": "World_Wide_Corp_Battle_Plan_Trafalgar.docx",
    "doc_pdf": "World_Wide_Corp_lorem.pdf",
    "doc_terms_pdf": "Term_Of_Service.pdf",
    "doc_txt": "Welcome.txt",
    "doc_offer_letter": "Offer_Letter_Demo.docx",
    "doc_dynamic_table": "Offer_Letter_Dynamic_Table.docx",
    # Payment gateway information is optional
    "gateway_account_id": "{DS_PAYMENT_GATEWAY_ID}",
    "gateway_name": "stripe",
    "gateway_display_name": "Stripe",
    "github_example_url": "https://github.com/docusign/code-examples-python/tree/master/app/eSignature/examples/",
    "monitor_github_url": "https://github.com/docusign/code-examples-python/tree/master/app/monitor/examples/",
    "admin_github_url": "https://github.com/docusign/code-examples-python/tree/master/app/admin/examples/",
    "click_github_url": "https://github.com/docusign/code-examples-python/tree/master/app/click/examples/",
    "connect_github_url": "https://github.com/docusign/code-examples-python/tree/master/app/connect/examples/",
    "example_manifest_url": "https://raw.githubusercontent.com/docusign/code-examples-csharp/master/manifest/CodeExamplesManifest.json",
    "documentation": "",  # Use an empty string to indicate no documentation path.
    "quickstart": "true"
}