
from pyglet.gl import *
import math, numpy

shift = 100
scale = 5
dots = [0]
connections = []

# G - coordinates of the gaze
G = [0.5, 0.5, 0.5]
# O - coordinates of the eye
O = [1, 1, 3]

window = pyglet.window.Window(500, 500)
window.flip()

def read_object(objectName):
    global dots, O, G
    global connections

    with open(objectName) as file:

        for line in file:
            if line.startswith("v"):
                coordinates = line.strip().split(" ")
                dots.append([float(coordinates[1]), float(coordinates[2]), float(coordinates[3]), 1])

            elif line.startswith("f"):
                connection = line.strip().split(" ")
                connections.append([int(connection[1]), int(connection[2]), int(connection[3])])


def main():
    global scale

    glScalef(scale/50, scale/50, scale/50)
    read_object("frog.obj")
    pyglet.app.run()

@window.event
def on_key_press(key, modifiers):
    global O, G, window, shift

    if(key == pyglet.window.key.UP):
        O[1] = O[1] + shift
        print(O)
        window.clear()
        draw_object(O, G)
    elif(key == pyglet.window.key.DOWN):
        O[1] = O[1] - shift
        print(O)
        window.clear()
        draw_object(O, G)
    elif(key == pyglet.window.key.LEFT):
        O[0] = O[0] - shift
        print(O)
        window.clear()
        draw_object(O, G)
    elif(key == pyglet.window.key.RIGHT):
        O[0] = O[0] + shift
        print(O)
        window.clear()
        draw_object(O, G)

@window.event
def calculate_view_transformation_matrix(O, G):
    x0, y0, z0 = O[0], O[1], O[2]
    xg, yg, zg = G[0], G[1], G[2]
    xg1, yg1, zg1 = xg-x0, yg-y0, zg-z0

    sinA = yg1/math.sqrt((xg1)**2 + (yg1)**2)
    cosA = xg1/math.sqrt((xg1)**2 + (yg1)**2)

    xg2 = math.sqrt((xg1)**2 + (yg1)**2)
    zg2 = zg1

    sinB = xg2/math.sqrt((xg2)**2 + (zg2)**2)
    cosB = zg2/math.sqrt((xg2)**2 + (zg2)**2)

    T1 = numpy.array([[1,     0,   0, 0],
                      [0,     1,   0, 0],
                      [0,     0,   1, 0],
                      [-x0, -y0, -z0, 1]])

    T2 = numpy.array([[cosA, -sinA, 0, 0],
                      [sinA,  cosA, 0, 0],
                      [0,        0, 1, 0],
                      [0,        0, 0, 1]])

    T3 = numpy.array([[cosB,  0, sinB, 0],
                      [0,     1,    0, 0],
                      [-sinB, 0, cosB, 0],
                      [0,     0,    0, 1]])

    T4 = numpy.array([[0, -1, 0, 0],
                      [1,  0, 0, 0],
                      [0,  0, 1, 0],
                      [0,  0, 0, 1]])

    T5 = numpy.array([[-1, 0, 0, 0],
                      [0,  1, 0, 0],
                      [0,  0, 1, 0],
                      [0,  0, 0, 1]])

    T2_3 = T2.dot(T3)
    T2_4 = T2_3.dot(T4)
    T2_5 = T2_4.dot(T5)
    T = T1.dot(T2_5)

    return T

@window.event
def calculate_perspective_projection_matrix(O, G):
    x0, y0, z0 = O[0], O[1], O[2]
    xg, yg, zg = G[0], G[1], G[2]

    H = math.sqrt((x0-xg)**2 + (y0-yg)**2 + (z0-zg)**2)
    hpStar = z0/H

    P = [[1, 0, 0, 0],
         [0, 1, 0, 0],
         [0, 0, 0, 1 / H],
         [0, 0, 0, 0]]

    return P, hpStar

@window.event
def draw_line(xS, yS, xE, yE):
    global window, scale

    glBegin(GL_LINES)
    glVertex2f(xS + window.width*scale, yS + window.height*scale)
    glVertex2f(xE + window.width*scale, yE + window.height*scale)
    glEnd()

@window.event
def draw_object(O, G):
    T = calculate_view_transformation_matrix(O, G)
    P, hpStar = calculate_perspective_projection_matrix(O ,G)
    connect_vertexes(T, P, hpStar)

@window.event
def make_transformations(dots, T, P, hpStar):
    dotsCopy = dots.copy()

    for i, d in enumerate(dotsCopy):
        matrixFormat = numpy.array(d)
        dotsCopy[i] = ((matrixFormat.dot(T)).dot(P)).dot(1 / hpStar)

    return dotsCopy

@window.event
def connect_vertexes(T, P, hpStar):
    global dots
    global connections

    dotsCopy = make_transformations(dots, T, P, hpStar)
    for connection in connections:
        vertexA = dotsCopy[connection[0]]
        vertexB = dotsCopy[connection[1]]

        x1, y1, z1 = vertexA[0], vertexA[1], vertexA[2]
        x2, y2, z2 = vertexB[0], vertexB[1], vertexB[2]

        draw_line(x1, y1, x2, y2)

if __name__ == '__main__':
    main()
