#-*- coding: utf-8 -*-
__author__ = 'dales3d'


class Vertex(object):

    def __init__(self, term = 'none', weightTF = 0.0, weightRW = 0.25):
        #print 'init Vertex: ' + term
        self._active = True
        self._termValue = term
        self._termWeightTF = weightTF
        self._termWeightOldTF = weightTF
        self._termWeightRW = weightRW
        self._termWeightOldRW = weightRW

        #self._termWeightOldRW = weightTF
        #self._termWeightRW = weightTF

    @property
    def term_value(self):
        return self._termValue

    @term_value.setter
    def term_value(self, value):
        self._termValue = value

    @property
    def is_active(self):
        return self._active

    @is_active.setter
    def is_active(self, value):
        self._active = value

    @property
    def term_weight_rw(self):
        return self._termWeightRW

    @term_weight_rw.setter
    def term_weight_rw(self, value):
        self._termWeightOldRW = self._termWeightRW
        self._termWeightRW = value

    @property
    def term_weight_rw_old(self):
        return self._termWeightOldRW

    @property
    def term_weight_tf(self):
        return self._termWeightTF

    @term_weight_tf.setter
    def term_weight_tf(self, value):
        self._termWeightOldTF = self._termWeightTF
        self._termWeightTF = value

    def assign_rw_new_to_old(self):
        self._termWeightOldRW = self._termWeightRW

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        result = '\n Term Value:[' + self._termValue + ']'
        return result

    @staticmethod
    def compare_by_rw(v_left, v_right):
        #print v_left.term_weight_rw, v_right.term_weight_rw
        if v_left.term_weight_rw > v_right.term_weight_rw:
            return 1
        elif v_left.term_weight_rw < v_right.term_weight_rw:
            return -1
        return 0

    @staticmethod
    def compare_by_tf(v_left, v_right):
        #print v_left.term_weight_rw, v_right.term_weight_rw
        if v_left.term_weight_tf > v_right.term_weight_tf:
            return 1
        elif v_left.term_weight_tf < v_right.term_weight_tf:
            return -1
        return 0