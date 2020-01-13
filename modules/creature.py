import pygame
import os
from .vector2D import Vector2
from .mobile import Mobile
from .soundManager import SoundManager
from .creatureFSM import CreatureFSM
from .selectionArrow import SelectionArrow
from .corpse import Corpse
from .weapon import Weapon
from .projectile import Projectile
from .gate import Gate
import random
import math

class Creature(Mobile):
   def __init__(self, imageName, position):
      super().__init__(imageName, position)
      self._isPlayer = False
      self._maxVelocity = 3.0
      self._acceleration = 1.0
      self._targetPos = self._position
      self._maxHitPoints = 4
      self._hitPoints = self._maxHitPoints
      self._experienceValue = 0
      # unarmed strike from regular human
      self._strength = 0
      self._dexterity = 0
      self._defaultAttackDamage = 1 + self._strength
      self._attackDamage = self._defaultAttackDamage
      self._attackTimerMax = 0.6
      self._attackTimer = self._attackTimerMax
      self._wanderTimer = random.randint(3,5)
      self._dead = False
      self._undead = False
      self._defaultSpecialDamage = "bludgeoning"
      self._specialDamage = self._defaultSpecialDamage
      self._weakness = []
      self._resistance = []
      self._immunity = []
      self._FSM = CreatureFSM()
      self._targetObject = None
      self._idleFrames = 1
      self._moveFrames = 2
      self._attackFrames = 2
      self._deathFrames = 3
      self._deathTimer = 1/6.0
      self._controlled = False
      self._selected = False
      # selection and control indicators - janky
      self._selectOffset = Vector2(4,-8)
      self._controlOffset = Vector2(0,3)
      self._selectionArrow = SelectionArrow(self._selectOffset + self._position, "red")
      self._controlCircle = ControlCircle(self._controlOffset + self._position)
      self._waterSplash = WaterSplash(self._position)
      # corpse creation - off by default, used by relevant parties i.e. humans
      self._hasCorpse = False
      self._killingBlow = None
      self._heldWeapon = None
      self._equipableWeapons = []
      # adjust this
      self._weaponOffset = Vector2(0,0)
      self._allies = []
      self._visualRadius = 440
      # water
      self._inWater = False

      self._cornered = False
      self._pathingTimer = 0.0
      self._pathingTimerMax = 1.0

   def zeroPathingTimer(self):
      # makes sure skeletons move when they're told by forcing the pathing timer
      self._pathingTimer = 0.0

   def move(self, targetPos):
      # go to a spot
      self._targetPos = targetPos
      self._FSM.manageState("move")

   def flee(self, targetObject):
      # run from a target
      self._targetObject = targetObject
      self._FSM.manageState("flee")

   def attack(self, targetObject):
      # attack a target
      self._targetObject = targetObject
      self._targetPos = (self._targetObject.getX(), self._targetObject.getY())
      self._FSM.manageState("attack")

   def follow(self, targetObject):
      # follow a target
      self._targetObject = targetObject
      self._targetPos = (self._targetObject.getX(), self._targetObject.getY())
      self._FSM.manageState("follow")

   def idle(self):
      # stop moving
      self._targetPos = self._position
      self._FSM.manageState("stopMoving")

   def getState(self):
      return self._FSM
      
   def hurt(self, amount, special):
      # taking damage
      priorHitPoints = self._hitPoints
      amount = abs(amount)

      if special == "fire" and self._inWater:
         amount //= 2
      
      if special in self._immunity:
         self._hitPoints -= amount * 0
      elif special in self._resistance:
         self._hitPoints -= amount // 2
      elif special in self._weakness:
         self._hitPoints -= amount * 2
      else:
         self._hitPoints -= amount
      SoundManager.getInstance().playSound(special +'_damage.wav')
      if self._hitPoints < 0:
         self._hitPoints = 0
      # killing blow damage types
      if self._hitPoints - priorHitPoints < 0:
         self._killingBlow = special
            

   def heal(self, amount):
      # healing damage
      amount = abs(amount)
      self._hitPoints = min(self._maxHitPoints, self._hitPoints + amount)

   def kill(self):
      self._FSM.manageState("die")

   def isDead(self):
      return self._dead

   def isUndead(self):
      return self._undead

   def getHitPoints(self):
      return self._hitPoints

   def getMaxHitPoints(self):
      return self._maxHitPoints

   def getExperienceValue(self):
      return self._experienceValue

   def isControlled(self):
      return self._controlled

   def isSelected(self):
      return self._selected

   def setControlled(self, status):
      self._controlled = status

   def setSelected(self, status):
      self._selected = status

   def getCorpse(self):
      # used to add corpses to the world from dead creatures
      if self._hasCorpse:
         if self._FSM.isFacing("right"):
            flipped = True
         else:
            flipped = False
         if self._killingBlow == "fire" or self._killingBlow == "necrotic":
            return Corpse(self._position, "skeleton", flipped)
         else:
            return Corpse(self._position, self._imageName[:-4], flipped)
      else:
         return None

   def getFrameStatusOffset(self, flipped):
      # used to make sure items appear properly in creature's hands
      # overridden in specific creature classes
      if self._FSM == "dying" or self._FSM == "dead":
         self._heldWeapon.setRow(2)
         return Vector2(0,0)
      return Vector2(0,0)

   def getHeldWeapon(self):
      return self._heldWeapon

   def setHeldWeapon(self, weapon):
      self._heldWeapon = weapon

   def dropWeapon(self):
      if self._heldWeapon != None:
         self._heldWeapon.setRow(2)
      self._heldWeapon = None

   def isPlayer(self):
      return self._isPlayer

   def getTargetPos(self):
      return self._targetPos

   def getTargetObject(self):
      return self._targetObject

   def getAllies(self):
      return self._allies

   def isInWater(self):
      return self._inWater

   def setWater(self, status):
      self._inWater = status

   def go(self, targetPos):
      # main method for movement
      if not self._isPlayer:
         self._velocity += Vector2(targetPos[0] - self._position[0], targetPos[1] - self._position[1]).normalized() * self._acceleration
      self._row = 1
      self._nFrames = self._moveFrames

   def collision(self, collider):
      # collision
      # allied creatures pass through each other when fleeing
      if collider in self._allies and ((collider.getVelocity().magnitude() == 0 or self._velocity.magnitude() == 0) or collider.getState() == "fleeing" or self._FSM == "fleeing"):
         clipRect = self._position + pygame.Rect(0,0,0,0)
         clipRectStop = self._position + pygame.Rect(0,0,0,0)
      else:
         collideRect = collider.getCollisionRect()
         clipRect = self.getCollisionRect().clip(collideRect)
         stopBox = collideRect.inflate(2,2)
         clipRectStop = self.getCollisionRect().clip(stopBox)
      # box for stopping movement
      if clipRectStop.size != (0,0):
         if clipRectStop.height < clipRectStop.width:
            if self.getY() + self.getHeight() / 2 < collider.getY() + collider.getHeight() / 2:
               if self._velocity[1] > 0:
                  self._velocity[1] = 0
            else:
               if self._velocity[1] < 0:
                  self._velocity[1] = 0
         if clipRectStop.width < clipRectStop.height:
            if self.getX() + self.getWidth() / 2 < collider.getX() + collider.getWidth() / 2:
               if self._velocity[0] > 0:
                  self._velocity[0] = 0
            else:
               if self._velocity[0] < 0:
                  self._velocity[0] = 0
      # box for pushing a creature out of a collider
      if clipRect.size != (0,0):
         if clipRect.height < clipRect.width:
            if self.getY() + self.getHeight() / 2 < collider.getY() + collider.getHeight() / 2:
               self._velocity[1] -= clipRect.height
            else:
               self._velocity[1] += clipRect.height
         if clipRect.width < clipRect.height:
            if self.getX() + self.getWidth() / 2 < collider.getX() + collider.getWidth() / 2:
               self._velocity[0] -= clipRect.width
            else:
               self._velocity[0] += clipRect.width

   def update(self, creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks):
      self._framesPerSecond = 5.0
      # if outside the grid, die and disappear
      if path.isOutside((self._position[0] + self.getWidth() // 2, self._position[1] + self.getHeight() // 2)):
         self._hasCorpse = False
         self._heldWeapon = None
         self._hitPoints = 0
         self._FSM.manageState("fullyDie")
      
      if self._hitPoints <= 0 and self._FSM != "dying" and self._FSM != "dead":
         # trying to get death animations lined up ok...
         # basically, I trick the animated class into drawing the 0 frame by forcing it to update from frame -1
         self._animationTimer = 1/self._framesPerSecond + 0.01
         self._frame = self._deathFrames - 1
         self.kill()
         
      # facing
      if not self._isPlayer and self._position[0] < self._targetPos[0]:
         self._FSM.manageState("right")
      elif not self._isPlayer and self._position[0] > self._targetPos[0] + 1:
         self._FSM.manageState("left")
         
      # hacky stopping solution - possibly want to move elsewhere so that the != following can be cut out
      if not self._isPlayer and self._FSM != "following" and self._FSM != "casting" and Vector2(self._targetPos[0] - self._position[0], self._targetPos[1] - self._position[1]).magnitude() <= self._maxVelocity:
         self._FSM.manageState("stopMoving")

      # weapon pickup goes here
      # compare weapons and take the better one
      droppedWeapons = []
      for weapon in weaponsList:
         if self.getCollisionRect().colliderect(weapon.getCollisionRect()) and weapon.getName() in self._equipableWeapons:
            if weapon.getBonus() == "strength":
               damageCheck = weapon.getDamage() + self._strength + 1 * weapon.isRanged()
            elif weapon.getBonus() == "dexterity":
               damageCheck = weapon.getDamage() + self._dexterity + 1 * weapon.isRanged()
            else:
               damageCheck = weapon.getDamage() + max(self._strength, self._dexterity) + 1 * weapon.isRanged()
            if damageCheck > self._attackDamage + 1 * (self._heldWeapon != None and self._heldWeapon.isRanged()):
               if self._heldWeapon != None:
                  droppedWeapons.append(self._heldWeapon)
               self.dropWeapon()
               self._heldWeapon = weapon
      if self._heldWeapon != None and self._heldWeapon in weaponsList:
         weaponsList.remove(self._heldWeapon)
      weaponsList.extend(droppedWeapons)

      # weapon damage adjustment
      if self._heldWeapon != None:
         if self._heldWeapon.getBonus() == "strength":
            self._attackDamage = self._heldWeapon.getDamage() + self._strength
         elif self._heldWeapon.getBonus() == "dexterity":
            self._attackDamage = self._heldWeapon.getDamage() + self._dexterity
         else:
            self._attackDamage = self._heldWeapon.getDamage() + max(self._strength, self._dexterity)
         self._specialDamage = self._heldWeapon.getSpecial()
      else:
         self._attackDamage = self._defaultAttackDamage
         self._specialDamage = self._defaultSpecialDamage

      # self defense - needs to be secondary to commands, may need to change with allied spellcasters
      if not self._isPlayer and self._FSM == "idle":
         for creature in creatureList:
            if creature not in self._allies and creature.getState() == "attacking" and creature.getTargetObject() == self and self.getCollisionRect().inflate(8,8).clip(creature.getCollisionRect()).size != (0,0):
               self.attack(creature)

      if self._FSM == "casting":
         # wizards only, fools
         pass
      elif self._FSM == "moving":
         # make sure not "moving" unless creature is moving under its own power
         self.go(self._targetPos)
      elif self._FSM == "fleeing":
         # this was more complex previously, but was simplified due to lag issues
         escapeTile = self._path.getEscapeRoutes((self._position[0] + self.getWidth() // 2, self._position[1] + self.getHeight() // 2), (self._targetObject.getX() + self._targetObject.getWidth() // 2, self._targetObject.getY() + self._targetObject.getHeight() // 2))
         if escapeTile == ((self._position[0]//16)*16,(self._position[1]//16)*16):
            for creature in creatureList:
               if creature not in self._allies and self.getCollisionRect().inflate(8,8).clip(creature.getCollisionRect()).size != (0,0):
                  # supposed to be used to encourage "fight or flight"
                  self._cornered = True
         else:
            self._cornered = False
         self.go(escapeTile)
      elif self._FSM == "idle":
         self._velocity = Vector2(0,0)
         self._row = 0
         self._nFrames = self._idleFrames
         if not self._isPlayer and not self._controlled:
            # wander around
            self._wanderTimer -= ticks
            if self._wanderTimer <=0:
               self._FSM.manageState("move")
               # try to stop wanderers from wandering into solid objects
               valid = False
               while not valid:
                  self._targetPos = self._position + Vector2(random.randint(-48,48),random.randint(-48,48))
                  valid = True
                  if self._targetPos[0] < 0 or self._targetPos[0] + self.getWidth() > worldSize[0]:
                     valid = False
                  elif self._targetPos[1] < 0 or self._targetPos[1] + self.getHeight() > worldSize[1]:
                     valid = False
                  else:
                     route = path.getPath((self._position[0] + self.getWidth() // 2, self._position[1] + self.getHeight() // 2), (self._targetPos[0] + 8,self._targetPos[1] + 8))
                     if len(route) == 0:
                        valid = False
                     elif len(route) > 6:
                        valid = False
                  targetRect = pygame.Rect(self._targetPos[0], self._targetPos[1], self.getWidth(), self.getHeight())
                  for creature in creatureList:
                     if creature.getCollisionRect().colliderect(targetRect):
                        valid = False
                  for collider in collisionList:
                     if collider.getCollisionRect().colliderect(targetRect):
                        valid = False
                  if not self._inWater:
                     # doesn't work?
                     for waterTile in waterTiles:
                        if waterTile.getCollisionRect().colliderect(targetRect):
                           valid = False
                     
               self._wanderTimer = random.randint(3,5)
      elif self._FSM == "attacking":
         # this targetPos line is repeated so that the command in the event queue works properly and attackers can't magically damage targets by attacking where they used to be
         self._targetPos = (self._targetObject.getX() + (self._targetObject.getWidth()/2 * (type(self._targetObject) == Gate)), self._targetObject.getY()+ (self._targetObject.getHeight()/2 * (type(self._targetObject) == Gate)))
         if self._heldWeapon == None or not self._heldWeapon.isRanged() or type(self._targetObject) == Gate:
            if self.getCollisionRect().inflate(8,8).clip(self._targetObject.getCollisionRect()).size == (0,0):
               # run up to enemy when out of range
               self.go(self._targetPos)
               self._attackTimer = self._attackTimerMax
            else:
               self._velocity = Vector2(0,0)
               self._row = 2
               self._nFrames = self._attackFrames
               self._framesPerSecond = 5.0 *0.6/self._attackTimerMax
               self._attackTimer -= ticks
               if self._attackTimer <= 0: 
                  self._targetObject.hurt(self._attackDamage, self._specialDamage)
                  self._attackTimer = self._attackTimerMax
         elif self._heldWeapon.isRanged():
            if self.getCollisionRect().inflate(self._visualRadius,self._visualRadius).clip(self._targetObject.getCollisionRect()).size == (0,0):
               self.go(self._targetPos)
               # may need to adjust how attackTimers work for ranged - maybe unique timers
               self._attackTimer = self._attackTimerMax * 2
            else:
               self._velocity = Vector2(0,0)
               self._row = 2
               self._nFrames = self._attackFrames
               #self._framesPerSecond = 5.0 *0.6/self._attackTimerMax
               self._attackTimer -= ticks
               if self._attackTimer <= 0:
                  # lead your shots!
                  z = Projectile.leadShot(self._position, self._targetPos, self._targetObject.getVelocity())
                  # back to default: z = 0 or z = 1
                  aimPos = (self._targetPos[0] + z * self._targetObject.getVelocity()[0], self._targetPos[1] + z * self._targetObject.getVelocity()[1])
                  projectilesList.append(Projectile("arrow", (self.getX()+self.getWidth()//2, self.getY()+self.getHeight()//2), aimPos, self, self._attackDamage, self._specialDamage))
                  self._attackTimer = self._attackTimerMax * 2
         if self._targetObject.getHitPoints()<=0:
            # maybe want this to occur when target is in dying state instead of dead
            self._FSM.manageState("stopMoving")
      elif self._FSM == "following":
         # copied everything but the attacking from attack ~ so it's just moving with the target object stuff...
         self._targetPos = (self._targetObject.getX(), self._targetObject.getY())
         self.go(self._targetPos)
         if self._targetObject.isDead():
            # maybe want this to occur when target is in dying state instead of dead
            self._FSM.manageState("stopMoving")
      elif self._FSM == "dying":
         # to help with death animation timing
         self._velocity = Vector2(0,0)
         self._row = 3
         self._nFrames = self._deathFrames
         if self._frame == self._deathFrames - 1:
            self._deathTimer -= ticks
         if self._deathTimer <= 0 and self._frame == self._deathFrames - 1:
            self._FSM.manageState("fullyDie")
      elif self._FSM == "dead":
         self._dead = True
      
      # look at target! may want to adjust for FSM
      if self._FSM.isFacing("right"):
         flipped = True
      else:
         flipped = False

      # water collision detection
      self._inWater = False
      for waterTile in waterTiles:
         if self.getCollisionRect().colliderect(waterTile.getCollisionRect()):
            self._inWater = True

      # collison detection
      for creature in creatureList:
         if self._isPlayer and creature.isControlled():
            pass
         elif self._FSM == "dying" or self._FSM == "dead" or creature.getState() == "dying" or creature.getState() == "dead":
            pass
         elif self != creature:
            self.collision(creature)
      for collider in collisionList:
         self.collision(collider)  

      # world border detection
      newPosition = self._position + self._velocity
      if newPosition[0] < 0 or newPosition[0] + self.getWidth() > worldSize[0]:
         self._velocity[0] = 0
      if newPosition[1] < 0 or newPosition[1] + self.getHeight() > worldSize[1]:
         self._velocity[1] = 0

      if self._velocity.magnitude() > self._maxVelocity / (1 +self._inWater):
         self._velocity.scale(self._maxVelocity / (1 +self._inWater))

      # added a flip all the way down to animated.py, maybe change that later...
      super().update(ticks, flipped)

      # janky select graphic nonsense
      if self._selected:
         self._selectionArrow.setPosition(self._selectOffset + self._position)
         self._selectionArrow.update(ticks, False)
      if self._controlled:
         self._controlCircle.setPosition(self._controlOffset + self._position)
         self._controlCircle.update(ticks, False)
      # other graphics attatched to creatures
      if self._heldWeapon != None:
         self._weaponOffset = self.getFrameStatusOffset(flipped)
         self._heldWeapon.setPosition(self._weaponOffset + self._position)
         self._heldWeapon.update(ticks, flipped)
      if self._inWater:
         self._waterSplash.setPosition(self._position)
         self._waterSplash.update(ticks)

   def draw(self, surface):
      # added for janky select graphics nonsense
      if self._controlled:
         self._controlCircle.draw(surface)
      super().draw(surface)
      if self._heldWeapon != None:
         self._heldWeapon.draw(surface)
      if self._inWater:
         self._waterSplash.draw(surface)
      if self._selected:
         self._selectionArrow.draw(surface)

class ControlCircle(Mobile):
   def __init__(self, position):
      super().__init__("controlCircle.png", position)
      self._nFrames = 1

class WaterSplash(Mobile):
   def __init__(self, position):
      super().__init__("waterSplash.png", position)
      self._nFrames = 4
