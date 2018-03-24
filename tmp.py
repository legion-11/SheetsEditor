from tkinter import *
from Row import Row
import xml.etree.ElementTree
e = xml.etree.ElementTree.parse('config').getroot()
HEIGH = e.find('canvasHeigh').text
WIDTH = e.find('canvasWidth').text
BG_COLOR = e.find('bgColor').text


def mouce_click(event):
    """temporary class to operate clicks"""
    if event.num == 1:  # click <Button-1>
        colisions = [row.isCollision(event.x, event.y) for row in rows]
        print(colisions)
        if colisions != [None]*len(colisions):
            num = [isinstance(item, list) for item in colisions].index(True)
            print(num)
            print(colisions[num][0])
            print(colisions[num][1])
            rows[num].lines[colisions[num][0]].nodes[colisions[num][1]].change()

    elif event.num == 3:  # click <Button-3>
        rows.append(Row(event.y, canvas))
        rows[-1].draw()

rows =[]


root = Tk()
root.title("Головне меню")
root.resizable(width=True, height=True)
canvas = Canvas(root, heigh=HEIGH, width=WIDTH, bg=BG_COLOR)
canvas.pack()
canvas.bind("<Button-1>", mouce_click)
canvas.bind("<Button-3>", mouce_click, '+')
root.mainloop()