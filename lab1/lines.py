# Program draws line from starting to ending point given by user and following line
# with coordinates raised by 20.

import pyglet
from pyglet.gl import *
from pyglet.window import mouse

window = pyglet.window.Window()

point1X, point1Y = 0, 0
point2X, point2Y = 0, 0 
clickCounter = 0  # Used to differentiate starting point and ending point.


# Algorithm that draws good lines from -45° to +45°.
# Loop iterates by the x variable.
def draw_line_X(xS, yS, xE, yE):
    dy = yE - yS
    a = abs(dy) / (xE - xS)
    yC = yS
    yF = -0.5

    correction = 1
    if dy < 0:
        correction = -correction

    for x in range(xS, xE):
        # Changed color to notice the difference between these and following lines.
        pyglet.graphics.draw(1, pyglet.gl.GL_POINTS, ('v2i', (x, yC)), ('c3B', (100, 150, 100)))
        yF += a
        if yF >= 0.0:
            yF -= 1.0
            yC += correction


# Algorithm that draws good lines from +45° to -45°.
# Loop iterates by the y variable.
def draw_line_Y(xS, yS, xE, yE):
    dx = xE - xS
    a = abs(dx) / (yE - yS)
    xC = xS
    xF = -0.5

    correction = 1
    if dx < 0:
        correction = -correction

    for y in range(yS, yE):
        pyglet.graphics.draw(1, pyglet.gl.GL_POINTS, ('v2i', (xC, y)), ('c3B', (100, 150, 100)))
        xF += a
        if xF >= 0.0:
            xF -= 1.0
            xC += correction


# Algorithm that calls draw_line_X or draw_line_Y based on points' coordinates.
def draw_line(xS, yS, xE, yE):
    dx = xE - xS
    dy = yE - yS

    if abs(dx) >= abs(dy):
        if dx >= 0:
            draw_line_X(xS, yS, xE, yE)
        else:
            draw_line_X(xE, yE, xS, yS)
    else:
        if dy >= 0:
            draw_line_Y(xS, yS, xE, yE)
        else:
            draw_line_Y(xE, yE, xS, yS)


# Method that draws following line raised by 20 pixels.
def draw_following_line(xS, yS, xE, yE):
    glBegin(GL_LINES)
    glVertex2i(xS, yS + 20)
    glVertex2i(xE, yE + 20)
    glEnd()


@window.event
def on_mouse_press(x, y, button, modifiers):
    global point1X, point1Y, point2X, point2Y, clickCounter

    if button & mouse.LEFT & clickCounter == 0:
        point1X, point1Y = x, y
        clickCounter = 1

    elif button & mouse.LEFT & clickCounter == 1:
        point2X, point2Y = x, y
        clickCounter = 0

    if clickCounter == 0:
        draw_line(point1X, point1Y, point2X, point2Y)
        draw_following_line(point1X, point1Y, point2X, point2Y)


pyglet.app.run()
