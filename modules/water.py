import pygame
from .animated import Animated
from .vector2D import Vector2

class Water(Animated):
   def __init__(self, position):
      super().__init__("water.png", position)
      self._nFrames = 4

   def getCollisionRect(self):
      # just didn't like touching the water so easily
      # iffy functionality
      newRect = super().getCollisionRect().inflate(-7,-7)
      return newRect
