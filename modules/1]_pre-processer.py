import sys, re, urllib, os
from nltk.corpus import wordnet as wn

dir_name = os.path.abspath(os.path.dirname(__file__))
sys.path.append(dir_name + '/libraries')
import triple_splitter as ts

# ==============================
# 환경 변수
lang = None
# ==============================

i_dir = dir_name + '/i_data/'
o_dir = dir_name + '/o_data/'

s_dictionary = set([])
p_dictionary = set([])
o_dictionary = set([])
c_dictionary = set([])

def main():
    global lang
    lang = sys.argv[1]
    
    process_ctriples()
    process_cskos()
    process_ktriples()
    process_ttriples()
    save_dictionary()

def process_ctriples():
    i_file = open(i_dir + 'c_triples.nt', 'r')
    o_file = open(i_dir + 'c_triples_preprocessed.tab', 'w+')
    
    line = i_file.readline()
    while line:
        if line[0] == '#':
            line = i_file.readline()
            continue
        line = line[0:-1]
        spo = ts.get_spo(line)
        if len(spo) < 3:
            line = i_file.readline()
            continue

        s = urllib.unquote(spo[0])
        try:
            s = unicode(s, 'unicode-escape').encode('utf-8')
        except UnicodeDecodeError:
            pass
        s = detach_sprefix(s)
        s = normalize(s)
        c = urllib.unquote(spo[2])
        try:
            c = unicode(c, 'unicode-escape').encode('utf-8')
        except UnicodeDecodeError:
            pass
        c = detach_cprefix(c)
        c = normalize(c)
        
        o_file.write(s + '\t' + 'categorizedIn' + '\t' + c + '\n')

        if s != spo[0]:
            s_dictionary.add((s, spo[0]))
        if c != spo[2]:
            c_dictionary.add((c, spo[2]))

        line = i_file.readline()

    o_file.close()
    i_file.close()

def process_cskos():
    i_file = open(i_dir + 'c_skos.nt', 'r')
    o_file = open(i_dir + 'c_skos_preprocessed.tab', 'w+')
    
    line = i_file.readline()
    while line:
        if line[0] == '#':
            line = i_file.readline()
            continue
        line = line[0:-1]
        spo = ts.get_spo(line)
        if len(spo) < 3:
            line = i_file.readline()
            continue

        if spo[1] != 'http://www.w3.org/2004/02/skos/core#broader':
            line = i_file.readline()
            continue

        l_c = urllib.unquote(spo[0])
        try:
            l_c = unicode(l_c, 'unicode-escape').encode('utf-8')
        except UnicodeDecodeError:
            pass
        l_c = detach_cprefix(l_c)
        l_c = normalize(l_c)
        r_c = urllib.unquote(spo[2])
        try:
            r_c = unicode(r_c, 'unicode-escape').encode('utf-8')
        except UnicodeDecodeError:
            pass
        r_c = detach_cprefix(r_c)
        r_c = normalize(r_c)

        o_file.write(l_c + '\t' + r_c + '\n')

        if l_c != spo[0]:
            c_dictionary.add((l_c, spo[0]))
        if r_c != spo[2]:
            c_dictionary.add((r_c, spo[2]))

        line = i_file.readline()

    o_file.close()
    i_file.close()

def process_ktriples():
    lines = set([])
    f_names = ['k_triples.nt']
    for f_name in f_names:
        i_file = open(i_dir + f_name, 'r')
        line = i_file.readline()
        while line:
            if line[0] == '#':
                line = i_file.readline()
                continue
            lines.add(line)
            line = i_file.readline()
        i_file.close()
    
    o_file = open(i_dir + 'k_triples_preprocessed.tab', 'w+')
    for line in sorted(lines):
        line = line[0:-1]
        spo = ts.get_spo(line)
        if len(spo) < 3:
            continue

        s = urllib.unquote(spo[0])
        try:
            s = unicode(s, 'unicode-escape').encode('utf-8')
        except UnicodeDecodeError:
            pass
        s = detach_sprefix(s)
        s = normalize(s)
        p = urllib.unquote(spo[1])
        try:
            p = unicode(p, 'unicode-escape').encode('utf-8')
        except UnicodeDecodeError:
            pass
        p = detach_pprefix(p)
        p = normalize(p)
        o = urllib.unquote(spo[2])
        try:
            o = unicode(o, 'unicode-escape').encode('utf-8')
        except UnicodeDecodeError:
            pass
        o = detach_oprefix(o)
        o = normalize(o)

        o_file.write(s + '\t' + p + '\t' + o + '\n')

        if s != spo[0]:
            s_dictionary.add((s, spo[0]))
        if p != spo[1]:
            p_dictionary.add((p, spo[1]))
        if o != spo[2]:
            o_dictionary.add((o, spo[2]))

    o_file.close()

def process_ttriples():
    lines = set([])
    f_names = ['t_triples.nt']
    for f_name in f_names:
        i_file = open(i_dir + f_name, 'r')
        line = i_file.readline()
        while line:
            if line[0] == '#':
                line = i_file.readline()
                continue
            lines.add(line)
            line = i_file.readline()
        i_file.close()
    
    o_file = open(i_dir + 't_triples_preprocessed.tab', 'w+')
    for line in sorted(lines):
        line = line[0:-1]
        spo = ts.get_spo(line)
        if len(spo) < 3:
            continue

        s = urllib.unquote(spo[0])
        try:
            s = unicode(s, 'unicode-escape').encode('utf-8')
        except UnicodeDecodeError:
            pass
        s = detach_sprefix(s)
        s = normalize(s)
        p = urllib.unquote(spo[1])
        try:
            p = unicode(p, 'unicode-escape').encode('utf-8')
        except UnicodeDecodeError:
            pass
        p = detach_pprefix(p)
        p = normalize(p)
        o = urllib.unquote(spo[2])
        try:
            o = unicode(o, 'unicode-escape').encode('utf-8')
        except UnicodeDecodeError:
            pass
        o = detach_oprefix(o)
        o = normalize(o)

        o_file.write(s + '\t' + p + '\t' + o + '\n')

        if s != spo[0]:
            s_dictionary.add((s, spo[0]))
        if p != spo[1]:
            p_dictionary.add((p, spo[1]))
        if o != spo[2]:
            o_dictionary.add((o, spo[2]))

    o_file.close()

def save_dictionary():
    o_file = open(i_dir + 's_dictionary.tab', 'w+')
    for (after, before) in sorted(s_dictionary):
        o_file.write(after + '\t' + before + '\n')
    o_file.close()
    o_file = open(i_dir + 'p_dictionary.tab', 'w+')
    for (after, before) in sorted(p_dictionary):
        o_file.write(after + '\t' + before + '\n')
    o_file.close()
    o_file = open(i_dir + 'o_dictionary.tab', 'w+')
    for (after, before) in sorted(o_dictionary):
        o_file.write(after + '\t' + before + '\n')
    o_file.close()
    o_file = open(i_dir + 'c_dictionary.tab', 'w+')
    for (after, before) in sorted(c_dictionary):
        o_file.write(after + '\t' + before + '\n')
    o_file.close()

def detach_sprefix(w):
    return re.split('/', w)[-1]

def detach_pprefix(w):
    prefix_set = set([])
    if lang == 'en':
        prefix_set = set(['http://dbpedia.org/property/', 'http://dbpedia.org/ontology/'])
    elif lang == 'ko':
        prefix_set = set(['http://dbpedia.org/property/', 'http://ko.dbpedia.org/property/', 'http://dbpedia.org/ontology/'])
    for p in prefix_set:
        if p in w:
            w= w.replace(p, '')
    return w
        
def detach_oprefix(w):
    return re.split('/|#', w)[-1]

def detach_cprefix(w):
    prefix_set = set([])
    if lang == 'en':
        prefix_set = set(['http://dbpedia.org/resource/', 'Category:'])
    elif lang == 'ko':
        prefix_set = set(['http://ko.dbpedia.org/resource/', '분류:'])
    
    for p in prefix_set:
        if p in w:
            w= w.replace(p, '')
    return w

def normalize(word):
    normed_word = ''
    
    if lang == 'en':
        word = camel_to_underscore(word)
        word = word.lower()
        word = re.sub(r'\s', '_', word)
        word = get_morpheme_str(word)

        normed_word = word
        
    elif lang == 'ko':
        word = camel_to_underscore(word)
        word = word.lower()
        word = re.sub(r'\s', '_', word)
        word = get_morpheme_str(word)

        #normed_word = word

        # Postfix separation
        postfixes_1leng = ['와', '과', '의', '을', '를', '은', '는', '이', '가', '년', '에', '로']
        postfixes_2leng = ['에서', '보다']
        postfixes_3leng = ['로부터']
        s_word = re.split('_', word)
        for sw in s_word:
            if sw[-3:] in postfixes_1leng:
                normed_word += sw[0:-3] + '_' + sw[-3:] + '_'
            elif sw[-6:] in postfixes_2leng:
                normed_word += sw[0:-6] + '_' + sw[-6:] + '_'
            elif sw[-9:] in postfixes_3leng:
                normed_word += sw[0:-9] + '_' + sw[-9:] + '_'
            else:
                normed_word += sw + '_'
        normed_word = normed_word[0:-1]

    return normed_word

regex = re.compile('([a-z])([A-Z][a-z]+)')
def camel_to_underscore(word):
    return regex.sub(r'\1_\2', word).lower()

morpheme = {}
def get_morpheme(w):
    # DP
    try:
        morpheme[w]
    except KeyError:
        if lang == 'en':
            try:
                morpheme[w] = wn.morphy(w).encode('utf-8')
            except:
                morpheme[w] = w
        elif lang == 'ko':
            morpheme[w] = w

    #return w
    return morpheme[w]

def get_morpheme_str(w):
    mstr = ''
    for s_w in re.split('_', w):
        mstr += get_morpheme(s_w) + '_'
    mstr = mstr[0:-1]

    return mstr

main()
