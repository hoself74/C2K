import sys, re, urllib, os

dir_name = os.path.abspath(os.path.dirname(__file__))

i_dir = dir_name + '/i_data/'
o_dir = dir_name + '/o_data/'
s_dir = dir_name + 'shared_files/'

rule_file_name = 'mined_rules.tab'

def main():
    load_ctriples()
    load_rules()
    predict_triples()
    save_triples()

c_to_e = {}
def load_ctriples():
    # T_cat 로딩
    i_file = open(i_dir + 'c_triples_preprocessed.tab', 'r')
    line = i_file.readline()
    while line:
        if line[0] == '#':
            line= i_file.readline()
            continue
        line = line[0:-1]
        s_line = re.split('\t', line)
        
        e = s_line[0]
        c = s_line[2]
        try:
            c_to_e[c].add(e)
        except KeyError:
            c_to_e[c] = set([e])
        
        line = i_file.readline()
    i_file.close()

rules = {}
unoverlapped_triples = set([])
#overlapped_triples = set([])
def load_rules():
    i_file = open(o_dir + rule_file_name, 'r')
    line = i_file.readline()
    while line:
        line = line[0:-1]
        match = re.findall(r'^\?x\scategorizedIn\s(.+?)\s=[>]\s\?x\s(.+?)\s(.+?)\s(.+?)\s(.+?)$', line)
        if len(match) > 0:
            if len(match[0]) == 5:
                c = match[0][0]
                r = match[0][1]
                o = match[0][2]
                conf = match[0][3]
                stand_conf = match[0][4]

                try:
                    rules[c].add((r, o, conf, stand_conf))
                except KeyError:
                    rules[c] = set([(r, o, conf, stand_conf)])
        line = i_file.readline()
    i_file.close()

top_conf = {}
def predict_triples():
    for c in c_to_e.keys():
        for e in c_to_e[c]:
            try:
                for (r, o, conf, stand_conf) in rules[c]:                    
                    try:
                        if float(top_conf[(e, r, o)][0]) < float(conf):
                            top_conf[(e, r, o)][0] = conf
                            top_conf[(e, r, o)][1] = stand_conf
                            top_conf[(e, r, o)][2] = c
                    except KeyError:
                        top_conf[(e, r, o)] = [conf, stand_conf, c]
            except KeyError:
                pass

    for ((e, r, o), [conf, stand_conf, c]) in sorted(top_conf.items()):
        unoverlapped_triples.add(e + '\t' + r + '\t' + o + '\t' + conf + '\t' + stand_conf + '\t' + c + '\n')            
        
def save_triples():
    o_file_name = 'predicted_triples.tab'
    o_file = open(o_dir + o_file_name, 'w+')
    for t in sorted(unoverlapped_triples):
        o_file.write(t)
    o_file.close()

main()
