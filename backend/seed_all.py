"""Seed all empty tables with realistic demo data for sheet metal manufacturing."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
self_dir = os.path.dirname(os.path.abspath(__file__))
if self_dir.endswith('backend'):
    sys.path.insert(0, self_dir)
else:
    sys.path.insert(0, os.path.join(self_dir, 'backend'))
from datetime import datetime, timezone
from app.models import Base, User, Customer, Quote, PricingParameter, Listing, Conversation, Message, PaymentOrder, PointsTransaction, BomItem, Supplier, PurchaseOrder, QualityCheck, ProductionOrder, InventoryItem, InventoryLog
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker
import random

DATABASE_URL = "sqlite:////data/www/vekus/vekus.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def seed():
    db = SessionLocal()

    print("Seeding all tables...")

    # ====== BOM Items ======
    bom_data = [
        # Level 0 (Finished Products)
        {"code":"FG-001","name":"电气控制柜壳体","spec":"2000×800×600mm","material":"冷轧板","unit":"台","unit_weight":85,"price":3200,"category":"组件","parent_id":0,"quantity":1,"level":0,"sort_order":1,"note":"标准配置","version":"2.1"},
        {"code":"FG-002","name":"钣金支架总成","spec":"1200×400×300mm","material":"镀锌板","unit":"套","unit_weight":24,"price":850,"category":"组件","parent_id":0,"quantity":1,"level":0,"sort_order":2,"note":"含安装附件","version":"1.5"},
        {"code":"FG-003","name":"配电箱外壳","spec":"600×400×200mm","material":"不锈钢","unit":"台","unit_weight":18,"price":1200,"category":"组件","parent_id":0,"quantity":1,"level":0,"sort_order":3,"note":"IP65防水","version":"1.0"},
        # Level 1 (Sub-assemblies under FG-001)
        {"code":"SA-001","name":"柜体框架","spec":"2000×800×600mm","material":"冷轧板","unit":"套","unit_weight":45,"price":1200,"category":"组件","parent_id":1,"quantity":1,"level":1,"sort_order":1},
        {"code":"SA-002","name":"前门板组件","spec":"1950×750mm","material":"冷轧板","unit":"件","unit_weight":15,"price":480,"category":"组件","parent_id":1,"quantity":1,"level":1,"sort_order":2},
        {"code":"SA-003","name":"侧板组件","spec":"1950×580mm","material":"冷轧板","unit":"件","unit_weight":12,"price":360,"category":"组件","parent_id":1,"quantity":2,"level":1,"sort_order":3},
        {"code":"SA-004","name":"顶板组件","spec":"780×580mm","material":"冷轧板","unit":"件","unit_weight":8,"price":220,"category":"零件","parent_id":1,"quantity":1,"level":1,"sort_order":4},
        # Level 1 under FG-002
        {"code":"SA-005","name":"支架底座","spec":"1200×400mm","material":"镀锌板","unit":"件","unit_weight":12,"price":320,"category":"零件","parent_id":2,"quantity":1,"level":1,"sort_order":1},
        {"code":"SA-006","name":"支架立柱","spec":"300mm高","material":"镀锌板","unit":"件","unit_weight":6,"price":180,"category":"零件","parent_id":2,"quantity":2,"level":1,"sort_order":2},
        # Level 2 (Raw materials / parts under SA-001)
        {"code":"RM-001","name":"冷轧钢板2.0mm","spec":"2500×1250×2.0mm","material":"冷轧板","unit":"张","unit_weight":49,"price":380,"category":"原材料","parent_id":4,"quantity":1,"level":2,"sort_order":1},
        {"code":"RM-002","name":"冷轧钢板1.5mm","spec":"2500×1250×1.5mm","material":"冷轧板","unit":"张","unit_weight":37,"price":285,"category":"原材料","parent_id":5,"quantity":1,"level":2,"sort_order":1},
        {"code":"RM-003","name":"铰链","spec":"不锈钢304","material":"不锈钢","unit":"个","unit_weight":0.15,"price":12,"category":"原材料","parent_id":5,"quantity":4,"level":2,"sort_order":2},
        {"code":"RM-004","name":"门锁","spec":"MS714","material":"锌合金","unit":"个","unit_weight":0.3,"price":45,"category":"原材料","parent_id":5,"quantity":1,"level":2,"sort_order":3},
        {"code":"RM-005","name":"密封胶条","spec":"8×5mm EPDM","material":"EPDM","unit":"米","unit_weight":0.05,"price":8,"category":"原材料","parent_id":5,"quantity":6,"level":2,"sort_order":4},
    ]
    bom_ids = {}
    for i, b in enumerate(bom_data, 1):
        row = BomItem(**b, created_at=now())
        db.add(row)
        db.flush()
        bom_ids[i] = row.id
    print(f"  BOM: {len(bom_data)} items")

    # ====== Inventory ======
    inv_data = [
        {"bom_item_id": bom_ids[10],"code":"RM-001","name":"冷轧钢板2.0mm","spec":"2500×1250×2.0mm","material":"冷轧板","unit":"张","quantity":45,"safety_stock":20,"location":"A-01-03","status":"正常"},
        {"bom_item_id": bom_ids[11],"code":"RM-002","name":"冷轧钢板1.5mm","spec":"2500×1250×1.5mm","material":"冷轧板","unit":"张","quantity":12,"safety_stock":25,"location":"A-01-04","status":"紧缺"},
        {"bom_item_id": bom_ids[13],"code":"RM-004","name":"门锁MS714","spec":"MS714","material":"锌合金","unit":"个","quantity":200,"safety_stock":50,"location":"B-03-01","status":"正常"},
        {"bom_item_id": bom_ids[14],"code":"RM-005","name":"密封胶条","spec":"8×5mm","material":"EPDM","unit":"米","quantity":8,"safety_stock":30,"location":"B-03-02","status":"紧缺"},
        {"bom_item_id": bom_ids[12],"code":"RM-003","name":"铰链","spec":"不锈钢","material":"不锈钢","unit":"个","quantity":380,"safety_stock":100,"location":"B-03-03","status":"正常"},
    ]
    for inv in inv_data:
        row = InventoryItem(**inv, updated_at=now())
        db.add(row)
        db.flush()
        db.add(InventoryLog(item_id=row.id, type="in", quantity=row.quantity, before_qty=0, after_qty=row.quantity, related_no="INIT", operator="系统", note="初始库存", created_at=now()))
    print(f"  Inventory: {len(inv_data)} items")

    # ====== Suppliers ======
    sup_data = [
        {"code":"SUP001","name":"宝钢股份","contact_name":"陈经理","phone":"13801001234","email":"chen@baosteel.com","address":"上海市宝山区","category":"材料"},
        {"code":"SUP002","name":"深圳华星五金","contact_name":"李厂长","phone":"13507551234","email":"li@hx-hardware.com","address":"深圳市宝安区","category":"外协"},
        {"code":"SUP003","name":"广州数控设备","contact_name":"王工","phone":"13902221234","email":"wang@gk-equip.com","address":"广州市番禺区","category":"设备"},
    ]
    for s in sup_data:
        db.add(Supplier(**s, created_at=now()))
    print(f"  Suppliers: {len(sup_data)}")

    # ====== Purchase Orders ======
    po_data = [
        {"order_no":"PO-20260610-001","supplier_name":"宝钢股份","item_name":"冷轧钢板2.0mm","spec":"2500×1250×2.0mm","quantity":30,"unit":"张","price":375,"total_amount":11250,"status":"received","order_date":"2026-06-10","receive_date":"2026-06-13"},
        {"order_no":"PO-20260612-001","supplier_name":"深圳华星五金","item_name":"铰链","spec":"不锈钢304","quantity":200,"unit":"个","price":11.5,"total_amount":2300,"status":"sent","order_date":"2026-06-12"},
        {"order_no":"PO-20260614-001","supplier_name":"宝钢股份","item_name":"冷轧钢板1.5mm","spec":"2500×1250×1.5mm","quantity":40,"unit":"张","price":280,"total_amount":11200,"status":"draft","order_date":"2026-06-14"},
    ]
    for po in po_data:
        db.add(PurchaseOrder(**po, created_at=now()))
    print(f"  Purchase Orders: {len(po_data)}")

    # ====== Production Orders ======
    prod_data = [
        {"order_no":"MO-20260610-001","product_name":"电气控制柜壳体","quantity":5,"status":"running","priority":"high","planned_start":"2026-06-10","planned_end":"2026-06-18","workshop":"钣金一车间","assigned_to":"张伟","progress":65,"note":"客户加急订单"},
        {"order_no":"MO-20260612-001","product_name":"钣金支架总成","quantity":20,"status":"draft","priority":"normal","planned_start":"2026-06-15","planned_end":"2026-06-22","workshop":"钣金二车间","assigned_to":"李娜","progress":0},
        {"order_no":"MO-20260613-001","product_name":"配电箱外壳","quantity":10,"status":"done","priority":"normal","planned_start":"2026-06-08","planned_end":"2026-06-13","workshop":"钣金一车间","assigned_to":"张伟","progress":100,"actual_start":"2026-06-08","actual_end":"2026-06-13"},
    ]
    for pd in prod_data:
        db.add(ProductionOrder(**pd, created_at=now(), updated_at=now()))
    print(f"  Production Orders: {len(prod_data)}")

    # ====== Quality Checks ======
    qc_data = [
        {"check_no":"QC-20260613-001","type":"incoming","item_name":"冷轧钢板2.0mm","quantity":30,"pass_qty":29,"fail_qty":1,"result":"partial","inspector":"刘芳","check_date":"2026-06-13","defect_desc":"1张表面有锈斑","handle":"return"},
        {"check_no":"QC-20260613-002","type":"final","item_name":"配电箱外壳","quantity":10,"pass_qty":10,"fail_qty":0,"result":"pass","inspector":"刘芳","check_date":"2026-06-13"},
        {"check_no":"QC-20260614-001","type":"process","item_name":"前门板组件","quantity":5,"pass_qty":4,"fail_qty":1,"result":"partial","inspector":"陈明","check_date":"2026-06-14","defect_desc":"折弯角度偏差","handle":"rework"},
    ]
    for qc in qc_data:
        db.add(QualityCheck(**qc, created_at=now()))
    print(f"  Quality Checks: {len(qc_data)}")

    # ====== Marketplace Listings ======
    if db.query(Listing).count() < 3:
        listings = [
            {"owner_user_id":1,"title":"1.5mm镀锌板余料出售 2000×1000mm","listing_type":"sell","category":"板材","material":"镀锌板","thickness":1.5,"dimensions":"2000×1000mm","quantity":50,"price":85,"unit":"张","description":"库存余料，表面完好，适合小件加工","location":"广东-深圳","status":"active","created_at":now(),"updated_at":now()},
            {"owner_user_id":2,"title":"求购不锈钢板 3.0mm","listing_type":"buy","category":"板材","material":"不锈钢","thickness":3.0,"quantity":20,"price":0,"unit":"张","description":"304不锈钢，需提供材质证明","location":"浙江-宁波","status":"active","created_at":now(),"updated_at":now()},
            {"owner_user_id":1,"title":"二手数控折弯机 100T/3200","listing_type":"sell","category":"设备","quantity":1,"price":85000,"unit":"台","description":"2019年购入，使用正常，可现场试机","location":"广东-东莞","status":"active","created_at":now(),"updated_at":now()},
        ]
        for l in listings:
            db.add(Listing(**l))
        print(f"  Listings: {len(listings)}")

    db.commit()
    db.close()
    print("\n✅ All tables seeded successfully!")

if __name__ == "__main__":
    seed()
