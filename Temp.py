from tkinter import Entry, Toplevel, Canvas, Button, StringVar

import xml.etree.ElementTree
e = xml.etree.ElementTree.parse('config').getroot()

BG_COLOR = e.find('bgColor').text
SMALL_CANVAS_WIDTH = int(e.find('smallCanvasWidth').text)
SMALL_CANVAS_HEIGHT = int(e.find('smallCanvasHeigh').text)
SIZE_OF_NUMS = int(e.find('sizeOfNums').text)


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
