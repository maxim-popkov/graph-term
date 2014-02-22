#-*- coding: utf-8 -*-
from operator import itemgetter

__author__ = 'dales3d'

class Report(object):

    def __init__(self, file_name='', windows=[2], methods=["rw"], graph=None):
        self._file = file_name
        self._windows = windows
        self._methods = methods
        self._terms = {}
        self._graph = graph

        print 'init report: ' + self._file

    def add_term_tf(self, term, tf):
        self._terms[term] = {"tf": tf}

    def add_term_rw_stats(self, term, method, window, stat):
        if window in self._terms[term]:
            self._terms[term][window][method] = stat
        else:
            self._terms[term][window] = {method: stat}



        #dict = {
        #        term:
        #            {
        #                "tf": 12,
        #                window: {method, stat}
        #            }
        #}

    @property
    def csv(self):
        result = ''
        divider = ';'
        terms = self._terms.keys()
        for term in terms:
            term_info = self._terms[term]
            result += term + divider
            result += str(term_info["tf"]) + divider
            for window in self._windows:
                for method in self._methods:
                    result += str(term_info[window][method]) + divider
            result += '\n'
        return result

    @property
    def csv_top20(self):
        result = ''
        divider = ';'
        words_num = 30

        for window in self._windows:
            for method in self._methods:
                result += method + divider
            result += divider
        result += '\n'

        sorted_top = {}
        for window in self._windows:
            sorted_top[window] = {}
            for method in self._methods:
                sort_arr = self.top_terms_for(window, method)
                sorted_top[window][method] = sort_arr[:words_num]
        for i in xrange(0, words_num):
            for window in self._windows:
                for method in self._methods:
                    (term, val) = sorted_top[window][method][i]
                    result += term + divider# + str(val) + divider
                result += divider
            result += '\n'
        return result

    @property
    def excel_graph(self):
        result = ''
        divider = ';'
        method = 'rw_oc'
        window = 3
        #hardcode todo fix hardcode
        sorted_top = self.top_terms_for(3, method)
        length = len(sorted_top)

        for i in xrange(0, length):
            (term, val) = sorted_top[i]
            result += term + divider
            for t in self._graph._verticlesJoins[term]:
                result += t + divider
            result += '\n'
        return result

    #return tuple (term, value)
    def top_terms_for(self, window, method):
        keys = self._terms.keys()
        dict = self._terms
        dirty_values = []
        for key in keys:
            dirty_values.append((key, dict[key][window][method]))#key = term
        sort_vals = sorted(dirty_values, key=itemgetter(1), reverse=True)
        return sort_vals