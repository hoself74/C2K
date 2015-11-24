import sys, re, urllib, operator, os

dir_name = os.path.abspath(os.path.dirname(__file__))
sys.path.append(dir_name + '/libraries')
import triple_formatter as tf

mode = None

i_dir = dir_name + '/i_data/'
o_dir = dir_name + '/o_data/'
s_dir = dir_name + 'shared_files/'

rule_file_name = 'mined_rules.tab'

def main():
    global mode
    mode = sys.argv[1]
    
    load_dictionaries()
    load_ktriples()
    load_ptriples()
    sort_triples()
    save_triples()

s_dic = {}
p_dic = {}
o_dic = {}
c_dic = {}
def load_dictionaries():
    i_file = open(i_dir + 's_dictionary.tab', 'r')
    line = i_file.readline()
    while line:
        line = line[0:-1]
        s_line = re.split('\t', line)
        if len(s_line[0]) > 0:
            s = urllib.unquote(s_line[1])
            try:
                s = unicode(s, 'unicode-escape').encode('utf-8')
            except UnicodeDecodeError:
                pass
            try:
                s_dic[s_line[0]].add(s)
            except KeyError:
                s_dic[s_line[0]] = set([s])
        line = i_file.readline()
    i_file.close()
    i_file = open(i_dir + 'p_dictionary.tab', 'r')
    line = i_file.readline()
    while line:
        line = line[0:-1]
        s_line = re.split('\t', line)
        if len(s_line[0]) > 0:
            p = urllib.unquote(s_line[1])
            try:
                p = unicode(p, 'unicode-escape').encode('utf-8')
            except UnicodeDecodeError:
                pass
            try:
                p_dic[s_line[0]].add(p)
            except KeyError:
                p_dic[s_line[0]] = set([p])
        line = i_file.readline()
    i_file.close()
    i_file = open(i_dir + 'o_dictionary.tab', 'r')
    line = i_file.readline()
    while line:
        line = line[0:-1]
        s_line = re.split('\t', line)
        if len(s_line[0]) > 0:
            o = urllib.unquote(s_line[1])
            try:
                o = unicode(o, 'unicode-escape').encode('utf-8')
            except UnicodeDecodeError:
                pass
            try:
                o_dic[s_line[0]].add(o)
            except KeyError:
                o_dic[s_line[0]] = set([o])

        line = i_file.readline()
    i_file.close()
    i_file = open(i_dir + 'c_dictionary.tab', 'r')
    line = i_file.readline()
    while line:
        line = line[0:-1]
        s_line = re.split('\t', line)
        if len(s_line[0]) > 0:
            c = urllib.unquote(s_line[1])
            try:
                c = unicode(c, 'unicode-escape').encode('utf-8')
            except UnicodeDecodeError:
                pass
            try:
                c_dic[s_line[0]].add(c)
            except KeyError:
                c_dic[s_line[0]] = set([c])
        line = i_file.readline()
    i_file.close()
    
k_triples = set([])
def load_ktriples():
    i_file = open(i_dir + mode + '_triples_preprocessed.tab', 'r')
    line = i_file.readline()
    while line:
        if line[0] == '#':
            line= i_file.readline()
            continue
        line = line[0:-1]
        s_line = re.split('\t', line)
        
        e = s_line[0]
        r = s_line[1]
        o = s_line[2]
        
        k_triples.add((e, r, o))
        
        line = i_file.readline()
    i_file.close()
    
p_triples = set([])
def load_ptriples():
    i_file_name = 'predicted_triples.tab'
    i_file = open(o_dir + i_file_name, 'r')
    line = i_file.readline()
    while line:
        if line[0] == '#':
            line= i_file.readline()
            continue
        line = line[0:-1]
        s_line = re.split('\t', line)
        
        e = s_line[0]
        r = s_line[1]
        o = s_line[2]
        conf = float(s_line[3])
        source = s_line[5]
        
        p_triples.add((e, r, o, conf, source))
        
        line = i_file.readline()
    i_file.close()

sorted_triples = []
def sort_triples():
    global p_triples
    p_triples = sorted(p_triples, key=operator.itemgetter(3), reverse=True)

def save_triples():
    o_file_name = 'predicted_triples_postprocessed.tab'
    o_file = open(o_dir + o_file_name, 'w+')
    
    for (e, r, o, conf, source) in p_triples:
        if (e, r, o) not in k_triples:
            try:
                e_oris = s_dic[e]
            except KeyError:
                e_oris = set([e])
            try:
                r_oris = p_dic[r]
                for r_ori in set(r_oris): # 중복 제거
                    r_ontology = 'http://dbpedia.org/ontology/' + re.split('/', r_ori)[-1]
                    if r_ontology in r_oris and r_ontology != r_oris:
                        r_oris.remove(r_ori)
            except KeyError:
                r_oris = set([r])
            try:
                try:
                    float(o)
                    o_oris = set([o])
                except:
                    o_oris = o_dic[o]
                    
                    for o_ori in set(o_oris): # 중복 제거
                        o_ko = 'http://ko.dbpedia.org/resource/' + re.split('/', o_ori.replace(' ', '_'))[-1]
                        o_en = 'http://dbpedia.org/resource/' + re.split('/', o_ori.replace(' ', '_'))[-1]
                        if o_ko in o_oris and o_ko != o_ori:
                            o_oris.remove(o_ori)
                        if o_en in o_oris and o_en != o_ori:
                            o_oris.remove(o_ori)
            except KeyError:
                o_oris = set([o])
            try:
                c_oris = c_dic[source]
            except KeyError:
                c_oris = set([source])

            for e_ori in e_oris:
                for r_ori in r_oris:
                    for o_ori in o_oris:
                        for c_ori in c_oris:
                            o_file.write(tf.upload_format(e_ori) + ' ' + tf.upload_format(r_ori) + ' ' + tf.upload_format(o_ori) + ' .' + '\t' + str(conf) + '\t' + c_ori + '\n')
    o_file.close()

main()
