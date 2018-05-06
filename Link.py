import xml.etree.ElementTree
e = xml.etree.ElementTree.parse('config').getroot()
SHIFT = int(e.find('shift').text)


class Link:
    line = None

    def __init__(self, scanvas, node1, node2):
        self.scanvas = scanvas
        if node1.numberOfLine < node2.numberOfLine:
            self.node1 = node1
            self.node2 = node2
        elif node2.numberOfLine > node2.numberOfLine:
            self.node2 = node1
            self.node1 = node2
        else:
            if node1.numberInLine < node2.numberInLine:
                self.node1 = node1
                self.node2 = node2
            else:
                self.node2 = node1
                self.node1 = node2

    def draw(self):
        self.line = self.scanvas.canvas.create_line(self.createPoints())

    def delete(self):
        self.scanvas.canvas.delete(self.line)
        self.node1.setLink(None)
        self.node2.setLink(None)

    def createPoints(self):
        x1, y1 = self.node1.x, self.node1.y
        x2, y2 = self.node2.x, self.node2.y
        if self.node1.numberOfLine < 12 or self.node2.numberOfLine < 12:
            x3, y3 = (max(x1, x2) + min(x1, x2)) / 2, min(y1, y2) - SHIFT
        else:
            x3, y3 = (max(x1, x2) + min(x1, x2)) / 2, max(y1, y2) + SHIFT
        a = (y3 - (x3 * (y2 - y1) + x2 * y1 - x1 * y2) / (x2 - x1)) / (x3 * (x3 - x1 - x2) + x1 * x2)
        b = (y2 - y1) / (x2 - x1) - a * (x1 + x2)
        c = (x2 * y1 - x1 * y2) / (x2 - x1) + a * x1 * x2
        xy = []
        for x in range(round(min(x1, x2)), round(max(x1, x2))):
            # x coordinates
            xy.append(x)
            # y coordinates
            xy.append(a * x ** 2 + b * x + c)
        return xy
