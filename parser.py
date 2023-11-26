from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup as bs
import pymongo


def connectDataBase():
    DB_NAME = "corpus"
    DB_HOST = "localhost"
    DB_PORT = 27017
    try:
        client = pymongo.MongoClient(host=DB_HOST, port=DB_PORT)
        db = client[DB_NAME]
        return db
    except:
        print("Database not connected successfully")


def stemming(input):
    # List of elements for remove...
    rm = ['Title:', 'Title', 'Office:', 'Office', 'Phone:', 'Phone', 'Email:', 'Email', 'Web:', 'Web', ':', ' ']
    for x in range(0, len(rm)):
        try:
            input.remove(rm[x])
        except Exception as error:
            print('No need to stem this word')

    return input


def save_prof_info(db, pf_name, pf_title, pf_office, pf_phone, pf_email, pf_web):
    try:
        col = db.professors
        if pf_name != '':
            doc = {
                "name": pf_name,
                "title": pf_title,
                "office": pf_office,
                "phone": pf_phone,
                "email": pf_email,
                "web": pf_web

            }
            result = col.insert_one(doc)
        else:
            print('This entry is already stored')
        return True
    except Exception as error:
        print("Mongo DB Error")
        return False


def target_page(db):
    try:
        col = db.pages
        pipeline = [
            {'$match': {'title': 'Permanent Faculty'}}
        ]
        docs = col.aggregate(pipeline)
        for data in docs:
            html_source = data['html']
            print(html_source)
        return html_source
    except Exception as error:
        print("Mongo DB Error")
        return None


partial_url_starter = 'https://www.cpp.edu'

## Get DB Connection
db = connectDataBase()

try:
    html_page = target_page(db)
    print(html_page)
except HTTPError as e:
    print(e)
else:
    my_soup = bs(html_page, "html.parser")
    all_prof = my_soup.find_all('div', {"class": "clearfix"})
    for prof in all_prof:
        pf_name = pf_title = pf_office = pf_phone = pf_email = pf_web = ''
        prof_name = prof.find_all('h2')
        for name in prof_name:
            pf_name = name.get_text().strip()
        ptag = prof.find_all('p')
        for p in ptag:
            info_list = p.get_text(strip=True, separator='\n').splitlines()
            clean_list = stemming(info_list)
            pf_title = clean_list[0].replace(':', '').strip()
            pf_office = clean_list[1].replace(':', '').strip()
            pf_phone = clean_list[2].replace(':', '').strip()
            pf_email = clean_list[3].replace(':', '').strip()
            pf_web = partial_url_starter + clean_list[4].replace(':', '').strip()
        print(pf_name, pf_title, pf_office, pf_phone, pf_email, pf_web)
        db_result = save_prof_info(db, pf_name, pf_title, pf_office, pf_phone, pf_email, pf_web)
