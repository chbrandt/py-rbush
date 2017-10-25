# from collections import defaultdict
# _node = defaultdict(None)
#
# Box = ["xmin","xmax","ymin","ymax"]
# Point = ["X","Y"]
#
# def createBox(item):
#     box = _node
#     for l in Box:
#         box[l] = item[l]
#     return box
#
# def pointBox(item):
#     bbox = _node
#     for l in Box:
#         c = "X" if "X" in l else "Y"
#         bbox[l] = item[c]
#     return bbox

import math
from collections import namedtuple

from .quickselect import quickselect

import sys
INF = sys.maxsize
# _node = dict(
#     xmin = INF,
#     ymin = INF,
#     xmax = -INF,
#     ymax = -INF,
#     leaf = True,
#     height = 1,
#     # data = None,
#     children = None
# )



class RBushBoxClass(object):

    def __init__(self,xmin, ymin, xmax, ymax):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

RBushBoxTuple = namedtuple('RBushTuple', ['xmin', 'ymin', 'xmax', 'ymax'])


class RBushNodeClass(object):

    def __init__(self,xmin,ymin,xmax,ymax,leaf,height,children):
        self.xmin = INF
        self.ymin = INF
        self.xmax = -INF
        self.ymax = -INF
        self.leaf = True
        self.height = 1
        self.children = children

RBushNodeTuple = namedtuple('RBushTuple', ['xmin', 'ymin', 'xmax', 'ymax',
                                            'leaf', 'height', 'children'])

RBushNode = RBushNodeClass
RBushBox = RBushBoxClass

RBushItem = RBushBox

def createNode(children=None):
    '''
    Create a node (leaf,parent or bbox)
    '''
    children = children or []
    children_ = children
    # children_ = []
    # for child in children:
    #     if isinstance(child,dict):
    #         if hasattr(child,'leaf'):
    #             children_.append(nodeFromDict(child))
    #         else:
    #             children_.append(itemFromDict(child))
    return RBushNode(INF, INF, -INF, -INF, True, 1, children_)

def toBBoxNode(item):
    '''
    Simply return 'item'
    '''
    if isinstance(item,dict):
        item = itemFromDict(item)
    return RBushBox(item.xmin, item.ymin, item.xmax, item.ymax)

def itemFromDict(item):
    if not isinstance(item,dict):
        assert isinstance(item,RBushItem)
        return item
    return RBushItem(item['xmin'],item['ymin'],item['xmax'],item['ymax'])

def boxFromDict(item):
    if not isinstance(item,dict):
        assert isinstance(item,RBushBox)
        return item
    return RBushBox(item['xmin'],item['ymin'],item['xmax'],item['ymax'])

def nodeFromDict(item):
    if not isinstance(item,dict):
        assert isinstance(item,RBushNode)
        return item
    node = RBushNode(item['xmin'],item['ymin'],item['xmax'],item['ymax'])
    node.leaf = item.leaf
    node.children = item.children
    node.height = item.height
    return node

# Javascript arrays have a 'splice' method,
#  this is the equivalent for Python lists
def splice(list_,insert_position,remove_how_many,*items_to_insert):
    removed_items = []
    for i in range(remove_how_many):
        removed_items.append( list_.pop(insert_position) )
    for item in items_to_insert[::-1]:
        list_.insert(insert_position, item)
    return removed_items

def findItem(item, items, equalsFn=None):
    if not equalsFn:
        return items.index(item) if item in items else None
    for i in range(0, len(items)):
        if equalsFn(item, items[i]):
            return i
    return None

def extend(a, b):
    """Return 'a' box enlarged by 'b'"""
    a.xmin = min(a.xmin, b.xmin)
    a.ymin = min(a.ymin, b.ymin)
    a.xmax = max(a.xmax, b.xmax)
    a.ymax = max(a.ymax, b.ymax)
    return a

# function compareNodexmin(a, b) { return a.xmin - b.xmin; }
def compareNodexmin(a):
    return a.xmin# - b.xmin

# function compareNodeymin(a, b) { return a.ymin - b.ymin; }
def compareNodeymin(a):
    return a.ymin# - b.ymin

# function bboxArea(a)   { return (a.xmax - a.xmin) * (a.ymax - a.ymin); }
def bboxArea(a):
    return (a.xmax - a.xmin) * (a.ymax - a.ymin)

# function bboxMargin(a) { return (a.xmax - a.xmin) + (a.ymax - a.ymin); }
def bboxMargin(a):
    return (a.xmax - a.xmin) + (a.ymax - a.ymin)


def enlargedArea(a, b):
    sect1 = max(b.xmax, a.xmax) - min(b.xmin, a.xmin)
    sect2 = max(b.ymax, a.ymax) - min(b.ymin, a.ymin)
    return sect1 * sect2

def intersectionArea(a,b):
    xmin = max(a.xmin, b.xmin)
    ymin = max(a.ymin, b.ymin)
    xmax = min(a.xmax, b.ymax)
    ymax = min(a.ymax, b.ymax)
    return max(0, xmax - xmin) * max(0, ymax - ymin)

def contains(a,b):
    a_lower_b = a.xmin <= b.xmin and a.ymin <= b.ymin
    a_upper_b = b.xmax <= a.xmax and b.ymax <= a.ymax
    return a_lower_b and a_upper_b


def intersects(a,b):
    b_lower_a = b.xmin <= a.xmax and b.ymin <= a.ymax
    b_upper_a = b.xmax >= a.xmin and b.ymax >= a.ymin
    return b_lower_a and b_upper_a


def multiSelect(items, left, right, n, compare):
    stack = [left, right]
    mid = None
    #FIXME: I don't like the object being checked (i.e, 'stack') being
    #       modified inside of the loop...probably change that.
    while len(stack):
        right = stack.pop()
        left = stack.pop()
        if (right - left) <= n:
            continue
        mid = left + math.ceil((right - left) / n / 2) * n
        quickselect(items, mid, left, right, compare)
        stack.extend([left, mid, mid, right])


def chooseSubtree(bbox, node, level, path):
    '''
    Return the node closer to 'bbox'

    Traverse the subtree searching for the tightest path,
    the node at the end, closest to bbox is returned
    '''
    while True:

        path.append(node)

        if node.leaf or (len(path)-1 == level):
            break

        minEnlargement = INF
        minArea = INF

        targetNode = None
        len_ = len(node.children)
        for i in range(0, len_):
            child = node.children[i]
            area = bboxArea(child)
            enlargement = enlargedArea(bbox, child) - area

            ## choose entry with the least area enlargement
            if (enlargement < minEnlargement):
                minEnlargement = enlargement
                minArea = area if area < minArea else minArea
                targetNode = child
            else:
                if (enlargement == minEnlargement):
                    ## otherwise choose one with the smallest area
                    if (area < minArea):
                        minArea = area
                        targetNode = child

        node = targetNode or node.children[0]

    #NOTE: 'node' is returned, 'path' was modified (i.e, filled)
    return node


def adjustParentBBoxes(bbox, path, level):
    ## adjust bboxes along the given tree path
    for i in range(level, -1, -1):
        extend(path[i],bbox);




class Rbush(object):
    _defaultMaxEntries = 9
    def __init__(self,maxEntries=None,format=None):
        ## max entries in a node is 9 by default; min node fill is 40% for best performance
        self._maxEntries = max(4, maxEntries or self._defaultMaxEntries);
        self._minEntries = max(2, math.ceil(self._maxEntries * 0.4));

        self._initFormat(format);

        self._createRoot()


    def __eq__(self,other):
        return self.toJSON() == other.toJSON()

    def __str__(self):
        return self.toJSON()

    def copy(self):
        new = Rbush(self._maxEntries,self._format)
        new.fromJSON(self.toJSON())
        assert new == self
        return new


    def _createRoot(self,item=None):
        _children = [item] if item else []
        root = createNode(children=_children)
        root.height = 1
        root.leaf = True
        self.calcBBox(root);
        self.data = root


    def insert(self,item=None,xmin=None,ymin=None,xmax=None,ymax=None):
        '''Insert an item'''
        if xmin is not None \
            and ymin is not None \
            and xmax is not None \
            and ymax is not None:
            try:
                liX = len(xmin)
                liY = len(ymin)
                laX = len(xmax)
                laY = len(ymax)
            except TypeError as e:
                # not iterable
                xmin = [xmin]
                ymin = [ymin]
                xmax = [xmax]
                ymax = [ymax]
            if not len(xmin)==len(ymin)==len(xmax)==len(ymax):
                print("Error: Arguments 'xmin','ymin','xmax','ymax' have different lenghts")
                return self
            items = []
            for i in range(len(xmin)):
                items.append( RBushItem(xmin[i],ymin[i],xmax[i],ymax[i]) )
            self.load(items)

        if item:
            item = itemFromDict(item)
            # if self.data.children:
            self._insert(item, self.data.height - 1)
            # else:
            #     self._createRoot(item)

        return self


    def _insert(self, item, level, isNode=False):
        #
        root = self.data
        bbox = self.toBBox(item) if not isNode else item

        insertPath = []

        ## find the best node for accommodating the item, saving all nodes along the path too
        node = chooseSubtree(bbox, root, level, insertPath)

        ## put the item into the node
        node.children.append(item)
        # node.children.append(bbox)
        extend(node,bbox)

        ## split on node overflow; propagate upwards if necessary
        while level >= 0:
            if len(insertPath[level].children) > self._maxEntries:
                self._split(insertPath, level)
                level=level-1
            else:
                break

        ## adjust bboxes along the insertion path
        adjustParentBBoxes(bbox, insertPath, level)

    ## split overflowed node into two
    def _split(self, insertPath, level):

        m = self._minEntries
        node = insertPath[level]
        M = len(node.children)

        self.chooseSplitAxis(node, m)

        splitIndex = self.chooseSplitIndex(node, m)
        # If an optimal index was not found, split at the minEntries
        splitIndex = splitIndex or m

        numChildren = len(node.children) - splitIndex
        adopted = splice(node.children, splitIndex, numChildren)
        newNode = createNode( children=adopted )
        newNode.height = node.height
        newNode.leaf = node.leaf
        # assert not node.leaf, "a leaf should not have children!"

        # Update the sizes (limits) of each box
        self.calcBBox(node)
        self.calcBBox(newNode)

        if level:
            insertPath[level-1].children.append(newNode)
        else:
            self._splitRoot(node, newNode)


    def chooseSplitAxis(self, node, minEntries):
        '''
        Sort node's children by the best axis for split

        The best axis is defined based on a estimate of
        "density", the more compact axis goes split.
        '''
        M = len(node.children)
        # m = self._minEntries
        # comparexmin = compareNodexmin
        # compareymin = compareNodeymin
        xMargin = self.allDistMargin(node, self.comparexmin, minEntries)
        yMargin = self.allDistMargin(node, self.compareymin, minEntries)

        ## if total distributions margin value is minimal for x, sort by xmin,
        ## otherwise it's already sorted by ymin
        if (xMargin < yMargin):
            node.children.sort(key=self.comparexmin)

    ## total margin of all possible split distributions where each node is at least m full
    def allDistMargin(self, node, compare, minEntries):
        '''
        Return the "size of all combinations of bounding-box to split
        '''
        M = len(node.children)
        m = minEntries

        # The sorting of (children) nodes according to an axis,
        # "compare-X/Y", guides the search for where to split
        node.children.sort(key=compare)

        leftBBox = self.distBBox(node, 0, m)
        rightBBox = self.distBBox(node, M - m, M)
        margin = bboxMargin(leftBBox) + bboxMargin(rightBBox)

        for i in range(m, M - m):
            child = node.children[i];
            extend(leftBBox, child);
            margin = margin + bboxMargin(leftBBox);

        for i in range(M-m-1, m-1, -1):
            child = node.children[i];
            extend(rightBBox, child);
            margin = margin + bboxMargin(rightBBox);

        return margin;

    def chooseSplitIndex(self, node, minEntries):
        '''
        Return the index (children) where to split

        Split position tries to minimize (primarily) the boxes overlap
        and, secondly, the area cover by each combination of boxes.
        '''
        M = len(node.children)
        m = minEntries

        minArea = INF
        minOverlap = INF

        index = None
        for i in range(m, M - m + 1):
            bbox1 = self.distBBox(node, 0, i);
            bbox2 = self.distBBox(node, i, M);

            overlap = intersectionArea(bbox1, bbox2);
            area = bboxArea(bbox1) + bboxArea(bbox2);

            ## choose distribution with minimum overlap
            if (overlap < minOverlap):
                minOverlap = overlap;
                index = i;
                minArea = area if area < minArea else minArea;

            else:
                if (overlap == minOverlap):
                    ## otherwise choose distribution with minimum area
                    if (area < minArea):
                        minArea = area
                        index = i

        return index;


    def _splitRoot(self, node, newNode):
        ## split root node
        newRoot = createNode([node, newNode])
        newRoot.height = node.height + 1
        newRoot.leaf = False
        self.calcBBox(newRoot);
        self.data = newRoot


    def clear(self):
        self.data = createNode()


    def all(self):
        return self._all(self.data, [])


    def _all(self, node, result):
        nodesToSearch = []
        while node:
            if node.leaf:
                # result.push.apply(result, node.children);
                result.extend(node.children)
                # result.append(node['data'])
            else:
                nodesToSearch.extend(node.children)
            node = nodesToSearch.pop() if len(nodesToSearch) else None

        return result


    def search(self,bbox):
        node = self.data
        result = []

        if isinstance(bbox,dict):
            bbox = boxFromDict(bbox)

        if not intersects(bbox, node):
            return result

        nodesToSearch = []
        while node:
            len_ = len(node.children)
            for i in range(0,len_):
                child = node.children[i]
                childBBox = self.toBBox(child) if node.leaf else child
                if intersects(bbox, childBBox):
                    if node.leaf:
                        result.append(child)
                    elif contains(bbox, childBBox):
                        self._all(child, result)
                    else:
                        nodesToSearch.append(child)
            node = nodesToSearch.pop() if len(nodesToSearch) else None

        return result


    def collides(self,bbox):
        node = self.data

        if isinstance(bbox,dict):
            bbox = boxFromDict(bbox)

        if not intersects(bbox, node):
            return False

        nodesToSearch = []
        while node:
            len_ = len(node.children)
            for i in range(0,len_):
                child = node.children[i]
                childBBox = self.toBBox(child) if node.leaf else child
                if intersects(bbox, childBBox):
                    if node.leaf or contains(bbox, childBBox):
                        return True;
                    nodesToSearch.append(child)
            node = nodesToSearch.pop() if len(nodesToSearch) else None

        return False

    def load(self,data):
        if not (data and len(data)):
            return self
        len_ = len(data)
        if (len_ < self._minEntries):
            for i in range(0,len_):
                self.insert(data[i])
            return self

        ## recursively build the tree with the given data from scratch using OMT algorithm
        node = self._build(data[:], 0, len(data) - 1, 0)

        if not len(self.data.children):
            ## save as is if tree is empty
            self.data = node
        elif (self.data.height == node.height):
            ## split root if trees have the same height
            self._splitRoot(self.data, node)
        else:
            if (self.data.height < node.height):
                ## swap trees if inserted one is bigger
                tmpNode = self.data
                self.data = node
                node = tmpNode
            ## insert the small tree into the large tree at appropriate level
            self._insert(node, self.data.height - node.height - 1, True)
        return self


    def remove(self, item, equalsFn=None):
        if not item:
            return self

        node = self.data
        bbox = self.toBBox(item)
        path = []
        indexes = []
        goingUp = False
        parent = None
        i = None

        ## depth-first iterative tree traversal
        while node or len(path):

            if not node: ## go up
                node = path.pop()
                parent = path[len(path) - 1] if len(path) else None
                i = indexes.pop() if len(indexes) else None
                goingUp = True

            if node.leaf: ## check current node
                index = findItem(item, node.children, equalsFn)
                if index is not None:
                    ## item found, remove the item and condense tree upwards
                    # node.children.splice(index, 1)
                    splice(node.children, index, 1)
                    path.append(node)
                    self._condense(path)
                    return self

            if not goingUp and not node.leaf and contains(node, bbox): ## go down
                path.append(node)
                if i is not None:
                    indexes.append(i)
                i = 0
                parent = node
                node = node.children[0]

            elif parent: ## go right
                i=i+1
                # if len(parent.children)<i:
                try:
                    node = parent.children[i]
                except IndexError as e:
                    node = None
                # else:
                #     node = None
                goingUp = False

            else:
                node = None ## nothing found
        return self


    def toBBox(self,item):
        return toBBoxNode(item)

    def calcBBox(self,node):
        """Update node sizes after its children"""
        return self.distBBox(node, 0, len(node.children), node);


    def distBBox(self, node, left_child, right_child, destNode=None):
        """Return a node enlarged by all children between left/right"""
        destNode = createNode() if destNode is None else destNode
        for i in range(left_child,right_child):
            child = node.children[i]
            extend(destNode, self.toBBox(child) if node.leaf else child)
        return destNode

    def comparexmin(self,a):
        return compareNodexmin(a)

    def compareymin(self,a):
        return compareNodeymin(a)

    def nodeToJSON(self,node):
        # content = { k:str(v) for k,v in vars(node).items() }
        content = vars(node).copy()
        try:
            children = []
            for child in node.children:
                children.append( self.nodeToJSON(child) )
            content['children'] = children
        except:
            pass
        return content

    def toDict(self):
        return self.nodeToJSON(self.data)

    def toJSON(self):
        import json
        return json.dumps(self.toDict())

    def nodeFromJSON(self,dict):
        # content = { k:str(v) for k,v in vars(node).items() }
        item = RBushItem(dict.pop('xmin'),
                            dict.pop('ymin'),
                            dict.pop('xmax'),
                            dict.pop('ymax'))
        try:
            children = []
            for child in dict['children']:
                children.append( self.nodeFromJSON(child) )
            node = RBushNode()
            node.xmin = item.xmin
            node.ymin = item.ymin
            node.xmax = item.xmax
            node.ymax = item.ymax
            node.leaf = dict['leaf']
            node.height = dict['height']
            node.children = children
        except:
            node = item
        return node

    def fromDict(self,dict):
        return self.nodeFromJSON(dict)
        
    def fromJSON(self,data):
        import json
        self.data = self.fromDict(json.loads(data))

    def _build(self, items, left, right, height):
        N = right - left + 1
        M = self._maxEntries
        node = None

        if N <= M:
            ## reached leaf level; return leaf
            node = createNode(items[left : right + 1])
            self.calcBBox(node)
            return node

        if not height:
            ## target height of the bulk-loaded tree
            height = math.ceil(math.log(N) / math.log(M))

            ## target number of root entries to maximize storage utilization
            M = math.ceil(N / math.pow(M, height - 1))

        node = createNode([])
        node.leaf = False
        node.height = height

        ## split the items into M mostly square tiles
        N2 = math.ceil(N / M)
        N1 = N2 * math.ceil(math.sqrt(M))

        multiSelect(items, left, right, N1, self.comparexmin)

        for i in range(left, right+1, N1):
            right2 = min(i + N1 - 1, right)
            multiSelect(items, i, right2, N2, self.compareymin)
            for j in range(i, right2+1, N2):
                right3 = min(j + N2 - 1, right2)
                ## pack each entry recursively
                node.children.append(self._build(items, j, right3, height - 1))
        self.calcBBox(node)

        return node


    def _condense(self,path):
        ## go through the path, removing empty nodes and updating bboxes
        siblings = None
        for i in range(len(path)-1, -1, -1):
            if len(path[i].children) == 0:
                if (i > 0):
                    siblings = path[i - 1].children;
                    splice(siblings, siblings.index(path[i]), 1);
                else:
                    self.clear();
            else:
                self.calcBBox(path[i]);


    def _initFormat(self,format_):
        ## data format (xmin, ymin, xmax, ymax accessors)
        self._format = format_
        if not format_:
            return None

        self.comparexmin = lambda a: a[format_[0]]
        self.compareymin = lambda a: a[format_[1]]

        self.toBBox = lambda a: RBushBox(a[format_[0]],a[format_[1]],
                                         a[format_[2]],a[format_[3]])
