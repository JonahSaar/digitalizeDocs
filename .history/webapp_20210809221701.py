import json
import logging

import uvicorn
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
async def post_file(request: Request, project: str = Form(...), company: str = Form(...), category: str = Form(...), date: str = Form(...), id: str = Form(...)):
    try:
        checkCompany(company)
        checkProject(project)

        data = { "project": project, "company": company, "category": category, "date": date, "id": id }

        main.save_Final(data)
    except Exception:
        pass

    return getIndex(request)


def getIndex(request):
    files = main.get_temp_files()
    companies = main.get_companies()
    projects = main.get_projects()

    return templates.TemplateResponse("index.html",
                                      {
                                          "request": request,
                                          "title": "Digitalize Docs",
                                          "projects": projects,
                                          "companies": companies,
                                          "files": files
                                        }
                                      )


def checkProject(project):
    with open("projects.json", "r") as jsonFile:
        projects = json.load(jsonFile)
        jsonFile.close()

        print(projects)

        if project not in projects:

            projects.append(project)
            print(projects)
            with open("projects.json", "w") as jsonFile:
                json.dump(projects, jsonFile)
                jsonFile.close()






def checkCompany(company):
    pass

def run():
    logging.getLogger("webapp").info("starting webapp")
    uvicorn.run(app, host="127.0.0.1", port="8000", log_level="warning")
