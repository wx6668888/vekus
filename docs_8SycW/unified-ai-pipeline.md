# Vekus 统一 AI 识图管道

## 目标
将所有文件类型统一接入同一条识图链路，但按文件类型做前处理分流。

## 总流程
1. 上传文件
2. 识别文件类型
3. 选择前处理策略
4. 执行对应处理器
5. 输出 detections
6. 输出 quotePayload
7. 回填报价页

## 文件类型分流
- DWG / DXF -> CAD 结构解析 + 规则补全
- PDF -> 页面解析 + OCR / 视觉模型
- STEP / STP / X_T / SLDPRT -> 3D 特征提取 + 钣金判断
- 图片 -> 视觉模型 + OCR

## 统一输出
- confidence
- detections
- quotePayload
- error

## 后续升级
- 真实 CAD 解析库
- PDF 转图组件
- OCR 服务
- 多模态模型路由
- 规则引擎融合
