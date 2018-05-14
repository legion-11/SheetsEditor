import xml.etree.ElementTree
from Link import Link
e = xml.etree.ElementTree.parse('config').getroot()
CANVAS_HEIGH = int(e.find('canvasHeigh').text)
LINE_COLOR = e.find('lineColor').text
LINE_LEN = int(e.find('notesExtraLineLen').text)
NODE_COLOR = e.find('nodeColor').text

NODE_RENDER_RADIUS = float(e.find('nodeRenderRadius').text)
NODE_WORK_RADIUS = float(e.find('nodeWorkRadius').text)
DISTANCE_BETWEEN_LINES = float(e.find('distanceBetweenLines').text)

NOTES_HEIGH = int(e.find('notesHeigh').text)
NOTES_WIDTH = int(e.find('notesWidth').text)

RESTS_HEIGH = int(e.find('restsHeigh').text)
RESTS_WIDTH = int(e.find('restsWidth').text)

SHIFT_FOR_DOT = int(e.find('shiftForDot').text)

LINE_PAD_X = float(e.find('linePadx').text)
LINE_START_POINT_FOR_NODES = float(e.find('lineStartPointForNodes').text)
LINE_END_POINT_FOR_NODES = float(e.find('lineEndPointForNodes').text)
WIDTH = float(e.find('canvasWidth').text)
AMOUNT_OF_TIME_IN_ROW = int(e.find('amountOfTimeInRow').text)
AMOUNT_OF_NODE_IN_TIME = int(e.find('amountOfNodeInTime').text)
DISTANCE_BETWEN_NODES = (WIDTH - LINE_PAD_X - LINE_START_POINT_FOR_NODES - LINE_END_POINT_FOR_NODES) / (AMOUNT_OF_TIME_IN_ROW * AMOUNT_OF_NODE_IN_TIME)
SHIFT_IN_ACCORD_FOR_HEAD = int(e.find('notesShiftInAccordForHead').text)
SHIFT_IN_ACCORD_FOR_TAIL = int(e.find('notesShiftInAccordForTail').text)

DISTANCE_TO_DRAW_COMPOSED_TAIL = int(e.find('distanceToDrawComposedTail').text)
DISTANCE_BEETWEN_COMPOSED_TAILS = int(e.find('distanceBeetwenComposedTails').text)

NOTES_WITHOUT_TAIL = ['assets/notes/breve.png',
                      'assets/notes/whole note.png',
                      'assets/notes/half note.png']
LEN_SHORT_COMPOSED_LINE = 10


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
        self.composeLinesRight = []
        self.extraLine = None
        self.path = None
        self.link = None
        self.dot = None
        self.shifted = None  # None - without shift, False - shift left, True - shift right
        self.composedWithLeft = None
        self.composedWithRight = None
        self.accordedWithUp = None
        self.accordedWithDown = None
        self.tailUp = None

    def drawPoint(self):
        """draw round by coordinates that was given at creation"""
        if self.round is None:
            self.round = self.scanvas.canvas.create_oval(self.x - self.radius, self.y - self.radius, self.x + self.radius,
                                                     self.y + self.radius, fill=NODE_COLOR, outline=NODE_COLOR)

    def hidePoint(self):
        """dell round"""
        if self.round is not None:
            self.scanvas.canvas.delete(self.round)
            self.round = None

    def isCollision(self, eveX, eveY):
        """return True if click on Node else False"""
        return self.y - DISTANCE_BETWEEN_LINES//4 < eveY < self.y + DISTANCE_BETWEEN_LINES//4 and\
            self.x - DISTANCE_BETWEN_NODES // 2 < eveX < self.x + DISTANCE_BETWEN_NODES // 2

    def isRested(self):
        """return true if this Node is on 10 line and it's path is barline or rest"""
        return self.path in self.scanvas.rests or self.path in self.scanvas.barlines

    def drawObj(self, path):
        """draw images of note"""
        if path in self.scanvas.notes:
            self.drawNote(path)

        # draw image of rest on the 10's line
        elif path in self.scanvas.rests or path in self.scanvas.barlines:
            if self.numberOfLine == 10:
                for i in range(23):
                    self.getNodeInSimilarColumn(i).delImages()
                self.obj = self.scanvas.canvas.create_image(self.x, self.y,
                           image=self.scanvas.rests[path] if path in self.scanvas.rests else self.scanvas.barlines[path])
                self.path = path
            # del of another images on the  same column
            else:
                self.scanvas.rows[self.numberOfRow].lines[10].nodes[self.numberInLine].drawObj(path)

        # draw modificator
        elif path in self.scanvas.modifications:
            canDraw = True
            for i in range(23):
                if self.getNodeInSimilarColumn(i).path in self.scanvas.notes:
                    canDraw = False
                    break
            if canDraw:
                self.delImages()
                # draw of head of the rest
                self.obj = self.scanvas.canvas.create_image(self.x, self.y, image=self.scanvas.modifications[path])
                self.path = path

        elif path in self.scanvas.startRowSigns:
            self.scanvas.rows[self.numberOfRow].changeClef(path)

    def isNotEmpty(self):
        """return path to the image of the note or rest or ...
        can be used for checking if Node is not empty"""
        return self.path is not None

    def isNote(self):
        return self.path in self.scanvas.notes

    def drawLink(self, node):
        if self.link is not None:
            self.link.delete()
        if node.link is not None:
            node.link.delete()
        node.link = self.link = Link(self.scanvas, self, node)
        self.link.draw()

    def delLink(self):
        self.link.delete()

    def delImages(self):
        """delete images obj, tail, extraLines and path of Node"""
        self.path = None
        if self.obj is not None:
            self.scanvas.canvas.delete(self.obj)
            if self.tail is not None:
                self.scanvas.canvas.delete(self.tail)
                self.tailUp = None
                #if self.composeLinesRight is not None:
                #    self.delComposeWithRight()
                #    self.delComposeWithLeft()
                #if self.accordedWithDown is not None and self.accordedWithUp is not None:
                #    self.accordedWithUp.composedWithDown = self.accordedWithDown
                #    self.accordedWithDown.composedWithUp = self.accordedWithUp
                #    self.accordedWithUp.drawObj(self.accordedWithUp.path)
                #    self.accordedWithDown = None
                #    self.accordedWithUp = None
                #elif self.accordedWithUp is not None and self.accordedWithDown is None:
                #    self.accordedWithUp.composedWithDown = None
                #    self.accordedWithUp.drawObj(self.accordedWithUp.path)
                #    self.accordedWithUp = None
                #elif self.accordedWithUp is None and self.accordedWithDown is not None:
                #    self.accordedWithDown.composedWithUp = None
                #    self.accordedWithDown.drawObj(self.accordedWithDown.path)
                #    self.accordedWithDown = None

            if self.link is not None:
                self.link.delete()

            # deletion of extraLines
            if self.numberOfLine <= 5:
                highestNoteLine = 6
                for i in range(6):
                    if self.getNodeInSimilarColumn(i).path in self.scanvas.notes:
                        highestNoteLine = i
                        break
                for i in range(1, highestNoteLine, 2):
                    if self.getNodeInSimilarColumn(i).extraLine is not None:
                        self.scanvas.canvas.delete(self.getNodeInSimilarColumn(i).extraLine)
                        self.getNodeInSimilarColumn(i).extraLine = None

            elif self.numberOfLine >= 17:
                lowestNoteLine = 16
                for i in range(22, 16, -1):
                    if self.getNodeInSimilarColumn(i).path in self.scanvas.notes:
                        lowestNoteLine = i
                        break
                for i in range(21, lowestNoteLine, -2):
                    if self.getNodeInSimilarColumn(i).extraLine is not None:
                        self.scanvas.canvas.delete(self.getNodeInSimilarColumn(i).extraLine)
                        self.getNodeInSimilarColumn(i).extraLine = None

            # update state of notes

        elif self.scanvas.rows[self.numberOfRow].lines[10].nodes[self.numberInLine].isRested():
            self.scanvas.rows[self.numberOfRow].lines[10].nodes[self.numberInLine].delImages()

    def getNodePosition(self) -> list:
        """return list of numberOfRow, numberOfLine, numberInLine"""
        return [self.numberOfRow, self.numberOfLine, self.numberInLine]

    def drawNote(self, path):
        self.delImages()
        self.path = path
        numberOfNotesInColumn = 1
        node = None
        for i in range(self.numberOfLine):
            if self.getNodeInSimilarColumn(i).path in self.scanvas.notes:
                numberOfNotesInColumn += 1
                if numberOfNotesInColumn == 8:
                    self.path = None
                    return
                if self.getNodeInSimilarColumn(i).path == self.path:
                    node = self.getNodeInSimilarColumn(i)

        self.accordedWithUp = node
        if self.accordedWithUp is not None:
            self.accordedWithUp.accordedWithDown = self

        node = None
        for i in range(22, self.numberOfLine, -1):
            if self.getNodeInSimilarColumn(i).path in self.scanvas.notes:
                numberOfNotesInColumn += 1
                if numberOfNotesInColumn == 8:
                    self.path = None
                    self.accordedWithUp = None
                    return
                if self.getNodeInSimilarColumn(i).path == self.path:
                    node = self.getNodeInSimilarColumn(i)

        self.accordedWithDown = node
        if self.accordedWithDown is not None:
            self.accordedWithDown.accordedWithUp = self

        # del rest or barline if it is in the similar column
        if self.scanvas.rows[self.numberOfRow].lines[10].nodes[self.numberInLine].isRested():
            self.scanvas.rows[self.numberOfRow].lines[10].nodes[self.numberInLine].delImages()

        # add extraLines
        if self.numberOfLine <= 5:
            for i in range(5, self.numberOfLine - 1, -2):
                self.getNodeInSimilarColumn(i).addExtraLine()

        elif self.numberOfLine >= 17:
            for i in range(17, self.numberOfLine + 1, 2):
                self.getNodeInSimilarColumn(i).addExtraLine()

        # draw tail of the note
        if self.scanvas.notes[path][1] is not None:
            accord = []  # from highest note to lowest
            tailsDown = 0
            tmp = self
            accord.append(tmp)
            if tmp.numberOfLine < 11:
                tailsDown += 1

            while tmp.accordedWithUp is not None:
                tmp = tmp.accordedWithUp
                accord.append(tmp)
                if tmp.numberOfLine < 11:
                    tailsDown += 1

            accord.reverse()
            tmp = self

            while tmp.accordedWithDown is not None:
                tmp = tmp.accordedWithDown
                accord.append(tmp)
                if tmp.numberOfLine < 11:
                    tailsDown += 1

            if len(accord) > 1 and accord[-1] == self and accord[-2].hasCompose():
                if accord[-2].composedWithLeft is not None:
                    accord[-2].delComposeWithLeft()
                    accord[-2].composedWithLeft.composedWithRight = self
                    self.composedWithLeft = accord[-2].composedWithLeft
                    accord[-2].composedWithLeft = None

                if accord[-2].composedWithRight is not None:
                    accord[-2].delComposeWithRight()
                    accord[-2].composedWithRight.composedWithLeft = self
                    self.composedWithRight = accord[-2].composedWithRight
                    accord[-2].composedWithRight = None

                self.composeWith(self.composedWithRight if self.composedWithRight is not None else self.composedWithLeft)

            elif len(accord) > 1 and accord[-1] != self and accord[-1].hasCompose():
                accord[-1].composeWith(accord[-1].composedWithRight if accord[-1].composedWithRight is not None else accord[-1].composedWithLeft)

            elif tailsDown > len(accord) - tailsDown:
                self.drawTailsDown(path, accord)

            else:
                self.drawTailsUp(path, accord)

        # draw of head of the note
        if self.accordedWithDown is not None and self.accordedWithDown.numberOfLine - self.numberOfLine == 1:
            if self.accordedWithDown.tailUp is False:
                if self.accordedWithDown.shifted is None:
                    self.shifted = False
                    self.obj = self.scanvas.canvas.create_image(self.x - SHIFT_IN_ACCORD_FOR_HEAD, self.y, image=self.scanvas.notes[path][0])
                else:
                    self.shifted = None
                    self.obj = self.scanvas.canvas.create_image(self.x, self.y,
                                                                image=self.scanvas.notes[path][0])

                higherNode = self.accordedWithUp
                while higherNode is not None:
                    if higherNode.accordedWithDown.numberOfLine - higherNode.numberOfLine == 1:
                        if higherNode.accordedWithDown.shifted == higherNode.shifted or higherNode.shifted is True:
                            self.scanvas.canvas.delete(higherNode.obj)
                            higherNode.obj = self.scanvas.canvas.create_image(
                                higherNode.x if higherNode.accordedWithDown.shifted is False
                                else (higherNode.x - SHIFT_IN_ACCORD_FOR_HEAD),
                                higherNode.y,
                                image=higherNode.scanvas.notes[path][0])
                            higherNode.shifted = None if higherNode.accordedWithDown.shifted is False else False
                    else:
                        break
                    higherNode = higherNode.accordedWithUp

            else:
                if self.accordedWithDown.shifted is None:
                    self.shifted = True
                    self.obj = self.scanvas.canvas.create_image(self.x + SHIFT_IN_ACCORD_FOR_HEAD, self.y, image=self.scanvas.notes[path][0])
                else:
                    self.shifted = None
                    self.obj = self.scanvas.canvas.create_image(self.x, self.y,
                                                                image=self.scanvas.notes[path][0])

                    higherNode = self.accordedWithUp
                    while higherNode is not None:
                        if higherNode.accordedWithDown.numberOfLine - higherNode.numberOfLine == 1:
                            if higherNode.accordedWithDown.shifted == higherNode.shifted or higherNode.shifted is False:
                                self.scanvas.canvas.delete(higherNode.obj)
                                higherNode.obj = self.scanvas.canvas.create_image(
                                    higherNode.x if higherNode.accordedWithDown.shifted is True
                                    else (higherNode.x + SHIFT_IN_ACCORD_FOR_HEAD),
                                    higherNode.y,
                                    image=higherNode.scanvas.notes[path][0])
                                higherNode.shifted = None if higherNode.accordedWithDown.shifted is True else True
                        else:
                            break
                        higherNode = higherNode.accordedWithUp

        else:
            self.shifted = None
            self.obj = self.scanvas.canvas.create_image(self.x, self.y,
                                                        image=self.scanvas.notes[path][0])
            if self.tailUp is False:
                higherNode = self.accordedWithUp
                while higherNode is not None:
                    if higherNode.accordedWithDown.numberOfLine - higherNode.numberOfLine == 1:
                        if higherNode.accordedWithDown.shifted == higherNode.shifted or higherNode.shifted is True:
                            self.scanvas.canvas.delete(higherNode.obj)
                            higherNode.obj = self.scanvas.canvas.create_image(
                                higherNode.x if higherNode.accordedWithDown.shifted is False
                                else (higherNode.x - SHIFT_IN_ACCORD_FOR_HEAD),
                                higherNode.y,
                                image=higherNode.scanvas.notes[path][0])
                            higherNode.shifted = None if higherNode.accordedWithDown.shifted is False else False
                    else:
                        break
                    higherNode = higherNode.accordedWithUp
            else:
                higherNode = self.accordedWithUp
                while higherNode is not None:
                    if higherNode.accordedWithDown.numberOfLine - higherNode.numberOfLine == 1:
                        if higherNode.accordedWithDown.shifted == higherNode.shifted or higherNode.shifted is False:
                            self.scanvas.canvas.delete(higherNode.obj)
                            higherNode.obj = self.scanvas.canvas.create_image(
                                higherNode.x if higherNode.accordedWithDown.shifted is True
                                else (higherNode.x + SHIFT_IN_ACCORD_FOR_HEAD),
                                higherNode.y,
                                image=higherNode.scanvas.notes[path][0])
                            higherNode.shifted = None if higherNode.accordedWithDown.shifted is True else True
                    else:
                        break
                    higherNode = higherNode.accordedWithUp

    def drawTailsDown(self, path, accord: list):
        if accord[-1].tail is not None:  # accord is drawing from highest note to lowest note
            self.scanvas.canvas.delete(accord[-1].tail)
        for i in range(len(accord) - 1):
            self.scanvas.canvas.delete(accord[i].tail)
            accord[i].tail = self.scanvas.canvas.create_line(accord[i].x - SHIFT_IN_ACCORD_FOR_TAIL,
                                                             accord[i].y,
                                                             accord[i + 1].x - SHIFT_IN_ACCORD_FOR_TAIL,
                                                             accord[i + 1].y)
            accord[i].tailUp = False

        accord[-1].tail = self.scanvas.canvas.create_image(accord[-1].x, accord[-1].y,
                                                           image=self.scanvas.notes[path][2])
        accord[-1].tailUp = False

    def drawTailsUp(self, path, accord: list):
        accord.reverse()  # accord is drawing from lowest note to highest note
        if accord[-1].tail is not None:
            self.scanvas.canvas.delete(accord[-1].tail)
        for i in range(len(accord) - 1):
            self.scanvas.canvas.delete(accord[i].tail)
            accord[i].tail = self.scanvas.canvas.create_line(accord[i].x + SHIFT_IN_ACCORD_FOR_TAIL,
                                                             accord[i].y,
                                                             accord[i + 1].x + SHIFT_IN_ACCORD_FOR_TAIL,
                                                             accord[i + 1].y)
            accord[i].tailUp = True

        accord[-1].tail = self.scanvas.canvas.create_image(accord[-1].x,
                                                           accord[-1].y,
                                                           image=self.scanvas.notes[path][1])
        accord[-1].tailUp = True

    def delTail(self):
        self.scanvas.canvas.delete(self.tail)
        self.tail = None

    def addExtraLine(self):
        """draw small line across node"""
        if self.extraLine is None:
            self.extraLine = self.scanvas.canvas.create_line(self.x-LINE_LEN, self.y, self.x+LINE_LEN, self.y, fill=LINE_COLOR)

    def dotNote(self):
        if self.path in self.scanvas.notes:
            self.dot = self.scanvas.canvas.create_image(self.x, self.y, image=self.scanvas.dot['assets/temp/dot.png'])

    def hasCompose(self):
        if self.composedWithLeft is not None or self.composedWithRight is not None:
            return True
        else:
            return False

    def getNodeInSimilarColumn(self, NumberOfLine: int):
        return self.scanvas.rows[self.numberOfRow].lines[NumberOfLine].nodes[self.numberInLine]

    def getHighestLineOfAccord(self):
        """highest line has lowest number"""
        node = self
        while node.accordedWithUp is not None:
            node = node.accordedWithUp
        return node.numberOfLine

    def getLowestLineOfAccord(self):
        node = self
        while node.accordedWithDown is not None:
            node = node.accordedWithDown
        return node.numberOfLine

    def getLineY(self, numberOfLine):
        return int(self.scanvas.rows[self.numberOfRow].lines[numberOfLine].y)

    def delComposeWithLeft(self):
        if self.composedWithLeft is not None:
            self.composedWithLeft.delComposeWithRight()

    def delComposeWithRight(self):
        if self.composedWithRight is not None:
            for i in range(len(self.composeLinesRight)-1, -1, -1):
                self.scanvas.canvas.delete(self.composeLinesRight.pop(i))

    def drawComposeWithRightDown(self, lowestY):
        if self.path == self.composedWithRight.path:
            amounOfLinesBetweenNodes = self.scanvas.notes[self.path][3]
            for i in range(amounOfLinesBetweenNodes):
                self.composeLinesRight.append(self.scanvas.canvas.create_line(self.x - SHIFT_IN_ACCORD_FOR_TAIL,
                                                                              lowestY - i*DISTANCE_BEETWEN_COMPOSED_TAILS,
                                                                              self.composedWithRight.x - SHIFT_IN_ACCORD_FOR_TAIL,
                                                                              lowestY - i*DISTANCE_BEETWEN_COMPOSED_TAILS,
                                                                              width=3))
            self.drawComposedTailsDown(lowestY)

        else:
            if self.composedWithRight.composedWithRight is not None and self.composedWithRight.path == self.composedWithRight.composedWithRight.path:
                pass

            else:
                amounOfLinesBetweenNodes1 = self.scanvas.notes[self.path][3]
                amounOfLinesBetweenNodes2 = self.scanvas.notes[self.composedWithRight.path][3]

                for i in range(min(amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2)):
                    self.composeLinesRight.append(self.scanvas.canvas.create_line(self.x - SHIFT_IN_ACCORD_FOR_TAIL,
                                                                                  lowestY - i * DISTANCE_BEETWEN_COMPOSED_TAILS,
                                                                                  self.composedWithRight.x - SHIFT_IN_ACCORD_FOR_TAIL,
                                                                                  lowestY - i * DISTANCE_BEETWEN_COMPOSED_TAILS,
                                                                                  width=3))

                if amounOfLinesBetweenNodes1 > amounOfLinesBetweenNodes2:
                    for i in range(min(amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2),
                                   max(amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2) - min(
                                       amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2) + 1):
                        self.composeLinesRight.append(self.scanvas.canvas.create_line(self.x - SHIFT_IN_ACCORD_FOR_TAIL,
                                                                                      lowestY - i * DISTANCE_BEETWEN_COMPOSED_TAILS,
                                                                                      self.x + LEN_SHORT_COMPOSED_LINE,
                                                                                      lowestY - i * DISTANCE_BEETWEN_COMPOSED_TAILS,
                                                                                      width=3))
                else:
                    for i in range(min(amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2),
                                   max(amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2) - min(
                                       amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2) + 1):
                        self.composeLinesRight.append(
                            self.scanvas.canvas.create_line(self.composedWithRight.x - SHIFT_IN_ACCORD_FOR_TAIL,
                                                            lowestY - i * DISTANCE_BEETWEN_COMPOSED_TAILS,
                                                            self.composedWithRight.x - LEN_SHORT_COMPOSED_LINE,
                                                            lowestY - i * DISTANCE_BEETWEN_COMPOSED_TAILS,
                                                            width=3))
                self.drawComposedTailsDown(lowestY)

    def drawComposedTailsDown(self, lowestY):
        if not self.tailUp:
            lowestNode = self.getNodeInSimilarColumn(self.getLowestLineOfAccord())
            lowestNode.scanvas.canvas.delete(lowestNode.tail)
            lowestNode.tail = self.scanvas.canvas.create_line(lowestNode.x - SHIFT_IN_ACCORD_FOR_TAIL,
                                                              lowestNode.y,
                                                              lowestNode.x - SHIFT_IN_ACCORD_FOR_TAIL,
                                                              lowestY)

        else:
            similarNotes = []
            node = self
            similarNotes.append(node)
            while node.accordedWithUp is not None:
                node = node.accordedWithUp
                similarNotes.append(node)

            similarNotes.reverse()
            node = self
            while node.accordedWithDown is not None:
                node = node.accordedWithDown
                similarNotes.append(node)

            for i in range(len(similarNotes) - 1):
                self.scanvas.canvas.delete(similarNotes[i].tail)
                similarNotes[i].tail = self.scanvas.canvas.create_line(similarNotes[i].x - SHIFT_IN_ACCORD_FOR_TAIL,
                                                                 similarNotes[i].y,
                                                                 similarNotes[i + 1].x - SHIFT_IN_ACCORD_FOR_TAIL,
                                                                 similarNotes[i + 1].y)
                similarNotes[i].tailUp = False
            lowestNode = similarNotes[-1]
            lowestNode.scanvas.canvas.delete(lowestNode.tail)
            lowestNode.tail = self.scanvas.canvas.create_line(lowestNode.x - SHIFT_IN_ACCORD_FOR_TAIL,
                                                              lowestNode.y,
                                                              lowestNode.x - SHIFT_IN_ACCORD_FOR_TAIL,
                                                              lowestY)

    def drawComposeWithRightUp(self, highestY):
        if self.path == self.composedWithRight.path:
            amounOfLinesBetweenNodes = self.scanvas.notes[self.path][3]
            for i in range(amounOfLinesBetweenNodes):
                self.composeLinesRight.append(self.scanvas.canvas.create_line(self.x + SHIFT_IN_ACCORD_FOR_TAIL,
                                                                              highestY + i*DISTANCE_BEETWEN_COMPOSED_TAILS,
                                                                              self.composedWithRight.x + SHIFT_IN_ACCORD_FOR_TAIL,
                                                                              highestY + i*DISTANCE_BEETWEN_COMPOSED_TAILS,
                                                                              width=3))

            self.drawComposedTailsUp(highestY)
        else:
            if self.composedWithRight.composedWithRight is not None and self.composedWithRight.path == self.composedWithRight.composedWithRight.path:
                pass

            else:
                amounOfLinesBetweenNodes1 = self.scanvas.notes[self.path][3]
                amounOfLinesBetweenNodes2 = self.scanvas.notes[self.composedWithRight.path][3]

                for i in range(min(amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2)):
                    self.composeLinesRight.append(self.scanvas.canvas.create_line(self.x + SHIFT_IN_ACCORD_FOR_TAIL,
                                                                                  highestY + i * DISTANCE_BEETWEN_COMPOSED_TAILS,
                                                                                  self.composedWithRight.x + SHIFT_IN_ACCORD_FOR_TAIL,
                                                                                  highestY + i * DISTANCE_BEETWEN_COMPOSED_TAILS,
                                                                                  width=3))

                if amounOfLinesBetweenNodes1 > amounOfLinesBetweenNodes2:
                    for i in range(min(amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2),
                                   max(amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2) - min(
                                       amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2) + 1):

                        self.composeLinesRight.append(self.scanvas.canvas.create_line(self.x + SHIFT_IN_ACCORD_FOR_TAIL,
                                                                                      highestY + i * DISTANCE_BEETWEN_COMPOSED_TAILS,
                                                                                      self.x + LEN_SHORT_COMPOSED_LINE,
                                                                                      highestY + i * DISTANCE_BEETWEN_COMPOSED_TAILS,
                                                                                      width=3))
                else:
                    for i in range(min(amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2),
                                   max(amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2) - min(
                                       amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2) + 1):
                        self.composeLinesRight.append(self.scanvas.canvas.create_line(self.composedWithRight.x + SHIFT_IN_ACCORD_FOR_TAIL,
                                                                                      highestY + i * DISTANCE_BEETWEN_COMPOSED_TAILS,
                                                                                      self.composedWithRight.x - LEN_SHORT_COMPOSED_LINE,
                                                                                      highestY + i * DISTANCE_BEETWEN_COMPOSED_TAILS,
                                                                                      width=3))
                self.drawComposedTailsUp(highestY)

    def drawComposedTailsUp(self, highestY):
        if self.tailUp:
            highestNode = self.getNodeInSimilarColumn(self.getHighestLineOfAccord())
            highestNode.scanvas.canvas.delete(highestNode.tail)
            highestNode.tail = self.scanvas.canvas.create_line(highestNode.x + SHIFT_IN_ACCORD_FOR_TAIL,
                                                               highestNode.y,
                                                               highestNode.x + SHIFT_IN_ACCORD_FOR_TAIL,
                                                               highestY)

        else:
            similarNotes = []
            node = self
            similarNotes.append(node)
            while node.accordedWithUp is not None:
                node = node.accordedWithUp
                similarNotes.append(node)
            similarNotes.reverse()
            node = self
            while node.accordedWithDown is not None:
                node = node.accordedWithDown
                similarNotes.append(node)
            similarNotes.reverse()
            for i in range(len(similarNotes) - 1):
                self.scanvas.canvas.delete(similarNotes[i].tail)
                similarNotes[i].tail = self.scanvas.canvas.create_line(similarNotes[i].x + SHIFT_IN_ACCORD_FOR_TAIL,
                                                                       similarNotes[i].y,
                                                                       similarNotes[i + 1].x + SHIFT_IN_ACCORD_FOR_TAIL,
                                                                       similarNotes[i + 1].y)
                similarNotes[i].tailUp = True

            highestNode = similarNotes[-1]
            highestNode.scanvas.canvas.delete(highestNode.tail)
            highestNode.tail = self.scanvas.canvas.create_line(highestNode.x + SHIFT_IN_ACCORD_FOR_TAIL,
                                                               highestNode.y,
                                                               highestNode.x + SHIFT_IN_ACCORD_FOR_TAIL,
                                                               highestY)

    def composeWith(self, node):
        if self.path not in self.scanvas.notes or node.path not in self.scanvas.notes or\
                self.path in ['assets/notes/breve.png',
                              'assets/notes/whole note.png',
                              'assets/notes/half note.png',
                              'assets/notes/quarter note.png'] or\
                node.path in ['assets/notes/breve.png',
                              'assets/notes/whole note.png',
                              'assets/notes/half note.png',
                              'assets/notes/quarter note.png'] or\
                self.numberInLine == node.numberInLine or self.numberOfRow != node.numberOfRow:
            return

        if self.accordedWithDown is not None:
            self.accordedWithDown.composeWith(node)
            return
        if node.accordedWithDown is not None:
            self.composeWith(node.accordedWithDown)
            return

        tailsDown = 0
        tailsUp = 0

        node1, node2 = (self, node) if self.numberInLine < node.numberInLine else (node, self)
        node1.composedWithRight, node2.composedWithLeft = node2, node1

        amountOfLinesBetweenNodes = node1.scanvas.notes[node1.path][3]
        nodesTail = node1
        lowestY = nodesTail.getLineY(nodesTail.numberOfLine) + DISTANCE_TO_DRAW_COMPOSED_TAIL + \
                  amountOfLinesBetweenNodes * DISTANCE_BEETWEN_COMPOSED_TAILS  # lowestY means that this y has bigger y coordinate

        while nodesTail.accordedWithUp is not None:
            if nodesTail.numberOfLine < 11:
                tailsDown += 1
            else:
                tailsUp += 1
            nodesTail = nodesTail.accordedWithUp

        if nodesTail.tailUp:
            tailsUp += 1
        else:
            tailsDown += 1

        highestY = nodesTail.getLineY(nodesTail.numberOfLine) - DISTANCE_TO_DRAW_COMPOSED_TAIL - \
                   amountOfLinesBetweenNodes * DISTANCE_BEETWEN_COMPOSED_TAILS

        while node1.composedWithRight is not None:
            node1 = node1.composedWithRight
            nodesTail = node1
            amountOfLinesBetweenNodes = node1.scanvas.notes[node1.path][3]
            nodeLowestY = nodesTail.getLineY(nodesTail.numberOfLine) + DISTANCE_TO_DRAW_COMPOSED_TAIL + \
                          amountOfLinesBetweenNodes * DISTANCE_BEETWEN_COMPOSED_TAILS  # lowestY means that this y has bigger y coordinate
            lowestY = nodeLowestY if nodeLowestY > lowestY else lowestY

            while nodesTail.accordedWithUp is not None:
                if nodesTail.numberOfLine < 11:
                    tailsDown += 1
                else:
                    tailsUp += 1
                nodesTail = nodesTail.accordedWithUp
            if nodesTail.tailUp:
                tailsUp += 1
            else:
                tailsDown += 1

            nodeHighestY = nodesTail.getLineY(nodesTail.numberOfLine) - DISTANCE_TO_DRAW_COMPOSED_TAIL - \
                           amountOfLinesBetweenNodes * DISTANCE_BEETWEN_COMPOSED_TAILS
            highestY = nodeHighestY if nodeHighestY < highestY else highestY

        node1 = self if self.numberInLine < node.numberInLine else node

        while node1.composedWithLeft is not None:
            node1 = node1.composedWithLeft
            nodesTail = node1
            amountOfLinesBetweenNodes = node1.scanvas.notes[node1.path][3]
            nodeLowestY = nodesTail.getLineY(nodesTail.numberOfLine) + DISTANCE_TO_DRAW_COMPOSED_TAIL + \
                          amountOfLinesBetweenNodes * DISTANCE_BEETWEN_COMPOSED_TAILS  # lowestY means that this y has bigger y coordinate
            lowestY = nodeLowestY if nodeLowestY > lowestY else lowestY

            while nodesTail.accordedWithUp is not None:
                if nodesTail.numberOfLine < 11:
                    tailsDown += 1
                else:
                    tailsUp += 1
                nodesTail = nodesTail.accordedWithUp
            if nodesTail.tailUp:
                tailsUp += 1
            else:
                tailsDown += 1

            nodeHighestY = nodesTail.getLineY(nodesTail.numberOfLine) - DISTANCE_TO_DRAW_COMPOSED_TAIL - \
                           amountOfLinesBetweenNodes * DISTANCE_BEETWEN_COMPOSED_TAILS
            highestY = nodeHighestY if nodeHighestY < highestY else highestY

        if tailsUp < tailsDown:
            while node1.composedWithRight is not None:
                node1.delComposeWithRight()
                node1.drawComposeWithRightDown(lowestY)
                node1 = node1.composedWithRight
            node1.drawComposedTailsDown(lowestY)

        else:
            while node1.composedWithRight is not None:
                node1.delComposeWithRight()
                node1.drawComposeWithRightUp(highestY)
                node1 = node1.composedWithRight
            node1.drawComposedTailsUp(highestY)


