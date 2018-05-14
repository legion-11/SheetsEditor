import xml.etree.ElementTree
from Line import Line

e = xml.etree.ElementTree.parse('config').getroot()
BG_COLOR = e.find('bgColor').text
DISTANCE_BETWEEN_LINES = float(e.find('distanceBetweenLines').text)
NODE_WORK_RADIUS = float(e.find('nodeWorkRadius').text)
X_TO_PASTE_CLEF = int(e.find('xToPasteClef').text)
SIZE_OF_NUMS = int(e.find('sizeOfNums').text)
X_TO_PASTE_TEMP = X_TO_PASTE_CLEF + int(e.find('plusXToPasteTemp').text)


class Row:

    def __init__(self, y, numberOfRow, scanvas, pathClef):
        self.y = y
        self.scanvas = scanvas
        self.lines = []
        self.numberOfRow = numberOfRow
        self.pathClef = pathClef
        self.clef = None
        self.numerator = None
        self.denominator = None
        self.numeratorNum = None
        self.denominatorNum = None
        for i in range(23):
            self.lines.append(Line(y + DISTANCE_BETWEEN_LINES * i, i, self.numberOfRow, self.scanvas,
                                   transparent=False if (7 <= i <= 15 and i % 2) else True))
        self.changeClef(pathClef)

    def draw(self):
        """draw lines"""
        [line.draw() for line in self.lines]

    def hide(self):
        """delete lines"""
        if self.numerator is not None:
            self.scanvas.canvas.delete(self.numerator)
        if self.denominator is not None:
            self.scanvas.canvas.delete(self.denominator)
        self.scanvas.canvas.delete(self.clef)
        [line.hide() for line in self.lines]

    def isCollision(self, eveX, eveY):
        """
        return list with [index of Row, index of Line, index of Node] that was clicked on
        return None if click was far
        """
        if self.y - NODE_WORK_RADIUS <= eveY <= self.y + NODE_WORK_RADIUS * 23:  # check if move was near row
            for line in self.lines:
                if line.isCollision(eveX, eveY):
                    return line.isCollision(eveX, eveY)

    def changeClef(self, path):
        """change the clef of row"""
        if self.clef is not None:
            self.scanvas.canvas.delete(self.clef)
        self.pathClef = path
        self.clef = self.scanvas.canvas.create_image(X_TO_PASTE_CLEF, self.y + DISTANCE_BETWEEN_LINES * 10, image=self.scanvas.startRowSigns[path])

    def changeTemp(self, numeratorNum, denominatorNum):
        """change temp by click on row"""
        if self.numerator is not None:
            self.scanvas.canvas.delete(self.numerator)
        self.numerator = self.scanvas.canvas.create_text(X_TO_PASTE_TEMP, self.lines[9].y,
                                                     fill="black", font=("Algerian", str(SIZE_OF_NUMS)), text=numeratorNum)
        self.numeratorNum = None
        if self.denominator is not None:
            self.scanvas.canvas.delete(self.denominator)
        self.denominator = self.scanvas.canvas.create_text(X_TO_PASTE_TEMP, self.lines[13].y,
                                                     fill="black", font=("Algerian", str(SIZE_OF_NUMS)), text=denominatorNum)
        self.denominatorNum = None
