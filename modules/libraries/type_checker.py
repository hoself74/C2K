import re

def is_date(x):
    date_1 = bool(re.search(r'^([0-9]{4}).([0-9]{2}).([0-9]{2})[tT]([0-9]{2}).([0-9]{2}).([0-9]{2})[zZ]$', x))
    date_2 = bool(re.search(r'^([0-9]{4}).([0-9]{2}).([0-9]{2})$', x))

    return date_1 or date_2

def is_int(x):
    return bool(re.findall(r'^[0-9]+$', x))

def is_double(x):
    return bool(re.search(r'^[0-9]+e\+[0-9]+$', x))

def is_float(x):
    return bool(re.search(r'^([0-9]*)\.[0-9]+$', x))
