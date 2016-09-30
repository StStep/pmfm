from collections import namedtuple
import random, copy

NEIGH_NUM = 4

class Element:
    """The base element class"""

    def __init__(self):
        self.cache = [0] * NEIGH_NUM
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
        update = False
        # Get Neigbor to process
        (i, neig) = self.ChooseNeighbor(neighbors)
        # Update cache and fork to empty
        if isinstance(neig, Empty):
            neighbors[i] = copy.deepcopy(self)
            if(self.dist != 0):
                neighbors[i].dist = self.dist + 1
            update = True
            self.cache[i] = neighbors[i].dist
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
