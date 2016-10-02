from collections import namedtuple
import random, copy

NEIGH_NUM = 4
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)
NeighIndex = enum('CENTER', 'UP', 'RIGHT', 'DOWN', 'LEFT')

class Element:
    """The base element class"""

    def __init__(self):
        self.cache = [0] * (NEIGH_NUM + 1)
        self.last_neigh = random.randint(1, NEIGH_NUM)

    def  ProcAtomicDir(_self, neighborHood):
        raise NotImplementedError("Please Implement this method")

    def ChooseNeighbor(self, neighborHood):
        """Deterministic choice of  one of the neighbors to process"""
        self.last_neigh = self.last_neigh + 1
        if self.last_neigh > NEIGH_NUM:
            self.last_neigh = 1
        return (self.last_neigh, neighborHood[self.last_neigh])

class Barrier(Element):
    """An element that acts the boundry for organs and organisms"""

    def __init__(self):
        Element.__init__(self)
        self.accepted_data_ids = []

    def ProcAtomicDir(_self, neighborHood):
        self = neighborHood[NeighIndex.CENTER]
        # Get Neigbor to process
        (i, neig) = self.ChooseNeighbor(neighborHood)
        # Update cache
        self.cache[i] = neig.__class__.__name__
        # Only affect data objects
        if isinstance(neig, Data):
            # TODO Concept of Inside and Outside
            pass
        else:
            pass

class Medium(Element):
    """An element that acts as a transportation medium for other elements"""

    def __init__(self):
        Element.__init__(self)
        self.absorbed_data_ids = []
        self.accepted_dist = []
        self.dist = 0
        self.moving_data = False
        self.mv_src = 0
        self.mv_dest = 0

    def ProcAtomicDir(_self, neighborHood):
        self = neighborHood[NeighIndex.CENTER]
        # Get Neigbor to process
        (i, neig) = self.ChooseNeighbor(neighborHood)
        # Update cache and fork to empty
        if isinstance(neig, Empty):
            neighborHood[i] = copy.deepcopy(self)
            if(self.dist != 0):
                neighborHood[i].dist = self.dist + 1
            self.cache[i] = neighborHood[i].dist
        elif isinstance(neig, Medium):
            self.cache[i] = neig.dist
        elif isinstance(neig, Barrier):
            self.cache[i] = -1
        else:
            self.cache[i] = 0

        min = 0
        for x in self.cache:
            if(x == 0):
                pass
            elif(x == -1):
                min = -1
            elif(min == 0):
                min = x
            elif(x < min):
                min = x
            else:
                pass

        if(min == 0):
            self.dist = 0;
        elif(min == -1):
            self.dist = 1
        else:
            self.dist = min + 1

class PassiveElement(Element):
    """A passive element, does nothing """

    def ProcAtomicDir(_self, neighborHood):
        pass;

class Data(PassiveElement):
    """A passive element that holds data"""

    def __init__(self, ID):
        PassiveElement.__init__(self)
        self.ID = ID
        self.lock = False

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
