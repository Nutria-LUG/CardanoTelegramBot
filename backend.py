#!/usr/bin/python
# -*- coding: utf-8 -*-


""" Fetch and classify notices from Itis G. Cardano website """


import requests, sqlite3, os, urllib2
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
from bs4 import BeautifulSoup
from hashlib import md5


BASE_URL = "http://circolari.cardano.pv.it/famiglie"
URL = "http://circolari.cardano.pv.it/famiglie/leggiavvisi.php"
DB_FILE_PATH = "./cardanobot.db"
PDF_FILES_BASE_PATH = "./pdfs/"
SCHOOL_CLASSES = ['1AI', '1AE', '1AM', '1ALS', '1AC', '1BI', '1BE', '1BM', '1BLS', '1BC', '1CI', '1CE', '1CM', '1CLS', '1CC', '1DI', '1DE', '1DM', '1DLS', '1DC', '1EI', '1EE', '1EM', '1ELS', '1EC', '1FI', '1FE', '1FM', '1FLS', '1FC', '1GI', '1GE', '1GM', '1GLS', '1GC', '1HI', '1HE', '1HM', '1HLS', '1HC', '1II', '1IE', '1IM', '1ILS', '1IC', '2AI', '2AE', '2AM', '2ALS', '2AC', '2BI', '2BE', '2BM', '2BLS', '2BC', '2CI', '2CE', '2CM', '2CLS', '2CC', '2DI', '2DE', '2DM', '2DLS', '2DC', '2EI', '2EE', '2EM', '2ELS', '2EC', '2FI', '2FE', '2FM', '2FLS', '2FC', '2GI', '2GE', '2GM', '2GLS', '2GC', '2HI', '2HE', '2HM', '2HLS', '2HC', '2II', '2IE', '2IM', '2ILS', '2IC', '3AI', '3AE', '3AM', '3ALS', '3AC', '3BI', '3BE', '3BM', '3BLS', '3BC', '3CI', '3CE', '3CM', '3CLS', '3CC', '3DI', '3DE', '3DM', '3DLS', '3DC', '3EI', '3EE', '3EM', '3ELS', '3EC', '3FI', '3FE', '3FM', '3FLS', '3FC', '3GI', '3GE', '3GM', '3GLS', '3GC', '3HI', '3HE', '3HM', '3HLS', '3HC', '3II', '3IE', '3IM', '3ILS', '3IC', '4AI', '4AE', '4AM', '4ALS', '4AC', '4BI', '4BE', '4BM', '4BLS', '4BC', '4CI', '4CE', '4CM', '4CLS', '4CC', '4DI', '4DE', '4DM', '4DLS', '4DC', '4EI', '4EE', '4EM', '4ELS', '4EC', '4FI', '4FE', '4FM', '4FLS', '4FC', '4GI', '4GE', '4GM', '4GLS', '4GC', '4HI', '4HE', '4HM', '4HLS', '4HC', '4II', '4IE', '4IM', '4ILS', '4IC', '5AI', '5AE', '5AM', '5ALS', '5AC', '5BI', '5BE', '5BM', '5BLS', '5BC', '5CI', '5CE', '5CM', '5CLS', '5CC', '5DI', '5DE', '5DM', '5DLS', '5DC', '5EI', '5EE', '5EM', '5ELS', '5EC', '5FI', '5FE', '5FM', '5FLS', '5FC', '5GI', '5GE', '5GM', '5GLS', '5GC', '5HI', '5HE', '5HM', '5HLS', '5HC', '5II', '5IE', '5IM', '5ILS', '5IC']


def setup_db_session():
    """
    """
    if os.path.isfile(DB_FILE_PATH):
        return sqlite3.connect(DB_FILE_PATH)


def get_webpage(url):
    """
    Fetch webpage
    """
    req = requests.get(url)
    content = req.text.encode('utf-8', 'ignore')
    return str(content)


def webpage_hash_calculator(url):
    """
    Stringified webpage hash calculator
    """
    content = get_webpage(url)
    md5_hash = md5(content).hexdigest()
    return md5_hash


def convert_pdf_to_txt(path):
    """
    """
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text


def classify_notice(pdf_path):
    """
    """
    tmp_list = []
    text = convert_pdf_to_txt(pdf_path)
    for school_class in SCHOOL_CLASSES:
        if text.find(school_class) != -1:
            tmp_list.append(school_class)
    notice_school_classes = ",".join(tmp_list)
    print notice_school_classes
    return notice_school_classes


def get_notices_uris():
    """
    """
    notices_uris = []
    notices_data = []
    content = get_webpage(URL)
    soup = BeautifulSoup(content,"lxml")
    rows = soup.findAll('tr')
    # skip the header of table
    for row in rows[1:]:
        cols = row.findAll('td')
        cols = [ele.text.strip().encode("utf-8") for ele in cols]
        notices_data.append([ele for ele in cols if ele])
    tab = soup.find('table')
    links = tab.findAll('a')
    for link in links:
        notices_uris.append(link['href'])
    # to avoid th links skip the first four
    notices_uris = notices_uris[4:]
    notices_uris = prepare_uris(notices_uris)
    return (notices_uris, notices_data)


def get_notice_pdf(download_url, number):
    """
    Download notice pdf file
    """
    response = urllib2.urlopen(download_url)
    file_name = number + ".pdf"
    file_path = PDF_FILES_BASE_PATH + file_name
    if not os.path.isfile(file_path):
        file = open(file_path, 'w')
        file.write(response.read())
        file.close()
        print("Completed")
    return file_path


def download_and_classify_notices(notices_to_be_downloaded):
    """
    """
    conn = setup_db_session()
    c = conn.cursor()
    for notice in notices_to_be_downloaded:
        file_path = get_notice_pdf(notice[0],notice[1])
        notice_school_classes = classify_notice(file_path)
        c.execute("UPDATE notices SET classes = ?, path = ? where number=" + "\"" + notice[1] + "\"", (notice_school_classes,file_path,))
    conn.commit()
    conn.close()


def update_hash(old_hash, new_hash):
    """
    """
    conn = setup_db_session()
    c = conn.cursor()
    c.execute("UPDATE md5s SET md5 = ? where md5=" + "\"" + old_hash + "\"",(new_hash,))
    conn.commit()
    conn.close()


def prepare_uris(notices_uris):
    """
    """
    new_notices_uris = []
    for i in range(len(notices_uris)):
        new_notices_uris.append(BASE_URL + notices_uris[i][1:])
    return new_notices_uris


def aggregate_data(notices_uris, notices_data):
    """
    """
    notices = {}
    if len(notices_uris) == len(notices_data):
        for i in range(len(notices_uris)):
            notices[i] = {"url":notices_uris[i],"number":notices_data[i][0],"title":notices_data[i][1],"pubblication_date":notices_data[i][5]}
    return notices


def add_new_notices_to_db(notices):
    """
    """
    notices_to_be_downloaded = []
    conn = setup_db_session()
    c = conn.cursor()
    for i in range(len(notices)):
        if c.execute("SELECT id FROM notices WHERE url=" + "\"" + notices[i]["url"] + "\"").fetchone() == None:
            c.execute("INSERT INTO notices (url, number, title, pubblication_date) VALUES (:url, :number, :title, :pubblication_date)",notices[i])
            notices_to_be_downloaded.append([notices[i]["url"],notices[i]["number"]])
    conn.commit()
    conn.close()
    return notices_to_be_downloaded


def main():
    
    conn = setup_db_session()
    c = conn.cursor()
    current_hash = webpage_hash_calculator(URL)
    old_hash = c.execute("SELECT md5 FROM md5s WHERE url=" + "\"" + URL + "\"").fetchone()[0].decode("utf-8")
    if old_hash == None:
        # first time hash calculation
        c.execute("INSERT INTO md5s (md5, url) VALUES (?,?)",(current_hash,URL,))
        conn.commit()
        conn.close()
        return

    if old_hash == current_hash:
    # comment up and uncomment down for rapid test
    #if old_hash == current_hash:
        # the website was modified
        update_hash(old_hash, current_hash)
        notices_uris, notices_data = get_notices_uris()
        notices = aggregate_data(notices_uris, notices_data)
        notices_to_be_downloaded = add_new_notices_to_db(notices)
        download_and_classify_notices(notices_to_be_downloaded)
    return


if __name__ == "__main__":
    main()
