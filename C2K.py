import sys, re, os, subprocess, operator

lang = None
type_mode = False

theta_c = None # confidence threshold
theta_q = None # 규칙의 증가율에 대한 임계치
theta_l = None # lower bound constant
theta_u = None # upper bound constant
            
def main():
    global lang
    global type_mode
    
    global theta_c
    global theta_q
    global theta_l
    global theta_u
    
    # Argument checking
    for argv in sys.argv[1:]:
        s_argv = re.split('\s', argv)

        if s_argv[0] == '-t':
            type_mode = True
        elif s_argv[0] == '-ko':
            lang = 'ko'
        elif s_argv[0] == '-en':
            lang = 'en'
        elif s_argv[0] == '-def':
            theta_c = '0.9' # confidence threshold
            theta_q = '0.1' # 규칙의 증가율에 대한 임계치
            theta_l = '5.0' # lower bound constant
            theta_u = '1000.0' # upper bound constant
        elif s_argv[0] == '-thc':
            theta_c = s_argv[1]
        elif s_argv[0] == '-thq':
            theta_q = s_argv[1]
        elif s_argv[0] == '-thl':
            theta_l = s_argv[1]
        elif s_argv[0] == '-thu':
            theta_u = s_argv[1] 
        else:
            print 'Invalid arguments'
            return

    if lang == None:
        print 'Incomplete arguments'
        return
    if theta_c == None or theta_q == None:
        print 'Incomplete arguments'
        return
    if theta_l == None or theta_u == None:
        print 'Incomplete arguments'
        return

    # Input file checking
    if not os.path.exists('inputs/c_triples.nt'):
        print 'Incomplete inputsss'
        return
    if not os.path.exists('inputs/k_triples.nt'):
        print 'Incomplete inputs'
        return
    if not os.path.exists('inputs/t_triples.nt'):
        print 'Incomplete inputs'
        return
    if not os.path.exists('inputs/c_skos.nt'):
        print 'Incomplete inputs'
        return

    # Data copying
    print 'Input data is being copied.'
    subprocess.call('cp inputs/c_triples.nt modules/i_data/c_triples.nt', shell=True)
    subprocess.call('cp inputs/k_triples.nt modules/i_data/k_triples.nt', shell=True)
    subprocess.call('cp inputs/t_triples.nt modules/i_data/t_triples.nt', shell=True)
    subprocess.call('cp inputs/c_skos.nt modules/i_data/c_skos.nt', shell=True)
    
    # pre-processer.py
    print 'Input data is being pre-processed.'
    subprocess.call('python modules/1]_pre-processer.py ' + lang, shell=True)

    # c_network_extracter.py
    print 'Category network is being extracted.'
    subprocess.call('python modules/2]_c_network_extracter.py ' + lang, shell=True)

    # seed_filter_strict.py
    print 'Erroneous data is being filtered out.'
    subprocess.call('python modules/2]_seed_filter_strict.py ' + lang, shell=True)

    # rule_miner.py
    print 'Rules are being mined.'
    if type_mode:
        mode = 't'
    else:
        mode =  'k_s-filtered'
    subprocess.call('python modules/3]_rule_miner.py ' + lang + ' ' + mode + ' ' + theta_c + ' ' + theta_q + ' ' + theta_l + ' ' + theta_u, shell=True)

    # triple_predicter.py
    print 'Triples are being predicted.'
    subprocess.call('python modules/4]_triple_predicter.py', shell=True)

    # post-processer.py
    print 'Triples are being post-processed.'
    subprocess.call('python modules/5]_post-processer.py ' + mode, shell=True)

    # Output relocating
    print 'Output is being produced.'
    subprocess.call('cp modules/o_data/predicted_triples_postprocessed.tab outputs/predicted_triples.tsv', shell=True)
    
    # Data removing
    print 'Temporary data is being removed.'
    #subprocess.call('rm modules/i_data/*', shell=True)
    #subprocess.call('rm modules/o_data/*', shell=True)

main()
