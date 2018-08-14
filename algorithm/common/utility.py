import os, sys
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(current_dir)

import json as _J
from defs import *

def json_loadAll():
    allData = []
    files= os.listdir(PARSED_DIR)
    for filename in files:
        if not os.path.isdir(filename):
            print("reading " + filename)
            name = os.path.splitext(filename)[0]
            data = json_load(name)
            allData.extend(data)
    return allData

def json_load(filename:str):
    with open(PARSED_DIR + filename + ".json", 'r', encoding='utf8') as fin:
        data = _J.load(fin)
    return data

def json_dump(obj, filename:str):
    with open(PARSED_DIR + filename + ".json", 'w', encoding='utf8') as fout:
        _J.dump(obj, fout, ensure_ascii=False)
    return obj