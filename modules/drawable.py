import pygame
from pygame import image
import os
from .frameManager import FRAMES
from .vector2D import Vector2

class Drawable(object):
   WINDOW_OFFSET = (0,0)
   
   def __init__(self, imageName, position, offset=None, worldBound = True):
      self._imageName = imageName

      if imageName != "":
         # Let frame manager handle loading the image
         self._image = FRAMES.getFrame(self._imageName, offset)

      self._position = Vector2(position[0], position[1])
      self._worldBound = worldBound

   @classmethod
   def updateOffset(cls, trackingObject, screenSize, worldSize, rawMousePos):
      interp = (1 - rawMousePos[0] / screenSize[0], 1 - rawMousePos[1] / screenSize[1])
      adjMousePos = cls.adjustMousePos(rawMousePos)
      cls.WINDOW_OFFSET = (max(0, \
                                    min((trackingObject.getX() + adjMousePos[0]) / 2 + \
                                        interp[0] * (trackingObject.getWidth() // 2) - \
                                        (screenSize[0] // 2), \
                                        worldSize[0] - screenSize[0])), \
                                max(0, \
                                    min((trackingObject.getY() + adjMousePos[1]) / 2 + \
                                        interp[1] * (trackingObject.getHeight() // 2) - \
                                        (screenSize[1] // 2), \
                                        worldSize[1] - screenSize[1])))

   @classmethod
   def adjustMousePos(cls, mousePos):
      return (mousePos[0] + cls.WINDOW_OFFSET[0], mousePos[1] + cls.WINDOW_OFFSET[1])

   def getX(self):
      return self._position[0]

   def getY(self):
      return self._position[1]

   def getWidth(self):
      return self._image.get_width()

   def getHeight(self):
      return self._image.get_height()
   
   def getPosition(self):
      return self._position

   def setPosition(self, newPosition):
      self._position = newPosition
      
   def getSize(self):
      return self._image.get_size()

   def getCollisionRect(self):
      newRect =  self._position + self._image.get_rect()
      return newRect
   
   def draw(self, surface):
      if self._worldBound == True:
         surface.blit(self._image, (self._position[0] - self.WINDOW_OFFSET[0], self._position[1] - self.WINDOW_OFFSET[1]))
      else:
         surface.blit(self._image, (self._position[0], self._position[1]))
     
