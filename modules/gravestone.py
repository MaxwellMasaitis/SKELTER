import pygame
from pygame import image
import os
from .drawable import Drawable
from .vector2D import Vector2
from .selectionArrow import SelectionArrow
from .corpse import Corpse
import random

class Gravestone(Drawable):
    def __init__(self, position):
        super().__init__("gravestone.png", position)
        self._filled = True
        self._holeOffset = Vector2(0,16)
        self._hole = Gravehole(self._holeOffset + self._position)
        self._corpse = Corpse(self._holeOffset + self._position, random.choice(["skeleton",random.choice(["human1","human2","human3"])]), random.choice([True, False]))
        self._selected = False
        self._selectOffset = Vector2(4,-8)
        self._selectionArrow = SelectionArrow(self._selectOffset + self._position, "blue")
        
    def isSelected(self):
        return self._selected

    def setSelected(self, status):
        self._selected = status
    
    def draw(self, surface):
        super().draw(surface)
        if not self._filled:
            self._hole.draw(surface)
        if self._selected:
            self._selectionArrow.draw(surface)

    def dig(self):
        self._filled = False
        return self._corpse

    def isFilled(self):
        return self._filled

class Gravehole(Drawable):
    def __init__(self, position):
        super().__init__("gravehole.png", position)
