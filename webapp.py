from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

app = FastAPI()

app.mount("/public/static", StaticFiles(directory="public/static"), name="static")
templates = Jinja2Templates(directory="public/templates")

projects = [{"name": "project 1", "files": ["Rechnung_2021-05-08.pdf", "Rechnung_2021-05-08.pdf", "Rechnung_2021-05-08.pdf"]}]


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "test", "projects": projects})
