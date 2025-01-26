
import os
import ast
import requests
import json
from states.state import AgentGraphState
from utils.helper_functions import load_config
from termcolor import colored
config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
from tavily import TavilyClient

def get_google_serper(state: AgentGraphState, plan):
    # Load configuration (assuming load_config is defined elsewhere)
    load_config(config_path)


    # Extract the search term from the plan
    plan_data = plan[-1].content
    plan_data = json.loads(plan_data)
    search_term = plan_data.get("search_term")

    print(colored(f"Search 👩🏿‍💻: {search_term}", 'cyan'))

    tavily_api_key = os.environ['TAVILY_API_KEY']



    try:
        tavily_client = TavilyClient(api_key=tavily_api_key)

        response = tavily_client.search(search_term)
        results = response["results"][0]["content"]
        print(colored(f"Result from Tavily 👩🏿‍💻: {results}", 'cyan'))

        # Update the state with the Tavily response
        state = {**state, "searchtool_response": results}
        return state

    except requests.exceptions.HTTPError as http_err:
        print(colored(f"Result from Tavily 👩🏿‍💻: {http_err}", 'cyan'))
        return {**state, "searchtool_response": f"HTTP error occurred: {http_err}"}

    except requests.exceptions.RequestException as req_err:
        return {**state, "searchtool_response": f"Request error occurred: {req_err}"}
    except KeyError as key_err:
        return {**state, "searchtool_response": f"Key error occurred: {key_err}"}