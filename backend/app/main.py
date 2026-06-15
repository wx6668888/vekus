import hashlib
import json
import random
import string
import tempfile
import time as time_module
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import sessionmaker

from .models import Base, Conversation, Customer, Listing, Message, PaymentOrder, PointsTransaction, PricingParameter, Quote, User

DATABASE_URL = "sqlite:///./vekus.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

app = FastAPI(title="Vekus API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 鈹€鈹€ Pydantic Schemas 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

class LoginBody(BaseModel):
    phone: str
    password: str

class RegisterBody(BaseModel):
    name: str
    phone: str
    password: str
    role: str = "sales"  # boss / sales
    factory_name: str = ""
    boss_id: int = 0


class SaveQuoteBody(BaseModel):
    customer_name: str = ""
    material: str = "galvanized"
    thickness: float = 1.5
    quantity: int = 100
    surface: str = "powder"
    delivery_days: int = 7
    note: str = ""
    recognized: Optional[dict] = None
    manual_overrides: Optional[dict] = None
    coefficients: Optional[dict] = None


class SaveSettingBody(BaseModel):
    category: str
    name: str
    value: str
    unit: str


# 鈹€鈹€ Helpers 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def generate_quote_no() -> str:
    date = datetime.now().strftime("%Y%m%d")
    seq = random.randint(1, 999)
    return f"QT-{date}-{seq:03d}"


def default_recognized():
    return {
        "thickness": 1.5, "expandLength": 420, "expandWidth": 280,
        "cutLength": 2140, "bendCount": 6, "paintArea": 0.32,
        "weldPoints": 14, "weldLength": 0, "holes": {"plain": 8, "threaded": 4, "counterbored": 2},
    }


def default_coefficients():
    return {"tax": 1.06, "discount": 0.95, "packaging": 80, "profitRate": 0.28}


MATERIAL_PRICES = {"镀锌板": 8.5, "冷轧板": 7.2, "铝板": 18.0, "不锈钢": 22.0}
SURFACE_PRICES = {"喷粉": 2.8, "喷漆": 3.2, "电镀": 4.5, "钝化": 1.8, "无": 0}


def compute_quote_prices(material: str, thickness: float, quantity: int,
                          surface: str, recognized: dict, coefficients: dict) -> dict:
    mat_price = MATERIAL_PRICES.get(material, 8.5)
    surf_price = SURFACE_PRICES.get(surface, 0)
    profit_rate = coefficients.get("profitRate", 0.28)
    tax = coefficients.get("tax", 1.06)
    discount = coefficients.get("discount", 0.95)
    packaging = coefficients.get("packaging", 80)

    el = recognized.get("expandLength", 0)
    ew = recognized.get("expandWidth", 0)
    area = (el / 1000) * (ew / 1000)

    material_cost = area * thickness * 7.85 * mat_price * quantity
    cutting_cost = recognized.get("cutLength", 0) * 0.12
    bending_cost = recognized.get("bendCount", 0) * 1.5
    welding_cost = recognized.get("weldLength", 0) * 0.35 + recognized.get("weldPoints", 0) * 0.8
    surface_cost = recognized.get("paintArea", 0) * surf_price * quantity
    admin_cost = 50 + recognized.get("cutLength", 0) * 0.05

    total_cost = material_cost + cutting_cost + bending_cost + welding_cost + surface_cost + admin_cost
    profit = total_cost * profit_rate
    sub_total = total_cost + profit
    total_price = round(sub_total * tax * discount + packaging)
    unit_price = round(total_price / max(quantity, 1))
    profit_margin = round((profit / total_price) * 100, 2) if total_price > 0 else 0

    return {
        "total_cost": round(total_cost),
        "total_price": total_price,
        "unit_price": unit_price,
        "profit_margin": profit_margin,
    }


def serialize_user(row: User) -> dict:
    return {
        "id": str(row.id), "username": row.username, "name": row.name or row.username,
        "phone": row.phone, "role": row.role, "factoryName": row.factory_name,
    }


def serialize_quote(row: Quote) -> dict:
    recognized = json.loads(row.recognized_json) if row.recognized_json else default_recognized()
    overrides = json.loads(row.overrides_json) if row.overrides_json else {}
    coefficients = json.loads(row.coefficients_json) if row.coefficients_json else default_coefficients()
    return {
        "id": str(row.id),
        "quoteNo": row.quote_no,
        "customerName": row.customer_name,
        "customerId": row.customer_id,
        "material": row.material,
        "thickness": row.thickness,
        "quantity": row.quantity,
        "surface": row.surface,
        "deliveryDays": row.delivery_days,
        "note": row.note,
        "recognized": recognized,
        "manualOverrides": overrides,
        "coefficients": coefficients,
        "totalCost": row.total_cost,
        "totalPrice": row.total_price,
        "unitPrice": row.unit_price,
        "profitMargin": row.profit_margin,
        "status": row.status,
        "createdAt": row.created_at,
        "updatedAt": row.updated_at,
    }


def serialize_customer(row: Customer) -> dict:
    ext = {}
    if row.ext_info:
        try: ext = json.loads(row.ext_info)
        except: pass
    return {
        "id": str(row.id), "code": row.code, "name": row.name,
        "contactName": row.contact_name, "phone": row.phone,
        "email": row.email, "address": row.address,
        "tier": row.tier,
        "tags": row.tags.split(",") if row.tags else [],
        "status": row.status, "assignedSales": row.assigned_sales,
        "createdAt": row.created_at,
        "extInfo": ext,
    }


def serialize_setting(row: PricingParameter) -> dict:
    return {
        "id": row.id, "category": row.category, "name": row.name,
        "value": row.value, "unit": row.unit, "enabled": bool(row.enabled),
    }


# 鈹€鈹€ Seed Data 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.query(User).count() == 0:
            db.add_all([
                User(username="admin", password="123456", name="Admin", phone="13800000000", role="boss", factory_name="Vekus"),
                User(username="sales", password="123456", name="Zhang Wei", phone="13800000001", role="sales", factory_name="Vekus"),
                User(username="zhangwei", password="123456", name="Zhang Wei", phone="138****1234", role="sales", factory_name="Vekus"),
            ])
        if db.query(Customer).count() == 0:
            db.add_all([
                Customer(name="Huanan Precision", contact_name="Mr Zhang", phone="138****1234", tier="A", tags="VIP", assigned_sales="Zhang Wei"),
                Customer(name="DeepBlue Mech", contact_name="Mr Li", phone="139****5678", tier="B", tags="", assigned_sales="Li Si"),
                Customer(name="Chenxing Equipment", contact_name="Mr Wang", phone="137****9012", tier="C", tags="new", assigned_sales="Zhang Wei"),
                Customer(name="Tiancheng Tech", contact_name="Mr Zhao", phone="136****3456", tier="A", tags="VIP", assigned_sales=""),
                Customer(name="Mingda Electronics", contact_name="Mr Zhou", phone="135****7890", tier="B", tags="", assigned_sales=""),
            ])
        if db.query(Quote).count() == 0:
            db.add_all([
                Quote(quote_no="QT-20260510-001", customer_name="Huanan Precision", material="galvanized", thickness=1.5, quantity=500, surface="powder", total_price=12480, status="won", created_at="2026-05-10T09:30:00Z", updated_at="2026-05-10T09:30:00Z"),
                Quote(quote_no="QT-20260509-004", customer_name="DeepBlue Mech", material="cold_rolled", thickness=2.0, quantity=300, surface="paint", total_price=8650, status="sent", created_at="2026-05-09T14:20:00Z", updated_at="2026-05-09T14:20:00Z"),
                Quote(quote_no="QT-20260508-011", customer_name="Chenxing Equipment", material="aluminum", thickness=3.0, quantity=200, surface="passivation", total_price=15200, status="lost", created_at="2026-05-08T11:45:00Z", updated_at="2026-05-08T11:45:00Z"),
                Quote(quote_no="QT-20260507-003", customer_name="Tiancheng Tech", material="stainless", thickness=1.2, quantity=100, surface="electroplating", total_price=9800, status="draft", created_at="2026-05-07T16:00:00Z", updated_at="2026-05-07T16:00:00Z"),
            ])
        if db.query(PricingParameter).count() == 0:
            db.add_all([
                PricingParameter(category="material", name="galvanized", value="8.5", unit="yuan/kg"),
                PricingParameter(category="material", name="cold_rolled", value="7.2", unit="yuan/kg"),
                PricingParameter(category="material", name="aluminum", value="18.0", unit="yuan/kg"),
                PricingParameter(category="material", name="stainless", value="22.0", unit="yuan/kg"),
                PricingParameter(category="surface", name="powder", value="2.8", unit="yuan/m2"),
                PricingParameter(category="surface", name="paint", value="3.2", unit="yuan/m2"),
                PricingParameter(category="surface", name="electroplating", value="4.5", unit="yuan/m2"),
                PricingParameter(category="weld", name="spot_weld", value="0.8", unit="yuan/point"),
                PricingParameter(category="weld", name="full_weld", value="0.35", unit="yuan/mm"),
                PricingParameter(category="bend", name="normal_bend", value="1.5", unit="yuan/time"),
                PricingParameter(category="bend", name="large_bend", value="2.0", unit="yuan/time"),
                PricingParameter(category="hole", name="plain_hole", value="0.5", unit="yuan/hole"),
                PricingParameter(category="hole", name="threaded_hole", value="1.2", unit="yuan/hole"),
                PricingParameter(category="hole", name="counterbored_hole", value="0.8", unit="yuan/hole"),
                PricingParameter(category="coefficient", name="tax_factor", value="1.06", unit="-"),
                PricingParameter(category="coefficient", name="default_profit_rate", value="0.28", unit="-"),
            ])
        if db.query(Listing).count() == 0:
            now = now_str()
            db.add_all([
                Listing(owner_user_id=1, title="1.5mm Galvanized Sheet Surplus 2000x1000", listing_type="sell", category="surplus", material="galvanized", thickness=1.5, dimensions="2000x1000mm", surface="powder", quantity=80, price=28, unit="sheet", description="Factory surplus galvanized sheets, 2000x1000x1.5mm, powder coated gray-white, 80 sheets.", location="Shenzhen", contact_phone="13800000001", status="active", created_at=now, updated_at=now),
                Listing(owner_user_id=1, title="SUS304 Stainless Steel Sheet 1.2mm", listing_type="sell", category="sheet", material="stainless", thickness=1.2, dimensions="2438x1219mm", surface="raw", quantity=200, price=185, unit="sheet", description="New SUS304 stainless steel sheets, standard 4x8ft, 2B finish.", location="Foshan", contact_phone="13800000001", status="active", created_at=now, updated_at=now),
                Listing(owner_user_id=2, title="Wanted: Cold Rolled Sheet 2.0mm Bulk", listing_type="buy", category="sheet", material="cold_rolled", thickness=2.0, dimensions="any", surface="any", quantity=500, price=35, unit="sheet", description="Long-term purchase of cold rolled sheets, cash payment, 500+ sheets/month.", location="Ningbo", contact_phone="13800000000", status="active", created_at=now, updated_at=now),
                Listing(owner_user_id=2, title="CNC Bending Processing Service", listing_type="sell", category="service", material="any", thickness=0, dimensions="max 3000mm", surface="any", quantity=1, price=5, unit="time", description="Professional CNC bending service, AMADA press brake, precision 0.1mm.", location="Suzhou", contact_phone="13800000002", status="active", created_at=now, updated_at=now),
                Listing(owner_user_id=1, title="3.0mm Aluminum Sheet Offcuts", listing_type="sell", category="surplus", material="aluminum", thickness=3.0, dimensions="various", surface="raw", quantity=150, price=12, unit="kg", description="Aluminum offcuts, 3.0mm, 5052/6061 mix, min 200x200.", location="Dongguan", contact_phone="13800000001", status="active", created_at=now, updated_at=now),
                Listing(owner_user_id=2, title="Used AMADA Press Brake 100T", listing_type="sell", category="equipment", material="", thickness=0, dimensions="", surface="", quantity=1, price=85000, unit="unit", description="Used AMADA RG-100 press brake, 100T, 2000mm, 2019 model, good condition.", location="Shanghai", contact_phone="13800000002", status="active", created_at=now, updated_at=now),
            ])
        if db.query(Conversation).count() == 0:
            now = now_str()
            db.add_all([
                Conversation(type="system", title="System Notifications", participants_json="[1]", last_message="Welcome to Vekus", last_message_at=now, created_at=now),
                Conversation(type="customer_service", title="Vekus Customer Service", participants_json="[1]", last_message="Hello, how can I help?", last_message_at=now, created_at=now),
                Conversation(type="user_chat", title="Mr Li (DeepBlue)", participants_json="[1, 2]", last_message="OK, I will take this batch", last_message_at=now, created_at=now),
            ])
        if db.query(Message).count() == 0:
            now = now_str()
            conv_sys = db.scalar(select(Conversation).where(Conversation.type == "system"))
            conv_cs = db.scalar(select(Conversation).where(Conversation.type == "customer_service"))
            conv_chat = db.scalar(select(Conversation).where(Conversation.type == "user_chat"))
            if conv_sys:
                db.add_all([
                    Message(conversation_id=conv_sys.id, sender_id=0, content="Welcome to Vekus AI Quoting Platform!", message_type="system", is_read=1, created_at="2026-06-01T09:00:00Z"),
                    Message(conversation_id=conv_sys.id, sender_id=0, content="Your free trial account has been activated with 3 free quotes.", message_type="system", is_read=0, created_at="2026-06-01T09:00:01Z"),
                    Message(conversation_id=conv_sys.id, sender_id=0, content="Your quote QT-20260510-001 has been viewed by the customer.", message_type="system", is_read=0, created_at="2026-06-05T14:30:00Z"),
                ])
            if conv_cs:
                db.add_all([
                    Message(conversation_id=conv_cs.id, sender_id=0, content="Hello, I am Vekus customer service AI assistant. How can I help you?", message_type="text", is_read=1, created_at="2026-06-03T10:00:00Z"),
                    Message(conversation_id=conv_cs.id, sender_id=1, content="Hi, how do I upload DWG drawings for quoting?", message_type="text", is_read=1, created_at="2026-06-03T10:01:00Z"),
                    Message(conversation_id=conv_cs.id, sender_id=0, content="On the quote workbench page, click the upload area and select your DWG file. The system will auto-detect drawing parameters. Supports DWG, DXF, STEP, PDF up to 10MB.", message_type="text", is_read=1, created_at="2026-06-03T10:02:00Z"),
                    Message(conversation_id=conv_cs.id, sender_id=1, content="Got it, thanks!", message_type="text", is_read=1, created_at="2026-06-03T10:03:00Z"),
                ])
            if conv_chat:
                db.add_all([
                    Message(conversation_id=conv_chat.id, sender_id=2, content="Hi, is the galvanized sheet surplus still available?", message_type="text", is_read=1, created_at="2026-06-06T15:00:00Z"),
                    Message(conversation_id=conv_chat.id, sender_id=1, content="Yes, all 80 sheets are still available.", message_type="text", is_read=1, created_at="2026-06-06T15:05:00Z"),
                    Message(conversation_id=conv_chat.id, sender_id=2, content="Can you discount? I need 50 sheets.", message_type="text", is_read=1, created_at="2026-06-06T15:06:00Z"),
                    Message(conversation_id=conv_chat.id, sender_id=1, content="For 50 sheets I can do 26 each, best price.", message_type="text", is_read=1, created_at="2026-06-06T15:08:00Z"),
                    Message(conversation_id=conv_chat.id, sender_id=2, content="OK, I will take this batch. How to pay?", message_type="text", is_read=0, created_at="2026-06-07T09:30:00Z"),
                ])
        db.commit()


# 鈹€鈹€ Auth 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

@app.post("/api/auth/login")
def login(body: LoginBody):
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.phone == body.phone))
        if not user:
            # Fallback: check username
            user = db.scalar(select(User).where(User.username == body.phone))
        if not user or user.password != body.password:
            raise HTTPException(401, "Invalid phone or password")
        return {
            "token": f"vekus-jwt-{user.id}-{random.randint(10000, 99999)}",
            "user": serialize_user(user),
        }


@app.post("/api/auth/register")
def register(body: RegisterBody):
    with SessionLocal() as db:
        existing = db.scalar(select(User).where((User.phone == body.phone) | (User.username == body.phone)))
        if existing:
            raise HTTPException(400, "手机号已注册")
        user = User(
            username=body.phone,
            password=body.password,
            name=body.name or body.phone,
            phone=body.phone,
            role=body.role,
            factory_name=body.factory_name or "",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return {
            "token": f"vekus-jwt-{user.id}-{random.randint(10000, 99999)}",
            "user": serialize_user(user),
        }

@app.get("/api/boss/sales")
def boss_sales(boss_id: int = 0):
    with SessionLocal() as db:
        users = db.scalars(select(User).where(User.role == "sales")).all()
        return [serialize_user(u) for u in users]


# ═══════════════════ Admin: User Management ═══════════════════

@app.get("/api/admin/users")
def admin_list_users():
    with SessionLocal() as db:
        rows = db.scalars(select(User).order_by(User.id.asc())).all()
        return [serialize_user(r) for r in rows]


class AdminUserBody(BaseModel):
    username: str = ""
    name: str = ""
    phone: str = ""
    password: str = "123456"
    role: str = "sales"
    factory_name: str = ""


@app.post("/api/admin/users")
def admin_create_user(body: AdminUserBody):
    with SessionLocal() as db:
        row = User(
            username=body.username or body.phone,
            password=body.password,
            name=body.name,
            phone=body.phone,
            role=body.role,
            factory_name=body.factory_name or "Vekus",
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return serialize_user(row)


@app.put("/api/admin/users/{user_id}")
def admin_update_user(user_id: int, data: dict):
    with SessionLocal() as db:
        row = db.get(User, user_id)
        if not row:
            raise HTTPException(404, "User not found")
        for field in ["name", "phone", "role", "factory_name"]:
            if field in data:
                setattr(row, field, data[field])
        if "password" in data and data["password"]:
            row.password = data["password"]
        db.commit()
        db.refresh(row)
        return serialize_user(row)


@app.delete("/api/admin/users/{user_id}")
def admin_delete_user(user_id: int):
    with SessionLocal() as db:
        row = db.get(User, user_id)
        if not row:
            raise HTTPException(404, "User not found")
        db.delete(row)
        db.commit()
        return {"ok": True}

@app.get("/api/profile")
def profile():
    return {
        "username": "sales", "name": "寮犱紵", "role": "sales",
        "phone": "400-888-9999", "free_query_count": 28,
        "factory_name": "Vekus",
    }


@app.get("/api/profile/stats")
def profile_stats():
    with SessionLocal() as db:
        total_quotes = db.query(Quote).count()
        won_quotes = db.query(Quote).where(Quote.status == "won").count()
        rate = round((won_quotes / total_quotes * 100) if total_quotes > 0 else 0, 1)
        return {
            "quotes": total_quotes,
            "won": won_quotes,
            "rate": rate,
        }


# 鈹€鈹€ AI / Scan 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

@app.post("/api/ai/scan")
async def scan_drawing(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    suffix = Path(file.filename or "upload").suffix or ".png"
    tmp_path = Path(tempfile.gettempdir()) / f"vekus_scan_{uuid.uuid4().hex}{suffix}"

    try:
        content = await file.read()
        tmp_path.write_bytes(content)

        # Use processor factory for recognition
        from .processors import create_processor
        processor = create_processor(tmp_path, file.filename or "unknown")
        result = processor.process(tmp_path, file.filename or "unknown")

        if result.status == "failed":
            raise HTTPException(500, f"AI识别失败: {result.error}")

        payload = result.quote_payload
        all_zero = (payload.thickness == 0 and payload.expand_length == 0 and
                    payload.expand_width == 0 and payload.cut_length == 0)
        if all_zero:
            raise HTTPException(500, "AI识别失败: 模型返回空结果，请尝试更清晰的图纸图片")

        # Generate preview image for 3D/DXF files
        preview_image = ""
        ext = suffix.lower()
        try:
            from .processors.renderer import render_3d_to_png, render_dxf_to_png
            if ext in ('.step', '.stp', '.iges', '.igs', '.stl', '.obj'):
                preview_image = render_3d_to_png(tmp_path)
            elif ext == '.dxf':
                preview_image = render_dxf_to_png(tmp_path)
        except Exception:
            pass

        response = payload.to_dict()
        response["previewImage"] = preview_image
        response["confidence"] = result.confidence
        response["detections"] = [{"label": d.label, "value": d.value, "confidence": d.confidence} for d in result.detections]
        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"AI识别异常: {str(e)[:200]}")

    finally:
        # Clean up temp file
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


# 鈹€鈹€ AI Customer Service 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

class ChatBody(BaseModel):
    question: str = ""
    image: Optional[str] = None  # base64 encoded image

@app.post("/api/ai/customer-service")
def customer_service(body: ChatBody):
    """AI-powered customer service with knowledge base. Supports images via vision model."""
    from .knowledge_base import DEEPSEEK_API_KEY, DEEPSEEK_API_BASE, DEEPSEEK_MODEL, SYSTEM_PROMPT
    import traceback, os

    if DEEPSEEK_API_KEY:
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            }

            # Build messages
            if body.image:
                # For vision requests, use multimodal format
                user_content = [
                    {"type": "text", "text": body.question or "请分析这张图片，提取其中的钣金零件参数、尺寸、材料等信息"},
                    {"type": "image_url", "image_url": {"url": body.image}},
                ]
                model = os.getenv("VEKUS_AI_MODEL", DEEPSEEK_MODEL)  # Use vision-capable model
                max_tokens = 1000
                timeout = 90
            else:
                user_content = body.question
                model = DEEPSEEK_MODEL
                max_tokens = 800
                timeout = 30

            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7,
            }

            resp = requests.post(
                f"{DEEPSEEK_API_BASE}/chat/completions",
                headers=headers,
                json=payload,
                timeout=timeout,
            )
            if resp.status_code == 200:
                data = resp.json()
                answer = data["choices"][0]["message"]["content"]
                return {"answer": answer}
            else:
                # Log the error for debugging
                error_detail = resp.text[:300] if resp.text else "unknown"
                print(f"[AI] API error {resp.status_code}: {error_detail}")
                if body.image:
                    return {"answer": "抱歉，当前 AI 模型暂不支持图片识别。请将图纸上传到「报价页面」使用专用识图功能，或在此输入文字问题。"}
        except Exception as e:
            traceback.print_exc()
            print(f"[AI] Exception: {e}")
            # Fall through to local KB

    # Local fallback
    if body.image:
        return {"answer": "抱歉，AI 识图服务暂时不可用。请尝试：\n1. 在「报价页面」上传图纸进行识别报价\n2. 输入文字描述您的问题\n3. 联系管理员检查 API 配置"}
    return {"answer": f"我是Vekus智能助手小V！您可以问我关于报价流程、材料价格、交易广场、充值等问题。如需人工服务，请拨打400-888-9999。\n\n您的问题是：{body.question}\n\n建议尝试咨询：\n1. 如何上传图纸进行报价？\n2. 交易广场怎么发布信息？\n3. 如何给客户发送报价？"}


# 鈹€鈹€ Dashboard 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

@app.get("/api/dashboard/summary")
def dashboard_summary():
    with SessionLocal() as db:
        total_quotes = db.query(Quote).count()
        total_customers = db.query(Customer).count()
        total_users = db.query(User).count()

        # Count quotes by status
        draft_quotes = db.query(Quote).where(Quote.status == "draft").count()
        sent_quotes = db.query(Quote).where(Quote.status == "sent").count()
        won_quotes = db.query(Quote).where(Quote.status == "won").count()
        viewed_quotes = db.query(Quote).where(Quote.status == "viewed").count()

        # Revenue calculations
        all_won = db.scalars(select(Quote).where(Quote.status == "won")).all()
        month_revenue = sum(q.total_price for q in all_won) if all_won else random.randint(80000, 250000)
        avg_deal = round(month_revenue / len(all_won)) if all_won else random.randint(8000, 20000)
        weekly_rev = round(month_revenue * random.uniform(0.22, 0.28))

        # Customer growth mock (last 6 months)
        months = ["1月", "2月", "3月", "4月", "5月", "6月"]
        customer_growth = [{"month": m, "count": total_customers + random.randint(-20, 30) - i * random.randint(3, 10)} for i, m in enumerate(reversed(months))]
        for g in customer_growth:
            g["count"] = max(g["count"], 5)

        # Recent activity
        recent_activity = [
            {"id": 1, "type": "quote", "text": "新报价单 QT-20260615-012 已发送给客户", "time": "10分钟前"},
            {"id": 2, "type": "deal", "text": "QT-20260614-008 已确认成交，金额 ¥18,500", "time": "1小时前"},
            {"id": 3, "type": "customer", "text": "新客户「华星精密制造」已建档", "time": "2小时前"},
            {"id": 4, "type": "quote", "text": "QT-20260615-010 图纸识别完成，待确认", "time": "3小时前"},
            {"id": 5, "type": "system", "text": "系统自动备份完成，vekus.db 已备份", "time": "4小时前"},
        ]

        return {
            "today_scans": random.randint(80, 160),
            "today_new_customers": random.randint(3, 12),
            "pending_quotes": random.randint(15, 40),
            "weekly_revenue": weekly_rev,
            "month_won_deals": won_quotes + random.randint(3, 10),
            "won_rate": round(random.uniform(0.30, 0.42), 3),
            "month_revenue": month_revenue,
            "avg_deal_size": avg_deal,
            "customer_count": total_customers,
            "active_quotes": draft_quotes + sent_quotes,
            "total_quotes": total_quotes,
            "sent_quotes": sent_quotes,
            "viewed_quotes": viewed_quotes,
            "customer_growth": customer_growth,
            "recent_activity": recent_activity,
        }


# 鈹€鈹€ Customers 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

@app.get("/api/customers")
def customers():
    with SessionLocal() as db:
        rows = db.scalars(select(Customer)).all()
        return [serialize_customer(r) for r in rows]


@app.get("/api/customers/search")
def search_customers(q: str = ""):
    with SessionLocal() as db:
        if q:
            like = f"%{q}%"
            rows = db.scalars(select(Customer).where(
                Customer.name.like(like) | Customer.contact_name.like(like)
            )).all()
        else:
            rows = db.scalars(select(Customer)).all()
        return [serialize_customer(r) for r in rows]


@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: int):
    with SessionLocal() as db:
        row = db.get(Customer, customer_id)
        if not row:
            raise HTTPException(404, "Customer not found")
        return serialize_customer(row)


@app.post("/api/customers")
def create_customer(data: dict):
    with SessionLocal() as db:
        row = Customer(
            name=data.get("name", ""),
            contact_name=data.get("contactName", ""),
            phone=data.get("phone", ""),
            email=data.get("email", ""),
            address=data.get("address", ""),
            tier=data.get("tier", "B"),
            tags=",".join(data.get("tags", [])),
            status=data.get("status", "active"),
            assigned_sales=data.get("assignedSales", ""),
            ext_info=json.dumps(data.get("extInfo", {}), ensure_ascii=False),
            code=data.get("code", f"C{random.randint(1000,9999)}"),
            created_at=now_str(),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return serialize_customer(row)


# 鈹€鈹€ Quotes 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

@app.get("/api/quotes")
def quotes(customer: str = "", status: str = "", page: int = 1):
    with SessionLocal() as db:
        stmt = select(Quote).order_by(Quote.id.desc())
        if customer:
            stmt = stmt.where(Quote.customer_name.like(f"%{customer}%"))
        if status:
            stmt = stmt.where(Quote.status == status)
        rows = db.scalars(stmt).all()
        return [serialize_quote(r) for r in rows]


@app.get("/api/quotes/{quote_id}")
def get_quote(quote_id: int):
    with SessionLocal() as db:
        row = db.get(Quote, quote_id)
        if not row:
            raise HTTPException(404, "Quote not found")
        return serialize_quote(row)


@app.post("/api/quotes")
def create_quote(body: SaveQuoteBody):
    with SessionLocal() as db:
        now = now_str()
        recognized = body.recognized or default_recognized()
        coefficients = body.coefficients or default_coefficients()
        prices = compute_quote_prices(
            body.material, body.thickness, body.quantity,
            body.surface, recognized, coefficients,
        )
        row = Quote(
            quote_no=generate_quote_no(),
            customer_name=body.customer_name,
            material=body.material,
            thickness=body.thickness,
            quantity=body.quantity,
            surface=body.surface,
            delivery_days=body.delivery_days,
            note=body.note,
            recognized_json=json.dumps(recognized, ensure_ascii=False),
            overrides_json=json.dumps(body.manual_overrides or {}, ensure_ascii=False),
            coefficients_json=json.dumps(coefficients, ensure_ascii=False),
            total_cost=prices["total_cost"],
            total_price=prices["total_price"],
            unit_price=prices["unit_price"],
            profit_margin=prices["profit_margin"],
            status="draft",
            created_at=now,
            updated_at=now,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return serialize_quote(row)


@app.put("/api/quotes/{quote_id}")
def update_quote(quote_id: int, body: SaveQuoteBody):
    with SessionLocal() as db:
        row = db.get(Quote, quote_id)
        if not row:
            raise HTTPException(404, "Quote not found")
        row.customer_name = body.customer_name
        row.material = body.material
        row.thickness = body.thickness
        row.quantity = body.quantity
        row.surface = body.surface
        row.delivery_days = body.delivery_days
        row.note = body.note
        if body.recognized is not None:
            row.recognized_json = json.dumps(body.recognized, ensure_ascii=False)
        if body.manual_overrides is not None:
            row.overrides_json = json.dumps(body.manual_overrides, ensure_ascii=False)
        if body.coefficients is not None:
            row.coefficients_json = json.dumps(body.coefficients, ensure_ascii=False)
        # Recompute prices
        recognized_raw = json.loads(row.recognized_json) if row.recognized_json else default_recognized()
        coefficients_raw = json.loads(row.coefficients_json) if row.coefficients_json else default_coefficients()
        prices = compute_quote_prices(
            row.material, row.thickness, row.quantity,
            row.surface, recognized_raw, coefficients_raw,
        )
        row.total_cost = prices["total_cost"]
        row.total_price = prices["total_price"]
        row.unit_price = prices["unit_price"]
        row.profit_margin = prices["profit_margin"]
        row.updated_at = now_str()
        db.commit()
        db.refresh(row)
        return serialize_quote(row)


@app.patch("/api/quotes/{quote_id}/status")
def update_quote_status(quote_id: int, body: dict):
    with SessionLocal() as db:
        row = db.get(Quote, quote_id)
        if not row:
            raise HTTPException(404, "Quote not found")
        row.status = body.get("status", row.status)
        row.updated_at = now_str()
        db.commit()
        db.refresh(row)
        return {"ok": True}


@app.delete("/api/quotes/{quote_id}")
def delete_quote(quote_id: int):
    with SessionLocal() as db:
        row = db.get(Quote, quote_id)
        if not row:
            raise HTTPException(404, "Quote not found")
        db.delete(row)
        db.commit()
    return {"ok": True}


# 鈹€鈹€ Settings (Pricing Parameters) 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

@app.get("/api/settings")
def settings(category: str = ""):
    with SessionLocal() as db:
        stmt = select(PricingParameter)
        if category:
            stmt = stmt.where(PricingParameter.category == category)
        rows = db.scalars(stmt).all()
        return [serialize_setting(r) for r in rows]


@app.post("/api/settings")
def create_setting(body: SaveSettingBody):
    with SessionLocal() as db:
        row = PricingParameter(category=body.category, name=body.name, value=body.value, unit=body.unit)
        db.add(row)
        db.commit()
        db.refresh(row)
        return serialize_setting(row)


@app.delete("/api/settings/{setting_id}")
def delete_setting(setting_id: int):
    with SessionLocal() as db:
        row = db.get(PricingParameter, setting_id)
        if not row:
            raise HTTPException(404, "Parameter not found")
        db.delete(row)
        db.commit()
    return {"ok": True}


# 鈹€鈹€ Marketplace 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def serialize_listing(row: Listing) -> dict:
    return {
        "id": str(row.id),
        "ownerUserId": row.owner_user_id,
        "title": row.title,
        "listingType": row.listing_type,
        "category": row.category,
        "material": row.material,
        "thickness": row.thickness,
        "dimensions": row.dimensions,
        "surface": row.surface,
        "quantity": row.quantity,
        "price": row.price,
        "unit": row.unit,
        "description": row.description,
        "images": json.loads(row.images_json) if row.images_json else [],
        "location": row.location,
        "contactPhone": row.contact_phone,
        "status": row.status,
        "viewsCount": row.views_count,
        "createdAt": row.created_at,
        "updatedAt": row.updated_at,
    }


@app.get("/api/marketplace/listings")
def marketplace_listings(category: str = "", listing_type: str = "", keyword: str = "", page: int = 1):
    with SessionLocal() as db:
        stmt = select(Listing).where(Listing.status == "active").order_by(Listing.id.desc())
        if category:
            stmt = stmt.where(Listing.category == category)
        if listing_type:
            stmt = stmt.where(Listing.listing_type == listing_type)
        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(Listing.title.like(like) | Listing.description.like(like) | Listing.material.like(like))
        rows = db.scalars(stmt).all()
        return [serialize_listing(r) for r in rows]


@app.get("/api/marketplace/my-listings")
def my_listings(owner_user_id: int = 0):
    with SessionLocal() as db:
        stmt = select(Listing).where(Listing.owner_user_id == owner_user_id).order_by(Listing.id.desc())
        rows = db.scalars(stmt).all()
        return [serialize_listing(r) for r in rows]


@app.get("/api/marketplace/listings/{listing_id}")
def get_listing(listing_id: int):
    with SessionLocal() as db:
        row = db.get(Listing, listing_id)
        if not row:
            raise HTTPException(404, "Product not found")
        row.views_count += 1
        db.commit()
        return serialize_listing(row)


@app.post("/api/marketplace/listings")
def create_listing(data: dict):
    with SessionLocal() as db:
        now = now_str()
        row = Listing(
            owner_user_id=data.get("ownerUserId", 0),
            title=data.get("title", ""),
            listing_type=data.get("listingType", "sell"),
            category=data.get("category", "鏉挎潗"),
            material=data.get("material", ""),
            thickness=float(data.get("thickness", 0)),
            dimensions=data.get("dimensions", ""),
            surface=data.get("surface", ""),
            quantity=int(data.get("quantity", 1)),
            price=float(data.get("price", 0)),
            unit=data.get("unit", "pcs"),
            description=data.get("description", ""),
            images_json=json.dumps(data.get("images", []), ensure_ascii=False),
            location=data.get("location", ""),
            contact_phone=data.get("contactPhone", ""),
            status="active",
            created_at=now,
            updated_at=now,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return serialize_listing(row)


@app.put("/api/marketplace/listings/{listing_id}")
def update_listing(listing_id: int, data: dict):
    with SessionLocal() as db:
        row = db.get(Listing, listing_id)
        if not row:
            raise HTTPException(404, "Product not found")
        for field in ["title", "listingType", "category", "material", "dimensions", "surface", "unit", "description", "location", "contactPhone", "status"]:
            if field in data:
                db_field = {"listingType": "listing_type", "contactPhone": "contact_phone"}.get(field, "".join("_" + c.lower() if c.isupper() else c for c in field).lstrip("_"))
                setattr(row, db_field, data[field])
        if "thickness" in data:
            row.thickness = float(data["thickness"])
        if "quantity" in data:
            row.quantity = int(data["quantity"])
        if "price" in data:
            row.price = float(data["price"])
        if "images" in data:
            row.images_json = json.dumps(data["images"], ensure_ascii=False)
        row.updated_at = now_str()
        db.commit()
        db.refresh(row)
        return serialize_listing(row)


@app.delete("/api/marketplace/listings/{listing_id}")
def delete_listing(listing_id: int):
    with SessionLocal() as db:
        row = db.get(Listing, listing_id)
        if not row:
            raise HTTPException(404, "Product not found")
        row.status = "closed"
        row.updated_at = now_str()
        db.commit()
    return {"ok": True}


# 鈹€鈹€ Messages 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def serialize_conversation(row: Conversation) -> dict:
    return {
        "id": str(row.id),
        "type": row.type,
        "title": row.title,
        "participants": json.loads(row.participants_json) if row.participants_json else [],
        "lastMessage": row.last_message,
        "lastMessageAt": row.last_message_at,
        "createdAt": row.created_at,
    }


def serialize_message(row: Message) -> dict:
    return {
        "id": str(row.id),
        "conversationId": str(row.conversation_id),
        "senderId": row.sender_id,
        "content": row.content,
        "messageType": row.message_type,
        "isRead": bool(row.is_read),
        "createdAt": row.created_at,
    }


@app.get("/api/messages/conversations")
def get_conversations(user_id: int = 0):
    with SessionLocal() as db:
        rows = db.scalars(
            select(Conversation).order_by(Conversation.id.desc())
        ).all()
        return [serialize_conversation(r) for r in rows]


@app.get("/api/messages/unread-count")
def unread_count(user_id: int = 0):
    with SessionLocal() as db:
        count = db.query(Message).where(Message.is_read == 0).count()
        return {"count": count}


@app.get("/api/messages/conversations/{conversation_id}")
def get_messages(conversation_id: int, limit: int = 100):
    with SessionLocal() as db:
        # Count total messages
        from sqlalchemy import func
        total = db.scalar(
            select(func.count()).select_from(Message).where(Message.conversation_id == conversation_id)
        )
        # Only fetch the last N messages
        if total and total > limit:
            rows = db.scalars(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.id.desc())
                .limit(limit)
            ).all()
            rows = list(reversed(rows))  # Back to ascending
        else:
            rows = db.scalars(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.id.asc())
            ).all()
        return [serialize_message(r) for r in rows]


@app.post("/api/messages/send")
def send_message(data: dict):
    with SessionLocal() as db:
        now = now_str()
        conversation_id = int(data.get("conversationId", 0))
        if not conversation_id:
            conv = Conversation(
                type=data.get("type", "user_chat"),
                title=data.get("title", "鑱婂ぉ"),
                participants_json=json.dumps(data.get("participants", [])),
                last_message=data.get("content", "")[:100],
                last_message_at=now,
                created_at=now,
            )
            db.add(conv)
            db.commit()
            db.refresh(conv)
            conversation_id = conv.id
        else:
            conv = db.get(Conversation, conversation_id)
            if conv:
                conv.last_message = data.get("content", "")[:100]
                conv.last_message_at = now
        msg = Message(
            conversation_id=conversation_id,
            sender_id=int(data.get("senderId", 0)),
            content=data.get("content", ""),
            message_type=data.get("messageType", "text"),
            is_read=0,
            created_at=now,
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return serialize_message(msg)


@app.post("/api/messages/read/{conversation_id}")
def mark_read(conversation_id: int, body: dict):
    with SessionLocal() as db:
        db.query(Message).where(
            Message.conversation_id == conversation_id, Message.is_read == 0
        ).update({"is_read": 1})
        db.commit()
    return {"ok": True}


# 鈹€鈹€ Payment 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

PRICING_PLANS = [
    {"id": "free", "name": "Free Trial", "price": 0, "points": 3, "description": "3 free quotes for trial"},
    {"id": "basic", "name": "Basic Pack", "price": 99, "points": 50, "description": "50 quotes, 1.98 yuan each"},
    {"id": "pro", "name": "Pro Pack", "price": 199, "points": 150, "description": "150 quotes, 1.33 yuan each"},
    {"id": "premium", "name": "Premium Pack", "price": 399, "points": 500, "description": "500 quotes, 0.80 yuan each"},
    {"id": "monthly", "name": "Monthly Unlimited", "price": 299, "points": -1, "description": "30 days unlimited quotes"},
]


@app.get("/api/payment/pricing")
def get_pricing():
    return PRICING_PLANS


@app.post("/api/payment/create-order")
def create_payment_order(data: dict):
    with SessionLocal() as db:
        plan_id = data.get("planId", "")
        plan = next((p for p in PRICING_PLANS if p["id"] == plan_id), None)
        if not plan:
            raise HTTPException(400, "Invalid pricing plan")
        now = now_str()
        order_no = f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
        row = PaymentOrder(
            user_id=int(data.get("userId", 0)),
            order_no=order_no,
            amount=plan["price"],
            points=plan["points"],
            plan_name=plan["name"],
            payment_method="wechat",
            status="pending",
            created_at=now,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return {
            "id": str(row.id),
            "orderNo": row.order_no,
            "amount": row.amount,
            "points": row.points,
            "planName": row.plan_name,
            "status": row.status,
            "createdAt": row.created_at,
        }


@app.post("/api/payment/complete")
def complete_payment(data: dict):
    """Complete a payment order and grant points. In production, this would be called after WeChat Pay verification."""
    order_no = data.get("orderNo", "")
    with SessionLocal() as db:
        order = db.scalar(select(PaymentOrder).where(PaymentOrder.order_no == order_no))
        if not order:
            raise HTTPException(404, "Order not found")
        if order.status != "pending":
            return {"ok": False, "message": "Order already processed"}
        now = now_str()
        order.status = "paid"
        order.paid_at = now
        # Grant points to user
        if order.points > 0:
            txn = PointsTransaction(
                user_id=order.user_id,
                amount=order.points,
                type="charge",
                description=f"璐拱{order.plan_name}",
                related_id=order.order_no,
                created_at=now,
            )
            db.add(txn)
        elif order.points == -1:
            # Monthly subscription
            txn = PointsTransaction(
                user_id=order.user_id,
                amount=9999,
                type="charge",
                description=f"璁㈤槄{order.plan_name}锛?0澶╋級",
                related_id=order.order_no,
                created_at=now,
            )
            db.add(txn)
        db.commit()
        return {"ok": True}


@app.get("/api/payment/transactions")
def payment_transactions(user_id: int = 0):
    with SessionLocal() as db:
        rows = db.scalars(
            select(PointsTransaction)
            .where(PointsTransaction.user_id == user_id)
            .order_by(PointsTransaction.id.desc())
        ).all()
        return [{
            "id": str(r.id),
            "userId": r.user_id,
            "amount": r.amount,
            "type": r.type,
            "description": r.description,
            "relatedId": r.related_id,
            "createdAt": r.created_at,
        } for r in rows]


@app.get("/api/payment/points")
def user_points(user_id: int = 0):
    with SessionLocal() as db:
        rows = db.scalars(
            select(PointsTransaction).where(PointsTransaction.user_id == user_id)
        ).all()
        balance = sum(r.amount for r in rows if r.type == "charge") - sum(r.amount for r in rows if r.type == "deduct")
        return {"balance": max(0, balance), "userId": user_id}


@app.post("/api/payment/deduct")
def deduct_points(data: dict):
    """Deduct points for a quote."""
    user_id = int(data.get("userId", 0))
    with SessionLocal() as db:
        rows = db.scalars(
            select(PointsTransaction).where(PointsTransaction.user_id == user_id)
        ).all()
        balance = sum(r.amount for r in rows if r.type == "charge") - sum(r.amount for r in rows if r.type == "deduct")
        if balance <= 0:
            raise HTTPException(402, "Insufficient points")
        now = now_str()
        txn = PointsTransaction(
            user_id=user_id,
            amount=-1,
            type="deduct",
            description=data.get("description", "鎶ヤ环鎵ｇ偣"),
            related_id=data.get("quoteId", ""),
            created_at=now,
        )
        db.add(txn)
        db.commit()
        return {"balance": balance - 1, "ok": True}


# 鈹€鈹€ Health 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

# ═══════════════════ Qichacha Company Search ═══════════════════

QICHACHA_KEY = "ed900f67edbb442597ddee5df1f5b308"
QICHACHA_SECRET = "ED9FBF5D7A713C5A9C69ED9A026B42B3"

@app.get("/api/qichacha/search")
def qichacha_search(searchKey: str = "", pageIndex: str = "1"):
    if not searchKey:
        raise HTTPException(400, "searchKey is required")
    try:
        import requests
        timespan = str(int(time_module.time()))
        token_raw = QICHACHA_KEY + timespan + QICHACHA_SECRET
        token = hashlib.md5(token_raw.encode()).hexdigest().upper()

        headers = {
            "Token": token,
            "Timespan": timespan,
        }
        params = {
            "key": QICHACHA_KEY,
            "searchKey": searchKey,
            "pageIndex": pageIndex,
        }
        resp = requests.get(
            "https://api.qichacha.com/FuzzySearch/GetList",
            headers=headers,
            params=params,
            timeout=15,
        )
        data = resp.json()
        if data.get("Status") == "200":
            return {
                "ok": True,
                "total": data["Paging"]["TotalRecords"],
                "pageSize": data["Paging"]["PageSize"],
                "pageIndex": int(pageIndex),
                "results": data.get("Result", []),
            }
        else:
            return {"ok": False, "message": data.get("Message", "查询失败"), "results": []}
    except Exception as e:
        return {"ok": False, "message": str(e)[:200], "results": []}


# ═══════════════════ Qichacha Risk Scan ═══════════════════

@app.get("/api/qichacha/risk-scan")
def qichacha_risk_scan(searchKey: str = "", customerId: int = 0):
    if not searchKey:
        raise HTTPException(400, "searchKey is required")

    # Deduct 20 points
    if customerId > 0:
        with SessionLocal() as db:
            now = now_str()
            txn = PointsTransaction(
                user_id=1,  # logged-in user
                amount=-20,
                type="deduct",
                description=f"客户风险排查: {searchKey}",
                related_id=str(customerId),
                created_at=now,
            )
            db.add(txn)
            db.commit()

    try:
        import requests
        timespan = str(int(time_module.time()))
        token_raw = QICHACHA_KEY + timespan + QICHACHA_SECRET
        token = hashlib.md5(token_raw.encode()).hexdigest().upper()

        headers = {"Token": token, "Timespan": timespan}
        params = {"key": QICHACHA_KEY, "searchKey": searchKey}
        resp = requests.get(
            "https://api.qichacha.com/RiskControl/Scan",
            headers=headers, params=params, timeout=30,
        )
        data = resp.json()
        if data.get("Status") == "200" and data.get("Result", {}).get("VerifyResult") == 1:
            return {"ok": True, "data": data["Result"]["Data"]}
        else:
            return {"ok": False, "message": data.get("Message", "未找到风险数据"), "data": None}
    except Exception as e:
        return {"ok": False, "message": str(e)[:200], "data": None}


# ═══════════════════ BOM 物料清单 ═══════════════════

from .models import BomItem

def serialize_bom(row: BomItem) -> dict:
    return {
        "id": str(row.id), "code": row.code, "name": row.name,
        "spec": row.spec, "material": row.material, "unit": row.unit,
        "unitWeight": row.unit_weight, "price": row.price,
        "category": row.category, "parentId": str(row.parent_id) if row.parent_id else "",
        "quantity": row.quantity, "level": row.level,
        "sortOrder": row.sort_order, "note": row.note,
        "version": row.version, "status": row.status,
        "createdAt": row.created_at,
    }

@app.get("/api/bom")
def bom_list(parent_id: int = 0):
    with SessionLocal() as db:
        if parent_id == 0:
            rows = db.scalars(select(BomItem).where(BomItem.parent_id == 0).order_by(BomItem.sort_order, BomItem.id)).all()
        else:
            rows = db.scalars(select(BomItem).where(BomItem.parent_id == parent_id).order_by(BomItem.sort_order, BomItem.id)).all()
        return [serialize_bom(r) for r in rows]

@app.get("/api/bom/tree")
def bom_tree():
    """Return full BOM tree."""
    with SessionLocal() as db:
        all_items = db.scalars(select(BomItem).order_by(BomItem.level, BomItem.sort_order, BomItem.id)).all()
        return [serialize_bom(r) for r in all_items]

@app.post("/api/bom")
def bom_create(data: dict):
    with SessionLocal() as db:
        row = BomItem(
            code=data.get("code", ""), name=data.get("name", ""),
            spec=data.get("spec", ""), material=data.get("material", ""),
            unit=data.get("unit", "件"), unit_weight=float(data.get("unitWeight", 0)),
            price=float(data.get("price", 0)), category=data.get("category", "零件"),
            parent_id=int(data.get("parentId", 0)), quantity=int(data.get("quantity", 1)),
            level=int(data.get("level", 0)), sort_order=int(data.get("sortOrder", 0)),
            note=data.get("note", ""), version=data.get("version", "1.0"),
            status=data.get("status", "active"), created_at=now_str(),
        )
        db.add(row); db.commit(); db.refresh(row)
        return serialize_bom(row)

@app.put("/api/bom/{item_id}")
def bom_update(item_id: int, data: dict):
    with SessionLocal() as db:
        row = db.get(BomItem, item_id)
        if not row: raise HTTPException(404, "Not found")
        for f in ["code","name","spec","material","unit","category","note","version","status"]:
            if f in data: setattr(row, f, data[f])
        for f in ["unitWeight","price","parentId","quantity","level","sortOrder"]:
            if f in data: setattr(row, f, float(data[f]) if f in ("unitWeight","price") else int(data[f]))
        db.commit(); db.refresh(row)
        return serialize_bom(row)

@app.delete("/api/bom/{item_id}")
def bom_delete(item_id: int):
    with SessionLocal() as db:
        row = db.get(BomItem, item_id)
        if not row: raise HTTPException(404, "Not found")
        # Also delete children
        children = db.scalars(select(BomItem).where(BomItem.parent_id == item_id)).all()
        for c in children: db.delete(c)
        db.delete(row); db.commit()
        return {"ok": True}


# ═══════════════════ Inventory ═══════════════════

from .models import InventoryItem, InventoryLog

def serialize_inv(row: InventoryItem) -> dict:
    return {"id":str(row.id),"bomItemId":str(row.bom_item_id),"code":row.code,"name":row.name,
            "spec":row.spec,"material":row.material,"unit":row.unit,"quantity":row.quantity,
            "safetyStock":row.safety_stock,"location":row.location,"status":row.status,"updatedAt":row.updated_at}

@app.get("/api/inventory")
def inventory_list():
    with SessionLocal() as db:
        rows = db.scalars(select(InventoryItem).order_by(InventoryItem.id.desc())).all()
        return [serialize_inv(r) for r in rows]

@app.post("/api/inventory")
def inventory_create(data: dict):
    with SessionLocal() as db:
        row = InventoryItem(bom_item_id=int(data.get("bomItemId",0)),code=data.get("code",""),
            name=data.get("name",""),spec=data.get("spec",""),material=data.get("material",""),
            unit=data.get("unit","件"),quantity=float(data.get("quantity",0)),
            safety_stock=float(data.get("safetyStock",0)),location=data.get("location",""),
            status="正常",updated_at=now_str())
        db.add(row); db.commit(); db.refresh(row)
        # Log
        db.add(InventoryLog(item_id=row.id,type="in",quantity=row.quantity,before_qty=0,
            after_qty=row.quantity,related_no="",operator="",note="初始入库",created_at=now_str()))
        db.commit()
        return serialize_inv(row)

@app.post("/api/inventory/{item_id}/transact")
def inventory_transact(item_id: int, data: dict):
    """入库/出库"""
    with SessionLocal() as db:
        row = db.get(InventoryItem, item_id)
        if not row: raise HTTPException(404,"Not found")
        t = data.get("type","in"); qty = float(data.get("quantity",0))
        before = row.quantity
        row.quantity = before + qty if t == "in" else before - qty
        row.status = "紧缺" if row.quantity <= row.safety_stock else "正常"
        row.updated_at = now_str()
        db.add(InventoryLog(item_id=item_id,type=t,quantity=abs(qty),before_qty=before,
            after_qty=row.quantity,related_no=data.get("relatedNo",""),
            operator=data.get("operator",""),note=data.get("note",""),created_at=now_str()))
        db.commit(); db.refresh(row)
        return serialize_inv(row)

@app.get("/api/inventory/{item_id}/logs")
def inventory_logs(item_id: int):
    with SessionLocal() as db:
        rows = db.scalars(select(InventoryLog).where(InventoryLog.item_id==item_id).order_by(InventoryLog.id.desc()).limit(50)).all()
        return [{"id":str(r.id),"itemId":r.item_id,"type":r.type,"quantity":r.quantity,
                 "beforeQty":r.before_qty,"afterQty":r.after_qty,"relatedNo":r.related_no,
                 "operator":r.operator,"note":r.note,"createdAt":r.created_at} for r in rows]

@app.delete("/api/inventory/{item_id}")
def inventory_delete(item_id: int):
    with SessionLocal() as db:
        row = db.get(InventoryItem, item_id)
        if row: db.delete(row); db.commit()
        return {"ok":True}


# ═══════════════════ Production Orders ═══════════════════

from .models import ProductionOrder

def serialize_prod(row: ProductionOrder) -> dict:
    return {"id":str(row.id),"orderNo":row.order_no,"bomItemId":str(row.bom_item_id),
            "productName":row.product_name,"quantity":row.quantity,"status":row.status,
            "priority":row.priority,"plannedStart":row.planned_start,"plannedEnd":row.planned_end,
            "actualStart":row.actual_start,"actualEnd":row.actual_end,"workshop":row.workshop,
            "assignedTo":row.assigned_to,"progress":row.progress,"note":row.note,
            "createdAt":row.created_at,"updatedAt":row.updated_at}

@app.get("/api/production")
def production_list(status: str = ""):
    with SessionLocal() as db:
        stmt = select(ProductionOrder).order_by(ProductionOrder.id.desc())
        if status: stmt = stmt.where(ProductionOrder.status == status)
        rows = db.scalars(stmt).all()
        return [serialize_prod(r) for r in rows]

@app.post("/api/production")
def production_create(data: dict):
    with SessionLocal() as db:
        no = f"MO-{datetime.now().strftime('%Y%m%d')}-{random.randint(100,999)}"
        row = ProductionOrder(order_no=no,bom_item_id=int(data.get("bomItemId",0)),
            product_name=data.get("productName",""),quantity=int(data.get("quantity",1)),
            status="draft",priority=data.get("priority","normal"),
            planned_start=data.get("plannedStart",""),planned_end=data.get("plannedEnd",""),
            workshop=data.get("workshop",""),assigned_to=data.get("assignedTo",""),
            progress=0,note=data.get("note",""),created_at=now_str(),updated_at=now_str())
        db.add(row); db.commit(); db.refresh(row)
        return serialize_prod(row)

@app.put("/api/production/{order_id}")
def production_update(order_id: int, data: dict):
    with SessionLocal() as db:
        row = db.get(ProductionOrder, order_id)
        if not row: raise HTTPException(404,"Not found")
        for f in ["status","priority","workshop","assignedTo","note","productName","plannedStart","plannedEnd"]:
            if f in data: setattr(row, f, data[f])
        if "quantity" in data: row.quantity = int(data["quantity"])
        if "progress" in data: row.progress = int(data["progress"])
        if data.get("status") == "running" and not row.actual_start: row.actual_start = now_str()
        if data.get("status") == "done" and not row.actual_end: row.actual_end = now_str(); row.progress = 100
        row.updated_at = now_str()
        db.commit(); db.refresh(row)
        return serialize_prod(row)

@app.delete("/api/production/{order_id}")
def production_delete(order_id: int):
    with SessionLocal() as db:
        row = db.get(ProductionOrder, order_id)
        if row: db.delete(row); db.commit()
        return {"ok":True}


# ═══════════════════ Suppliers ═══════════════════

from .models import Supplier

def serialize_sup(row: Supplier) -> dict:
    return {"id":str(row.id),"code":row.code,"name":row.name,"contactName":row.contact_name,
            "phone":row.phone,"email":row.email,"address":row.address,"category":row.category,
            "status":row.status,"createdAt":row.created_at}

@app.get("/api/suppliers")
def supplier_list():
    with SessionLocal() as db:
        rows = db.scalars(select(Supplier).order_by(Supplier.id.desc())).all()
        return [serialize_sup(r) for r in rows]

@app.post("/api/suppliers")
def supplier_create(data: dict):
    with SessionLocal() as db:
        row = Supplier(code=data.get("code",""),name=data.get("name",""),contact_name=data.get("contactName",""),
            phone=data.get("phone",""),email=data.get("email",""),address=data.get("address",""),
            category=data.get("category","材料"),status="active",created_at=now_str())
        db.add(row); db.commit(); db.refresh(row)
        return serialize_sup(row)

@app.put("/api/suppliers/{sup_id}")
def supplier_update(sup_id: int, data: dict):
    with SessionLocal() as db:
        row = db.get(Supplier, sup_id)
        if not row: raise HTTPException(404,"Not found")
        for f in ["name","contactName","phone","email","address","category","status"]:
            if f in data: setattr(row, f, data[f])
        db.commit(); db.refresh(row)
        return serialize_sup(row)

@app.delete("/api/suppliers/{sup_id}")
def supplier_delete(sup_id: int):
    with SessionLocal() as db:
        row = db.get(Supplier, sup_id)
        if row: db.delete(row); db.commit()
        return {"ok":True}


# ═══════════════════ Purchase Orders ═══════════════════

from .models import PurchaseOrder

def serialize_po(row: PurchaseOrder) -> dict:
    return {"id":str(row.id),"orderNo":row.order_no,"supplierId":str(row.supplier_id),
            "supplierName":row.supplier_name,"itemName":row.item_name,"spec":row.spec,
            "quantity":row.quantity,"unit":row.unit,"price":row.price,"totalAmount":row.total_amount,
            "status":row.status,"orderDate":row.order_date,"receiveDate":row.receive_date,
            "note":row.note,"createdAt":row.created_at}

@app.get("/api/purchases")
def purchase_list(status: str = ""):
    with SessionLocal() as db:
        stmt = select(PurchaseOrder).order_by(PurchaseOrder.id.desc())
        if status: stmt = stmt.where(PurchaseOrder.status == status)
        rows = db.scalars(stmt).all()
        return [serialize_po(r) for r in rows]

@app.post("/api/purchases")
def purchase_create(data: dict):
    with SessionLocal() as db:
        qty = float(data.get("quantity",1)); price = float(data.get("price",0))
        no = f"PO-{datetime.now().strftime('%Y%m%d')}-{random.randint(100,999)}"
        row = PurchaseOrder(order_no=no,supplier_id=int(data.get("supplierId",0)),
            supplier_name=data.get("supplierName",""),item_name=data.get("itemName",""),
            spec=data.get("spec",""),quantity=qty,unit=data.get("unit","件"),
            price=price,total_amount=round(qty*price,2),
            status="draft",order_date=data.get("orderDate",""),receive_date=data.get("receiveDate",""),
            note=data.get("note",""),created_at=now_str())
        db.add(row); db.commit(); db.refresh(row)
        return serialize_po(row)

@app.put("/api/purchases/{po_id}")
def purchase_update(po_id: int, data: dict):
    with SessionLocal() as db:
        row = db.get(PurchaseOrder, po_id)
        if not row: raise HTTPException(404,"Not found")
        for f in ["status","orderDate","receiveDate","note","supplierName"]:
            if f in data: setattr(row, f, data[f])
        if "quantity" in data: row.quantity = float(data["quantity"])
        if "price" in data: row.price = float(data["price"]); row.total_amount = round(row.quantity*row.price,2)
        # Auto-add to inventory on receive
        if data.get("status") == "received":
            with SessionLocal() as db2:
                inv = db2.scalar(select(InventoryItem).where(InventoryItem.name == row.item_name))
                if inv:
                    inv.quantity += row.quantity; inv.updated_at = now_str()
                    db2.add(InventoryLog(item_id=inv.id,type="in",quantity=row.quantity,before_qty=inv.quantity-row.quantity,
                        after_qty=inv.quantity,related_no=row.order_no,operator="",note=f"采购收货: {row.order_no}",created_at=now_str()))
                    db2.commit()
        db.commit(); db.refresh(row)
        return serialize_po(row)

@app.delete("/api/purchases/{po_id}")
def purchase_delete(po_id: int):
    with SessionLocal() as db:
        row = db.get(PurchaseOrder, po_id)
        if row: db.delete(row); db.commit()
        return {"ok":True}


# ═══════════════════ Quality ═══════════════════

from .models import QualityCheck

def serialize_qc(row: QualityCheck) -> dict:
    return {"id":str(row.id),"checkNo":row.check_no,"type":row.type,"relatedType":row.related_type,
            "relatedId":str(row.related_id),"itemName":row.item_name,"quantity":row.quantity,
            "passQty":row.pass_qty,"failQty":row.fail_qty,"result":row.result,
            "inspector":row.inspector,"checkDate":row.check_date,"defectDesc":row.defect_desc,
            "handle":row.handle,"note":row.note,"createdAt":row.created_at}

@app.get("/api/quality")
def quality_list(type: str = ""):
    with SessionLocal() as db:
        stmt = select(QualityCheck).order_by(QualityCheck.id.desc())
        if type: stmt = stmt.where(QualityCheck.type == type)
        rows = db.scalars(stmt).all()
        return [serialize_qc(r) for r in rows]

@app.post("/api/quality")
def quality_create(data: dict):
    with SessionLocal() as db:
        no = f"QC-{datetime.now().strftime('%Y%m%d')}-{random.randint(100,999)}"
        row = QualityCheck(check_no=no,type=data.get("type","incoming"),
            related_type=data.get("relatedType",""),related_id=int(data.get("relatedId",0)),
            item_name=data.get("itemName",""),quantity=int(data.get("quantity",1)),
            pass_qty=int(data.get("passQty",0)),fail_qty=int(data.get("failQty",0)),
            result=data.get("result","pass"),inspector=data.get("inspector",""),
            check_date=data.get("checkDate",""),defect_desc=data.get("defectDesc",""),
            handle=data.get("handle",""),note=data.get("note",""),created_at=now_str())
        db.add(row); db.commit(); db.refresh(row)
        return serialize_qc(row)

@app.put("/api/quality/{qc_id}")
def quality_update(qc_id: int, data: dict):
    with SessionLocal() as db:
        row = db.get(QualityCheck, qc_id)
        if not row: raise HTTPException(404,"Not found")
        for f in ["result","inspector","checkDate","defectDesc","handle","note","relatedType"]:
            if f in data: setattr(row, f, data[f])
        for f in ["quantity","passQty","failQty"]:
            if f in data: setattr(row, f, int(data[f]))
        db.commit(); db.refresh(row)
        return serialize_qc(row)

@app.delete("/api/quality/{qc_id}")
def quality_delete(qc_id: int):
    with SessionLocal() as db:
        row = db.get(QualityCheck, qc_id)
        if row: db.delete(row); db.commit()
        return {"ok":True}


# ═══════════════════ Approvals ═══════════════════

from .models import Approval

def serialize_approval(row: Approval) -> dict:
    return {"id":str(row.id),"approvalNo":row.approval_no,"entityType":row.entity_type,
            "entityId":row.entity_id,"entityTitle":row.entity_title,
            "applicant":row.applicant,"approver":row.approver,"status":row.status,
            "comment":row.comment,"createdAt":row.created_at,"updatedAt":row.updated_at}

@app.get("/api/approvals")
def approval_list(status: str = "", entity_type: str = ""):
    with SessionLocal() as db:
        stmt = select(Approval).order_by(Approval.id.desc())
        if status: stmt = stmt.where(Approval.status == status)
        if entity_type: stmt = stmt.where(Approval.entity_type == entity_type)
        rows = db.scalars(stmt).all()
        return [serialize_approval(r) for r in rows]

@app.post("/api/approvals")
def approval_create(data: dict):
    with SessionLocal() as db:
        no = f"AP-{datetime.now().strftime('%Y%m%d')}-{random.randint(100,999)}"
        row = Approval(approval_no=no,entity_type=data.get("entityType","quote"),
            entity_id=str(data.get("entityId","")),entity_title=data.get("entityTitle",""),
            applicant=data.get("applicant",""),approver=data.get("approver",""),
            status="pending",comment=data.get("comment",""),created_at=now_str(),updated_at=now_str())
        db.add(row); db.commit(); db.refresh(row)
        _audit(db, data.get("applicant",""),"approve","approval",str(row.id),f"提交审批: {row.entity_title}")
        return serialize_approval(row)

@app.put("/api/approvals/{ap_id}")
def approval_update(ap_id: int, data: dict):
    with SessionLocal() as db:
        row = db.get(Approval, ap_id)
        if not row: raise HTTPException(404,"Not found")
        old_status = row.status
        for f in ["status","comment","approver"]:
            if f in data: setattr(row, f, data[f])
        row.updated_at = now_str()
        db.commit(); db.refresh(row)
        if old_status != row.status:
            _audit(db, row.approver,"approve","approval",str(row.id),
                   f"{'通过' if row.status=='approved' else '驳回'}审批: {row.entity_title}")
        return serialize_approval(row)


# ═══════════════════ Audit Logs ═══════════════════

from .models import AuditLog

def _audit(db, user_name: str, action: str, target_type: str, target_id: str, detail: str):
    db.add(AuditLog(user_name=user_name,action=action,target_type=target_type,
        target_id=target_id,detail=detail,ip_address="",created_at=now_str()))
    db.commit()

@app.get("/api/audit-logs")
def audit_list(limit: int = 100):
    with SessionLocal() as db:
        rows = db.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(limit)).all()
        return [{"id":str(r.id),"userName":r.user_name,"action":r.action,
                 "targetType":r.target_type,"targetId":r.target_id,
                 "detail":r.detail,"ipAddress":r.ip_address,"createdAt":r.created_at} for r in rows]


# ═══════════════════ Document Management ═══════════════════

import shutil
DOC_STORAGE = Path(os.getenv("VEKUS_STORAGE_DIR", "storage/uploads"))
DOC_STORAGE.mkdir(parents=True, exist_ok=True)

# Simple doc registry using a JSON file
DOC_REGISTRY = DOC_STORAGE / "registry.json"

def _load_docs():
    if DOC_REGISTRY.exists():
        return json.loads(DOC_REGISTRY.read_text())
    return []

def _save_docs(docs):
    DOC_REGISTRY.write_text(json.dumps(docs, ensure_ascii=False, indent=2))

@app.get("/api/docs")
def docs_list():
    return _load_docs()

@app.post("/api/docs/upload")
async def docs_upload(file: UploadFile = File(...)):
    docs = _load_docs()
    doc_id = str(uuid.uuid4())[:8]
    ext = Path(file.filename).suffix if file.filename else ""
    saved_name = f"{doc_id}{ext}"
    saved_path = DOC_STORAGE / saved_name
    with open(saved_path, "wb") as f:
        content = await file.read()
        f.write(content)
    doc = {
        "id": doc_id, "fileName": file.filename, "fileType": ext.lstrip("."),
        "fileSize": len(content), "customerName": "", "version": "1.0",
        "createdAt": now_str(), "path": str(saved_path),
    }
    docs.insert(0, doc)
    _save_docs(docs)
    return doc

@app.get("/api/files/{doc_id}/download")
def docs_download(doc_id: str):
    docs = _load_docs()
    doc = next((d for d in docs if d["id"] == doc_id), None)
    if not doc: raise HTTPException(404, "Not found")
    from fastapi.responses import FileResponse
    return FileResponse(doc["path"], filename=doc["fileName"])

@app.delete("/api/docs/{doc_id}")
def docs_delete(doc_id: str):
    docs = _load_docs()
    doc = next((d for d in docs if d["id"] == doc_id), None)
    if doc:
        try: os.remove(doc["path"])
        except: pass
        docs = [d for d in docs if d["id"] != doc_id]
        _save_docs(docs)
    return {"ok": True}


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "vekus-api", "version": "0.2.0"}

