import requests
import re
from azure.identity import ClientSecretCredential
import urllib.parse
import os
import psycopg2
from dotenv import load_dotenv, find_dotenv
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_openai import AzureOpenAIEmbeddings
load_dotenv(find_dotenv())

credentials = ClientSecretCredential(
    client_id="86dfb3ef-b0fc-4bbe-90b6-f1a11c619f8e",
    client_secret="34d8Q~B72MZ5PUCQKI5ZCR2L3cM6PB4eJ1teFbw.",
    tenant_id="1b314d3f-4df5-485a-a59b-72335826d944"
)

scopes = ["https://graph.microsoft.com/.default"]


name_to_link = {}

# url structure -> https://fifthstreet791.sharepoint.com/sites/SAPSuccessFactorsAgent
# site_name = "SAPSuccessFactorsAgent"

def get_sharepoint_site_details(credential, scopes, site_name):
    access_token = credential.get_token(*scopes)
    endpoint = f'https://graph.microsoft.com/v1.0/sites/fifthstreet791.sharepoint.com:/sites/{site_name}'
    headers = {
        'Authorization': f'Bearer {access_token.token}'
    }
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        site_details = response.json()
        print("Site ID: ", site_details['id'])
        return site_details['id']
    else:
        print(f"Failed to retrieve site details: {response.status_code}")

def get_drive_id(credential, scopes, site_id):
    access_token = credential.get_token(*scopes)
    endpoint = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives'
    headers = {
        'Authorization': f'Bearer {access_token.token}'
    }
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        drives = response.json()
        for drive in drives['value']:
            if drive['name'] == 'Documents':
                print(f"Drive ID: {drive['id']}")
                return drive['id']
    else:
        print(f"Failed to retrieve drives: {response.status_code}")

def get_folder_ids(credential, scopes, site_id, drive_id):
    access_token = credential.get_token(*scopes)
    # Endpoint to get items in the drive root (including folders)
    endpoint = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root/children'
    headers = {
        'Authorization': f'Bearer {access_token.token}'
    }  

    FOLDER_ID_GENERAL = ""
    FOLDER_ID_DATA = ""
    workbook_id = ""
    
    # # First, get all items in the root directory to find the 'General' folder
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        items = response.json()
        folder_id = None
        for item in items['value']:
            if item['name'] == 'General':
                folder_id = item['id']
                print(f"General Folder ID: {folder_id}")
                FOLDER_ID_GENERAL = folder_id
                break
    folder_endpoint = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/{FOLDER_ID_GENERAL}/children'
    folder_response = requests.get(folder_endpoint, headers=headers)
    if folder_response.status_code == 200:
        folder_items = folder_response.json()
        for item in folder_items['value']:
            if item['name'] == "Data":
                print(f"Data Folder ID: {item['id']}")
                FOLDER_ID_DATA = item['id']
            if item['name'] == 'Response Automator.xlsx':
                print(f"Workbook ID: {item['id']}")
                workbook_id = item['id']
        
        return FOLDER_ID_DATA, workbook_id
    else:
        print(f"Failed to retrieve items in 'General' folder: {folder_response.status_code}")


def get_workbook_details(credential, scopes, site_id, drive_id, workbook_id):
    access_token = credential.get_token(*scopes)
    endpoint = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/{workbook_id}/workbook/worksheets'
    headers = {
        'Authorization': f'Bearer {access_token.token}'
    }
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        worksheets = response.json()
        for worksheet in worksheets['value']:
            print(f"Worksheet ID: {worksheet['id']}")
            return worksheet['id']
    else:
        print(f"Failed to retrieve worksheets: {response.status_code}")

def download_data(credential, scopes, site_id, drive_id, FOLDER_ID, site_name):
    access_token = credential.get_token(*scopes)
    endpoint = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/{FOLDER_ID}/children'
    headers = {
        'Authorization': f'Bearer {access_token.token}'
    }
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        data = response.json()
        for item in data['value']:
            download_url = item['@microsoft.graph.downloadUrl']
            file_name = None
            url = item['webUrl']
            if 'file=' in url:
                file_match = re.search(r'file=([^&]+)', url)
                if file_match:
                    file_name =  urllib.parse.unquote(file_match.group(1))
            
            # Fallback for URLs that directly end with the filename
            if file_name is None:
                path_match = re.search(r'/([^/?]+)(?:\?|$)', url)
                if path_match:
                    file_name =  urllib.parse.unquote(path_match.group(1))

            name_to_link[file_name] = url

            
            if not os.path.exists(f"Data/{site_name}"):
                os.makedirs(f"Data/{site_name}")
            # check if file already exists
            if os.path.exists(f"Data/{site_name}/{file_name}"):
                print(f"File {file_name} already exists")
                continue
            # download
            response = requests.get(download_url, stream=True)
            if response.status_code == 200:
                file_name = f"Data/{site_name}/{file_name}"
                with open(file_name, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192): 
                        f.write(chunk)
                print(f"Downloaded {file_name}")
            else:
                print(f"Failed to download file: {response.status_code}")
    else:
        print(f"Failed to download data: {response.status_code}")



#only works for pdf and docx files

def create_db_from_documents(documents: list, namespace):

    embeddings = AzureOpenAIEmbeddings(
        model= "text-embedding-3-large",
        azure_endpoint = os.environ["AZURE_ENDPOINT"], 
        api_key=os.environ["API_KEY"],  
        api_version=os.environ["API_VERSION"],
        azure_deployment=os.environ["AZURE_DEPLOYMENT"],
    )

    all_docs = []
    for document in documents:

        name = document["Name"]
        name = name.replace("%20", " ")

        if document["Name"].endswith(".docx"):
            loader = Docx2txtLoader(document['Path'])
        elif document["Name"].endswith(".pdf"):
            loader = PyPDFLoader(document['Path'])
        content = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
        split_documents = text_splitter.split_documents(content)
        
        for i, doc in enumerate(split_documents):
            if name.endswith(".docx"):
                all_docs.append(Document(
                page_content=doc.page_content,
                metadata={'name':name, "doc_link": document['Link'], 'page_number': i//4 + 1}
            ))
            else:
                all_docs.append(Document(
                    page_content=doc.page_content,
                    metadata={'name':name, 'page_number': doc.metadata['page'], "doc_link": document['Link']}
                ))
        print(f"Loaded {len(split_documents)} documents from {document}")

    vectorstore_from_docs = PineconeVectorStore.from_documents(
        all_docs,
        index_name="data",
        embedding=embeddings,
        namespace = namespace
    )
    return "Vector store created successfully."

def main(credentials, scopes, site_name):
    site_id = get_sharepoint_site_details(credentials, scopes, site_name)
    drive_id = get_drive_id(credentials, scopes, site_id)
    folder_id_data, workbook_id = get_folder_ids(credentials, scopes, site_id, drive_id)
    worksheet_id = get_workbook_details(credentials, scopes, site_id, drive_id, workbook_id)
    download_data(credentials, scopes, site_id, drive_id, folder_id_data, site_name)

    conn = psycopg2.connect(
        user= f"{os.environ.get('POSTGRES_USER')}", 
        password=f"{os.environ.get('POSTGRES_PASSWORD')}", 
        host=f"{os.environ.get('POSTGRES_HOST')}", 
        port=f"{os.environ.get('POSTGRES_PORT')}", 
        database=f"{os.environ.get('POSTGRES_DATABASE')}"
    )
    cur = conn.cursor()
    
    # check if site already exists
    # not optimised for new data currently 
    cur.execute(f"SELECT * FROM links WHERE comp_name = '{site_name}'")
    if cur.fetchone():
        print("Site already exists")
        return
    
    for file_name, url in name_to_link.items():
        cur.execute(f"INSERT INTO links (comp_name, doc_name, link) VALUES ('{site_name}', '{file_name}', '{url}')")

    cur.execute(f"INSERT INTO site (name, site_id, drive_id, workbook_id, worksheet_id) VALUES ('{site_name}', '{site_id}', '{drive_id}', '{workbook_id}', '{worksheet_id}')")
    
    conn.commit()
    cur.close()
    conn.close()
    print("Data successfully downloaded and values stored in database")

    documents = []

    files = os.listdir(f"Data/{site_name}")
    for file in files:
        if file.endswith(".pdf") or file.endswith(".docx"):
            documents.append({"Name": file, "Link": name_to_link[file], "Path": f"Data/Tendered/{file}"})

    response = create_db_from_documents(documents, namespace= site_name)
    print(response)

main(credentials, scopes, site_name= "Tendered")
