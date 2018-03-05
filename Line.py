import xml.etree.ElementTree
from Node import Node

e = xml.etree.ElementTree.parse('config').getroot()
BG_COLOR = e.find('bgColor').text
LINE_PAD_X = float(e.find('linePadx').text)
LINE_COLOR = e.find('lineColor').text
WIDTH = float(e.find('width').text)
AMOUNT_OF_TIME_IN_ROW = int(e.find('amountOfTimeInRow').text)
NODE_RADIUS = float(e.find('nodeRadius').text)


class Line:
    """class that represent collection of nodes"""
    def __init__(self, y, canvas, transparent=False):
        """
        @:param y - y coordinate of horizontal line
        @:param transparent - if it's True line is background color
        @:param canvas - represent canvas where Line is drawing
        """
        self.y = y
        self.transparent = transparent
        self.canvas = canvas
        self.nodes = [Node(LINE_PAD_X * 3 // 2 + i * ((WIDTH - 2 * LINE_PAD_X) / (AMOUNT_OF_TIME_IN_ROW * 32)),
                           self.y, i, self.canvas) for i in range(AMOUNT_OF_TIME_IN_ROW * 32)]  # creation of nodes

    def draw(self):
        """draw Line and at the same time create Nodes and replace them on canvas"""
        self.canvas.create_line(LINE_PAD_X, self.y, WIDTH - LINE_PAD_X, self.y,
                                fill=LINE_COLOR if self.transparent is False else BG_COLOR)
        for node in self.nodes:
            node.draw()

    def hide(self):
        """hide Line but don't hide Nodes"""
        self.canvas.create_line(LINE_PAD_X, self.y, WIDTH - LINE_PAD_X, self.y, fill=BG_COLOR)
        self.transparent = True
        [node.hide() for node in self.nodes]

    def isCollision(self, eveX, eveY):
        """return index of Node that was clicked on or return None if click was far"""
        if self.y-NODE_RADIUS <= eveY <= self.y+NODE_RADIUS:  # check if click was near line
            for node in self.nodes:
                if node.isCollision(eveX, eveY):
                    return node.numberInLine
