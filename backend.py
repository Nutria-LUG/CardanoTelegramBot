#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Fetch avvisi from Itis G. Cardano website """

import requests
import sqlite
from hashlib import md5

URL = "http://circolari.cardano.pv.it/famiglie/leggiavvisi.php"
DB_FILE = "avvisi.db"

def get_webpage(url):
    """ Fetch webpage """
    req = requests.get(url)
    content = req.text.encode('utf-8', 'ignore')
    return str(content)

def webpage_hash_calculator(url):
    """ Stringified webpage hash calculator """
    content = get_webpage(url)
    md5_hash = md5(content).hexdigest()
    return md5_hash

def classify_notice(pdf_path):
    return

def get_notices_uris():
    return uris

def get_notice_pdf():
    return

def main():
    # check if website md5 exist in db or file
    # if it exists, get it
    # else generate and save it
    if webpage_hash_calculator(URL) != md5:
        uris = get_notices_uris(URL)
        for uri in uris:
            pdf_path = get_notice_pdf(uri)
            classify_notice(pdf_path)
            # add notice to db
    return

if __name__ == "__main__":
    main()
