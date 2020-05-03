from pyglet.gl import *
import math, numpy

dots = [0]
connections = []
points = []

scaleOfCoordinate = 60
scaleOfWindow = 0.2
index = 0

G = [0.5, 0.5, 0.5]

window = pyglet.window.Window()
windowObject = pyglet.window.Window()

def main():
    global scaleOfCoordinate, scaleOfWindow, points

    glScalef(scaleOfWindow, scaleOfWindow, scaleOfWindow)
    R, RX, RY = get_vertices_of_control_polygon()
    calculate_bezier_coordinates(R, RX, RY)
    draw_control_points(R)
    draw_bezier_curve()
    read_object("frog.obj")
    pyglet.app.run()

def read_object(objectName):
    global dots
    global connections

    with open(objectName) as file:

        for line in file:
            if line.startswith("v"):
                coordinates = line.strip().split(" ")
                dots.append([float(coordinates[1]), float(coordinates[2]), float(coordinates[3]), 1])

            elif line.startswith("f"):
                connection = line.strip().split(" ")
                connections.append([int(connection[1]), int(connection[2]), int(connection[3])])


@window.event
# Starts the animation on ENTER key press.
def on_key_press(key, modifiers):
    global G, points, index
    # Random eye location.
    point = [1, -15, 1]

    while(key == pyglet.window.key.ENTER and index < 100):
        eyeOfBezier = [float(point[0]) + points[index][0]*scaleOfCoordinate, float(point[1]) + points[index][1]*scaleOfCoordinate, 1]
        print(points[index])
        window.flip()
        window.clear()
        draw_object(eyeOfBezier, G)
        index += 1
        if index == 100:
            index = 0

# Calculates binomial coefficient.
def C(n, k):
    if k+1 > n or k < 0: raise ArithmeticError

    C = [[0 for filler in range(0, k + 1)] for filler in range(0, n)]

    for i in range (0, n):
        for j in range (0, k + 1):
            if j in (0, i): C[i][j] = 1
            else: C[i][j] = C[i - 1][j - 1] + C[i - 1][j]

    return C[n-1][k]

def get_vertices_of_control_polygon():
    R = [[0, 0, 0],
         [-3, 1, 0],
         [3, 1, 0],
         [4, 2, 0]]

    RX = []
    RY = []

    for dot in R:
        RX.append(dot[0])
        RY.append(dot[1])

    return R, RX, RY

def calculate_bezier_coordinates(R, RX, RY):
    global points
    t = 0
    level = len(R)

    while t <= 1:
        pointTx = 0
        pointTy = 0
        for i in range (0, level):
            try: constant = C(level, i) * ((1 - t) ** (level - 1 - i)) * (t ** (i))
            except ArithmeticError:
                print("Wrong parameters.")
                pass
            pointTx += constant * RX[i]
            pointTy += constant * RY[i]
        points.append([pointTx, pointTy, 1])
        t += 0.001

def draw_control_points(R):
    for point in R:
        pyglet.graphics.draw(1, pyglet.gl.GL_POINTS,
                             ('v2i', (point[0], point[1]))
                             )

def draw_bezier_curve():
    global points
    for point in points:
        # print(point)
        pyglet.graphics.draw(1, pyglet.gl.GL_POINTS,
                             ('v2f', (point[0], point[1]))
                             )


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

def draw_line(xS, yS, xE, yE):
    global window

    glBegin(GL_LINES)
    glVertex2f(xS + window.width/2, yS + window.height/2)
    glVertex2f(xE + window.width/2, yE + window.height/2)
    glEnd()

def draw_object(O, G):
    T = calculate_view_transformation_matrix(O, G)
    P, hpStar = calculate_perspective_projection_matrix(O ,G)
    connect_vertexes(T, P, hpStar)

def make_transformations(dots, T, P, hpStar):
    dotsCopy = dots.copy()

    for i, d in enumerate(dotsCopy):
        matrixFormat = numpy.array(d)
        dotsCopy[i] = ((matrixFormat.dot(T)).dot(P)).dot(1 / hpStar)

    return dotsCopy

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
    # Exits while(True) loop with KeyboardInterruption.
    try: main()
    except KeyboardInterrupt: pass
