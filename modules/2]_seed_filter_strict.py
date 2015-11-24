import sys, re, operator, os
from nltk.corpus import wordnet as wn

dir_name = os.path.abspath(os.path.dirname(__file__))
sys.path.append(dir_name + '/libraries')
import type_checker as tc

i_dir = dir_name + '/i_data/'
o_dir = dir_name + '/o_data/'

e_type = {}

def main():
    load_types()
    filter_seed()

def load_types():
    i_file = open(i_dir + 't_triples_preprocessed.tab', 'r')
    line = i_file.readline()
    while line:
        line = line[0:-1]
        s_line = re.split('\s', line)
        e = s_line[0]
        t = s_line[2]
        if 'thing' in t: # 논문에 언급
            line = i_file.readline()
            continue
        
        try:
            e_type[e].add(t)
        except KeyError:
            e_type[e] = set([t])
        
        line = i_file.readline()
    i_file.close()    

def filter_seed():
    rt_statistics = {}
    filtered_t = {}

    i_file = open(i_dir + 'k_triples_preprocessed.tab', 'r')
    line = i_file.readline()
    while line:
        line = line[0:-1]
        s_line = re.split('\s', line)
        e = s_line[0]
        r = s_line[1]
        o = s_line[2]
        o_type = get_type(o)

        try:
            rt_statistics[r]
        except KeyError:
            rt_statistics[r] = {}

        for t in o_type:
            try:
                rt_statistics[r][t] += 1
            except KeyError:
                rt_statistics[r][t] = 1

        line = i_file.readline()
    i_file.close()

    o_file1 = open(o_dir + 'rt_statistics_unfiltered.tab', 'w+')
    o_file2 = open(o_dir + 'rt_statistics_filtered.tab', 'w+')
    for r in sorted(rt_statistics.keys()):
        o_file1.write('Relation: ' + r + '\n')
        o_file2.write('Relation: ' + r + '\n')
        t_statistics = sorted(rt_statistics[r].items(), key=operator.itemgetter(1), reverse=True)
        t_average = 0.0
        for (t, cnt) in t_statistics:
            t_average += cnt
            o_file1.write(t + '\t' + str(cnt) + '\n')
        o_file1.write('\n')     
        if t_statistics > 0.0:
            t_average /= float(len(t_statistics))

        for (t, cnt) in t_statistics:
            if float(cnt) >= t_average:
                try:
                    filtered_t[r].add(t)
                except KeyError:
                    filtered_t[r] = set([t])
                o_file2.write(t + '\t' + str(cnt) + '\n')
        o_file2.write('\n')
 
    o_file1.close()
    o_file2.close()

    i_file = open(i_dir + 'k_triples_preprocessed.tab', 'r')
    o_file = open(i_dir + 'k_s-filtered_triples_preprocessed.tab', 'w+')
    line = i_file.readline()
    while line:
        line = line[0:-1]
        s_line = re.split('\s', line)
        e = s_line[0]
        r = s_line[1]
        o = s_line[2]
        o_type = get_type(o)

        if len(o_type & filtered_t[r]) > 0:
            o_file.write(line + '\n')
                
        line = i_file.readline()
    o_file.close()
    i_file.close()

def get_type(x):
    if tc.is_int(x):
        return set(['int'])
    elif tc.is_float(x):
        return set(['float'])
    elif tc.is_double(x):
        return set(['double'])
    elif tc.is_date(x):
        return set(['date'])
    else:
        try:
            return e_type[x]
        except KeyError:
            return set(['str'])

main()
