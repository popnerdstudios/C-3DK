from langchain.utilities import SerpAPIWrapper
from dotenv import load_dotenv
import os

# If your .env file is in a subdirectory called 'config', for example
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

# Now you can safely retrieve the environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
serpapi_api_key = os.getenv("SERPAPI_API_KEY")

serpapi_params = {
    "engine": "google",
    "gl": "us",
    "hl": "en",
}

serp_api = SerpAPIWrapper(params=serpapi_params)

def search_general(input_text):
    return serp_api.run(input_text)
