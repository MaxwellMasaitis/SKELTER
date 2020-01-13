from .drawable import Drawable
from .animated import Animated
from .vector2D import Vector2
from .soundManager import SoundManager

class Gate(Animated):
   def __init__(self, imageName, position, cost):
      super().__init__(imageName, position)
      self._nFrames = 1
      self._cost = cost
      self._hitPoints = cost * 8
      self._open = False
      self._attackers = []
      #self._detectionRect = Vector2(0,self.getHeight()) + self.getCollisionRect()

      # number drawing stuff
      self._uiSlash = Drawable('uiSlash.png', (self._position[0] + self.getWidth()//2 - 3, self._position[1] + self.getHeight()//2), (0,0), True)
      self._uiNumbers = []
      costText = str(self._cost)
      for digit in range(len(costText)):
         self._uiNumbers.append(Drawable('numbers.png', (self._position[0] + self.getWidth()//2 + 3 + digit*6,self._position[1] + self.getHeight()//2), (int(costText[digit]),0), True))

   def hurt(self, amount, special):
      # gate damage
      if len(self._attackers) >= self._cost:
         amount = abs(amount)
         self._hitPoints -= amount
         SoundManager.getInstance().playSound(special +'_damage.wav')
         if self._hitPoints < 0:
            self._hitPoints = 0

   def isOpen(self):
      return self._open

   def getCost(self):
      return self._cost

   def getHitPoints(self):
      return self._hitPoints

   def draw(self, surface):
      super().draw(surface)
      # draw numbers for the gate cost and current attackers
      attackerCount = len(self._attackers)
      if attackerCount > 0 and not self._open:
         attackerText = str(attackerCount)
         for digit in range(len(attackerText)):
            fromRight = len(attackerText) - digit
            Drawable('numbers.png', (self._position[0] + self.getWidth()//2 - 3 - fromRight*6,self._position[1] + self.getHeight()//2), (int(attackerText[digit]),0), True).draw(surface)
         self._uiSlash.draw(surface)
         for number in self._uiNumbers:
            number.draw(surface)
   
   def update(self, creatures, ticks):
      super().update(ticks, False)
##      undead.getCollisionRect().clip(self._detectionRect).size != (0,0)
      self._attackers = [undead for undead in creatures if undead.isUndead() and undead.isControlled() and undead.getTargetObject() == self]
      if self._hitPoints <= 0 and not self._open:
         self._open = True
         self._row = 1
         # play breaking sound here?
