# Vekus 真实识图处理器接口协议

## 目标
将 PDF / 图片 / DWG / DXF / STEP / X_T / SLDPRT 统一送入识图处理器，并输出标准报价数据。

## 一、处理器输入协议

### 函数签名
```python
def process(file_path: Path, original_name: str) -> tuple[float, list[DetectionItem], QuotePayload]:
    ...
```

### 入参
- `file_path`：上传后的本地文件路径
- `original_name`：原始文件名

### 返回
- `confidence`：整体置信度，0~1
- `detections`：识别明细列表
- `quotePayload`：标准报价字段

---

## 二、DetectionItem 结构

```json
{
  "label": "板厚",
  "value": "1.2 mm",
  "confidence": 0.98
}
```

### 字段说明
- `label`：识别项名称
- `value`：识别值
- `confidence`：单项置信度

---

## 三、QuotePayload 结构

```json
{
  "customerName": "XX科技",
  "quantity": 100,
  "materialPrice": 12.3,
  "surfacePrice": 18,
  "cutLength": 4.6,
  "bendCount": 12,
  "sprayArea": 0.18,
  "spotWeldCount": 24,
  "fullWeldLength": 1.3,
  "lightHoleCount": 8,
  "threadHoleCount": 0,
  "countersunkHoleCount": 0,
  "extraCost": 50,
  "taxFactor": 1.25,
  "discountFactor": 0.95,
  "packFee": 0.5
}
```

### 字段说明
- `customerName`：客户名
- `quantity`：数量
- `materialPrice`：材料单价
- `surfacePrice`：表面处理单价
- `cutLength`：切割长度
- `bendCount`：折弯次数
- `sprayArea`：喷涂面积
- `spotWeldCount`：点焊数
- `fullWeldLength`：满焊长度
- `lightHoleCount`：光孔数
- `threadHoleCount`：螺纹孔数
- `countersunkHoleCount`：沉头孔数
- `extraCost`：特殊费用
- `taxFactor`：税管费系数
- `discountFactor`：折扣系数
- `packFee`：包装费率

---

## 四、处理器分流建议

### 1. PDF / 图片处理器
- OCR
- 多模态图像理解
- 尺寸与文字抽取
- 规则补全

### 2. DWG 处理器
- 图层解析
- 文本解析
- 标注解析
- 几何提取
- 二次计算

### 3. DXF 处理器
- 类似 DWG，但结构更适合解析

### 4. STEP / X_T / SLDPRT 处理器
- 几何特征提取
- 薄板判断
- 孔 / 槽 / 圆角 / 倒角识别
- 是否进入钣金报价流程

---

## 五、推荐返回策略

### 成功
```json
{
  "scanId": "scan_xxx",
  "status": "done",
  "confidence": 0.92,
  "detections": [],
  "quotePayload": {}
}
```

### 处理中
```json
{
  "scanId": "scan_xxx",
  "status": "processing"
}
```

### 失败
```json
{
  "scanId": "scan_xxx",
  "status": "failed",
  "error": "reason"
}
```

---

## 六、实现约定
- 处理器必须可插拔
- 处理器必须返回统一结构
- 处理器内部允许多阶段推理
- 处理器必须支持人工确认回填

---

## 七、后续扩展
可以把处理器拆成：
- OCRProcessor
- DwgProcessor
- Cad3dProcessor
- VisionProcessor
- RuleEngineProcessor
