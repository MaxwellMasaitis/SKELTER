import pygame
import os
from .vector2D import Vector2
from .mobile import Mobile
import math
import numpy as np
import numpy.linalg as la

class Projectile(Mobile):
   def __init__(self, name, position, targetPos, owner, damage, special):
      self._name = name
      super().__init__(name + ".png", position)
      self._startPos = self._position
      self._targetPos = targetPos
      self._velocity = Vector2(self._targetPos[0] - self._position[0], self._targetPos[1] - self._position[1]).normalized() * 6.0
      self._owner = owner
      self._damage = damage
      self._special = special
      # decays based on distance instead of time now
##      self._lifeTime = 1.0
      # this math picks the sprite based on the direction the projectile is headed, since I didn't want to learn pygame's rotate.
      if self._velocity[0] != 0:
         theta = math.degrees(math.atan(self._velocity[1]/self._velocity[0]))
      else:
         if self._velocity[1] >= 0:
            self._row = 4
         else:
            self._row = 0
      if self._velocity[0] < 0:
         if theta >= 67.5:
            self._row = 0
         elif theta >= 22.5:
            self._row = 1
         elif theta >= -22.5:
            self._row = 2
         elif theta >= -67.5:
            self._row = 3
         else:
            self._row = 4
      elif self._velocity[0] > 0:
         if theta >= 67.5:
            self._row = 4
         elif theta >= 22.5:
            self._row = 5
         elif theta >= -22.5:
            self._row = 6
         elif theta >= -67.5:
            self._row = 7
         else:
            self._row = 0
      
      self._nFrames = 1
      # spell projectiles are animated
      if self._name == "firebolt":
         self._nFrames = 2
      elif self._name == "gravebolt":
         self._nFrames = 2
      self._hit = False

   def hasHit(self):
      return self._hit

   def update(self, creatureList, collisionList, worldSize, ticks):
##      self._lifeTime -= ticks
##      if self._lifeTime <= 0:
##         self._hit = True
      # distance-based decay
      if math.sqrt(math.pow(self._position[0] - self._startPos[0] ,2) + math.pow(self._position[1] - self._startPos[1],2)) >= 488:
         self._hit = True

      # hitting things
      for creature in creatureList:
         if not self._hit and creature.getCollisionRect().colliderect(self.getCollisionRect()) and not creature.getState() == "dying" and not creature.getState() == "dead" and creature != self._owner and creature not in self._owner.getAllies():
            creature.hurt(self._damage, self._special)
            self._hit = True
      for collider in collisionList:
         if not self._hit and collider.getCollisionRect().colliderect(self.getCollisionRect()):
            self._hit = True
      # world border detection
      if self._position[0] < 0 or self._position[0] + self.getWidth() > worldSize[0]:
         self._hit = True
      if self._position[1] < 0 or self._position[1] + self.getHeight() > worldSize[1]:
         self._hit = True
      super().update(ticks, False)

   @classmethod
   def leadShot(cls, q, p, v):
      # LEADING SHOTS!
      # q is own position, p is target position, v is target velocity
      # 6.0 is projectile speed. keep that in mind if variable ones are to be used later
      # via
      # https://answers.unity.com/questions/429234/constant-time-way-to-find-intersection-of-two-obje.html
      # https://newtonexcelbach.com/2014/03/01/the-angle-between-two-vectors-python-version/
      pq = Vector2(q[0] - p[0], q[1] - p[1])
      vA = np.array(list(v))
      pqA = np.array(list(pq))
      a = 6.0**2 - v.magnitude()**2
      b = 2 * v.magnitude() * pq.magnitude() * math.cos(np.arctan2(la.norm(np.cross(pqA,vA)),np.dot(pqA,vA)))
      c = -(pq.magnitude())**2
      if a == 0:
         return 0
      else:
         zP = (-b + math.sqrt(b**2 - 4*a*c))/(2*a)
         zM = (-b - math.sqrt(b**2 - 4*a*c))/(2*a)
         if zP >= 0 and zM >= 0:
            z = min(zP,zM)
         else:
            z = max(zP,zM)
         return z
