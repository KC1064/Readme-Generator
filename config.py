import os
from dotenv import load_dotenv

def load_api_keys():
    load_dotenv()
    api_key = os.getenv("API_KEY")
    
    return api_key
