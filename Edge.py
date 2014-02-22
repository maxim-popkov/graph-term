#-*- coding: utf-8 -*-
from Vertex import Vertex

__author__ = 'dales3d'


class Edge(object):
    def __init__(self, v1, v2):
        #print 'edge init: ' + str(v1.term_value) + '-' + str(v2.term_value)
        self._veStart = v1
        self._veFin = v2
        self._weight = 0.0
        self._weightOld = 0.0
        self._freq = 1;

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, value):
        self._weightOld = self._weight
        self._weight = value

    @property
    def veStart(self):
        return self._veStart

    @property
    def veFinish(self):
        return self._veFin

    @property
    def freq(self):
        return self._freq

    @freq.setter
    def freq(self, value):
        self._freq = value

    @property
    def hash(self):
        t1 = self._veStart.term_value
        t2 = self._veFin.term_value
        return t1+t2 if t1 < t2 else t2 + t1

    def addFreq(self, value):
        self._freq += value

    def calc_edge_weight(self):
        self.weight = self._veStart.term_weight_tf * self._veFin.term_weight_tf

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        result = '\n Edge:[\n    v1: ' + self._veStart.__str__() + '\n    v2: ' + self._veFin.__str__() + ']'
        return result

    @staticmethod
    def compare_by_freq(e_left, e_right):
        #print v_left.term_weight_rw, v_right.term_weight_rw
        if e_left._freq > e_right._freq:
            return 1
        elif e_left._freq < e_right._freq:
            return -1
        return 0