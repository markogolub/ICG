# Program draws and colors the convex polygon determined by clock-wise points given by user
# and check the position of a new point(s) in relation to the polygon.

import numpy as np
from pyglet.gl import *
from pyglet.window import mouse

window = pyglet.window.Window()

dots = []

leftEdges = []
rightEdges = []

flag = 0

# Returns the intersection of two lines as tuple.
def intersect(G1, G2):
    X = np.cross(G1, G2)
    return ((X[0] / X[2], X[1] / X[2]))


def draw_line(xS, yS, xE, yE):
    glBegin(GL_LINES)
    glVertex2i(xS, yS)
    glVertex2i(xE, yE)
    glEnd()


@window.event
def on_mouse_press(x, y, button, modifiers):
    global dots, flag, leftEdges, rightEdges

    if button & mouse.LEFT and flag == 0:
        dots.append((x, y))

    elif button & mouse.RIGHT and flag == 0:
        print("Number of the polygon vertices: " + str(len(dots)) + "\n")
        for dot in dots:
            print("Coordinates od vertices: " + str(dot))
        print()

        for i in range(0, len(dots)):
            xS = dots[i][0]
            yS = dots[i][1]
            try:
                xE = dots[i + 1][0]
                yE = dots[i + 1][1]
            except:
                xE = dots[0][0]
                yE = dots[0][1]

            a = yS - yE
            b = -xS + xE
            c = xS * yE - xE * yS

            if yS < yE:
                leftEdges.append((a, b, c))
            else:
                rightEdges.append((a, b, c))

            draw_line(xS, yS, xE, yE)

        flag = 1
        # These numbers act as -infinity and infinity.
        xMax, xMin = -100000000, 100000000
        yMax, yMin = -100000000, 100000000

        for dot in dots:
            if dot[0] > xMax:
                xMax = dot[0]
            if dot[0] < xMin:
                xMin = dot[0]
            if dot[1] > yMax:
                yMax = dot[1]
            if dot[1] < yMin:
                yMin = dot[1]

        for y in range(yMin, yMax):
            L = xMin
            R = xMax
            for edge in (leftEdges + rightEdges):
                intersectPoint = intersect(edge, (0, 1, -y))
                S = np.floor(intersectPoint[0])
                if edge in leftEdges and S > L:
                    L = S
                elif edge in rightEdges and S < R:
                    R = S
            if L <= R:
                draw_line(int(L // 1), y, int(R // 1), y)

    elif button & mouse.LEFT and flag == 1:
        print("Coordinate of the point: " + str((x, y)))
        for edge in (leftEdges + rightEdges):
            # For points given counter-clockwise required "<=".
            if x * edge[0] + y * edge[1] + edge[2] > 0:
                print("Outside.\n")
                break
        else:
            print("Inside.\n")

    elif button & mouse.RIGHT and flag == 1:
        flag = "Flag raised to stop program."
        print("The end.")


print("Set points (clockwise direction) with left mouse click.\n"
      "End action with right click.\n"
      "Then with left click check if new point (place clicked) is inside or outside the coloured area.\n"
      "Stop program with new right click.\n")

pyglet.app.run()