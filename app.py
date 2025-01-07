from starlette.responses import HTMLResponse, FileResponse
from pathlib import Path
from fastapi import FastAPI
from routers.rout_build import router as build_rout
from routers.rout_activity import router as activity_rout
from routers.rout_organization import router as organization_rout
from setup import lifespan

app = FastAPI(lifespan=lifespan)

app.include_router(build_rout)
app.include_router(activity_rout)
app.include_router(organization_rout)


@app.get("/", response_class=HTMLResponse)
async def read_root():
    file_path = Path("static/image.png")
    return FileResponse(file_path, status_code=200)
