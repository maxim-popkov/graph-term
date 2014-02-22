#-*- coding: utf-8 -*-
__author__ = 'dales3d'

from Vertex import Vertex
from Edge import Edge
from TermGraph import TermGraph
from Report import Report
import Reader
import nltk
from nltk.corpus import reuters


class Reporter(object):
    def __init__(self, windows=[2], methods=["rw"]):
        self._windows = windows
        self._methods = methods
        self._terms = []  # документ как список термов
        self._keywords = {}  # словарь термов с параметром tf {term: tf}
        self._reportDir = ''
        self._reportFiles = []
        self._extentions = []
        self._reports = {}
        self.graph_cache = {}
        self.classifier_rw_cache = None
        self.classifier_tf_cache = None
        self.tf_features_cache = {}
        self.rw_features_cache = {}
        print 'reporter init'

    @property
    def reportDir(self):
        return self._reportDir

    @reportDir.setter
    def reportDir(self, value):
        self._reportDir = self.value

    @property
    def exts(self):
        return self._extentions

    @exts.setter
    def exts(self, value):
        self._extentions = self.value

    def save_report_detailed(self, r_name, out_file):
        report = self._reports[r_name]
        with open(out_file, "w") as f_out:
            result = report.csv
            f_out.write(result)
            f_out.close()

    def save_report_top_words(self, r_name, out_file):
            report = self._reports[r_name]
            with open(out_file, "w") as f_out:
                result = report.csv_top20
                f_out.write(result)
                f_out.close()

    def save_report_excel_graph(self, r_name, out_file):
            report = self._reports[r_name]
            with open(out_file, "w") as f_out:
                result = report.excel_graph
                f_out.write(result)
                f_out.close()

    #строит отчет для заданного метода и окна
    #нужен для совместимости (зависит от внутренних полей terms, keywords)
    def get_rw_for(self, method, window):
        graph = TermGraph()
        terms = self._terms
        keywords = self._keywords
        length = len(terms)
        # balance для случая, когда длина массива не делится на цело на шаг,
        # избегание выхода за границу массива
        balance = length % window
        last_step = length / window + 1

        edges = []
        for i in xrange(0, length - 1, window - 1):
            #print '----', i, '----'
            #print terms[i:i+window]
            #заполняем вершины
            verts = []
            vert_border = i + window
            edge_border = window

            if vert_border > length:
                balance = vert_border - length
                vert_border -= balance
                edge_border -= balance
                #print length, vert_border, balance
            for k in xrange(i, vert_border):
                term = terms[k]
                v = Vertex(term, keywords[term])
                verts.append(v)
                #заполняем ребра
            for x in xrange(0, edge_border):
                for y in xrange(x + 1, edge_border):
                    edge = Edge(verts[x], verts[y])
                    edges.append(edge)

        for edge in edges:
            graph.add_edge(edge)

        #for v in graph._verticles.values():
        #    print v.term_value, v.term_weight_rw

        graph.recalc_edges()
        graph.recalc_vert_weights(method)

        for i in xrange(0, 10):
            graph.recalc_vert_weights(method)

        array = graph._verticles.values()
        array.sort(comparator)
        return (array, graph)

    def get_category_top(self, categories, cat_test, mode='rw_oc', window=3):
        if not self.classifier_rw_cache:
            gr_array = {}
            for category in categories:
                gr_array[category] = []

            for category in categories:
                files = Reader.batchReadReuters('training', [category])

                for file_name in files:
                    raw_txt = Reader.readFromFile('/home/dales3d/nltk_data/corpora/reuters/' + file_name)
                    words = Reader.extractWords(raw_txt)
                    keywords = Reader.meter(words)
                    if file_name not in self.graph_cache.keys():
                        gr = self.get_graph_for(words, keywords, mode, window)
                        self.graph_cache[file_name] = gr
                        #print 'Go to Cache ', file_name
                    else:
                        gr = self.graph_cache[file_name]
                        #print 'from cache: ', file_name
                    gr_array[category].append(gr)


            top_words_rw = set()
            gr_ver_arr = []
            for k in gr_array.keys():
                gr_ver_arr += gr_array[k]
            for gr in gr_ver_arr:
                #top_tf = gr.getTopWords("rw_oc", 50)
                top_rw = gr.getTopVerts("rw", 100)
                #for w_tf in top_tf:
                #    top_words_tf.add(w_tf)
                for w_rw in top_rw:
                    top_words_rw.add(w_rw)

            #inter = top_words_rw & top_words_tf

            rw_dict = {}
            for v in top_words_rw:
                if v.term_value in rw_dict:
                    if v.term_weight_rw > rw_dict[v.term_value]:
                        rw_dict[v.term_value] = v.term_weight_rw
                else:
                    rw_dict[v.term_value] = v.term_weight_rw

            sort_rw = sorted(rw_dict.items(), key=lambda x: x[1], reverse=True)
            sort_rw = sort_rw[:1000]
            self.rw_features_cache = sort_rw

            training_set = []
            for category in categories:
                for gr in gr_array[category]:
                    top_rw = gr.getTopVerts("rw_oc", 100)
                    features = {}
                    file_top_words = set()
                    for w_rw in top_rw:
                        file_top_words.add(w_rw.term_value)
                    for term in sort_rw:
                        features[term[0]] = (term[0] in file_top_words)
                    training_set.append((features, category))
            self.classifier_rw_cache = nltk.NaiveBayesClassifier.train(training_set)

        #from cache
        sort_rw = self.rw_features_cache
        #test
        #cat_test = "jobs"
        files = Reader.batchReadReuters('test', [cat_test])
        #gr_tests
        results = {}
        for category in categories:
            results[category] = 0
        for f in files:
            cats = reuters.categories(f)
            raw_txt = Reader.readFromFile('/home/dales3d/nltk_data/corpora/reuters/' + f)
            words = Reader.extractWords(raw_txt)
            keywords = Reader.meter(words)
            if f in self.graph_cache.keys():
                #print f
                gr = self.graph_cache[f]
            else:
                gr = self.get_graph_for(words, keywords, mode, window)
            top_rw = gr.getTopVerts("rw_oc", 1000)
            features = {}
            file_top_words = set()
            for w_rw in top_rw:
                file_top_words.add(w_rw.term_value)
            for term in sort_rw:
                features[term[0]] = (term[0] in file_top_words)
            result = self.classifier_rw_cache.classify(features)
            if result in cats:
                results[cat_test] += 1
            else:
                results[result] += 1
        print results
        sum = 0
        for cat_key in results.keys():
            sum += results[cat_key]
        print float(results[cat_test])/sum * 100

        #print sort_rw[:100]
        #print sort_tf[:100]

        #print len(inter)
        #print len(top_words_rw), len(top_words_rw)

    def get_category_top_tf(self, categories, cat_test, mode='rw_oc', window=3):
        if not self.classifier_tf_cache:
            gr_array = {}
            for category in categories:
                gr_array[category] = []

            for category in categories:
                files = Reader.batchReadReuters('training', [category])

                for file_name in files:
                    raw_txt = Reader.readFromFile('/home/dales3d/nltk_data/corpora/reuters/' + file_name)
                    words = Reader.extractWords(raw_txt)
                    keywords = Reader.meter(words)
                    if file_name not in self.graph_cache.keys():
                        gr = self.get_graph_for(words, keywords, mode, window)
                        self.graph_cache[file_name] = gr
                    else:
                        #print 'tf from cache: ', file_name
                        gr = self.graph_cache[file_name]
                    gr_array[category].append(gr)

            top_words_tf = set()
            gr_ver_arr = []
            for k in gr_array.keys():
                gr_ver_arr += gr_array[k]
            for gr in gr_ver_arr:
                top_tf = gr.getTopVerts("tf", 100)
                for w_tf in top_tf:
                    top_words_tf.add(w_tf)

            tf_dict = {}
            for v in top_words_tf:
                if v.term_value in tf_dict:
                    tf_dict[v.term_value] += v.term_weight_tf
                    #if v.term_weight_tf > tf_dict[v.term_value]:
                    #    tf_dict[v.term_value] += v.term_weight_tf
                else:
                    tf_dict[v.term_value] = v.term_weight_tf

            sort_tf = sorted(tf_dict.items(), key=lambda x: x[1], reverse=True)
            sort_tf = sort_tf[:1000]
            self.tf_features_cache = sort_tf

            training_set = []
            for category in categories:
                for gr in gr_array[category]:
                    top_tf = gr.getTopVerts("tf", 100)
                    features = {}
                    file_top_words = set()
                    for w_tf in top_tf:
                        file_top_words.add(w_tf.term_value)
                    for term in sort_tf:
                        features[term[0]] = (term[0] in file_top_words)
                    training_set.append((features, category))

            self.classifier_tf_cache = nltk.NaiveBayesClassifier.train(training_set)
        #from cache
        sort_tf = self.tf_features_cache
        #test
        #cat_test = "jobs"
        files = Reader.batchReadReuters('test', [cat_test])
        #gr_tests
        results = {}
        for category in categories:
            results[category] = 0
        for f in files:
            cats = reuters.categories(f)
            raw_txt = Reader.readFromFile('/home/dales3d/nltk_data/corpora/reuters/' + f)
            words = Reader.extractWords(raw_txt)
            keywords = Reader.meter(words)
            if f not in self.graph_cache.keys():
                gr = self.get_graph_for(words, keywords, mode, window)
                self.graph_cache[f] = gr
            else:
                gr = self.graph_cache[f]
            top_tf = gr.getTopVerts("tf", 1000)
            features = {}
            file_top_words = set()
            for w_tf in top_tf:
                file_top_words.add(w_tf.term_value)
            for term in sort_tf:
                features[term[0]] = (term[0] in file_top_words)
            result = self.classifier_tf_cache.classify(features)
            if result in cats:
                results[cat_test] += 1
            else:
                results[result] += 1
        print results
        sum = 0
        for cat_key in results.keys():
            sum += results[cat_key]
        print float(results[cat_test])/sum * 100

    def get_category_graph(self, categories, cat_test, mode='rw_oc', window=3):
        gr_array = {}

        #print '--indexing--'
        for category in categories:
            files = Reader.batchReadReuters('training', [category])
            #print 'category: ', category
            big_cat_raw_txt = ''
            #print '1) read files: start'
            for file_name in files:
                big_cat_raw_txt += Reader.readFromFile('/home/dales3d/nltk_data/corpora/reuters/' + file_name)
            #print '1) read files: finished'
            #print '2) preprocess text: start'
            words = Reader.extractWords(big_cat_raw_txt)
            keywords = Reader.meter(words)
            #print '2) preprocess text: finished'
            #print '3) term weighting: start'
            if category in self.graph_cache.keys():
                gr = self.graph_cache[category]
            else:
                gr = self.get_graph_for(words, keywords, mode, window)
                self.graph_cache[category] = gr
            #print '3) term weighting: finished'
            gr_array[category] = gr

        files = Reader.batchReadReuters('test', [cat_test])
        #gr_tests
        results = {}
        results[''] = 0
        for category in categories:
            results[category] = 0
        for f in files:
            #print '---', f, '---'
            cats = reuters.categories(f)
            raw_txt = Reader.readFromFile('/home/dales3d/nltk_data/corpora/reuters/' + f)
            words = Reader.extractWords(raw_txt)
            keywords = Reader.meter(words)
            if f not in self.graph_cache.keys():
                gr = self.get_graph_for(words, keywords, mode, window)
                self.graph_cache[f] = gr
            else:
                gr = self.graph_cache[f]

            sim = {}
            max_res = 0.0
            max_cat = ''
            for category in categories:
                gr_1 = gr_array[category]
                gr_2 = gr
                #(mes_l, mes_r) = TermGraph.compare_graphs_terms_with_weight(gr_1, gr_2)
                mesuare_terms = TermGraph.compare_graphs_terms_with_weight(gr_1, gr_2)
                mesuare_edges = TermGraph.compare_graphs_edges(gr_1, gr_2)
                res = mesuare_terms * (1 + mesuare_edges)
                if max_res < res:
                    max_cat = category
                    max_res = res
                sim[category] = res

            if max_cat in cats:
                results[cat_test] += 1
                #print max_res
            else:
                results[max_cat] += 1
                #print max_res
                print 'no ok'
        print results
        sum = 0
        for cat_key in results.keys():
            sum += results[cat_key]
        print float(results[cat_test])/sum * 100

    def get_graph_for(self, doc_terms, doc_keywords, method, window):
        """
        @param doc_terms - последовательность термов документа:
        @param doc_keywords - ключевые слова с их частотами вхождения:
        @param method - метод подсчета весов:
        @param window - окно для подсчета весов:
        @return граф документа:
        """
        graph = TermGraph()
        terms = doc_terms
        keywords = doc_keywords
        cache_verts = {}
        length = len(terms)
        # balance для случая, когда длина массива не делится на цело на шаг,
        # избегание выхода за границу массива
        balance = length % window
        last_step = length / window + 1

        edges = []
        for i in xrange(0, length - 1, window - 1):
            verts = []
            vert_border = i + window
            edge_border = window

            if vert_border > length:
                balance = vert_border - length
                vert_border -= balance
                edge_border -= balance
                #print length, vert_border, balance
            for k in xrange(i, vert_border):
                term = terms[k]
                if term in cache_verts:
                    v = cache_verts[term]
                else:
                    v = Vertex(term, keywords[term]) #tf уже посчитан
                    cache_verts[term] = v

                verts.append(v)
                #заполняем ребра
            for x in xrange(0, edge_border):
                for y in xrange(x + 1, edge_border):
                    edge = Edge(verts[x], verts[y])
                    edges.append(edge)

        for edge in edges:
            graph.add_edge(edge)

        #for v in graph._verticles.values():
        #    print v.term_value, v.term_weight_rw

        graph.recalc_edges()
        graph.recalc_vert_weights(method)

        for i in xrange(0, 10):
            graph.recalc_vert_weights(method)

        return graph

    def report_for_file(self, file_name):
        print 'report for: ' + file_name
        windows = self._windows
        methods = self._methods
        report = Report(file_name, windows, methods)

        raw_txt = Reader.readFromFile(file_name)
        #print raw_txt

        words = Reader.extractWords(raw_txt, "russian")

        keywords = Reader.meter(words)
        self._keywords = keywords
        self._terms = words

        #инициализация отчета термами с tf
        for term in self._terms:
            report.add_term_tf(term, keywords[term])

        for window in windows:
            for method in methods:
                print method, window
                (array, graph) = self.get_rw_for(method, window)
                report._graph = graph #todo graph как св-во, пересмотреть логику
                for v in array:
                    term = v.term_value
                    report.add_term_rw_stats(term, method, window, v.term_weight_rw)

        self._reports[file_name] = report

    def similiarity_of_texts(self, txt1, txt2):
        #print 'report for: ' + txt1
        #print 'report for: ' + txt2
        window = self._windows[0]
        method = self._methods[0]
        raw_txt_1 = Reader.readFromFile(txt1)
        raw_txt_2 = Reader.readFromFile(txt2)
        words_1 = Reader.extractWords(raw_txt_1, "russian")
        words_2 = Reader.extractWords(raw_txt_2, "russian")
        keywords_1 = Reader.meter(words_1)
        keywords_2 = Reader.meter(words_2)
        (gr_1) = self.get_graph_for(words_1, keywords_1, method, window)
        (gr_2) = self.get_graph_for(words_2, keywords_2, method, window)
        mesuare_terms = TermGraph.compare_graphs_terms(gr_1, gr_2)
        mesuare_edges = TermGraph.compare_graphs_edges(gr_1, gr_2)
        return (mesuare_terms, mesuare_edges)

    def report_for_files(self, files):
        print 'report for files: ' + str(files)

    def report_for_dir(self, dir):
        print 'report for dir: ' + dir


def comparator(v1, v2):
    if v1.term_weight_rw > v2.term_weight_rw:
        return 1
    elif v1.term_weight_rw < v2.term_weight_rw:
        return -1
    return 0
