from tkinter import *
from Node import Node
import xml.etree.ElementTree
e = xml.etree.ElementTree.parse('config').getroot()
HEIGH = e.find('heigh').text
WIDTH = e.find('width').text
BG_COLOR = e.find('bgColor').text


def mouce_click(event):

    if event.num == 1:
        colisions = [node.is_collision(event.x, event.y) for node in nodes]
        if True not in colisions:
            nodes.append(Node(event.x, event.y, canvas=canvas))
            nodes[-1].draw()
        else:
            nodes.pop(colisions.index(True)).hide()

nodes = []


root = Tk()
root.title("Головне меню")
root.resizable(width=False, height=False)
canvas = Canvas(root, heigh=HEIGH, width=WIDTH, bg=BG_COLOR)
canvas.pack()
canvas.bind("<Button-1>", mouce_click)
root.mainloop()