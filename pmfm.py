from collections import namedtuple
import random, copy

NEIGH_NUM = 4
class NeighIndex:
    CENTER = 0
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4

########################################################################
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

########################################################################
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

#----------------------------------------------------------------------
def GetCacheMin(cache):
    '''
    Return of (0, 0): There is nothing nearby
    Return of (-1, ind): Next to barrier, barrier index given
    Else (min, ind): Given index is to min neighbor
    '''
    min, ind = 0, 0
    for i, x in enumerate(cache):
        if(x == 0): # entry has nothing
            pass
        elif(x == -1): # entry is barrier
            min = -1
            ind = i
        elif(min == 0): # entry has something, self has nothing
            min = x
            ind = i
        elif(x < min): # entry and self have something
            min = x
            ind = i
        else: # entry is larger
            pass
    return (min, ind)


########################################################################
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

    def UpdateCache(_self, neighborHood):
        self = neighborHood[NeighIndex.CENTER]
        # Get Neigbor to process
        (i, neig) = self.ChooseNeighbor(neighborHood)
        # Fork to empty
        if isinstance(neig, Empty):
            neighborHood[i] = copy.deepcopy(self)
            if(self.dist != 0):
                neighborHood[i].dist = self.dist + 1
            self.cache[i] = neighborHood[i].dist
        elif isinstance(neig, Medium):
            self.cache[i] = neig.dist
        elif isinstance(neig, Data):
            self.cache[i] = 0
            if(neig.lock == 0):
                neig.lock = 2
                self.mv_src = i
                self.moving_data = True
                min, ind = GetCacheMin(self.cache)
                if(min <=  0):
                    self.mv_dest = 0;
                else:
                    self.mv_dest = ind
            else:
                neig.lock = neig.lock - 1
        elif isinstance(neig, Barrier):
            self.cache[i] = -1
        else:
            self.cache[i] = 0

        min, ind = GetCacheMin(self.cache)
        if(min == 0):
            self.dist = 0;
        elif(min == -1):
            self.dist = 1
        else:
            self.dist = min + 1

    def MoveData(_self, neighborHood):
        self = neighborHood[NeighIndex.CENTER]
        self.moving_data = False
        neighborHood[self.mv_src].lock = 0
        # Abort if dest is data or barrier
        if (isinstance(neighborHood[self.mv_dest], Data) or
            isinstance(neighborHood[self.mv_dest], Barrier)):
            return

        # Move dest to source, copy self into source
        neighborHood[self.mv_dest] = copy.deepcopy(neighborHood[self.mv_src])
        neighborHood[self.mv_src] = copy.deepcopy(self)
        if(self.dist != 0):
            neighborHood[self.mv_src].dist = self.dist + 1

    def ProcAtomicDir(_self, neighborHood):
        if(_self.moving_data):
            _self.MoveData(neighborHood)
        else:
            _self.UpdateCache(neighborHood)

########################################################################
class PassiveElement(Element):
    """A passive element, does nothing """

    def ProcAtomicDir(_self, neighborHood):
        pass;

########################################################################
class Data(PassiveElement):
    """A passive element that holds data"""

    def __init__(self, ID):
        PassiveElement.__init__(self)
        self.ID = ID
        self.lock = 0

########################################################################
class Empty(PassiveElement):
    """A passive element that represents an empty location"""
    pass

########################################################################
class Dead(PassiveElement):
    """A passive element that represents an dead, unusable location"""
    pass

#----------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    print(str(sys.argv))

    fish = Element()
    print(str(fish.cache))
