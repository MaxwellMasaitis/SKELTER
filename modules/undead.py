import pygame
import os
from .vector2D import Vector2
from .creature import Creature
from .weapon import Weapon
import random

# see also humans for ai stuff

class Zombie(Creature):
   def __init__(self, position):
      super().__init__("zombie.png", position)
      self._maxVelocity = 2.0
      self._maxHitPoints = 22
      self._hitPoints = self._maxHitPoints
      self._strength = 1
      self._dexterity = -2
      self._defaultAttackDamage = 3 + self._strength
      self._attackDamage = self._defaultAttackDamage
      self._undead = True
      self._immunity = ["poison"]
      self._moveFrames = 3

      # zombies were even tougher before, this is disabled now
      # random chance to not die based on damage taken
      
##   def hurt(self, amount, special = None):
##      # undead fortitude ~ change this as tests indicate
##      super().hurt(amount, special)
##      if self._hitPoints <= 0 and special != "holy":
##         check = random.uniform(0,1)
##         if check > (1 + amount) * .05:
##            self._hitPoints = 1

   def update(self, creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks):
      self._allies = []
      allLiving = [creature for creature in creatureList if not creature.isUndead()]
      if not self._controlled:
         # uncontrolled undead attack the living
         targetRange = 1200
         targetEnemy = None
         if len(allLiving) > 0:
            for enemy in allLiving:
               distance = Vector2(enemy.getX() - self.getX(), enemy.getY() - self.getY()).magnitude()
               if self.getCollisionRect().inflate(self._visualRadius,self._visualRadius).clip(enemy.getCollisionRect()).size != (0,0) and distance < targetRange and enemy.getHitPoints() > 0:
                  targetRange = distance
                  targetEnemy = enemy
            if targetEnemy != None:
               self.attack(targetEnemy)
            elif not self._FSM == "moving":
               self.idle()
      else:
         self._allies = [creature for creature in creatureList if creature.isControlled() or creature.isPlayer()]
      super().update(creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks)

class Skeleton(Creature):
   def __init__(self, position):
      super().__init__("skeleton.png", position)
      self._maxHitPoints = 13
      self._hitPoints = self._maxHitPoints
      self._dexterity = 2
      self._undead = True
      self._defaultSpecialDamage = "slashing"
      self._specialDamage = self._defaultSpecialDamage
      self._weakness = ["bludgeoning"]
      self._immunity = ["poison"]
      self._attackFrames = 3
      self._equipableWeapons = Weapon.MARTIAL

   def update(self, creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks):
      self._path = path
      self._pathingTimer -= ticks
      self._allies = []
      allLiving = [creature for creature in creatureList if not creature.isUndead()]
      if not self._controlled:
         targetRange = 1200
         targetEnemy = None
         if len(allLiving) > 0:
            for enemy in allLiving:
               distance = Vector2(enemy.getX() - self.getX(), enemy.getY() - self.getY()).magnitude()
               if self.getCollisionRect().inflate(self._visualRadius,self._visualRadius).clip(enemy.getCollisionRect()).size != (0,0) and distance < targetRange and enemy.getHitPoints() > 0:
                  targetRange = distance
                  targetEnemy = enemy
            if targetEnemy != None:
               self.attack(targetEnemy)
            elif not self._FSM == "moving":
               self.idle()
      else:
         self._allies = [creature for creature in creatureList if creature.isControlled() or creature.isPlayer()]
      super().update(creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks)

   def go(self, targetPos):
      # same basic setup as humans, except undead do not flee
      if self._pathingTimer <= 0:
         self._route = self._path.getPath((self._position[0] + self.getWidth() // 2, self._position[1] + self.getHeight() // 2), (targetPos[0] + self.getWidth() // 2,targetPos[1] + self.getHeight() // 2))
         # slightly adjusted to make them easier to control
         self._pathingTimer = self._pathingTimerMax + random.random()/2 -0.6
      if len(self._route) >= 2:
         # since we use a framerule
         if ((self._position[0] + self.getWidth() // 2)//16 * 16, (self._position[1] + self.getHeight() // 2)//16 * 16) == self._route[1]:
            super().go(self._route.pop(1))
         else:
            super().go(self._route[1])
      elif self._FSM != "following" and self._FSM != "attacking":
         self.idle()
         
   def getFrameStatusOffset(self, flipped):
      # for holding weapons
      self._heldWeapon.setRow(0)
      if self._FSM == "idle":
         if flipped == False:
            return Vector2(0,-2)
         else:
            return Vector2(0,-2)
      elif self._FSM == "moving" or self._FSM == "following":
         if flipped == False:
            if self._frame == 0:
               return Vector2(0,-2)
            else:
               return Vector2(0,-1)
         else:
            if self._frame == 0:
               return Vector2(0,-2)
            else:
               return Vector2(0,-1)
      elif self._FSM == "attacking":
         # slightly glitchy here
         if self.getCollisionRect().inflate(8,8).clip(self._targetObject.getCollisionRect()).size == (0,0):
            if flipped == False:
               if self._frame == 0:
                  return Vector2(0,-2)
               else:
                  return Vector2(0,-1)
            else:
               if self._frame == 0:
                  return Vector2(0,-2)
               else:
                  return Vector2(0,-1)
         else:
            if flipped == False:
               if self._frame == 0:
                  return Vector2(1,-2)
               elif self._frame == 1:
                  return Vector2(-1,-2)
               else:
                  self._heldWeapon.setRow(1)
                  return Vector2(-6,2)
            else:
               if self._frame == 0:
                  return Vector2(-1,-2)
               elif self._frame == 1:
                  return Vector2(1,-2)
               else:
                  self._heldWeapon.setRow(1)
                  return Vector2(6,2)
      elif self._FSM == "dying" or self._FSM == "dead":
         self._heldWeapon.setRow(2)
         return Vector2(0,0)
      else:
         return Vector2(0,0)

