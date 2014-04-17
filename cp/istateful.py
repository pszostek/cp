#!/usr/bin/env python

class IStateful(object):
    def getState(self):
        raise NotImplementedError()

    def setState(self, state):
        raise NotImplementedError()