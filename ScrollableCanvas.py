import tkinter as tk
from Row import Row
import xml.etree.ElementTree
e = xml.etree.ElementTree.parse('config').getroot()
HEIGH = e.find('canvasHeigh').text
WIDTH = e.find('canvasWidth').text
BG_COLOR = e.find('bgColor').text


class ScrollableCanvas(tk.Frame):
    rows = []

    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGH, background=BG_COLOR)
        self.xsb = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.ysb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.ysb.set, xscrollcommand=self.xsb.set)
        self.canvas.configure(scrollregion=(0, 0, WIDTH, HEIGH))

        self.xsb.grid(row=1, column=0, sticky="ew")
        self.ysb.grid(row=0, column=1, sticky="ns")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # This is what enables using the mouse:
        self.canvas.bind("<ButtonPress-2>", self.move_start)
        self.canvas.bind("<B2-Motion>", self.move_move)

        self.canvas.bind("<Button-1>", self.mouce_click)
        self.canvas.bind("<Button-3>", self.mouce_click, '+')

    # move
    def move_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def move_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def mouce_click(self, event):
        print(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        """temporary class to operate clicks"""
        if event.num == 1:  # click <Button-1>
            collisions = [row.isCollision(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)) for row in self.rows]
            print(collisions)
            if collisions != [None] * len(collisions):
                num = [isinstance(item, list) for item in collisions].index(True)
                print(num)
                print(collisions[num][0])
                print(collisions[num][1])
                self.rows[num].lines[collisions[num][0]].nodes[collisions[num][1]].change()

        elif event.num == 3:  # click <Button-3>
            self.rows.append(Row(event.y, self.canvas))
            self.rows[-1].draw()


if __name__ == "__main__":
    root = tk.Tk()
    a = ScrollableCanvas(root).pack(fill="both", expand=False)
    root.mainloop()