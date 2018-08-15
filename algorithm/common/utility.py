import os, sys
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(current_dir)

import json as _J
from defs import *
from sample import Sample

def json_load(filename:str):
    with open(PARSED_DIR + filename + ".json", 'r', encoding='utf8') as fin:
        data = _J.load(fin)
    return data

def json_dump(obj, filename:str):
    with open(PARSED_DIR + filename + ".json", 'w', encoding='utf8') as fout:
        _J.dump(obj, fout, ensure_ascii=False)
    return obj

def json_loadAll(class_num=None):
    allData = []
    files= os.listdir(PARSED_DIR)
    for filename in files:
        if not os.path.isdir(filename):
            print("reading " + filename)
            name = os.path.splitext(filename)[0]
            data = json_load(name)
            if class_num:
                sorted(data, key=lambda x: x['tp'])
                for i in range(len(data)):
                    if data[i]['label'] == 6:
                        data = data[:i]
                        break
            allData.extend(data)
    return [Sample(obj=da) for da in allData]
