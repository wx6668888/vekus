"""DWG/SLDPRT/x_t processor — format guidance and conversion attempt."""
import uuid, subprocess, os, shutil
from pathlib import Path
from .base import BaseProcessor, DetectionItem, QuotePayload, ScanResult

class DwgProcessor(BaseProcessor):
    def process(self, file_path: Path, original_name: str) -> ScanResult:
        sid = f"scan_{uuid.uuid4().hex[:12]}"
        ext = file_path.suffix.lower()
        
        # Try to convert DWG using available tools
        if ext == ".dwg":
            # Try libreDWG dwg2dxf
            if shutil.which("dwg2dxf"):
                try:
                    dxf_path = file_path.with_suffix(".dxf")
                    subprocess.run(["dwg2dxf", str(file_path), str(dxf_path)], timeout=30, capture_output=True)
                    if dxf_path.exists():
                        from .dxf_processor import DxfProcessor
                        return DxfProcessor().process(dxf_path, original_name)
                except: pass
            
            # Try ODA FileConverter
            oda_paths = ["/usr/bin/ODAFileConverter", "/opt/oda/ODAFileConverter", "/usr/local/bin/ODAFileConverter"]
            for oda in oda_paths:
                if os.path.exists(oda):
                    try:
                        outdir = file_path.parent / "oda_out"
                        outdir.mkdir(exist_ok=True)
                        subprocess.run([oda, str(file_path.parent), str(outdir), "ACAD2018", "DXF", "0", "1"], timeout=60)
                        dxf_files = list(outdir.glob("*.dxf"))
                        if dxf_files:
                            from .dxf_processor import DxfProcessor
                            return DxfProcessor().process(dxf_files[0], original_name)
                    except: pass
            
            return ScanResult(sid, "failed", 
                f"DWG格式需转换。请安装libreDWG: sudo apt install libredwg-tools，或在CAD中导出为DXF后上传。")

        if ext in (".sldprt", ".x_t", ".sldasm"):
            return ScanResult(sid, "failed",
                f"{ext.upper()}是私有3D格式，无法直接解析。请用SolidWorks/NX导出为STEP格式后上传。")

        return ScanResult(sid, "failed", f"不支持的格式: {ext}")
