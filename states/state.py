from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages



# Define state object for agent graph
# Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)

class AgentGraphState(TypedDict):
  query_question: str 
  planner_response: Annotated[list, add_messages]
  retriever_response: Annotated[list, add_messages]
  datamanager_response: Annotated[list, add_messages]
  searcher_response: Annotated[list, add_messages]
  reviewer_response: Annotated[list, add_messages]
  end_chain: Annotated[list, add_messages]
  dbquery_response: Annotated[list, add_messages]
  searchtool_response: Annotated[list, add_messages]
  image_info : Annotated[list,add_messages]
  ocr_response: Annotated[list,add_messages]



def get_agent_graph_state(state:AgentGraphState, state_key: str): 
  return None

state = {

  "query_question": "",
  "planner_response": [],
  "retriever_response": [],
  "datamanager_response": [],
  "searcher_response": [],
  "dbquery_response": [],
  "searchtool_response": [],
  "reviewer_response": [],
  "image_info": [],
  "ocr_response": [],
  "end_chain": []
} 