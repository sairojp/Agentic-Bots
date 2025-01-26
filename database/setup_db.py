import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, Enum, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    address = Column(String, nullable=True)

    orders = relationship("Order", back_populates="user")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    price = Column(Float)
    category = Column(String)
    stock_quantity = Column(Integer, default=0)

    order_items = relationship("OrderItem", back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    order_date = Column(DateTime, default=func.now())
    status = Column(Enum("Placed", "Packaged", "Shipped", "Delivered", "Cancelled", name="order_status"), default="Placed")
    total_amount = Column(Float)

    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    price = Column(Float)

    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")


DATABASE_URL = "sqlite:///test_database.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()

    # Adding example users
    users = [
        User(name="Alice", email="alice@example.com", address="123 Main St"),
        User(name="Bob", email="bob@example.com", address="456 Oak St"),
        User(name="Charlie", email="charlie@example.com", address="789 Pine St"),
        User(name="David", email="david@example.com", address="101 Maple Ave"),
        User(name="Eva", email="eva@example.com", address="202 Birch Rd"),
        User(name="Frank", email="frank@example.com", address="303 Cedar Blvd"),
    ]
    session.add_all(users)
    session.commit()

    # Adding example products (vehicle parts)
    products = [
        Product(name="Brake Pads", description="High-quality brake pads for cars", price=50.0, category="Car Parts", stock_quantity=100),
        Product(name="Air Filter", description="Air filter for bikes", price=15.0, category="Bike Parts", stock_quantity=150),
        Product(name="Oil Change Kit", description="Oil change kit for vehicles", price=25.0, category="Vehicle Servicing", stock_quantity=200),
        Product(name="Car Battery", description="12V car battery", price=80.0, category="Car Parts", stock_quantity=50),
        Product(name="Motorcycle Helmet", description="Full-face motorcycle helmet", price=120.0, category="Bike Accessories", stock_quantity=75),
        Product(name="Chain Lube", description="Chain lubricant for bikes", price=8.0, category="Bike Accessories", stock_quantity=300),
        Product(name="Tire Pressure Gauge", description="Digital tire pressure gauge", price=18.0, category="Vehicle Tools", stock_quantity=120),
        Product(name="Spark Plugs", description="Spark plugs for motorcycles", price=12.5, category="Bike Parts", stock_quantity=180),
        Product(name="Wrench Set", description="12-piece wrench set for cars", price=35.0, category="Vehicle Tools", stock_quantity=60),
    ]
    session.add_all(products)
    session.commit()

    # Adding example orders
    orders = [
        Order(user_id=1, total_amount=65.0, status="Placed"),
        Order(user_id=2, total_amount=40.0, status="Shipped"),
        Order(user_id=3, total_amount=190.0, status="Delivered"),
        Order(user_id=4, total_amount=150.0, status="Cancelled"),
        Order(user_id=5, total_amount=245.0, status="Packaged"),
        Order(user_id=6, total_amount=85.0, status="Shipped"),
    ]
    session.add_all(orders)
    session.commit()

    # Adding order items for each order
    order_items = [
        # Order 1 (Alice)
        OrderItem(order_id=1, product_id=1, quantity=1, price=50.0),
        OrderItem(order_id=1, product_id=3, quantity=1, price=15.0),

        # Order 2 (Bob)
        OrderItem(order_id=2, product_id=2, quantity=2, price=15.0),

        # Order 3 (Charlie)
        OrderItem(order_id=3, product_id=4, quantity=1, price=80.0),
        OrderItem(order_id=3, product_id=6, quantity=1, price=120.0),

        # Order 4 (David)
        OrderItem(order_id=4, product_id=5, quantity=1, price=120.0),
        OrderItem(order_id=4, product_id=8, quantity=1, price=18.0),

        # Order 5 (Eva)
        OrderItem(order_id=5, product_id=3, quantity=2, price=25.0),
        OrderItem(order_id=5, product_id=7, quantity=1, price=35.0),

        # Order 6 (Frank)
        OrderItem(order_id=6, product_id=9, quantity=1, price=12.5),
        OrderItem(order_id=6, product_id=2, quantity=3, price=15.0),
    ]
    session.add_all(order_items)
    session.commit()

    session.close()
    print("Database successfully created and populated with more example data.")


if __name__ == "__main__":
    if not os.path.exists("test_database.db"):
        init_db()
    else:
        print("The database 'test_database.db' already exists.")
