from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import io, os
from googleapiclient.http import MediaIoBaseDownload
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
from dotenv import load_dotenv
load_dotenv()

scopes = ['https://www.googleapis.com/auth/drive']
credentials = Credentials.from_service_account_file('credentials.json', scopes=scopes)
service = build('drive', 'v3', credentials=credentials)
name_to_link = {}

def list_files_in_folder(folder_id):
    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    files = results.get('files', [])
    return files

def download_file(file_id, file_name, folder_name):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    local_folder_path = f"Data/{folder_name}"
    if not os.path.exists(local_folder_path):
        os.makedirs(local_folder_path)

    if os.path.exists(f"{local_folder_path}/{file_name}"):
        print(f"{file_name} already exists in {local_folder_path}.")
        return
    
    done = False
    while not done:
        status, done = downloader.next_chunk()

    with open(f"{local_folder_path}/{file_name}", 'wb') as f:
        fh.seek(0)
        f.write(fh.read())
        print(f'{file_name} downloaded successfully to {local_folder_path}.')

def find_and_download_data_folders(parent_folder_id):
    sub_folders = list_files_in_folder(parent_folder_id)
    return sub_folders


def download_files(site_name, sub_folders):
    for folder in sub_folders:
        if folder['mimeType'] == 'application/vnd.google-apps.folder':
            data_folder = list_files_in_folder(folder['id'])
            for file in data_folder:
                link = f"https://drive.google.com/drive/folders/{folder['id']}"
                name_to_link[file['name']] = link
                download_file(file['id'], file['name'], site_name)

    return "Data downloaded successfully."

def create_db_from_documents(documents: list, namespace):

    embeddings = AzureOpenAIEmbeddings(
        model= "text-embedding-3-large",
        azure_endpoint = "https://salesiqdemo.openai.azure.com/", 
        api_key=os.environ["API_KEY"],  
        api_version="2024-02-15-preview",
        azure_deployment="langchain-test",
    )

    all_docs = []
    for document in documents:

        name = document["Name"]
        name = name.replace("%20", " ")

        if document["Name"].endswith(".docx"):
            loader = Docx2txtLoader(document['Path'])
        elif document["Name"].endswith(".pdf"):
            loader = PyPDFLoader(document['Path'])
        elif document["Name"].endswith(".xlsx"):
            loader = AzureAIDocumentIntelligenceLoader(
                api_endpoint="https://maservices-di.cognitiveservices.azure.com/",
                api_key=f"{os.environ['DOC_INTELLIGENCE_API_KEY']}",
                file_path=document['Path'],
                api_model="prebuilt-layout"
            )
        content = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
        split_documents = text_splitter.split_documents(content)
        
        for i, doc in enumerate(split_documents):
            if name.endswith(".docx"):
                all_docs.append(Document(
                page_content=doc.page_content,
                metadata={'name':name, "doc_link": document['Link'], 'page_number': i//4 + 1}
            ))
            elif name.endswith(".xlsx"):
                all_docs.append(Document(
                page_content=doc.page_content,
                metadata={'name':name, "doc_link": document['Link'], 'page_number': "N/A"}
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



def main(site_name):
    sub_folders = find_and_download_data_folders(parent_folder_id)
    download = download_files(site_name, sub_folders)

    documents = []
    files = os.listdir(f"Data/{site_name}")
    for file in files:
        if file.endswith(".pdf") or file.endswith(".docx") or file.endswith(".xlsx"):
            documents.append({"Name": file, "Link": name_to_link[file], "Path": f"Data/{site_name}/{file}"})

    create_db_from_documents(documents, site_name)

parent_folder_id = '128bzYva3GFxo1sDyCQvIHCGPNlx-SSFG'
main(site_name = "DiscoveryConsulting")