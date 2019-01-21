import os
import pathlib
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from wimpy import cached_property

class GoogleSheetsAPI(object):
  TOKEN_PATH = pathlib.Path("google-auth-token.pickle")

  # If modifying these scopes, delete the TOKEN_PATH.
  SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

  @cached_property
  def creds(self):
    creds_path = pathlib.Path(os.environ["SB_BOMTOOL_GOOGLE_API_CREDS"])
    creds = None
    if self.TOKEN_PATH.exists():
      with self.TOKEN_PATH.open("rb") as file:
        creds = pickle.load(file)
    if not creds or not creds.valid:
      # Need to update credentials.
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(creds_path, self.SCOPES)
        creds = flow.run_local_server()
      with self.TOKEN_PATH.open("wb") as file:
        pickle.dump(creds, file)
    return creds

  @cached_property
  def service(self):
    return build("sheets", "v4",
      credentials=self.creds,
      cache_discovery=False, # https://github.com/googleapis/google-api-python-client/issues/299
    )

  def spreadsheet(self, id):
    return Spreadsheet(self, id)

class Spreadsheet(object):
  def __init__(self, api, id):
    self.api = api
    self.id = id

  def sheet(self, name):
    return Sheet(self.api, self, name)

class Sheet(object):
  def __init__(self, api, spreadsheet, name):
    self.api = api
    self.spreadsheet = spreadsheet
    self.name = name

  @property
  def range(self):
    return f"'{self.name}'"

  def clear(self):
    self.api.service.spreadsheets().values().clear(
      spreadsheetId = self.spreadsheet.id,
      range = self.range,
    ).execute()

  def append(self, rows):
    self.api.service.spreadsheets().values().append(
      spreadsheetId = self.spreadsheet.id,
      range = self.range,
      body = {
        "majorDimension": "ROWS",
        "values": list(rows),
      },
      valueInputOption = "USER_ENTERED",
    ).execute()
