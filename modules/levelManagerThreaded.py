import pygame
import os
import pickle
from .pathing import Pathing
from .vector2D import Vector2
from .frameManager import FrameManager
from .drawable import Drawable
from .animated import Animated
from .projectile import Projectile
from .player import Player
from .undead import *
from .strawman import Strawman
from .humans import *
from .gravestone import Gravestone
from .water import Water
from .gate import Gate
import random
from operator import methodcaller
import time, threading

class LevelManagerThreaded(object):

    _DEBUG = False

    def __init__(self, fileName):
        self._fileName = fileName
        
        self._loaded = False

    def load(self):
        self._loadingThread = threading.Thread(target = self._loadAssets)
        self._loadingThread.start()

    def _loadAssets(self):
        self._fullCollideAble = []
        self._halfCollideAble = []
        self._contactInvisibles = []
        self._creatures = []
        self._corpses = []
        self._weapons = []
        self._projectiles = []
        self._waterTiles = []
        self._gates = []

        self._mouseDrag = False
        self._hudIcons = []
        self._hudNumbers = []
        self._selectRectCoords = [[-2, -2], [-1, -1]]
        self._controlledUndead = []
        self._selectedUndead = []
        self._selectedGraves = []
        self._selectedCorpses = []
        self._localSelectedCorpses = []

        self._winScreen = Drawable("winScreen.png", (200,200), worldBound = False)
        self._winScreen.setPosition(self._winScreen.getPosition()-Vector2(*self._winScreen.getSize())//2)
        self._deathScreen = Drawable("deathScreen.png", (200,200), worldBound = False)
        self._deathScreen.setPosition(self._deathScreen.getPosition()-Vector2(*self._deathScreen.getSize())//2)

        # doesn't work
##        self._alarm = Animated("uiAlarm.png", (371,37))
        
        # for A* pathing
        self._path = Pathing(self._fileName)
        
        file = open(os.path.join("levels", self._fileName))
        fileCharacters = [[y for y in x] for x in file.read().split("\n")]
        file.close()

        self._worldSize = Vector2(len(fileCharacters[0]) * 16, len(fileCharacters) * 16)

        # build the world from a file
        # see "backgroundizer" class to see how the backgrounds get made: it's done seperate

        if os.path.isfile(os.path.join("images", self._fileName[:-4] + "background.png")):
            self._background = Drawable(self._fileName[:-4] + "background.png", (0,0))
        else:
            self._background = Drawable("background.png", (0,0))

        for row in range(len(fileCharacters)):
            for col in range(len(fileCharacters[row])):
                # creatures
                if fileCharacters[row][col] == "p":
                    x = col * 16
                    y = row * 16
                elif fileCharacters[row][col] == "m":
                    self._creatures.append(Strawman((col*16,row*16)))
                elif fileCharacters[row][col] == "c":
                    self._creatures.append(Human((col*16,row*16)))
                elif fileCharacters[row][col] == "g":
                    self._creatures.append(Guard((col*16,row*16)))
                elif fileCharacters[row][col] == "s":
                    self._creatures.append(Soldier((col*16,row*16)))
                elif fileCharacters[row][col] == "a":
                    self._creatures.append(Acolyte((col*16,row*16)))
                elif fileCharacters[row][col] == "b":
                    self._creatures.append(Archer((col*16,row*16)))
                elif fileCharacters[row][col] == "u":
                    self._creatures.append(Cultist((col*16,row*16)))
                elif fileCharacters[row][col] == "k":
                    self._king = King((col*16,row*16))
                    self._creatures.append(self._king)
                
                # weapons
                elif fileCharacters[row][col] == "#":
                    self._weapons.append(Weapon("handaxe",(col*16,row*16)))
                elif fileCharacters[row][col] == "?":
                    self._weapons.append(Weapon("shovel",(col*16,row*16)))
                elif fileCharacters[row][col] == "8":
                    self._weapons.append(Weapon("shortbow",(col*16,row*16)))
                elif fileCharacters[row][col] == "9":
                    self._weapons.append(Weapon("shortsword",(col*16,row*16)))

                # fully collideable things
                elif fileCharacters[row][col] == "W":
                    self._fullCollideAble.append(Drawable("wall.png",(col*16,row*16)))
                elif fileCharacters[row][col] == "T":
                    self._fullCollideAble.append(Drawable("tree.png",(col*16,row*16)))
                elif fileCharacters[row][col] == "B":
                    self._fullCollideAble.append(Drawable("boulder.png",(col*16,row*16)))
                elif fileCharacters[row][col] == "Z":
                    self._fullCollideAble.append(Drawable("throne.png",(col*16,row*16)))
                elif fileCharacters[row][col] == "F":
                    self._fullCollideAble.append(Drawable("fakeHouse"+str(random.randint(1,3))+".png",(col*16,row*16)))
                
                elif fileCharacters[row][col] == "H":
                    # construct a house in multiple pieces
                    self._fullCollideAble.append(Drawable("houseTop.png",(col*16,row*16)))
                    self._fullCollideAble.append(Drawable("houseSide.png",(col*16,(row+1)*16)))
                    self._fullCollideAble.append(Drawable("houseSide.png",((col+5)*16,(row+1)*16)))
                    self._fullCollideAble.append(Drawable("houseFrontLeft.png",(col*16,(row+3)*16)))
                    self._fullCollideAble.append(Drawable("houseFrontRight.png",((col+4)*16,(row+3)*16)))
                    self._contactInvisibles.append(Drawable("houseRoof"+str(random.randint(1,3))+".png",(col*16,row*16)))

                elif fileCharacters[row][col] == "Q":
                    # construct the castle
                    self._fullCollideAble.append(Drawable("wall.png",(col*16,row*16)))
                    self._fullCollideAble.append(Drawable("wall.png",((col+3)*16,row*16)))
                    self._fullCollideAble.append(Drawable("wall.png",((col+6)*16,row*16)))
                    self._fullCollideAble.append(Drawable("wall.png",((col+9)*16,row*16)))
                    self._fullCollideAble.append(Drawable("wall.png",((col+12)*16,row*16)))
                    self._fullCollideAble.append(Drawable("wall.png",((col+13)*16,row*16)))
                    self._fullCollideAble.append(Drawable("wall.png",(col*16,(row+3)*16)))
                    self._fullCollideAble.append(Drawable("wall.png",((col+13)*16,(row+3)*16)))
                    self._fullCollideAble.append(Drawable("portrait2.png",(col*16,(row+6)*16)))
                    self._fullCollideAble.append(Drawable("portrait3.png",((col+13)*16,(row+6)*16)))
                    self._fullCollideAble.append(Drawable("portrait1.png",(col*16,(row+10)*16)))
                    self._fullCollideAble.append(Drawable("portrait4.png",((col+13)*16,(row+10)*16)))
                    self._fullCollideAble.append(Drawable("wall.png",(col*16,(row+14)*16)))
                    self._fullCollideAble.append(Drawable("wall.png",((col+13)*16,(row+14)*16)))
                    self._fullCollideAble.append(Drawable("wall.png",(col*16,(row+17)*16)))
                    self._fullCollideAble.append(Drawable("wall.png",((col+3)*16,(row+17)*16)))
                    self._fullCollideAble.append(Drawable("wall.png",((col+10)*16,(row+17)*16)))
                    self._fullCollideAble.append(Drawable("wall.png",((col+13)*16,(row+17)*16)))

                    self._contactInvisibles.append(Drawable("castleRoof.png",(col*16,row*16)))
                    
                # things that projectiles do not collide with
                elif fileCharacters[row][col] == "S":
                    self._halfCollideAble.append(Drawable("shrub.png",(col*16,row*16)))
                elif fileCharacters[row][col] == "G":
                    self._halfCollideAble.append(Gravestone((col*16,row*16)))
                elif fileCharacters[row][col] == "C":
                    self._halfCollideAble.append(Drawable("stump.png",(col*16,row*16)))
                elif fileCharacters[row][col] == "L":
                    self._halfCollideAble.append(Drawable("cliffLeft.png",(col*16,row*16)))
                elif fileCharacters[row][col] == "U":
                    self._halfCollideAble.append(Drawable("cliffWide.png",(col*16,row*16)))

                # water tiles
                elif fileCharacters[row][col] == "w":
                    self._waterTiles.append(Water((col*16,row*16)))

                # gates
                elif fileCharacters[row][col] == "|":
                    self._gates.append(Gate("gateGraveyard.png", (col*16,row*16), 4))
                elif fileCharacters[row][col] == "{":
                    # forest gate
                    self._gates.append(Gate("gateForest.png", (col*16,row*16), 6))
                elif fileCharacters[row][col] == "}":
                    self._gates.append(Gate("gateTown.png", (col*16,row*16), 10))
                elif fileCharacters[row][col] == "%":
                    # castle gate
                    self._gates.append(Gate("gateCastle.png", (col*16,row*16), 14))
                elif fileCharacters[row][col] == "@":
                    # castle vault
                    self._gates.append(Gate("gateVault.png", (col*16,row*16), 18))
                    
        self._protag = Player((x,y))
        self._creatures.append(self._protag)
        self._loaded = True

    def isLoaded(self):
        return self._loaded

    def draw(self, surface):
        # draw the background
        self._background.draw(surface)
        for waterTile in self._waterTiles:
            waterTile.draw(surface)

        # draw everything, things farther north are drawn behind things further south with this
        worldThings = sorted(self._fullCollideAble + self._halfCollideAble + self._creatures + self._corpses + self._weapons + self._projectiles + self._gates, key=methodcaller('getY'))
        for thing in worldThings:
            thing.draw(surface)

        # roofs and such
        for invis in self._contactInvisibles:
            contacts = [self._protag]
            contacts.extend(self._controlledUndead)
            if any(creature.getCollisionRect().clip(invis.getCollisionRect()).size != (0,0) for creature in contacts):
                pass
            else:
                invis.draw(surface)

        for icon in self._hudIcons:
            icon.draw(surface)
        # hp, mp, xp bars
        pygame.draw.rect(surface, pygame.Color(227,59,67), pygame.Rect(93, 374, 98*(self._protag.getHitPoints()/self._protag.getMaxHitPoints()), 10))
        pygame.draw.rect(surface, pygame.Color(0,152,217), pygame.Rect(211, 374, 98*(self._protag.getMagicPoints()/self._protag.getMaxMagicPoints()), 10))
        pygame.draw.rect(surface, pygame.Color(100,199,78), pygame.Rect(80, 390, 242*(self._protag.experiencePoints()/self._protag.getNextExp()), 3))
        for number in self._hudNumbers:
            number.draw(surface)

        # doesn't work
##        if len(self._localSelectedCorpses) + len(self._controlledUndead) > self._protag.getMaxMagicPoints():
##            self._alarm.draw(surface)

        if self._mouseDrag and not self._protag.isDead():
            # selection rectangle, color is based on current mode
            if self._protag.isCommanding():
                color = pygame.Color(255,0,0)
            else:
                color = pygame.Color(0,0,255)
            pygame.draw.rect(surface, color, self._selectRect, 1)

        if self._protag.isDead():
            self._deathScreen.draw(surface)
        elif self._king.isDead():
            self._winScreen.draw(surface)

    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            return True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # for starting the selection box on left click
            adjust = [int(x/self._scale) for x in event.pos]
            adjust = Drawable.adjustMousePos(adjust)
            self._mouseDrag = True
            self._selectRectCoords[0] = adjust
            self._selectRectCoords[1] = adjust
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            # letting go of the selection box
            self._mouseDrag = False
            # 'undoes' the world offset since the rectangle top coords are relative to the screen for some reason.
            offsetSelectRect = pygame.Rect(self._selectRect.left + Drawable.WINDOW_OFFSET[0], self._selectRect.top + Drawable.WINDOW_OFFSET[1], self._selectRect.width, self._selectRect.height)
            if self._protag.isCommanding():
                # selecting undead
                for undead in self._controlledUndead:
                    undead.setSelected(False)
                    if undead.getCollisionRect().colliderect(offsetSelectRect):
                        undead.setSelected(True)
            elif self._protag.getSpellList()[self._protag.getSpellIndex()] == "unearth":
                # selecting graves
                self._selectedGraves = []
                for grave in self._halfCollideAble:
                    if type(grave) == Gravestone and grave.getCollisionRect().colliderect(offsetSelectRect) and grave.isFilled():
                        self._selectedGraves.append(grave)
            elif self._protag.getSpellList()[self._protag.getSpellIndex()] == "animate dead":
                # selecting corpses
                self._selectedCorpses = []
                for corpse in self._corpses:
                    if corpse.getCollisionRect().colliderect(offsetSelectRect):
                        self._selectedCorpses.append(corpse)
        elif event.type == pygame.MOUSEMOTION:
            # setting the size of the selection box
            if self._mouseDrag:
                adjust = [int(x/self._scale) for x in event.pos]
                adjust = Drawable.adjustMousePos(adjust)
                self._selectRectCoords[1] = adjust
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
            if self._protag.isCommanding():
                # deselect and select all
                if len(self._selectedUndead) == len(self._controlledUndead):
                    for undead in self._controlledUndead:
                        undead.setSelected(False)
                else:
                    for undead in self._controlledUndead:
                        undead.setSelected(True)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            # right click events
            adjust = [int(x/self._scale) for x in event.pos]
            adjust = Drawable.adjustMousePos(adjust)
            midAdjust = (adjust[0]-8, adjust[1]-8)
            if self._protag.isCommanding():     
                if len(self._selectedUndead) > 0:
                    attacking = False
                    following = False
                    # undead attack target at right click. don't target allies or leader, follow leader
                    attackables = [creature for creature in self._creatures if not creature.isControlled()]
                    attackables += [gate for gate in self._gates if not gate.isOpen()]
                    for attackable in attackables:
                        if attackable.getCollisionRect().inflate(24,24).collidepoint(adjust):
                            if type(attackable) == Player:
                                following = True
                                for undead in self._selectedUndead:
                                    undead.zeroPathingTimer()
                                    undead.follow(attackable)
                            else:
                                attacking = True
                                for undead in self._selectedUndead:
                                    undead.zeroPathingTimer()
                                    undead.attack(attackable)
                    # send selected undead to the location of choice on right click
                    if not attacking and not following:
                        for undead in self._selectedUndead:
                            undead.zeroPathingTimer()
                            undead.move(midAdjust)
            else:
                # spellcasting
                if self._protag.getState() != "casting" and self._protag.getSpellList()[self._protag.getSpellIndex()] == "unearth" and len(self._selectedGraves) > 0 and self._protag.getMagicPoints() >= 1:
                    self._protag.cast(self._selectedGraves, self._corpses)
                elif self._protag.getState() != "casting" and self._protag.getSpellList()[self._protag.getSpellIndex()] == "animate dead" and len(self._selectedCorpses) > 0 and self._protag.getMagicPoints() >= 1:
                    self._protag.cast(self._selectedCorpses, self._creatures)
                elif self._protag.getState() != "casting" and self._protag.getSpellList()[self._protag.getSpellIndex()] == "gravebolt" and self._protag.getMagicPoints() >= 1:
                    self._protag.cast(self._projectiles)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            # swap between commanding and casting modes
            self._protag.toggleCommanding()
            if not self._protag.isCommanding():
                if self._protag.isForcing():
                    self._protag.toggleForcing()
                for undead in self._controlledUndead:
                    undead.setSelected(False)
            else:
                self._selectedGraves = []
                self._selectedCorpses = []
                
        # forced commands are unused
        
##        elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
##            # toggle forcing command mode
##            self._protag.toggleForcing()
##            if not self._protag.isCommanding():
##                self._protag.toggleCommanding()
##                self._selectedGraves = []
##                self._selectedCorpses = []
        elif self._DEBUG and event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            # spawn a random controlled undead
            mousePos = [int(x/self._scale) for x in pygame.mouse.get_pos()]
            adjust = Drawable.adjustMousePos(mousePos)
            randSpawn = random.randint(0,1)
            if randSpawn == 0:
                zombie = Zombie(Vector2(adjust[0]-8,adjust[1]-8))
                zombie.setControlled(True)
                self._creatures.append(zombie)
            else:
                skeleton = Skeleton(Vector2(adjust[0]-8,adjust[1]-8))
                skeleton.setControlled(True)
                self._creatures.append(skeleton)
        elif self._DEBUG and event.type == pygame.KEYDOWN and event.key == pygame.K_o:
            # spawn humans
            mousePos = [int(x/self._scale) for x in pygame.mouse.get_pos()]
            adjust = Drawable.adjustMousePos(mousePos)
            self._creatures.append(Guard(Vector2(adjust[0]-8,adjust[1]-8)))
        elif self._DEBUG and event.type == pygame.KEYDOWN and event.key == pygame.K_t:
            # teleport to mouse
            mousePos = [int(x/self._scale) for x in pygame.mouse.get_pos()]
            adjust = Drawable.adjustMousePos(mousePos)
            self._protag.setPosition(Vector2(adjust[0]-8,adjust[1]-8))

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            # halt selected
            for undead in self._selectedUndead:
                undead.idle()
        else:
            # protag inputs: wasd and spell selection
            self._protag.move(event)


    def update(self, ticks, screenSize, scale):
        self._scale = scale
        mousePos = [int(x/self._scale) for x in pygame.mouse.get_pos()]
        Drawable.updateOffset(self._protag, screenSize, self._worldSize, mousePos)

        # janky method of creating the selection rectangle
        self._selectRect = pygame.Rect(min(self._selectRectCoords[0][0], self._selectRectCoords[1][0]) - Drawable.WINDOW_OFFSET[0], \
                                 min(self._selectRectCoords[0][1], self._selectRectCoords[1][1]) - Drawable.WINDOW_OFFSET[1], \
                                 abs(self._selectRectCoords[0][0] - self._selectRectCoords[1][0]), \
                                 abs(self._selectRectCoords[0][1] - self._selectRectCoords[1][1]))

        # meant to be used with the Alarm, currently unused
        self._localSelectedCorpses = []

        for corpse in self._corpses:
            # only nearby corpses "light up" and can be converted
            if corpse in self._selectedCorpses and self._protag.getCollisionRect().inflate(200,200).clip(corpse.getCollisionRect()).size != (0,0):
                corpse.setSelected(True)
                self._localSelectedCorpses.append(corpse)
            else:
                corpse.setSelected(False)

        for grave in self._halfCollideAble:
            # only nearby graves "light up" and can be converted
            if grave in self._selectedGraves and self._protag.getCollisionRect().inflate(200,200).clip(grave.getCollisionRect()).size != (0,0):
                grave.setSelected(True)
            elif type(grave) == Gravestone:
                # things in self._selectedGraves are implicitly Gravestones
                grave.setSelected(False)

        # undead limit! value tbd. also, you lose control when you die
        if len(self._controlledUndead) > self._protag.getMaxMagicPoints():
            rogue = self._controlledUndead[0]
            rogue.setControlled(False)
            rogue.setSelected(False)
            rogue.idle()
        if self._protag.getState() == "dying" or self._protag.getState() == "dead" or self._protag.isDead():
            for undead in self._controlledUndead:
                undead.setControlled(False)
                undead.setSelected(False)
                undead.idle()

        # general purpose kill cleaning
        for creature in self._creatures:
            if creature.isDead():
                creature.setControlled(False)
                creature.setSelected(False)
                self._protag.earnExperience(creature.getExperienceValue())
                if creature.getCorpse() != None:
                    self._corpses.append(creature.getCorpse())
                if creature.getHeldWeapon() != None:
                    self._weapons.append(creature.getHeldWeapon())
                    creature.dropWeapon()
        # apparently [:] is very slow, but keeps memory locations intact so spells can work
        self._creatures[:] = [creature for creature in self._creatures if not creature.isDead()]
        self._corpses[:] = [corpse for corpse in self._corpses if not corpse.isExpended()]
        self._projectiles[:] = [projectile for projectile in self._projectiles if not projectile.hasHit()]
        self._controlledUndead = [undead for undead in self._creatures if undead.isUndead() and undead.isControlled()]
        self._selectedUndead = [undead for undead in self._creatures if undead.isUndead() and undead.isSelected()]

        # update all the things that need it
        # efficiency???
        updatingCreatures = [creature for creature in self._creatures if self._protag.getCollisionRect().inflate(800,800).clip(creature.getCollisionRect()).size != (0,0)]
        colliders = self._fullCollideAble + self._halfCollideAble + [gate for gate in self._gates if not gate.isOpen()]
        colliders = [collider for collider in colliders if self._protag.getCollisionRect().inflate(800,800).clip(collider.getCollisionRect()).size != (0,0)]
        for creature in updatingCreatures:
            personalColliders = [collider for collider in colliders if creature.getCollisionRect().inflate(48,48).clip(collider.getCollisionRect()).size != (0,0)]
            water = [tile for tile in self._waterTiles if creature.getCollisionRect().inflate(48,48).clip(tile.getCollisionRect()).size != (0,0)]
            if creature == self._protag:
                creature.update(self._creatures, personalColliders, self._weapons, self._projectiles, water, self._worldSize, self._path, ticks, mousePos)
            elif not creature.isDead():
                creature.update(self._creatures, personalColliders, self._weapons, self._projectiles, water, self._worldSize, self._path, ticks)
        for weapon in self._weapons:
            weapon.update(ticks)
        for projectile in self._projectiles:
            projectile.update(self._creatures, self._fullCollideAble + [gate for gate in self._gates if not gate.isOpen()], self._worldSize, ticks)
        for waterTile in self._waterTiles:
            waterTile.update(ticks)
        updatingGates = [gate for gate in self._gates if self._protag.getCollisionRect().inflate(800,800).clip(gate.getCollisionRect()).size != (0,0)]
        for gate in updatingGates:
            gate.update(updatingCreatures, ticks)

        # display numbers of controlled undead, also player hp and mana
        # everything HUD
        zombies = 0
        skeletons = 0

        for undead in self._controlledUndead:
            if type(undead) == Zombie:
                zombies += 1
            elif type(undead) == Skeleton:
                skeletons += 1
      
        self._hudIcons = []
        self._hudNumbers = []

        # the big ui elements
        if self._protag.isCommanding():
            self._hudIcons.append(Drawable("uiRed.png", (-1,-1), (0,0), False))
            self._hudIcons.append(Drawable("commandIcon.png", (26,6), (0,0), False))
            self._hudIcons.append(Drawable("uiText.png", (0,27), (0,3), False))
        else:
            self._hudIcons.append(Drawable("uiBlue.png", (-1,-1), (0,0), False))
            self._hudIcons.append(Drawable("spellIcons.png", (26,6), (self._protag.getSpellIndex(),0), False))
            self._hudIcons.append(Drawable("uiText.png", (0,27), (0,self._protag.getSpellIndex()), False))

        # all the ui numbers are here
        zombieText = str(zombies)
        for digit in range(len(zombieText)):
            fromRight = len(zombieText) - digit
            self._hudNumbers.append(Drawable('numbers.png', (screenSize[0]-(fromRight*6)-9,4), (int(zombieText[digit]),0), False))
        skeleText = str(skeletons)
        for digit in range(len(skeleText)):
            fromRight = len(skeleText) - digit
            self._hudNumbers.append(Drawable('numbers.png', (screenSize[0]-(fromRight*6)-9,15), (int(skeleText[digit]),0), False))
        undeadTotalText = str(len(self._controlledUndead))
        for digit in range(len(undeadTotalText)):
            fromRight = len(undeadTotalText) - digit
            self._hudNumbers.append(Drawable('numbers.png', (screenSize[0]-(fromRight*6)-9,26), (int(undeadTotalText[digit]),0), False))
            
        protagHitPointsText = str(self._protag.getHitPoints())
        for digit in range(len(protagHitPointsText)):
            fromRight = len(protagHitPointsText) - digit
            self._hudNumbers.append(Drawable('numbers.png', (screenSize[0]-(fromRight*6)-262,screenSize[1] - 24), (int(protagHitPointsText[digit]),0), False))

        self._hudNumbers.append(Drawable('uiSlash.png', (screenSize[0]-262,screenSize[1] - 24), (0,0), False))
        
        protagMaxHitPointsText = str(self._protag.getMaxHitPoints())
        for digit in range(len(protagMaxHitPointsText)):
            fromRight = len(protagMaxHitPointsText) - digit
            self._hudNumbers.append(Drawable('numbers.png', (screenSize[0]-(fromRight*6)-244,screenSize[1] - 24), (int(protagMaxHitPointsText[digit]),0), False))
            
        protagMagicPointsText = str(self._protag.getMagicPoints())
        for digit in range(len(protagMagicPointsText)):
            fromRight = len(protagMagicPointsText) - digit
            self._hudNumbers.append(Drawable('numbers.png', (screenSize[0]-(fromRight*6)-145,screenSize[1] - 24), (int(protagMagicPointsText[digit]),0), False))

        self._hudNumbers.append(Drawable('uiSlash.png', (screenSize[0]-145,screenSize[1] - 24), (0,0), False))
        
        protagMaxMagicPointsText = str(self._protag.getMaxMagicPoints())
        for digit in range(len(protagMaxMagicPointsText)):
            fromRight = len(protagMaxMagicPointsText) - digit
            self._hudNumbers.append(Drawable('numbers.png', (screenSize[0]-(fromRight*6)-9,37), (int(protagMaxMagicPointsText[digit]),0), False))
            self._hudNumbers.append(Drawable('numbers.png', (screenSize[0]-(fromRight*6)-127,screenSize[1] - 24), (int(protagMaxMagicPointsText[digit]),0), False))
        
##        if len(self._localSelectedCorpses) + len(self._controlledUndead) > self._protag.getMaxMagicPoints():
##            self._alarm.update(ticks)
