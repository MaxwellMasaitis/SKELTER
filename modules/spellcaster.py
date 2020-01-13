from .soundManager import SoundManager
from .vector2D import Vector2
from .mobile import Mobile
from .creature import Creature
from .projectile import Projectile
from .spell import Spell
from .magicCircle import MagicCircle

class Spellcaster(Creature):
    def __init__(self, imageName, position):
        super().__init__(imageName, position)
        self._maxMagicPoints = 0
        self._magicPoints = self._maxMagicPoints
        self._spellBonus = 0
        # spells?
        self._spellList = []
        self._spellSelectedIndex = 0
        self._currentSpell = None
        # mess with this
        self._magicRegenTimerMax = 5.0
        self._magicRegenTimer = self._magicRegenTimerMax
        self._castTimer = 1.2
        self._castFrames = 4
        self._magicOffset = Vector2(-16,-16)
        self._magicCircle = MagicCircle(self._magicOffset + self._position)
       # may need to change later
       
    def cast(self, spellTarget, spellGoal = None):
        # cast action, like move and attack in creature
        self._currentSpell = Spell(self, self.getSpellList()[self.getSpellIndex()],spellTarget,spellGoal)
        self._castTimer = self._currentSpell.getCastTime()
        self._FSM.manageState("cast")

    def getMagicPoints(self):
        return self._magicPoints

    def expendMagicPoints(self, amount):
        amount = abs(amount)
        self._magicPoints -= amount

    def getMaxMagicPoints(self):
        return self._maxMagicPoints

    def getSpellBonus(self):
        return self._spellBonus

    def getSpellList(self):
        return self._spellList

    def getSpellIndex(self):
        return self._spellSelectedIndex

    def update(self, creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks):
        # mp regens over time
        if self._magicPoints < self._maxMagicPoints:
            self._magicRegenTimer -= ticks
            if self._magicRegenTimer <= 0:
                self._magicPoints += 1
                self._magicRegenTimer = self._magicRegenTimerMax

        if self._FSM == "casting":
            if self._castTimer == self._currentSpell.getCastTime():
                SoundManager.getInstance().playSound("spellcast.wav")
            if self._targetObject != None:
                self._targetPos = (self._targetObject.getX(), self._targetObject.getY())
                # make sure projectile spells are led by NPCs using them
                # player shouldn't ever see this, since it shouldn't use targetObject
                if self._spellList[self._spellSelectedIndex] == "gravebolt" or self._spellList[self._spellSelectedIndex] == "firebolt":
                    z = Projectile.leadShot(self._position, self._targetPos, self._targetObject.getVelocity())
                    self._targetPos = (self._targetPos[0] + z * self._targetObject.getVelocity()[0], self._targetPos[1] + z * self._targetObject.getVelocity()[1])
            self._magicCircle.setPosition(self._magicOffset + self._position)
            self._magicCircle.update(ticks)
            self._velocity = Vector2(0,0)

            self._row = 4
            self._nFrames = self._castFrames
            self._castTimer -= ticks
            if self._castTimer <= 0: 
                self._castTimer = self._currentSpell.getCastTime()
                self._currentSpell.cast()
                self._FSM.manageState("stopMoving")

        super().update(creatureList, collisionList, weaponsList, projectilesList, waterTiles, worldSize, path, ticks)

    def draw(self, surface):
        if self._FSM == "casting":
            self._magicCircle.draw(surface)
        super().draw(surface)


