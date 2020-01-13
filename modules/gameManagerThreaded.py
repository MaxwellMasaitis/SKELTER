from .pauser import Pauser
from .levelManagerThreaded import LevelManagerThreaded
from .gameThreadedFSM import GameState
# this is only here for the loading screen
from .frameManager import FrameManager

class GameManagerThreaded(object):

    def __init__(self, screenSize):
        self._pauser = Pauser(screenSize)
        self._level = LevelManagerThreaded("level0.txt")
        self._FSM = GameState()
        self._FSM.manageState("nextLevel")
        self._currentLevel = -1

    def draw(self, surface):
        if self._FSM == "loading":
            # draw loading screen
            surface.fill((0,0,0))
            surface.blit(FrameManager.getInstance().getFrame("loading.png"), (0,0))
        else:
            if self._FSM in ["paused", "running"]:
                self._level.draw(surface)
            if self._FSM == "paused":
                self._pauser.draw(surface)

    def handleEvent(self, event):
        if self._FSM == "paused":
            self._pauser.handleEvent(event)

            if not self._pauser.isActive():
                self._FSM.manageState("unpause")

        elif self._FSM == "running":
            self._pauser.handleEvent(event)
            
            if self._pauser.isActive():
                self._FSM.manageState("pause")
            else:
                levelDone = self._level.handleEvent(event)

                if levelDone:
                    self._FSM.manageState("nextLevel")

    def update(self, ticks, screenSize, scale):
        if self._FSM == "running":
            levelDone = self._level.update(ticks, screenSize, scale)

            if levelDone:
                self._FSM.manageState("nextLevel")

        elif self._FSM == "startLoading":
            self._currentLevel += 1
            # number of levels
            self._currentLevel %= 1

            self._level = LevelManagerThreaded("level" + str(self._currentLevel) + ".txt")
            self._level.load()
            self._FSM.manageState("load")

        elif self._FSM == "loading" and self._level.isLoaded():
            self._FSM.manageState("doneLoading")
