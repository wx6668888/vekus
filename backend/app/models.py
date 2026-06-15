from sqlalchemy import Integer, String, Float, Text, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False, default="123456")
    name: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    phone: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="sales")
    factory_name: Mapped[str] = mapped_column(String(128), nullable=False, default="Vekus")


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    contact_name: Mapped[str] = mapped_column(String(64), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)
    email: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    address: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    tier: Mapped[str] = mapped_column(String(8), nullable=False, default="B")
    tags: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    assigned_sales: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    ext_info: Mapped[str] = mapped_column(Text, nullable=False, default="")  # JSON: Qichacha extra info
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")


class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quote_no: Mapped[str] = mapped_column(String(64), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    customer_id: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    material: Mapped[str] = mapped_column(String(64), nullable=False, default="镀锌板")
    thickness: Mapped[float] = mapped_column(Float, nullable=False, default=1.5)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    surface: Mapped[str] = mapped_column(String(64), nullable=False, default="喷粉")
    delivery_days: Mapped[int] = mapped_column(Integer, nullable=False, default=7)
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # Recognized data (stored as JSON string)
    recognized_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    overrides_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    coefficients_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")

    # Calculated results
    total_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    total_price: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    profit_margin: Mapped[float] = mapped_column(Float, nullable=False, default=0)

    # Status: draft, sent, viewed, won, lost
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")


class PricingParameter(Base):
    __tablename__ = "pricing_parameters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    value: Mapped[str] = mapped_column(String(64), nullable=False)
    unit: Mapped[str] = mapped_column(String(32), nullable=False)
    enabled: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    listing_type: Mapped[str] = mapped_column(String(16), nullable=False, default="sell")  # sell / buy
    category: Mapped[str] = mapped_column(String(32), nullable=False, default="板材")  # 板材/型材/余料/设备/加工服务
    material: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    thickness: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    dimensions: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    surface: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    unit: Mapped[str] = mapped_column(String(16), nullable=False, default="件")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    images_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    location: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    contact_phone: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")  # active / sold / closed
    views_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(32), nullable=False, default="user_chat")  # system / customer_service / user_chat / order
    title: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    participants_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")  # [user_id, user_id]
    last_message: Mapped[str] = mapped_column(Text, nullable=False, default="")
    last_message_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(Integer, nullable=False)
    sender_id: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    message_type: Mapped[str] = mapped_column(String(16), nullable=False, default="text")  # text / image / system
    is_read: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")


class PaymentOrder(Base):
    __tablename__ = "payment_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    order_no: Mapped[str] = mapped_column(String(64), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    plan_name: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    payment_method: Mapped[str] = mapped_column(String(16), nullable=False, default="wechat")
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")  # pending / paid / expired
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    paid_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")


class PointsTransaction(Base):
    __tablename__ = "points_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    type: Mapped[str] = mapped_column(String(16), nullable=False, default="charge")  # charge / deduct / expire
    description: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    related_id: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")
