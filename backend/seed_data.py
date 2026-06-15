"""Seed demo data with proper UTF-8 encoding."""
import sys
sys.path.insert(0, '.')

from backend.app.main import SessionLocal, now_str
from backend.app.models import Listing, Conversation, Message
from sqlalchemy import select, delete

def seed():
    db = SessionLocal()
    now = now_str()

    # Clear existing listings and re-insert
    db.execute(delete(Listing))
    db.add_all([
        Listing(owner_user_id=1, title="1.5mm镀锌板余料 2000×1000", listing_type="sell", category="余料", material="镀锌板", thickness=1.5, dimensions="2000×1000mm", surface="喷粉", quantity=80, price=28, unit="张", description="工厂剩余镀锌板，规格2000×1000×1.5mm，表面已喷粉处理灰白色，共80张，打包价更优。适合机箱机柜、配电箱等钣金加工。", location="广东深圳", contact_phone="13800000001", status="active", created_at=now, updated_at=now),
        Listing(owner_user_id=1, title="SUS304不锈钢板 1.2mm厚 4×8尺", listing_type="sell", category="板材", material="不锈钢", thickness=1.2, dimensions="2438×1219mm", surface="原色", quantity=200, price=185, unit="张", description="全新SUS304不锈钢板，标准尺寸4×8尺，表面2B处理。适合食品设备、医疗器械、化工容器等高要求场景。", location="广东佛山", contact_phone="13800000001", status="active", created_at=now, updated_at=now),
        Listing(owner_user_id=2, title="求购冷轧板 2.0mm 大量现货", listing_type="buy", category="板材", material="冷轧板", thickness=2.0, dimensions="不限", surface="无要求", quantity=500, price=35, unit="张", description="长期求购冷轧板，规格不限，要求现货，现金结算。主要用于配电柜生产，月需求500张以上。", location="浙江宁波", contact_phone="13800000000", status="active", created_at=now, updated_at=now),
        Listing(owner_user_id=2, title="数控折弯加工服务 精度±0.1mm", listing_type="sell", category="加工服务", material="不限", thickness=0, dimensions="最大3000mm", surface="不限", quantity=1, price=5, unit="次", description="提供专业数控折弯加工服务，设备为AMADA数控折弯机，精度±0.1mm，可加工碳钢、不锈钢、铝板。最大折弯长度3000mm，厚度0.5-6mm。", location="江苏苏州", contact_phone="13800000002", status="active", created_at=now, updated_at=now),
        Listing(owner_user_id=1, title="3.0mm铝板边角料 多种规格", listing_type="sell", category="余料", material="铝板", thickness=3.0, dimensions="多种规格", surface="原色", quantity=150, price=12, unit="kg", description="铝板加工剩余边角料，3.0mm厚，5052和6061材质混合，最小尺寸200×200，适合小件加工或回收利用。按公斤出售。", location="广东东莞", contact_phone="13800000001", status="active", created_at=now, updated_at=now),
        Listing(owner_user_id=2, title="二手AMADA折弯机 100吨出售", listing_type="sell", category="设备", material="", thickness=0, dimensions="", surface="", quantity=1, price=85000, unit="台", description="二手AMADA RG-100折弯机，100吨，2000mm台面，2019年出厂，使用时间约8000小时，设备状况良好，精度正常。因工厂搬迁急售。", location="上海", contact_phone="13800000002", status="active", created_at=now, updated_at=now),
    ])

    # Clear existing conversations and messages (keep only those created by seed, skip API-created)
    db.execute(delete(Message))
    db.execute(delete(Conversation))

    conv_sys = Conversation(type="system", title="系统通知", participants_json="[1]", last_message="您的报价已被客户查看", last_message_at=now, created_at=now)
    conv_cs = Conversation(type="customer_service", title="Vekus官方客服", participants_json="[1]", last_message="好的，谢谢！", last_message_at=now, created_at=now)
    conv_chat = Conversation(type="user_chat", title="李经理（深蓝机电）", participants_json="[1, 2]", last_message="好的，这批镀锌板我要了", last_message_at=now, created_at=now)
    db.add_all([conv_sys, conv_cs, conv_chat])
    db.flush()

    db.add_all([
        Message(conversation_id=conv_sys.id, sender_id=0, content="欢迎使用Vekus智能报价平台！", message_type="system", is_read=1, created_at="2026-06-01T09:00:00Z"),
        Message(conversation_id=conv_sys.id, sender_id=0, content="系统已为您开通免费体验账户，含3次免费报价机会。", message_type="system", is_read=0, created_at="2026-06-01T09:00:01Z"),
        Message(conversation_id=conv_sys.id, sender_id=0, content="您的报价 QT-20260510-001 已被客户查看。", message_type="system", is_read=0, created_at="2026-06-05T14:30:00Z"),
        Message(conversation_id=conv_cs.id, sender_id=0, content="您好，我是Vekus官方客服小V，有什么可以帮您的？", message_type="text", is_read=1, created_at="2026-06-03T10:00:00Z"),
        Message(conversation_id=conv_cs.id, sender_id=1, content="你好，我想问一下怎么上传DWG图纸？", message_type="text", is_read=1, created_at="2026-06-03T10:01:00Z"),
        Message(conversation_id=conv_cs.id, sender_id=0, content="您好！在报价工作台页面，点击上传区域，选择您的DWG文件即可。系统会自动识别图纸中的参数。支持DWG、DXF、STEP、PDF等格式，最大10MB。", message_type="text", is_read=1, created_at="2026-06-03T10:02:00Z"),
        Message(conversation_id=conv_cs.id, sender_id=1, content="好的，谢谢！", message_type="text", is_read=1, created_at="2026-06-03T10:03:00Z"),
        Message(conversation_id=conv_chat.id, sender_id=2, content="你好，看到你发布的镀锌板余料，还在吗？", message_type="text", is_read=1, created_at="2026-06-06T15:00:00Z"),
        Message(conversation_id=conv_chat.id, sender_id=1, content="在的，80张都还在。", message_type="text", is_read=1, created_at="2026-06-06T15:05:00Z"),
        Message(conversation_id=conv_chat.id, sender_id=2, content="能便宜点吗？我要50张", message_type="text", is_read=1, created_at="2026-06-06T15:06:00Z"),
        Message(conversation_id=conv_chat.id, sender_id=1, content="50张的话26一张给你，最低了", message_type="text", is_read=1, created_at="2026-06-06T15:08:00Z"),
        Message(conversation_id=conv_chat.id, sender_id=2, content="好的，这批镀锌板我要了，怎么付款？", message_type="text", is_read=0, created_at="2026-06-07T09:30:00Z"),
    ])

    db.commit()
    db.close()
    print("Seed data inserted successfully with UTF-8 encoding!")

if __name__ == "__main__":
    seed()
