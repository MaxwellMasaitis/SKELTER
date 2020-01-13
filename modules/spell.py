import pygame
import os
from .vector2D import Vector2
from .projectile import Projectile
from .undead import *

class Spell(object):
   def __init__(self, caster, spellName, spellData, spellGoal):
      self._caster = caster
      self._spellName = spellName
      self._spellData = spellData
      self._spellGoal = spellGoal
      self._castTime = 1.5
      if self._spellName == "gravebolt":
         # to get the player out of hairy situations
         self._castTime = 0.9

   def cast(self):
      if self._spellName == "animate dead":
         # turns corpses into undead
         # spellData is a list of selected corpses, spellGoal is the creature list
         for corpse in self._spellData:
            if self._caster.getCollisionRect().inflate(200,200).clip(corpse.getCollisionRect()).size != (0,0) and self._caster.getMagicPoints() >= 1:
               self._caster.expendMagicPoints(1)
               if corpse.getKind() == "skeleton":
                  skeleton = Skeleton(corpse.getPosition())
                  skeleton.setControlled(True)
                  self._spellGoal.append(skeleton)
               else:
                  zombie = Zombie(corpse.getPosition())
                  zombie.setControlled(True)
                  self._spellGoal.append(zombie)
               corpse.expend()
         self._spellData[:] = []
      elif self._spellName == "unearth":
         # opens up graves
         # spellData is a list of selected graves, spellGoal is a list of corpses
         for grave in self._spellData:
            if self._caster.getCollisionRect().inflate(200,200).clip(grave.getCollisionRect()).size != (0,0):
               corpse = grave.dig()
               self._spellGoal.append(corpse)
         self._spellData[:] = []
      elif self._spellName == "healing word":
         # heals a target
         # spellData is a creature, no spellGoal
         if self._caster.getCollisionRect().inflate(200,200).clip(self._spellData.getCollisionRect()).size != (0,0) and self._caster.getMagicPoints() >= 2:
            self._caster.expendMagicPoints(2)
            self._spellData.heal(2+self._caster.getSpellBonus())
      elif self._spellName == "firebolt":
         # fires a firey projectile
         # spellData is projectiles list, no spellGoal
         # player can use it as is, make sure it works for NPC spellcasters too
         self._spellData.append(Projectile("firebolt", (self._caster.getX()+self._caster.getWidth()//2, self._caster.getY()+self._caster.getHeight()//2), self._caster.getTargetPos(), self._caster, 5, "fire"))
      elif self._spellName == "gravebolt":
         # fires a dark projectile
         # spellData is projectiles list, no spellGoal
         # player can use it as is, make sure it works for NPC spellcasters too
         self._spellData.append(Projectile("gravebolt", (self._caster.getX()+self._caster.getWidth()//2, self._caster.getY()+self._caster.getHeight()//2), self._caster.getTargetPos(), self._caster, 5, "necrotic"))

   def getCastTime(self):
      return self._castTime
