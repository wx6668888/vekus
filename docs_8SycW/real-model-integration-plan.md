# Vekus 真实模型接入方案

## 目标
将当前的 `MockProcessor` 替换为真实的 OCR / 多模态 / CAD 解析模型处理器，并保持统一输出结构：
- confidence
- detections
- quotePayload

## 一、推荐的接入方式

### 方案 A：通用多模态模型 + 规则引擎
适合：
- PDF
- 图片
- 截图
- CAD 渲染图

流程：
1. 文件预处理
2. 图片化 / 页面化
3. 调用多模态模型
4. 解析模型返回的结构化结果
5. 规则引擎补全报价字段
6. 输出 quotePayload

### 方案 B：OCR + CAD 结构解析 + 模型补全
适合：
- DWG
- DXF
- STEP
- X_T
- SLDPRT

流程：
1. 结构解析或 OCR
2. 提取尺寸、标注、图层、特征
3. 模型补全缺失字段
4. 二次计算
5. 输出 quotePayload

### 方案 C：混合式引擎
最适合当前项目。

输入文件后按类型分流：
- PDF / 图片 → OCR + 多模态
- DWG / DXF → CAD 结构解析 + 模型补全
- STEP / X_T / SLDPRT → 几何特征提取 + 模型补全

---

## 二、模型选择建议

### 1. 视觉理解模型
用于：
- 图纸识别
- 标注理解
- 面积/轮廓推断

推荐方向：
- Anthropic Claude Sonnet 4.6（多模态）
- OpenAI GPT-4o 类模型
- Qwen2.5-VL

### 2. OCR 引擎
用于：
- 图纸文字识别
- 标题栏识别
- 技术要求识别

推荐方向：
- PaddleOCR
- 云 OCR 服务
- 本地 OCR 引擎

### 3. CAD 解析引擎
用于：
- DWG / DXF / 3D CAD 结构提取
- 图层
- 块
- 尺寸
- 特征

推荐方向：
- DWG 转 DXF 中间层
- CAD SDK
- 几何解析库

---

## 三、处理器接口要求
所有真实处理器必须实现：

```python
def process(file_path: Path, original_name: str) -> tuple[float, list[DetectionItem], QuotePayload]:
    ...
```

### 返回要求
- `confidence`：0~1
- `detections`：结构化识别项
- `quotePayload`：最终回填报价字段

---

## 四、处理器分工

### PdfProcessor
职责：
- 提取文字
- 识别尺寸
- 识别表格
- 识别技术要求

### VisionProcessor
职责：
- 识别图片中的结构
- 识别标注
- 识别轮廓
- 识别人工拍照图

### DwgProcessor
职责：
- 提取图层
- 提取标注
- 提取尺寸
- 提取文本
- 提取块

### Cad3DProcessor
职责：
- 识别实体
- 判断薄板件
- 识别孔/槽/圆角/倒角
- 判断是否进入钣金报价

---

## 五、真实接口接入位置

### 1. 替换 `MockProcessor`
当前文件：
- `backend/app/services/processor.py`

建议：
- 保留 `BaseProcessor`
- 新增 provider-specific processor
- 根据 `VEKUS_AI_PROVIDER` 切换

### 2. 统一由工厂创建
当前文件：
- `backend/app/services/processor_factory.py`

建议：
- 根据文件类型 + provider 选择对应处理器

### 3. 结果统一整理
当前文件：
- `backend/app/services/field_mapper.py`

建议：
- 所有模型输出先进入标准字段映射层
- 再输出 quotePayload

---

## 六、建议的 provider 配置

```env
VEKUS_AI_PROVIDER=claude
VEKUS_AI_API_KEY=your_key
VEKUS_AI_BASE_URL=https://api.anthropic.com
```

或：

```env
VEKUS_AI_PROVIDER=qwen
VEKUS_AI_API_KEY=your_key
VEKUS_AI_BASE_URL=https://your-provider.example.com
```

---

## 七、Claude 类接入建议
如果使用 Claude / Anthropic 类模型：
- PDF / 图片先转成可视内容
- 发送图像和结构化提示词
- 让模型输出 JSON
- 再做字段映射和二次计算

### 推荐输出 JSON
```json
{
  "confidence": 0.92,
  "detections": [
    { "label": "板厚", "value": "1.2 mm", "confidence": 0.98 }
  ],
  "quotePayload": {
    "materialPrice": 12.3,
    "cutLength": 4.6,
    "bendCount": 12
  }
}
```

---

## 八、推荐实施顺序
1. 先接 PDF / 图片真实模型
2. 再接 DWG 结构解析
3. 再接 STEP / X_T / SLDPRT
4. 最后统一成一个混合识图服务

---

## 九、上线建议
- 先用单机部署跑通
- 再替换为异步队列
- 再加持久化任务表
- 最后接分布式 worker
