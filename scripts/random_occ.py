from numpy.random import choice
import numpy as np
class randomOccGenerator(object):
    def __init__(self):
        self.occs = open('occs.txt').read().splitlines()
        self.probs = np.array(open('occp.txt').read().splitlines()).astype(float)
        self.probs = self.probs/np.sum(self.probs)

    def occ(self):
        out= choice(self.occs,p=self.probs)
        return out
