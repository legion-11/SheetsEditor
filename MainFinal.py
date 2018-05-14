import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog, Entry, Toplevel, Canvas, Button, StringVar
from pickle import dump, load
from PIL import Image, ImageTk
import xml.etree.ElementTree
e = xml.etree.ElementTree.parse('config').getroot()
BUTTON_WIDTH = int(e.find('buttonWidth').text)
BUTTON_HEIGH = int(e.find('buttonHeigh').text)


class ButtonsPanel(tk.Frame):
    """menu class that handle buttons"""
    images = []
    pathToImageToPaste = None
    numerator = '4'
    denominator = '4'

    def __init__(self, root, main):
        tk.Frame.__init__(self, root, width=BUTTON_WIDTH*2+5)
        self.root = root
        self.main = main
        for i in ColPath:
            self.images.append(batchResize(i, BUTTON_WIDTH, BUTTON_HEIGH))
        self.columns = [ttk.Button(self, image=self.images[i], command=lambda i=i: self.btnPressed(i))
                        for i in range(len(self.images))]
        [self.columns[i].grid(row=i if i < len(startRowSigns + time + modifications + temp + barlines)
                              else i - len(startRowSigns + time + modifications + temp + barlines),
                              column=0 if i < len(startRowSigns + time + modifications + temp + barlines)
                              else 1) for i in range(len(self.columns))]

    def btnPressed(self, index):
        """press one button and unpress another"""
        for btn in self.columns:
            if str(btn['state']) == 'disabled':
                btn.configure(state='normal')
        self.columns[index].configure(state='disabled')
        self.pathToImageToPaste = ColPath[index]
        if self.pathToImageToPaste == r'assets/startrowsigns/common time.png':
            Temp(self.root, self)
        self.main.scanvas.nodeForCompose, self.main.scanvas.nodeForSlur = None, None

    def getPathToImage(self):
        """return path to image of pressed button"""
        return self.pathToImageToPaste


LINE_PAD_X = float(e.find('linePadx').text)
LINE_START_POINT_FOR_NODES = float(e.find('lineStartPointForNodes').text)
LINE_END_POINT_FOR_NODES = float(e.find('lineEndPointForNodes').text)
LINE_COLOR = e.find('lineColor').text
WIDTH = float(e.find('canvasWidth').text)
AMOUNT_OF_TIME_IN_ROW = int(e.find('amountOfTimeInRow').text)
AMOUNT_OF_NODE_IN_TIME = int(e.find('amountOfNodeInTime').text)
DISTANCE_BETWEEN_LINES = float(e.find('distanceBetweenLines').text)


class Line:
    """class that represent collection of nodes"""
    def __init__(self, y, numberOfLine, numberOfRow, scanvas, transparent):
        """
        @:param y - y coordinate of horizontal line
        @:param transparent - if it's True line don't draw
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
        print(type(LINE_PAD_X), type(LINE_START_POINT_FOR_NODES),type(WIDTH),type(LINE_PAD_X), type(LINE_START_POINT_FOR_NODES), type(LINE_END_POINT_FOR_NODES))
        self.nodes = [Node(LINE_PAD_X + LINE_START_POINT_FOR_NODES +
                           i * ((WIDTH - LINE_PAD_X - LINE_START_POINT_FOR_NODES - LINE_END_POINT_FOR_NODES) / (AMOUNT_OF_TIME_IN_ROW * AMOUNT_OF_NODE_IN_TIME)),
                           self.y, i, self.numberOfLine, self.numberOfRow, self.scanvas) for i in range(AMOUNT_OF_TIME_IN_ROW * AMOUNT_OF_NODE_IN_TIME)]

    def draw(self):
        """draw line"""
        if self.transparent is False:
            self.line = self.scanvas.canvas.create_line(LINE_PAD_X, self.y, WIDTH - LINE_PAD_X, self.y, fill=LINE_COLOR)

    def hide(self):
        """del Line and hide Nodes"""
        self.scanvas.canvas.delete(self.line)
        [node.delImages() for node in self.nodes]

    def isCollision(self, eveX, eveY):
        """
        return list with [index of Line, index of Node] that was clicked on
        return None if click was far
        """
        if self.y-DISTANCE_BETWEEN_LINES <= eveY <= self.y+DISTANCE_BETWEEN_LINES:  # check if click was near line
            for node in self.nodes:
                if node.isCollision(eveX, eveY):
                    return [self.numberOfLine, node.numberInLine]


SHIFT = int(e.find('shift').text)


class Link:
    """slur class"""
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
        """draw line(slur)"""
        self.line = self.scanvas.canvas.create_line(self.createPoints())

    def delete(self):
        """delate slur"""
        self.scanvas.canvas.delete(self.line)
        self.line = None
        if self.node1 is not None:
            self.node1.link = None
        if self.node2 is not None:
            self.node2.link = None
        del self

    def createPoints(self):
        """creates points of slur parabola"""
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


BG_COLOR = e.find('bgColor').text
START_Y = int(e.find('startRowY').text)


class Main:
    """main class that handle menu and another classes"""
    def __init__(self):
        self.root = tk.Tk()
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open)
        filemenu.add_command(label="Save", command=self.save)
        filemenu.add_command(label="Close", command=self.close)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)
        self.root.title("Головне меню")
        self.root.resizable(width=True, height=True)

        self.buttons = ButtonsPanel(self.root, self)
        self.buttons.pack(fill="both", expand=False, side=tk.LEFT)
        self.scanvas = ScrollableCanvas(self.root, self.buttons)
        self.scanvas.pack(fill="both", expand=True, side=tk.RIGHT)
        self.root.mainloop()

    def open(self):
        if self.scanvas.activeNode is not None:
            self.scanvas.activeNode.hidePoint()
        file = filedialog.askopenfilename(initialdir=r"F:\GitHub\SheetsEditor\Save dir", title="Select file",
                                                   filetypes=(("SheetsEditor files", "*.she"), ("all files", "*.*")))
        try:
            with open(file, "rb") as fileR:
                tmp = load(fileR)
                data = tmp['data']
                links = tmp['links']
                clefsAndTemp = tmp['clefsAndTemp']
                compose = tmp['compose']

            for i in self.scanvas.rows:
                i.hide()
            self.scanvas.rows.clear()
            self.scanvas.canvas.delete(self.scanvas.activeNode)
            self.scanvas.activeNode = None

            for row in range(len(data)):
                self.scanvas.createRows('')
                for line in range(len(data[row])):
                    for node in range(len(data[row][line])):
                        self.scanvas.rows[row].lines[line].nodes[node].drawObj(data[row][line][node])
                        if links[row][line][node] is not None:
                            self.scanvas.rows[row].lines[line].nodes[node].drawLink(
                                self.scanvas.rows[links[row][line][node][0]]
                                            .lines[links[row][line][node][1]]
                                            .nodes[links[row][line][node][2]])
            for row in range(len(data)):
                for line in range(len(data[row])):
                    for node in range(len(data[row][line])):
                        if compose[row][line][node] is not None:
                            self.scanvas.rows[row].lines[line].nodes[node].composeWith(
                                self.scanvas.rows[compose[row][line][node][0]]
                                    .lines[compose[row][line][node][1]]
                                    .nodes[compose[row][line][node][2]])

            for i in range(len(clefsAndTemp)):
                self.scanvas.rows[i].changeClef(clefsAndTemp[i][0])
                if clefsAndTemp[i][1] is not None:
                    self.scanvas.rows[i].changeTemp(clefsAndTemp[i][1])
                if clefsAndTemp[i][2] is not None:
                    self.scanvas.rows[i].changeTemp(clefsAndTemp[i][2])

        except FileNotFoundError:
            pass
        except:
            pass

    def save(self):
        file = filedialog.asksaveasfilename(initialdir=r"F:\GitHub\SheetsEditor\Save dir", title="Select file",
                                             filetypes=(("SheetsEditor files", "*.she"), ("all files", "*.*")))
        if file[-4:] != '.she':
            file += '.she'
        data = []
        links = []
        clefsAndTemp = []
        compose = []
        for i in self.scanvas.rows:
            data.append([])
            links.append([])
            compose.append([])
            for j in i.lines:
                data[-1].append([])
                links[-1].append([])
                compose[-1].append([])
                for k in j.nodes:
                    data[-1][-1].append(k.path)
                    if k.link is not None and k.link.node2 == k:
                        links[-1][-1].append(k.link.node1.getNodePosition())
                    else:
                        links[-1][-1].append(None)

                    if k.composedWithRight is not None:
                        compose[-1][-1].append(k.composedWithRight.getNodePosition())
                    else:
                        compose[-1][-1].append(None)

        for i in self.scanvas.rows:
            clefsAndTemp.append([i.pathClef, i.numeratorNum, i.denominatorNum])
        with open(file, "wb") as fileW:
            dump({'data': data, 'links': links, 'clefsAndTemp': clefsAndTemp, 'compose': compose}, fileW)

    def edit(self):
        pass

    def close(self):
        if messagebox.askyesno("EXIT?", "EXIT?"):
            self.root.destroy()


e = xml.etree.ElementTree.parse('config').getroot()
CANVAS_HEIGH = int(e.find('canvasHeigh').text)
LINE_LEN = int(e.find('notesExtraLineLen').text)
NODE_COLOR = e.find('nodeColor').text

NODE_RENDER_RADIUS = float(e.find('nodeRenderRadius').text)
NODE_WORK_RADIUS = float(e.find('nodeWorkRadius').text)

NOTES_HEIGH = int(e.find('notesHeigh').text)
NOTES_WIDTH = int(e.find('notesWidth').text)

RESTS_HEIGH = int(e.find('restsHeigh').text)
RESTS_WIDTH = int(e.find('restsWidth').text)

SHIFT_FOR_DOT = int(e.find('shiftForDot').text)

DISTANCE_BETWEN_NODES = (WIDTH - LINE_PAD_X - LINE_START_POINT_FOR_NODES - LINE_END_POINT_FOR_NODES) / (AMOUNT_OF_TIME_IN_ROW * AMOUNT_OF_NODE_IN_TIME)
SHIFT_IN_ACCORD_FOR_HEAD = int(e.find('notesShiftInAccordForHead').text)
SHIFT_IN_ACCORD_FOR_TAIL = int(e.find('notesShiftInAccordForTail').text)

DISTANCE_TO_DRAW_COMPOSED_TAIL = int(e.find('distanceToDrawComposedTail').text)
DISTANCE_BEETWEN_COMPOSED_TAILS = int(e.find('distanceBeetwenComposedTails').text)

NOTES_WITHOUT_TAIL = ['assets/notes/breve.png',
                      'assets/notes/whole note.png',
                      'assets/notes/half note.png']
LEN_SHORT_COMPOSED_LINE = int(e.find('lenShortComposedLine').text)


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
                if self.getNodeInSimilarColumn(i).path is not None:
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
        """return True if Node's path is note"""
        return self.path in self.scanvas.notes

    def drawLink(self, node):
        """create slur between this and node nodes"""
        if self.link is not None:
            self.link.delete()
        if node.link is not None:
            node.link.delete()
        node.link = self.link = Link(self.scanvas, self, node)
        self.link.draw()

    def delLink(self):
        """delete slur"""
        if self.link is not None:
            self.link.delete()

    def delImages(self):
        """delete images obj, tail, extraLines and path of Node"""
        self.path = None
        if self.obj is not None:
            self.scanvas.canvas.delete(self.obj)
            if self.dot is not None:
                self.scanvas.canvas.delete(self.dot)
            if self.tail is not None:
                self.scanvas.canvas.delete(self.tail)
                self.tailUp = None
                if self.hasCompose():
                    if self.accordedWithUp is not None:
                        if self.composedWithRight is not None:
                            self.delComposeWithRight()
                            self.accordedWithUp.accordedWithDown = None
                            self.composedWithRight.composedWithLeft = None
                            self.accordedWithUp.composeWith(self.composedWithRight)

                        if self.composedWithLeft is not None:
                            self.delComposeWithLeft()
                            self.accordedWithUp.accordedWithDown = None
                            self.composedWithLeft.composedWithRight = None
                            self.accordedWithUp.composeWith(self.composedWithLeft)

                    elif self.composedWithRight is not None and self.composedWithLeft is not None:
                        self.delComposeWithLeft()
                        self.delComposeWithRight()
                        self.composedWithRight.composeWith(self.composedWithLeft)
                    elif self.composedWithRight is None:
                        if self.composedWithLeft.composedWithLeft is not None:
                            self.delComposeWithLeft()
                            self.composedWithLeft.composedWithRight = None
                            self.composedWithLeft = None
                        else:
                            self.delComposeWithLeft()
                            self.composedWithLeft.composedWithRight = None
                            self.composedWithLeft.drawObj(self.composedWithLeft.path)
                            self.composedWithLeft = None

                    else:
                        if self.composedWithRight.composedWithRight is not None:
                            self.delComposeWithRight()
                            self.composedWithRight.composedWithLeft = None
                            self.composedWithRight = None
                        else:
                            self.delComposeWithRight()
                            self.composedWithRight.composedWithLeft = None
                            self.composedWithRight.drawObj(self.composedWithRight.path)
                            self.composedWithRight = None

                else:
                    if self.accordedWithDown is not None and self.accordedWithUp is not None:
                        self.accordedWithUp.composedWithDown = self.accordedWithDown
                        self.accordedWithDown.composedWithUp = self.accordedWithUp
                        self.accordedWithUp.drawObj(self.accordedWithUp.path)
                        self.accordedWithDown = None
                        self.accordedWithUp = None
                    elif self.accordedWithUp is not None and self.accordedWithDown is None:
                        self.accordedWithUp.composedWithDown = None
                        self.accordedWithUp.drawObj(self.accordedWithUp.path)
                        self.accordedWithUp = None
                    elif self.accordedWithUp is None and self.accordedWithDown is not None:
                        self.accordedWithDown.composedWithUp = None
                        self.accordedWithDown.drawObj(self.accordedWithDown.path)
                        self.accordedWithDown = None

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

        elif len(self.scanvas.rows) > self.numberOfRow and self.scanvas.rows[self.numberOfRow].lines[10].nodes[self.numberInLine].isRested():
            self.scanvas.rows[self.numberOfRow].lines[10].nodes[self.numberInLine].delImages()

    def getNodePosition(self) -> list:
        """return list of numberOfRow, numberOfLine, numberInLine"""
        return [self.numberOfRow, self.numberOfLine, self.numberInLine]

    def drawNote(self, path):
        """draw note"""
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
                else:
                    self.path = None
                    return
            elif self.getNodeInSimilarColumn(i).path in self.scanvas.modifications:
                self.path = None
                return

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
                else:
                    self.path = None
                    return

            elif self.getNodeInSimilarColumn(i).path in self.scanvas.modifications:
                self.path = None
                return

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
        """draw tails of accord down"""
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
        """draw tails of accord up"""
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

    def addExtraLine(self):
        """draw small line across node"""
        if self.extraLine is None:
            self.extraLine = self.scanvas.canvas.create_line(self.x-LINE_LEN, self.y, self.x+LINE_LEN, self.y, fill=LINE_COLOR)

    def dotNote(self):
        """draw small point near note"""
        if self.path in self.scanvas.notes:
            self.dot = self.scanvas.canvas.create_image(self.x, self.y, image=self.scanvas.dot['assets/temp/dot.png'])

    def delDot(self):
        if self.dot is not None:
            self.scanvas.canvas.delete(self.dot)
            self.dot = None

    def hasCompose(self):
        """return True if Node is composed with some node"""
        if self.composedWithLeft is not None or self.composedWithRight is not None:
            return True
        else:
            return False

    def getNodeInSimilarColumn(self, NumberOfLine: int):
        """return node in the similar column by the number of line"""
        return self.scanvas.rows[self.numberOfRow].lines[NumberOfLine].nodes[self.numberInLine]

    def getHighestLineOfAccord(self):
        """return highest line (has lowest number)"""
        node = self
        while node.accordedWithUp is not None:
            node = node.accordedWithUp
        return node.numberOfLine

    def getLowestLineOfAccord(self):
        """return lowest line of accord (has biggest number)"""
        node = self
        while node.accordedWithDown is not None:
            node = node.accordedWithDown
        return node.numberOfLine

    def getLineY(self, numberOfLine):
        """return y coordinate of line by number of line"""
        return int(self.scanvas.rows[self.numberOfRow].lines[numberOfLine].y)

    def delComposeWithLeft(self):
        """delate compose tails beetwen this node and left"""
        if self.composedWithLeft is not None:
            self.composedWithLeft.delComposeWithRight()

    def delComposeWithRight(self):
        """delate compose tails beetwen this node and  right"""
        if self.composedWithRight is not None:
            for i in range(len(self.composeLinesRight)-1, -1, -1):
                self.scanvas.canvas.delete(self.composeLinesRight.pop(i))

    def drawComposeWithRightDown(self, lowestY):
        """draw tails down and conect them with composed line"""
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
                    for i in range(min(amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2), min(amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2) +
                                   max(amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2) - min(
                                       amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2)):
                        self.composeLinesRight.append(self.scanvas.canvas.create_line(self.x - SHIFT_IN_ACCORD_FOR_TAIL,
                                                                                      lowestY - i * DISTANCE_BEETWEN_COMPOSED_TAILS,
                                                                                      self.x - SHIFT_IN_ACCORD_FOR_TAIL + LEN_SHORT_COMPOSED_LINE,
                                                                                      lowestY - i * DISTANCE_BEETWEN_COMPOSED_TAILS,
                                                                                      width=3))
                else:
                    for i in range(min(amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2),
                                   min(amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2) +
                                           max(amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2) - min(
                                       amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2)):
                        self.composeLinesRight.append(
                            self.scanvas.canvas.create_line(self.composedWithRight.x - SHIFT_IN_ACCORD_FOR_TAIL,
                                                            lowestY - i * DISTANCE_BEETWEN_COMPOSED_TAILS,
                                                            self.composedWithRight.x - SHIFT_IN_ACCORD_FOR_TAIL - LEN_SHORT_COMPOSED_LINE,
                                                            lowestY - i * DISTANCE_BEETWEN_COMPOSED_TAILS,
                                                            width=3))
                self.drawComposedTailsDown(lowestY)

    def drawComposedTailsDown(self, lowestY):
        """draw tails down to the lowestY coordinate of lowest composed line"""
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
        """draw tails up and connect them with composed line"""
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
                                   min(amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2) +
                                           max(amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2) - min(
                                       amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2)):

                        self.composeLinesRight.append(self.scanvas.canvas.create_line(self.x + SHIFT_IN_ACCORD_FOR_TAIL,
                                                                                      highestY + i * DISTANCE_BEETWEN_COMPOSED_TAILS,
                                                                                      self.x + SHIFT_IN_ACCORD_FOR_TAIL + LEN_SHORT_COMPOSED_LINE,
                                                                                      highestY + i * DISTANCE_BEETWEN_COMPOSED_TAILS,
                                                                                      width=3))
                else:
                    for i in range(min(amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2),
                                   min(amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2) +
                                           max(amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2) - min(
                                       amounOfLinesBetweenNodes1, amounOfLinesBetweenNodes2)):
                        self.composeLinesRight.append(self.scanvas.canvas.create_line(self.composedWithRight.x + SHIFT_IN_ACCORD_FOR_TAIL,
                                                                                      highestY + i * DISTANCE_BEETWEN_COMPOSED_TAILS,
                                                                                      self.composedWithRight.x + SHIFT_IN_ACCORD_FOR_TAIL - LEN_SHORT_COMPOSED_LINE,
                                                                                      highestY + i * DISTANCE_BEETWEN_COMPOSED_TAILS,
                                                                                      width=3))
                self.drawComposedTailsUp(highestY)

    def drawComposedTailsUp(self, highestY):
        """draw tails down to the highestY coordinate of highest composed line"""
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
        """create composition between this node and node"""
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


def batchResize(image, width, height):
    if image is not None:
        resized = Image.open(image).resize((width, height), Image.ANTIALIAS)
        return ImageTk.PhotoImage(resized)


startRowSigns = [r'assets/startrowsigns/g clef.png',
                 r'assets/startrowsigns/f clef.png']

time = [r'assets/startrowsigns/common time.png']

barlines = ['assets/barlines/single barline.png',
            'assets/barlines/final barline.png',
            'assets/barlines/left repeat sign.png',
            'assets/barlines/right repeat sign.png']

modifications = ['assets/modifications/double flat.png',
                 'assets/modifications/double sharp.png',
                 'assets/modifications/flat.png',
                 'assets/modifications/natural.png',
                 'assets/modifications/sharp.png']
temp = ['assets/temp/dotnote.png',
        'assets/temp/slur.png',
        #'assets/temp/staccato.png',
        'assets/temp/compose.png']

aboveSigns = ['assets/abovesigns/fermata .png']

rests = ['assets/rests/multi rest.png',
         'assets/rests/whole rest.png',
         'assets/rests/half rest.png',
         'assets/rests/quarter rest.png',
         'assets/rests/eighth rest.png',
         'assets/rests/sixteenth rest.png',
         'assets/rests/thirty-second rest.png',
         'assets/rests/sixty-fourth rest.png',
         'assets/rests/one hundred twenty-eighth rest.png']

notes = ['assets/notes/breve.png',
         'assets/notes/whole note.png',
         'assets/notes/half note.png',
         'assets/notes/quarter note.png',
         'assets/notes/eighth note.png',
         'assets/notes/sixteenth note.png',
         'assets/notes/thirty-second note.png',
         'assets/notes/sixty-fourth note.png',
         'assets/notes/one hundred twenty-eighth note.png']

ColPath = startRowSigns + time + barlines + modifications + temp + rests + notes

heads = ['assets/heads/breve.png',
         'assets/heads/filled.png',
         'assets/heads/unfilled.png',
         'assets/heads/whole note.png']

tails = ['assets/tails/eighth tail.png',
         'assets/tails/one hundred twenty-eighth tail.png',
         'assets/tails/sixteenth tail.png',
         'assets/tails/sixty-fourth tail.png',
         'assets/tails/thirty-second tail.png',
         'assets/tails/untailed.png']


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


HEIGH = e.find('Heigh').text
CANVAS_WIDTH = int(e.find('canvasWidth').text)


BARS_HEIGH = int(e.find('barlinesHeigh').text)
BARS_WIDTH = int(e.find('barlinesWidth').text)

MODS_HEIGH = int(e.find('modificationsHeigh').text)
MODS_WIDTH = int(e.find('modificationsWidth').text)

START_ROW_HEIGH = int(e.find('startRowSignsHeigh').text)
START_ROW_WIDTH = int(e.find('startRowSignsWidth').text)


AMOUNT_OF_TIME_IN_ROW = int(e.find('amountOfTimeInRow').text)
AMOUNT_OF_NODE_IN_TIME = int(e.find('amountOfNodeInTime').text)


class ScrollableCanvas(tk.Frame):
    """canvas that handle images of notes, can draw images, notes, etc"""
    rows = []
    activeNode = None
    notes = {
        'assets/notes/breve.png':              ['assets/heads/breve.png', None, None, 0],
        'assets/notes/whole note.png':         ['assets/heads/whole note.png', None, None, 0],
        'assets/notes/half note.png':          ['assets/heads/unfilled.png', 'assets/tails/untailed.png', 'assets/tails/untailed down.png', 0],
        'assets/notes/quarter note.png':       ['assets/heads/filled.png', 'assets/tails/untailed.png', 'assets/tails/untailed down.png', 0],
        'assets/notes/eighth note.png':        ['assets/heads/filled.png', 'assets/tails/eighth tail.png', 'assets/tails/eighth tail down.png', 1],
        'assets/notes/sixteenth note.png':     ['assets/heads/filled.png', 'assets/tails/sixteenth tail.png', 'assets/tails/sixteenth tail down.png', 2],
        'assets/notes/thirty-second note.png': ['assets/heads/filled.png', 'assets/tails/thirty-second tail.png', 'assets/tails/thirty-second tail down.png', 3],
        'assets/notes/sixty-fourth note.png':  ['assets/heads/filled.png', 'assets/tails/sixty-fourth tail.png', 'assets/tails/sixty-fourth tail down.png', 4],
        'assets/notes/one hundred twenty-eighth note.png': ['assets/heads/filled.png', 'assets/tails/one hundred twenty-eighth tail.png', 'assets/tails/one hundred twenty-eighth tail down.png', 5]
    }

    rests = {}

    barlines = {}

    modifications = {}

    startRowSigns = {}

    dot = {}

    nodeForSlur = None  # Node for creation Links between this Node and another

    nodeForCompose = None

    def __init__(self, root, panel):
        tk.Frame.__init__(self, root, width=WIDTH, height=HEIGH)
        self.panel = panel
        for k, v in self.notes.items():
            self.notes[k][0] = batchResize(self.notes[k][0], NOTES_WIDTH, NOTES_HEIGH)
            self.notes[k][1] = batchResize(self.notes[k][1], NOTES_WIDTH, NOTES_HEIGH)
            self.notes[k][2] = batchResize(self.notes[k][2], NOTES_WIDTH, NOTES_HEIGH)
        for i in rests:
            self.rests.update([[i, batchResize(i, RESTS_WIDTH, RESTS_HEIGH)]])
        for i in barlines:
            self.barlines.update([[i, batchResize(i, BARS_WIDTH, BARS_HEIGH)]])
        for i in modifications:
            self.modifications.update([[i, batchResize(i, MODS_WIDTH, MODS_HEIGH)]])
        for i in startRowSigns:
            self.startRowSigns.update([[i, batchResize(i, START_ROW_WIDTH, START_ROW_HEIGH)]])
        self.dot.update([['assets/temp/dot.png', batchResize('assets/temp/dot.png', NOTES_WIDTH, NOTES_HEIGH)]])

        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGH, background=BG_COLOR)
        self.xsb = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.ysb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.ysb.set, xscrollcommand=self.xsb.set)
        self.canvas.configure(scrollregion=(0, 0, CANVAS_WIDTH, CANVAS_HEIGH))

        self.xsb.grid(row=1, column=0, sticky="ew")
        self.ysb.grid(row=0, column=1, sticky="ns")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # This is what enables using the mouse:
        self.canvas.bind("<ButtonPress-2>", self.move_start)
        self.canvas.bind("<B2-Motion>", self.move_move)

        self.canvas.bind("<Button-1>", self.mouce_click)
        self.canvas.bind("<Button-3>", self.mouce_click, '+')

        root.bind("<space>", self.createRows)
        root.bind('<d>', self.shiftActiveNode)
        root.bind('<s>', self.shiftActiveNode)
        root.bind('<w>', self.shiftActiveNode)
        root.bind('<a>', self.shiftActiveNode)
        root.bind('<Return>', self.draw)
        root.bind('<BackSpace>', self.delete)
        root.bind('<Delete>', self.delete)
        root.bind('<Down>', self.delSlur)
        root.bind('<Right>', self.delDot)
        root.bind('<Up>', self.delCompose)
        root.bind('<r>', self.delRow)
        root.bind('<Left>', self.delTemp)

        self.canvas.bind("<Motion>", self.aiming)

    # move
    def move_start(self, event):
        """start point of moving"""
        self.canvas.scan_mark(event.x, event.y)

    def move_move(self, event):
        """drag canvas """
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def draw(self, event):
        if self.activeNode is not None:
            if self.panel.getPathToImage() not in temp + time:
                self.activeNode.drawObj(self.panel.getPathToImage())

            elif self.panel.getPathToImage() == 'assets/temp/slur.png':
                if self.nodeForSlur is None and (self.activeNode.path in self.notes):
                    self.nodeForSlur = self.activeNode

                elif self.nodeForSlur is not None and\
                        (self.activeNode.path in self.notes) and\
                        (self.nodeForSlur.numberOfRow == self.activeNode.numberOfRow) and\
                        (self.nodeForSlur.numberInLine != self.activeNode.numberInLine):
                    self.nodeForSlur.drawLink(self.activeNode)
                    self.nodeForSlur = None

            elif self.panel.getPathToImage() == r'assets/temp/dotnote.png':
                self.activeNode.dotNote()

            elif self.panel.getPathToImage() == r'assets/temp/compose.png':
                if self.nodeForCompose is None:
                    self.nodeForCompose = self.activeNode
                else:
                    self.activeNode.composeWith(self.nodeForCompose)
                    self.nodeForCompose = self.activeNode

            elif self.panel.getPathToImage() == r'assets/startrowsigns/common time.png':
                self.rows[self.activeNode.numberOfRow].changeTemp(self.panel.numerator, self.panel.denominator)

    def delete(self, event):
        self.nodeForSlur = None
        self.nodeForCompose = None
        if self.activeNode is not None:
            self.activeNode.delImages()

    def mouce_click(self, event):
        """operate mouce clicks"""
        if event.num == 1 and self.activeNode is not None:  # click <Button-1>
            self.draw(event)

        elif event.num == 3:  # click <Button-3>
            self.delete(event)

    def delSlur(self, event):
        if self.activeNode is not None:
            self.activeNode.delLink()

    def delDot(self, event):
        if self.activeNode is not None:
            self.activeNode.delDot()

    def delRow(self, event):
        if len(self.rows) != 0:
            for i in range(23):
                for j in range(AMOUNT_OF_TIME_IN_ROW * AMOUNT_OF_NODE_IN_TIME):
                    if self.rows[-1].lines[i].nodes[j].path is not None:
                        return
            self.rows.pop(-1).hide()
            self.activeNode.hidePoint()

    def delTemp(self, event):
        if self.activeNode is not None:
            if self.rows[self.activeNode.numberOfRow].numerator is not None:
                self.canvas.delete(self.rows[self.activeNode.numberOfRow].numerator)
            if self.rows[self.activeNode.numberOfRow].denominator is not None:
                self.canvas.delete(self.rows[self.activeNode.numberOfRow].denominator)

    def delCompose(self, event):

        if self.activeNode is not None:
            self.activeNode.drawObj(self.activeNode.path)

    def shiftActiveNode(self, event):
        if event.char == 'd':
            if self.activeNode is not None and self.activeNode.numberInLine != AMOUNT_OF_TIME_IN_ROW * AMOUNT_OF_NODE_IN_TIME - 1:
                self.activeNode.hidePoint()
                pos = self.activeNode.getNodePosition()
                self.activeNode = self.rows[pos[0]].lines[pos[1]].nodes[pos[2] + 1]
                self.activeNode.drawPoint()

        elif event.char == 's':
            if self.activeNode is not None and self.activeNode.numberOfLine != 22:
                self.activeNode.hidePoint()
                self.activeNode = self.activeNode.getNodeInSimilarColumn(self.activeNode.numberOfLine + 1)
                self.activeNode.drawPoint()

            elif self.activeNode is not None and self.activeNode.numberOfRow != self.rows[-1].numberOfRow:
                print(self.activeNode.numberOfRow, self.rows[-1].numberOfRow)
                self.activeNode.hidePoint()
                pos = self.activeNode.getNodePosition()
                self.activeNode = self.rows[pos[0] + 1].lines[0].nodes[pos[2]]
                self.activeNode.drawPoint()

        elif event.char == 'a':
            if self.activeNode is not None and self.activeNode.numberInLine != 0:
                self.activeNode.hidePoint()
                pos = self.activeNode.getNodePosition()
                self.activeNode = self.rows[pos[0]].lines[pos[1]].nodes[pos[2] - 1]
                self.activeNode.drawPoint()

        elif event.char == 'w':
            if self.activeNode is not None and self.activeNode.numberOfLine != 0:
                self.activeNode.hidePoint()
                self.activeNode = self.activeNode.getNodeInSimilarColumn(self.activeNode.numberOfLine - 1)
                self.activeNode.drawPoint()

            elif self.activeNode is not None and self.activeNode.numberOfRow != self.rows[0].numberOfRow:
                self.activeNode.hidePoint()
                pos = self.activeNode.getNodePosition()
                self.activeNode = self.rows[pos[0] - 1].lines[22].nodes[pos[2]]
                self.activeNode.drawPoint()

    def aiming(self, event):
        """operates moving of mouce"""
        collisions = [row.isCollision(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)) for row in self.rows]
        if collisions != [None] * len(collisions):
            num = [isinstance(item, list) for item in collisions].index(True)
            if self.activeNode != self.rows[num].lines[collisions[num][0]].nodes[collisions[num][1]]:
                if self.activeNode is not None:
                    self.activeNode.hidePoint()
                self.activeNode = self.rows[num].lines[collisions[num][0]].nodes[collisions[num][1]]
                self.activeNode.drawPoint()

    def createRows(self, event, clef=r'assets/startrowsigns/g clef.png'):
        """creates rows """
        if len(self.rows) == 0:
            self.rows.append(Row(START_Y, len(self.rows), self, clef))
            self.rows[0].changeTemp(self.panel.numerator, self.panel.denominator)
        else:
            if self.rows[-1].y < CANVAS_HEIGH - 2 * DISTANCE_BETWEEN_LINES * 28:
                self.rows.append(Row(self.rows[-1].y + DISTANCE_BETWEEN_LINES * 28, len(self.rows), self, clef))
        self.rows[-1].draw()



SMALL_CANVAS_WIDTH = int(e.find('smallCanvasWidth').text)
SMALL_CANVAS_HEIGHT = int(e.find('smallCanvasHeigh').text)\


class Temp:
    denominator = 4
    imageNum = None
    imageDenum = None

    def __init__(self, root, panel):
        self.win = Toplevel(root)
        self.win.title('Temp')
        self.panel = panel
        self.smallcanvas = Canvas(self.win, width=SMALL_CANVAS_WIDTH, height=SMALL_CANVAS_HEIGHT, background=BG_COLOR)

        self.numerator = StringVar()
        self.numerator.trace('w', self.limitSize)
        self.e1 = Entry(self.win, width=2, font=("Arial", 20), textvariable=self.numerator)

        self.denominator = StringVar()
        self.denominator.trace('w', self.limitSize)
        self.e2 = Entry(self.win, width=2, font=("Arial", 20), textvariable=self.denominator)

        button = Button(self.win, text="Save", font=("Arial", 8), command=self.drawNum)

        self.e1.grid(row=0, column=0, padx=3)
        self.e2.grid(row=1, column=0)
        button.grid(row=2, column=0)
        self.smallcanvas.grid(row=0, column=1, rowspan=3)

        self.smallcanvas.create_line(SMALL_CANVAS_WIDTH//2 - SIZE_OF_NUMS // 2, SMALL_CANVAS_HEIGHT//2,
                                     SMALL_CANVAS_WIDTH // 2 + SIZE_OF_NUMS // 2 + 1, SMALL_CANVAS_HEIGHT // 2)
        self.e1.insert(0, self.panel.numerator)
        self.e2.insert(0, self.panel.denominator)
        self.drawNum()

    def drawNum(self):
        if str(self.e1.get()).isdigit() and len(self.e1.get()) == 1:
            if self.imageNum is not None:
                self.smallcanvas.delete(self.imageNum)
            self.imageNum = self.smallcanvas.create_text(SMALL_CANVAS_WIDTH//2, SMALL_CANVAS_HEIGHT//2 - SIZE_OF_NUMS,
                                         fill="black", font=("Algerian", str(SIZE_OF_NUMS)), text=self.e1.get())
            self.numerator = self.e1.get()
            self.panel.numerator = str(self.e1.get())

        if str(self.e2.get()).isdigit():
            if self.imageDenum is not None:
                self.smallcanvas.delete(self.imageDenum)
            self.imageDenum = self.smallcanvas.create_text(SMALL_CANVAS_WIDTH//2, SMALL_CANVAS_HEIGHT//2 + SIZE_OF_NUMS,
                                         fill="black", font=("Algerian", str(SIZE_OF_NUMS)), text=self.e2.get())
            self.denominator = self.e2.get()
            self.panel.denominator = str(self.e2.get())

    def limitSize(self, *args):
        if len(self.numerator.get()) > 1: self.numerator.set(self.numerator.get()[:1])
        if len(self.denominator.get()) > 1: self.denominator.set(self.numerator.get()[:2])


if __name__ == '__main__':
    Main()
