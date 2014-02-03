from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

def display(w, h):
    aspect = float(w)/float(h)
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-320, 320, -240, 240, 0, 1)#-5, 5, -5, 5, 0, 1)#-aspect * 5, aspect * 5, -5, 5, -1, 1)
    #glTranslatef(0, -480, 0);

    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glBegin(GL_QUADS)
    glVertex2f(0.25, -0.25)
    glVertex2f(0.25, 0.25)
    glVertex2f(-0.25, 0.25)
    glVertex2f(-0.25,-0.25)
    glEnd()

    glutSwapBuffers()

def reshape(w, h):
    glutDisplayFunc(lambda: display(w, h))
    glutPostRedisplay();

if __name__ == '__main__':
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(640,480)
    glutCreateWindow("Hello World :'D")

    glutReshapeFunc(reshape)
    glutIdleFunc(glutPostRedisplay)
    glutMainLoop()