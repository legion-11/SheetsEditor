import tkinter as tk
from tkinter import ttk
from PathToImage import *
from Temp import Temp
import xml.etree.ElementTree
e = xml.etree.ElementTree.parse('config').getroot()
BUTTON_WIDTH = int(e.find('buttonWidth').text)
BUTTON_HEIGH = int(e.find('buttonHeigh').text)


class ButtonsPanel(tk.Frame):
    images = []
    pathToImageToPaste = None
    numerator = '4'
    denominator = '4'

    def __init__(self, root):
        tk.Frame.__init__(self, root, width=BUTTON_WIDTH*2+5)
        self.root = root
        for i in ColPath:
            self.images.append(batchResize(i, BUTTON_WIDTH, BUTTON_HEIGH))
        self.columns = [ttk.Button(self, image=self.images[i], command=lambda i=i: self.btnPressed(i))
                        for i in range(len(self.images))]
        [self.columns[i].grid(row=i if i < len(startRowSigns + time + modifications + temp + barlines + aboveSigns)
                              else i - len(startRowSigns + time + modifications + temp + barlines + aboveSigns),
                              column=0 if i < len(startRowSigns + time + modifications + temp + barlines + aboveSigns)
                              else 1) for i in range(len(self.columns))]

    def btnPressed(self, index):
        for btn in self.columns:
            if str(btn['state']) == 'disabled':
                btn.configure(state='normal')
        self.columns[index].configure(state='disabled')
        self.pathToImageToPaste = ColPath[index]
        if self.pathToImageToPaste == r'assets/startrowsigns/common time.png':
            Temp(self.root, self)

    def getPathToImage(self):
        return self.pathToImageToPaste







if __name__ == '__main__':
    root = tk.Tk()
    ButtonsPanel(root).pack()
    root.mainloop()