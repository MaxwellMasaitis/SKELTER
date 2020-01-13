
from .animated import Animated
from .vector2D import Vector2

class Mobile(Animated):
   def __init__(self, imageName, position):
      super().__init__(imageName, position)
      self._velocity = Vector2(0,0)
   
   def update(self, ticks, isFlipped = False):
      super().update(ticks, isFlipped)
      newPosition = self.getPosition() + self._velocity
      
      self.setPosition(newPosition)

   def getVelocity(self):
      return self._velocity
