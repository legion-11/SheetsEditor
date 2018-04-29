from PIL import Image, ImageTk


def batchResize(image, width, height):
    if image is not None:
        resized = Image.open(image).resize((width, height), Image.ANTIALIAS)
        return ImageTk.PhotoImage(resized)


startRowSigns = [r'assets/startrowsigns/g clef.png',
                 r'assets/startrowsigns/f clef.png']

time = [r'assets/startrowsigns/common time.png']

barlines = ['assets/barlines/single barline.png',
            'assets/barlines/final barline.png',
            'assets/barlines/left repeat sign.png',
            'assets/barlines/right repeat sign.png']

modifications = ['assets/modifications/double flat.png',
                 'assets/modifications/double sharp.png',
                 'assets/modifications/flat.png',
                 'assets/modifications/natural.png',
                 'assets/modifications/sharp.png']
temp = ['assets/temp/dotnote.png',
        'assets/temp/slur.png',
        'assets/temp/staccato.png']

aboveSigns = ['assets/abovesigns/crescendo.png',
              'assets/abovesigns/decrescendo.png',
              'assets/abovesigns/fermata .png']

rests = ['assets/rests/multi rest.png',
         'assets/rests/whole rest.png',
         'assets/rests/half rest.png',
         'assets/rests/quarter rest.png',
         'assets/rests/eighth rest.png',
         'assets/rests/sixteenth rest.png',
         'assets/rests/thirty-second rest.png',
         'assets/rests/sixty-fourth rest.png',
         'assets/rests/one hundred twenty-eighth rest.png']

notes = ['assets/notes/breve.png',
         'assets/notes/whole note.png',
         'assets/notes/half note.png',
         'assets/notes/quarter note.png',
         'assets/notes/eighth note.png',
         'assets/notes/sixteenth note.png',
         'assets/notes/thirty-second note.png',
         'assets/notes/sixty-fourth note.png',
         'assets/notes/one hundred twenty-eighth note.png']

ColPath = startRowSigns+ time + barlines + modifications + temp + aboveSigns + rests + notes

heads = ['assets/heads/breve.png',
         'assets/heads/filled.png',
         'assets/heads/unfilled.png',
         'assets/heads/whole note.png']

tails = ['assets/tails/eighth tail.png',
         'assets/tails/one hundred twenty-eighth tail.png',
         'assets/tails/sixteenth tail.png',
         'assets/tails/sixty-fourth tail.png',
         'assets/tails/thirty-second tail.png',
         'assets/tails/untailed.png']
