import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_BASE_URL_1 = "https://api.gpts.vin/v1"
    OPENAI_API_BASE_URL_2 = "https://api.gpts.vin"
    OPENAI_API_BASE_URL_3 = "https://api.gpts.vin/v1/chat/completions"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Assuming you have this in your .env file
