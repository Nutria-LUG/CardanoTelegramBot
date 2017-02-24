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

def classify_by_classes():
    return

def get_avvisi_uris():
    return

def get_avvisi():
    return

def main():
    return

if __name__ == "__main__":
    main()
