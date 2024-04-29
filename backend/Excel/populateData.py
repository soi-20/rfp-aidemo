import requests

def populateDataTendered(credentials, scopes, site_id, drive_id, workbook_id, worksheet_id, row_num_start, row_num_end, values):
    access_token = credentials.get_token(*scopes)
    endpoint = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/{workbook_id}/workbook/worksheets/{worksheet_id}/range(address=\'C{row_num_start}:G{row_num_end}\')'
    headers = {
        'Authorization': f'Bearer {access_token.token}'
    }
    data = {"values": values}
    response = requests.patch(endpoint, headers=headers, json=data)
    if response.status_code == 200:
        print("Successfully updated the workbook.")
    else:
        print(f"Failed to update the workbook: {response.status_code} - {response.text}")