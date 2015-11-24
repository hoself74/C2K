import re

def upload_format(e):
    # completed data type
    if len(re.findall(r'^".+"\^\^\<.+\>$', e)) > 0: 
        e = e
    # date
    elif bool(re.search(r'^[0-9]{4}.[0-9]{2}.[0-9]{2}[tT][0-9]{2}.[0-9]{2}.[0-9]{2}[zZ]$', e)):
        e = '"' + e + '"^^<http://www.w3.org/2001/XMLSchema#date>'
    elif bool(re.search(r'^([0-9]{4}).([0-9]{2}).([0-9]{2})$', e)):
        e = '"' + e + '"^^<http://www.w3.org/2001/XMLSchema#date>'
    # double
    elif bool(re.search(r'^[+-]?[0-9]*\.[0-9]+e[+-]?[0-9]+$', e)):
        e = '"' + e + '"^^<http://www.w3.org/2001/XMLSchema#double>'
    # float
    elif bool(re.search(r'^[+-]?[0-9]*\.[0-9]+$', e)): 
        e = '"' + e + '"^^<http://www.w3.org/2001/XMLSchema#float>'
    # integer
    elif bool(re.findall(r'^[+-]?[0-9]+$', e)):
        e = '"' + e + '"^^<http://www.w3.org/2001/XMLSchema#integer>'
    # label
    elif bool(re.findall(r'"^.+"@.+$', e)): 
        e = e
    # url
    elif bool(re.findall(r'^http://.+$', e)):
        e = '<' + e + '>'
    # string
    else:
        e = '"' + e + '"'

    return e
