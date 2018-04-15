import xml.etree.ElementTree
e = xml.etree.ElementTree.parse('config').getroot()

LINE_COLOR = e.find('lineColor').text
LINE_LEN = int(e.find('notesExtraLineLen').text)
NODE_COLOR = e.find('nodeColor').text

NODE_RENDER_RADIUS = float(e.find('nodeRenderRadius').text)
NODE_WORK_RADIUS = float(e.find('nodeWorkRadius').text)

NOTES_HEIGH = int(e.find('notesHeigh').text)
NOTES_WIDTH = int(e.find('notesWidth').text)

RESTS_HEIGH = int(e.find('restsHeigh').text)
RESTS_WIDTH = int(e.find('restsWidth').text)


class Node:
    """This node can be changed on notes by click on them"""
    radius = NODE_RENDER_RADIUS
    workRadius = NODE_WORK_RADIUS

    def __init__(self, x, y, numberOfNode, numberOfLine, numberOfRow, scanvas):
        """
        create Node by coordinates x, y
        @:param x - represent x coordinate of Node
        @:param y - represent y coordinate of Node
        @:param numberInLine - represent index of Node in Line class
        @:param canvas - represent canvas where Node is drawing
        """
        self.x = x
        self.y = y
        self.numberInLine = numberOfNode
        self.numberOfLine = numberOfLine
        self.numberOfRow = numberOfRow
        self.scanvas = scanvas
        self.round = None
        self.obj = None
        self.tail = None
        self.extraLine = None
        self.path = None

    def drawPoint(self):
        """draw Node by coordinates that was given at creation"""
        self.round = self.scanvas.canvas.create_oval(self.x - self.radius, self.y - self.radius, self.x + self.radius,
                                             self.y + self.radius, fill=NODE_COLOR, outline=NODE_COLOR)

    def hide(self):
        """fill Node with background color"""
        self.scanvas.canvas.delete(self.round)

    def isCollision(self, eveX, eveY):
        """return True if click on Node else False"""
        return (eveX - self.x)**2+(eveY - self.y)**2 <= self.workRadius ** 2

    def delImages(self):
        if self.obj is not None:
            self.scanvas.canvas.delete(self.obj)
            if self.tail is not None:
                self.scanvas.canvas.delete(self.tail)
            #add deletion of extraLines
            #if self.numberOfLine <= 5:
            #    tallestNote = self.numberOfLine
            #    for i in range(5, self.numberOfLine-1, -1):
            #        if self.scanvas.rows[self.numberOfRow].lines[i].nodes[self.numberInLine].isNotEmpty():
            #            tallestNote = i
            #    print(tallestNote)
            #    for i in range(self.numberOfLine, tallestNote+1):
            #        self.scanvas.rows[self.numberOfRow].lines[tallestNote].nodes[i].delExtraLine()

            self.path = None

    def getNode(self):
        return [self.numberOfRow, self.numberOfLine, self.numberInLine]

    def isRested(self):
        return self.path in self.scanvas.rests or self.path in self.scanvas.barlines

    def drawObj(self, path):
        if path in self.scanvas.notes:
            self.delImages()
            if self.scanvas.rows[self.numberOfRow].lines[10].nodes[self.numberInLine].isRested():
                self.scanvas.rows[self.numberOfRow].lines[10].nodes[self.numberInLine].delImages()

            if self.numberOfLine <= 5:
                for i in range(5, self.numberOfLine-1, -2):
                    self.scanvas.rows[self.numberOfRow].lines[i].nodes[self.numberInLine].addExtraLine()
            elif self.numberOfLine >= 17:
                for i in range(17, self.numberOfLine+1, 2):
                    self.scanvas.rows[self.numberOfRow].lines[i].nodes[self.numberInLine].addExtraLine()

            self.obj = self.scanvas.canvas.create_image(self.x, self.y, image=self.scanvas.notes[path][0])
            self.path = path
            if self.scanvas.notes[path][1] is not None:
                self.tail = self.scanvas.canvas.create_image(self.x, self.y, image=self.scanvas.notes[path][1])

        elif path in self.scanvas.rests or path in self.scanvas.barlines:
            if self.numberOfLine == 10:
                for i in range(23):
                    self.scanvas.rows[self.numberOfRow].lines[i].nodes[self.numberInLine].delImages()
                self.obj = self.scanvas.canvas.create_image(self.x, self.y,
                           image=self.scanvas.rests[path] if path in self.scanvas.rests else self.scanvas.barlines[path])
                self.path = path
            else:
                self.scanvas.rows[self.numberOfRow].lines[10].nodes[self.numberInLine].drawObj(path)

    def addExtraLine(self):
        if self.extraLine is None:
            self.extraLine = self.scanvas.canvas.create_line(self.x-LINE_LEN, self.y, self.x+LINE_LEN, self.y, fill=LINE_COLOR)

    def delExtraLine(self):
        if self.extraLine is not None:
            self.scanvas.canvas.delete(self.extraLine)
            print(self.extraLine)

    def isNotEmpty(self):
        return self.path is not None



