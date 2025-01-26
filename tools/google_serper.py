import os
import ast 
import requests
import json 
from langchain_community.utilities import GoogleSerperAPIWrapper
from states.state import AgentGraphState
from utils.helper_functions import load_config
from termcolor import colored
config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')

def format_results(result):
  result_strings = []
  for place in result.get("results", []):
    Name = place.get('name', 'No Name')
    Address = place.get('formatted_address','No address')
    Location = place.get('geometry', {}).get('location')
    result_strings.append(f"Name: {Name}\nAddress: {Address}\nLocation: {Location}")

  return '\n'.join(result_strings)
  
def get_google_serper(state:AgentGraphState, plan):
  load_config(config_path)

  plan_data = plan[-1].content
  plan_data = json.loads(plan_data)
  search_term = plan_data.get("search_term")

  print(colored(f"search 👩🏿‍💻: {search_term}", 'cyan'))
  search = search_term
  search_url = "https://google.serper.dev/search"
  headers = {
    "X-API-KEY" : "your_serper_api_key",
    "Content-Type": "application/json"
  }
  payload = json.dumps({"q": search})

  try:
    response = requests.post(search_url, headers=headers, data = payload)
    response.raise_for_status()
    results = response.json()

    formatted_results = format_results(results)

    print(colored(f"Result from serper 👩🏿‍💻: {str(results)}", 'cyan'))
    state = {**state, "serpent_response": formatted_results}
    return state 
  
  except requests.exceptions.HTTPError as http_err:
    return {**state, "serper_response": f"HTTP error occurred: {http_err}"}
  except requests.exceptions.RequestException as req_err:
    return {**state, "serper_response": f"Req error occurred: {req_err}"}
  except KeyError as key_err:
    return {**state, "serper_response": f"Key error occurred: {key_err}"}

  
