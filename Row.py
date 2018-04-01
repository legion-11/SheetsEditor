import xml.etree.ElementTree
from Line import Line

e = xml.etree.ElementTree.parse('config').getroot()
BG_COLOR = e.find('bgColor').text
DISTANCE_BETWEEN_LINES = float(e.find('distanceBetweenLines').text)
NODE_WORK_RADIUS = float(e.find('nodeWorkRadius').text)


class Row:

    def __init__(self, y, canvas):
        self.y = y
        self.canvas = canvas
        self.lines = []
        for i in range(23):
            self.lines.append(Line(y + DISTANCE_BETWEEN_LINES * i, self.canvas, i,
                                   transparent=False if (7 <= i <= 15 and i % 2) else True))

    def draw(self):
        [line.draw() for line in self.lines]

    def hide(self):
        [line.hide() for line in self.lines]

    def isCollision(self, eveX, eveY):
        if self.y - NODE_WORK_RADIUS <= eveY <= self.y + NODE_WORK_RADIUS ** 23:  # check if click was near row
            for line in self.lines:
                if line.isCollision(eveX, eveY):
                    return line.isCollision(eveX, eveY)