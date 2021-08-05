from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

import main

app = FastAPI()

app.mount("/public", StaticFiles(directory="public"), name="static")
templates = Jinja2Templates(directory="public/templates")


@app.get("/", response_class=HTMLResponse)
async def read_files(request: Request):
    return getIndex(request)

@app.post("/", response_class=HTMLResponse)
async def post_file(request: Request, project: str = Form(...), company: str = Form(...), category: str = Form(...), date: str = Form(...)):

    print(project, company, category, date)
    return getIndex(request)


def getIndex(request):
    files = main.get_temp_files()

    companies = main.get_companies()
    projects = main.get_projects()

    return templates.TemplateResponse("index.html", {"request": request, "title": "Digitalize Docs", "projects": projects, "companies": companies, "files": files})
