import pygame
import os
from .mobile import Mobile

class SelectionArrow(Mobile):
   def __init__(self, position, color):
      if color == "red":
         image = "selectionArrow1.png"
      elif color == "blue":
         image = "selectionArrow2.png"
      super().__init__(image, position)
      self._nFrames = 4
