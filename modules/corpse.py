import pygame
from pygame import image
import os
from .drawable import Drawable
from .vector2D import Vector2
from .selectionArrow import SelectionArrow

class Corpse(Drawable):
    def __init__(self, position, kind, flipped):
        self._expended = False
        self._kind = kind
        # use this for potential creatures with unusual death frame lengths
        if self._kind == "longer death frames":
            pass
        else:
            super().__init__(self._kind + ".png", position, (2,3))

        if flipped:
            self._image = pygame.transform.flip(self._image, True, False)
        self._selected = False
        self._selectOffset = Vector2(4,-4)
        self._selectionArrow = SelectionArrow(self._selectOffset + self._position, "blue")
        
    def isSelected(self):
        return self._selected
    
    def setSelected(self, status):
        # helps draw the indicator arrow
        self._selected = status

    def draw(self, surface):
        super().draw(surface)
        if self._selected:
            self._selectionArrow.draw(surface)
        
    def getKind(self):
        return self._kind

    def expend(self):
        # used to make sure corpses can't be used more than once
        self._expended = True

    def isExpended(self):
        return self._expended
