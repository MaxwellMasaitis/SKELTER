from .drawable import Drawable
from .vector2D import Vector2
import pygame

class Pauser(Drawable):
    def __init__(self, screenSize):
        self._active = False
        super().__init__("paused.png", screenSize // 2, worldBound = False)

        self._position -= Vector2(*self.getSize())//2

    def handleEvent(self, event):
        # bind this key properly later
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._active= not self._active

    def draw(self, surface):
        if self._active:
            super().draw(surface)

    def isActive(self):
        return self._active
