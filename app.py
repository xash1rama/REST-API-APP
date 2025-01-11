from starlette.responses import HTMLResponse, FileResponse
from pathlib import Path
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from routers.rout_build import router as build_rout
from routers.rout_activity import router as activity_rout
from routers.rout_organization import router as organization_rout
from setup import lifespan

app = FastAPI(lifespan=lifespan)

app.include_router(build_rout)
app.include_router(activity_rout)
app.include_router(organization_rout)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    file_path = Path("static/main.html")
    return FileResponse(file_path, media_type='text/html')