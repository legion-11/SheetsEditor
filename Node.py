import xml.etree.ElementTree

e = xml.etree.ElementTree.parse('config').getroot()
BG_COLOR = e.find('bgColor').text
NODE_COLOR = e.find('nodeColor').text
NODE_RENDER_RADIUS = float(e.find('nodeRenderRadius').text)
NODE_WORK_RADIUS = float(e.find('nodeWorkRadius').text)

class Node:
    """This node can be changed on notes by click on them"""
    radius = NODE_RENDER_RADIUS
    workRadius = NODE_WORK_RADIUS

    def __init__(self, x, y, numberInLine, canvas):
        """
        create Node by coordinates x, y
        @:param x - represent x coordinate of Node
        @:param y - represent y coordinate of Node
        @:param numberInLine - represent index of Node in Line class
        @:param canvas - represent canvas where Node is drawing
        """
        self.x = x
        self.y = y
        self.numberInLine = numberInLine
        self.canvas = canvas

    def draw(self):
        """draw Node by coordinates that was given at creation"""
        self.canvas.create_oval(self.x - self.radius, self.y - self.radius, self.x + self.radius, self.y + self.radius,
                                fill=NODE_COLOR, outline=NODE_COLOR)

    def hide(self):
        """fill Node with background color"""
        self.canvas.create_oval(self.x - self.radius, self.y - self.radius, self.x + self.radius, self.y + self.radius,
                                fill=BG_COLOR, outline=BG_COLOR)

    def isCollision(self, eveX, eveY):
        """return True if click on Node else False"""
        return (eveX - self.x)**2+(eveY - self.y)**2 <= self.workRadius ** 2

    def change(self):
        """this will change Node with note for now it is abstract"""
        print("node", self.numberInLine, 'changed')
        self.hide()
