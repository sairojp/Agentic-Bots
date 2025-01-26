import os
from termcolor import colored
import json 
from states.state import AgentGraphState
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.setup_db import Order

DATABASE_URL = "sqlite:///test_database.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_order_status(state:AgentGraphState,dataquery):
  
  order_data = dataquery[-1].content
  order_data = json.loads(order_data)
  order_id = order_data.get("order_id")
  try:
    session = SessionLocal()
    order = session.query(Order).filter(Order.id == order_id).first()

    if order :
      order_details = {
        "order_id": order.id,
        "order_status": order.status,
        "order_date": order.order_date.isoformat() 
      }

      order_details_json = json.dumps(order_details)
      print(colored(f"DB 🧑🏼‍💻: {order_details_json}", 'green'))
      session.close()
      state = {**state, "dbquery_response": order_details_json}
      return state 
    else:
      session.close()
      return {**state, "dbquery_response": f"No user found"}

  except :
    session.close()
    return {**state, "dbquery_response": f"Unexpected error occurred"}

