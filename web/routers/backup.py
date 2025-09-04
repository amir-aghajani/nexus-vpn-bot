import io
import os
import shutil
import zipfile

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

router = APIRouter(
    prefix="/backup",
    tags=['Data Backups'],
    dependencies=[]
)


@router.get('/download')
async def download_backup():
    folder_path = "data"
    zip_filename = "nexus-backup.zip"

    zip_stream = io.BytesIO()
    with zipfile.ZipFile(zip_stream, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zip_file.write(file_path, arcname)

    zip_stream.seek(0)

    return StreamingResponse(
        zip_stream,
        media_type="application/x-zip-compressed",
        headers={
            "Content-Disposition": f"attachment; filename={zip_filename}"
        }
    )


@router.post("/upload")
async def upload_backup(file: UploadFile = File(...)):
    folder_path = "data"

    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are allowed")

    os.makedirs(folder_path, exist_ok=True)

    temp_zip_path = os.path.join(folder_path, "temp_upload.zip")
    with open(temp_zip_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    with zipfile.ZipFile(temp_zip_path, "r") as zip_ref:
        zip_ref.extractall(folder_path)

    os.remove(temp_zip_path)

    return {"status": "success", "message": f"{file.filename} extracted to {folder_path}"}
