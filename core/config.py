import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
  # Gogle OAuth
  GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID','')
  GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET','') 
  GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/google/callback")

  # Optional: Database or secrets manager settings
  DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

  # OPENAI API
  OPENAI_API_KEY = os.getenv('OPENAI_API_KEY','')


settings = Settings()
