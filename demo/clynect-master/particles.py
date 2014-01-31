
import numpy
import random

def fountain():
    num = 20000
    #setup initial values of arrays
    pos = numpy.ndarray((num, 4), dtype=numpy.float32)
    col = numpy.ndarray((num, 4), dtype=numpy.float32)
    vel = numpy.ndarray((num, 4), dtype=numpy.float32)

    random.seed()
    for i in xrange(0, num):
        rad = random.uniform(.2, .5);
        x = rad*sin(2*3.14 * i/num)
        z = 0.
        y = rad*cos(2*3.14 * i/num)

        pos[i,0] = x
        pos[i,1] = y
        pos[i,2] = z
        pos[i,3] = 1.

        col[i,0] = 1.
        col[i,1] = 0.
        col[i,2] = 0.
        col[i,3] = 1.

        life = random.random()
        vel[i,0] = x*2.
        vel[i,1] = y*2.
        vel[i,2] = 3.
        vel[i,3] = life

    #print pos
    #print col
    #print vel


    #for some reason trying to do this inside CL.loadData gives me errors on mac
    from OpenGL.arrays import vbo
    pos_vbo = vbo.VBO(data=pos, usage=GL_DYNAMIC_DRAW, target=GL_ARRAY_BUFFER)
    pos_vbo.bind()
    col_vbo = vbo.VBO(data=col, usage=GL_DYNAMIC_DRAW, target=GL_ARRAY_BUFFER)
    col_vbo.bind()
     


def render(pos_vbo, col_vbo):
    glEnable(GL_POINT_SMOOTH)
    glPointSize(5)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    example.col_vbo.bind()
    glColorPointer(4, GL_FLOAT, 0, col_vbo)

    example.pos_vbo.bind()
    glVertexPointer(4, GL_FLOAT, 0, pos_vbo)

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)
    glDrawArrays(GL_POINTS, 0, num)

    glDisableClientState(GL_COLOR_ARRAY)
    glDisableClientState(GL_VERTEX_ARRAY)

    glDisable(GL_BLEND)

