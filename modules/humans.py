import pygame
import os
from .vector2D import Vector2
from .mobile import Mobile
from .creature import Creature
from .spellcaster import Spellcaster
from .magicCircle import MagicCircle
import random
from .weapon import Weapon

# these all generally work the same ways so I'm not commenting all of them
# the interesting ones are the spellcasters and default human

class Human(Creature):
   def __init__(self, position):
      skin = random.choice(("human1.png", "human2.png", "human3.png"))
      super().__init__(skin, position)
      self._maxHitPoints = 4
      self._hitPoints = self._maxHitPoints
      self._experienceValue = 10
      self._undead = False
      self._hasCorpse = True
      self._equipableWeapons = Weapon.SIMPLE
      

   def update(self, creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks):
      self._path = path
      self._pathingTimer -= ticks
      self._allies = [creature for creature in creatureList if not creature.isUndead() and not creature.isPlayer() and not type(creature) == Cultist]
      localAllies = [ally for ally in self._allies if self.getCollisionRect().inflate(200,200).clip(ally.getCollisionRect()).size != (0,0)]
      humanEnemies = [creature for creature in creatureList if creature.isUndead() or creature.isPlayer()]
      localHumanEnemies = [enemy for enemy in humanEnemies if self.getCollisionRect().inflate(self._visualRadius,self._visualRadius).clip(enemy.getCollisionRect()).size != (0,0)]
      targetRange = 1200
      targetEnemy = None
      if len(localHumanEnemies) > 0:
         # detect enemies and make a decision
         for enemy in localHumanEnemies:
            distance = Vector2(enemy.getX() - self.getX(), enemy.getY() - self.getY()).magnitude()
            if distance < targetRange and enemy.getHitPoints() > 0:
               targetRange = distance
               targetEnemy = enemy
         if targetEnemy != None:
            # adjust numbers
            # made common humans a bit dumber by making them attack even when outnumbered
            if not self._cornered and len(localHumanEnemies) > len(localAllies)+1:
               self.flee(targetEnemy)
            else:
               self.attack(targetEnemy)
         elif not self._FSM == "moving":
            self.idle()
      else:
         self._cornered = False
      super().update(creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks)

   def go(self, targetPos):
      if self._FSM == "fleeing":
         # run away directly
         super().go(targetPos)
      else:
         if self._pathingTimer <= 0:
            # uses a framerule for pathing lag stuff
            self._route = self._path.getPath((self._position[0] + self.getWidth() // 2, self._position[1] + self.getHeight() // 2), (targetPos[0] + self.getWidth() // 2,targetPos[1] + self.getHeight() // 2))
            self._pathingTimer = self._pathingTimerMax + random.random()/2
         if len(self._route) >= 2:
            if ((self._position[0] + self.getWidth() // 2)//16 * 16, (self._position[1] + self.getHeight() // 2)//16 * 16) == self._route[1]:
               # this is also part of the framerule
               super().go(self._route.pop(1))
            else:
               super().go(self._route[1])
         else:
            self.idle()
         
   def getFrameStatusOffset(self, flipped):
      # for holding weapons
      self._heldWeapon.setRow(0)
      if self._FSM == "idle":
         if not flipped:
            return Vector2(5,0)
         else:
            return Vector2(-5,0)
      elif self._FSM == "moving" or self._FSM == "fleeing":
         if not flipped:
            if self._frame == 0:
               return Vector2(6,-1)
            else:
               return Vector2(1,-2)
         else:
            if self._frame == 0:
               return Vector2(-6,-1)
            else:
               return Vector2(-1,-2)
      elif self._FSM == "attacking":
         # slightly glitchy here
         if self.getCollisionRect().inflate(8,8).clip(self._targetObject.getCollisionRect()).size == (0,0):
            if not flipped:
               if self._frame == 0:
                  return Vector2(6,-1)
               else:
                  return Vector2(1,-2)
            else:
               if self._frame == 0:
                  return Vector2(-6,-1)
               else:
                  return Vector2(-1,-2)
         else:
            if not flipped:
               if self._frame == 0:
                  return Vector2(4,-3)
               else:
                  self._heldWeapon.setRow(1)
                  return Vector2(-10,1)
            else:
               if self._frame == 0:
                  return Vector2(-4,-3)
               else:
                  self._heldWeapon.setRow(1)
                  return Vector2(10,1)
      elif self._FSM == "dying" or self._FSM == "dead":
         self._heldWeapon.setRow(2)
         return Vector2(0,0)
      else:
         return Vector2(0,0)

class Acolyte(Spellcaster):
   def __init__(self, position):
      skin = random.choice(("acolyte1.png", "acolyte2.png", "acolyte3.png"))
      super().__init__(skin, position)
      self._maxHitPoints = 9
      self._hitPoints = self._maxHitPoints
      self._maxMagicPoints = 6
      self._magicPoints = self._maxMagicPoints
      self._experienceValue = 50
      self._spellBonus = 2
      self._spellList = ["healing word","firebolt"]
      self._undead = False
      self._hasCorpse = True
      self._heldWeapon = Weapon("club", self._weaponOffset + self._position)
      self._equipableWeapons = Weapon.SIMPLE
      self._visualRadius += 80

      self._magicCircle = MagicCircle(self._magicOffset + self._position, "holy")

   def update(self, creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks):
      self._path = path
      self._pathingTimer -= ticks
      self._allies = [creature for creature in creatureList if not creature.isUndead() and not creature.isPlayer() and not type(creature) == Cultist]
      humanEnemies = [creature for creature in creatureList if creature.isUndead() or creature.isPlayer()]
      targetRange = 1200
      targetAlly = None
      targetEnemy = None
      targetHitPointPercent = 1.0
      # detect allies and heal the injured within a certain damage threshold
      # only detect allies you can "see" within visual radius
      for ally in self._allies:
         if self.getCollisionRect().inflate(self._visualRadius,self._visualRadius).clip(ally.getCollisionRect()).size != (0,0) and ally.getHitPoints() >=1 and ally.getHitPoints()/ally.getMaxHitPoints() < targetHitPointPercent:
            targetAlly = ally
            targetHitPointPercent = ally.getHitPoints()/ally.getMaxHitPoints()
      if targetAlly != None and self._magicPoints >= 2 and targetAlly.getMaxHitPoints() - targetAlly.getHitPoints() >= 2 + self._spellBonus and targetAlly.getState() != "dying" and targetAlly.getState() != "dead":
         if self.getCollisionRect().inflate(200,200).clip(targetAlly.getCollisionRect()).size == (0,0):
            # healing word has a limited range so get close
            self.move((targetAlly.getX(), targetAlly.getY()))
         elif self.getCollisionRect().inflate(144,144).clip(targetAlly.getCollisionRect()).size == (0,0) and self._FSM != "casting":
            self.move((targetAlly.getX(), targetAlly.getY()))
         elif self._FSM != "casting":
            # healing word - maybe adjust this in the future
            self._spellSelectedIndex = self._spellList.index("healing word")
            self.cast(targetAlly)
         
      elif len(humanEnemies) > 0 and self._FSM != "casting":
         # detect enemies and make decisions
         for enemy in humanEnemies:
            distance = Vector2(enemy.getX() - self.getX(), enemy.getY() - self.getY()).magnitude()
            if self.getCollisionRect().inflate(self._visualRadius,self._visualRadius).clip(enemy.getCollisionRect()).size != (0,0) and distance < targetRange and enemy.getHitPoints() > 0:
               targetRange = distance
               targetEnemy = enemy
               self._targetObject = targetEnemy
         if targetEnemy != None:
            if not self._cornered and (self._hitPoints <= 5 or targetRange <= 96):
               self.flee(targetEnemy)
            elif self._magicPoints > 0:
               # magic attack spell
               self._spellSelectedIndex = self._spellList.index("firebolt")
               self.cast(projectilesList)
            else:
               self.attack(targetEnemy)
         elif not self._FSM == "moving":
            self.idle()
      else:
         self._cornered = False
      super().update(creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks)

   def go(self, targetPos):
      if self._FSM == "fleeing":
         super().go(targetPos)
      else:
         if self._pathingTimer <= 0:
            self._route = self._path.getPath((self._position[0] + self.getWidth() // 2, self._position[1] + self.getHeight() // 2), (targetPos[0] + self.getWidth() // 2,targetPos[1] + self.getHeight() // 2))
            self._pathingTimer = self._pathingTimerMax + random.random()/2
         if len(self._route) >= 2:
            if ((self._position[0] + self.getWidth() // 2)//16 * 16, (self._position[1] + self.getHeight() // 2)//16 * 16) == self._route[1]:
               super().go(self._route.pop(1))
            else:
               super().go(self._route[1])
         else:
            self.idle()
         
   def getFrameStatusOffset(self, flipped):
      self._heldWeapon.setRow(0)
      if self._FSM == "idle":
         if flipped == False:
            return Vector2(2,-1)
         else:
            return Vector2(-2,-1)
      elif self._FSM == "moving" or self._FSM == "fleeing":
         if flipped == False:
            if self._frame == 0:
               return Vector2(2,-1)
            else:
               return Vector2(1,0)
         else:
            if self._frame == 0:
               return Vector2(-2,-1)
            else:
               return Vector2(-1,0)
      elif self._FSM == "attacking":
         # slightly glitchy here
         if self.getCollisionRect().inflate(8,8).clip(self._targetObject.getCollisionRect()).size == (0,0):
            if flipped == False:
               if self._frame == 0:
                  return Vector2(2,-1)
               else:
                  return Vector2(1,0)
            else:
               if self._frame == 0:
                  return Vector2(-2,-1)
               else:
                  return Vector2(-1,0)
         else:
            if flipped == False:
               if self._frame == 0:
                  return Vector2(2,0)
               else:
                  self._heldWeapon.setRow(2)
                  return Vector2(-3,-2)
            else:
               if self._frame == 0:
                  return Vector2(-2,0)
               else:
                  self._heldWeapon.setRow(2)
                  return Vector2(3,-2)
      elif self._FSM == "casting":
         self._heldWeapon.setRow(2)
         return Vector2(0,0)
      elif self._FSM == "dying" or self._FSM == "dead":
         self._heldWeapon.setRow(2)
         return Vector2(0,0)
      else:
         return Vector2(0,0)

class Guard(Creature):
   def __init__(self, position):
      skin = random.choice(("guard1.png", "guard2.png", "guard3.png"))
      super().__init__(skin, position)
      self._maxHitPoints = 11
      self._hitPoints = self._maxHitPoints
      self._experienceValue = 25
      self._strength = 1
      self._dexterity = 1
      self._defaultAttackDamage = 1 + self._strength
      self._attackDamage = self._defaultAttackDamage
      self._undead = False
      self._hasCorpse = True
      self._heldWeapon = Weapon("spear", self._weaponOffset + self._position)
      self._equipableWeapons = Weapon.SIMPLE

   def update(self, creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks):
      self._path = path
      self._pathingTimer -= ticks
      self._allies = [creature for creature in creatureList if not creature.isUndead() and not creature.isPlayer() and not type(creature) == Cultist]
      humanEnemies = [creature for creature in creatureList if creature.isUndead() or creature.isPlayer()]
      targetRange = 1200
      targetEnemy = None
      if len(humanEnemies) > 0:
         for enemy in humanEnemies:
            distance = Vector2(enemy.getX() - self.getX(), enemy.getY() - self.getY()).magnitude()
            if self.getCollisionRect().inflate(self._visualRadius,self._visualRadius).clip(enemy.getCollisionRect()).size != (0,0) and distance < targetRange and enemy.getHitPoints() > 0:
               targetRange = distance
               targetEnemy = enemy
         if targetEnemy != None:
            if not self._cornered and self._hitPoints <= 5:
               self.flee(targetEnemy)
            else:
               self.attack(targetEnemy)
         elif not self._FSM == "moving":
            self.idle()
      else:
         self._cornered = False
      super().update(creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks)

   def go(self, targetPos):
      if self._FSM == "fleeing":
         super().go(targetPos)
      else:
         if self._pathingTimer <= 0:
            self._route = self._path.getPath((self._position[0] + self.getWidth() // 2, self._position[1] + self.getHeight() // 2), (targetPos[0] + self.getWidth() // 2,targetPos[1] + self.getHeight() // 2))
            self._pathingTimer = self._pathingTimerMax + random.random()/2
         if len(self._route) >= 2:
            if ((self._position[0] + self.getWidth() // 2)//16 * 16, (self._position[1] + self.getHeight() // 2)//16 * 16) == self._route[1]:
               super().go(self._route.pop(1))
            else:
               super().go(self._route[1])
         else:
            self.idle()
         
   def getFrameStatusOffset(self, flipped):
      self._heldWeapon.setRow(0)
      if self._FSM == "idle":
         if flipped == False:
            return Vector2(5,0)
         else:
            return Vector2(-5,0)
      elif self._FSM == "moving" or self._FSM == "fleeing":
         if flipped == False:
            if self._frame == 0:
               return Vector2(6,-1)
            else:
               return Vector2(1,-2)
         else:
            if self._frame == 0:
               return Vector2(-6,-1)
            else:
               return Vector2(-1,-2)
      elif self._FSM == "attacking":
         # slightly glitchy here
         if self.getCollisionRect().inflate(8,8).clip(self._targetObject.getCollisionRect()).size == (0,0):
            if flipped == False:
               if self._frame == 0:
                  return Vector2(6,-1)
               else:
                  return Vector2(1,-2)
            else:
               if self._frame == 0:
                  return Vector2(-6,-1)
               else:
                  return Vector2(-1,-2)
         else:
            if flipped == False:
               if self._frame == 0:
                  return Vector2(4,-3)
               else:
                  self._heldWeapon.setRow(1)
                  return Vector2(-10,1)
            else:
               if self._frame == 0:
                  return Vector2(-4,-3)
               else:
                  self._heldWeapon.setRow(1)
                  return Vector2(10,1)
      elif self._FSM == "dying" or self._FSM == "dead":
         self._heldWeapon.setRow(2)
         return Vector2(0,0)
      else:
         return Vector2(0,0)

class Soldier(Creature):
   def __init__(self, position):
      skin = random.choice(("soldier1.png", "soldier2.png", "soldier3.png"))
      super().__init__(skin, position)
      self._maxHitPoints = 16
      self._hitPoints = self._maxHitPoints
      self._experienceValue = 100
      self._strength = 1
      self._dexterity = 1
      self._defaultAttackDamage = 1 + self._strength
      self._attackDamage = self._defaultAttackDamage
      self._attackTimerMax /= 2
      self._attackTimer = self._attackTimerMax
      self._undead = False
      self._hasCorpse = True
      self._heldWeapon = Weapon("longsword", self._weaponOffset + self._position)
      self._equipableWeapons = Weapon.MARTIAL

   def update(self, creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks):
      self._path = path
      self._pathingTimer -= ticks
      self._allies = [creature for creature in creatureList if not creature.isUndead() and not creature.isPlayer() and not type(creature) == Cultist]
      humanEnemies = [creature for creature in creatureList if creature.isUndead() or creature.isPlayer()]
      targetRange = 1200
      targetEnemy = None
      if len(humanEnemies) > 0:
         for enemy in humanEnemies:
            distance = Vector2(enemy.getX() - self.getX(), enemy.getY() - self.getY()).magnitude()
            if self.getCollisionRect().inflate(self._visualRadius,self._visualRadius).clip(enemy.getCollisionRect()).size != (0,0) and distance < targetRange and enemy.getHitPoints() > 0:
               targetRange = distance
               targetEnemy = enemy
         if targetEnemy != None:
            if not self._cornered and self._hitPoints <= 5:
               self.flee(targetEnemy)
            else:
               self.attack(targetEnemy)
         elif not self._FSM == "moving":
            self.idle()
      else:
         self._cornered = False
      super().update(creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks)

   def go(self, targetPos):
      if self._FSM == "fleeing":
         super().go(targetPos)
      else:
         if self._pathingTimer <= 0:
            self._route = self._path.getPath((self._position[0] + self.getWidth() // 2, self._position[1] + self.getHeight() // 2), (targetPos[0] + self.getWidth() // 2,targetPos[1] + self.getHeight() // 2))
            self._pathingTimer = self._pathingTimerMax + random.random()/2
         if len(self._route) >= 2:
            if ((self._position[0] + self.getWidth() // 2)//16 * 16, (self._position[1] + self.getHeight() // 2)//16 * 16) == self._route[1]:
               super().go(self._route.pop(1))
            else:
               super().go(self._route[1])
         else:
            self.idle()
         
   def getFrameStatusOffset(self, flipped):
      self._heldWeapon.setRow(0)
      if self._FSM == "idle":
         if flipped == False:
            return Vector2(5,0)
         else:
            return Vector2(-5,0)
      elif self._FSM == "moving" or self._FSM == "fleeing":
         if flipped == False:
            if self._frame == 0:
               return Vector2(6,-1)
            else:
               return Vector2(1,-2)
         else:
            if self._frame == 0:
               return Vector2(-6,-1)
            else:
               return Vector2(-1,-2)
      elif self._FSM == "attacking":
         # slightly glitchy here
         if self.getCollisionRect().inflate(8,8).clip(self._targetObject.getCollisionRect()).size == (0,0):
            if flipped == False:
               if self._frame == 0:
                  return Vector2(6,-1)
               else:
                  return Vector2(1,-2)
            else:
               if self._frame == 0:
                  return Vector2(-6,-1)
               else:
                  return Vector2(-1,-2)
         else:
            if flipped == False:
               if self._frame == 0:
                  return Vector2(4,-3)
               else:
                  self._heldWeapon.setRow(1)
                  return Vector2(-10,1)
            else:
               if self._frame == 0:
                  return Vector2(-4,-3)
               else:
                  self._heldWeapon.setRow(1)
                  return Vector2(10,1)
      elif self._FSM == "dying" or self._FSM == "dead":
         self._heldWeapon.setRow(2)
         return Vector2(0,0)
      else:
         return Vector2(0,0)

class Archer(Creature):
   def __init__(self, position):
      skin = random.choice(("archer1.png", "archer2.png", "archer3.png"))
      super().__init__(skin, position)
      self._maxHitPoints = 16
      self._hitPoints = self._maxHitPoints
      self._experienceValue = 100
      self._dexterity = 2
      self._defaultAttackDamage = 1 + self._strength
      self._attackDamage = self._defaultAttackDamage
      self._attackTimerMax /= 2
      self._attackTimer = self._attackTimerMax
      self._undead = False
      self._hasCorpse = True
      self._heldWeapon = Weapon("longbow", self._weaponOffset + self._position)
      self._equipableWeapons = Weapon.MARTIAL
      self._visualRadius += 80

   def update(self, creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks):
      self._path = path
      self._pathingTimer -= ticks
      self._allies = [creature for creature in creatureList if not creature.isUndead() and not creature.isPlayer() and not type(creature) == Cultist]
      humanEnemies = [creature for creature in creatureList if creature.isUndead() or creature.isPlayer()]
      targetRange = 1200
      targetEnemy = None
      if len(humanEnemies) > 0:
         for enemy in humanEnemies:
            distance = Vector2(enemy.getX() - self.getX(), enemy.getY() - self.getY()).magnitude()
            if self.getCollisionRect().inflate(self._visualRadius,self._visualRadius).clip(enemy.getCollisionRect()).size != (0,0) and distance < targetRange and enemy.getHitPoints() > 0:
               targetRange = distance
               targetEnemy = enemy
         if targetEnemy != None:
            if not self._cornered and self._hitPoints <= 5:
               self.flee(targetEnemy)
            else:
               self.attack(targetEnemy)
         elif not self._FSM == "moving":
            self.idle()
      else:
         self._cornered = False
      super().update(creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks)

   def go(self, targetPos):
      if self._FSM == "fleeing":
         super().go(targetPos)
      else:
         if self._pathingTimer <= 0:
            self._route = self._path.getPath((self._position[0] + self.getWidth() // 2, self._position[1] + self.getHeight() // 2), (targetPos[0] + self.getWidth() // 2,targetPos[1] + self.getHeight() // 2))
            self._pathingTimer = self._pathingTimerMax + random.random()/2
         if len(self._route) >= 2:
            if ((self._position[0] + self.getWidth() // 2)//16 * 16, (self._position[1] + self.getHeight() // 2)//16 * 16) == self._route[1]:
               super().go(self._route.pop(1))
            else:
               super().go(self._route[1])
         else:
            self.idle()
         
   def getFrameStatusOffset(self, flipped):
      self._heldWeapon.setRow(0)
      if self._FSM == "idle":
         if flipped == False:
            return Vector2(5,0)
         else:
            return Vector2(-5,0)
      elif self._FSM == "moving" or self._FSM == "fleeing":
         if flipped == False:
            if self._frame == 0:
               return Vector2(6,-1)
            else:
               return Vector2(1,-2)
         else:
            if self._frame == 0:
               return Vector2(-6,-1)
            else:
               return Vector2(-1,-2)
      elif self._FSM == "attacking":
         # slightly glitchy here
         if self.getCollisionRect().inflate(8,8).clip(self._targetObject.getCollisionRect()).size == (0,0):
            if flipped == False:
               if self._frame == 0:
                  return Vector2(6,-1)
               else:
                  return Vector2(1,-2)
            else:
               if self._frame == 0:
                  return Vector2(-6,-1)
               else:
                  return Vector2(-1,-2)
         else:
            if flipped == False:
               if self._frame == 0:
                  return Vector2(4,-3)
               else:
                  self._heldWeapon.setRow(1)
                  return Vector2(-10,1)
            else:
               if self._frame == 0:
                  return Vector2(-4,-3)
               else:
                  self._heldWeapon.setRow(1)
                  return Vector2(10,1)
      elif self._FSM == "dying" or self._FSM == "dead":
         self._heldWeapon.setRow(2)
         return Vector2(0,0)
      else:
         return Vector2(0,0)

class Cultist(Spellcaster):
   def __init__(self, position):
      skin = "cultist.png"
      super().__init__(skin, position)
      self._maxHitPoints = 9
      self._hitPoints = self._maxHitPoints
      self._moveFrames = 4
      self._attackFrames = 3
      self._castFrames = 2
      self._maxMagicPoints = 6
      self._magicPoints = self._maxMagicPoints
      self._experienceValue = 25
      self._dexterity = 1
      self._spellBonus = 1
      self._spellList = ["healing word"]
      self._undead = False
      self._hasCorpse = True
      self._heldWeapon = Weapon("dagger", self._weaponOffset + self._position)
      self._equipableWeapons = ["dagger"]

      self._visualRadius = 744

      self._magicCircle = MagicCircle(self._magicOffset + self._position, "demonic")

   def update(self, creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks):
      self._path = path
      self._pathingTimer -= ticks
      self._allies = [creature for creature in creatureList if creature.isPlayer() or type(creature) == Cultist]
      enemies = [creature for creature in creatureList if not creature.isPlayer() and creature.isUndead() and not creature.isControlled()]
      enemies = [enemy for enemy in enemies if self.getCollisionRect().inflate(self._visualRadius,self._visualRadius).clip(enemy.getCollisionRect()).size != (0,0)]
      checkProtag = [ally for ally in self._allies if ally.isPlayer()]
      if len(checkProtag) > 0:
         # cultists heal you before anyone else
         protag = checkProtag[0]
      else:
         protag = None
      targetRange = 1200
      targetAlly = None
      targetEnemy = None
      targetHitPointPercent = 1.0
      if protag != None and protag.getHitPoints() >=1 and protag.getHitPoints()/protag.getMaxHitPoints() < 1:
         hpThreshold = 1
         targetAlly = protag
      else:
         hpThreshold = 2 + self._spellBonus
         for ally in self._allies:
            if self.getCollisionRect().inflate(self._visualRadius,self._visualRadius).clip(ally.getCollisionRect()).size != (0,0) and ally.getHitPoints() >=1 and ally.getHitPoints()/ally.getMaxHitPoints() < targetHitPointPercent:
               targetAlly = ally
               targetHitPointPercent = ally.getHitPoints()/ally.getMaxHitPoints()
      if targetAlly != None and self._magicPoints >= 2 and targetAlly.getMaxHitPoints() - targetAlly.getHitPoints() >= hpThreshold and targetAlly.getState() != "dying" and targetAlly.getState() != "dead":
         if self.getCollisionRect().inflate(200,200).clip(targetAlly.getCollisionRect()).size == (0,0):
            self.move((targetAlly.getX(), targetAlly.getY()))
         elif self.getCollisionRect().inflate(144,144).clip(targetAlly.getCollisionRect()).size == (0,0) and self._FSM != "casting":
            self.move((targetAlly.getX(), targetAlly.getY()))
         elif self._FSM != "casting":
            # healing word - maybe adjust this in the future
            self._spellSelectedIndex = self._spellList.index("healing word")
            self.cast(targetAlly)

      elif len(enemies) > 0:
         for enemy in enemies:
            distance = Vector2(enemy.getX() - self.getX(), enemy.getY() - self.getY()).magnitude()
            if distance < targetRange and enemy.getHitPoints() > 0:
               targetRange = distance
               targetEnemy = enemy
         if targetEnemy != None:
            # cultists prefer to flee instead of fight
            if not self._cornered:
               self.flee(targetEnemy)
            else:
               self.attack(targetEnemy)
               
         elif not self._FSM == "moving":
            self.idle()
      else:
         self._cornered = False
      super().update(creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks)

   def go(self, targetPos):
      if self._FSM == "fleeing":
         super().go(targetPos)
      else:
         if self._pathingTimer <= 0:
            self._route = self._path.getPath((self._position[0] + self.getWidth() // 2, self._position[1] + self.getHeight() // 2), (targetPos[0] + self.getWidth() // 2,targetPos[1] + self.getHeight() // 2))
            self._pathingTimer = self._pathingTimerMax + random.random()/2
         if len(self._route) >= 2:
            if ((self._position[0] + self.getWidth() // 2)//16 * 16, (self._position[1] + self.getHeight() // 2)//16 * 16) == self._route[1]:
               super().go(self._route.pop(1))
            else:
               super().go(self._route[1])
         else:
            self.idle()
         
   def getFrameStatusOffset(self, flipped):
      self._heldWeapon.setRow(0)
      if self._FSM == "idle":
         if flipped == False:
            return Vector2(5,0)
         else:
            return Vector2(-5,0)
      elif self._FSM == "moving" or self._FSM == "fleeing":
         if flipped == False:
            if self._frame == 0 or self._frame == 2:
               return Vector2(2,0)
            elif self._frame == 1:
               return Vector2(4,-9)
            else:
               return Vector2(1,1)
               
         else:
            if self._frame == 0 or self._frame == 2:
               return Vector2(-2,0)
            elif self._frame == 1:
               return Vector2(-4,-9)
            else:
               return Vector2(-1,1)
      elif self._FSM == "attacking":
         # slightly glitchy here
         if self.getCollisionRect().inflate(8,8).clip(self._targetObject.getCollisionRect()).size == (0,0):
            if flipped == False:
               if self._frame == 0 or self._frame == 2:
                  return Vector2(2,0)
               elif self._frame == 1:
                  return Vector2(4,-9)
               else:
                  return Vector2(1,1)
                  
            else:
               if self._frame == 0 or self._frame == 2:
                  return Vector2(-2,0)
               elif self._frame == 1:
                  return Vector2(-4,-9)
               else:
                  return Vector2(-1,1)
         else:
            if flipped == False:
               if self._frame == 0:
                  return Vector2(2,-2)
               elif self._frame == 1:
                  return Vector2(5,-7)
               else:
                  self._heldWeapon.setRow(1)
                  return Vector2(-10,3)
            else:
               if self._frame == 0:
                  return Vector2(-2,-2)
               elif self._frame == 1:
                  return Vector2(-5,-7)
               else:
                  self._heldWeapon.setRow(1)
                  return Vector2(10,3)
      elif self._FSM == "casting":
         self._heldWeapon.setRow(2)
         if flipped == False:
            return Vector2(4,1)
         else:
            return Vector2(-4,1)
      elif self._FSM == "dying" or self._FSM == "dead":
         self._heldWeapon.setRow(2)
         return Vector2(0,0)
      else:
         return Vector2(0,0)

class King(Creature):
   def __init__(self, position):
      skin = "king.png"
      super().__init__(skin, position)
      self._maxHitPoints = 1
      self._hitPoints = self._maxHitPoints
      self._experienceValue = 0
      self._undead = False
      self._hasCorpse = True
      self._equipableWeapons = []

      self._crownOffset = Vector2(1,-9)
      self._crown = Crown(self._crownOffset+self._position)
      

   def update(self, creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks):
      self._path = path
      self._pathingTimer -= ticks
      self._allies = [creature for creature in creatureList if not creature.isUndead() and not creature.isPlayer() and not type(creature) == Cultist]
      localAllies = [ally for ally in self._allies if self.getCollisionRect().inflate(200,200).clip(ally.getCollisionRect()).size != (0,0)]
      humanEnemies = [creature for creature in creatureList if creature.isUndead() or creature.isPlayer()]
      localHumanEnemies = [enemy for enemy in humanEnemies if self.getCollisionRect().inflate(self._visualRadius,self._visualRadius).clip(enemy.getCollisionRect()).size != (0,0)]
      targetRange = 1200
      targetEnemy = None
      if len(localHumanEnemies) > 0:
         for enemy in localHumanEnemies:
            distance = Vector2(enemy.getX() - self.getX(), enemy.getY() - self.getY()).magnitude()
            if distance < targetRange and enemy.getHitPoints() > 0:
               targetRange = distance
               targetEnemy = enemy
         if targetEnemy != None:
            # king doesn't fight
            # with 1 hp hopefully the fact that he has no combat animations will not be noticed
            self.flee(targetEnemy)
         elif not self._FSM == "moving":
            self.idle()
      super().update(creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks)

      # janky crown stuff
      flipped = self._FSM.isFacing("right")
      if self._FSM == "moving" or self._FSM == "fleeing":
         if self._frame == 0:
            if not flipped:
               self._crownOffset = Vector2(2,-9)
            else:
               self._crownOffset = Vector2(-2,-9)
         else:
            if not flipped:
               self._crownOffset = Vector2(1,-8)
            else:
               self._crownOffset = Vector2(-1,-8)
      else:
         if not flipped:
            self._crownOffset = Vector2(1,-9)
         else:
            self._crownOffset = Vector2(-1,-9)
      self._crown.setPosition(self._crownOffset+self._position)
      self._crown.update(ticks, flipped)

   def go(self, targetPos):
      if self._FSM == "fleeing":
         super().go(targetPos)
      else:
         if self._pathingTimer <= 0:
            self._route = self._path.getPath((self._position[0] + self.getWidth() // 2, self._position[1] + self.getHeight() // 2), (targetPos[0] + self.getWidth() // 2,targetPos[1] + self.getHeight() // 2))
            self._pathingTimer = self._pathingTimerMax + random.random()/2
         if len(self._route) >= 2:
            if ((self._position[0] + self.getWidth() // 2)//16 * 16, (self._position[1] + self.getHeight() // 2)//16 * 16) == self._route[1]:
               super().go(self._route.pop(1))
            else:
               super().go(self._route[1])
         else:
            self.idle()

   def draw(self, surface):
      # added for janky hat purposes and nothing else
      super().draw(surface)
      if not self._FSM == "dying" and not self._FSM == "dead":
         self._crown.draw(surface)

class Crown(Mobile):
   def __init__(self, position):
      super().__init__("hat.png", position)
      self._nFrames = 1
      self._row = 0
