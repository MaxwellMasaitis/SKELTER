import os
import math
import numpy as np

def getDistance(coords1, coords2):
    return math.sqrt(math.pow(coords1[0] - coords2[0], 2) + math.pow(coords1[1] - coords2[1], 2))

class Pathing(object):
    def __init__(self, fileName):
        self._fileName = fileName
        
        file = open(os.path.join("levels", self._fileName))
        fileCharacters = [[y for y in x] for x in file.read().split("\n")]
        file.close()

        self._worldSize = [len(fileCharacters[0]) * 16, len(fileCharacters) * 16], 

        self._verts = []
        self._edgeDict = {}

        # possibly problems with corners...

        # create all the verts
        for row in range(len(fileCharacters)):
            for col in range(len(fileCharacters[row])):
                if fileCharacters[row][col].isupper() or fileCharacters[row][col] == "-":
                    pass
                else:
                    self._verts.append((col,row))

        # create all the nearby edges
        for vert in self._verts:
            #up
            if (vert[0],vert[1]-1) in self._verts:
                if fileCharacters[vert[1]][vert[0]] == "w" or fileCharacters[vert[1]-1][vert[0]] == "w":
                    self._edgeDict[(vert,(vert[0],vert[1]-1))] = 2
                    self._edgeDict[((vert[0],vert[1]-1),vert)] = 2
                else:
                    self._edgeDict[(vert,(vert[0],vert[1]-1))] = 1
                    self._edgeDict[((vert[0],vert[1]-1),vert)] = 1
            #left
            if (vert[0]-1,vert[1]) in self._verts:
                if fileCharacters[vert[1]][vert[0]] == "w" or fileCharacters[vert[1]][vert[0]-1] == "w":
                    self._edgeDict[(vert,(vert[0]-1,vert[1]))] = 2
                    self._edgeDict[((vert[0]-1,vert[1]),vert)] = 2
                else:
                    self._edgeDict[(vert,(vert[0]-1,vert[1]))] = 1
                    self._edgeDict[((vert[0]-1,vert[1]),vert)] = 1
            #up left
            if (vert[0]-1,vert[1]-1) in self._verts and (vert[0]-1,vert[1]) in self._verts and (vert[0],vert[1]-1) in self._verts:
                if fileCharacters[vert[1]][vert[0]] == "w" or fileCharacters[vert[1]-1][vert[0]] == "w" or fileCharacters[vert[1]][vert[0]-1] == "w" or fileCharacters[vert[1]-1][vert[0]-1] == "w":
                    # change for a*?
                    self._edgeDict[(vert,(vert[0]-1,vert[1]-1))] = 2*math.sqrt(2)
                    self._edgeDict[((vert[0]-1,vert[1]-1),vert)] = 2*math.sqrt(2)
                else:
                    self._edgeDict[(vert,(vert[0]-1,vert[1]-1))] = 1*math.sqrt(2)
                    self._edgeDict[((vert[0]-1,vert[1]-1),vert)] = 1*math.sqrt(2)
            #up right
            if (vert[0]+1,vert[1]-1) in self._verts and (vert[0]+1,vert[1]) in self._verts and (vert[0],vert[1]-1) in self._verts:
                if fileCharacters[vert[1]][vert[0]] == "w" or fileCharacters[vert[1]-1][vert[0]] == "w" or fileCharacters[vert[1]][vert[0]+1] == "w" or fileCharacters[vert[1]-1][vert[0]+1] == "w":
                    # change for a*?
                    self._edgeDict[(vert,(vert[0]+1,vert[1]-1))] = 2*math.sqrt(2)
                    self._edgeDict[((vert[0]+1,vert[1]-1),vert)] = 2*math.sqrt(2)
                else:
                    self._edgeDict[(vert,(vert[0]+1,vert[1]-1))] = 1*math.sqrt(2)
                    self._edgeDict[((vert[0]+1,vert[1]-1),vert)] = 1*math.sqrt(2)

    def isOutside(self, position):
        # checks if something is not on a vert in the map
        if (position[0]//16, position[1]//16) not in self._verts:
            return True
        else:
            return False

    def getPath(self,position, goal):
        # A*! A*! A*! A*!
        if (goal[0]//16, goal[1]//16) not in self._verts:
            return []
        distanceDict = {(position[0]//16, position[1]//16) : 0}
        nextDict = {(position[0]//16, position[1]//16) : (position[0]//16, position[1]//16)}
        openList = []
        closedList = [(position[0]//16, position[1]//16)]
        for vert in self._verts:
            openList.append(vert)
            if ((position[0]//16, position[1]//16),vert) in self._edgeDict:
                edgeWeight = self._edgeDict[((position[0]//16, position[1]//16),vert)]
                if edgeWeight != np.inf:
                    distanceDict[vert] = edgeWeight + math.sqrt((goal[0] - vert[0])**2+(goal[1] - vert[1])**2)
                    nextDict[vert] = (position[0]//16, position[1]//16)
                else:
                    distanceDict[vert] = np.inf
                    nextDict[vert] = None
            else:
                distanceDict[vert] = np.inf
                nextDict[vert] = None
        while openList != []:
            openList = sorted(openList, key = lambda x: distanceDict[x])
            vert = openList.pop(0)
            if vert == (goal[0]//16, goal[1]//16):
                tuplesOrder = []
                current = vert
                while current != (position[0]//16, position[1]//16):
                    tuplesOrder.append(current)
                    current = nextDict[current]
                tuplesOrder.append(current)
                tuplesOrder.reverse()
                trueTuplesOrder = []
                for x in tuplesOrder:
                    trueTuplesOrder.append((x[0]*16,x[1]*16))
                return trueTuplesOrder #?

            # try only local 8 verts
            # marginally faster?
            otherVerts = [(vert[0]-1,vert[1]),(vert[0]-1,vert[1]-1),(vert[0],vert[1]-1),(vert[0]+1,vert[1]-1),(vert[0]+1,vert[1]),(vert[0]+1,vert[1]+1),(vert[0],vert[1]+1),(vert[0]-1,vert[1]+1)]
            otherVerts = [vert for vert in otherVerts if vert in openList]
            for otherVert in otherVerts:
                if (otherVert,vert) not in self._edgeDict:
                    newDistance = np.inf
                else:
                    # changed here
                    newDistance = self._edgeDict[((otherVert[0],otherVert[1]),(vert[0],vert[1]))] + math.sqrt((goal[0]//16-otherVert[0])**2+(goal[1]//16-otherVert[1])**2) + distanceDict[vert]
                if newDistance < distanceDict[otherVert]:
                    distanceDict[otherVert] = newDistance
                    nextDict[otherVert] = vert
                        
##            for otherVert in openList:
##                if (otherVert,vert) not in self._edgeDict:
##                    newDistance = np.inf
##                else:
##                    # changed here
##                    newDistance = self._edgeDict[((otherVert[0],otherVert[1]),(vert[0],vert[1]))] + math.sqrt((goal[0]//16-otherVert[0])**2+(goal[1]//16-otherVert[1])**2) + distanceDict[vert]
##                if newDistance < distanceDict[otherVert]:
##                    distanceDict[otherVert] = newDistance
##                    nextDict[otherVert] = vert
            closedList.append(vert)

    def getEscapeRoutes(self, ownPosition, enemyPosition):
       # was more complicated before but caused lag
       # just check the adjacent verts and find the one farthest from the fear source 
       ownPosition = (ownPosition[0]//16, ownPosition[1]//16)
       enemyPosition = (enemyPosition[0]//16, enemyPosition[1]//16)

       nearVerts = [ownPosition,(ownPosition[0]-1,ownPosition[1]),(ownPosition[0]-1,ownPosition[1]-1),(ownPosition[0],ownPosition[1]-1),(ownPosition[0]+1,ownPosition[1]-1),(ownPosition[0]+1,ownPosition[1]),(ownPosition[0]+1,ownPosition[1]+1),(ownPosition[0],ownPosition[1]+1),(ownPosition[0]-1,ownPosition[1]+1)]
       nearVerts = [vert for vert in nearVerts if vert in self._verts]

       fleeDist = [getDistance(enemyPosition, vert) for vert in nearVerts]
       if len(fleeDist) == 0:
           return (ownPosition[0]*16, ownPosition[1]*16)

       fleePos = nearVerts[fleeDist.index(max(fleeDist))]
       return (fleePos[0]*16,fleePos[1]*16)
        
def main():
    # for testing, the relevant files are not here now though
    x = Pathing("level1.txt")

    print('GET PATH')
    print(x.getPath((16*2,16*12),(16*60,16*12)))
if __name__ == "__main__":
   main()
                    
