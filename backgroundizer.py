import os
from PIL import Image

class Backgroundizer(object):
    def __init__(self, fileName):
        # generates the background png from a txt file
        self._fileName = fileName

        file = open(os.path.join("levels", self._fileName))
        fileCharacters = [[y for y in x] for x in file.read().split("\n")]
        file.close()

        self._worldSize = (len(fileCharacters[0]) * 16, len(fileCharacters) * 16)

        background = Image.new('RGBA', self._worldSize)

        for row in range(len(fileCharacters)):
            for col in range(len(fileCharacters[row])):
                background.paste(Image.open(os.path.join("images", "bgImages", "grass.png")),(col*16, row*16))

        for row in range(len(fileCharacters)):
            for col in range(len(fileCharacters[row])):
                if fileCharacters[row][col] == "T":
                    tree = Image.open(os.path.join("images", "bgImages", "tree.png"))
                    background.paste(tree, (col*16, row*16), tree)
                elif fileCharacters[row][col] == "S":
                    shrub = Image.open(os.path.join("images", "bgImages", "shrub.png"))
                    background.paste(shrub, (col*16, row*16), shrub)
                elif fileCharacters[row][col] == "B":
                    rock = Image.open(os.path.join("images", "bgImages", "boulder.png"))
                    background.paste(rock, (col*16, row*16), rock)
                elif fileCharacters[row][col] == "Z":
                    castle = Image.open(os.path.join("images", "bgImages", "castleFloor.png"))
                    background.paste(castle, (col*16, row*16), castle)

                elif fileCharacters[row][col] == "u":
                    water = Image.open(os.path.join("images", "bgImages", "NwaterEdge.png"))
                    background.paste(water, (col*16, row*16), water)
                elif fileCharacters[row][col] == "d":
                    water = Image.open(os.path.join("images", "bgImages", "SwaterEdge.png"))
                    background.paste(water, (col*16, row*16), water)
                elif fileCharacters[row][col] == "l":
                    water = Image.open(os.path.join("images", "bgImages", "WwaterEdge.png"))
                    background.paste(water, (col*16, row*16), water)
                elif fileCharacters[row][col] == "r":
                    water = Image.open(os.path.join("images", "bgImages", "EwaterEdge.png"))
                    background.paste(water, (col*16, row*16), water)
                elif fileCharacters[row][col] == "v":
                    water = Image.open(os.path.join("images", "bgImages", "NWwaterEdge.png"))
                    background.paste(water, (col*16, row*16), water)
                elif fileCharacters[row][col] == "x":
                    water = Image.open(os.path.join("images", "bgImages", "NEwaterEdge.png"))
                    background.paste(water, (col*16, row*16), water)
                elif fileCharacters[row][col] == "y":
                    water = Image.open(os.path.join("images", "bgImages", "SWwaterEdge.png"))
                    background.paste(water, (col*16, row*16), water)
                elif fileCharacters[row][col] == "z":
                    water = Image.open(os.path.join("images", "bgImages", "SEwaterEdge.png"))
                    background.paste(water, (col*16, row*16), water)
                elif fileCharacters[row][col] == "m":
                    water = Image.open(os.path.join("images", "bgImages", "NWwaterCorner.png"))
                    background.paste(water, (col*16, row*16), water)
                elif fileCharacters[row][col] == "n":
                    water = Image.open(os.path.join("images", "bgImages", "NEwaterCorner.png"))
                    background.paste(water, (col*16, row*16), water)
                elif fileCharacters[row][col] == "o":
                    water = Image.open(os.path.join("images", "bgImages", "SWwaterCorner.png"))
                    background.paste(water, (col*16, row*16), water)
                elif fileCharacters[row][col] == "p":
                    water = Image.open(os.path.join("images", "bgImages", "SEwaterCorner.png"))
                    background.paste(water, (col*16, row*16), water)
                elif fileCharacters[row][col] == "w":
                    water = Image.open(os.path.join("images", "bgImages", "water.png"))
                    background.paste(water, (col*16, row*16), water)
                
                elif fileCharacters[row][col] == "a":
                    bridge = Image.open(os.path.join("images", "bgImages", "vertBridgeLeft.png"))
                    background.paste(bridge, (col*16, row*16), bridge)
                elif fileCharacters[row][col] == "b":
                    bridge = Image.open(os.path.join("images", "bgImages", "vertBridgeMid.png"))
                    background.paste(bridge, (col*16, row*16), bridge)
                elif fileCharacters[row][col] == "c":
                    bridge = Image.open(os.path.join("images", "bgImages", "vertBridgeRight.png"))
                    background.paste(bridge, (col*16, row*16), bridge)
                elif fileCharacters[row][col] == "e":
                    bridge = Image.open(os.path.join("images", "bgImages", "horzBridgeTop.png"))
                    background.paste(bridge, (col*16, row*16), bridge)
                elif fileCharacters[row][col] == "f":
                    bridge = Image.open(os.path.join("images", "bgImages", "horzBridgeMid.png"))
                    background.paste(bridge, (col*16, row*16), bridge)
                elif fileCharacters[row][col] == "g":
                    bridge = Image.open(os.path.join("images", "bgImages", "horzBridgeBot.png"))
                    background.paste(bridge, (col*16, row*16), bridge)

                elif fileCharacters[row][col] == "L":
                    cliff = Image.open(os.path.join("images", "bgImages", "cliffLeft.png"))
                    background.paste(cliff, (col*16, row*16), cliff)
                elif fileCharacters[row][col] == "W":
                    cliff = Image.open(os.path.join("images", "bgImages", "cliffWide.png"))
                    background.paste(cliff, (col*16, row*16), cliff)
                elif fileCharacters[row][col] == "R":
                    cliff = Image.open(os.path.join("images", "bgImages", "cliffRight.png"))
                    background.paste(cliff, (col*16, row*16), cliff)
                elif fileCharacters[row][col] == "U":
                    cliff = Image.open(os.path.join("images", "bgImages", "cliffTop.png"))
                    background.paste(cliff, (col*16, row*16), cliff)
                elif fileCharacters[row][col] == "M":
                    cliff = Image.open(os.path.join("images", "bgImages", "cliffMid.png"))
                    background.paste(cliff, (col*16, row*16), cliff)
                elif fileCharacters[row][col] == "A":
                    cliff = Image.open(os.path.join("images", "bgImages", "cliffBottom.png"))
                    background.paste(cliff, (col*16, row*16), cliff)

                elif fileCharacters[row][col] == "#":
                    path = Image.open(os.path.join("images", "bgImages", "path.png"))
                    background.paste(path, (col*16, row*16), path)

                elif fileCharacters[row][col] == "Q":
                    floor = Image.open(os.path.join("images", "bgImages", "castleFloor.png"))
                    background.paste(floor, (col*16, row*16), floor)
                
                elif fileCharacters[row][col] == "H":
                    floor = Image.open(os.path.join("images", "bgImages", "houseFloor.png"))
                    background.paste(floor, ((col)*16, (row)*16), floor)
                    background.paste(floor, ((col)*16, (row+1)*16), floor)
                    background.paste(floor, ((col)*16, (row+2)*16), floor)
                    background.paste(floor, ((col)*16, (row+3)*16), floor)
                    background.paste(floor, ((col+1)*16, (row)*16), floor)
                    background.paste(floor, ((col+1)*16, (row+1)*16), floor)
                    background.paste(floor, ((col+1)*16, (row+2)*16), floor)
                    background.paste(floor, ((col+1)*16, (row+3)*16), floor)
                    background.paste(floor, ((col+2)*16, (row)*16), floor)
                    background.paste(floor, ((col+2)*16, (row+1)*16), floor)
                    background.paste(floor, ((col+2)*16, (row+2)*16), floor)
                    background.paste(floor, ((col+2)*16, (row+3)*16), floor)
                    background.paste(floor, ((col+3)*16, (row)*16), floor)
                    background.paste(floor, ((col+3)*16, (row+1)*16), floor)
                    background.paste(floor, ((col+3)*16, (row+2)*16), floor)
                    background.paste(floor, ((col+3)*16, (row+3)*16), floor)
                    background.paste(floor, ((col+4)*16, (row)*16), floor)
                    background.paste(floor, ((col+4)*16, (row+1)*16), floor)
                    background.paste(floor, ((col+4)*16, (row+2)*16), floor)
                    background.paste(floor, ((col+4)*16, (row+3)*16), floor)
                    background.paste(floor, ((col+5)*16, (row)*16), floor)
                    background.paste(floor, ((col+5)*16, (row+1)*16), floor)
                    background.paste(floor, ((col+5)*16, (row+2)*16), floor)
                    background.paste(floor, ((col+5)*16, (row+3)*16), floor)
                

        background.save(os.path.abspath("images//" +self._fileName[:-4] + ".png"),"PNG")

def main():
    x = Backgroundizer("level0background.txt")

if __name__ == "__main__":
    main()
