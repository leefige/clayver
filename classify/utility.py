import json as _J

FEAT_SIZE = 6
PARSED_DIR = "../parsed/"

def json_load(filename:str):
    with open(PARSED_DIR + filename + ".json", 'r', encoding='utf8') as fin:
        data = _J.load(fin)
    return data

def json_dump(obj, filename:str):
    with open(PARSED_DIR + filename + ".json", 'w', encoding='utf8') as fout:
        _J.dump(obj, fout, ensure_ascii=False)
    return obj