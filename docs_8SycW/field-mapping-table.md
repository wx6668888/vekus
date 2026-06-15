# Vekus 字段映射表

## 目标
将 DWG / PDF / 图片中提取到的原始信息，映射为报价系统可直接使用的标准字段。

## 一、标准报价字段
- customerName
- quantity
- materialPrice
- surfacePrice
- cutLength
- bendCount
- sprayArea
- spotWeldCount
- fullWeldLength
- lightHoleCount
- threadHoleCount
- countersunkHoleCount
- extraCost
- taxFactor
- discountFactor
- packFee
- blankWeightKg
- sheetThickness
- blankLengthMm
- blankWidthMm
- confidence
- detections

---

## 二、DWG / CAD 原始字段 → 标准字段

| 原始字段 | 标准字段 | 说明 | 处理方式 |
|---|---|---|---|
| 标题栏材料 | materialPrice | 材料名称对应单价 | 读取后字典映射 |
| 技术要求材料 | materialPrice | 材料名称对应单价 | 读取后字典映射 |
| 厚度标注 | sheetThickness | 板厚 | 直接读取 |
| 展开长 | blankLengthMm | 展开长度 | 直接读取或推断 |
| 展开宽 | blankWidthMm | 展开宽度 | 直接读取或推断 |
| 外轮廓周长 | cutLength | 切割长度 | 几何计算 |
| 折弯线数量 | bendCount | 折弯总数 | 统计去重 |
| 喷涂面积标注 | sprayArea | 喷涂面积 | 直接读取或推断 |
| 焊点符号数量 | spotWeldCount | 点焊数 | 统计 |
| 满焊线长度 | fullWeldLength | 满焊长度 | 几何+标注 |
| 光孔数量 | lightHoleCount | 光孔数 | 统计 |
| 螺纹孔数量 | threadHoleCount | 螺纹孔数 | 统计 |
| 沉头孔数量 | countersunkHoleCount | 沉头孔数 | 统计 |
| 标准件数量 | quantity / standardPartCount | 视业务定义 | 统计 |
| 备注中的特殊费用 | extraCost | 特殊另加 | 提取/人工 |
| 价格系数 | taxFactor | 税管费系数 | 配置项 |
| 折扣系数 | discountFactor | 折扣系数 | 配置项 |
| 包装费率 | packFee | 包装运输费 | 配置项 |
| 毛坯重量 | blankWeightKg | 重量 | 计算或人工 |

---

## 三、PDF / 图片 原始字段 → 标准字段

| 原始字段 | 标准字段 | 说明 | 处理方式 |
|---|---|---|---|
| OCR 文本中的材料 | materialPrice | 材料名称对应单价 | OCR + 字典映射 |
| OCR 文本中的厚度 | sheetThickness | 板厚 | OCR 正则提取 |
| OCR 文本中的尺寸 | blankLengthMm / blankWidthMm | 展开长宽 | OCR + 规则 |
| OCR 文本中的孔标注 | lightHoleCount / threadHoleCount / countersunkHoleCount | 孔类 | OCR + 分类 |
| OCR 文本中的焊接说明 | spotWeldCount / fullWeldLength | 焊接量 | OCR + 规则 |
| OCR 文本中的喷涂说明 | sprayArea | 喷涂面积 | OCR + 推断 |
| 图片识别出的外轮廓 | cutLength | 切割长度 | 视觉 + 几何 |

---

## 四、AI 推理字段 → 标准字段

| AI 推理结果 | 标准字段 | 说明 | 处理方式 |
|---|---|---|---|
| 外轮廓估算 | cutLength | 切割长度 | 推理 |
| 轮廓面积估算 | sprayArea | 喷涂面积 | 推理 |
| 折弯线推断 | bendCount | 折弯总数 | 推理 |
| 孔阵列推断 | lightHoleCount | 光孔数 | 推理 |
| 焊缝符号推断 | fullWeldLength | 满焊长度 | 推理 |
| 材料识别置信度 | confidence | 结果可信度 | 推理 |

---

## 五、回填优先级

1. **DWG 结构直接读取**
2. **PDF / 图片 OCR 提取**
3. **AI 推理补全**
4. **人工确认覆盖**

---

## 六、冲突处理规则

### 同一字段多个来源
优先级：
1. 人工确认
2. 直接读取
3. OCR 提取
4. AI 推理
5. 默认值

### 冲突示例
- DWG 标注板厚为 1.2mm，OCR 识别为 1.0mm，则优先取 DWG 标注
- OCR 识别有 8 个孔，但 CAD 结构统计 10 个，则优先取 CAD 结构，人工确认提示异常

---

## 七、建议默认值
- taxFactor: 1.25
- discountFactor: 0.95
- packFee: 0.5
- extraCost: 0
- confidence: 0
