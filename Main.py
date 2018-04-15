import tkinter as tk
from ScrollableCanvas import ScrollableCanvas
from ButtonsPanel import ButtonsPanel
import xml.etree.ElementTree
e = xml.etree.ElementTree.parse('config').getroot()
BG_COLOR = e.find('bgColor').text


class Main:

    def __init__(self):
        root = tk.Tk()
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open)
        filemenu.add_command(label="Save", command=self.save)
        filemenu.add_command(label="Close", command=self.close)
        menubar.add_cascade(label="File", menu=filemenu)
        root.config(menu=menubar)
        root.title("Головне меню")
        root.resizable(width=True, height=True)

        self.buttons = ButtonsPanel(root)
        self.buttons.pack(fill="both", expand=False, side=tk.LEFT)
        self.canvas = ScrollableCanvas(root, self.buttons).pack(fill="both", expand=True, side=tk.RIGHT)
        root.mainloop()

    def open(self):
        pass

    def save(self):
        pass

    def edit(self):
        pass

    def close(self):
        pass


if __name__ == '__main__':
    Main()
