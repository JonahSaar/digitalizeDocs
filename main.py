import logging
import os
import shutil
import threading
from re import search
import json
from time import sleep

from PIL import Image
import pytesseract

import pdf2image
import datefinder

import webapp

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(name)s - %(levelname)s - %(message)s')


def save_file_temp(file, category: str = "", date: str = ""):
    destination = "public/temp"
    shutil.move("scans/" + file, "public/temp/" + category + "_" + date + ".png")


def get_cat_and_date(file_list):
    # define keyterms
    rechnung = "Rechnung"
    angebot = "Angebot"
    gutachten = "Gutachten"

    for file in file_list:
        text = pytesseract.image_to_string(Image.open('scans/' + file), lang="deu")

        # Extract Date
        date = search(r'\d{2}.\d{2}.\d{4}', text)
        if date is not None:
            save_file_temp(file, rechnung)
        else:
            date = date.group(0)
            date = date.replace(".", "-")
    else:
        date = ""

        # Determine if Rechnung or Angebot or Gutachten
        category_R = search(rechnung, text)
        catergory_A = search(angebot, text)
        catergory_G = search(gutachten, text)

        if category_R is not None:
            save_file_temp(file, rechnung, date)
        elif catergory_A is not None:
            save_file_temp(file, angebot, date)
        elif catergory_G is not Node:
            save_file_temp(file, gutachten, date)


def get_temp_files():
    # TODO
    list = []
    for file in os.listdir("public/temp"):
        if file.endswith('.png'):
            filename = file.split(".")[0]
            params = filename.split("_")
            list.append(
                {
                    "project": "",
                    "company": "",
                    "filepath": file,
                    "category": params[0],
                    "date": params[1]
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
    if file_list:
        print(file_list)
    return file_list


def pdf_to_png (path,filename):
    # What happens if we have multiple pages?
    # just analize the first page
    # then delete it.
    # Store Pdf with convert_from_path function
    images = convert_from_path(filename)
    # Save pages as images in the pdf
    images[0].save(path+"/"+filename+'.png', 'PNG')


def unternehmem_txt_to_json(path: str = "/Unternehmen.txt"):
    file1 = open('Unternehmen.txt', 'w')
    lines = file1.readlines()
    count = 0
    c = json.load(companies.json)
    for line in lines:
        count += 1
        c.update(line)


if __name__ == "__main__":

    logging.getLogger("main").info("start")

    webapp = threading.Thread(target=webapp.run)
    webapp.daemon = True
    webapp.start()

    while True:
        logging.getLogger("main").info("check for new files")
        file_list = read_files()
        get_cat_and_date(file_list)
        sleep(5)
