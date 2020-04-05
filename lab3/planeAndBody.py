# Program read a ".obj" file, draws the 2D body described in the file and
# and check the position of a new point given by the user in relation to the body.

from pyglet.gl import *


def draw_point(t):
    glBegin(GL_POINTS)
    glVertex3f(t[0], t[1], t[2])
    glEnd()


def draw_line(xS, yS, xE, yE):
    glBegin(GL_LINES)
    glVertex2f(xS, yS)
    glVertex2f(xE, yE)
    glEnd()


with open("cube.obj") as file:
    # Indexing in ".obj" files starts from 1 for vertexs. It is in our interest to have V(i), i>0
    dots = [0]
    connections = []

    xCoordinates = []
    yCoordinates = []
    zCoordinates = []

    for line in file:
        if line.startswith("v"):
            coordinates = line.strip().split(" ")
            dots.append((float(coordinates[1]), float(coordinates[2]), float(coordinates[3])))
            xCoordinates.append(float(coordinates[1]))
            yCoordinates.append(float(coordinates[2]))
            zCoordinates.append(float(coordinates[3]))

        elif line.startswith("f"):
            connection = line.strip().split(" ")
            connections.append((int(connection[1]), int(connection[2]), int(connection[3])))

xMin, xMax = min(xCoordinates), max(xCoordinates)
yMin, yMax = min(yCoordinates), max(xCoordinates)
zMin, zMax = min(zCoordinates), max(zCoordinates)
centerOfBody = (sum(xCoordinates)/len(xCoordinates), sum(yCoordinates)/len(yCoordinates), sum(zCoordinates)/len(zCoordinates))

window = pyglet.window.Window()
# Might be needed to scale for larger bodys.
glScalef(1/xMax, 1/yMax, 1/zMax)
# Translates the body into the middle of the window.
glTranslatef(-centerOfBody[0], -centerOfBody[1], -centerOfBody[2])

print("Set the point P(x,y,z):")
px, py, pz = float(input()), float(input()), float(input())
point = (px, py, pz)

planeEquation = []

for connection in connections:
    # Triangle defines plane.
    # Calculating plane equations.
    vertexA = dots[connection[0]]
    vertexB = dots[connection[1]]
    vertexC = dots[connection[2]]

    x1 = vertexA[0]
    y1 = vertexA[1]
    z1 = vertexA[2]

    x2 = vertexB[0]
    y2 = vertexB[1]
    z2 = vertexB[2]

    x3 = vertexC[0]
    y3 = vertexC[1]
    z3 = vertexC[2]

    a = (y2 - y1) * (z3 - z1) - (z2 - z1) * (y3 - y1)
    b = -(x2 - x1) * (z3 - z1) + (z2 - z1) * (x3 - x1)
    c = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)
    d = -x1*a - y1*b - z1*c

    planeEquation.append((a,b,c,d))
    # Seting the z-coordinate to z=0 and drawing the body.
    draw_line(x1,y1,x2,y2)

# Checking if the point is inside convex body.
for plane in planeEquation:
    #Ax + By + Cz + D > 0
    if (point[0] * plane[0] + point[1] * plane[1] + point[2] * plane[2] + plane[3]) > 0:
        print("Point is outside the body.")
        break
else:
    print("Point is inside the body.")

draw_point(point)
pyglet.app.run()