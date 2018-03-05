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

    def __init__(self, y, canvas, transparent=False):
        self.y = y
        self.transparent = transparent
        self.canvas = canvas
        self.draw()

    def draw(self):
        self.canvas.create_line(LINE_PAD_X, self.y, WIDTH - LINE_PAD_X, self.y,
                                fill=LINE_COLOR if self.transparent is False else BG_COLOR)
        self.nodes = [Node(LINE_PAD_X * 3 // 2 + i * ((WIDTH - 2 * LINE_PAD_X) / (AMOUNT_OF_TIME_IN_ROW * 32)),
                           self.y, i, self.canvas) for i in range(AMOUNT_OF_TIME_IN_ROW * 32)]

    def hide(self):
        self.canvas.create_line(LINE_PAD_X, self.y, WIDTH - LINE_PAD_X, self.y, fill=BG_COLOR)
        self.transparent = True
        [node.hide() for node in self.nodes]

    def isCollision(self, eveX, eveY):
        if self.y-NODE_RADIUS <= eveY <= self.y+NODE_RADIUS:
            for node in self.nodes:
                if node.isCollision(eveX, eveY):
                    return node.numberInLine
