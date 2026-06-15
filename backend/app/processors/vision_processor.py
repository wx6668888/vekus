"""Vision processor using Claude / GPT-4V multimodal API for real drawing recognition."""

import base64
import json
import os
import uuid
from pathlib import Path

from .base import BaseProcessor, DetectionItem, QuotePayload, ScanResult


class VisionProcessor(BaseProcessor):
    """Uses a multimodal AI model (Claude, GPT-4V, Qwen-VL) to recognize sheet metal drawings."""

    SYSTEM_PROMPT = """你是一个专业的钣金图纸识别专家。请仔细分析上传的图纸图片，提取以下参数：

1. 板厚 (thickness): 材料厚度，单位 mm
2. 展开长 (expandLength): 展开后的长度，单位 mm
3. 展开宽 (expandWidth): 展开后的宽度，单位 mm
4. 切割长度 (cutLength): 总切割路径长度，单位 mm
5. 折弯数 (bendCount): 折弯的次数
6. 喷涂面积 (paintArea): 需要表面处理的面积，单位 ㎡
7. 焊点数 (weldPoints): 点焊的数量
8. 满焊长度 (weldLength): 满焊的总长度，单位 mm
9. 光孔数 (plainHoles): 普通圆孔数量
10. 螺纹孔数 (threadedHoles): 螺纹孔数量
11. 沉孔数 (counterboredHoles): 沉头孔数量

请以JSON格式返回结果。对于无法识别的参数，请设置为0。
每个识别项请同时给出置信度(0-1)。

输出格式示例：
{
  "confidence": 0.92,
  "detections": [
    {"label": "板厚", "value": "1.5 mm", "confidence": 0.95},
    {"label": "展开长", "value": "420 mm", "confidence": 0.90}
  ],
  "quotePayload": {
    "thickness": 1.5,
    "expandLength": 420,
    "expandWidth": 280,
    "cutLength": 2140,
    "bendCount": 6,
    "paintArea": 0.32,
    "weldPoints": 14,
    "weldLength": 0,
    "holes": {"plain": 8, "threaded": 4, "counterbored": 2}
  }
}

只输出JSON，不要输出其他内容。"""

    def __init__(self, provider: str = "claude"):
        self.provider = provider
        # Load .env file if env vars not set
        if not os.getenv("VEKUS_AI_API_KEY"):
            for env_path in ["/data/www/vekus/.env", os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")]:
                if os.path.exists(env_path):
                    with open(env_path) as f:
                        for line in f:
                            if "=" in line and not line.startswith("#"):
                                k, v = line.strip().split("=", 1)
                                if k not in os.environ: os.environ[k] = v
                    break
        self.api_key = os.getenv("VEKUS_AI_API_KEY", "")
        self.model = os.getenv("VEKUS_AI_MODEL", "claude-sonnet-4-6")
        self.base_url = os.getenv("VEKUS_AI_BASE_URL", "https://api.anthropic.com")

    def process(self, file_path: Path, original_name: str) -> ScanResult:
        scan_id = f"scan_{uuid.uuid4().hex[:12]}"

        try:
            # Read file and convert to base64
            with open(file_path, "rb") as f:
                file_data = base64.b64encode(f.read()).decode("utf-8")

            # Determine media type
            ext = file_path.suffix.lower()
            media_type_map = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".webp": "image/webp",
                ".gif": "image/gif",
                ".bmp": "image/bmp",
                ".pdf": "application/pdf",
            }
            media_type = media_type_map.get(ext, "image/png")

            # Route to appropriate API
            # claude -> Anthropic API, all others (openai/qwen/qiniu/deepseek) -> OpenAI-compatible
            if self.provider == "claude":
                return self._call_claude(scan_id, file_data, media_type)
            else:
                return self._call_openai(scan_id, file_data, media_type)

        except Exception as e:
            return ScanResult(
                scan_id=scan_id,
                status="failed",
                error=str(e),
            )

    def _call_claude_legacy(self, scan_id: str, file_data: str, media_type: str) -> ScanResult:
        """Call Claude API for vision recognition."""
        try:
            import requests

            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }

            body = {
                "model": self.model,
                "max_tokens": 2048,
                "system": self.SYSTEM_PROMPT,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": file_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": "请识别这张钣金图纸，提取报价所需的参数。",
                            },
                        ],
                    }
                ],
            }

            resp = requests.post(
                f"{self.base_url}/v1/messages",
                headers=headers,
                json=body,
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()

            # Extract text from Claude response
            content_blocks = data.get("content", [])
            text = ""
            for block in content_blocks:
                if block.get("type") == "text":
                    text += block.get("text", "")

            return self._parse_response(scan_id, text)

        except Exception as e:
            return ScanResult(scan_id=scan_id, status="failed", error=f"Claude API error: {str(e)}")

    def _call_openai(self, scan_id: str, file_data: str, media_type: str) -> ScanResult:
        """Call OpenAI-compatible vision API."""
        try:
            import urllib.request, json as jmod
            body = jmod.dumps({
                "model": self.model,
                "max_tokens": 2048,
                "messages": [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": [
                        {"type": "text", "text": "请识别这张钣金图纸，提取报价所需的参数。"},
                        {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{file_data}"}}
                    ]}
                ]
            }).encode()
            req = urllib.request.Request(f"{self.base_url}/chat/completions", data=body,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"})
            resp = urllib.request.urlopen(req, timeout=60)
            data = jmod.loads(resp.read())
            text = data["choices"][0]["message"]["content"]
            return self._parse_response(scan_id, text)
        except Exception as e:
            return ScanResult(scan_id=scan_id, status="failed", error=f"Vision API error: {str(e)[:150]}")

    def _call_generic(self, scan_id: str, file_data: str, media_type: str) -> ScanResult:
        """Generic OpenAI-compatible API call (Qwen, etc.)."""
        try:
            import requests

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            body = {
                "model": self.model,
                "max_tokens": 2048,
                "messages": [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "请识别这张钣金图纸，提取报价所需的参数。"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{media_type};base64,{file_data}",
                                },
                            },
                        ],
                    },
                ],
            }

            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=body,
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            return self._parse_response(scan_id, text)

        except Exception as e:
            return ScanResult(scan_id=scan_id, status="failed", error=f"API error: {str(e)}")

    def _parse_response(self, scan_id: str, raw_text: str) -> ScanResult:
        """Parse model response text into structured ScanResult."""
        parsed = self.parse_model_json(raw_text)

        if not parsed or "quotePayload" not in parsed:
            # Try to parse direct JSON
            try:
                parsed = json.loads(raw_text)
            except json.JSONDecodeError:
                return ScanResult(
                    scan_id=scan_id,
                    status="failed",
                    error=f"无法解析模型返回结果: {raw_text[:200]}",
                )

        confidence = float(parsed.get("confidence", 0.5))
        payload_data = parsed.get("quotePayload", {})
        holes = payload_data.get("holes", {})

        payload = QuotePayload(
            thickness=float(payload_data.get("thickness", 0)),
            expand_length=int(payload_data.get("expandLength", 0)),
            expand_width=int(payload_data.get("expandWidth", 0)),
            cut_length=int(payload_data.get("cutLength", 0)),
            bend_count=int(payload_data.get("bendCount", 0)),
            paint_area=float(payload_data.get("paintArea", 0)),
            weld_points=int(payload_data.get("weldPoints", 0)),
            weld_length=int(payload_data.get("weldLength", 0)),
            holes={
                "plain": int(holes.get("plain", 0)),
                "threaded": int(holes.get("threaded", 0)),
                "counterbored": int(holes.get("counterbored", 0)),
            },
        )

        detections = []
        for d in parsed.get("detections", []):
            detections.append(DetectionItem(
                label=d.get("label", ""),
                value=d.get("value", ""),
                confidence=float(d.get("confidence", 0)),
            ))

        return ScanResult(
            scan_id=scan_id,
            status="done",
            confidence=confidence,
            detections=detections,
            quote_payload=payload,
        )
