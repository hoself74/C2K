import sys, re, operator, time, math, os
from nltk.corpus import wordnet as wn
from gensim.models import Word2Vec

dir_name = os.path.abspath(os.path.dirname(__file__))
sys.path.append(dir_name + '/libraries')
import type_checker as tc

# ==============================
# 환경 변수
lang = None
mode = None # k | k_l-filtered | k_s-filtered | t

theta_c = None # confidence threshold
theta_q = None # 규칙의 증가율에 대한 임계치
theta_l = None # lower bound constant
theta_u = None # upper bound constant

base_conf_name = 'averaged_conf'
# ==============================

i_dir = dir_name + '/i_data/'
o_dir = dir_name + '/o_data/'
s_dir = dir_name + '/shared_files/'

csro_str = {}
csro_id = {}

child_cats = {}
parent_cats = {}

used_ro_set = {}
redundant_ro_set = {}
htable_preword = {}
htable_postword = {}

T_cat = {}
T_know = {}

c_to_e = {}
ro_to_e = {}

all_c_set = set([])
all_o_set = set([])

rules = {}
source_rp = {}
aggregated_c_support = {}
aggregated_cro_support = {}

total_conf = {}
averaged_conf = {}
stand_conf = {}
base_conf = {}
if base_conf_name == 'averaged_conf':
    base_conf = averaged_conf

model = None

s_l_links = {}
l_s_links = {}
l_a_links = {}
s_mm_links = {}
s_mh_links = {}

en_to_ko = {}
ko_to_en = {}

def main():
    global lang
    global mode
    global theta_c
    global theta_q
    global theta_l
    global theta_u
    
    lang = sys.argv[1]
    mode = sys.argv[2]
    theta_c = float(sys.argv[3])
    theta_q = float(sys.argv[4])
    theta_l = float(sys.argv[5])
    theta_u = float(sys.argv[6])
    
    # Overview
    if lang == 'ko':
        load_langdict()
    load_wordvectors()
    load_wordnet()
    load_cnetwork()
    load_ctriples()
    load_ktriples()
    mine_rules()
    save_rules()

def load_langdict():
    i_file = open(s_dir + 'language_dictionary.tab', 'r')
    line = i_file.readline()
    while line:
        if line[0] == '#':
            line = i_file.readline()
            continue
        line = line[0:-1]
        s_line = re.split('\t', line)

        en = unicode(s_line[1], 'cp949').encode('utf-8').lower()
        if len(en) > 2:
            if en[0:2] == 'a ':
                en = en[2:]
        ko = unicode(s_line[3], 'cp949').encode('utf-8')

        try:
            en_to_ko[en].add(ko)
        except KeyError:
            en_to_ko[en] = set([ko])
        try:
            ko_to_en[ko].add(en)
        except KeyError:
            ko_to_en[ko] = set([en])
        
        line = i_file.readline()
    i_file.close()

    print 'LANGDICT LOADED'

def load_wordvectors():
    global model
    model = Word2Vec.load(s_dir + 'en_500_stem/en.model')
    print 'WORDVECTOR LOADED'
    
def load_wordnet():
    i_file = open(s_dir + 'synset_lemma_links.tab', 'r')
    line = i_file.readline()
    while line:
        line = line[0:-1]
        s_line = re.split('\t', line.lower())

        s = s_line[0]
        l_set = set(s_line[1:])
        l_set.remove('')

        s_l_links[s] = l_set

        line = i_file.readline()
    i_file.close()

    i_file = open(s_dir + 'lemma_synset_links.tab', 'r')
    line = i_file.readline()
    while line:
        line = line[0:-1]
        s_line = re.split('\t', line.lower())

        l = s_line[0]
        s_set = set(s_line[1:])
        s_set.remove('')

        l_s_links[l] = s_set

        line = i_file.readline()
    i_file.close()

    i_file = open(s_dir + 'lemma_antonym_links.tab', 'r')
    line = i_file.readline()
    while line:
        line = line[0:-1]
        s_line = re.split('\t', line.lower())

        l = s_line[0]
        a_set = set(s_line[1:])
        a_set.remove('')

        l_a_links[l] = a_set

        line = i_file.readline()
    i_file.close()

    i_file = open(s_dir + 'synset_mmeronym_links.tab', 'r')
    line = i_file.readline()
    while line:
        line = line[0:-1]
        s_line = re.split('\t', line.lower())

        s = s_line[0]
        mm_set = set(s_line[1:])
        mm_set.remove('')

        s_mm_links[s] = mm_set

        line = i_file.readline()
    i_file.close()

    i_file = open(s_dir + 'synset_mholonym_links.tab', 'r')
    line = i_file.readline()
    while line:
        line = line[0:-1]
        s_line = re.split('\t', line.lower())

        s = s_line[0]
        mh_set = set(s_line[1:])
        mh_set.remove('')

        s_mh_links[s] = mh_set

        line = i_file.readline()
    i_file.close()

    print 'WORDNET LOADED'
    
def load_cnetwork():
    # 카테고리 네트워크 로딩
    i_file = open(i_dir + 'c_network.tab', 'r')
    line = i_file.readline()
    while line:
        if line[0] == '#':
            line = i_file.readline()
            continue
        line = line[0:-1] 
        s_line = re.split('\t', line)

        ch = s_line[0]
        par = s_line[1]

        ch_id = get_id(ch)
        par_id = get_id(par)
        
        try:
            child_cats[par_id].add(ch_id)
        except KeyError:
            child_cats[par_id] = set([ch_id])
        try:
            parent_cats[ch_id].add(par_id)
        except KeyError:
            parent_cats[ch_id] = set([par_id])
        
        line = i_file.readline()
    i_file.close()

    print 'CNETWORK LOADED'

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
        
        e_id = get_id(e)
        c_id = get_id(c)
        all_c_set.add(c_id)

        try:
            T_cat[e_id].add(c_id)
        except KeyError:
            T_cat[e_id] = set([c_id])
        try:
            c_to_e[c_id].add(e_id)
        except KeyError:
            c_to_e[c_id] = set([e_id])

        c_preword = re.split('_', c)[0]
        c_postword = re.split('_', c)[-1]
        if c_preword != '':
            try:
                htable_preword[c_preword].add(c_id)
            except KeyError:
                htable_preword[c_preword] = set([c_id])
        if c_postword != '':
            try:
                htable_postword[c_postword].add(c_id)
            except KeyError:
                htable_postword[c_postword] = set([c_id])
        
        line = i_file.readline()
    i_file.close()

    print 'CTRIPLES LOADED'

def load_ktriples():
    # T_know 로딩
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
        all_o_set.add(o)

        e_id = get_id(e)
        r_id = get_id(r)
        o_id = get_id(o)
        
        try:
            T_know[e_id].add((r_id, o_id))
        except KeyError:
            T_know[e_id] = set([(r_id, o_id)])
        try:
            ro_to_e[(r_id, o_id)].add(e_id)
        except KeyError:
            ro_to_e[(r_id, o_id)] = set([e_id])  
        
        line = i_file.readline()
    i_file.close()

    print 'KTRIPLES LOADED'

def mine_rules():
    o_file = open(o_dir + 'experimental_results_(' + mode + ').txt', 'w+')

    overall_time = 0
    pre_rule_cnt = 1
    iteration = 0
    while True:
        iteration += 1
        print 'Iteration:', iteration
        iteration_start_time = time.time()
        
        # ==============================
        # 룰 마이닝
        c_cnt = 0
        for c_id in all_c_set:
            c_cnt = increase_ccnt(c_cnt)
            
            try:
                used_ro_set[c_id]
            except KeyError:
                used_ro_set[c_id] = set([])
            try:
                redundant_ro_set[c_id]
            except KeyError:
                redundant_ro_set[c_id] = set([])

            ro_set = set([])
            for e_id in c_to_e[c_id]:
                try:
                    ro_set |= T_know[e_id]
                except KeyError:
                    pass

            rp_set = set([])
            for (r_id, o_id) in ro_set - used_ro_set[c_id] - redundant_ro_set[c_id]:
                c = get_str(c_id)
                r = get_str(r_id)
                o = get_str(o_id)
                
                # 워드넷 인리칭
                redundant = True
                for o_sim in get_o_simword_set(o):
                    # 어휘 패턴 학습 (어절 단위 매칭: 최소 에러 위함)
                    if len(set(re.split('_', o_sim)) - set(re.split('_', c))) == 0:
                        p = tuple(re.split(re.escape(o_sim), c))
                        if len(p) == 2:
                            rp_set.add((r_id, p, (o_id, o_sim)))
                            redundant = False
                            break
                if redundant:
                    redundant_ro_set[c_id].add((r_id, o_id))

            # 어휘 패턴 전파
            for (r_id, p, (o_id, o_sim)) in rp_set:
                r = get_str(r_id)
                o = get_str(o_id)
                o_sim_id = get_id(o_sim)
                
                similar_o_set = get_category_siblings(o_id)
                similar_o_set |= get_article_siblings(o_id)
                if o_sim != o:
                    similar_o_set |= get_category_siblings(o_sim_id)
                    similar_o_set |= get_article_siblings(o_sim_id)

                # 오브젝트 일치 카테고리 검사
                for s_c_id in get_category_siblings(c_id):
                    s_c = get_str(s_c_id)
                    if o_sim == s_c:
                        generate_rule(s_c_id, r_id, o_id, None)

                # 어휘패턴 일치 카테고리 검사
                submatched_cats = get_submatched_cats(p)
                for s_c_id in get_category_siblings(c_id) & submatched_cats:
                    s_c = get_str(s_c_id)
                    new_o = apply_pattern(s_c, p)
                    new_o_id = get_id(new_o)
                    try:
                        if (r_id, new_o_id) in used_ro_set[s_c_id]:
                            continue
                    except KeyError:
                        pass

                    if new_o_id in similar_o_set or equal_format(new_o, o):
                        # 카테고리, 데이터타입 필터링
                        if mode == 't':
                            if lang == 'en':
                                if new_o in all_o_set:
                                    generate_rule(s_c_id, r_id, new_o_id, (r, p))
                            elif lang == 'ko':
                                try:
                                    new_to_set = ko_to_en[new_o]
                                except KeyError:
                                    new_to_set = set([])

                                for new_to in new_to_set:
                                    if new_to in all_o_set:
                                        new_to_id = get_id(new_to)
                                        generate_rule(s_c_id, r_id, new_to_id, (r, p))
                        else:
                            generate_rule(s_c_id, r_id, new_o_id, (r, p))

        print 'RULES MINED'
        # ==============================
        
        # ==============================
        # 결과 출력
        update_conf()
        print 'CONFIDENCE UPDATED'
        curr_rule_cnt = len(total_conf.items())
        trustworthy_rules = get_trustworthy_rules()
        
        print 'Iteration ' + str(iteration) + ' results:'
        print '\t|rules| =', curr_rule_cnt
        o_file.write('Iteration ' + str(iteration) + ' results:' + '\n')
        o_file.write('\t|rules| = ' + str(curr_rule_cnt) + '\n')

        iteration_end_time = time.time()
        overall_time += iteration_end_time - iteration_start_time
        print '\tSpending time:', iteration_end_time - iteration_start_time
        o_file.write('\tSpending time: ' + str(iteration_end_time - iteration_start_time) + '\n')
        # ==============================

        # ==============================
        # 부트스트래핑 종료 검사
        increase_ratio = float(curr_rule_cnt - pre_rule_cnt) / float(pre_rule_cnt)
        if increase_ratio <= theta_q:
            break
        # ==============================

        # ==============================
        # KB 부트스트래핑
        for e_id in T_cat.keys():
            c_set = T_cat[e_id]
            new_ro_set = set([])
            for c_id in c_set:
                try:
                    new_ro_set |= trustworthy_rules[c_id]
                except KeyError:
                    pass

            for (r_id, o_id) in new_ro_set:
                try:
                    T_know[e_id].add((r_id, o_id))
                except KeyError:
                    T_know[e_id] = set([(r_id, o_id)])
                '''
                try:
                    ro_to_e[(r, o)].add(e)
                except KeyError:
                    ro_to_e[(r, o)] = set([e])
                '''
        # ==============================

        pre_rule_cnt = curr_rule_cnt

    print 'Overall spending time:', overall_time
    o_file.write('Overall spending time: ' + str(overall_time) + '\n')
    o_file.close()

def save_rules():
    # 룰 출력
    o_file = open(o_dir + 'mined_rules.tab', 'w+')
    total_conf_list = sorted(total_conf.items(), key=operator.itemgetter(1), reverse=True)
    for ((c_id, r_id, o_id), t_conf) in total_conf_list:
        c = get_str(c_id)
        r = get_str(r_id)
        o = get_str(o_id)
        
        #rule_str = '?x\t' + 'categorizedIn' + '\t' + c + '\t=>\t?x\t' + r + '\t' + o + '\t' + str(t_conf) + '\t' + str(base_conf[(c_id, r_id, o_id)]) + '\t' + str(stand_conf[(c_id, r_id, o_id)]) + '\n'
        rule_str = '?x\t' + 'categorizedIn' + '\t' + c + '\t=>\t?x\t' + r + '\t' + o + '\t' + str(t_conf) + '\t' + str(stand_conf[(c_id, r_id, o_id)]) + '\n'
        o_file.write(rule_str)
    o_file.close()

def update_conf():    
    for c_id in rules.keys():
        for (r_id, o_id) in rules[c_id]:
            try:
                total_conf[(c_id, r_id, o_id)]
                continue
            except KeyError:
                pass
            
            # Stand conf calculation
            if c_support(c_id) != 0.0:
                stand_conf[(c_id, r_id, o_id)] = cro_support(c_id, r_id, o_id) / c_support(c_id)
            else:
                stand_conf[(c_id, r_id, o_id)] = 0.0

            rp = source_rp[(c_id, r_id, o_id)]
            # Averaged conf calculation
            if rp != None:
                if aggregated_c_support[rp] != 0.0:
                    bounded_cro_support = min(aggregated_cro_support[rp], theta_u)
                    bounded_c_support = min(max(aggregated_c_support[rp], theta_l), theta_u)
                    averaged_conf[(c_id, r_id, o_id)] = bounded_cro_support / bounded_c_support
                else:
                    averaged_conf[(c_id, r_id, o_id)] = 0.0
            else:
                if c_support(c_id) != 0.0:
                    bounded_cro_support = min(cro_support(c_id, r_id, o_id), theta_u)
                    bounded_c_support = min(max(c_support(c_id), theta_l), theta_u)
                    averaged_conf[(c_id, r_id, o_id)] = bounded_cro_support / bounded_c_support
                else:
                    averaged_conf[(c_id, r_id, o_id)] = 0.0

            # Total conf calculation
            sim_score = 0.0
            if rp != None:
                sim_score = get_sim_score(rp[0], rp[1])
                
            dsim_score = 0.0
            if rp != None:
                dsim_score = get_dsim_score(rp[0], rp[1])
                
            total_conf[(c_id, r_id, o_id)] = base_conf[(c_id, r_id, o_id)] + math.pow(sim_score, 2) - math.sqrt(dsim_score)

def increase_ccnt(c_cnt):
    if c_cnt % 100000 == 0:
        print str(c_cnt) + ' / ' + str(len(all_c_set))
    return c_cnt + 1

def c_support(c_id):
    try:
        support = float(len(c_to_e[c_id]))
    except KeyError:
        support = 0.0
        
    return support 

def cro_support(c_id, r_id, o_id):
    c_e_set = set([])
    ro_e_set = set([])
    try:
        c_e_set = c_to_e[c_id]
    except KeyError:
        pass
    try:
        ro_e_set = ro_to_e[(r_id, o_id)]
    except KeyError:
        pass
    support = float(len(c_e_set & ro_e_set))
    
    return support

def get_simword_set(w):    
    # 현재 영어만 워드넷으로 확장 가능
    if len(w) <= 0:
        return set([])

    l_set = set([w])
    try:
        s_set = l_s_links[w]
        for s in s_set:
            l_set |= s_l_links[s]
            try:
                for mm in s_mm_links[s]:
                    l_set |= s_l_links[mm]
            except KeyError:
                pass
            try:
                for mh in s_mh_links[s]:
                    l_set |= s_l_links[mh]
            except KeyError:
                pass
    except:
        pass

    return l_set

def get_dsimword_set(w):
    # 현재 영어만 워드넷으로 얻을 수 있음
    if len(w) <= 0:
        return set([])

    a_set = set([])
    try:
        a_set |= l_a_links[w]
    except:
        pass
    return a_set

def trans_ko_to_en(w):
    try:
        return ko_to_en[w]
    except KeyError:
        return set([])

def trans_en_to_ko(w):
    try:
        return en_to_ko[w]
    except KeyError:
        return set([])

sim_score_history = {}
def get_sim_score(r, p):
    # Memoization
    try:
        return sim_score_history[r][p]
    except KeyError:
        try:
            sim_score_history[r]
        except KeyError:
            sim_score_history[r] = {}

        sim_score_history[r][p] = 0.0
    # /Memoization
    
    sim_score = 0.0

    p_simword_set = set([])
    for p_part in p:
        for p_w in re.split('_', p_part):
            p_simword_set.add(p_w)
            
            en_p_wset = set([p_w])
            if lang == 'ko':
                en_p_wset |= trans_ko_to_en(p_w)
            for en_p_w in en_p_wset:         
                p_simword_set |= get_simword_set(en_p_w)

    r_words = re.split('_', r)
    for r_w in r_words:
        r_simword_set = set([r_w])
        
        en_r_wset = set([r_w])
        if lang == 'ko':
            en_r_wset |= trans_ko_to_en(r_w)
        for en_r_w in en_r_wset:
            r_simword_set |= get_simword_set(en_r_w)
        
        max_sim = 0.0
        for r_l in r_simword_set:
            for p_l in p_simword_set:
                try:
                    sim = 0.0
                    if r_l == p_l:
                        sim = 1.0
                    else:
                        sim = model.similarity(r_l, p_l)

                    if sim > max_sim:
                        max_sim = sim
                except KeyError:
                    pass

        sim_score += max_sim                

    total_cnt = float(len(r_words))
    if total_cnt != 0.0:
        sim_score /= total_cnt

    sim_score_history[r][p] = sim_score
    
    return sim_score

dsim_score_history = {}
def get_dsim_score(r, p):
    # Memoization
    try:
        return dsim_score_history[r][p]
    except KeyError:
        try:
            dsim_score_history[r]
        except KeyError:
            dsim_score_history[r] = {}

        dsim_score_history[r][p] = 0.0
    # /Memoization
    
    dsim_score = 0.0

    p_simword_set = set([])
    for p_part in p:
        for p_w in re.split('_', p_part):
            p_simword_set.add(p_w)
            
            en_p_wset = set([p_w])
            if lang == 'ko':
                en_p_wset |= trans_ko_to_en(p_w)
            for en_p_w in en_p_wset:         
                p_simword_set |= get_simword_set(en_p_w)
    
    r_words = re.split('_', r)
    for r_w in r_words:
        r_dsimword_set = set([])

        en_r_wset = set([r_w])
        if lang == 'ko':
            en_r_wset |= trans_ko_to_en(r_w)
        for en_r_w in en_r_wset:
            r_dsimword_set |= get_dsimword_set(en_r_w)
        
        max_dsim = 0.0
        for r_a in r_dsimword_set:
            for p_l in p_simword_set:
                try:
                    dsim = 0.0
                    if r_a == p_l:
                        dsim = 1.0
                    else:
                        dsim = model.similarity(r_a, p_l)

                    if dsim > max_dsim:
                        max_dsim = dsim
                except KeyError:
                    pass

        dsim_score += max_dsim                

    total_cnt = float(len(r_words))
    if total_cnt != 0.0:
        dsim_score /= total_cnt

    dsim_score_history[r][p] = dsim_score
    
    return dsim_score

def get_o_simword_set(w):    
    o_simword_set = set([])
    if lang == 'en':
        o_simword_set |= get_simword_set(w)
    elif lang == 'ko':
        if mode == 't':
            en_simword_set = get_simword_set(w)
            for en_sim in en_simword_set:
                o_simword_set |= trans_en_to_ko(en_sim)
        else:
            o_simword_set.add(w)

            en_simword_set = set([])
            trans_w_set = trans_ko_to_en(w)
            for t_w in trans_w_set:
                try:
                    en_simword_set |= get_simword_set(t_w)
                except KeyError:
                    pass
            for en_sim in en_simword_set:
                try:
                    o_simword_set |= en_to_ko[en_sim]
                except KeyError:
                    pass
    
    return o_simword_set

category_siblings = {}
def get_category_siblings(x):
    # Memoization
    try:
        return category_siblings[x]
    except KeyError:
        pass

    local_c_siblings = set([x])
    try:
        # x가 카테고리일 때의 sibling들
        parents = parent_cats[x]
        for par in parents:
            try:
                local_c_siblings |= child_cats[par]
            except KeyError:
                pass
    except KeyError:
        pass

    for c_s in local_c_siblings:
        category_siblings[c_s] = local_c_siblings

    return local_c_siblings

article_siblings = {}
def get_article_siblings(x):
    # Memoization
    try:
        return article_siblings[x]
    except KeyError:
        pass

    local_a_siblings = set([x])
    try:
        # x가 아티클일 때의 sibling들
        categories = T_cat[x]
        for cat in categories:
            try:
                local_a_siblings |= c_to_e[cat]
            except KeyError:
                pass
    except KeyError:
        pass

    for a_s in local_a_siblings:
        article_siblings[a_s] = local_a_siblings

    return local_a_siblings

def apply_pattern(c, p):    
    o = c
    for p_part in p:
        o = o.replace(p_part, '')

    return o

def equal_format(w1, w2):
    answer = False

    if tc.is_int(w1) and tc.is_int(w2):
        answer = True
    elif tc.is_float(w1) and tc.is_float(w2):
        answer = True
    elif tc.is_double(w1) and tc.is_double(w2):
        answer = True
    elif tc.is_date(w1) and tc.is_date(w2):
        answer = True

    return answer

def get_submatched_cats(p):
    submatched_cats = set([])
    
    p_preword = re.split('_', p[0])[0]
    p_postword = re.split('_', p[-1])[-1]
    if p_preword != '':
        try:
            submatched_cats |= htable_preword[p_preword]
        except KeyError:
            pass
    if p_postword != '':
        try:
            submatched_cats |= htable_postword[p_postword]
        except KeyError:
            pass

    return submatched_cats

def generate_rule(c_id, r_id, o_id, rp):
    # 룰 생성
    try:
        rules[c_id].add((r_id, o_id))
    except KeyError:
        rules[c_id] = set([(r_id, o_id)])
    #print (c, r, o)

    # 신뢰값을 위한 기록
    source_rp[(c_id, r_id, o_id)] = rp

    try:
        aggregated_c_support[rp]
    except KeyError:
        aggregated_c_support[rp] = 0.0
    try:
        aggregated_cro_support[rp]
    except KeyError:
        aggregated_cro_support[rp] = 0.0

    # For averaged conf
    try:
        aggregated_c_support[rp] += c_support(c_id)
    except KeyError:
        pass
    try:
        aggregated_cro_support[rp] += cro_support(c_id, r_id, o_id)
    except KeyError:
        pass

    # 히스토리 기록
    try:
        used_ro_set[c_id].add((r_id, o_id))
    except KeyError:
        used_ro_set[c_id] = set([(r_id, o_id)])

def get_trustworthy_rules():
    trustworthy_rules = {}
    conf_list = sorted(total_conf.items(), key=operator.itemgetter(1), reverse=True)
    for ((c_id, r_id, o_id), conf) in conf_list:
        if float(conf) >= theta_c:
            try:
                trustworthy_rules[c_id].add((r_id, o_id))
            except KeyError:
                trustworthy_rules[c_id] = set([(r_id, o_id)])
    return trustworthy_rules

def get_id(x):
    try:
        csroid = csro_id[x]
    except KeyError:
        csro_id[x] = len(csro_str)
        csro_str[csro_id[x]] = x

        csroid = csro_id[x]

    return csroid
    
def get_str(csroid):
    return csro_str[csroid]

main()
