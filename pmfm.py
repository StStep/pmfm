from collections import namedtuple
import random, copy

NEIGH_NUM = 4

class Element:
    """The base element class"""

    def __init__(self):
        self.cache = [None] * NEIGH_NUM
        self.last_neigh = random.randint(0, NEIGH_NUM - 1)

    def  ProcAtomicDir(self, neighbors):
        raise NotImplementedError("Please Implement this method")

    def ChooseNeighbor(self, neighbors):
        """Deterministic choice of  one of the neighbors to process"""
        self.last_neigh = (self.last_neigh + 1) % NEIGH_NUM
        return (self.last_neigh, neighbors[self.last_neigh])

class Barrier(Element):
    """An element that acts the boundry for organs and organisms"""

    def __init__(self):
        Element.__init__(self)
        self.accepted_data_ids = []

    def ProcAtomicDir(self, neighbors):
        update = True
        # Get Neigbor to process
        (i, neig) = self.ChooseNeighbor(neighbors)
        # Update cache
        self.cache[i] = neig.__class__.__name__
        # Only affect data objects
        if isinstance(neig, Data):
            # TODO Concept of Inside and Outside
            update = False
        else:
            update = False
        return update


class Medium(Element):
    """An element that acts as a transportation medium for other elements"""

    def __init__(self):
        Element.__init__(self)
        self.absorbed_data_ids = []
        self.accepted_dist = []
        self.dist = 0

    def ProcAtomicDir(self, neighbors):
        update = True
        # Get Neigbor to process
        (i, neig) = self.ChooseNeighbor(neighbors)
        # Update cache
        self.cache[i] = neig.__class__.__name__
        # Fork to empty
        if isinstance(neig, Empty):
            neighbors[i] = copy.deepcopy(self)
            if(self.dist != 0):
                neighbors[i].dist = self.dist + 1
        elif isinstance(neig, Medium):
            if(neig.dist == 0):
                pass
            elif(self.dist == 0):
                self.dist = neig.dist + 1
            else:
                self.dist = neig.dist + 1 if ((neig.dist + 1) < self.dist) else self.dist
        elif isinstance(neig, Barrier):
            self.dist = 1
        else:
            update = False
        return update

class PassiveElement(Element):
    """A passive element, does nothing """

    def ProcAtomicDir(self, neighbors):
        return False

class Data(PassiveElement):
    """A passive element that holds data"""

    def __init__(self, ID):
        PassiveElement.__init__(self)
        self.ID = ID

class Empty(PassiveElement):
    """A passive element that represents an empty location"""
    pass

class Dead(PassiveElement):
    """A passive element that represents an dead, unusable location"""
    pass

if __name__ == "__main__":
    import sys
    print(str(sys.argv))

    fish = Element()
    print(str(fish.cache))
