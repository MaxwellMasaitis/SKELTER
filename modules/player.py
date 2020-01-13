import pygame
import os
from .vector2D import Vector2
from .soundManager import SoundManager
from .mobile import Mobile
from .spellcaster import Spellcaster
from .magicCircle import MagicCircle
import random

class Player(Spellcaster):
   def __init__(self, position):
      super().__init__("protag.png", position)
      self._isPlayer = True
      self._movement = {pygame.K_w : False, pygame.K_s : False, pygame.K_a : False, pygame.K_d : False}
      self._maxHitPoints = 6
      self._hitPoints = self._maxHitPoints
      self._maxMagicPoints = 4
      self._magicPoints = self._maxMagicPoints
      self._spellBonus = 3
      
      # spells
      self._spellList = ["unearth", "animate dead", "gravebolt"]
      self._spellSelectedIndex = 0
      
      self._attackFrames = 2
      self._castFrames = 6
      self._deathFrames = 5
      
      self._experiencePoints = 0
      self._nextLevelExperiencePoints = 300
      self._level = 1
      self._commanding = True
      self._forcing = False
            
      # janky hat nonsense
      self._hatOffset = Vector2(0,-8)
      self._hat = Hat(self._hatOffset + self._position)

   def isCommanding(self):
      return self._commanding

   def toggleCommanding(self):
      self._commanding = not self._commanding

   def isForcing(self):
      # unused
      return self._forcing

   def toggleForcing(self):
      self._forcing = not self._forcing

   def earnExperience(self, amount):
      self._experiencePoints += amount

   def experiencePoints(self):
      return self._experiencePoints

   def getNextExp(self):
      return self._nextLevelExperiencePoints
      
   def move(self, event):
      # WASD controls via classwork
      if event.type == pygame.KEYDOWN:
         self._movement[event.key] = True
         self._FSM.manageState("move")
      if event.type == pygame.KEYUP:
         self._movement[event.key] = False
      if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
         self._hat.nextHat()
      if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4 and self._FSM != "casting" and not self._commanding:
         self._spellSelectedIndex -= 1
         self._spellSelectedIndex %= len(self._spellList)
      if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5 and self._FSM != "casting" and not self._commanding:
         self._spellSelectedIndex += 1
         self._spellSelectedIndex %= len(self._spellList)

   def update(self, creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks, lookingPos):
      # leveling up - may need changing
      if self._experiencePoints >= self._nextLevelExperiencePoints:
         self._level += 1
         self._experiencePoints -= self._nextLevelExperiencePoints
         self._nextLevelExperiencePoints += 100
         SoundManager.getInstance().playSound("level_up_jingle.wav")
         self._hitPoints += 4
         self._maxHitPoints += 4
         self._magicPoints += 4
         self._maxMagicPoints += 4
      # WASD again
      if self._movement[pygame.K_w] == True:
         self._velocity[1] -= self._acceleration
      if self._movement[pygame.K_s] == True:
         self._velocity[1] += self._acceleration
      if self._movement[pygame.K_a] == True:
         self._velocity[0] -= self._acceleration
      if self._movement[pygame.K_d] == True:
         self._velocity[0] += self._acceleration
         
      # casting is janky...
      if self._FSM != "casting" and self._movement[pygame.K_w] == False and self._movement[pygame.K_a] == False and self._movement[pygame.K_s] == False and self._movement[pygame.K_d] == False:
         self._FSM.manageState("stopMoving")

      self._allies = [creature for creature in creatureList if creature.isControlled()]
      
      # look at cursor!
      self._targetPos = (self.adjustMousePos(lookingPos)[0], self.adjustMousePos(lookingPos)[1])
      if self._targetPos[0]-7 > self._position[0]:
         self._FSM.manageState("right")
      else:
         self._FSM.manageState("left")

      # loud death sound
      if self._hitPoints <= 0 and self._FSM != "dying" and self._FSM != "dead":
         SoundManager.getInstance().playSound("death.wav")

      super().update(creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks)

      # janky hat nonsense
      flipped = self._FSM.isFacing("right")
      if self._FSM == "moving" and self._frame == 1:
         if not flipped:
            self._hatOffset = Vector2(-1,-7)
         else:
            self._hatOffset = Vector2(1,-7)         
      elif self._FSM == "casting":
         if self._frame >=3:
            flipped = not flipped
         if not flipped:
            if self._frame == 0 or self._frame == 3:
               self._hatOffset = Vector2(-1,-7)
            elif self._frame == 1 or self._frame == 4:
               self._hatOffset = Vector2(1,-10)
            else:
               self._hatOffset = Vector2(0,-8)
         else:
            if self._frame == 0 or self._frame == 3:
               self._hatOffset = Vector2(1,-7)
            elif self._frame == 1 or self._frame == 4:
               self._hatOffset = Vector2(-1,-10)
            else:
               self._hatOffset = Vector2(0,-8)
      else:
         self._hatOffset = Vector2(0,-8)
      self._hat.setPosition(self._hatOffset + self._position)
      self._hat.update(ticks, flipped)

   def draw(self, surface):
      # added for janky hat purposes and nothing else
      super().draw(surface)
      if not self._FSM == "dying" and not self._FSM == "dead":
         self._hat.draw(surface)

class Hat(Mobile):
   # janky hat
   def __init__(self, position):
      super().__init__("hat.png", position)
      self._nFrames = 1
      self._row = random.randint(0,4)

   def nextHat(self):
      self._row += 1
      if self._row == 6:
         self._row = 0
