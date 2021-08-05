import os
from re import search
import PyPDF4
import json

# Folder scan
path ="/"
dirs = os.listdir(path)
dirs.sort()
checks = []
# Liste an zu kontrollierenden Files erstellen
for file in dirs:
    if file.endswith('.pdf'):
        checks.append(file)

# define keyterms
String1 = "Rechnung"
String2 = "Angebot"
String4 = "Test"
for check in checks:
    pdfFileObj = open(check, 'rb')
    # open the pdf file
    object = PyPDF4.PdfFileReader(pdfFileObj)
    # get number of pages
    NumPages = object.getNumPages()
    # extract text and do the search
    for i in range(0, NumPages):
        PageObj = object.getPage(i)
        Text = PageObj.extractText()
        # print(Text)
        ResSearch1 = search(String1, Text)
        ResSearch2 = search(String1, Text)
        if ResSearch1=="Rechnung":
            # TODO Dann kontrolliere nach Datum
            #anschließend speichere es ab
            pass
        if ResSearch2== "Angebot":
            # TODO s.o
            pass


def get_temp_files():

    list = []
    for file in os.listdir("public/temp"):

        list.append(
            {
                "project": "",
                "company": "",
                "filepath": "",
                "category": "",
                "date": "",
            }
        )


    return list


def get_companies():
    f = open('companies.json', )
    data = json.load(f)
    f.close()
    return data


def get_projects():
    f = open('projects.json', )
    data = json.load(f)
    f.close()
    return data
