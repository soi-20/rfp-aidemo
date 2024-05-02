import os
from flask import Flask, request, jsonify
from models import db
from azure.identity import ClientSecretCredential
import gspread
from google.oauth2.service_account import Credentials
from Excel.getData import getData
from Excel.populateData import populateData
from Model.main import create_chain, get_response_from_query, filterResponse
from Model.prompts import TENDERED_PROMPT, MAServicesPrompt, JLLServicesPrompt, DiscoveryConsultingPrompt
from dotenv import load_dotenv
import psycopg2
load_dotenv()

credentials = ClientSecretCredential(
    client_id="86dfb3ef-b0fc-4bbe-90b6-f1a11c619f8e",
    client_secret="34d8Q~B72MZ5PUCQKI5ZCR2L3cM6PB4eJ1teFbw.",
    tenant_id="1b314d3f-4df5-485a-a59b-72335826d944"
)

scopes = ["https://graph.microsoft.com/.default"]

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://utsav:{os.environ.get("POSTGRES_PASSWORD_SQL")}@salesforce-slack-bot-server.postgres.database.azure.com:5432/rfpdemo'
app.config["DEBUG"] = True
db.init_app(app)

with app.app_context():
    db.create_all()


conn = psycopg2.connect(
    user= f"{os.environ.get('POSTGRES_USER')}", 
    password=f"{os.environ.get('POSTGRES_PASSWORD')}", 
    host=f"{os.environ.get('POSTGRES_HOST')}", 
    port=f"{os.environ.get('POSTGRES_PORT')}", 
    database=f"{os.environ.get('POSTGRES_DATABASE')}"
)
cur = conn.cursor()

@app.route('/', methods=['GET'])
def home():
    return "<h1>API is working</h1>"

@app.route('/fill-sheet-tendered', methods=['GET'])
def fill_sheet_tendered():
    site_name = "Tendered"
    cur.execute(f"SELECT * FROM site WHERE name = '{site_name}'")
    site = cur.fetchone()

    chain = create_chain(namespace='Tendered', Prompt = TENDERED_PROMPT )
    row_count, data = getData(credentials, scopes, site_id = site[2], drive_id = site[3], workbook_id = site[4], worksheet_id = site[5])

    if not data:
        return jsonify({"message": "No Data available."})
    

    final_data = []
    for row in data:
        if row[2] == "":
            chat_history = []
            question = row[1]
            response = get_response_from_query(question, chain, chat_history)
            answer = response['Answer']
            answer = answer.replace('""', "")
            print("Answer: ", answer + "\n")
            link = response['link']
            source = response['source']
            confidence_score = response['Confidence']
            page_content = response['page_content'  ]
            print("Confidence: ", confidence_score + "\n")

            invalid_response = filterResponse(answer)
            if invalid_response == "YES":
                confidence_score = "N.A."
                source = "N.A."
                link = "N.A."
                page_content = "N.A."
            final_data.append([answer, confidence_score, source, link, page_content])        

    if final_data:
        start_col ="C"
        end_col = "G"
        populateData(credentials, scopes, site_id = site[2], drive_id = site[3], workbook_id = site[4], worksheet_id = site[5],row_num_start = row_count, row_num_end= row_count+len(final_data)-1, values = final_data, start_col = start_col, end_col = end_col)
        return jsonify({"message": "Questions answered"})

    else:
        return jsonify({"message": "No New Questions to answer."})
    



@app.route('/fill-sheet-maservices', methods=['GET'])
def fill_sheet_maservices():
    site_name = "MAServices"
    cur.execute(f"SELECT * FROM site WHERE name = '{site_name}'")
    site = cur.fetchone()

    chain = create_chain(namespace= site_name, Prompt = MAServicesPrompt )
    row_count, data = getData(credentials, scopes, site_id = site[2], drive_id = site[3], workbook_id = site[4], worksheet_id = site[5])

    if not data:
        return jsonify({"message": "No Data available."})
    

    final_data = []
    for row in data:
        if row[2] == "":
            chat_history = []
            question = row[1]
            response = get_response_from_query(question, chain, chat_history)
            answer = response['Answer']
            answer = answer.replace('""', "")
            print("Answer: ", answer + "\n")
            link = response['link']
            source = response['source']
            confidence_score = response['Confidence']
            page_content = response['page_content'  ]
            print("Confidence: ", confidence_score + "\n")

            invalid_response = filterResponse(answer)
            if invalid_response == "YES":
                confidence_score = "N.A."
                source = "N.A."
                link = "N.A."
                page_content = "N.A."
            final_data.append([answer, confidence_score, source, link, page_content])        

    if final_data:
        start_col ="C"
        end_col = "G"
        populateData(credentials, scopes, site_id = site[2], drive_id = site[3], workbook_id = site[4], worksheet_id = site[5],row_num_start = row_count, row_num_end= row_count+len(final_data)-1, values = final_data, start_col = start_col, end_col = end_col)
        return jsonify({"message": "Questions answered"})

    else:
        return jsonify({"message": "No New Questions to answer."})
    
@app.route('/fill-sheet-jllservices', methods=['GET'])
def fill_sheet_jllservices():
    site_name = "JLLServices"
    cur.execute(f"SELECT * FROM site WHERE name = '{site_name}'")
    site = cur.fetchone()

    chain = create_chain(namespace= site_name, Prompt = JLLServicesPrompt )
    row_count, data = getData(credentials, scopes, site_id = site[2], drive_id = site[3], workbook_id = site[4], worksheet_id = site[5])

    if not data:
        return jsonify({"message": "No Data available."})
    

    final_data = []
    for row in data:
        if row[2] == "":
            chat_history = []
            question = row[1]
            response = get_response_from_query(question, chain, chat_history)
            answer = response['Answer']
            answer = answer.replace('""', "")
            print("Answer: ", answer + "\n")
            link = response['link']
            source = response['source']
            confidence_score = response['Confidence']
            page_content = response['page_content'  ]
            print("Confidence: ", confidence_score + "\n")

            invalid_response = filterResponse(answer)
            if invalid_response == "YES":
                confidence_score = "N.A."
                source = "N.A."
                link = "N.A."
                page_content = "N.A."
            final_data.append([answer, confidence_score, source, link, page_content])        

    if final_data:
        start_col ="C"
        end_col = "G"
        populateData(credentials, scopes, site_id = site[2], drive_id = site[3], workbook_id = site[4], worksheet_id = site[5],row_num_start = row_count, row_num_end= row_count+len(final_data)-1, values = final_data, start_col = start_col, end_col = end_col)
        return jsonify({"message": "Questions answered"})

    else:
        return jsonify({"message": "No New Questions to answer."})
    


@app.route('/fill-sheet-discovery-consulting', methods=['GET'])
def fill_sheet_discovery_consulting():
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials_sheet = Credentials.from_service_account_info(
        {
  "type": "service_account",
  "project_id": "clear-apogee-419012",
  "private_key_id": "de17e216f9f891dcab21d6fbb27e127ef9d0a491",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDb0lAs1fHZ7puG\nSuJMkgklP89iL0EyyMzhzA9V+fAUFsgzt2UP0ehU3uE1c4R2YP/5H2gVPDHge6KB\nYqCGXzXZflOdaHcVQhl0SP6aLk0Cj7WIqGhSys9Af25teG7VV6kFbriu84Qo1y9P\nile4IKY06+JJACKZFhmbYQTd3aAEXTTpY6ERjL7ddg0c67QUznwEOk4KTtlLH6uB\nSrrxbk4czsyNLr+eFHMqVc0J2/SxHTPBsey2eMm73TTVliM6VcqLr6fs3jjekbNs\njkDty35BCB7LY2VeMNdMLBdEW9+uiqCX0LqEH/pAFSgdepIEFzkLiF4dRhqh5qTe\nFaPP9nrRAgMBAAECggEACejfFElcDPp9rIH6VhA4jTNFZ6hIkrf0jAqTZ6lkADzX\nb0Tpj3szk4Vlbs/fiShl67q1qgzn1PZP4PAzu0EGLAEO1wwVP7omTHyorSXQkxCs\nUu4AH3jc+1vvTAwzh2a7c/cuCFWKJ/7s5yOeARsIMR8v6SFyXdc+Jef7lJ6ryrx9\nRFNTgOgsLCerCLLjm1K2lq224qwLn92ZZWEC7FAaoGc260aYqYQYaTha/V0CT1Gf\nKErPD+ECP77I0RIT0tfIJCcGAZpDfLL4A0GrW61sEw+C5wjlrriy9JaHrp9A+aVq\n8Duxm2IPyMfDDMGfJJixk+++OHBkYie5lrW3UvCoQQKBgQD7RN036DEyjZXhzLpX\nOo/ZFTaTcVIka0dOCDBJ1ngpyhh8XhCidksgS5XSO9O68fEC3Vl5wQo91FYBXwVC\nCqCjvN84hYB90CT94fpVj/+kWsr4t++NzVS8qOKBcqx1qXv61PQ31aB+dkYJxQHg\nmb6dKYnlPxZ2fJ4mSru/msStEQKBgQDf9d6u7/g8VVkviF6yeIJOcDLdsevKJis2\nMhuMKRlnDwaWagbp2s2iqyCNyVN7VAERmk/fYO+Sj0+RGa0cAakemoHPDyI89/Qs\nI6kZw54RUu12LeXdVB436Uj83q7IbWy9yE8O+JcXgWNMVUh3FN6xyG/qPPnioGRC\numzb+pPxwQKBgQC7IEr7gtF4y5bOxXAU3Ekaq0Csx50cAETnKRQFOVLeFGLt5APR\nafWDBKd8HRAOznXl40DqesgMyeCPPtukllOR/WvkJRBPIj8aUDvlkssY9IDqf9lI\nqp0rrz6YlvU231S0tfl2x4KyC5UXW3+NbBJX6wKGFti8vwvsioWOKU3FcQKBgBTM\nOl+4fS7tJhkZ6uFb+43ZMYAQ87qUDNM9l/1OG8PMS2pQck/pN8txZNaF6bC8PlUq\nJVyzHcxYbqUk40SEivYClydpWl6bEBvBPATee6FUOCUPYhdJpny+tz50V3rZXo3J\nOj5Dq5RNObFvAgm88GlGGc6A1xvKlUT1FwLepDqBAoGBAOunkjiCvt7/vp3J8+Mk\nEVxLr43KuNAZrSEIcL0KkGqqxmG4DRJ1iHr1kGeVbWvB90wOdaPI9Gffi2+b4E+O\naX/+WtIUvtDTP4EZ72FRqUGstMThLI9mIUa9DdV0/JBbnNZ9sjoHPNH5gNXINzT/\nXTA3WApOWI+ttE/Hh381AuTv\n-----END PRIVATE KEY-----\n",
  "client_email": "python-api@clear-apogee-419012.iam.gserviceaccount.com",
  "client_id": "114125707600062601450",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/python-api%40clear-apogee-419012.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

        
        
        , scopes=scope)
    client = gspread.authorize(credentials_sheet)
    site_name = "DiscoveryConsulting"
    SHEET_ID_DISCOVERY_CONSULTING = "1Da6VxazZnjuZ86BdnYstwGAOLD_BmfiryfKvM4jNwHo"

    workbook = client.open_by_key(SHEET_ID_DISCOVERY_CONSULTING)
    sheets = workbook.worksheets()
    sheet = sheets[0]
    all_values = sheet.get_all_records(head = 2, expected_headers=["Section", "Requirement", "Response", "Confidence score", "Data Source", "URL", "Snippet"])

    chain = create_chain(namespace= site_name, Prompt = DiscoveryConsultingPrompt)

    found_first_empty = False
    row_num = None
    data = []
    for i, row in enumerate(all_values):
        question = row['Requirement']
        Response = row['Response']

        if question == "":
            break
        elif Response != "":
            continue
        elif Response == "" and not found_first_empty:
            found_first_empty = True
            row_num = i + 3

        chat_history = []
        response = get_response_from_query(question, chain, chat_history)
        answer = response['Answer']
        answer = answer.replace('""', "")
        print("Answer: ", answer + "\n")
        link = response['link']
        source = response['source']
        confidence_score = response['Confidence']
        page_content = response['page_content']
        print("Confidence: ", confidence_score + "\n")

        invalid_response = filterResponse(answer)
        if invalid_response == "YES":
            confidence_score = "N.A."
            source = "N.A."
            link = "N.A."
            page_content = "N.A."
        data.append([answer, confidence_score, source, link, page_content]) 

    if data:
        print(data)
        print(f'C{row_num}')
        sheet.update(data, f'C{row_num}')
        return jsonify({"message": "Questions answered"})

    else:
        return jsonify({"message": "No New Questions to answer."})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
