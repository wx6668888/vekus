"""Processor factory — selects the right processor based on config and file type."""

import os
from pathlib import Path

from .base import BaseProcessor
from .mock_processor import MockProcessor
from .vision_processor import VisionProcessor
from .dxf_processor import DxfProcessor
from .dwg_processor import DwgProcessor
from .step_processor import StepProcessor


def create_processor(file_path: Path, original_name: str = "") -> BaseProcessor:
    """Create the appropriate processor for the given file type.

    Routing:
    - .dxf → DxfProcessor (ezdxf structural parse, 2D)
    - .step/.stp/.iges/.igs → StepProcessor (trimesh 3D analysis)
    - .stl/.obj → StepProcessor (mesh analysis)
    - .png/.jpg/.pdf → VisionProcessor (AI vision)
    - .dwg/.sldprt/.x_t → VisionProcessor (AI vision attempt, may fail)
    """
    provider = os.getenv("VEKUS_AI_PROVIDER", "mock").lower()
    if provider == 'mock':
        return MockProcessor()

    ext = file_path.suffix.lower()
    if ext == '.dxf':
        return DxfProcessor()
    if ext in ('.step', '.stp', '.iges', '.igs'):
        return StepProcessor()
    if ext in ('.stl', '.obj'):
        return StepProcessor()
    if ext in ('.dwg', '.sldprt', '.sldasm', '.x_t'):
        return DwgProcessor()
    return VisionProcessor(provider=provider)

