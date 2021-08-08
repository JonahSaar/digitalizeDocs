import logging
import os
import shutil
import threading
from re import search
import json
import uuid
from time import sleep

from PIL import Image
import pytesseract

from pdf2image import convert_from_path

import webapp

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(name)s - %(levelname)s - %(message)s')

def png_to_pdf(png_file, path):
    png_file = Image.open(path)
    pdf_file = png_file.convert('RGB')
    pdf_file.save(path)

def save_file_temp(file, id):
    shutil.move("scans/" + file, "public/temp/" +id+ ".pdf")


def get_cat_and_date(file_list):
    #define keys
    rechnung = "Rechnung" 
    angebot = "Angebot"
    gutachten = "Gutachten"
    text = ""
    file = ""
    id = uuid.uuid4
    for file in file_list:
        file = pdf_to_png(file, 'scans/')
        text = pytesseract.image_to_string(Image.open('scans/' + file), lang="deu")
        file= png_to_pdf(file, 'scans/')
        # Extract Date
        date = search(r'\d{2}.\d{2}.\d{4}', text)
        if date is not None:
            save_file_temp(file, id)
        else:
            date = date.group(0)
            date = date.replace(".", "-")
    else:
        date = ""

        # Determine if Rechnung or Angebot or Gutachten
        category_r = search(rechnung, text)
        catergory_a = search(angebot, text)
        catergory_g = search(gutachten, text)

        if category_r is not None:
            save_file_temp(file, id)
        elif catergory_a is not None:
            save_file_temp(file, id)
        elif catergory_g is not None:
            save_file_temp(file, id)


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
        if file.endswith('.pdf'):
            file_list.append(file)
    if file_list:
        print(file_list)
    return file_list


def pdf_to_png(filename, path):
    # What happens if we have multiple pages?
    # just analize the first page
    # then delete it.
    # Store Pdf with convert_from_path function
    images = convert_from_path(filename)
    # Save pages as images in the pdf
    images[0].save(path + "/" + filename + '.png', 'PNG')


def unternehmem_txt_to_json():
    file1 = open('Unternehmen.txt', 'w')
    lines = file1.readlines()
    count = 0
    c = json.load('companies.json')
    for line in lines:
        count += 1
        c.append(line)


def find_date(text):
    month_list = ['Januar', 'januar', 'Februar', 'februar', 'März', 'märz', 'April', 'mai', 'Mai',
                  'juni', 'Juni', 'juli', 'Juli', 'august', 'August', 'September',
                  'september', 'oktober', 'Oktober','november', 'November', 'dezember', 'Dezember']
    dd_mm_yyyy_pattern = "r'\d{2}.\d{2}.\d{4}'"
    dd_mm_yyyy_pattern2 = "r'\d{2}-\d{2}-\d{4}'"
    yyyy_mm_dd_pattern =  "r'\d{4}.\d{2}.\d{2}'"
    yyyy_mm_dd_pattern2 = "r'\d{4}-\d{2}-\d{2}'"
    date_list = []
    #dd_mm_yyyy_pattern
    date=search(dd_mm_yyyy_pattern, text)
    date = date.group(0)
    date_list.append(date)
    #dd_mm_yyyy_pattern2
    date=search(dd_mm_yyyy_pattern2, text)
    date = date.group(0)
    date = date.replace(".", "-")
    date_list.append(date)
    #yyyy_mm_dd_pattern
    date=search(yyyy_mm_dd_pattern, text)
    date = date.group(0)
    date_list.append(date)
    #yyyy_mm_dd_pattern2
    date=search(yyyy_mm_dd_pattern2, text)
    date = date.group(0)
    date = date.replace(".", "-")
    date_list.append(date)
    #Mit ausgeschrieben Monat und . 
    for month in month_list: 
        date=search("r'\d{2}."+month+".\d{4}'", text)
    date = date.group(0)
    date_list.append(date)
    #Mit ausgeschrieben Monat und - 
    for month in month_list: 
        date=search("r'\d{2}-"+month+"-\d{4}'", text)
    date = date.group(0)
    date_list.append(date)

if __name__ == "__main__":

    logging.getLogger("main").info("start")

    webapp = threading.Thread(target=webapp.run)
    webapp.daemon = True
    webapp.start()

    while True:s
        logging.getLogger("main").info("check for new files")
        file_list = read_files()
        get_cat_and_date(file_list)
        sleep(5)
