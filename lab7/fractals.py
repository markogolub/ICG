from pyglet.gl import *

xmax, ymax = 499, 499
umin, umax = -2, 1
vmin, vmax = -1.2, 1.2

m, eps, mode = 64, 100, 0

window = pyglet.window.Window(500, 500)

def divergence_test(c, limit, mode, eps):
    if mode == 1: z = [0, 0]
    if mode == 2:
        z = [c[0], c[1]]
        modul2 = z[0] * z[0] + z[1] + z[1]
        if modul2 > eps*eps:return 0
        c = [0.11, 0.65]

    for i in range(0, limit):
        next_re = z[0] * z[0] - z[1] * z[1] + c[0]
        next_im = 2 * z[0] * z[1] + c[1]
        z[0] = next_re
        z[1] = next_im
        modul2 = z[0] * z[0] + z[1] + z[1]
        if modul2 > 4: return i

    return -1

@window.event
def on_draw():
    c = [0.11, 0.65]
    glPointSize(1)
    glBegin(GL_POINTS)

    for y in range(0, ymax):
        for x in range(0, xmax):
            c[0] = x / xmax * (umax - umin) + umin
            c[1] = y / ymax * (vmax - vmin) + vmin

            if mode == 1: n = divergence_test(c, m, 1, eps)
            elif mode == 2: n = divergence_test(c, m, 2, eps)

            if n == -1: glColor3f(0, 0, 0)
            else: glColor3f(n / m, (1 - (n / m)) / 2, (0.8 - (n / m)) / 3)

            glVertex2i(x, y)

    glEnd()

print("Select mode:\n1) Mandelbrotov\n2) Julijev")
while mode not in [1, 2]: mode = int(input())
pyglet.app.run()