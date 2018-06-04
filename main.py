from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo
from file_parser import read_obj
import object_viewer
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Bitte Dateipfad als Argument angeben")
        sys.exit(-1)
    else:
        read_obj(sys.argv[1])
