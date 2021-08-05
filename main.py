import os
import shutil
from re import search
import PyPDF4
import json
import PIL
from PIL import Image
import pytesseract


def save_file_temp(file: str, category: str = "none", date: str = "none"):
    destination = "public/temp"
    shutil.move("scans/" + file, "public/temp/" + category + "_" + date + ".png")


def get_cat_and_date(file_list):
    # define keyterms
    Rechnung1 = "Rechnung"
    Rechnung2 = "RECHNUNG"
    Angebot1 = "Angebot"
    Angebot2 = "ANGEBOT"

    for file in file_list:
        text = pytesseract.image_to_string(Image.open('scans/' + file), lang="deu")
        # extract text and do the search

        category_R1 = search(Rechnung1, text)
        catergory_A1 = search(Angebot1, text)
        if category_R1 != None:
            date = search(r'\d{2}.\d{2}.\d{4}', text)
            print(date)
            if date is None:
                save_file_temp(file, Rechnung1)
            else:
                save_file_temp(file, Rechnung1, date.group(0))
            continue
        if catergory_A1 != None:
            date = search(r'\d{2}-\d{2}-\d{4}', text)
            save_file_temp(file, Angebot1, date)


def get_temp_files():
    list = []
    for file in os.listdir("public/temp"):
        list.append(
            {
                "project": "Projekt A",
                "company": "Peter baut Tief",
                "filepath": "Test.pdf",
                "category": "Rechnung",
                "date": "02-02-2021"
            }
        )

    return list


def set_companies(company_name):
    f = open('companies.json', )
    data = json.load(f)
    data.append(company_name)
    with open('companies.json', "w") as company:
        json.dump(data, company)


def get_companies():
    f = open('companies.json', )
    data = json.load(f)
    f.close()
    return data


def set_projects(project_name):
    f = open('projects.json', )
    data = json.load(f)
    data.append(project_name)
    with open('projects.json', "w") as project:
        json.dump(data, project)


def get_projects():
    f = open('projects.json', )
    data = json.load(f)
    f.close()
    return data


def read_files():
    # Folder scan
    path = "scans"
    dirs = os.listdir(path)
    dirs.sort()
    file_list = []
    # Liste an zu kontrollierenden Files erstellen
    for file in dirs:
        if file.endswith('.png'):
            file_list.append(file)
    print(file_list)
    return file_list


if __name__ == "__main__":
    file_list = read_files()
    get_cat_and_date(file_list)
