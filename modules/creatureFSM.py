
# not 100% sure about all this
class CreatureFSM(object):
   def __init__(self, state="idle"):
      self._state = state
      self._facing = "left"
      


   def manageState(self, action):
      # decide whether to flip sprite
      if action in ["left", "right"]:
         self._setFacing(action)
         
      # idle when stopped
      elif action == "stopMoving" and self._state != "dying" and self._state != "dead":
         self._state = "idle"
      
      elif action == "move" and self._state != "dying" and self._state != "dead":
         self._state = "moving"

      elif action == "flee" and self._state != "dying" and self._state != "dead":
         self._state = "fleeing"

      elif action == "attack" and self._state != "dying" and self._state != "dead":
         self._state = "attacking"

      elif action == "follow" and self._state != "dying" and self._state != "dead":
         self._state = "following"

      elif action == "cast" and self._state != "dying" and self._state != "dead":
         self._state = "casting"

      elif action == "die":
         self._state = "dying"

      elif action == "fullyDie":
         self._state = "dead"
   
   
   def _setFacing(self, direction):
      self._facing = direction
      
   
   def _setState(self, state):
      self._state = state
      
   
   def isFacing(self, facing):
      return self._facing == facing
      
   
   def __eq__(self, state):
      return self._state == state

   def __str__(self):
      return self._state
   
