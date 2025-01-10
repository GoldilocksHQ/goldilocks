from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os
import json


class TokenManager:
  def __init__(self):
    self.token_store_path = 'token.json' # For MVP only; in production use a DB or Vault TODO

  def load_tokens(self):
    if os.path.exists(self.token_store_path):
      with open(self.token_store_path, 'r') as token_file:
        return json.load(token_file)
    return {}
  
  def save_tokens(self, token_dict):
    with open(self.token_store_path, 'w') as token_file:
      json.dump(token_dict, token_file)

  def get_credentials(self, user_id: str)-> Credentials:
    token_dict = self.load_tokens()
    user_tokens = token_dict.get(user_id)
    if not user_tokens:
      return None

    creds = Credentials.from_authorized_user_info(user_tokens)
    # If credentials are invalid or expired, try refresh
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
      # Save updated creds
      token_dict[user_id] = json.loads(creds.to_json())
      self.save_tokens(token_dict)
    return creds
  
  def store_credentials(self, user_id:str, creds: Credentials):
    tokens_dict = self.load_tokens()
    tokens_dict[user_id] = json.loads(creds.to_json())
    self.save_tokens(tokens_dict)