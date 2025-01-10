import json
from fastapi import FastAPI, Request, HTTPException
from connectors.google_sheets.connector import GoogleSheetsConnector
from core.config import settings

app = FastAPI()
sheets_connector = GoogleSheetsConnector()

@app.get("/google/auth_url")
def get_auth_url(user_id: str):
  """Generate a Google Sheets OAuth URL for the given user ID"""
  url = sheets_connector.get_authorization_url(user_id)
  return {"auth_url": url}

@app.get("/google/callback")
def google_callback(request: Request, state: str, code: str):
  """Handle Google OAuth callback"""
  # state: user_id is embedded in the state parameter
  # code: the auth code from Google
  try:
    # Decode state to get user_id
    state_data = json.loads(state)
    user_id = state_data.get("user_id")
    if not user_id:
      raise HTTPException(status_code=400, detail="Missing user_id in state")
    sheets_connector.exchange_code_for_tokens(user_id, code)
    return {"message": "Google Sheets authorization successful"}
  except json.JSONDecodeError:
    raise HTTPException(status_code=400, detail="Invalid state parameter")
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))

@app.get("/google/read")
def read_sheet(user_id: str, spreadsheet_id: str, range_name: str):
  """Read data from a specified range in Google Sheets"""
  try:
    values = sheets_connector.read_values(user_id, spreadsheet_id, range_name)
    return {"values": values}
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))
  
@app.post("/google/update")
def write_sheet(user_id: str, spreadsheet_id: str, range_name: str, data: dict):
  """Write data to a specified range in Google Sheets"""
  # data: {"values": [[row1_col1, row1_col2], [row2_col1, row2_col2]]}
  try:
    results = sheets_connector.update_values(user_id, spreadsheet_id, range_name, data)
    return {"results": results}
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))