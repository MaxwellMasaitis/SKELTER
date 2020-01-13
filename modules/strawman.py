import pygame
import os
from .vector2D import Vector2
from .creature import Creature

# for testing purposes

class Strawman(Creature):
   def __init__(self, position):
      super().__init__("strawman.png", position)
      self._maxVelocity = 0
      self._maxHitPoints = 100
      self._hitPoints = self._maxHitPoints
      self._experienceValue = 800
      self._defaultAttackDamage = 0
      self._attackDamage = self._defaultAttackDamage
      self._deathFrames = 4

   def update(self, creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks):
      self._FSM.manageState("stopMoving")
      super().update(creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks)
