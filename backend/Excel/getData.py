import requests

def getData(credentials, scopes, site_id, drive_id, workbook_id, worksheet_id):
    access_token = credentials.get_token(*scopes)
    endpoint = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/{workbook_id}/workbook/worksheets/{worksheet_id}/usedRange'
    headers = {
        'Authorization': f'Bearer {access_token.token}'
    }
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        worksheet_data = response.json()
        data = worksheet_data['values']
        first_empty_row = None
        for i, row in enumerate(data):
            if row[2] == "":
                first_empty_row = i + 1
                break
        return first_empty_row, worksheet_data['values']
    else:
        print(f"Failed to retrieve worksheet data: {response.status_code}")