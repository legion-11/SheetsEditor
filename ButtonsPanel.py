import tkinter as tk
from tkinter import ttk
from PathToImage import *
from Temp import Temp
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
