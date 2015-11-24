import re

def get_spo(t):
    spo = []
    if t[-1] == '.':
        # case 1: object = URI
        match = re.findall(r'^[<](.+?)[>]\s[<](.+?)[>]\s[<](.+?)[>]\s\.$', t)
        if len(match) > 0:
            if len(match[0]) == 3:
                spo = match[0]
                
        # case 3: object = literals (string)
        match = re.findall(r'^[<](.+?)[>]\s[<](.+?)[>]\s"(.+?)"\s\.$', t)
        if len(match) > 0:
            if len(match[0]) == 3:
                spo = match[0]

        # case 2: object = literals (string) with language-prefix
        match = re.findall(r'^[<](.+?)[>]\s[<](.+?)[>]\s"(.+?)"@.+\s\.$', t)
        if len(match) > 0:
            if len(match[0]) == 3:
                spo = match[0]
   
        # case 4: object = literals (non-string)
        match = re.findall(r'^[<](.+?)[>]\s[<](.+?)[>]\s"(.+?)"\^\^[<].+[>]\s\.$', t)
        if len(match) > 0:
            if len(match[0]) == 3:
                spo = match[0]
    else:
        match = re.split('\s', t)
        if len(match) == 3:
            spo = match

    return spo
