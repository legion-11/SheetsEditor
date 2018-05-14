import tkinter as tk
from Row import Row
from PathToImage import batchResize, rests, barlines, modifications, startRowSigns, temp, time
import xml.etree.ElementTree
e = xml.etree.ElementTree.parse('config').getroot()
HEIGH = e.find('Heigh').text
WIDTH = e.find('Width').text
CANVAS_HEIGH = int(e.find('canvasHeigh').text)
CANVAS_WIDTH = int(e.find('canvasWidth').text)

NOTES_HEIGH = int(e.find('notesHeigh').text)
NOTES_WIDTH = int(e.find('notesWidth').text)

RESTS_HEIGH = int(e.find('restsHeigh').text)
RESTS_WIDTH = int(e.find('restsWidth').text)

BARS_HEIGH = int(e.find('barlinesHeigh').text)
BARS_WIDTH = int(e.find('barlinesWidth').text)

MODS_HEIGH = int(e.find('modificationsHeigh').text)
MODS_WIDTH = int(e.find('modificationsWidth').text)

START_ROW_HEIGH = int(e.find('startRowSignsHeigh').text)
START_ROW_WIDTH = int(e.find('startRowSignsWidth').text)

BG_COLOR = e.find('bgColor').text
DISTANCE_BETWEEN_LINES = float(e.find('distanceBetweenLines').text)

START_Y = int(e.find('startRowY').text)

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
