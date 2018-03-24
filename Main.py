from tkinter import *
from ScrollableCanvas import ScrollableCanvas
import xml.etree.ElementTree
e = xml.etree.ElementTree.parse('config').getroot()
BG_COLOR = e.find('bgColor').text

root = Tk()
root.title("Головне меню")
root.resizable(width=True, height=True)
canvas = ScrollableCanvas(root).pack(fill="both", expand=False)

root.mainloop()