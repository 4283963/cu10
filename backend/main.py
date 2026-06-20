from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from typing import Optional, List
from pydantic import BaseModel
import uuid
import os
import json

from analyzer.petal_analyzer import (
    PetalAnalyzer,
    AnalysisResult,
    image_to_base64,
    export_results_to_excel,
)

app = FastAPI(
    title="花瓣形态学分析系统 API",
    description="植物园标本馆花期标本花瓣多维形态学分析系统",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = PetalAnalyzer()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
async def root():
    return {"message": "花瓣形态学分析系统 API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


def validate_image_file(file: UploadFile) -> bool:
    if file.content_type and file.content_type.startswith("image/"):
        return True
    filename = file.filename or ""
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff'}
    return any(filename.lower().endswith(ext) for ext in allowed_extensions)


@app.post("/api/analyze")
async def analyze_image(file: UploadFile = File(...)):
    if not validate_image_file(file):
        raise HTTPException(status_code=400, detail="请上传图片文件")

    try:
        contents = await file.read()

        result = analyzer.analyze(contents)

        overlay_bytes = analyzer.generate_overlay_image(contents, result)
        overlay_base64 = image_to_base64(overlay_bytes)

        original_base64 = image_to_base64(contents)

        return {
            "success": True,
            "data": {
                **result.to_dict(),
                "original_image": original_base64,
                "overlay_image": overlay_base64,
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")
    finally:
        await file.close()


@app.post("/api/analyze/preview")
async def analyze_preview(file: UploadFile = File(...)):
    if not validate_image_file(file):
        raise HTTPException(status_code=400, detail="请上传图片文件")

    try:
        contents = await file.read()

        result = analyzer.analyze(contents)

        return {
            "success": True,
            "data": result.to_dict(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")
    finally:
        await file.close()


@app.post("/api/analyze/overlay")
async def get_overlay_image(file: UploadFile = File(...)):
    if not validate_image_file(file):
        raise HTTPException(status_code=400, detail="请上传图片文件")

    try:
        contents = await file.read()

        result = analyzer.analyze(contents)
        overlay_bytes = analyzer.generate_overlay_image(contents, result)

        return Response(content=overlay_bytes, media_type="image/png")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")
    finally:
        await file.close()


class ExcelExportItem(BaseModel):
    filename: str
    result: dict


@app.post("/api/export/excel")
async def export_excel(items: List[ExcelExportItem]):
    try:
        results = []
        filenames = []
        
        for item in items:
            r = item.result
            result = AnalysisResult(
                vein_count=int(r.get("vein_count", 0)),
                serration_area=float(r.get("serration_area", 0)),
                serration_count=int(r.get("serration_count", 0)),
                petal_area=float(r.get("petal_area", 0)),
                petal_perimeter=float(r.get("petal_perimeter", 0)),
                circularity=float(r.get("circularity", 0)),
                shape_type=str(r.get("shape_type", "未知")),
                shape_score=r.get("shape_score", {"圆形": 0.0, "尖形": 0.0, "波浪形": 0.0}),
                contours=r.get("contours", []),
                vein_points=r.get("vein_points", []),
                serration_points=r.get("serration_points", []),
                original_width=int(r.get("original_width", 0)),
                original_height=int(r.get("original_height", 0)),
            )
            results.append(result)
            filenames.append(item.filename)

        excel_bytes = export_results_to_excel(results, filenames)
        
        filename = f"花瓣形态分析结果_{uuid.uuid4().hex[:8]}.xlsx"
        
        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")
