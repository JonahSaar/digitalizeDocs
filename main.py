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
# from pdf2image import PDFInfo

import webapp

DOCUMENT_PATH = "public/documents/"
TEMP_PATH = "public/temp/"

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

    jsonFile = open("public/data/" + str(id) + ".json", "w")
    json.dump(meta_data, jsonFile)
    jsonFile.close()

    # Move from scans to temp
    shutil.move("scans/" + file, "public/temp/" + str(id) + ".pdf")


def get_Info(file_list: [str]):
    temp_path = 'public/temp/'
    # define keys
    rechnung = "Rechnung"
    angebot = "Angebot"
    gutachten = "Gutachten"
    text = ""
    # file = ""

    for file in file_list:
        id = uuid.uuid4().hex

        # 1. kopieren
        copyfile('scans/' + file, temp_path + file + "_copy")
        # 2. copy convert
        pdf_to_png(file + "_copy", temp_path)
        # 3. analize copy
        text = pytesseract.image_to_string(Image.open(temp_path + file + "_copy.png"), lang="deu")
        # 4. delete copy
        if os.path.isfile(temp_path + file + "_copy"):
            os.remove(temp_path + file + "_copy")

        if os.path.isfile(temp_path + file + "_copy.png"):
            os.remove(temp_path + file + "_copy.png")
        # Extract Date
        dates = find_date(text)

        #print("Dates found:")
        #print(dates)
        # Find company
        file1 = open('companies.json', 'r')

        companies = json.load(file1)

        found_companies = []

        print(text)

        for company in companies:

            if company in text:


            #if len(findall(company, text, re.IGNORECASE)) > 0:

                print(f"Company found:  {company}")
                # if company is not None:
                found_companies += company

        found_companies = list(dict.fromkeys(found_companies))

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
    # TODO What is this? 
    list = []
    for file in os.listdir("public/temp"):
        if file.endswith('.pdf'):
            id = file.split(".")[0]

            f = open('public/data/' + id + '.json', )
            data = json.load(f)

            """
            id = file.split(".")[0]
            list.append(id)
                """

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
    # TODO COpy + convert
    # What happens if we have multiple pages?
    # just analize the first page
    # then delete it.
    # Store Pdf with convert_from_path function
    print("Read: " + path + filename)
    images = convert_from_path(path + filename)
    # Save pages as images in the pdf
    images[0].save(path + filename + '.png', 'PNG')

"""
def unternehmem_txt_to_json():
    file1 = open('Unternehmen.txt', 'w')
    lines = file1.readlines()
    count = 0
    c = json.load('companies.json')
    for line in lines:
        count += 1
        c.append(line)
"""

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

    date_list += search_date(dd_mm_yyyy_pattern, text)
    date_list += search_date(dd_mm_yyyy_pattern2, text)
    date_list += search_date(yyyy_mm_dd_pattern, text)
    date_list += search_date(yyyy_mm_dd_pattern2, text)

    """
    #date_list.append(search_date(dd_mm_yyyy_pattern, text))

    #dd_mm_yyyy_pattern
    date=search(dd_mm_yyyy_pattern, text)

    date_list.append(search_date(dd_mm_yyyy_pattern, text))

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
    """

    # Mit ausgeschrieben Monat und .
    for month in month_list:
        date_list += search_date("\d{2}." + month + " \d{4}", text)
        # date=search("r'\d{2}."+month+".\d{4}'", text)

    # ate = date.group(0)
    # date_list.append(date)
    # Mit ausgeschrieben Monat und -
    for month in month_list:
        date_list += search_date("\d{2}-" + month + "-\d{4}", text)
    # date=search("r'\d{2}-"+month+"-\d{4}'", text)
    # date = date.group(0)
    # date_list.append(date)

    return list(dict.fromkeys(date_list))


def search_date(pattern, text):
    dates = re.findall(pattern, text, re.IGNORECASE)
    new_dates = []
    if dates:
        for date in dates:
            new_dates.append(date.replace(".", "-"))

    print(new_dates)
    return new_dates


# Save after editing
def save_Final(data):  # data = dic from frontend or json? TODO
    # Final Json
    # "ID": id,
    # "project": project,
    # "company": company,
    # "filepath": file,
    # "category": category,
    # "date": date
    # If folder doesnt exist, create it. Afterwards add file with count if alrady existing 
    if (os.path.isdir(DOCUMENT_PATH + data["project"]) is False):
        os.mkdir(DOCUMENT_PATH + data["project"])

    if (os.path.isdir(DOCUMENT_PATH + data["project"] + '/' + data["category"]) is False):
        os.mkdir(DOCUMENT_PATH + data["project"] + '/' + data["category"])

    if (os.path.isdir(DOCUMENT_PATH + data["project"] + '/' + data["category"] + '/' + data["company"]) is False):
        os.mkdir(DOCUMENT_PATH + data["project"] + '/' + data["category"] + '/' + data["company"])
    """
    if (os.path.isfile(DOCUMENT_PATH + data["project"] + '/' + data["category"] + '/' + data["company"] + "/" + data[
        "date"] + ".pdf") is False):
        shutil.move(TEMP_PATH + data["id"] + ".pdf",
                    DOCUMENT_PATH + data["project"] + '/' + data["category"] + '/' + data["company"] + "/" + data[
                        "date"] + ".pdf")
        return
    """

    # Sonst zähle auf und füge nummer hinzu TODO überarbeiten, dass nur die gezählt werden mit dem datum + Lines deleten nach Scan 
    # Vielleicht einfach alle Dateien mit einem Counter versehen?
    dirs = os.listdir(DOCUMENT_PATH + data["project"] + '/' + data["category"] + '/' + data["company"])
    counter = len(dirs) + 1
    shutil.move(TEMP_PATH + data["id"] + ".pdf",
                DOCUMENT_PATH + data["project"] + '/' + data["category"] + '/' + data["company"] + "/" + data[
                    "date"] + "_"+ str(counter) + ".pdf")


if __name__ == "__main__":

    logging.getLogger("main").info("start")

    webapp = threading.Thread(target=webapp.run)
    webapp.daemon = True
    webapp.start()
    # Wenn bearbeitet dann save final aufrufen TODO
    while True:
        logging.getLogger("main").info("check for new files")
        file_list = read_files()
        get_Info(file_list)
        sleep(5)
