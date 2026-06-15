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


class BomItem(Base):
    """物料/零件"""
    __tablename__ = "bom_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, default="")       # 物料编码
    name: Mapped[str] = mapped_column(String(128), nullable=False)                   # 物料名称
    spec: Mapped[str] = mapped_column(String(128), nullable=False, default="")       # 规格/型号
    material: Mapped[str] = mapped_column(String(64), nullable=False, default="")    # 材质
    unit: Mapped[str] = mapped_column(String(16), nullable=False, default="件")       # 单位
    unit_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0)     # 单重(kg)
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0)           # 参考单价
    category: Mapped[str] = mapped_column(String(32), nullable=False, default="零件") # 零件/组件/原材料
    parent_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0)       # 父级物料ID(0=顶层)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)         # 组件用量
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)            # 层级(0=成品,1=一级...)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)       # 排序
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")               # 备注
    version: Mapped[str] = mapped_column(String(16), nullable=False, default="1.0")   # 版本
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")  # active/inactive
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")


class InventoryItem(Base):
    """库存物料"""
    __tablename__ = "inventory"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bom_item_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0)    # 关联BOM
    code: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    spec: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    material: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    unit: Mapped[str] = mapped_column(String(16), nullable=False, default="件")
    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=0)        # 当前库存
    safety_stock: Mapped[float] = mapped_column(Float, nullable=False, default=0)     # 安全库存
    location: Mapped[str] = mapped_column(String(64), nullable=False, default="")     # 库位
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="正常")    # 正常/紧缺/过剩
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")


class InventoryLog(Base):
    """库存流水"""
    __tablename__ = "inventory_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[str] = mapped_column(String(16), nullable=False)  # in/out/check
    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    before_qty: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    after_qty: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    related_no: Mapped[str] = mapped_column(String(64), nullable=False, default="")   # 关联单号
    operator: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")


class ProductionOrder(Base):
    """生产工单"""
    __tablename__ = "production_orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(64), nullable=False)
    bom_item_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    product_name: Mapped[str] = mapped_column(String(128), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="draft")  # draft/scheduled/running/done/cancelled
    priority: Mapped[str] = mapped_column(String(8), nullable=False, default="normal") # high/normal/low
    planned_start: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    planned_end: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    actual_start: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    actual_end: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    workshop: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    assigned_to: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 0-100
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")


class Supplier(Base):
    """供应商"""
    __tablename__ = "suppliers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    contact_name: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    phone: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    email: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    address: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    category: Mapped[str] = mapped_column(String(32), nullable=False, default="材料")  # 材料/外协/设备/其他
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")


class PurchaseOrder(Base):
    """采购订单"""
    __tablename__ = "purchase_orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(64), nullable=False)
    supplier_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    supplier_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    item_name: Mapped[str] = mapped_column(String(128), nullable=False)          # 采购物料
    spec: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=1)
    unit: Mapped[str] = mapped_column(String(16), nullable=False, default="件")
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0)       # 单价
    total_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0) # 总金额
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="draft")  # draft/sent/received/done/cancelled
    order_date: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    receive_date: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")


class QualityCheck(Base):
    """质量检验"""
    __tablename__ = "quality_checks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    check_no: Mapped[str] = mapped_column(String(64), nullable=False)
    type: Mapped[str] = mapped_column(String(16), nullable=False)  # incoming/process/final
    related_type: Mapped[str] = mapped_column(String(16), nullable=False, default="")  # purchase/production
    related_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0)        # 关联采购单/工单ID
    item_name: Mapped[str] = mapped_column(String(128), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)          # 检验数量
    pass_qty: Mapped[int] = mapped_column(Integer, nullable=False, default=0)          # 合格
    fail_qty: Mapped[int] = mapped_column(Integer, nullable=False, default=0)          # 不合格
    result: Mapped[str] = mapped_column(String(8), nullable=False, default="pass")     # pass/fail/partial
    inspector: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    check_date: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    defect_desc: Mapped[str] = mapped_column(Text, nullable=False, default="")          # 不良描述
    handle: Mapped[str] = mapped_column(String(32), nullable=False, default="")         # 处理方式: rework/scrap/return/accept
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")


class Approval(Base):
    """审批记录"""
    __tablename__ = "approvals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    approval_no: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)   # quote/purchase/production/refund
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_title: Mapped[str] = mapped_column(String(256), nullable=False, default="")  # 如"报价单 QT-xxx"
    applicant: Mapped[str] = mapped_column(String(64), nullable=False, default="")      # 申请人
    approver: Mapped[str] = mapped_column(String(64), nullable=False, default="")       # 审批人
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")   # pending/approved/rejected
    comment: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")


class AuditLog(Base):
    """操作日志"""
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_name: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    action: Mapped[str] = mapped_column(String(32), nullable=False)  # login/logout/create/update/delete/send/approve
    target_type: Mapped[str] = mapped_column(String(32), nullable=False, default="")  # quote/customer/user/inventory
    target_id: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    detail: Mapped[str] = mapped_column(Text, nullable=False, default="")
    ip_address: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")


class Invoice(Base):
    """发票/对账单"""
    __tablename__ = "invoices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_no: Mapped[str] = mapped_column(String(64), nullable=False)
    quote_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    customer_name: Mapped[str] = mapped_column(String(128), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    tax_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="draft")  # draft/sent/paid/overdue/cancelled
    invoice_date: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    due_date: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    paid_date: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")


class Employee(Base):
    """员工/人员"""
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    department: Mapped[str] = mapped_column(String(32), nullable=False, default="")  # 管理/生产/质量/采购/销售
    position: Mapped[str] = mapped_column(String(32), nullable=False, default="")   # 经理/主管/工程师/操作工
    phone: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    email: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    hire_date: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")  # active/inactive
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")


class Equipment(Base):
    """设备/机器"""
    __tablename__ = "equipment"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False, default="")  # 折弯机/激光切割/冲床/焊接/其他
    model: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    workshop: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="idle")  # idle/running/maintenance/repair
    last_maintenance: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    next_maintenance: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    capacity_hours: Mapped[float] = mapped_column(Float, nullable=False, default=8)  # 每日可用工时
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")


class CompanyProfile(Base):
    """公司信息"""
    __tablename__ = "company_profile"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_name: Mapped[str] = mapped_column(String(128), nullable=False, default="Vekus")
    short_name: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    address: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    phone: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    email: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    website: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    tax_id: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    bank_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    bank_account: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    logo_url: Mapped[str] = mapped_column(String(256), nullable=False, default="")


class PointsTransaction(Base):
    __tablename__ = "points_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    type: Mapped[str] = mapped_column(String(16), nullable=False, default="charge")  # charge / deduct / expire
    description: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    related_id: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")
