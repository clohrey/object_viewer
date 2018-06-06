import numpy as np
import sys
import math
from file_parser import read_obj

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo

posX, posY = 0.0, 0.0
vertex_buffer_object = None
default_color = (0.2, 0.8, 0.4, 0.0)


def generate_environment():
    global vertex_buffer_object
    geo_vertices, vertex_normals, faces = read_obj(sys.argv[1])

    data = generate_vbo_data(geo_vertices, vertex_normals, faces)
    vertex_buffer_object = vbo.VBO(np.array(data, 'f'))


def generate_vbo_data(geo_vertices, vertex_normals, faces):
    data = []

    for face in faces:
        if not vertex_normals:
            normal = calculate_normal(geo_vertices, face)
        for vertex in face:
            vi = vertex[0]
            ni = vertex[2]
            if vertex_normals:
                data.append(geo_vertices[vi] + vertex_normals[ni])
            else:
                data.append(np.append(np.array(geo_vertices[vi]), normal))
    return data


def calculate_normal(geo_vertices, face):
    a = geo_vertices[face[0][0]]
    b = geo_vertices[face[1][0]]
    c = geo_vertices[face[2][0]]
    return np.cross(np.subtract(b, a), np.subtract(c, a))


def init_gl():
    glMatrixMode(GL_MODELVIEW)


def display():
    """
    Zeichnet nacheinander jedes Frame
    """
    glMatrixMode(GL_MODELVIEW)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    # Erstellt eine Betrachtungsmatrix aus einem Betrachterpunkt(CenterX, CenterY, CenterZ)
    gluLookAt(-2, 0, 4, 0, 0, 0, 0, 1, 0)

    # Vertex Buffer Object rendern
    vertex_buffer_object.bind()
    glVertexPointer(3, GL_FLOAT, 24, vertex_buffer_object)
    glNormalPointer(GL_FLOAT, 24, vertex_buffer_object + 12)

    # Bewegt den Koordinatenursprung in den Punkt(posX, posY, 0.0)
    glTranslate(posX, posY, 0.0)

    glColor(default_color)

    vertex_buffer_object.unbind()

    # Back zu Front Buffer swappen für Anzeige
    glutSwapBuffers()


