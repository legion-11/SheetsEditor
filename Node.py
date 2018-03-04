import xml.etree.ElementTree

e = xml.etree.ElementTree.parse('config').getroot()
BG_COLOR = e.find('bgColor').text
NODE_COLOR = e.find('nodeColor').text
NODE_RADIUS = float(e.find('nodeRadius').text)


class Node:
    """This nodes can be chanched by click on them on notes or """
    r = NODE_RADIUS

    def __init__(self, x, y, canvas):
        self.x = x
        self.y = y
        self.canvas = canvas

    def draw(self):
        self.canvas.create_oval(self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r, fill=NODE_COLOR, outline=NODE_COLOR)

    def hide(self):
        self.canvas.create_oval(self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r, fill=BG_COLOR, outline=BG_COLOR)

    def is_collision(self, eveX, eveY):
        """return True if click on node"""
        return (eveX - self.x)**2+(eveY - self.y)**2 <= self.r**2