import pygame
import os
from modules.vector2D import Vector2
from modules.drawable import Drawable
from modules.gameManagerThreaded import GameManagerThreaded

SCREEN_SIZE = Vector2(400, 400)
SCALE = 2
UPSCALED_SCREEN_SIZE = Vector2(*[x * SCALE for x in SCREEN_SIZE])

def main():

    # initialize the pygame module
    pygame.init()
    # load and set the logo

    pygame.display.set_caption("SKELTER!")

    # consider adding custom cursors for the modes: magic, commanding, force commanding
    pygame.mouse.set_visible(True)

    screen = pygame.display.set_mode(list(UPSCALED_SCREEN_SIZE))

    drawSurface = pygame.Surface(list(SCREEN_SIZE))

    game = GameManagerThreaded(SCREEN_SIZE)

    # Make a game clock for nice, smooth animations
    gameClock = pygame.time.Clock()

    # define a variable to control the main loop
    running = True

    # main loop
    while running:

        # Let our game clock tick at 60 fps
        gameClock.tick(60)
        
        # Draw everything
        game.draw(drawSurface)
        
        # Flip the display to the monitor
        pygame.transform.scale(drawSurface, list(UPSCALED_SCREEN_SIZE), screen)
        pygame.display.flip()

        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT or Q is pressed
            #if event.type == pygame.QUIT:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                # change the value to False, to exit the main loop
                running = False
            else:
                game.handleEvent(event)
        
        # Get some time in seconds
        ticks = gameClock.get_time() / 1000
        
        # update
        game.update(ticks, SCREEN_SIZE, SCALE)

    pygame.quit()

if __name__ == "__main__":
   main()
