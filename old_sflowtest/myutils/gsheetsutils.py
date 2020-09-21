from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from json import dumps

def get_service(scopes='https://www.googleapis.com/auth/spreadsheets', clientsecrets_f_name='credentials.json', store_f_name='token.json'):
  # check if method called as part of main program or library function
  if __name__ != '__main__':
    # if method called as library function, need to emulate parsing parameters from command line
    import argparse
    parser = argparse.ArgumentParser(
      description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter,
      parents=[tools.argparser])
    args = parser.parse_args(['--noauth_local_webserver'])

  store = file.Storage(store_f_name)
  creds = store.get()
  if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets(clientsecrets_f_name, scopes)
    creds = tools.run_flow(flow, store)
  service = build('sheets', 'v4', http=creds.authorize(Http()))
  return service

def get_sheet_ID(service, spreadsheet_ID, sheet_name):
  data_sheet_ID = None
  response = service.spreadsheets().get(spreadsheetId=spreadsheet_ID).execute()
  for s in response['sheets']:
    if s['properties']['title'] == sheet_name:
      data_sheet_ID = s['properties']['sheetId']
      break
  # print_err('Sheet ID: {}'.format(data_sheet_ID))
  return data_sheet_ID

def get_sheet_ID_removing_other_sheets(service, spreadsheet_ID, sheet_name):
  # discover sheet ID
  keep_sheet_ID = None
  response = service.spreadsheets().get(spreadsheetId=spreadsheet_ID).execute()
  for s in response['sheets']:
    if s['properties']['title'] == sheet_name:
      keep_sheet_ID = s['properties']['sheetId']
      break
  # print_err('Sheet ID: {}'.format(keep_sheet_ID))

  # remove other sheets
  requests = []
  for s in response['sheets']:
    if s['properties']['sheetId'] != keep_sheet_ID:
      requests.append({
        "deleteSheet": {
          "sheetId": s['properties']['sheetId']
        }
      })
  # proceed only if there are sheets to be removed
  if requests:
    # prepare body of batchUpdate
    body = {
      'requests': requests
    }
    # send batchUpdate
    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_ID,
        body=body).execute()

  return keep_sheet_ID

def clear_values(service, spreadsheet_ID, range_to_clear):
  # clear sheet in range
  request = service.spreadsheets().values().clear(spreadsheetId=spreadsheet_ID, range=range_to_clear, body={})
  response = request.execute()

def add_data(service, spreadsheet_ID, start_position, rows_list):
  # add data to sheet
  body = {
      'values': rows_list
  }
  response = service.spreadsheets().values().update(
      spreadsheetId=spreadsheet_ID, range=start_position,
      valueInputOption='USER_ENTERED', body=body).execute()
  # return number of updated cells
  return response.get('updatedCells')

def add_data_and_chart(service, spreadsheet_ID, start_position, rows_list, data_sheet_ID, chart_type='LINE', chart_title='Test Chart', x_title='x', y_title='y'):
  # first, add data
  add_data(service, spreadsheet_ID, start_position, rows_list)
  # add chart
  endRow = len(rows_list)
  series = []
  for start_column_index in range(len(rows_list[0])):
    series.append({
      "series": {
        "sourceRange": {
          "sources": [
            {
              "sheetId": data_sheet_ID,
              "startRowIndex": 0,
              "endRowIndex": endRow,
              "startColumnIndex": start_column_index,
              "endColumnIndex": start_column_index+1
            }
          ]
        }
      },
      "targetAxis": "LEFT_AXIS"
    })
  # build request body
  body = {
    "requests": [
      {
        "addChart": {
          "chart": {
            "spec": {
              "title": chart_title,
              "basicChart": {
                "chartType": chart_type,
                "legendPosition": "BOTTOM_LEGEND",
                "axis": [
                  {
                    "position": "BOTTOM_AXIS",
                    "title": x_title
                  },
                  {
                    "position": "LEFT_AXIS",
                    "title": y_title
                  }
                ],
                "domains": [],
                "series": series,
                "headerCount": 1
              }
            },
            "position": {
              "newSheet": True
            }
          }
        }
      }
    ]
  }
  request = service.spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_ID, body=body)
  response = request.execute()

# TODO
# def update_sheet(...)
# function that takes data as input and clears datasheet, removes old chart and adds new one
def rewrite_sheet(scopes, clientsecrets_f_name, store_f_name, spreadsheet_ID, sheet_name, rows_list,
                  chart_type='LINE', chart_title='Test Chart', x_title='x', y_title='y'):
  service = get_service(scopes, clientsecrets_f_name, store_f_name)
  data_sheet_ID = get_sheet_ID_removing_other_sheets(service, spreadsheet_ID, sheet_name)
  clear_values(service, spreadsheet_ID, sheet_name+'!$A$1:$YY')
  add_data_and_chart(service, spreadsheet_ID, sheet_name+'!A1', rows_list, data_sheet_ID, chart_type, chart_title, x_title, y_title)

# MAIN that will be executed when library called as script
if __name__ == '__main__':

  from sys import stderr, argv
  def print_err(s):
    print(s, file=stderr)

  # parse parameters from command line
  import argparse

  parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])

  #parser = argparse.ArgumentParser()

  # SAMPLE_SPREADSHEET_ID = '1fk2AuFigFR_g66etEJEeGm_Hb8ERF8IlEIuaf974nSk'
  # SAMPLE_RANGE_NAME = 'Foglio1!$A$1:$YY'
  parser.add_argument('spreadsheet_ID', help="Google Sheet ID (as in the URL)")
  parser.add_argument('data_sheet_name', help="Name of the sheet with the data (e.g. Sheet1)", nargs='?', default='Sheet1')  
  parser.add_argument('scopes', help="Google API authorization scope(s)", nargs='?', default='https://www.googleapis.com/auth/spreadsheets')

  args = parser.parse_args(['--noauth_local_webserver'] + argv[1:])

  spreadsheet_ID = args.spreadsheet_ID
  print_err('Spreadsheet ID: {}'.format(spreadsheet_ID))
  data_sheet_name = args.data_sheet_name
  print_err('Data sheet name: {}'.format(data_sheet_name))
  scopes = args.scopes
  print_err('Scopes: {}'.format(scopes))

  service = get_service(scopes)

  data_sheet_ID = get_sheet_ID_removing_other_sheets(service, spreadsheet_ID, data_sheet_name)
  print_err('Sheet {} has Sheet ID {}'.format(data_sheet_name, data_sheet_ID))

  clear_values(service, spreadsheet_ID, data_sheet_name+'!$A$1:$YY')

  # generate example data
  from random import randint
  rows_list = [['', 'Data1', 'Data2', 'Data3']]
  for row_index in range(randint(33, 66)):
    rows_list.append(['Point {}'.format(row_index), row_index*randint(0,3), row_index*randint(4,6), row_index*randint(7,9)])

  add_data_and_chart(service, spreadsheet_ID, data_sheet_name+'!A1', rows_list, data_sheet_ID, chart_type='COLUMN', chart_title='Test Chart', x_title='Test X', y_title='Test Y')

