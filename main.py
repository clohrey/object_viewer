from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo

from file_parser import read_obj
from object_viewer import *
import sys

WIDTH, HEIGHT = 500, 500


def main():
    if len(sys.argv) < 2:
        print("Keinen Dateipfad bzw. Dateinamen angegeben!")
        sys.exit(-1)
    else:
        print("Objectfile: " + sys.argv[1])

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow("Object Viewer")

    glutDisplayFunc(display)

    glutKeyboardFunc(key_events)
    glutMouseFunc(mouse_button_pressed)
    glutMotionFunc(mouse_moved)

    init_geometry()
    init_gl()

    glutMainLoop()


if __name__ == "__main__":
    main()
