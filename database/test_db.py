from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from setup_db import User, Order

DATABASE_URL = "sqlite:///test_database.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Open a session
session = SessionLocal()

# Query all users and their orders
users = session.query(User).all()

for user in users:
    print(f"User: {user.name}")
    for order in user.orders:
        print(f"  Order ID: {order.id} - Status: {order.status} - Total Amount: ${order.total_amount}")

# Close the session
session.close()
