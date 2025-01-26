import os
from datetime import datetime, timezone 
import yaml 

# Load configs to environment variables
def load_config(file_path):
  default_values = {
    'TAVILY_API_KEY': 'default_tavily_api_key',
    'GROQ_API_KEY': 'default_groq_api_key',
  }

  with open(file_path, "r") as file:
    config = yaml.safe_load(file)
    for key, value in config.items():
      if not value:
        os.environ[key] = default_values.get(key, "")
      else:
        os.environ[key] = value

# Get current date and time in UTC
def get_current_utc_datetime():
  now_utc = datetime.now(timezone.utc)
  current_time_utc = now_utc.strftime("%Y-%m-%d %H:%M:%S %Z")
  return current_time_utc

