from tkinter import *
from Line import Line
import xml.etree.ElementTree
e = xml.etree.ElementTree.parse('config').getroot()
HEIGH = e.find('heigh').text
WIDTH = e.find('width').text
BG_COLOR = e.find('bgColor').text


def mouce_click(event):

    if event.num == 1:
        colisions = [line.isCollision(event.x, event.y) for line in lines]
        print(colisions)
        if colisions != [None]*len(colisions):
            num = [isinstance(item, int) for item in colisions].index(True)
            lines[num].nodes[colisions[num]].change()


    elif event.num == 3:
        lines.append(Line(event.y, canvas))

lines =[]


root = Tk()
root.title("Головне меню")
root.resizable(width=False, height=False)
canvas = Canvas(root, heigh=HEIGH, width=WIDTH, bg=BG_COLOR)
canvas.pack()
canvas.bind("<Button-1>", mouce_click)
canvas.bind("<Button-3>", mouce_click, '+')
root.mainloop()