from pyglet.gl import *
import numpy, math

O = [6, 6, 2]
G = [0, 0, 0]
I = [5, 5, 5]
V = [1, 1, 1]

dots, connections, translatedVertexes = [], [], []
xCoordinates, yCoordinates, zCoordinates = [], [], []

vertexImpact, normals = {}, {}

mode = 0

window = pyglet.window.Window(800, 800)
batch = pyglet.graphics.Batch()

def main():
    global mode
    global O, G, I
    print("Select mode:\n1) Constant\n2) Gouraud")
    while mode not in [1, 2]: mode = int(input())
    draw_object(O, G)
    pyglet.app.run()

# Calculates transformation and projection.
def translate_and_project(O, G):
    T1 = numpy.array([[1, 0, 0, 0],
                      [0, 1, 0, 0],
                      [0, 0, 1, 0],
                      [-O[0], -O[1], -O[2], 1]])

    z = [G[0] - O[0], G[1] - O[1], G[2] - O[2]]

    lenOfZ = math.sqrt(z[0] * z[0] + z[1] * z[1] + z[2] * z[2])
    lenOfV = math.sqrt(V[0] * V[0] + V[1] * V[1] + V[2] * V[2])

    normalizedZ = [z[0] / lenOfZ, z[1] / lenOfZ, z[2] / lenOfZ]
    vNorm = [V[0] / lenOfV, V[1] / lenOfV, V[2] / lenOfV]

    normalizedX = numpy.cross(normalizedZ, vNorm)
    normalizedY = numpy.cross(normalizedX, normalizedZ)

    rUk = numpy.array([[normalizedX[0], normalizedY[0], normalizedZ[0], 0],
                       [normalizedX[1], normalizedY[1], normalizedZ[1], 0],
                       [normalizedX[2], normalizedY[2], normalizedZ[2], 0],
                       [0, 0, 0, 1]])

    Tz = numpy.array([[1, 0, 0, 0],
                      [0, 1, 0, 0],
                      [0, 0, -1, 0],
                      [0, 0, 0, 1]])

    T = numpy.dot(numpy.dot(T1, rUk), Tz)

    H = math.sqrt((O[0] - G[0]) * (O[0] - G[0])
                  + (O[1] - G[1]) * (O[1] - G[1])
                  + (O[2] - G[2]) * (O[2] - G[2]))

    P = [[1, 0, 0, 0],
         [0, 1, 0, 0],
         [0, 0, 0, 1 / H],
         [0, 0, 0, 0]]

    return T, P

def read_object(objectName):
    global dots, connections
    global xCoordinates, yCoordinates, zCoordinates

    with open(objectName) as file:
        for line in file:
            if line.startswith("v"):
                coordinates = line.strip().split(" ")
                xCoordinates.append(float(coordinates[1]))
                yCoordinates.append(float(coordinates[2]))
                zCoordinates.append(float(coordinates[3]))
                dots.append((float(coordinates[1]), float(coordinates[2]), float(coordinates[3])))

            elif line.startswith("f"):
                connection = line.strip().split(" ")
                connections.append((int(connection[1]) - 1, int(connection[2]) - 1, int(connection[3]) - 1))

def calculcate_index(L, N):
    Ia, ka = 10, 0.9
    Ii, kd = 222, 0.2
    Ig = Ia * ka
    Id = Ii * kd * max(0, numpy.dot(L, N))
    return Id + Ig

def draw_in_constant_mode(visible):
    global connections, dots, translatedVertexes
    global I, batch

    for connection in connections:
        if connection in visible:
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

            L = [I[0] - (x1 + x2 + x3) / 3,
                 I[1] - (y1 + y2 + y3) / 3,
                 I[2] - (z1 + z2 + z3) / 3]

            N = [a, b, c]

            indexColor = calculcate_index(numpy.linalg.norm(L), numpy.linalg.norm(N))

            vertexA = translatedVertexes[connection[0]]
            vertexB = translatedVertexes[connection[1]]
            vertexC = translatedVertexes[connection[2]]

            x1, y1, z1 = vertexA[0], vertexA[1], vertexA[2]
            x2, y2, z2 = vertexB[0], vertexB[1], vertexB[2]
            x3, y3, z3 = vertexC[0], vertexC[1], vertexC[2]

            batch.add(3, pyglet.gl.GL_TRIANGLES, None, ('v2f', (x1, y1, x2, y2, x3, y3)),
                      ('c3f', (0, indexColor / 255, 0, 0, indexColor / 255, 0, 0, indexColor / 255, 0)))

def draw_in_gouraud_mode(visible):
    global vertexImpact, normals
    global connections, dots, translatedVertexes
    global I, batch

    for i in range(0, len(dots)):
        vertexImpact[i] = []

    for connection in connections:
        for i in range(0, len(dots)):
            if i in connection:
                vertexImpact[i].append(connection)

    for i in range(0, len(dots)):
        aSum, bSum, cSum = 0, 0, 0
        for vertex in vertexImpact[i]:
            vertexA = dots[vertex[0]]
            vertexB = dots[vertex[1]]
            vertexC = dots[vertex[2]]

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

            aSum += a
            bSum += b
            cSum += c

            V = [aSum / len(vertexImpact[i]),
                 bSum / len(vertexImpact[i]),
                 cSum / len(vertexImpact[i])]

            normals[i] = (V[0] / numpy.linalg.norm(V),
                          V[1] / numpy.linalg.norm(V),
                          V[2] / numpy.linalg.norm(V))

    for connection in connections:
        if connection in visible:
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

            L1 = [I[0] - x1,
                  I[1] - y1,
                  I[2] - z1]

            N1 = [normals[connection[0]][0],
                  normals[connection[0]][1],
                  normals[connection[0]][2]]

            I1 = calculcate_index(numpy.linalg.norm(L1), numpy.linalg.norm(N1))

            L2 = [I[0] - x2,
                  I[1] - y2,
                  I[2] - z2]

            N2 = [normals[connection[1]][0],
                  normals[connection[1]][1],
                  normals[connection[1]][2]]

            I2 = calculcate_index(numpy.linalg.norm(L2), numpy.linalg.norm(N2))

            L3 = [I[0] - x3,
                  I[1] - y3,
                  I[2] - z3]

            N3 = [normals[connection[2]][0],
                  normals[connection[2]][1],
                  normals[connection[2]][2]]

            I3 = calculcate_index(numpy.linalg.norm(L3), numpy.linalg.norm(N3))

            vertexA = translatedVertexes[connection[0]]
            vertexB = translatedVertexes[connection[1]]
            vertexC = translatedVertexes[connection[2]]

            x1, y1, z1 = vertexA[0], vertexA[1], vertexA[2]
            x2, y2, z2 = vertexB[0], vertexB[1], vertexB[2]
            x3, y3, z3 = vertexC[0], vertexC[1], vertexC[2]

            batch.add(3, pyglet.gl.GL_TRIANGLES, None, ('v2f', (x1, y1, x2, y2, x3, y3)),
                      ('c3f', (0, (I1 - 100) / 256, 0, 0, (I2 - 100) / 256, 0, 0, (I3 - 100) / 256, 0)))

def draw_object(O, G):
    global batch, translatedVertexes, mode

    visible = []
    read_object("frog.obj")

    T, P = translate_and_project(O, G)

    for dot in dots:
        tempVertex = numpy.dot(numpy.dot([dot[0], dot[1], dot[2], 1], T), P)
        tempVertex = numpy.multiply(tempVertex, 1 / tempVertex[3])
        translatedVertexes.append(tempVertex)

    for connection in connections:

        vertexA = translatedVertexes[connection[0]]
        vertexB = translatedVertexes[connection[1]]
        vertexC = translatedVertexes[connection[2]]

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
        d = -x1 * a - y1 * b - z1 * c

        angle = a * O[0] + b * O[1] + c * O[2] + d
        if angle > 0 and angle < 90: visible.append(connection)

    if mode == 1: draw_in_constant_mode(visible)
    if mode == 2: draw_in_gouraud_mode(visible)

@window.event
def on_draw():
    window.clear()
    glScalef(40.0, 40.0, 0.0)
    glTranslatef(8, 8, 0.0)
    batch.draw()

if __name__ == '__main__':
    main()