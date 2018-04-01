from tkinter import *
from ScrollableCanvas import ScrollableCanvas
from ButtonsPanel import ButtonsPanel
import xml.etree.ElementTree
e = xml.etree.ElementTree.parse('config').getroot()
BG_COLOR = e.find('bgColor').text

root = Tk()
root.title("Головне меню")
root.resizable(width=True, height=True)
canvas = ScrollableCanvas(root).pack(fill="both", expand=True, side=RIGHT)
buttons = ButtonsPanel(root).pack(fill="both", expand=False, side=LEFT)
root.mainloop()
