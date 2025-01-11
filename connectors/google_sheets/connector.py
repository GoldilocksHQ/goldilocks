import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from typing import Optional
from core.config import settings
from core.token_manager import TokenManager
from googleapiclient.discovery import build

class GoogleSheetsConnector:
  def __init__(self):
    self.token_manager = TokenManager()

  def is_authorized(self, user_id: str) -> bool:
    return self.token_manager.get_credentials(user_id) is not None

  def get_authorization_url(self, user_id: str)-> str:
    # Scopes to read/write Google Sheets
    flow  = Flow.from_client_config(
      {
        "web": {
          "client_id": settings.GOOGLE_CLIENT_ID,
          "client_secret": settings.GOOGLE_CLIENT_SECRET,
          "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
          "auth_uri": "https://accounts.google.com/o/oauth2/auth",
          "token_uri": "https://accounts.google.com/o/oauth2/token"
        }
      },
      scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

    state = json.dumps({"user_id": user_id}).replace(' ', '%20')
    authorization_url, state = flow.authorization_url(
      access_type="offline",
      prompt="consent",
      state=state
    )
    # Optionally store "state" in a local dict or DB for validation: TODO
    return authorization_url
  
  def exchange_code_for_tokens(self, user_id:str, code:str) -> None:
    flow = Flow.from_client_config(
      {
          "web": {
              "client_id": settings.GOOGLE_CLIENT_ID,
              "client_secret": settings.GOOGLE_CLIENT_SECRET,
              "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
              "auth_uri": "https://accounts.google.com/o/oauth2/auth",
              "token_uri": "https://oauth2.googleapis.com/token"
          }
      },
      scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    flow.fetch_token(code=code)

    creds = flow.credentials
    self.token_manager.store_credentials(user_id, creds)

  def get_credentials(self, user_id: str) -> Optional[Credentials]:
    # Retrieve valid credentials from token manager
    return self.token_manager.get_credentials(user_id)
  
  def read_values(self, user_id:str, spreadsheet_id: str, range_name: str):
    creds = self.get_credentials(user_id)
    if not creds:
      raise Exception("No valid credentials. User must authorize first.")
    
    service = build("sheets", "v4", credentials=creds)
    result = service.spreadsheets().values().get(
      spreadsheetId=spreadsheet_id,
      range=range_name
    ).execute()

    return result.get("values", [])
  
  def update_values(self, user_id:str, spreadsheet_id: str, range_name: str, data: dict):
    creds = self.get_credentials(user_id)
    if not creds:
      raise Exception("No valid credentials. User must authorize first.")
    
    service = build("sheets", "v4", credentials=creds)
    result = service.spreadsheets().values().update(
      spreadsheetId=spreadsheet_id,
      range=range_name,
      valueInputOption="RAW",
      body=data
    ).execute()

    return result
    


