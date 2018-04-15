import xml.etree.ElementTree
from Node import Node

e = xml.etree.ElementTree.parse('config').getroot()
BG_COLOR = e.find('bgColor').text
LINE_PAD_X = float(e.find('linePadx').text)
LINE_START_POINT_FOR_NODES = float(e.find('lineStartPointForNodes').text)
LINE_END_POINT_FOR_NODES = float(e.find('lineEndPointForNodes').text)
LINE_COLOR = e.find('lineColor').text
WIDTH = float(e.find('canvasWidth').text)
AMOUNT_OF_TIME_IN_ROW = int(e.find('amountOfTimeInRow').text)
AMOUNT_OF_NODE_IN_TIME = int(e.find('amountOfNodeInTime').text)
NODE_WORK_RADIUS = float(e.find('nodeWorkRadius').text)


class Line:
    """class that represent collection of nodes"""
    def __init__(self, y, numberOfLine, numberOfRow, scanvas, transparent):
        """
        @:param y - y coordinate of horizontal line
        @:param transparent - if it's True line has background color
        @:param canvas - represent canvas where Line is drawing
        """
        self.y = y
        self.transparent = transparent
        self.numberOfLine = numberOfLine
        self.numberOfRow = numberOfRow
        self.scanvas = scanvas
        self.line = None
        """
         creation of nodes, 32 because it can be 32 thirty-second notes in one time
         (I'm not sure is there any purpose to add: sixty-fourth, hundred twenty-eighth, two hundred fifty-sixth notes,
         because nobody use them, at least I have never seen them except https://en.wikipedia.org/wiki/Note_value)
         """
        self.nodes = [Node(LINE_PAD_X + LINE_START_POINT_FOR_NODES +
                           i * ((WIDTH - LINE_PAD_X - LINE_START_POINT_FOR_NODES - LINE_END_POINT_FOR_NODES) / (AMOUNT_OF_TIME_IN_ROW * AMOUNT_OF_NODE_IN_TIME)),
                           self.y, i, self.numberOfLine, numberOfRow, self.scanvas) for i in range(AMOUNT_OF_TIME_IN_ROW * AMOUNT_OF_NODE_IN_TIME)]

    def draw(self):
        """draw line"""
        if self.transparent is False:
            self.line = self.scanvas.canvas.create_line(LINE_PAD_X, self.y, WIDTH - LINE_PAD_X, self.y, fill=LINE_COLOR)

    def hide(self):
        """hide Line and hide Nodes"""
        self.scanvas.canvas.delete(self.line)
        self.transparent = True
        [node.hide() for node in self.nodes]

    def isCollision(self, eveX, eveY):
        """
        return list with [index of Line, index of Node] that was clicked on
        return None if click was far
        """
        if self.y-NODE_WORK_RADIUS <= eveY <= self.y+NODE_WORK_RADIUS:  # check if click was near line
            for node in self.nodes:
                if node.isCollision(eveX, eveY):
                    return [self.numberOfLine, node.numberInLine]
