import tkinter as tk
from tkinter import messagebox
from pickle import dump, load
from ScrollableCanvas import ScrollableCanvas
from ButtonsPanel import ButtonsPanel
import xml.etree.ElementTree
e = xml.etree.ElementTree.parse('config').getroot()
BG_COLOR = e.find('bgColor').text
START_Y = int(e.find('startRowY').text)
DISTANCE_BETWEEN_LINES = float(e.find('distanceBetweenLines').text)


class Main:

    def __init__(self):
        self.root = tk.Tk()
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open)
        filemenu.add_command(label="Save", command=self.save)
        filemenu.add_command(label="Close", command=self.close)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)
        self.root.title("Головне меню")
        self.root.resizable(width=True, height=True)

        self.buttons = ButtonsPanel(self.root)
        self.buttons.pack(fill="both", expand=False, side=tk.LEFT)
        self.scanvas = ScrollableCanvas(self.root, self.buttons)
        self.scanvas.pack(fill="both", expand=True, side=tk.RIGHT)
        self.root.mainloop()

    def open(self, file=r"file1.txt"):
        for i in self.scanvas.rows:
            i.hide()
        self.scanvas.rows.clear()
        with open(file, "rb") as fileR:
            data = load(fileR)
        for row in range(len(data)):
            self.scanvas.createRows()
            for line in range(len(data[row])):
                for node in range(len(data[row][line])):
                    self.scanvas.rows[row].lines[line].nodes[node].drawObj(data[row][line][node])

    def save(self, file=r"file1.txt"):
        data = []
        for i in self.scanvas.rows:
            data.append([])
            for j in i.lines:
                data[-1].append([])
                for k in j.nodes:
                    data[-1][-1].append(k.path)
        with open(file, "wb") as fileW:
            dump(data, fileW)

    def edit(self):
        pass

    def close(self):
        if messagebox.askyesno("EXOT?", "EXOT?"):
            self.root.destroy()


if __name__ == '__main__':
    Main()
