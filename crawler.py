from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import pymongo
import datetime


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


def target_page(url_seed, url):
    if url.startswith("/sci/computer-science/"):
        url = url_seed + url

    html = urlopen(url)
    bs = BeautifulSoup(html.read(), "html.parser")
    tag_h1 = bs.find('h1', {"class": "cpp-h1"})

    if tag_h1:
        returnstr = tag_h1.get_text()
    else:
        returnstr = ''

    return returnstr


def store_page(url_seed, url, page_title):
    db = connectDataBase()
    col = db.pages

    if url.startswith("/sci/computer-science/"):
        url = url_seed + url

    html_obj = urlopen(url)
    bs = BeautifulSoup(html_obj.read(), "html.parser")
    html_text = bs.find_all('html')

    doc = {
        "url": url,
        "title": page_title,
        "html": str(html_text),
    }

    result = col.insert_one(doc)


def append_seeds(url_seed, frontier_queue, url_string):
    if url_string in frontier_queue:
        print('Already Visited')
    else:
        if url_string.startswith("/sci/computer-science/"):
            url_string = url_seed + url_string
        frontier_queue.append(url_string)
    return frontier_queue


frontier = ['https://www.cpp.edu/sci/computer-science/']
url_seed = 'https://www.cpp.edu'

try:
    html_page = urlopen(frontier[0])
except HTTPError as e:
    print(e)
else:
    bs = BeautifulSoup(html_page.read(), "html.parser")
    all_links = bs.find_all('a', {})
    for link in all_links:
        inner_link = link.get("href")
        if str(inner_link).startswith("/sci/computer-science/") or str(inner_link).startswith("http"):
            frontier = append_seeds(url_seed, frontier, inner_link)
            title = target_page(url_seed, inner_link)
            print(title)
            store_page(url_seed, inner_link, title)
            if str(title).strip() == 'Permanent Faculty':
                print("STOPPING! FOUND TARGET PAGE")
                frontier.clear()
                break
