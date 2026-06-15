"""Mock processor for development and fallback use."""

import random
import uuid
from pathlib import Path

from .base import BaseProcessor, DetectionItem, QuotePayload, ScanResult


class MockProcessor(BaseProcessor):
    """Returns realistic random data for development and testing."""

    def process(self, file_path: Path, original_name: str) -> ScanResult:
        filename = original_name.lower()
        if "厚" in filename or "thick" in filename:
            thickness = round(random.uniform(0.5, 6.0), 1)
        else:
            thickness = round(random.uniform(0.8, 3.0), 1)

        area_factor = random.uniform(0.5, 2.0)
        expand_length = round(200 + random.randint(100, 600) * area_factor)
        expand_width = round(150 + random.randint(50, 300) * area_factor)
        cut_length = round(800 + random.randint(500, 3000) * area_factor)
        bend_count = random.randint(2, 16)
        paint_area = round(random.uniform(0.1, 1.5) * area_factor, 2)
        weld_points = random.randint(0, 40)
        weld_length = round(random.uniform(0, 500) * area_factor)
        plain_holes = random.randint(0, 20)
        threaded_holes = random.randint(0, 10)
        counterbored_holes = random.randint(0, 6)

        confidence = round(random.uniform(0.5, 0.95), 2)

        payload = QuotePayload(
            thickness=thickness,
            expand_length=expand_length,
            expand_width=expand_width,
            cut_length=cut_length,
            bend_count=bend_count,
            paint_area=paint_area,
            weld_points=weld_points,
            weld_length=weld_length,
            holes={"plain": plain_holes, "threaded": threaded_holes, "counterbored": counterbored_holes},
        )

        detections = [
            DetectionItem(label="板厚", value=f"{thickness} mm", confidence=confidence),
            DetectionItem(label="展开长", value=f"{expand_length} mm", confidence=round(confidence * random.uniform(0.9, 1.0), 2)),
            DetectionItem(label="展开宽", value=f"{expand_width} mm", confidence=round(confidence * random.uniform(0.9, 1.0), 2)),
            DetectionItem(label="切割长度", value=f"{cut_length} mm", confidence=round(confidence * random.uniform(0.85, 1.0), 2)),
            DetectionItem(label="折弯数", value=str(bend_count), confidence=round(confidence * random.uniform(0.8, 1.0), 2)),
            DetectionItem(label="喷涂面积", value=f"{paint_area} ㎡", confidence=round(confidence * random.uniform(0.9, 1.0), 2)),
            DetectionItem(label="焊点数", value=str(weld_points), confidence=round(confidence * random.uniform(0.7, 0.95), 2)),
        ]

        return ScanResult(
            scan_id=f"scan_{uuid.uuid4().hex[:12]}",
            status="done",
            confidence=confidence,
            detections=detections,
            quote_payload=payload,
        )
