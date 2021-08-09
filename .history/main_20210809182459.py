import logging
import os
import re
import shutil
import threading
from re import findall
import json
import uuid
from time import sleep
from shutil import copyfile
from PIL import Image
import pytesseract

from pdf2image import convert_from_path
import os.path as osp
import subprocess
import webapp

DOCUMENT_PATH = "public/documents/" 
TEMP_PATH = "public/temp/"
SCANS_PATH = "scans/"
DATA_PATH = "public/data/"

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(name)s - %(levelname)s - %(message)s')
filesData = []  # Nested Dic


# We need a dic before and a dic after
def save_file_temp(file, id, companies, category, dates):
    # Save json
    meta_data = {
        "id": str(id),
        "project": "",
        "company": companies,
        "category": category,
        "date": dates
    }

    jsonFile = open(DATA_PATH + str(id) + ".json", "w")
    json.dump(meta_data, jsonFile)
    jsonFile.close()

    # Move from scans to temp
    shutil.move(SCANS_PATH + file, "public/temp/" + str(id) + ".pdf")


def get_Info(file_list):
    # define keys
    rechnung = "Rechnung"
    angebot = "Angebot"
    gutachten = "Gutachten"
    text = ""
    # file = ""

    for file in file_list:
        id = uuid.uuid4().hex

        # 1. kopieren
        copyfile(SCANS_PATH + file, TEMP_PATH + file + "_copy")
        # 2. copy convert
        pdf_to_png(file + "_copy", TEMP_PATH)
        # 3. analize copy
        text = pytesseract.image_to_string(Image.open (TEMP_PATH + file + "_copy.png"), lang="deu")
        # 4. delete copy
        if os.path.isfile (TEMP_PATH + file + "_copy"):
            os.remove (TEMP_PATH + file + "_copy")

        if os.path.isfile (TEMP_PATH + file + "_copy.png"):
            os.remove (TEMP_PATH + file + "_copy.png")
        # Extract Date
        dates = find_date(text)

        # Find company
        file1 = open('companies.json', 'r')

        companies = json.load(file1)

        found_companies = []

        print(text)

        found_companies = findall(r'(?:\w(?:\, ?| |(?: ?\& ?)|-|\. ?)?)*)(?:Bautenschutz|Architekturbüro|Abruch-Entsorgungskonzepte|Elektroinstallation|mbH|Versorgungstechnik|Fliesenlegermeister|Bedachungen|Bauelemente|Golaschewski|Malerfachbetrieb|Fugentechnik|Trockenbau|GbR|e.?K.?|GmbH|AG|AkNW|AKNW|SE|(?:GmbH.?&.?Co.?KG)))',text)
        found_companies = list(dict.fromkeys(found_companies))
        found_companies += findall(r'?i)(?:\bINGENIEURBÜRO|Projektbau|Architekturbüro|Fugentechnik\b) ((?:\w.?)*))',text)
        found_companies = list(dict.fromkeys(found_companies))

        print(found_companies)

        # Determine if Rechnung or Angebot or Gutachten
        category_r = findall(rechnung, text)
        catergory_a = findall(angebot, text)
        catergory_g = findall(gutachten, text)

        category_r = list(dict.fromkeys(category_r))
        catergory_a = list(dict.fromkeys(catergory_a))
        catergory_g = list(dict.fromkeys(catergory_g))

        if category_r is not None:
            save_file_temp(file, id, found_companies, category_r, dates)
        elif catergory_a is not None:
            save_file_temp(file, id, found_companies, catergory_a, dates)
        elif catergory_g is not None:
            save_file_temp(file, id, found_companies, catergory_a, dates)


def get_temp_files():
    list = []
    for file in os.listdir (TEMP_PATH):
        if file.endswith('.pdf'):
            id = file.split(".")[0]

            f = open(DATA_PATH + id + '.json', )
            data = json.load(f)

            list.append(
                {
                    "path": file,
                    "data": data
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
    dirs = os.listdir(SCANS_PATH)
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
    print("Read: " + path + filename)
    images = convert_from_path(path + "/" +filename)
    images[0].save(path + filename + '.png', 'PNG')


def find_date(text):
    months = [
        [
            "Januar", "1", "01", "january", "januar"
        ], [
            "Januar", "1", "01", "january", "januar"
        ], [
            "Januar", "1", "01", "january", "januar"
        ]
    ]

    month_list = ['Januar', 'januar', 'Februar', 'februar', 'März', 'märz', 'April', 'mai', 'Mai',
                  'juni', 'Juni', 'juli', 'Juli', 'august', 'August', 'September',
                  'september', 'oktober', 'Oktober', 'november', 'November', 'dezember', 'Dezember']
    dd_mm_yyyy_pattern = "\d{2}.\d{2}.\d{4}"
    dd_mm_yyyy_pattern2 = "\d{2}-\d{2}-\d{4}"
    yyyy_mm_dd_pattern = "\d{4}.\d{2}.\d{2}"
    yyyy_mm_dd_pattern2 = "\d{4}-\d{2}-\d{2}"
    date_list = []

    date_list += list(dict.fromkeys(search_date(dd_mm_yyyy_pattern, text)))
    date_list += list(dict.fromkeys(search_date(dd_mm_yyyy_pattern2, text)))
    date_list += list(dict.fromkeys(search_date(yyyy_mm_dd_pattern, text)))
    date_list += list(dict.fromkeys(search_date(yyyy_mm_dd_pattern2, text)))

    # Mit ausgeschrieben Monat und .
    for month in month_list:
        date_list += search_date("\d{2}." + month + " \d{4}", text)
    for month in month_list:
        date_list += search_date("\d{2}-" + month + "-\d{4}", text)

    return list(dict.fromkeys(date_list)) #Schmeißt sofort alle duplikate raus


def search_date(pattern, text):
    dates = re.findall(pattern, text, re.IGNORECASE)
    new_dates = []
    if dates:
        for date in dates:
            new_dates.append(date.replace(".", "-"))

    print(new_dates)
    return new_dates


# Save after editing
def save_Final(data):  
    # If folder doesnt exist, create it. Afterwards add file with count if alrady existing 
    if (os.path.isdir(DOCUMENT_PATH + data["project"]) is False):
        os.mkdir(DOCUMENT_PATH + data["project"])

    if (os.path.isdir(DOCUMENT_PATH + data["project"] + '/' + data["category"]) is False):
        os.mkdir(DOCUMENT_PATH + data["project"] + '/' + data["category"])

    if (os.path.isdir(DOCUMENT_PATH + data["project"] + '/' + data["category"] + '/' + data["company"]) is False):
        os.mkdir(DOCUMENT_PATH + data["project"] + '/' + data["category"] + '/' + data["company"])

    #Save with counter 
    dirs = os.listdir(DOCUMENT_PATH + data["project"] + '/' + data["category"] + '/' + data["company"])
    counter = len(dirs) + 1
    shutil.move (TEMP_PATH + data["id"] + ".pdf",
                DOCUMENT_PATH + data["project"] + '/' + data["category"] + '/' + data["company"] + "/" + data[
                    "date"] + "_"+ str(counter) + ".pdf")


if __name__ == "__main__":

    logging.getLogger("main").info("start")

    webapp = threading.Thread(target=webapp.run)
    webapp.daemon = True
    webapp.start()
    while True:
        logging.getLogger("main").info("check for new files")
        file_list = read_files()
        get_Info(file_list)
        sleep(5)
