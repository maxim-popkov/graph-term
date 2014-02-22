#-*- coding: utf-8 -*-
from Vertex import Vertex
from Edge import  Edge
from TermGraph import TermGraph
import Reader
import nltk
from Reporter import Reporter
from os import listdir
from os.path import isfile, join

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

__author__ = 'dales3d'


def test_vertex():
    v1 = Vertex()
    print v1.term_weight_tf
    v1.term_weight_tf = 3
    v1.term_weight_tf = 6
    print v1._termWeightOldTF
    print v1.term_weight_tf

    print v1.term_weight_rw
    v1.term_weight_rw = 10
    v1.term_weight_rw = 12
    print v1.term_weight_rw
    print v1._termWeightOldRW

    print v1.term_value
    v1.term_value = 'some term'
    print v1.term_value

def test_graph():
    g1 = TermGraph()
    v1 = Vertex('vert1', 2)
    v2 = Vertex('vert2', 2)
    e1 = Edge(v1, v2)
    g1.add_edge(e1)

    v3 = Vertex('vert3', 3)
    v4 = Vertex('vert4', 4)
    e2 = Edge(v3, v4)
    g1.add_edge(e2)

    e3 = Edge(v1,v4)
    g1.add_edge(e3)
    g1.add_edge(e1)


    print g1._verticlesJoins
    print g1._verticles
    print g1._edges

    g1.recalc_edges()
    g1.recalc_vert_weights()
    g1.recalc_vert_weights()

    for x in xrange(0,10):
        print '--------' + str(x) + '------'
        g1.recalc_vert_weights()

def comparator(v1, v2):
    if v1.term_weight_rw > v2.term_weight_rw:
        return 1
    elif v1.term_weight_rw < v2.term_weight_rw:
        return -1
    return 0

def file_report():
    raw_txt = Reader.readFromFile('data/test1')
    words = Reader.extractWords(raw_txt)
    keywords = Reader.meter(words)
    window = 3

    graph_rw = TermGraph()

    stopwords = nltk.corpus.stopwords.words('english')
    words_clean = []
    for word in words:
        if word not in stopwords:
            words_clean.append(word)
    words = words_clean
    length = words.__len__()
   # print length, len(keywords), window
   # print words

    for i in xrange(0, length-1, 2):
        print '----', i, '----'
        print words[i:i+window]
        v1 = Vertex(words[i], keywords[words[i]])
        v2 = Vertex(words[i+1], keywords[words[i+1]])
        v3 = Vertex(words[i+2], keywords[words[i+2]])
        e1 = Edge(v1, v2)
        e2 = Edge(v1, v3)
        e3 = Edge(v2, v3)
        graph_rw.add_edge(e1)
        graph_rw.add_edge(e2)
        graph_rw.add_edge(e3)


    graph_rw.recalc_edges()

    mode = 'rw'
    graph_rw.recalc_vert_weights(mode)

    for i in xrange(0,100):
        graph_rw.recalc_vert_weights(mode)


    array = graph_rw._verticles.values()
    array.sort(comparator)

    #report
    file = './test_results/' + mode + '-win3.csv'
    toCsv = ''
    for v in array:
        num_joins = graph_rw._verticlesJoins[v.term_value].__len__()
        toCsv += str(v.term_value) + ',' +str(v.term_weight_rw) + ',' + str(v.term_weight_tf) + '\n'
        print v, v.term_weight_rw, num_joins, v.term_weight_tf
        print graph_rw._verticlesJoins[v.term_value]
    #with open(file, "w") as f_out:
    #    f_out.write(toCsv)
    #    f_out.close()


    #reader.writeToFile(output_file, keywords)
config = \
    {
        'windows': [2],
        'methods': ['rw_oc'],  # , 'rw', 'pr'],
        'trg': './kostop/',  # './test_results/'
        'src': './data/psy/'  # './data/All_in/'# './data/Arts/'
    }

def test_doc():
    files = [f for f in listdir(config['src']) if isfile(join(config['src'], f))]
    #files = ['aita2011', 'Мур_алг_статико-дин_расп', 'Програм_Хопфилд']

    for f in files:
        f_full_name = join(config['src'], f)
        reporter = Reporter(config['windows'], config['methods'])
        #reporter.report_for_file(f_full_name)
        #reporter.save_report_detailed(f_full_name, config['trg'] + f + 'DetailCsvRes' + '.csv')
        #reporter.save_report_top_words(f_full_name, config['trg'] + f + 'TopCsvRes' + '.csv')
        #reporter.save_report_excel_graph(f_full_name, config['trg'] + f + 'GraphCsvRes' + '.csv')
        v1, v2 = reporter.similiarity_of_texts('./data/psy/3', f_full_name)
        print f, ': ', v1, v2
        print f, ': ', v1 * (1 + v2)

def test_reuters_with_bayse():
    reporter = Reporter(config['windows'], config['methods'])
    #categories = ['livestock', 'jobs']
    #categories = ['crude', 'livestock', 'jobs', 'ship', 'corn', 'trade', 'interest']

    #categories = ['crude', 'livestock', 'earn', 'acq', 'grain', 'wheat', 'money', 'jobs', 'ship', 'corn', 'trade', 'interest']
    categories = ['crude', 'livestock', 'earn', 'jobs', 'ship', 'corn', 'trade', 'interest']
    #categories = ['acq', 'alum', 'barley', 'bop', 'carcass', 'castor-oil', 'cocoa', 'coconut', 'coconut-oil', 'coffee', 'copper', 'copra-cake', 'corn', 'cotton', 'cotton-oil', 'cpi', 'cpu', 'crude', 'dfl', 'dlr', 'dmk', 'earn', 'fuel', 'gas', 'gnp', 'gold', 'grain', 'groundnut', 'groundnut-oil', 'heat', 'hog', 'housing', 'income', 'instal-debt', 'interest', 'ipi', 'iron-steel', 'jet', 'jobs', 'l-cattle', 'lead', 'lei', 'lin-oil', 'livestock', 'lumber', 'meal-feed', 'money-fx', 'money-supply', 'naphtha', 'nat-gas', 'nickel', 'nkr', 'nzdlr', 'oat', 'oilseed', 'orange', 'palladium', 'palm-oil', 'palmkernel', 'pet-chem', 'platinum', 'potato', 'propane', 'rand', 'rape-oil', 'rapeseed', 'reserves', 'retail', 'rice', 'rubber', 'rye', 'ship', 'silver', 'sorghum', 'soy-meal', 'soy-oil', 'soybean', 'strategic-metal', 'sugar', 'sun-meal', 'sun-oil', 'sunseed', 'tea', 'tin', 'trade', 'veg-oil', 'wheat', 'wpi', 'yen', 'zinc']

    for cat in categories:
        print '----', cat, '----'
        reporter.get_category_top(categories, cat, 'rw_oc', 3)
        reporter.get_category_top_tf(categories, cat, 'rw_oc', 3)
        #reporter.get_category_graph(categories, cat, 'rw_oc', 2)

def test_reuters_with_graph_sim():
    reporter = Reporter(config['windows'], config['methods'])
    #categories = ['crude', 'livestock', 'earn', 'jobs', 'ship', 'corn', 'trade', 'interest']
    categories = ['livestock', 'jobs']
    #categories = ['crude', 'livestock', 'jobs', 'ship', 'corn', 'trade', 'interest']

    for cat in categories:
        print '----', cat, '----'
        reporter.get_category_graph(categories, cat, 'rw_oc', 2)


if __name__ == '__main__':
    #test_reuters_with_bayse()
    #test_reuters_with_graph_sim()
    reporter = Reporter(config['windows'], config['methods'])
    reporter.report_for_file('./data/rusTextChiliGuake')
    reporter.save_report_detailed('./data/rusTextChiliGuake', './tes/diplom.csv')
#
#---- crude ----
#{'earn': 24, 'jobs': 0, 'livestock': 0, 'corn': 0, 'trade': 3, 'interest': 0, 'crude': 155, 'ship': 7}
#82.0105820106
#{'earn': 27, 'jobs': 0, 'livestock': 0, 'corn': 0, 'trade': 3, 'interest': 0, 'crude': 153, 'ship': 6}
#80.9523809524

#---- livestock ----
#{'earn': 0, 'jobs': 0, 'livestock': 16, 'corn': 6, 'trade': 1, 'interest': 1, 'crude': 0, 'ship': 0}
#66.6666666667
#{'earn': 0, 'jobs': 0, 'livestock': 18, 'corn': 5, 'trade': 1, 'interest': 0, 'crude': 0, 'ship': 0}
#75.0

#---- earn ----
#{'earn': 1049, 'jobs': 0, 'livestock': 0, 'corn': 1, 'trade': 3, 'interest': 1, 'crude': 33, 'ship': 0}
#96.5041398344
#{'earn': 1048, 'jobs': 0, 'livestock': 0, 'corn': 1, 'trade': 3, 'interest': 1, 'crude': 34, 'ship': 0}
#96.4121435143

#---- jobs ----
#{'earn': 3, 'jobs': 10, 'livestock': 0, 'corn': 0, 'trade': 7, 'interest': 1, 'crude': 0, 'ship': 0}
#47.619047619
#{'earn': 3, 'jobs': 10, 'livestock': 0, 'corn': 0, 'trade': 6, 'interest': 2, 'crude': 0, 'ship': 0}
#47.619047619

#---- ship ----
#{'earn': 2, 'jobs': 0, 'livestock': 0, 'corn': 1, 'trade': 4, 'interest': 0, 'crude': 4, 'ship': 78}
#87.6404494382
#{'earn': 2, 'jobs': 0, 'livestock': 0, 'corn': 0, 'trade': 4, 'interest': 0, 'crude': 3, 'ship': 80}
#89.8876404494

#---- corn ----
#{'earn': 0, 'jobs': 0, 'livestock': 0, 'corn': 53, 'trade': 2, 'interest': 0, 'crude': 0, 'ship': 1}
#94.6428571429
#{'earn': 1, 'jobs': 0, 'livestock': 1, 'corn': 52, 'trade': 1, 'interest': 0, 'crude': 0, 'ship': 1}
#92.8571428571

#---- trade ----
#{'earn': 5, 'jobs': 0, 'livestock': 0, 'corn': 1, 'trade': 106, 'interest': 3, 'crude': 1, 'ship': 1}
#90.5982905983
#{'earn': 5, 'jobs': 0, 'livestock': 0, 'corn': 1, 'trade': 105, 'interest': 3, 'crude': 2, 'ship': 1}
#89.7435897436

#---- interest ----
#{'earn': 5, 'jobs': 0, 'livestock': 0, 'corn': 1, 'trade': 22, 'interest': 102, 'crude': 1, 'ship': 0}
#77.8625954198
#{'earn': 6, 'jobs': 0, 'livestock': 0, 'corn': 1, 'trade': 22, 'interest': 101, 'crude': 1, 'ship': 0}
#77.0992366412