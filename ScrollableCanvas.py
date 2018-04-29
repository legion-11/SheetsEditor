import tkinter as tk
from Row import Row
from PathToImage import batchResize, rests, barlines, modifications, startRowSigns
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


class ScrollableCanvas(tk.Frame):
    rows = []
    activeNode = None
    notes = {
        'assets/notes/breve.png':              ['assets/heads/breve.png', None, None],
        'assets/notes/whole note.png':         ['assets/heads/whole note.png', None, None],
        'assets/notes/half note.png':          ['assets/heads/unfilled.png', 'assets/tails/untailed.png', 'assets/tails/untailed down.png'],
        'assets/notes/quarter note.png':       ['assets/heads/filled.png', 'assets/tails/untailed.png', 'assets/tails/untailed down.png'],
        'assets/notes/eighth note.png':        ['assets/heads/filled.png', 'assets/tails/eighth tail.png', 'assets/tails/eighth tail down.png'],
        'assets/notes/sixteenth note.png':     ['assets/heads/filled.png', 'assets/tails/sixteenth tail.png', 'assets/tails/sixteenth tail down.png'],
        'assets/notes/thirty-second note.png': ['assets/heads/filled.png', 'assets/tails/thirty-second tail.png', 'assets/tails/thirty-second tail down.png'],
        'assets/notes/sixty-fourth note.png':  ['assets/heads/filled.png', 'assets/tails/sixty-fourth tail.png', 'assets/tails/sixty-fourth tail down.png'],
        'assets/notes/one hundred twenty-eighth note.png': ['assets/heads/filled.png', 'assets/tails/one hundred twenty-eighth tail.png', 'assets/tails/one hundred twenty-eighth tail down.png']
    }

    rests = {}

    barlines = {}

    modifications = {}

    startRowSigns = {}

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
        root.bind("<space>", self.delete)  # change to "<Button-3>" later

        self.canvas.bind("<Motion>", self.aiming)

    # move
    def move_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def move_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def mouce_click(self, event):
        """temporary class to operate clicks"""
        if event.num == 1:  # click <Button-1>
            if self.activeNode is not None:
                self.activeNode.drawObj(self.panel.getPathToImage())

        elif event.num == 3:  # click <Button-3>
            self.createRows()

    def delete(self, event):
        if self.activeNode is not None:
            self.activeNode.delImages()

    def aiming(self, event):
        collisions = [row.isCollision(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)) for row in self.rows]
        if collisions != [None] * len(collisions):
            if self.activeNode is not None:
                self.activeNode.hidePoint()
            num = [isinstance(item, list) for item in collisions].index(True)
            self.activeNode = self.rows[num].lines[collisions[num][0]].nodes[collisions[num][1]]
            self.activeNode.drawPoint()

    def createRows(self):
        if len(self.rows) == 0:
            self.rows.append(Row(START_Y, len(self.rows), self))
        else:
            if self.rows[-1].y < CANVAS_HEIGH - 2 * DISTANCE_BETWEEN_LINES * 27:
                self.rows.append(Row(self.rows[-1].y + DISTANCE_BETWEEN_LINES * 27, len(self.rows), self))
        self.rows[-1].draw()

