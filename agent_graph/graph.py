import json
import ast
from termcolor import colored
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage
from agents.agents import (
  PlannerAgent,
  DataManagerAgent,
  WebSearcherAgent,
  DatabaseReviewerAgent,
  WebReviewerAgent,
  ConversationalAgent,
  OCRReviewerAgent,
  EndNodeAgent
)

from prompts.prompts import (
  planner_prompt_template,
  retriever_prompt_template,
  websearcher_prompt_template,
  datamanager_prompt_template,
  webreviewer_prompt_template,
  dbreviewer_prompt_template,
  conversational_prompt_template,
  ocrreviewer_prompt_template,
  planner_guided_json,
  retriever_guided_json,
  websearcher_guided_json,
  datamanager_guided_json,

  
)

from states.state import AgentGraphState, get_agent_graph_state, state 
from tools.tavily import get_google_serper
from tools.database_query import get_order_status
from tools.perform_ocr import perform_ocr

def create_graph(server=None, model=None, stop=None, model_endpoint=None, temperature=0):
  graph = StateGraph(AgentGraphState)

  graph.add_node(
    "planner",
    lambda state: PlannerAgent(
      state = state,
      model = model,
      server = server,
      guided_json = planner_guided_json,
      stop = stop,
      model_endpoint = model_endpoint,
      temperature = temperature
    ).invoke(
      query_question = state["query_question"],
      prompt = planner_prompt_template
    )
  )


  # graph.add_node(
  #   "retriever",
  #   lambda state: RetrieverAgent(
  #     state = state,
  #     model = model,
  #     server = server,
  #     guided_json = retriever_guided_json,
  #     stop = stop,
  #     model_endpoint = model_endpoint,
  #     temperature = temperature
  #   ).invoke(
  #     query_question = state["query_question"],
  #     prompt = retriever_prompt_template
  #   )
  # )


  graph.add_node(
    "datamanager",
    lambda state: DataManagerAgent(
      state = state,
      model = model,
      server = server,
      guided_json = datamanager_guided_json,
      stop = stop,
      model_endpoint = model_endpoint,
      temperature = temperature
    ).invoke(
      query_question = state["query_question"],
      prompt = datamanager_prompt_template
    )
  )

  graph.add_node(
    "websearcher",
    lambda state: WebSearcherAgent(
      state = state,
      model = model,
      server = server,
      guided_json = websearcher_guided_json,
      stop = stop,
      model_endpoint = model_endpoint,
      temperature = temperature
    ).invoke(
      query_question = state["query_question"],
      prompt = websearcher_prompt_template
    )
  )



  graph.add_node(
    "dbreviewer",
    lambda state : DatabaseReviewerAgent(
      state = state,
      model = model,
      server = server,
      guided_json = None,
      stop = stop,
      model_endpoint = model_endpoint,
      temperature = temperature
    ).invoke(
      query_question = state["query_question"],
      previous_report = state["dbquery_response"],
      prompt = dbreviewer_prompt_template
    )
  )

  graph.add_node(
    "webreviewer",
    lambda state : WebReviewerAgent(
      state = state,
      model = model,
      server = server,
      guided_json = None,
      stop = stop,
      model_endpoint = model_endpoint,
      temperature = temperature
    ).invoke(
      query_question = state["query_question"],
      previous_report = state["searchtool_response"],
      prompt = webreviewer_prompt_template
    )
  )

  graph.add_node(
    "ocr_reviewer",
    lambda state: OCRReviewerAgent(
      state=state,
      model=model,
      server=server,
      guided_json=None,
      stop=stop,
      model_endpoint=model_endpoint,
      temperature=temperature
    ).invoke(
      query_question=state["query_question"],
      previous_report=state["ocr_response"],
      prompt=ocrreviewer_prompt_template
    )
  )

  graph.add_node(
    "conversational",
    lambda state: ConversationalAgent(
      state=state,
      model=model,
      server=server,
      guided_json=None,
      stop=stop,
      model_endpoint=model_endpoint,
      temperature=temperature
    ).invoke(
      query_question=state["query_question"],
      previous_report=state["searchtool_response"],
      prompt=conversational_prompt_template
    )
  )

  graph.add_node(
    "serper_tool",
    lambda state: get_google_serper(
      state = state,
      plan = state["searcher_response"]
    )
  )

  graph.add_node(
    "database_tool",
    lambda state: get_order_status(
      state = state,
      dataquery = state["datamanager_response"]
    )
  )

  graph.add_node(
    "ocr_tool",
    lambda state: perform_ocr(
      state = state,
      image_info = state["image_info"]
    )
  )

  def decide_next_node(state:state) :
      planner_response = state["planner_response"]

      last_item = planner_response[-1].content
      value = json.loads(last_item)
      next_agent = value.get("next_agent")
      print(colored(f"Next Node 👩🏿‍💻: {next}", 'cyan'))
      if next_agent == "WebSearcher":
        return "websearcher"
      if next_agent == "DataManager":
        return "datamanager"
      if next_agent == "OcrTool":
        return "ocr_tool"
      if next_agent == "Conversational":
        return "conversational"
      else :
        return "conversatational"


  graph.add_node("end", lambda state: EndNodeAgent(state).invoke())


  graph.set_entry_point("planner")
  graph.set_finish_point("end")

  graph.add_conditional_edges("planner", lambda state: decide_next_node(state= state))

  graph.add_edge("websearcher", "serper_tool")
  graph.add_edge("serper_tool","webreviewer")


  graph.add_edge("datamanager", "database_tool")
  graph.add_edge("database_tool","dbreviewer")

  graph.add_edge("dbreviewer","end")
  graph.add_edge("webreviewer", "end")

  graph.add_edge("ocr_tool","ocr_reviewer")
  graph.add_edge("ocr_reviewer","end")

  graph.add_edge("conversational", "end")
  

  return graph 

def compile_workflow(graph):
  workflow = graph.compile()
  return workflow