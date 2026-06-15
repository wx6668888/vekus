# Vekus DWG 智能识别架构

## 目标
不依赖简单 OCR，而是对 DWG 做结构化理解、字段推断和二次计算，最后输出可直接用于报价的 quotePayload。

## 输入分层
1. 直接读取
   - 图层
   - 块
   - 文本
   - 标注
   - 尺寸
   - 引线
   - 几何实体

2. 视觉辅助
   - 需要时渲染为图片辅助识别
   - 与 CAD 结构结果交叉验证

3. AI 推理
   - 补全缺失字段
   - 推断工艺参数
   - 识别图纸意图

## 处理流程
DWG 文件
→ 结构解析
→ 图元/标注提取
→ 特征归类
→ 缺失字段推断
→ 二次计算
→ 输出 quotePayload

## 字段分层

### 直接读取
- 图纸编号
- 标题栏信息
- 材料
- 板厚
- 尺寸标注
- 孔标注
- 焊接符号

### AI 推断
- 折弯总数
- 展开长宽
- 切割长度
- 喷涂面积
- 焊点数
- 满焊长度
- 标准件数量

### 二次计算
- 切割长度 = 外轮廓周长或路径长度求和
- 折弯总数 = 折弯线统计 + 剖视图验证
- 喷涂面积 = 外表面积/可喷涂面积推导
- 孔加工量 = 孔标注 + 块统计
- 焊接量 = 焊接符号 + 引线 + 说明推导

## 识别策略
1. 优先读 CAD 原生结构
2. 读不到的字段交给 AI 推断
3. AI 结果不足时用规则引擎补全
4. 置信度低的字段标记为人工确认

## 输出结构
```json
{
  "confidence": 0.92,
  "detections": [
    { "label": "板厚", "value": "1.2 mm", "confidence": 0.98 },
    { "label": "展开长", "value": "820 mm", "confidence": 0.95 }
  ],
  "quotePayload": {
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
    "extraCost": 50,
    "taxFactor": 1.25,
    "discountFactor": 0.95,
    "packFee": 0.5
  }
}
```

## 交互建议
- 置信度高的结果自动回填
- 置信度低的结果在报价页高亮
- 支持一键恢复识图结果
- 支持人工修正后重新计算
