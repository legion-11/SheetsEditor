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
        """draw round by coordinates that was given at creation"""
        if self.round is None:
            self.round = self.scanvas.canvas.create_oval(self.x - self.radius, self.y - self.radius, self.x + self.radius,
                                                     self.y + self.radius, fill=NODE_COLOR, outline=NODE_COLOR)

    def hidePoint(self):
        """dell round"""
        if self.round is not None:
            self.scanvas.canvas.delete(self.round)

    def isCollision(self, eveX, eveY):
        """return True if click on Node else False"""
        return (eveX - self.x)**2+(eveY - self.y)**2 <= self.workRadius ** 2

    def delImages(self):
        """delete images obj, tail, extraLines and path of Node"""
        if self.obj is not None:
            self.scanvas.canvas.delete(self.obj)
            if self.tail is not None:
                self.scanvas.canvas.delete(self.tail)
            self.path = None
            # deletion of extraLines
            if self.numberOfLine <= 5:
                flag = False
                for i in range(1, 6, 2):
                    if flag:
                        break
                    for j in range(i, -1, -1):
                        if self.scanvas.rows[self.numberOfRow].lines[j].nodes[self.numberInLine].isNotEmpty():
                            flag = True
                        else:
                            self.scanvas.rows[self.numberOfRow].lines[j].nodes[self.numberInLine].delExtraLine()
            elif self.numberOfLine >= 17:
                flag = False
                for i in range(22, 15, -2):
                    if flag:
                        break
                    for j in range(i, 23):
                        if self.scanvas.rows[self.numberOfRow].lines[j].nodes[self.numberInLine].isNotEmpty():
                            flag = True
                        else:
                            self.scanvas.rows[self.numberOfRow].lines[j].nodes[self.numberInLine].delExtraLine()

    def getNode(self) -> list:
        """return list of numberOfRow, numberOfLine, numberInLine"""
        return [self.numberOfRow, self.numberOfLine, self.numberInLine]

    def isRested(self):
        """return true if this Node is on 10 line and it's path is barline or rest"""
        return self.path in self.scanvas.rests or self.path in self.scanvas.barlines

    def drawObj(self, path):
        """draw images of note"""
        if path in self.scanvas.notes:
            self.delImages()
            # del rest or barline if it is in the similar column
            if self.scanvas.rows[self.numberOfRow].lines[10].nodes[self.numberInLine].isRested():
                self.scanvas.rows[self.numberOfRow].lines[10].nodes[self.numberInLine].delImages()
            # add extraLines
            if self.numberOfLine <= 5:
                for i in range(5, self.numberOfLine-1, -2):
                    self.scanvas.rows[self.numberOfRow].lines[i].nodes[self.numberInLine].addExtraLine()
            elif self.numberOfLine >= 17:
                for i in range(17, self.numberOfLine+1, 2):
                    self.scanvas.rows[self.numberOfRow].lines[i].nodes[self.numberInLine].addExtraLine()
            # draw of head of the note
            self.obj = self.scanvas.canvas.create_image(self.x, self.y, image=self.scanvas.notes[path][0])
            self.path = path
            # draw tail of the note
            if self.scanvas.notes[path][1] is not None:
                if self.numberOfLine > 11:
                    self.tail = self.scanvas.canvas.create_image(self.x, self.y, image=self.scanvas.notes[path][1])
                else:
                    self.tail = self.scanvas.canvas.create_image(self.x, self.y, image=self.scanvas.notes[path][2])

        # draw image of rest on the 10's line
        elif path in self.scanvas.rests or path in self.scanvas.barlines:
            if self.numberOfLine == 10:
                for i in range(23):
                    self.scanvas.rows[self.numberOfRow].lines[i].nodes[self.numberInLine].delImages()
                self.obj = self.scanvas.canvas.create_image(self.x, self.y,
                           image=self.scanvas.rests[path] if path in self.scanvas.rests else self.scanvas.barlines[path])
                self.path = path
            # del of another images on the  same column
            else:
                self.scanvas.rows[self.numberOfRow].lines[10].nodes[self.numberInLine].drawObj(path)

        # draw modificator
        elif path in self.scanvas.modifications:
            self.delImages()
            # draw of head of the rest
            self.obj = self.scanvas.canvas.create_image(self.x, self.y, image=self.scanvas.modifications[path])
            self.path = path

        elif path in self.scanvas.startRowSigns:
            self.scanvas.rows[self.numberOfRow].changeClef(path)

    def addExtraLine(self):
        """draw small line across node"""
        if self.extraLine is None:
            self.extraLine = self.scanvas.canvas.create_line(self.x-LINE_LEN, self.y, self.x+LINE_LEN, self.y, fill=LINE_COLOR)

    def delExtraLine(self):
        """draw small line """
        if self.extraLine is not None:
            self.scanvas.canvas.delete(self.extraLine)
            self.extraLine = None

    def isNotEmpty(self):
        """return path to the image of the note or rest or ..."""
        return self.path is not None
