"""STEP/STP 3D file processor."""
import uuid, os, re, math
from pathlib import Path
from .base import BaseProcessor, DetectionItem, QuotePayload, ScanResult

class StepProcessor(BaseProcessor):
    def process(self, file_path, original_name=""):
        sid = f"scan_{uuid.uuid4().hex[:12]}"
        try:
            # Try trimesh first (faster, more accurate)
            import trimesh, numpy as np
            mesh = trimesh.load(str(file_path), force="mesh")
            if isinstance(mesh, trimesh.Scene):
                meshes = list(mesh.geometry.values())
                if not meshes: return self._text_parse(file_path, sid)
                mesh = trimesh.util.concatenate(meshes)
            bounds = mesh.bounds
            L=round(bounds[1][0]-bounds[0][0]);W=round(bounds[1][1]-bounds[0][1]);H=round(bounds[1][2]-bounds[0][2])
            dims=sorted([abs(L),abs(W),abs(H)])
            T=round(dims[0],1)if dims[0]>0 else 1.5
            area=mesh.area if hasattr(mesh,"area")else L*W
            faces=mesh.faces if hasattr(mesh,"faces")else[]
            holes=int(len(faces)/100)if len(faces)>0 else 0
            return self._make_result(sid,T,L,W,H,round(L*2+W*2),0,holes,round(area/1e6,3))
        except Exception as e:
            return self._text_parse(file_path, sid, str(e)[:80])

    def _text_parse(self, file_path, sid, oe=""):
        try:
            ct=open(file_path,encoding="utf-8",errors="ignore").read()
            pts=re.findall(r"CARTESIAN_POINT.*?\(([\d.\-]+),([\d.\-]+),([\d.\-]+)\)",ct)
            if pts:
                coords=[(float(x),float(y),float(z))for x,y,z in pts]
                xs=sorted(c[0]for c in coords);ys=sorted(c[1]for c in coords);zs=sorted(c[2]for c in coords)
                n=len(coords);lo=max(0,n//20);hi=n-n//20
                L=round(xs[hi]-xs[lo]);W=round(ys[hi]-ys[lo]);H=round(zs[hi]-zs[lo])
                dims=sorted([abs(L),abs(W),abs(H)]);T=round(dims[0],1)if dims[0]>0 else 1.5
            else:L=W=H=0;T=1.5
            # Count unique circles (by entity ID)
            cr=len(set(re.findall(r"#(\d+)=CIRCLE",ct)))
            ln=len(set(re.findall(r"#(\d+)=LINE",ct)))
            # Estimate cut length from line count
            cut=round(L*2+W*2+ln*5)
            return self._make_result(sid,T,L,W,H,cut,max(0,ln//30),cr,round(L*W/1e6,3)if L>0 else 0.01)
        except Exception as e2:
            return ScanResult(sid,"failed",error=f"STEP parse error: {oe} | {str(e2)[:80]}")

    def _make_result(self, sid, T, L, W, H, cut, bends, holes, area):
        payload=QuotePayload(thickness=T,expand_length=L,expand_width=W,cut_length=cut,
            bend_count=bends,paint_area=area,weld_points=0,weld_length=0,
            holes={"plain":holes,"threaded":min(holes//4,5),"counterbored":0})
        detections=[
            DetectionItem(label="板厚",value=f"{T}mm",confidence=0.7),
            DetectionItem(label="展开长",value=f"{L}mm",confidence=0.8),
            DetectionItem(label="展开宽",value=f"{W}mm",confidence=0.8),
            DetectionItem(label="高度",value=f"{H}mm",confidence=0.8),
            DetectionItem(label="切割长度",value=f"{cut}mm",confidence=0.6),
            DetectionItem(label="折弯数(估)",value=str(bends),confidence=0.4),
            DetectionItem(label="光孔数(估)",value=str(holes),confidence=0.5),
        ]
        conf=0.75 if L>0 and W>0 else 0.5
        return ScanResult(sid,"done",confidence=conf,detections=detections,quote_payload=payload)
