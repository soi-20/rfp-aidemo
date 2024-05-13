import os
from flask import Flask, request, jsonify
from models import db
from azure.identity import ClientSecretCredential
import gspread
from google.oauth2.service_account import Credentials
from Excel.getData import getData, getDataHeightPM
from Excel.populateData import populateData
from Model.main import create_chain, get_response_from_query, filterResponse, get_response_from_query_heightPM
from Model.prompts import TENDERED_PROMPT, MAServicesPrompt, JLLServicesPrompt, DiscoveryConsultingPrompt, ServiceFMPrompt, HeightPMPrompt, DownerGroupPrompt
from dotenv import load_dotenv
import psycopg2
load_dotenv()

credentials = ClientSecretCredential(
    client_id="86dfb3ef-b0fc-4bbe-90b6-f1a11c619f8e",
    client_secret="34d8Q~B72MZ5PUCQKI5ZCR2L3cM6PB4eJ1teFbw.",
    tenant_id="1b314d3f-4df5-485a-a59b-72335826d944"
)

scopes = ["https://graph.microsoft.com/.default"]

scope = ["https://www.googleapis.com/auth/spreadsheets"]
credentials_sheet = Credentials.from_service_account_file("credentials.json", scopes=scope)
client = gspread.authorize(credentials_sheet)

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
    

@app.route('/fill-sheet-servicefm', methods=['GET'])
def fill_sheet_serviceFM():
    site_name = "ServiceFM"
    cur.execute(f"SELECT * FROM site WHERE name = '{site_name}'")
    site = cur.fetchone()
    print(site)
    chain = create_chain(namespace= site_name, Prompt = ServiceFMPrompt )
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


@app.route('/fill-sheet-downer', methods=['GET'])
def fill_sheet_downer():
    site_name = "DownerGroup2"
    cur.execute(f"SELECT * FROM site WHERE name = '{site_name}'")
    site = cur.fetchone()
    chain = create_chain(namespace= site_name, Prompt = DownerGroupPrompt )
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
    
@app.route('/fill-sheet-heightpm', methods=['GET'])
def fill_sheet_heightPM():
    site_name = "HeightPM"
    cur.execute(f"SELECT * FROM site WHERE name = '{site_name}'")
    site = cur.fetchone()

    chain = create_chain(namespace= site_name, Prompt = HeightPMPrompt )
    row_count, data = getDataHeightPM(credentials, scopes, site_id = site[2], drive_id = site[3], workbook_id = site[4], worksheet_id = site[5])

    if not data:
        return jsonify({"message": "No Data available."})
    

    final_data = []
    for i, row in enumerate(data):
        if row[1] == "":
            if i == 0:
                continue
            chat_history = []
            question = row[0]
            response = get_response_from_query_heightPM(question, chain, chat_history)
            answer = response['Answer']
            final_answer = ""
            try:
                answer = answer.split("\n")
                for ans in answer:
                    final_answer += ans + "\n\n"
                # Remove the last 2 new lines
                final_answer = final_answer[:-2]
            
            except Exception as e:
                final_answer = answer
        
            print("Answer: ", final_answer + "\n")
            # link = response['link']
            # source = response['source']
            # page_content = response['page_content']
            final_data.append([final_answer])        

    if final_data:
        start_col ="B"
        end_col = "B"
        populateData(credentials, scopes, site_id = site[2], drive_id = site[3], workbook_id = site[4], worksheet_id = site[5],row_num_start = row_count, row_num_end= row_count+len(final_data)-1, values = final_data, start_col = start_col, end_col = end_col)
        return jsonify({"message": "Questions answered"})

    else:
        return jsonify({"message": "No New Questions to answer."})
    


@app.route('/fill-sheet-discovery-consulting', methods=['GET'])
def fill_sheet_discovery_consulting():
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
