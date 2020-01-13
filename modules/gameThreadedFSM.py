class GameState(object):
    def __init__(self, state="running"):
        self._state = state

    def manageState(self, action):
        if action == "pause" and self._state != "paused":
            self._state = "paused"
            
        elif action == "unpause" and self._state == "paused":
            self._state = "running"
            
        elif action == "nextLevel" and self._state == "running":
            self._state = "startLoading"
            
        elif action == "load" and self._state == "startLoading":
            self._state = "loading"
            
        elif action == "doneLoading" and self._state == "loading":
            self._state = "running"
            
    def __eq__(self, other):
        return self._state == other
