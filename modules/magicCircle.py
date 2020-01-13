from .mobile import Mobile

class MagicCircle(Mobile):
    def __init__(self, position, school = None):
        if school == "holy":
            super().__init__("magicCircleHoly.png", position)
        elif school == "demonic":
            super().__init__("magicCircleDemonic.png", position)
        else:
            super().__init__("magicCircle.png", position)
        self._nFrames = 8
