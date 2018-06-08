import numpy as np
from file_parser import read_obj

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo

posX, posY = 0.0, 0.0
vertex_buffer_object = None

DEFAULT_COLOR = (0.2, 0.8, 0.4, 0.0)
WIDTH, HEIGHT = 500, 500

RED = (1.0, 0.0, 0.0, 0.0)
GREEN = (0.0, 1.0, 0.0, 0.0)
BLUE = (0.0, 0.0, 1.0, 0.0)
YELLOW = (1.0, 1.0, 0.0, 0.0)
BLACK = (0.0, 0.0, 0.0, 0.0)
WHITE = (1.0, 1.0, 1.0, 0.0)

center = None
field_of_view = 45.0
near = 0.1
far = 100.0
display_mode = 's'
projection_mode = 'p'
light = None
data_for_vbo = None
scale_factor = 0
model_color = BLACK

zoomFactor, zoomMin, zoomMax = 1.0, 0.5, 10.0


def generate_vbo_data(geo_vertices, vertex_normals, faces):
    data = []

    for face in faces:
        if not vertex_normals:
            normal = calculate_normal(geo_vertices, face)
        for vertex in face:
            v = vertex[0]
            vn = vertex[2]
            if vertex_normals:
                data.append(geo_vertices[v] + vertex_normals[vn])
            else:
                data.append(np.append(np.array(geo_vertices[v]), normal))
    return data


def calculate_normal(geo_vertices, face):
    a = geo_vertices[face[0][0]]
    b = geo_vertices[face[1][0]]
    c = geo_vertices[face[2][0]]
    return np.cross(np.subtract(b, a), np.subtract(c, a))


def init_gl():
    global field_of_view, near, far, projection_mode
    aspect_ratio = float(WIDTH) / HEIGHT

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glClearColor(*WHITE)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(field_of_view / zoomFactor, aspect_ratio, near, far)

    glMatrixMode(GL_MODELVIEW)
    glutPostRedisplay()


def init_geometry():
    # TODO: Nochmal drüber schauen!
    global vertex_buffer_object, scale_factor, center, light, data_for_vbo
    geo_vertices, vertex_normals, faces = read_obj(sys.argv[1])

    bounding_box = [list(map(min, zip(*geo_vertices))), list(map(max, zip(*geo_vertices)))]
    scale_factor = 2.0 / max([(x[1] - x[0]) for x in zip(*bounding_box)])
    center = [(x[0] + x[1]) / 2.0 for x in zip(*bounding_box)]
    light = [bounding_box[1][0] * 2, bounding_box[1][1] * 3, bounding_box[1][2] / 2]

    data_for_vbo = generate_vbo_data(geo_vertices, vertex_normals, faces)
    vertex_buffer_object = vbo.VBO(np.array(data_for_vbo, 'f'))


def display():
    """
    Zeichnet nacheinander jedes Frame
    Quelle: https://wiki.delphigl.com/
    """
    global data_for_vbo, vertex_buffer_object, center

    # ModelView-Matrix-Modus aktivieren
    glMatrixMode(GL_MODELVIEW)

    # Leert die Buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Ersetzt die aktuelle Matrix durch die Einheitsmatrix
    glLoadIdentity()

    # Erstellt eine Betrachtungsmatrix aus einem Betrachterpunkt(CenterX, CenterY, CenterZ)
    gluLookAt(-2, 0, 4, 0, 0, 0, 0, 1, 0)

    # Vertex Buffer Object rendern
    vertex_buffer_object.bind()

    # Werte aus Folie 193
    # config zum Lesen der Vertices und Pointer auf VBO's bzw. Normalen
    glVertexPointer(3, GL_FLOAT, 24, vertex_buffer_object)
    glNormalPointer(GL_FLOAT, 24, vertex_buffer_object + 12)

    # Bewegt den Koordinatenursprung in den Punkt(posX, posY, 0.0)
    glTranslate(posX, posY, 0.0)

    # Folie 193, Verzerrung bzw. Spiegelung der Koordinatensystems
    glScale(scale_factor, scale_factor, scale_factor)
    glTranslate(-center[0], -center[1], -center[2])

    # Setzt Farbe des anzuzeigenden Objektes
    glColor(model_color)

    if display_mode == 's':
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        # Wenn aktiviert werden Tiefenvergleiche getätigt
        # und der Tiefenpuffer (z-Buffer) aktualisiert.
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)
        glEnable(GL_COLOR_MATERIAL)
        glCullFace(GL_BACK)
        glLight(GL_LIGHT0, GL_POSITION, light)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glDrawArrays(GL_TRIANGLES, 0, len(data_for_vbo))
    elif display_mode == 'w':
        # Polygon-Netz
        glDisable(GL_LIGHT0)
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_NORMALIZE)
        glDisable(GL_COLOR_MATERIAL)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glDrawArrays(GL_TRIANGLES, 0, len(data_for_vbo))

    vertex_buffer_object.unbind()
    # Back zu Front Buffer swappen für Anzeige
    glutSwapBuffers()


def key_events(key):
    global display_mode

    if key == 'd':
        if display_mode == 's':
            display_mode = 'w'
            glutPostRedisplay()
        elif display_mode == 'w':
            display_mode = 's'
            glutPostRedisplay()
