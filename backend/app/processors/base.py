"""Base processor interface for drawing recognition."""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class DetectionItem:
    label: str
    value: str
    confidence: float


@dataclass
class QuotePayload:
    thickness: float = 0
    expand_length: int = 0
    expand_width: int = 0
    cut_length: int = 0
    bend_count: int = 0
    paint_area: float = 0
    weld_points: int = 0
    weld_length: int = 0
    holes: dict = field(default_factory=lambda: {"plain": 0, "threaded": 0, "counterbored": 0})

    def to_dict(self) -> dict:
        return {
            "thickness": self.thickness,
            "expandLength": self.expand_length,
            "expandWidth": self.expand_width,
            "cutLength": self.cut_length,
            "bendCount": self.bend_count,
            "paintArea": self.paint_area,
            "weldPoints": self.weld_points,
            "weldLength": self.weld_length,
            "holes": self.holes,
        }


@dataclass
class ScanResult:
    scan_id: str
    status: str  # done / processing / failed
    confidence: float = 0
    detections: list[DetectionItem] = field(default_factory=list)
    quote_payload: QuotePayload = field(default_factory=QuotePayload)
    error: str = ""

    def to_dict(self) -> dict:
        return {
            "scanId": self.scan_id,
            "status": self.status,
            "confidence": self.confidence,
            "detections": [{"label": d.label, "value": d.value, "confidence": d.confidence} for d in self.detections],
            "quotePayload": self.quote_payload.to_dict(),
            "error": self.error,
        }


class BaseProcessor(ABC):
    """Abstract base for all drawing recognition processors."""

    @abstractmethod
    def process(self, file_path: Path, original_name: str) -> ScanResult:
        """Process a file and return standardized scan result."""
        ...

    @staticmethod
    def parse_model_json(raw_text: str) -> dict[str, Any]:
        """Attempt to parse JSON from model response text."""
        # Try to find JSON block
        import re
        json_match = re.search(r'\{[\s\S]*\}', raw_text)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        return {}
