from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import uuid
import os

from analyzer.petal_analyzer import PetalAnalyzer, AnalysisResult, image_to_base64

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

        from fastapi.responses import Response

        return Response(content=overlay_bytes, media_type="image/png")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")
    finally:
        await file.close()
