#-*- coding: utf-8 -*-
from Vertex import Vertex
from Edge import Edge
__author__ = 'dales3d'


class TermGraph(object):
    _calc_mode = ['pr', 'rw', 'rw_oc']
    _precision = 0.001
    def __init__(self):
        self._verticles = {} #словарь всех вершин типа Vertex
        self._verticlesJoins = {} #словарь {term: set([terms])} для хранения связей вершин
        self._verticlesJoinsNum = {} #experiment field словарь для хранения числа реальных связей вершины
        self._edges = {} #словарь для хранения всех ребер типа Edge
        self._edgeMaxWeight = 0.0
        #self._verticles_active = {} #вершины для которых требуется делать пересчет значений
        #print 'term graph init'

    def add_vertex(self, vertex):
        """
        Добавить вершину в граф
        """
        self._verticles[vertex.term_value] = vertex

    def rem_vertex(self, term):
        print 'rem vertex'

    def add_edge(self, edge):
        """
        Добавить ребро в граф
        """
        v1 = edge.veStart
        v2 = edge.veFinish

        t1 = v1.term_value
        t2 = v2.term_value

#добавить термы, если их не было, создать связи
        if not t1 in self._verticlesJoins:
            arr = set([t2])
            self._verticlesJoins[t1] = arr
            self.add_vertex(v1)
            self._verticlesJoinsNum[t1] = 1
        else:
            self._verticlesJoins[t1].add(t2)
            self._verticlesJoinsNum[t1] += 1

        if not t2 in self._verticlesJoins:
            arr = set([t1])
            self._verticlesJoins[t2] = arr
            self.add_vertex(v2)
            self._verticlesJoinsNum[t2] = 1
        else:
            self._verticlesJoins[t2].add(t1)
            self._verticlesJoinsNum[t2] += 1


        #добавить ребро в граф
        hash = t1+t2 if t1 < t2 else t2 + t1
        if hash not in self._edges.keys():
            self._edges[hash] = edge
        else:
            self._edges[hash].addFreq(1)

    def get_edge_with_terms(self, t1, t2):
        edge = None
        hash = t1+t2 if t1 < t2 else t2 + t1

        edge = self._edges[hash]
        return edge

    def calc_undir_pr_for_term(self, term):
        """
        Пересчитать вес для вершины по алгоритму Page Rank без учета направления ребер [hassan page 2]
        """
        current_vert = self._verticles[term]
        linked_terms = self._verticlesJoins[term]
        linked_verts = []
        for t in linked_terms:
            vert = self._verticles[t]
            linked_verts.append(vert)

        d = 0.85
        c = 0.95
        n = self._verticles.__len__()

        result = (1-d)/n
        sum = 0.0
        for v in linked_verts:
            result_iter = 0.0
            curr_weight = v.term_weight_rw_old
            damping = d
            num_out_verts = self._verticlesJoins[v.term_value].__len__()
            result_iter = curr_weight * damping / num_out_verts
            sum += result_iter
        result += sum

        current_vert.term_weight_rw = result

    def calc_rw_for_term(self, term):
        """
        Пересчитать вес для вершины по алгоритму RW [hassan page 2]
        """
        current_vert = self._verticles[term]
        linked_terms = self._verticlesJoins[term]
        linked_verts = []
        for t in linked_terms:
            vert = self._verticles[t]
            linked_verts.append(vert)
        d = 0.85
        c = 0.95
        n = self._verticles.__len__()

        #experiment
        #verts = self._verticles.keys()
        #max_out = 0
        #for v in verts:
        #    tmp_val = self._verticlesJoins[v].__len__()
        #    max_out = max_out if max_out > tmp_val else tmp_val
        #n = max_out
        #experiment

        result = (1-d) / n
        sum = 0.0
        for v in linked_verts:
            curr_weight = v.term_weight_rw_old
            curr_edge = self.get_edge_with_terms(term, v.term_value)
            damping = float(curr_edge.weight) / self._edgeMaxWeight
            num_out_verts = self._verticlesJoins[v.term_value].__len__()
            result_iter = curr_weight * damping / num_out_verts
           # print v.term_value
           # print 'damping: ' + str(damping), 'num_out: ' + str(num_out_verts), 'curr_weight: ' + str(curr_weight)
            sum += result_iter
        result += sum * c #* d # * c

        #print '---' + term + str(current_vert.term_weight_tf) + '---'
        #print 'rw: ', sum

        current_vert.term_weight_rw = result

    def calc_rw_occur_for_term(self, term):
        """
        Пересчитать вес для вершины по алгоритму RW ,без нормировки ребер [hassan page 2]
        """
        current_vert = self._verticles[term]
        linked_terms = self._verticlesJoins[term]
        linked_verts = []
        for t in linked_terms:
            vert = self._verticles[t]
            linked_verts.append(vert)

        d = 0.85
        c = 0.95
        n = self._verticles.__len__()

        #experiment
        #verts = self._verticles.keys()
        #max_out = 0
        #for v in verts:
        #    tmp_val = self._verticlesJoins[v].__len__()
        #    max_out = max_out if max_out > tmp_val else tmp_val
        #n = max_out
        #experiment

        result = (1-d)/n
        sum = 0.0
        for v in linked_verts:
            curr_weight = v.term_weight_rw_old
            curr_edge = self.get_edge_with_terms(term, v.term_value)
            damping = curr_edge.freq
            num_out_verts = self._verticlesJoinsNum[v.term_value]#self._verticlesJoins[v.term_value].__len__()# #
            result_iter = curr_weight * damping / num_out_verts
            #print 'damping: ' + str(damping), 'num_out: ' + str(num_out_verts), 'curr_weight: ' + str(curr_weight)
            sum += result_iter
        result += sum * d #* c

        current_vert.term_weight_rw = result

        old_rw = current_vert.term_weight_rw_old
        div_rw = result - old_rw
        if div_rw <= self._precision:
            current_vert.is_active = False

    def recalc_vert_weights(self, mode='rw'):
        """
        Пересчитать веса для всех вершин по алгоритму RW
        """
        #Переприсвоить старым значениям, текущие новые
        verts = self._verticles.values()
        for v in verts:
            v.assign_rw_new_to_old()
        terms = self._verticles.keys()
        active_terms = []
        for term in self._verticles.keys():
            if self._verticles[term].is_active:
                active_terms.append(term)
        #print len(active_terms)
        if mode == 'rw':
            for term in terms:
                self.calc_rw_for_term(term)
        elif mode == 'rw_oc':
            for term in active_terms:
                self.calc_rw_occur_for_term(term)
        elif mode == 'pr':
            for term in terms:
                self.calc_undir_pr_for_term(term)

    def recalc_edges(self):
        edges = self._edges.values()

        for edge in edges:
            edge.calc_edge_weight()
            if edge.weight > self._edgeMaxWeight:
                self._edgeMaxWeight = edge.weight
            #print edge.weight

    def getTopVerts(self, mode='rw', num=100):
        sorted_verts = []
        verts = self._verticles.values()
        if mode == 'rw' or mode == 'rw_oc' or mode == 'pr':
            sorted_verts = sorted(verts, cmp=Vertex.compare_by_rw, reverse=True)
        elif mode == 'tf':
            sorted_verts = sorted(verts, cmp=Vertex.compare_by_tf, reverse=True)
        else:
            return sorted_verts
        sorted_verts = sorted_verts[:num]
        return sorted_verts
    #
    #@staticmethod
    #def intersect_graphs_terms(graphs):
    #    sort_grhs_verts = []
    #    for gr in graphs:
    #        sort_verts = sorted(gr._verticles.values(), cmp=Vertex.compare_by_rw, reverse=True)
    #        sort_verts = sort_verts[:30]
    #        sort_grhs_verts.append(sort_verts)
    #
    #    grhs_intersect = set()
    #    for verts in sort_grhs_verts[:1]:
    #        for vert in verts:
    #            grhs_intersect.add(vert.term_value)
    #
    #    print grhs_intersect
    #    for verts in sort_grhs_verts[1:]:
    #        gr_vert_set = set()
    #        for vert in verts:
    #            gr_vert_set.add(vert.term_value)
    #            grhs_intersect = grhs_intersect | gr_vert_set
    #
    #        print grhs_intersect
    #
    #    return grhs_intersect

    @staticmethod
    def compare_graphs_terms(gr_left, gr_right):
        #gr_left_terms = set(gr_left._verticles.keys())
        #gr_right_terms = set(gr_right._verticles.keys())
        #test
        sort_left = sorted(gr_left._verticles.values(), cmp=Vertex.compare_by_rw, reverse=True)
        sort_right = sorted(gr_right._verticles.values(), cmp=Vertex.compare_by_rw, reverse=True)
        len_left = len(sort_left)
        len_right = len(sort_right)
        min_len = min([len_left, len_right, 100])
        length = min_len
        gr_left_terms = set()
        gr_right_terms = set()
        #length = length if length < len(gr_right_terms) else len(gr_right_terms)
        for i in xrange(0, length):
            gr_left_terms.add(sort_left[i].term_value)
            gr_right_terms.add(sort_right[i].term_value)
        #
        union = gr_left_terms | gr_right_terms
        inter = gr_left_terms & gr_right_terms
        union_num = len(union)
        inter_num = len(inter)
        mesuare = float(inter_num) / union_num
        #print 'mesuare result: ', union_num, inter_num, mesuare
        return mesuare

    @staticmethod
    def compare_graphs_terms_with_weight(gr_left, gr_right):
        #gr_left_terms = set(gr_left._verticles.keys())
        #gr_right_terms = set(gr_right._verticles.keys())
        #test
        sort_left = sorted(gr_left._verticles.values(), cmp=Vertex.compare_by_rw, reverse=True)
        sort_right = sorted(gr_right._verticles.values(), cmp=Vertex.compare_by_rw, reverse=True)
        len_left = len(sort_left)
        len_right = len(sort_right)
        min_len = min([len_left, len_right, 100])
        length = min_len
        gr_left_terms = set()
        gr_right_terms = set()
        #length = length if length < len(gr_right_terms) else len(gr_right_terms)
        for i in xrange(0, length):
            gr_left_terms.add(sort_left[i].term_value)
            gr_right_terms.add(sort_right[i].term_value)
        #
        #union = gr_left_terms | gr_right_terms
        inter = gr_left_terms & gr_right_terms
        #union_num = len(union)
        #inter_num = len(inter)
        dev = 0.0
        #total_cat = 0.0
        total_r_cat = 0.0
        total_l_cat = 0.0
        inter_dim = len(inter)

        total_r_cat_sum = 0.0
        total_l_cat_sum = 0.0

        for v in gr_left._verticles.values():
            total_l_cat_sum += v.term_weight_rw
        for v in gr_right._verticles.values():
            total_r_cat_sum += v.term_weight_rw
        for term in inter:
            total_l_cat += gr_left._verticles[term].term_weight_rw
            total_r_cat += gr_right._verticles[term].term_weight_rw
        mesuare_l = total_l_cat / total_l_cat_sum
        mesuare_r = total_r_cat / total_r_cat_sum

        #print 'mesuare result: ', union_num, inter_num, mesuare
        res = 0.0
        #if mesuare_r > 0 and mesuare_l > 0:
        res = mesuare_r + mesuare_l
        return res

    @staticmethod
    def compare_graphs_edges(gr_left, gr_right):
        sort_left = sorted(gr_left._edges.values(), cmp=Edge.compare_by_freq, reverse=True)
        sort_right = sorted(gr_right._edges.values(), cmp=Edge.compare_by_freq, reverse=True)
        len_left = len(sort_left)
        len_right = len(sort_right)
        min_len = min([len_left, len_right, 100])
        length = min_len
        gr_left_edges = set()
        gr_right_edges = set()
        for i in xrange(0, length):
            gr_left_edges.add(sort_left[i].hash)
            gr_right_edges.add(sort_right[i].hash)

        union = gr_left_edges | gr_right_edges
        inter = gr_left_edges & gr_right_edges
        union_num = len(union)
        inter_num = len(inter)
        mesuare = float(inter_num) / union_num
        return mesuare
