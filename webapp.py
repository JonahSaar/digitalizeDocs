from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

import main

app = FastAPI()

app.mount("/public", StaticFiles(directory="public"), name="static")
templates = Jinja2Templates(directory="public/templates")


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):

    files = main.get_temp_files()

    companies = main.get_companies()
    projects = main.get_projects()

    return templates.TemplateResponse("index.html", {"request": request, "title": "Digitalize Docs", "projects": projects, "companies": companies, "files": files})


