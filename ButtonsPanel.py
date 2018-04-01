import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import xml.etree.ElementTree
e = xml.etree.ElementTree.parse('config').getroot()
BUTTON_WIDTH = int(e.find('buttonWidth').text)
BUTTON_HEIGH = int(e.find('buttonHeigh').text)

startRowSigns = [r'assets/startrowsigns/g clef.png', r'assets/startrowsigns/f clef.png',
                 r'assets/startrowsigns/common time.png',]

barlines = ['assets/barlines/single barline.png', 'assets/barlines/final barline.png',
            'assets/barlines/left repeat sign.png', 'assets/barlines/right repeat sign.png']

modifications = ['assets/modifications/dotnote.png', 'assets/modifications/double flat.png',
                 'assets/modifications/double sharp.png', 'assets/modifications/flat.png',
                 'assets/modifications/natural.png', 'assets/modifications/sharp.png',
                 'assets/modifications/slur.png', 'assets/modifications/staccato.png']

aboveSigns = ['assets/abovesigns/crescendo.png', 'assets/abovesigns/decrescendo.png', 'assets/abovesigns/fermata .png']

rests = ['assets/rests/eighth rest.png', 'assets/rests/half rest.png', 'assets/rests/multi rest.png',
         'assets/rests/one hundred twenty-eighth rest.png', 'assets/rests/quarter rest.png',
         'assets/rests/sixteenth rest.png', 'assets/rests/sixty-fourth rest.png', 'assets/rests/thirty-second rest.png',
         'assets/rests/whole rest.png']

notes = ['assets/notes/breve.png', 'assets/notes/eighth note.png', 'assets/notes/half note.png',
         'assets/notes/one hundred twenty-eighth note.png', 'assets/notes/quarter note.png',
         'assets/notes/sixteenth note.png', 'assets/notes/sixty-fourth note.png',
         'assets/notes/thirty-second note.png', 'assets/notes/whole note.png']


ColPath = startRowSigns + barlines + modifications + aboveSigns + rests + notes


class ButtonsPanel(tk.Frame):

    def __init__(self, root):
        tk.Frame.__init__(self, root, width=BUTTON_WIDTH*2+5)
        self.batchResize(ColPath)
        self.col = [ttk.Button(self, image=ColPath[i], command=lambda i=i: self.btnPressed(i))
                                  for i in range(len(ColPath))]
        [self.col[i].grid(row=i if i < len(startRowSigns + modifications + barlines + aboveSigns)
                                else i - len(startRowSigns + modifications + barlines + aboveSigns),
                        column=0 if i < len(startRowSigns + modifications + barlines + aboveSigns)
                                 else 1) for i in range(len(self.col))]

    def btnPressed(self, index):
        for btn in self.col:
            if str(btn['state']) == 'disabled':
                btn.configure(state='normal')
        self.col[index].configure(state='disabled')
        print(self.col[index])

    def batchResize(self, images):
        for i in range(len(images)):
            images[i] = Image.open(images[i]).resize((BUTTON_WIDTH, BUTTON_HEIGH), Image.ANTIALIAS)
            images[i] = ImageTk.PhotoImage(images[i])



if __name__ == '__main__':
    root = tk.Tk()
    ButtonsPanel(root).pack()
    root.mainloop()