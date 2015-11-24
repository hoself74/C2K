import sys, re, os

dir_name = os.path.abspath(os.path.dirname(__file__))
i_dir = dir_name + '/i_data/'
o_dir = dir_name + '/o_data/'

def main():
    ch_par_set = set([])

    i_file = open(i_dir + 'c_skos_preprocessed.tab', 'r')
    line = i_file.readline()
    while line:
        line = line[0:-1]
        
        s_line = re.split('\t', line)
        ch_c = s_line[0]
        par_c = s_line[1]

        ch_par_set.add(ch_c + '\t' + par_c + '\n')
        
        line = i_file.readline()
    i_file.close()

    o_file = open(i_dir + 'c_network.tab', 'w+')
    for ch_par in sorted(ch_par_set):
        o_file.write(ch_par)
    o_file.close()

main()
