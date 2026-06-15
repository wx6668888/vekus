"""DXF file processor — parses CAD drawings for sheet metal parameters."""
import uuid, re, math
from pathlib import Path
from .base import BaseProcessor, DetectionItem, QuotePayload, ScanResult

class DxfProcessor(BaseProcessor):
    """Parses DXF files using ezdxf to extract sheet metal parameters."""
    def process(self, file_path: Path, original_name: str) -> ScanResult:
        scan_id = f"scan_{uuid.uuid4().hex[:12]}"
        try:
            import ezdxf
            doc = ezdxf.readfile(str(file_path))
            msp = doc.modelspace()
            lines, arcs, circles, lwpolylines, dimensions = [], [], [], [], []
            for entity in msp:
                t = entity.dxftype()
                if t == 'LINE': lines.append(entity)
                elif t == 'ARC': arcs.append(entity)
                elif t == 'CIRCLE': circles.append(entity)
                elif t == 'LWPOLYLINE': lwpolylines.append(entity)
                elif t in ('DIMENSION','DIMLINEAR','DIMALIGNED','DIMANGULAR','DIMRADIUS','DIMDIAMETER'):
                    dimensions.append(entity)
            # Hole detection
            hole_circles = [c for c in circles if hasattr(c.dxf,'layer') and ('HOLE' in c.dxf.layer.upper() or 'KONG' in c.dxf.layer.upper())]
            if not hole_circles: hole_circles = [c for c in circles if c.dxf.radius < 50]
            threaded = [c for c in hole_circles if c.dxf.radius < 4]
            plain = [c for c in hole_circles if c not in threaded]
            # Bend count
            bend_arcs = [a for a in arcs if hasattr(a.dxf,'layer') and 'BEND' in a.dxf.layer.upper()]
            bend_count = len(bend_arcs) if bend_arcs else len(arcs)
            # Bounding box
            all_pts = []
            for ln in lines: all_pts.extend([(ln.dxf.start.x,ln.dxf.start.y),(ln.dxf.end.x,ln.dxf.end.y)])
            for pl in lwpolylines:
                try:
                    pts = list(pl.get_points('xyb'))
                    all_pts.extend([(p[0],p[1]) for p in pts])
                except: pass
            if all_pts:
                xs=[p[0] for p in all_pts]; ys=[p[1] for p in all_pts]
                length=round(max(xs)-min(xs)); width=round(max(ys)-min(ys))
            else: length=width=0
            # Cut length
            cut=0
            for ln in lines:
                cut+=math.dist((ln.dxf.start.x,ln.dxf.start.y),(ln.dxf.end.x,ln.dxf.end.y))
            for pl in lwpolylines:
                try:
                    pts=list(pl.get_points('xyb'))
                    for i in range(len(pts)-1): cut+=math.dist(pts[i][:2],pts[i+1][:2])
                except: pass
            # Thickness from text
            thickness=0
            try:
                for e in msp.query('TEXT MTEXT'):
                    txt=getattr(e,'text','') or getattr(e,'plain_text','')
                    if 'mm' in txt.lower() or 'hou' in txt.lower():
                        nums=re.findall(r'[\d.]+',txt)
                        if nums: thickness=float(nums[0]); break
            except: pass
            if thickness==0: thickness=1.5
            payload = QuotePayload(
                thickness=round(thickness,1), expand_length=length, expand_width=width,
                cut_length=round(cut), bend_count=bend_count,
                paint_area=round(length*width/1e6,3), weld_points=0, weld_length=0,
                holes={"plain":len(plain),"threaded":len(threaded),"counterbored":0}
            )
            detections = [
                DetectionItem(label="板厚",value=f"{thickness}mm",confidence=0.7),
                DetectionItem(label="展开长",value=f"{length}mm",confidence=0.9 if length>0 else 0.3),
                DetectionItem(label="展开宽",value=f"{width}mm",confidence=0.9 if width>0 else 0.3),
                DetectionItem(label="切割长度",value=f"{round(cut)}mm",confidence=0.8),
                DetectionItem(label="折弯数",value=str(bend_count),confidence=0.7),
                DetectionItem(label="光孔数",value=str(len(plain)),confidence=0.85),
                DetectionItem(label="螺纹孔数",value=str(len(threaded)),confidence=0.7),
            ]
            conf = min(0.95, (len(lines)+len(circles))/100)
            return ScanResult(scan_id=scan_id, status="done", confidence=conf,
                              detections=detections, quote_payload=payload)
        except Exception as e:
            return ScanResult(scan_id=scan_id, status="failed", error=f"DXF parse error: {str(e)[:150]}")
