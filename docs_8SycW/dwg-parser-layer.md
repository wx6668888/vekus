# Vekus DWG 解析器接入层

## 目标
将 DWG 的结构信息提取成中间层，为后续 AI 推断和二次计算提供输入。

## 输入
- DWG 文件

## 输出
- layers
- texts
- dimensions
- blocks
- notes
- raw_summary

## 处理步骤
1. 读取文件
2. 提取图层信息
3. 提取文本和标注
4. 提取块定义
5. 输出中间结构

## 后续可接入
- CAD SDK
- DWG 转换服务
- 结构化解析器
- AI 推理层

## 与识图链路的关系
DWG 解析器不是最终识图，而是：
DWG → 结构层 → AI 推理 → 二次计算 → quotePayload
