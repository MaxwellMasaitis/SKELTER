# SKELTER
Code and assets for SKELTER! game

SKELTER! by Max Masaitis


STARTING THE GAME:

After unzipping the file, make sure that the images, levels, sounds, and modules folders are still intact. main.py must be in the same folder as all of these other folders. Then, run main.py through the shell, terminal, or another means of running a python file. Backgroundizer is not necessary, but was included for completion's sake.


KNOWN BUGS:

The game experiences significant lag whenever there are a large number of creatures, including undead and humans, on the screen.

The game also experiences lag any time an "intelligent" creature tries to move a long distance or across a wide open area, due to the slow speed of the pathing algorithm. This comes up frequently when using skeletons.

When lagging, it is easy for the screen to become totally filled with projectiles, since they decay based on distance instead of time.

Text on gates does not disappear if you stop attacking it.

Ranged weapons do not animate properly.

Alarm graphic for when players might go over the minion cap does not work.



CONTROLS:

ESCAPE --------- Pause

R -------------- Reset

Q -------------- Quit

WASD ----------- Movement

E -------------- Toggle between magic and commanding modes

MOUSE MOVEMENT - Drag to move the camera

H -------------- Change character's hat



The HUD will be colored red in Command Mode and blue in Magic Mode



Magic Mode Controls:

SCROLL WHEEL SCROLL - Scroll through spells

LEFT MOUSE ---------- Click to select a target, click and drag to select an area of targets

RIGHT MOUSE --------- Cast current spell. This action is context-dependent based on the current spell



Command Mode Controls:

LEFT MOUSE ---------- Click to select a minion, click and drag to select an area of minions

MIDDLE MOUSE -------- Click to select all minions, or deselect all if all minions are selected

RIGHT MOUSE --------- Click to command selected minions. This action is context-dependent based on what the mouse is pointing at. Targeting empty space causes your minions to move to that spot. Targeting an enemy or gate causes your minions to attack it. Targeting yourself causes your minions to follow you.

SPACE --------------- Halt all currently selected minions
