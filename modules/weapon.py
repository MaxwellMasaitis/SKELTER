import pygame
import os
from .mobile import Mobile
import random

class Weapon(Mobile):
   SIMPLE = ["club","dagger","handaxe","shovel","spear","shortbow"]
   MARTIAL = SIMPLE + ["shortsword","longsword","longbow"]
   def __init__(self, name, position):
      # weapons and damage
      self._flipped = random.choice([True, False])
      self._name = name
      super().__init__(name + ".png", position)
      self._row = 2
      self._nFrames = 1
      if self._name == "club":
         self._damage = 2
         self._bonus = "strength"
         self._special = "bludgeoning"
         self._ranged = False
      elif self._name == "dagger":
         self._damage = 2
         self._bonus = "either"
         self._special = "piercing"
         self._ranged = False
      elif self._name == "handaxe":
         self._damage = 3
         self._bonus = "strength"
         self._special = "slashing"
         self._ranged = False
      elif self._name == "shovel":
         self._damage = 3
         self._bonus = "strength"
         self._special = "bludgeoning"
         self._ranged = False
      elif self._name == "spear":
         self._damage = 4
         self._bonus = "strength"
         self._special = "piercing"
         self._ranged = False
      elif self._name == "shortsword":
         self._damage = 3
         self._bonus = "either"
         self._special = "piercing"
         self._ranged = False
      elif self._name == "longsword":
         self._damage = 5
         self._bonus = "strength"
         self._special = "slashing"
         self._ranged = False
      elif self._name == "shortbow":
         self._damage = 3
         self._bonus = "dexterity"
         self._special = "piercing"
         self._ranged = True
      elif self._name == "longbow":
         self._damage = 4
         self._bonus = "dexterity"
         self._special = "piercing"
         self._ranged = True

   def setRow(self, index):
      self._row = index

   def getName(self):
      return self._name

   def getDamage(self):
      return self._damage

   def getSpecial(self):
      # damage types
      return self._special

   def getBonus(self):
      return self._bonus

   def isRanged(self):
      return self._ranged

   def update(self, ticks, flipped = None):
      if flipped != None:
         self._flipped = flipped
      super().update(ticks, self._flipped)

