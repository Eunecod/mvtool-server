# main.py

import os
import json

from typing import cast
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse

LOCK_FILE = "lock.json"

HOST = "127.0.0.1"
PORT = 8000

app: FastAPI = FastAPI(title="mvtool-server")

def get_version() -> str | None:
    try:
        with open(LOCK_FILE, "r", encoding="utf-8") as file:
            data = cast(dict[str, str], json.load(file))
            return data.get("version")
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def get_file_size(filename: str) -> int:
    if os.path.exists(filename):
        return os.path.getsize(filename)
    return 0

@app.get('/update')
async def update() -> JSONResponse:
    version = get_version()
    if not version:
        return JSONResponse(content={"error": "No version found"}, status_code=404)

    response_data: dict[str, str | list[dict[str, str | int]]] = {
        "tag_name": f"v{version}",
        "html_url": f"https://github.com/Eunecod/mvtool-tui/releases/tag/v{version}",
        "assets": [
            {
                "name": "mvtool-x86_64-linux.tar",
                "browser_download_url": f"http://{HOST}:{PORT}/download/mvtool-x86_64-linux.tar",
                "size": get_file_size("./assets/mvtool-x86_64-linux.tar"),
            },
            {
                "name": "mvtool-x86_64-windows.tar",
                "browser_download_url": f"http://{HOST}:{PORT}/download/mvtool-x86_64-windows.tar",
                "size": get_file_size("./assets/mvtool-x86_64-windows.tar"),
            },
        ],
    }
    return JSONResponse(content=response_data)

@app.get("/download/{filename}")
async def download(filename: str) -> FileResponse:
    safe_filename = os.path.basename(filename)
    safe_path = os.path.join(".", "assets", safe_filename)

    if not os.path.exists(safe_path):
        raise HTTPException(status_code=404, detail="Файл обновления не найден")

    return FileResponse(
        path=safe_path,
        media_type="application/octet-stream",
        filename=safe_filename,
    )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=HOST, port=PORT)
