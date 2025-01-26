from termcolor import colored
from models.groq_model import GroqModel , GroqJSONModel
from prompts.prompts import (
  planner_prompt_template,
  websearcher_prompt_template,
  retriever_prompt_template,
  datamanager_prompt_template,
  dbreviewer_prompt_template,
  webreviewer_prompt_template,
  conversational_prompt_template,
  ocrreviewer_prompt_template
)
from states.state import AgentGraphState

class Agent:
  def __init__(self, state: AgentGraphState, model=None, server = None, temperature = 0,model_endpoint = None, stop = None, guided_json = None):
    self.state = state 
    self.model = model
    self.server = server
    self.temperature = temperature
    self.model_endpoint = model_endpoint
    self.stop = stop 
    self.guided_json = guided_json

  def get_llm(self, json_model = True):
    if self.server == 'groq':
      return GroqJSONModel(
        model=self.model,
        temperature= self.temperature
      )if json_model else GroqModel(
        model = self.model,
        temperature = self.temperature
      )
    
  def update_state(self,key,value):
    self.state = {**self.state, key: value}


class PlannerAgent(Agent):
  def invoke(self, query_question, prompt = planner_prompt_template, feedback = None):

    # Insert values for placeholder in prompt, Useful for future
    # planner_prompt = prompt.format()

    messages = [
      {"role": "system", "content": prompt},
      {"role": "user", "content": f"query question : {query_question}"}
    ]

    llm = self.get_llm()
    ai_msg = llm.invoke(messages)
    response = ai_msg.content

    self.update_state("planner_response", response)
    print(colored(f"Planner: {response}", "cyan"))
    return self.state
  
class RetrieverAgent(Agent):
  def invoke(self, query_question, prompt=retriever_prompt_template, feedback = None, previous_selections = None, serp = None):
    

    retriever_prompt = prompt.format()

    messages = [
      {"role": "system", "content": retriever_prompt},
      {"role": "user", "content":f"query_question: {query_question}"}
    ]

    llm = self.get_llm()
    ai_msg = llm.invoke(messages)
    response = ai_msg.content

    # print(colored(f"selector 🧑🏼‍💻: {response}", 'green'))
    self.update_state("retriever_response", response)
    return self.state
  
class DataManagerAgent(Agent):
    def invoke(self, query_question, prompt = datamanager_prompt_template, feedback = None):

      datamanager_prompt = prompt.format()

      messages = [
        {"role": "system", "content": datamanager_prompt},
        {"role": "user", "content": f"query question: {query_question}"}
      ]

      llm = self.get_llm()
      ai_msg = llm.invoke(messages)
      response = ai_msg.content

      print(colored(f"Datamanager 👨‍💻: {response}", 'yellow'))
      self.update_state("datamanager_response", response)
      return self.state
    
class WebSearcherAgent(Agent):
  def invoke(self, query_question, prompt = websearcher_prompt_template, feedback = None):

    websearcher_prompt = prompt.format()

    messages = [
      {"role": "system", "content": websearcher_prompt},
      {"role": "user", "content": f"query question: {query_question}"}
    ]

    llm = self.get_llm()
    ai_msg = llm.invoke(messages)
    response = ai_msg.content

    print(colored(f"WebSearcher 🧭: {response}", 'blue'))
    self.update_state("searcher_response", response)
    return self.state
  
class DatabaseReviewerAgent(Agent):
    def invoke(self, query_question, prompt=dbreviewer_prompt_template, previous_report = None):
      dataquery = str(previous_report[-1].content)

      final_prompt = prompt.format(
        dataquery = dataquery
      )
      # final_prompt = prompt

      messages = [
      {"role": "system", "content": final_prompt},
      {"role": "user", "content": f"query question: {query_question}"}
    ]

      llm = self.get_llm(json_model=False)
      ai_msg = llm.invoke(messages)
      response = ai_msg.content
      # response = previous_report_value.content
      print(colored(f"Reviewer : {response}", 'blue'))
      self.update_state("reviewer_response", response)
      return self.state


class WebReviewerAgent(Agent):
  def invoke(self, query_question, prompt=webreviewer_prompt_template, previous_report=None):
    searchquery = str(previous_report[-1].content)

    final_prompt = prompt.format(
      searchquery=searchquery
    )
    # final_prompt = prompt

    messages = [
      {"role": "system", "content": final_prompt},
      {"role": "user", "content": f"query question: {query_question}"}
    ]

    llm = self.get_llm(json_model=False)
    ai_msg = llm.invoke(messages)
    response = ai_msg.content
    # response = previous_report_value.content
    print(colored(f"Reviewer : {response}", 'blue'))
    self.update_state("reviewer_response", response)
    return self.state

class OCRReviewerAgent(Agent):
  def invoke(self, query_question, prompt=ocrreviewer_prompt_template, previous_report=None):
    ocr_result = str(previous_report[-1].content)

    final_prompt = prompt.format(
      ocr_result=ocr_result
    )
    # final_prompt = prompt

    messages = [
      {"role": "system", "content": final_prompt},
      {"role": "user", "content": f"query question: {query_question}"}
    ]

    llm = self.get_llm(json_model=False)
    ai_msg = llm.invoke(messages)
    response = ai_msg.content
    # response = previous_report_value.content
    print(colored(f"OCR : {response}", 'blue'))
    self.update_state("reviewer_response", response)
    return self.state


class ConversationalAgent(Agent):
  def invoke(self, query_question, prompt=conversational_prompt_template, previous_report=None):

    messages = [
      {"role": "system", "content": prompt},
      {"role": "user", "content": f"query question: {query_question}"}
    ]

    llm = self.get_llm(json_model=False)
    ai_msg = llm.invoke(messages)
    response = ai_msg.content
    # response = previous_report_value.content
    print(colored(f"Reviewer : {response}", 'blue'))
    self.update_state("reviewer_response", response)
    return self.state

class EndNodeAgent(Agent):
  def invoke(self):
    self.update_state("end_chain", "end_chain")
    return self.state