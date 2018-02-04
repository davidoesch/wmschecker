
#According to https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html
#Created google credentials via https://gspread.readthedocs.io/en/latest/oauth2.html

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

def ExportToGoogle (my_data,my_sheet,my_creds):
        
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name(my_creds, scope)
    client = gspread.authorize(creds)

    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open(my_sheet).sheet1                        
    sheet.append_row([str(datetime.datetime.now().strftime("%Y-%m-%d")),my_data['WMS_IDENT_TITLE'],my_data['URL'],my_data['Layer'],my_data['Test_OGC'],my_data['Test_Speed'],my_data['Test_Browser'],my_data['MapGeo_Link'],my_data['OtherError']])

def ClearGoogle (my_sheet,my_creds):
        
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name(my_creds, scope)
    client = gspread.authorize(creds)

    # Find a workbook by name and open the first sheet
    # delete all but first and second (due to freozen pane).
    sheet = client.open(my_sheet).sheet1                        
    sheet.resize(rows=2)

    # Select Second row
    cell_list = sheet.range('A2:Z2')
    for cell in cell_list:
        cell.value = ''
    # Update in batch
    sheet.update_cells(cell_list)
