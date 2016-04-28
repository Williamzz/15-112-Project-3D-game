from math import pi, sin, cos, asin, atan
import sys, random
from direct.showbase import DirectObject
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3, KeyboardButton
from pandac.PandaModules import WindowProperties
from direct.gui.DirectGui import *
from panda3d.core import TextNode
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TransparencyAttrib
from panda3d.core import loadPrcFileData

# Grass: https://vrty.org/image/bzyxuyshpc
# Stone: http://www.texturex.com/albums/Stone-Textures/Stone%20Texture%20cobblestone%20wall%20flag%20rock%20masonry%20grey%20large%20photo.jpg
# Gold: https://pixabay.com/en/gold-texture-swabs-gradient-1000665/
# Golden Monkey: http://www.goldbad-sargans.com/baden-in-gold.html
# Lava Stone: http://wpaulsen.blogspot.com/2014/07/lava-texture.html
# Lava: http://www.outworldz.com/cgi/free-seamless-textures.plx?c=Lava
# Water: http://www.123rf.com/photo_20535240_seamless-water-texture-computer-graphic-big-collection.html
# Tree Bark: http://www.lughertexture.com/wood-old-and-new-hires-textures/bark-wood-hires-textures
# Diamond: https://www.c4dmodelshop.com/ipos/description.php?path=37&sort=Id&page=0&id=306
# Rainbow: https://www.flickr.com/photos/pareeerica/4016548266/player/afd68403be
# sky: http://e2ua.com/data/wallpapers/92/WDF_1366223.jpg
# hand: http://www.lowes.com/creative-ideas/images/2012_03/101844092.jpg
# Blood: http://nobacks.com/blood-splatter-thirty-nine/
# Blood2: https://slate.adobe.com/a/AvZyl/
# red: http://globe-views.com/dreams/red.html
# bg: http://wallpapercave.com/w/vdzssS4

loadPrcFileData("", "win-size 1440 760")
# loadPrcFileData('', 'fullscreen true')
class Player(object):
    def __init__(self,camera):
        self.model = loader.loadModel('models/gold.egg') 
        self.model.clearModelNodes()
        self.model.reparentTo(render)
        self.camera = camera
        self.hand = []
        self.level = 0
        self.health = self.magic = 100
        self.exp = 1

    def discard(self):
        if len(self.hand)>0:
            block = self.hand.pop(-1)
            self.exp += block.potential
            if block.edible == True:
                self.health += block.potential 
            block.model.removeNode()

    def swap(self):
        if len(self.hand)>=2:
            block0 = self.hand[0]
            block1 = self.hand[1]
            self.hand[0]=block1
            self.hand[1]=block0

class Block(object):
    size = 2
    r = size / 2
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        name = type(self).__name__.lower()
        self.name = name
        nameStr = 'models/%s.egg' % name
        self.model = loader.loadModel(nameStr)
        self.model.clearModelNodes()
        self.model.reparentTo(render)
        self.model.setPos(self.x, self.y, self.z)
        self.lethal = False
        self.edible = False
        self.potential = 1

    def __repr__(self):
        return "%s" %type(self).__name__n

class Stone(Block):
    def __init__(self, x, y, z):
        super(type(self),self).__init__(x, y, z)

class GroundBlock(Block):
    def __init__(self, x, y, z):
        super(type(self),self).__init__(x, y, z)
    
class Water(Block):
    def __init__(self, x, y, z):
        super(type(self),self).__init__(x, y, z)
        self.edible = True
       
class Lava(Block):
    def __init__(self, x, y, z):
        super(type(self),self).__init__(x, y, z)
        self.lethal = True
        self.potential = 42
       
class LavaStone(Block):
    def __init__(self, x, y, z):
        super(type(self),self).__init__(x, y, z)
        self.lethal = True
        self.potential = 21
        
class Rainbow(Block):
    def __init__(self, x, y, z):
        super(type(self),self).__init__(x, y, z)
        self.potential = 110
       
class TreeBark(Block):
    def __init__(self, x, y, z):
        super(type(self),self).__init__(x, y, z)
        self.edible = True
        self.potential = 5
        
class Diamond(Block):
    def __init__(self, x, y, z):
        super(type(self),self).__init__(x, y, z)
        self.potential = 417
       
class Gold(Block):
    def __init__(self, x, y, z):
        super(type(self),self).__init__(x, y, z)
        self.potential = 112

class Mob(Block):
    mobCount = 0
    mobKilled = 0
    def __init__(self, x, y, z):
        super(type(self),self).__init__(x, y, z)
        Mob.mobCount +=1
        self.potential = 37

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.title = "Monkeys"
        self.setFrameRateMeter(True)

        # Disable the camera trackball controls.
        self.disableMouse()
        props = WindowProperties()
        props.setCursorHidden(True)
        props.setTitle("Stay Away From The Monkeys")
        props.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(props)
        # set scene
        self.scene = self.loader.loadModel("models/skyTest.egg")
        self.scene.reparentTo(self.render)
        m = 37
        self.scene.setScale(m, m, m)
        self.scene.setPos(0, 0, -5)
        # set camera
        self.camera.setPos(0, 0, 1)
        self.camera.setHpr(0, 0, 0)
        self.cameraSpeed = (0, 0, 0)
        self.maxSpeed = 0.09
        self.lastKeyPressed = ""
        self.blockList = []
        self.mobMax = 0
        self.player = Player(self.camera)
        self.loadModel()
        self.createBars()
        self.die = False
        self.paused = True
        self.helpScreen()
        self.accept("p",self.flipPause)
        self.accept("h",self.helpFlip)
        self.accept("escape",sys.exit)
        self.taskMgr.add(self.update, "updateAll")
                
    def loadModel(self): 
    # background model
        for x in range(-21,22,2):
            for y in range(-21,22,2):
                for z in range(-11,1,2): # top level should be at 0
                    if z == -1: name = "groundBlock"
                    elif z == -3: name = random.choice(["groundBlock",
                        "rainbow","water","treeBark"])
                    elif z == -11: name = "stone"
                    else: name = random.choice(["gold","stone","lava",
                        "diamond","lavaStone","nothing"])
                    if name == "groundBlock" :
                        self.blockList.append(GroundBlock(x, y, z))
                    elif name == "stone": self.blockList.append(Stone(x, y, z))
                    elif name == "water": self.blockList.append(Water(x, y, z))
                    elif name == "gold": self.blockList.append(Gold(x, y, z))
                    elif name == "lava": self.blockList.append(Lava(x,y,z))
                    elif name == "diamond": self.blockList.append(Diamond(x,y,z))
                    elif name == "lavaStone": self.blockList.append(LavaStone(x,y,z))
                    elif name == "rainbow": self.blockList.append(Rainbow(x,y,z))
                    elif name == "treeBark": self.blockList.append(TreeBark(x,y,z))
        for x in range(-31,-22,2):
            for y in range(-31,32,2):
                z = -1
                self.blockList.append(Water(x, y, z))
                self.blockList.append(Water(-x, y, z))
                self.blockList.append(Water(y, x, z))
                self.blockList.append(Water(y, -x, z))

            def rainbowBridge(self,x,y):
                y += 2
                for z in range(9,0,-2):
                    y += 2
                    self.blockList.append(Rainbow(x,y,z))
                    self.blockList.append(Rainbow(x+2,y,z))
                    self.blockList.append(Rainbow(x,20-y,z))
                    self.blockList.append(Rainbow(x+2,20-y,z)) 

            def hill(self,x,y):
                block = 0
                for z in range(9,0,-2):
                    block += 1
                    for i0 in range(block):
                        for i1 in range(block):
                            self.blockList.append(Stone(x-2*i0,y-2*i1,z))
            
            def totem(self,x,y):
                for z in range(5,0,-2):
                    self.blockList.append(LavaStone(x,y,z))
                for z in range(12,4,-2):
                    self.blockList.append(LavaStone(x,y-2,z))
                    self.blockList.append(LavaStone(x,y+2,z))
                    if z==12:
                        self.blockList.append(LavaStone(x,y,z+1))
                    else:
                        self.blockList.append(Lava(x,y,z+1))

            def mysteriousSymbol(self,x,y):
                z = 6
                for z0 in range(0,10,2):
                    self.blockList.append(Diamond(x,y,z+z0))
                    self.blockList.append(Diamond(x-4,y,z+z0))
                for z0 in range(0,10,4):
                    for x0 in range(0,5,2):
                        self.blockList.append(Diamond(x-8-x0,y,z+z0))
                self.blockList.append(Diamond(x-8,y,z+2))
                self.blockList.append(Diamond(x-12,y,z+6))
        hill(self,21,21)
        rainbowBridge(self,-17,7)
        totem(self,-11,-3)
        mysteriousSymbol(self,10,-10)

    def createBars(self):
        # create health bar
        self.healthText = "Health"
        self.healthbar = DirectWaitBar(text = "%d/100" %self.player.health,
            text_scale = 0.3, value = 100, scale = 0.2,
            pos = (1.5,0.5,.8),barColor = (1,0.4,0.4,1))
        self.healthTextObject = OnscreenText(text = self.healthText, pos = (1.2,0.8), 
            scale = 0.05,fg=(0,0,0,1),align=TextNode.ACenter)
        # create magic bar
        self.magicText = "Magic"
        self.magicbar = DirectWaitBar(text = "%d/100" %self.player.magic, 
            text_scale = 0.3,value = 100, scale = 0.2,
            pos = (1.5,.5,.7), barColor = (0,0.5,1,1))
        self.magicTextObject = OnscreenText(text = self.magicText, 
            pos = (1.2,.7), scale = 0.05,fg=(0,0,0,1),align=TextNode.ACenter)
        # create exp bar
        self.expText = "Level.%d" %self.player.level
        self.expbar = DirectWaitBar(value = 1, scale = 0.4,
            pos = (0,.5,-0.87), barColor = (0.6,1,0.6,1),
            frameSize = (-2,2,-0.04,0.04),text = "%d/100" %self.player.exp)
        self.expTextObject = OnscreenText(text = self.expText, pos = (0,-0.82), 
            scale = 0.05,fg=(0,0,0,1),align=TextNode.ACenter)
        # create bar in the center of the screen
        self.centerHorizontalBar = DirectWaitBar(text = "", value = 100, 
            scale = 0.1, pos = (0,0,0), barColor = (0,0,0,1),
            frameSize = (-1,1,-0.04,0.04))
        self.centerVerticalBar = DirectWaitBar(text = "", value = 100, 
            scale = 0.1, pos = (0,0,0), barColor = (0,0,0,1),
            frameSize = (-0.04,0.04,-1,1))
        # create important hints
        self.bk_text0 = "Press H to get help"
        self.HeplText = OnscreenText(text = self.bk_text0,pos = (0,0.8), 
            scale = 0.07,fg=(0,0,0,1),align=TextNode.ACenter,mayChange=0)
        # create blood
        self.blood = OnscreenImage(image = 'texture/Blood.png',pos = (-1.5,0.6, 0.63),
            scale = 0.7, color = (1,1,1,0))
        self.blood.setTransparency(TransparencyAttrib.MAlpha)
        self.blood2 = OnscreenImage(image = 'texture/Blood2.jpg', pos = (0, 0.7, 0),
            scale = (2,1,1), color = (1,1,1,0))
        self.blood2.setTransparency(TransparencyAttrib.MAlpha)
        self.red = OnscreenImage(image = 'texture/red.jpeg', pos = (0, 1, 0),
            scale = (2.5,2,2), color = (1,1,1,0))
        self.red.setTransparency(TransparencyAttrib.MAlpha)

    def helpScreen(self):
        self.bg = OnscreenImage(image = 'texture/bg.jpg', pos = (0, 100, -0.1),
            color=(1,1,1,1),scale = (2,2,1.3))
        self.bg.setTransparency(TransparencyAttrib.MAlpha)

    def helpFlip(self):
        alpha = self.bg["color"][3]
        if alpha == 1: self.bg["color"]=(1,1,1,0)
        else: self.bg["color"]=(1,1,1,1)
        
    def accForward(self):
        speedStep = 0.1
        (dx, dy, dz) = self.cameraSpeed
        (x, y, z) = self.camera.getPos()
        (h, p, r) = self.camera.getHpr()
        angle = h * pi / 180
        if self.lastKeyPressed != "w":
            self.lastKeyPressed = "w"
            dx, dy = 0, 0
        dxNew = dx - speedStep * sin(angle)
        dyNew = dy + speedStep * cos(angle)
        if dxNew ** 2 + dyNew ** 2 > self.maxSpeed: 
            self.cameraSpeed = (dx, dy, dz)
        else: self.cameraSpeed = (dxNew,dyNew,dz)
            
    def accBackward(self):
        speedStep = 0.02
        (dx, dy, dz) = self.cameraSpeed
        (x, y, z) = self.camera.getPos()
        (h, p, r) = self.camera.getHpr()
        angle = h * pi / 180
        if self.lastKeyPressed != "s":
            self.lastKeyPressed = "s"
            dx, dy = 0, 0
        dxNew = dx + speedStep * sin(angle)
        dyNew = dy - speedStep * cos(angle)
        if dxNew ** 2 + dyNew ** 2 > self.maxSpeed: 
            self.cameraSpeed = (dx, dy, dz)
        else: self.cameraSpeed = (dxNew,dyNew,dz)

    def accLeftward(self):
        speedStep = 0.06
        (dx, dy, dz) = self.cameraSpeed
        (x, y, z) = self.camera.getPos()
        (h, p, r) = self.camera.getHpr()
        angle = h * pi / 180
        if self.lastKeyPressed != "a":
            self.lastKeyPressed = "a"
            dx, dy = 0, 0
        dxNew = dx - speedStep * cos(angle)
        dyNew = dy - speedStep * sin(angle)
        if dxNew ** 2 + dyNew ** 2 > self.maxSpeed: 
            self.cameraSpeed = (dx, dy, dz)
        else: self.cameraSpeed = (dxNew,dyNew,dz)

    def accRightward(self):
        speedStep = 0.06
        (dx, dy, dz) = self.cameraSpeed
        (x, y, z) = self.camera.getPos()
        (h, p, r) = self.camera.getHpr()
        angle = h * pi / 180
        if self.lastKeyPressed != "a":
            self.lastKeyPressed = "a"
            dx, dy = 0, 0
        dxNew = dx + speedStep * cos(angle)
        dyNew = dy + speedStep * sin(angle)
        if dxNew ** 2 + dyNew ** 2 > self.maxSpeed: 
            self.cameraSpeed = (dx, dy, dz)
        else: self.cameraSpeed = (dxNew,dyNew,dz)

    def jump(self):
        (x, y, z) = self.camera.getPos()
        (dx, dy, dz) = self.cameraSpeed
        if dz == 0: self.cameraSpeed = (dx,dy,2)

    def isLegalMove(self, newX, newY, newZ, r = 1):
        for block in self.blockList:
            (blockX, blockY, blockZ) = block.model.getPos()
            if self.collision((newX-r,newY-r,newZ-r),(newX+r,newY+r,newZ+r),
                (blockX-1,blockY-1,blockZ-1),(blockX+1,blockY+1,blockZ+1)):
                 return False
        return True

    def flipPause(self): 
        self.paused = not(self.paused)

    def dieScreen(self,time):
        dieMessage = OnscreenText(text = "You are dead", pos = (0,0), 
            scale = 0.45, fg = (1,0,0,1), align=TextNode.ACenter)
        scoreMessage = OnscreenText(text = "You survived %d seconds" %time, 
            pos = (0,-0.3), scale = 0.2, fg = (1,0,0,1), align=TextNode.ACenter)
        levelMessage = OnscreenText(text = "You reached level %d" %self.player.level, 
            pos = (0,-0.5), scale = 0.1, fg = (1,0,0,1), align=TextNode.ACenter)
        exit = OnscreenText(text = "Press esc to quit", pos = (0,-0.6), 
            scale = 0.1, fg = (1,0,0,1), align=TextNode.ACenter)

    # Define a procedure to move the camera.
    def update(self,task):
        if self.paused==True:
            self.lookAround()
            return Task.cont
        else:
            if self.die == False:
                self.cameraUpdate()
                self.mobUpdate()
                self.playerUpdate()
                return Task.cont
            else:
                self.dieScreen(task.time)
                return task.done

    def mobUpdate(self):
        if Mob.mobCount <= self.mobMax:
            x = random.randint(-10,10)
            y = random.randint(-10,10)
            z = random.randint(1,10)
            self.blockList.append(Mob(x,y,z))
        try:
            (x0,y0,z0) = self.camera.getPos()
            for block in self.blockList:
                if type(block) == Mob:
                    (x1,y1,z1) = block.model.getPos()
                    (h, p, r) = self.camera.getHpr()
                    (xSpeed,ySpeed,zSpeed)=((x0-x1)*0.01,(y0-y1)*0.01,(z0-z1)*0.01)
                    for speed in [xSpeed,ySpeed,zSpeed]:
                        speed = max(speed,0.01) # speed has minimum value
                    newX,newY,newZ = x1+xSpeed,y1+ySpeed,z1+zSpeed
                    self.mobPostition(newX,newY,newZ,block)
                    block.model.setHpr(h,p,r)
        except: pass

    def mobPostition(self,newX,newY,newZ,block):
        (x1,y1,z1) = block.model.getPos()
        (x2,y2,z2) = self.player.model.getPos()
        r = 1
        if self.collision((x1-r,y1-r,z1-r),(x1+r,y1+r,z1+r),(x2-r,y2-r,z2-r),
            (x2+r,y2+r,z2+r)):
            self.player.health -= 1
            if self.player.health <= 0:
                self.die = True
            return
        for block0 in self.blockList:
            (blockX, blockY, blockZ) = block0.model.getPos()
            if block0 == block: continue
            if self.collision((newX-r,newY-r,newZ-r),(newX+r,newY+r,newZ+r),
                (blockX-1,blockY-1,blockZ-1),(blockX+1,blockY+1,blockZ+1)):
                block.model.setPos(x1,y1,z1+0.01)
                return
        block.model.setPos(newX,newY,newZ)

    def cameraUpdate(self):
        # these two function decides the direction of moving
        def fall(self):
            (x, y, z) = self.camera.getPos()
            (dx, dy, dz) = self.cameraSpeed
            (newX, newY, newZ) = (x+dx, y+dy, z+dz)
            if newZ < -7:
                dz = 0.2
            self.cameraSpeed = (dx, dy, dz-0.2)
            if not self.isLegalMove(newX, newY, newZ):
                self.cameraSpeed = (dx,dy,0)

        def acceptMovement(self):
            # accept movement
            (x, y, z) = self.camera.getPos()
            (dx, dy, dz) = self.cameraSpeed
            (newX, newY, newZ) = (x+dx, y+dy, z+dz)
            forward_button = KeyboardButton.ascii_key('w')
            backward_button = KeyboardButton.ascii_key('s')
            leftward_button = KeyboardButton.ascii_key('a')
            rightward_button = KeyboardButton.ascii_key('d')
            # next line is from panda3D website
            is_down = self.mouseWatcherNode.is_button_down
            if is_down(forward_button): self.accForward()
            elif is_down(backward_button): self.accBackward()
            elif is_down(leftward_button): self.accLeftward()
            elif is_down(rightward_button): self.accRightward()
            else: self.cameraSpeed = (0, 0, dz)

        def inBoundPos(x, y, z):
            lowerBound = -22
            upperBound = 22
            if x < lowerBound: x = lowerBound
            elif x > upperBound: x = upperBound 
            if y < lowerBound: y = lowerBound
            elif y > upperBound: y = upperBound 
            return (x, y, z)

        fall(self)
        acceptMovement(self)
        size = 2
        r = size / 2
        (x, y, z) = self.camera.getPos()
        (dx, dy, dz) = self.cameraSpeed
        (newX, newY, newZ) = (x+dx, y+dy, z+dz)
        self.accept("space",self.jump)
        (newX,newY,newZ) = inBoundPos(newX,newY,newZ)
        for block in self.blockList:
            (blockX, blockY, blockZ) = block.model.getPos()
            if self.collision((newX-r,newY-r,newZ-r),(newX+r,newY+r,newZ+r),
                (blockX-r,blockY-r,blockZ-r),(blockX+r,blockY+r,blockZ+r)):
                if block.lethal == True:
                    self.player.health -= 0.2
                # When it's on the ground colliding
                if z-r >= blockZ+r:
                    newZ = blockZ + 2 * r
                    if self.isLegalMove(newX,newY,newZ+0.25):
                        self.camera.setPos(newX,newY,newZ)
                        self.cameraSpeed = (dx, dy, 0)
                        break
                    else:
                        newX, newY = x, y
                        self.camera.setPos(newX,newY,newZ)
                        self.cameraSpeed = (0, 0, 0)
                        break
                else:
                    newX, newY, newZ = x, y, z
                    self.camera.setPos(x,y,z)
                    self.cameraSpeed = (0, 0, 0)
                    break
        
        # when it doesn't collide, move the camera along the should be
        self.camera.setPos(newX, newY, newZ)
        # the rest of the function controls the camera angle
        # the next two lines are from panda 3D website
        self.lookAround()

    def lookAround(self):
        mw = base.mouseWatcherNode
        if mw.hasMouse():
            # get the position, which at center is (0, 0) 
            x, y = mw.getMouseX(), mw.getMouseY()
            props = base.win.getProperties() 
            hMax, pMax = 150, 75
            (h, p, r) = self.camera.getHpr()
            h = (-hMax * x / 3) % 360
            p = pMax * y / 3
            # constrain the camera angle
            if p > 90: p = 90
            elif p <= -90: p = -90 
            self.camera.setHpr(h, p, r)

    def playerUpdate(self):
        def findBlock(self):
            (x, y, z) = self.camera.getPos()
            (h, p, r) = self.camera.getHpr()
            theta = h * pi /180
            phi = p * pi /180
            for radius in range(1,4):
                # default setting of looking at blocks
                lookX = x - radius * cos(phi) * sin(theta)
                lookY = y + radius * cos(phi) * cos(theta)
                lookZ = z + radius * sin(phi)
                smallR = 0.1
                for block in self.blockList:
                    (blockX, blockY, blockZ) = block.model.getPos()
                    if self.collision((lookX-smallR,lookY-smallR,lookZ-smallR),
                        (lookX+smallR,lookY+smallR,lookZ+smallR),
                        (blockX-1,blockY-1,blockZ-1),
                        (blockX+1,blockY+1,blockZ+1)):
                        return block

        (x, y, z) = self.camera.getPos()
        (h, p, r) = self.camera.getHpr()
        self.player.model.setPos(x, y, z)
        self.blockLookAt = findBlock(self)
        if self.blockLookAt != None:
            self.accept("c",self.collectBlock)
        self.accept("x",self.player.discard)
        self.showHand()
        self.accept("z",self.player.swap)
        if len(self.player.hand)<2:
            try: self.textObject.setText("")
            except: pass
        self.statusUpdate()

    def statusUpdate(self):
        # make sure health and magic regenerates
        health = self.player.health 
        magic = self.player.magic
        exp = self.player.exp
        if magic < self.magicbar["range"]: self.player.magic += 0.1
        else: self.player.magic = self.magicbar["range"]
        if health < self.healthbar["range"]: self.player.health += 0.1
        else: self.player.health = self.healthbar["range"]
        if exp >= self.expbar["range"]:
            self.player.level += 1
            self.player.exp -= self.expbar["range"]
            self.expbar["range"] += 500
            self.healthbar["range"] *= 2
            self.magicbar["range"] *= 2
            self.expTextObject["text"] = "Level.%d" %self.player.level
            # update information on the bar
        self.healthbar["value"] = health
        self.healthbar["text"] = "%d/%d" %(health,self.healthbar["range"])
        self.magicbar["value"] = self.player.magic
        self.magicbar["text"] = "%d/%d" %(magic,self.magicbar["range"])
        self.expbar["value"] = self.player.exp
        self.expbar["text"] = "%d/%d" %(exp,self.expbar["range"])
        self.mobMax = Mob.mobKilled
        if health <= 75:
            alpha = 1 - self.player.health / 75
            self.blood["color"] = (1,1,1,alpha/3*2)
            self.blood2["color"] = (1,1,1,alpha/2)
            self.red["color"] = (1,1,1,alpha/4)

    def showHand(self):
        (x, y, z) = self.camera.getPos()
        (h, p, r) = self.camera.getHpr()
        theta = h * pi /180
        phi = p * pi /180
        radius = 1.5
        if len(self.player.hand)>=2:
            for block in self.player.hand:
                block.model.detachNode()
            m = 0.1
            phi -= pi/12
            leftBlock = self.player.hand[0]
            theta += pi/16
            leftX = x - radius * cos(phi) * sin(theta)
            leftY = y + radius * cos(phi) * cos(theta)
            leftZ = z + radius * sin(phi)
            leftBlock.model.reparentTo(render)
            leftBlock.model.setScale(m,m,m)
            leftBlock.model.setPos(leftX,leftY,leftZ)

            rightBlock = self.player.hand[1]
            theta -= pi/8
            rightX = x - radius * cos(phi) * sin(theta)
            rightY = y + radius * cos(phi) * cos(theta)
            rightZ = z + radius * sin(phi)
            rightBlock.model.reparentTo(render)
            rightBlock.model.setScale(m,m,m)
            rightBlock.model.setPos(rightX,rightY,rightZ)

        elif len(self.player.hand)==1:
            m = 0.1
            phi -= pi/12
            leftBlock = self.player.hand[0]
            theta += pi/16
            leftX = x - radius * cos(phi) * sin(theta)
            leftY = y + radius * cos(phi) * cos(theta)
            leftZ = z + radius * sin(phi)
            leftBlock.model.reparentTo(render)
            leftBlock.model.setScale(m,m,m)
            leftBlock.model.setPos(leftX,leftY,leftZ)

    def collectBlock(self):
        if self.player.magic < 20:
            self.blockLookAt = None 
            return 
        if type(self.blockLookAt) == Mob:
            Mob.mobCount -= 1
            Mob.mobKilled += 1
        if (len(self.player.hand)<2 and self.blockLookAt in self.blockList 
            and self.blockLookAt!= None):
            self.player.hand.append(self.blockLookAt)
            self.blockList.remove(self.blockLookAt)
            self.blockLookAt.model.detachNode()
            self.player.magic -= 20
        self.blockLookAt = None

    @staticmethod
    def collision(position00, position01, position10, position11):
        # this is strict collision
        (x00,y00,z00) = position00
        (x01,y01,z01) = position01
        (x10,y10,z10) = position10
        (x11,y11,z11) = position11
        if ((((x10<x00<x11) or (x10<x01<x11)) and ((y10<y00<y11) or (y10<y01<y11))
            and ((z10<=z00<=z11) or (z10<=z01<=z11))) or (((x00<x10<x01) 
                or (x00<x11<x01)) and ((y00<y10<y01) or (y00<y11<y01)) 
                    and (((z10<=z00<=z11) or (z10<=z01<=z11))))):
            return True
        else: return False
        
app = MyApp()
app.run()