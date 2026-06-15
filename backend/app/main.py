import json
import random
import string
import tempfile
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
    return {
        "id": str(row.id), "code": row.code, "name": row.name,
        "contactName": row.contact_name, "phone": row.phone,
        "email": row.email, "address": row.address,
        "tier": row.tier,
        "tags": row.tags.split(",") if row.tags else [],
        "status": row.status, "assignedSales": row.assigned_sales,
        "createdAt": row.created_at,
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
    question: str

@app.post("/api/ai/customer-service")
def customer_service(body: ChatBody):
    """AI-powered customer service using DeepSeek with knowledge base."""
    from .knowledge_base import DEEPSEEK_API_KEY, DEEPSEEK_API_BASE, DEEPSEEK_MODEL, SYSTEM_PROMPT

    # Try DeepSeek API first
    if DEEPSEEK_API_KEY:
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": DEEPSEEK_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": body.question},
                ],
                "max_tokens": 600,
                "temperature": 0.7,
            }
            resp = requests.post(
                f"{DEEPSEEK_API_BASE}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )
            if resp.status_code == 200:
                data = resp.json()
                answer = data["choices"][0]["message"]["content"]
                return {"answer": answer}
        except Exception:
            pass  # Fall through to local KB

    # Local fallback
    return {"answer": f"鎴戞槸Vekus鏅鸿兘鍔╂墜灏廣锛佹偍鍙互闂垜鍏充簬鎶ヤ环娴佺▼銆佹潗鏂欎环鏍笺€佷氦鏄撳箍鍦恒€佸厖鍊肩瓑闂銆傚闇€浜哄伐鏈嶅姟锛岃鎷ㄦ墦400-888-9999銆俓n\n鎮ㄧ殑闂鏄細{body.question}\n\n寤鸿灏濊瘯鍜ㄨ锛歕n鈥?濡備綍涓婁紶鍥剧焊杩涜鎶ヤ环锛焅n鈥?浜ゆ槗骞垮満鎬庝箞鍙戝竷淇℃伅锛焅n鈥?濡備綍缁欏鎴峰彂閫佹姤浠凤紵"}


# 鈹€鈹€ Dashboard 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

@app.get("/api/dashboard/summary")
def dashboard_summary():
    with SessionLocal() as db:
        return {
            "today_scans": random.randint(80, 160),
            "pending_quotes": random.randint(15, 40),
            "conversion_rate": round(random.uniform(0.3, 0.45), 3),
            "customers": db.query(Customer).count(),
            "users": db.query(User).count(),
            "quotes": db.query(Quote).count(),
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
def get_messages(conversation_id: int):
    with SessionLocal() as db:
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

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "vekus-api", "version": "0.2.0"}

